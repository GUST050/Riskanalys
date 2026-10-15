"""Avgränsad iXBRL-läsare. Okänd semantik ger inget omsättningsförslag.

Stöd: gen-base 2021-10-31, odimensionerad bolagskontext, SEK och
numspacecomma/numdotdecimal. Ingen nätverksläsning eller ZIP-extraktion.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import io
from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile
import zlib
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.bokslut import Bokslut
from riskanalys.profil.modeller import Period

MAX_ZIP = 20 * 1024 * 1024
MAX_XML = 8 * 1024 * 1024
X = '{http://www.xbrl.org/2003/instance}'
IX = '{http://www.xbrl.org/2013/inlineXBRL}'
GEN = 'http://www.taxonomier.se/se/fr/gen-base/2021-10-31'
TRANS = {'http://www.xbrl.org/inlineXBRL/transformation/2010-04-20',
         'http://www.xbrl.org/inlineXBRL/transformation/2015-02-26'}


def _qname(text, ns):
    prefix, local = text.split(':')
    return ns[prefix], local


def _tal(e, ns):
    if e.get('continuedAt') or e.get('sign', '') not in ('', '-') or list(e):
        raise ValueError('talformat')
    if e.get('{http://www.w3.org/2001/XMLSchema-instance}nil') in ('true', '1'):
        raise ValueError('nil')
    value = (e.text or '').strip()
    fmt = e.get('format')
    if fmt:
        uri, name = _qname(fmt, ns)
        if uri not in TRANS or name not in ('numspacecomma', 'numdotdecimal'):
            raise ValueError('transform')
        if name == 'numspacecomma':
            if not re.fullmatch(r'(?:[0-9]+|[0-9]{1,3}(?:[ \u00a0\u202f][0-9]{3})+)(?:,[0-9]+)?', value):
                raise ValueError('tal')
            value = re.sub(r'[ \u00a0\u202f]', '', value).replace(',', '.')
        elif not re.fullmatch(r'(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?', value):
            raise ValueError('tal')
        else:
            value = value.replace(',', '')
    elif not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value):
        raise ValueError('tal')
    scale = int(e.get('scale', '0'))
    dec = e.get('decimals', '')
    decimals = 20 if dec == 'INF' else int(dec)
    if not -12 <= scale <= 12 or not -12 <= decimals <= 20 or len(value) > 40:
        raise ValueError('precision')
    tal = Decimal(value) * (Decimal(10) ** scale)
    if e.get('sign') == '-':
        tal = -tal
    if not tal.is_finite() or not 0 <= tal <= 10**15:
        raise ValueError('belopp')
    return tal, decimals


def _varde(fakta, exakt=False):
    if not fakta:
        return None
    value, precision = max(fakta, key=lambda v: v[1])
    if exakt and precision < 0:
        raise ValueError('bara avrundat belopp')
    for v, d in fakta:
        # Olika precision tillåts bara inom den grövre postens avrundningsintervall.
        if (d == precision and v != value) or abs(value - v) > Decimal('0.5') * Decimal(10) ** -d:
            raise ValueError('motstridiga dubbletter')
    return value


def _rapport(raw, orgnr, slut):
    text = raw.decode('utf-8-sig')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD')
    ns = {}
    for event, item in ET.iterparse(io.StringIO(text), events=('start-ns',)):
        prefix, uri = item
        if prefix in ns and ns[prefix] != uri:
            raise ValueError('omdefinierad namespace')
        ns[prefix] = uri
    root = ET.fromstring(text)
    ids = {}
    for e in root.iter():
        if e.get('id'):
            if e.get('id') in ids:
                raise ValueError('dubblett-id')
            ids[e.get('id')] = e
    fakta = []
    for e in root.iter(IX + 'nonFraction'):
        uri, name = _qname(e.get('name', ''), ns)
        if name not in ('Nettoomsattning', 'MedelantaletAnstallda'):
            continue
        if uri != GEN:
            raise ValueError('taxonomi')
        ctx = ids[e.attrib['contextRef']]
        if ctx.tag != X + 'context':
            raise ValueError('kontext')
        if ctx.find('.//' + X + 'segment') is not None or ctx.find(X + 'scenario') is not None:
            continue
        identifier = ctx.find(X + 'entity/' + X + 'identifier')
        if identifier is None or identifier.get('scheme') != 'http://www.bolagsverket.se':
            raise ValueError('identifierare')
        if (identifier.text or '').replace('-', '').strip() != orgnr:
            raise ValueError('bolagsidentitet')
        period = ctx.find(X + 'period')
        start = date.fromisoformat(period.findtext(X + 'startDate', ''))
        end = date.fromisoformat(period.findtext(X + 'endDate', ''))
        if end != slut:
            continue
        if start > end:
            raise ValueError('period')
        unit = ids[e.attrib['unitRef']]
        if unit.tag != X + 'unit' or len(unit) != 1 or unit[0].tag != X + 'measure':
            raise ValueError('enhet')
        measure = _qname(unit[0].text, ns)
        expected = ('http://www.xbrl.org/2003/iso4217', 'SEK') if name == 'Nettoomsattning' else ('http://www.taxonomier.se/se/fr/k2/datatype', 'AntalAnstallda')
        if measure != expected:
            raise ValueError('enhet')
        fakta.append((name, start, _tal(e, ns), e.attrib['contextRef']))
    oms = [f for f in fakta if f[0] == 'Nettoomsattning']
    if not oms:
        return None
    starts = {f[1] for f in oms}
    if len(starts) != 1:
        raise ValueError('olika periodstarter')
    start = starts.pop()
    return dict(period=Period(fran=start, till=slut),
                omsattning=_varde([f[2] for f in oms], exakt=True),
                medelantal=_varde([f[2] for f in fakta if f[0] == 'MedelantaletAnstallda' and f[1] == start]),
                kontext=max(oms, key=lambda f: f[2][1])[3], taxonomi=GEN)


def las_arsredovisning(raw: bytes, orgnr: str, periodslut: date, dokument_id: str) -> Bokslut:
    try:
        if len(raw) > MAX_ZIP:
            raise ValueError('paketstorlek')
        resultat = []
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            filer = z.infolist()
            if len(filer) > 32 or sum(f.file_size for f in filer) > 40 * 1024 * 1024:
                raise ValueError('uppackad storlek')
            for f in filer:
                path = PurePosixPath(f.filename)
                if path.is_absolute() or '..' in path.parts or '\\' in f.filename or len(f.filename) > 500:
                    raise ValueError('sökväg')
                if path.suffix.lower() not in ('.xhtml', '.html', '.htm'):
                    continue
                if f.file_size > MAX_XML or f.flag_bits & 1:
                    raise ValueError('dokumentstorlek')
                with z.open(f) as stream:
                    xml = stream.read(MAX_XML + 1)
                if len(xml) > MAX_XML:
                    raise ValueError('dokumentstorlek')
                data = _rapport(xml, orgnr, periodslut)
                if data:
                    resultat.append(Bokslut(**data, fil=f.filename, dokument_id=dokument_id,
                                           sha256=hashlib.sha256(raw).hexdigest()))
        if len(resultat) != 1:
            raise ValueError('ingen entydig årsredovisning')
        return resultat[0]
    except (ValueError, KeyError, TypeError, AttributeError, InvalidOperation, ET.ParseError,
            zipfile.BadZipFile, zlib.error, EOFError, RuntimeError, NotImplementedError, OSError):
        raise RiskanalysFel('Årsredovisningen kunde inte ge ett säkert omsättningsförslag. Kontrollera dokumentets bolag, period, SEK, taxonomi och precision; ange uppgiften manuellt vid behov.') from None
