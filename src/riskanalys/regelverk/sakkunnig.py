"""Granskningsbeslut binds till innehåll; atomisk import skriver en lokal attestfil."""

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import skriv_manifest
from riskanalys.lagring.yamlfil import las_yaml, spara_yaml
from riskanalys.regelverk.modeller import Regelbas, Sakkunnig, Strikt, _summa, utan_granskningsmetadata
from riskanalys.regelverk.urval import valj


class Objektbeslut(Strikt):
    beslut: Literal['ej_granskad', 'verifierad', 'ändras']
    kommentar: str = ''


class Granskningsbeslut(Strikt):
    paket: str
    version: str
    datum: date
    granskningsdatum: date
    kontrollsumma: str
    granskare: str
    kompetens: str
    oberoende: bool
    objekt: dict[str, Objektbeslut]


def granskningsobjekt(rb: Regelbas, paket_id: str) -> dict[str, str]:
    """Samla rättsliga objekt och metodval; tillsynsfacit granskas separat."""
    rb.paketets_innehallssumma(paket_id)  # Kontrollera ID före åtkomst till paketet.
    objekt = {k: rb.kravets_innehallssumma(k) for k in rb.regelpaket[paket_id].krav}
    objekt['PARAGRAFKARTA'] = rb.kartans_innehallssumma(paket_id)
    for namn in ('hot', 'sarbarheter', 'kontroller', 'tjanster'):
        for id, post in getattr(rb, namn).items():
            objekt[id] = _summa(utan_granskningsmetadata(post.model_dump(mode='json')))
    for post in (*rb.metod.riskmatris, *rb.metod.regler(), rb.skalmappning, rb.sanktionsmetod):
        if post is not None:
            objekt[post.id] = _summa(utan_granskningsmetadata(post.model_dump(mode='json')))
    if rb.kundmall:
        for rad in rb.kundmall.rader:
            objekt[rad.id] = _summa(utan_granskningsmetadata(rad.model_dump(mode='json')))
        objekt['KUNDMETOD-C'] = rb.kundmall.c_innehallssumma()
    return objekt


def exportera_sakkunnigunderlag(rot: Path, paket_id: str, datum: date, utmapp: Path) -> Path:
    """Exportera innehåll, obesvarade beslutsmallar och manifest utan AI-anrop."""
    from riskanalys.regelverk.facit import exportera_facitmall
    from riskanalys.regelverk.laddning import LYDELSETEXTER, ladda_regelbas
    from riskanalys.regelverk.validering import validera

    rb = ladda_regelbas(rot)
    fel = validera(rb)
    if fel:
        raise RiskanalysFel('Rätta regelbasen före export: ' + '; '.join(fel))
    summa = rb.paketets_innehallssumma(paket_id)
    valj(rb, paket_id, datum, rb.regelpaket[paket_id].lan[0])
    if utmapp.exists() and any(utmapp.iterdir()):
        raise RiskanalysFel(f'{utmapp} är inte tom. Välj en ny granskningsmapp.')
    utmapp.mkdir(parents=True, exist_ok=True)
    data = utan_granskningsmetadata(rb.model_dump(mode='json', exclude={'kontrollsumma'}))
    data['val'] = {'paket': paket_id, 'datum': datum.isoformat(), 'kontrollsumma': summa}
    data['lydelsetexter'] = {
        k: (rot / LYDELSETEXTER / f'{k}.txt').read_text(encoding='utf-8') for k in rb.lydelser
    }
    (utmapp / 'underlag.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    mall = Granskningsbeslut(
        paket=paket_id, version=rb.version, datum=datum, granskningsdatum=datum, kontrollsumma=summa,
        granskare='', kompetens='', oberoende=False,
        objekt={k: Objektbeslut(beslut='ej_granskad') for k in granskningsobjekt(rb, paket_id)},
    )
    spara_yaml(utmapp / 'granskningsmall.yaml', mall.model_dump(mode='python'))
    if rb.facit:
        (utmapp / 'facit.json').write_text(json.dumps(rb.facit, ensure_ascii=False, indent=2), encoding='utf-8')
        exportera_facitmall(rb.facit, datum, utmapp / 'facitgranskningsmall.yaml')
    (utmapp / 'granskning.md').write_text(_granskningsinstruktion(mall), encoding='utf-8')
    skriv_manifest(utmapp, {'typ': 'sakkunnigunderlag', 'regelpaket': paket_id, 'innehallssumma': summa})
    return utmapp


