"""Komplettera SCB-bilden utan att göra registerhämtning till bekräftelse."""
from datetime import date, datetime
import hashlib
from pathlib import Path
from pydantic import ValidationError
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.arsredovisning import las_arsredovisning
from riskanalys.foretagsdata.lagring import registerlas, _atomiskt
from riskanalys.foretagsdata.modeller import Bolagsverksbild, Registerbild


def _text(rad, falt, nyckel):
    obj = rad.get(falt, {})
    return obj.get(nyckel) if not obj.get('status') else None


def _original(mapp: Path, raw: bytes):
    with registerlas(mapp) as register:
        original = register / 'original'
        original.mkdir(mode=0o700, exist_ok=True)
        path = original / (hashlib.sha256(raw).hexdigest() + '.zip')
        if path.exists():
            if path.read_bytes() != raw:
                raise RiskanalysFel('Årsredovisningens sparade original har ändrats. Återställ originalet.')
        else:
            _atomiskt(path, raw)


def komplettera_bolagsverket(bild: Registerbild, leverantor, mapp: Path) -> Registerbild:
    data = leverantor.hamta(bild.orgnr)
    if data['orgnr'] != bild.orgnr or len(data['organisationer']) != 1:
        raise RiskanalysFel('Bolagsverket och SCB gäller inte en entydig gemensam juridisk person.')
    rad = data['organisationer'][0]
    namn = [n['namn'] for n in rad.get('organisationsnamn', {}).get('organisationsnamnLista', [])
            if n.get('organisationsnamntyp', {}).get('kod') == 'FORETAGSNAMN' and n.get('namn')]
    bakgrund = []
    for falt, key, label in (
        ('organisationsdatum', 'registreringsdatum', 'Registreringsdatum'),
        ('verksamOrganisation', 'kod', 'Verksam enligt registerkriterier (kod)'),
        ('avregistreradOrganisation', 'avregistreringsdatum', 'Avregistreringsdatum'),
        ('avregistreringsorsak', 'klartext', 'Avregistreringsorsak'),
    ):
        value = _text(rad, falt, key)
        bakgrund.append((label, str(value) if value is not None else 'Uppgift saknas eller kunde inte hämtas'))
    forfarande = rad.get('pagaendeAvvecklingsEllerOmstruktureringsforfarande', {})
    poster = forfarande.get('pagaendeAvvecklingsEllerOmstruktureringsforfarandeLista', [])
    bakgrund.append(('Pågående förfaranden', '; '.join(str(p.get('klartext') or p.get('kod', '')) for p in poster) or 'Uppgift saknas; inget intyg om frånvaro'))
    bokslut = None
    notis = 'Ingen tillgänglig digital årsredovisning i dokumentlistan. Ange omsättning manuellt.'
    try:
        docs = data['dokument']
        if docs:
            # Ogiltig metadata eller flera dokument vid samma periodslut ger inget tyst urval.
            dates = [(date.fromisoformat(str(d['rapporteringsperiodTom'])), d) for d in docs]
            senaste = max(t for t, d in dates)
            valda = [d for t, d in dates if t == senaste]
            if len(valda) != 1 or valda[0].get('filformat', '').lower() != 'ixbrl':
                raise RiskanalysFel('Senaste årsredovisningen är inte entydig i iXBRL-format. Kontrollera dokumentlistan manuellt.')
            raw = leverantor.hamta_dokument(valda[0]['dokumentId'])
            _original(mapp, raw)
            bokslut = las_arsredovisning(raw, bild.orgnr, senaste, valda[0]['dokumentId'])
            notis = ''
    except RiskanalysFel as exc:
        notis = str(exc)
    except (ValueError, KeyError, TypeError):
        notis = 'Dokumentlistans period eller format kunde inte tolkas. Ange omsättning manuellt.'
    try:
        bv = Bolagsverksbild(orgnr=bild.orgnr, hamtad=datetime.fromisoformat(data['hamtad']),
                            namn=namn[0] if len(namn) == 1 else None,
                            organisationsform=_text(rad, 'organisationsform', 'kod'),
                            verksamhet=_text(rad, 'verksamhetsbeskrivning', 'beskrivning'),
                            bakgrund=tuple(bakgrund), bokslut=bokslut, bokslutsnotis=notis)
        return Registerbild.model_validate({**bild.model_dump(), 'schema_version': 4, 'bolagsverket': bv})
    except (ValueError, ValidationError):
        raise RiskanalysFel('Bolagsverkets underlag kunde inte kopplas till registerbilden. Tidigare förslag behålls.') from None
