"""Syntetisk iXBRL: fel skala, identitet eller kontext får inte bli profilsvar."""
import io
import zipfile
from datetime import date
from decimal import Decimal
import pytest
from riskanalys.fel import RiskanalysFel

ORG = '5599991238'

def xhtml(exakt='1234567', avrundat='1 235', orgnr=ORG, dimension='', valuta='SEK', extra='', taxonomi='2021-10-31'):
    return f'''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:x="http://www.xbrl.org/2003/instance"
 xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:g="http://www.taxonomier.se/se/fr/gen-base/{taxonomi}"
 xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2010-04-20" xmlns:iso="http://www.xbrl.org/2003/iso4217"
 xmlns:k="http://www.taxonomier.se/se/fr/k2/datatype">
 <x:context id="p"><x:entity><x:identifier scheme="http://www.bolagsverket.se">{orgnr}</x:identifier></x:entity>
 <x:period><x:startDate>2024-01-01</x:startDate><x:endDate>2024-12-31</x:endDate></x:period>{dimension}</x:context>
 <x:unit id="kr"><x:measure>iso:{valuta}</x:measure></x:unit>
 <x:unit id="antal"><x:measure>k:AntalAnstallda</x:measure></x:unit>
 <ix:nonFraction name="g:Nettoomsattning" contextRef="p" unitRef="kr" scale="3" decimals="-3" format="ixt:numspacecomma">{avrundat}</ix:nonFraction>
 <ix:nonFraction name="g:Nettoomsattning" contextRef="p" unitRef="kr" scale="0" decimals="0" format="ixt:numspacecomma">{exakt}</ix:nonFraction>
 <ix:nonFraction name="g:MedelantaletAnstallda" contextRef="p" unitRef="antal" scale="0" decimals="0" format="ixt:numspacecomma">7</ix:nonFraction>{extra}</html>'''.encode()

def paket(raw=None, namn='rapport.xhtml'):
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:z.writestr(namn,raw if raw is not None else xhtml())
    return buf.getvalue()

def las(raw=None):
    from riskanalys.foretagsdata.arsredovisning import las_arsredovisning
    return las_arsredovisning(paket(raw), ORG, date(2024,12,31), 'syntetisk-doc')

def test_exakt_belopp_vinner_over_forenligt_avrundat_tusental():
    r=las()
    assert r.omsattning==Decimal('1234567')
    assert r.period.fran==date(2024,1,1) and r.period.till==date(2024,12,31)
    assert r.medelantal==Decimal('7') and len(r.sha256)==64

@pytest.mark.parametrize('kwargs',[
 {'orgnr':'5299999994'}, {'dimension':'<x:scenario>koncern</x:scenario>'},
 {'valuta':'EUR'}, {'taxonomi':'2099-01-01'}, {'exakt':'9876543'},
 {'exakt':'NaN'}, {'exakt':'-1234567'},
 {'extra':'<ix:nonFraction name="g:Nettoomsattning" contextRef="p" unitRef="kr" decimals="0">1234568</ix:nonFraction>'},
])
def test_osakert_bokslut_avvisas(kwargs):
    with pytest.raises(RiskanalysFel):las(xhtml(**kwargs))

@pytest.mark.parametrize('change',[
 lambda s:s.replace(b'scale="0" decimals="0"',b'scale="1000000" decimals="0"'),
 lambda s:s.replace(b'2024-12-31',b'2023-12-31'),
 lambda s:s.replace(b'<html ',b'<!DOCTYPE html [<!ENTITY x "test">]><html '),
 lambda s:s.replace(b'<x:unit id="kr">',b'<x:unit id="kr"><x:divide/>'),
])
def test_ogiltiga_format_och_perioder_avvisas(change):
    with pytest.raises(RiskanalysFel):las(change(xhtml()))

def test_zip_sokvag_och_flera_rapporter_avvisas():
    from riskanalys.foretagsdata.arsredovisning import las_arsredovisning
    for raw in (paket(namn='../rapport.xhtml'), b'ej zip'):
        with pytest.raises(RiskanalysFel):las_arsredovisning(raw,ORG,date(2024,12,31),'doc')
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:
        z.writestr('a.xhtml',xhtml());z.writestr('b.xhtml',xhtml(exakt='1234600'))
    with pytest.raises(RiskanalysFel):las_arsredovisning(buf.getvalue(),ORG,date(2024,12,31),'doc')


def test_skadad_deflate_ger_begripligt_fel():
    from riskanalys.foretagsdata.arsredovisning import las_arsredovisning
    raw=bytearray(paket())
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        f=z.infolist()[0]
        offset=f.header_offset+30+len(f.filename.encode())+len(f.extra)
    raw[offset:offset+3]=b'\xff\xff\xff'
    with pytest.raises(RiskanalysFel):las_arsredovisning(bytes(raw),ORG,date(2024,12,31),'doc')