def _granskningsinstruktion(mall: Granskningsbeslut) -> str:
    """Beskriv vad som måste prövas av en verklig sakkunnig före frigivning."""
    text = (
        f'# Sakkunnigunderlag {mall.paket}\n\n'
        f'Version {mall.version}, rättsligt datum {mall.datum}, summa {mall.kontrollsumma}.\n\n'
        'Granska inventarium, samtliga lydelser/datum, yrkesroller/län, paragrafkarta och typade mål. '
        'Granska alla metodval, källskalor, sanktionsdimensionen samt kundspår A–D med egna undantag. '
        'Alla objekt måste få beslut och kommentar.\n\n'
        'Facit är negativt underlag från två tillsynsfall, inte universellt positivt facit. '
        'Dess 17 fynd och fem kontrollvarianter är ännu inte produktutvärderade. '
        'Granska dem i facitgranskningsmall.yaml, separat från regelpaketet. '
        'Facitbeslut binds till hela facitfilens version och innehållssumma. '
        'Facitimport frigör inget regelpaket; en facitrevision upphäver bara facitets egen attest.\n\n'
        'Verifiera identitet, oberoende och PTL/FS/metodkompetens utanför programmet. '
        'Metadata i YAML bevisar ingen kompetens. Rättslig status/laga kraft och NRA-grafik samt '
        'tabell 1 i tre FS-PDF:er måste kontrolleras manuellt. '
        'EU269 är avgränsat till artikel 2 med ett återgivet engelskt EUT-källutdrag; kontrollera '
        'autentiskt original, ägande/kontroll och individuella undantag/tillstånd. '
        'Andra sanktionsprogram omfattas inte. C-förslaget är ingen frigiven produktionsformel '
        'och ska kompletteras och prövas i M3.\n\n'
        'Granskningsbesluten innehåller personuppgifter och sparas lokalt utanför offentligt Git. '
        'Motstridiga aktuella beslut om gemensamma objekt stoppar alla berörda paket tills '
        'besluten har samordnats och ersatts.\n\n'
    )
    return text + '\n'.join(f'- {k}' for k in mall.objekt)


def kontrollera_beslut(b: Granskningsbeslut, rb: Regelbas, paket_id: str) -> None:
    """Bind ett importbeslut till giltigt innehåll, rätt paket och rättsligt datum."""
    from riskanalys.regelverk.validering import validera

    fel = validera(rb)
    if fel:
        raise RiskanalysFel('Rätta regelbasen före granskningsimport: ' + '; '.join(fel))
    if paket_id not in rb.regelpaket:
        raise RiskanalysFel(f'Okänt regelpaket {paket_id}. Välj ett befintligt paket och exportera en ny granskningsmall.')
    if (b.paket != paket_id or b.version != rb.version
            or b.kontrollsumma != rb.paketets_innehallssumma(paket_id)):
        raise RiskanalysFel('Granskningens paket, version eller innehållssumma har ändrats. Exportera och granska på nytt.')
    valj(rb, paket_id, b.datum, rb.regelpaket[paket_id].lan[0])
    kontrollera_attestmetadata(b, rb, paket_id)


def kontrollera_attestmetadata(b: Granskningsbeslut, rb: Regelbas, paket_id: str) -> None:
    """Kräv identitet, oberoende och fullständiga beslut även vid återinläsning."""
    if b.granskningsdatum < b.datum or not b.granskare.strip() or not b.kompetens.strip() or not b.oberoende:
        raise RiskanalysFel('Ange granskare, kompetens, oberoende och granskningsdatum efter underlagets datum.')
    if set(b.objekt) != set(granskningsobjekt(rb, paket_id)):
        raise RiskanalysFel('Granskningen har saknade eller okända objekt. Exportera en ny granskningsmall.')
    if any(post.beslut == 'ej_granskad' or not post.kommentar.strip() for post in b.objekt.values()):
        raise RiskanalysFel('Varje objekt kräver beslut verifierad/ändras och kommentar före import.')


def las_granskningsfil(fil: Path, regelbas: Regelbas, paket_id: str) -> Granskningsbeslut:
    """Läs och validera en sakkunnigfil före import."""
    try:
        beslut = Granskningsbeslut.model_validate(las_yaml(fil))
    except ValidationError as exc:
        raise RiskanalysFel(f'Granskningsfilen {fil} har fel. Rätta mot den exporterade mallen.') from exc
    kontrollera_beslut(beslut, regelbas, paket_id)
    return beslut


