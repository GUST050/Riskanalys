"""Fryst lokal analys och verifierade belägg för dokumentets återbyggnad."""
import json
from pathlib import Path

from riskanalys.analys.lagring import Analyssnapshot, las_belaggsfil
from riskanalys.analys.modeller import Analyspaket
from riskanalys.analys.provning import registersumma
from riskanalys.drift.modellrisk import Modellvalidering, kontrollera_rapportkoppling
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes

SNAPSHOTFIL = 'analys/snapshot.json'


def spara_fryst_analys(rot: Path, snapshot: Analyssnapshot) -> None:
    """Spara bara de redan kontrollerade bytes som byggaren fick se."""
    (rot/'analys/belagg').mkdir(parents=True, exist_ok=True, mode=0o700)
    for namn, data in snapshot.filer:
        # Referenserna har kontrollerats av AB2:s säkra läsare innan snapshot skapades.
        p = Path(namn)
        if p.is_absolute() or '..' in p.parts or '\\' in namn or ':' in namn:
            raise RiskanalysFel('Analyskopian innehåller en otillåten beläggssökväg.')
        fil = rot/'analys/belagg'/p
        fil.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fil.write_bytes(data)
    data = dict(paket=snapshot.paket.model_dump(mode='json') if snapshot.paket else None,
                registersumma=snapshot.registersumma, brister=snapshot.brister,
                filer={namn:for_bytes(data) for namn,data in snapshot.filer})
    (rot/SNAPSHOTFIL).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def las_fryst_analys(rot: Path) -> Analyssnapshot:
    """Historisk läsning kontrollerar sparade bytes, aldrig dagens modellkod."""
    try:
        data=json.loads((rot/SNAPSHOTFIL).read_text(encoding='utf-8'))
        paket=Analyspaket.model_validate(data['paket']) if data['paket'] is not None else None
        summa=registersumma(paket) if paket else ''
        if summa!=data['registersumma']:
            raise ValueError('Fel analysbindning')
        filer=tuple((namn,las_belaggsfil(rot,namn,hash)) for namn,hash in sorted(data['filer'].items()))
        return Analyssnapshot(paket,summa,tuple(data['brister']),filer)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise RiskanalysFel('Den frysta analyskopian är skadad. Återställ granskningen eller granska igen.') from exc


def fryst_modellrapport(snapshot: Analyssnapshot) -> Modellvalidering | None:
    """Visa endast descriptor som motsvarar frysta faktiska tre rapportkopior."""
    u=snapshot.paket.modellrisk if snapshot.paket else None
    if u is None:return None
    filer=dict(snapshot.filer)
    try:
        def data(b):
            raw=filer[b.fil]
            if for_bytes(raw)!=b.kontrollsumma:raise ValueError('Ändrad rapport')
            return raw
        rapport=Modellvalidering.model_validate_json(data(u.projektrapport))
        kontrollera_rapportkoppling(rapport,data(u.modellfiler),data(u.valideringsrapport))
        if rapport.modellbindning!=u.modellbindning:return None
        return rapport
    except (KeyError,ValueError,RiskanalysFel):
        return None


def registerhinder(byramapp: Path,snapshot: Analyssnapshot) -> tuple[str,...]:
    from riskanalys.analys.lagring import las_analys
    aktuell=las_analys(byramapp)
    if snapshot.paket is None or aktuell is None or registersumma(aktuell)!=snapshot.registersumma:
        return ('Analysregistret har ändrats eller saknas. Granska det aktuella underlaget igen.',)
    return ()


def aktuell_analys_hinder(byramapp,rb,granskningsmapp,datum,*,krav_godkand=True):
    """Anroparen håller analyslas genom kontroll och efterföljande publicering."""
    from riskanalys.analys.lagring import analysaktualitetshinder
    from riskanalys.bedomning.korning import BEDOMNINGAR,las_bedomning,las_bedomningsprofil
    from riskanalys.dokument.skrivning import UTKAST
    from riskanalys.drift.modellrisk import modellriskhinder
    from riskanalys.granskning.korning import granskningens_metadata
    from riskanalys.granskning.dokument_v6 import analyshinder
    snapshot=las_fryst_analys(granskningsmapp)
    hinder=list(registerhinder(byramapp,snapshot))
    metadata=granskningens_metadata(granskningsmapp)
    if metadata.get('analysbindning')!=snapshot.registersumma:
        hinder.append('Granskningens analysbindning saknas eller avviker. Granska igen.')
    if snapshot.paket is None:return (*hinder,'Lokal analys saknas.')
    bm=byramapp/BEDOMNINGAR/metadata['bedomning']
    um=byramapp/UTKAST/metadata['utkast']
    hinder.extend(analysaktualitetshinder(byramapp,rb,snapshot.paket,datum,
        bedomningsmapp=bm,utkastmapp=um,krav_modellrisk=krav_godkand))
    if krav_godkand:
        hinder.extend(snapshot.brister)
        hinder.extend(analyshinder(rb,las_bedomningsprofil(bm),las_bedomning(bm),snapshot.paket,datum=datum))
        hinder.extend(modellriskhinder(granskningsmapp,rb,snapshot.paket.modellrisk,datum))
    return tuple(dict.fromkeys(hinder))