def applicera_attester(rb: Regelbas, b: Granskningsbeslut) -> Regelbas:
    """Återläs beslut; ett aktuellt ändringskrav på gemensamt innehåll har företräde."""
    if b.paket not in rb.regelpaket:
        raise RiskanalysFel('Attesten hänvisar till ett okänt paket. Exportera och granska på nytt.')
    summor = granskningsobjekt(rb, b.paket)
    aktuell = b.version == rb.version and b.kontrollsumma == rb.paketets_innehallssumma(b.paket)
    if aktuell:
        kontrollera_attestmetadata(b, rb, b.paket)

    def attest(id: str, befintlig: Sakkunnig | None = None) -> Sakkunnig:
        # Paketordningen får varken sudda ut aktuell granskning eller en konflikt.
        tidigare_aktuell = (befintlig is not None and befintlig.kontrollsumma == summor.get(id)
                            and befintlig.status in {'verifierad', 'ändras'})
        if tidigare_aktuell and (not aktuell or befintlig.status == 'ändras'):
            return befintlig
        post = b.objekt.get(id)
        return Sakkunnig(
            status=post.beslut if aktuell and post else 'ändras', av=b.granskare, datum=b.granskningsdatum,
            kontrollsumma=summor.get(id) if aktuell else b.kontrollsumma,
        )

    krav = {
        k: v.model_copy(update={'sakkunnig': attest(k, v.sakkunnig)}) if k in b.objekt else v
        for k, v in rb.krav.items()
    }
    paket = rb.regelpaket[b.paket]
    status = 'verifierad' if aktuell and all(post.beslut == 'verifierad' for post in b.objekt.values()) else 'ändras'
    paket = paket.model_copy(update={
        'granskning': Sakkunnig(status=status, av=b.granskare, datum=b.granskningsdatum, kontrollsumma=b.kontrollsumma),
        'paragrafkarta': paket.paragrafkarta.model_copy(update={'sakkunnig': attest('PARAGRAFKARTA')}),
    })
    updates = {'krav': krav, 'regelpaket': {**rb.regelpaket, b.paket: paket}}
    for namn in ('hot', 'sarbarheter', 'kontroller', 'tjanster'):
        updates[namn] = {
            k: v.model_copy(update={'sakkunnig': attest(k, v.sakkunnig)}) for k, v in getattr(rb, namn).items()
        }
    metod = rb.metod
    metoduppdateringar = {
        'riskmatris': tuple(v.model_copy(update={'sakkunnig': attest(v.id, v.sakkunnig)}) for v in metod.riskmatris),
    }
    for namn in ('sannolikhet', 'konsekvens', 'terrorfinansiering', 'kvarstaende_ej_belagd', 'kvarstaende_sankning'):
        regel = getattr(metod, namn)
        metoduppdateringar[namn] = regel.model_copy(update={'sakkunnig': attest(regel.id, regel.sakkunnig)})
    if metod.omfattning:
        regel = metod.omfattning
        metoduppdateringar['omfattning'] = regel.model_copy(update={'sakkunnig': attest(regel.id, regel.sakkunnig)})
    updates['metod'] = metod.model_copy(update=metoduppdateringar)
    for namn in ('skalmappning', 'sanktionsmetod'):
        post = getattr(rb, namn)
        if post:
            updates[namn] = post.model_copy(update={'sakkunnig': attest(post.id, post.sakkunnig)})
    if rb.kundmall:
        updates['kundmall'] = rb.kundmall.model_copy(update={
            'c_granskning': attest('KUNDMETOD-C', rb.kundmall.c_granskning),
            'rader': tuple(v.model_copy(update={'sakkunnig': attest(v.id, v.sakkunnig)}) for v in rb.kundmall.rader),
        })
    return rb.model_copy(update=updates)


def tillampa_granskning(regelbasrot: Path, beslut: Granskningsbeslut) -> None:
    """Ersätt det valda paketets lokala beslut atomiskt och bevara övriga beslut."""
    from riskanalys.regelverk.laddning import ladda_regelbas

    rb = ladda_regelbas(regelbasrot)
    kontrollera_beslut(beslut, rb, beslut.paket)
    fd, namn = tempfile.mkstemp(prefix='.granskning-', suffix='.tmp', dir=regelbasrot)
    os.close(fd)
    tmp = Path(namn)
    try:
        fil = regelbasrot / 'granskning.yaml'
        gamla = las_yaml(fil) if fil.exists() else {}
        tidigare = gamla.get('beslut', {}) if 'beslut' in gamla else ({gamla['paket']: gamla} if gamla else {})
        spara_yaml(tmp, {'beslut': {**tidigare, beslut.paket: beslut.model_dump(mode='python')}})
        kontrollera_beslut(beslut, ladda_regelbas(regelbasrot), beslut.paket)
        os.replace(tmp, regelbasrot / 'granskning.yaml')
    finally:
        tmp.unlink(missing_ok=True)
