"""Gemensamma utkastflöden för ingångar utan transportberoenden."""
from datetime import date
from contextlib import nullcontext
from pathlib import Path
from riskanalys.bedomning.korning import kor_bedomning, BEDOMNINGAR, kontrollera_aktuell
from riskanalys.dokument.export import kor_export_utkast, UTKASTFIL
from riskanalys.dokument.skrivning import kor_skrivning, las_skrivresultat, Skrivresultat, UTKAST
from riskanalys.granskning.korning import kor_granskning, GRANSKNING, granskningens_metadata, kontrollera_kallor
from riskanalys.drift.historik import historikens_kontrollsumma
from riskanalys.lagring.manifest import manifestets_metadata, verifiera_manifest
from riskanalys.intag.tackning import tackning
from riskanalys.profil.lagring import las_profil
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.dokument.leverantor import Textleverantor


def skapa_utkast(byramapp: Path, rb: Regelbas, leverantor: Textleverantor) -> Path:
    from riskanalys.profil.text import kontrollera_profiltext
    profil = las_profil(byramapp)
    kontrollera_profiltext(profil)
    t = tackning(rb, profil)
    if not t.utkastklart:
        raise RiskanalysFel('Komplettera intaget före skrivning: ' + ', '.join(t.saknade) + '\n' + '\n'.join(t.hinder))
    historik = historikens_kontrollsumma(byramapp)
    kor_bedomning(byramapp,rb)
    mapp=kor_skrivning(byramapp,rb,leverantor)
    if any(isinstance(p,Skrivresultat) and not p.godkant_utkast for p in las_skrivresultat(mapp)):
        raise RiskanalysFel('AI-texten underkändes. Se de sparade skrivförsöken och rätta underlaget före ett nytt försök.')
    bedomningsnamn = manifestets_metadata(mapp, 'bedomning')['bedomning']
    granskning = kor_granskning(byramapp,rb,date.today(),
                               bedomningsmapp=byramapp / BEDOMNINGAR / bedomningsnamn, utkastmapp=mapp)
    fil = kor_export_utkast(byramapp,date.today(),granskningsmapp=granskning,regelbas=rb) / UTKASTFIL
    if historik != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken ändrades under skrivningen. Skapa ett nytt utkast.')
    kontrollera_utkast(byramapp, rb, fil)
    return fil


def kontrollera_utkast(byramapp: Path, rb: Regelbas, fil: Path) -> None:
    if verifiera_manifest(fil.parent):
        raise RiskanalysFel('Exporten är ändrad. Skapa ett nytt utkast.')
    metadata = manifestets_metadata(fil.parent, 'granskning')
    namn = metadata['granskning']
    if not namn or Path(namn).name != namn:
        raise RiskanalysFel('Exportens granskningsreferens är ogiltig. Skapa ett nytt utkast.')
    granskning = byramapp / GRANSKNING / namn
    kontrollera_kallor(byramapp, granskning)
    if (fil.parent/'granskning').is_dir():
        from riskanalys.lagring.kontrollsumma import for_fil
        if for_fil(fil.parent/'granskning/manifest.json') != for_fil(granskning/'manifest.json'):
            raise RiskanalysFel('Exporten hör till en annan granskningskälla. Granska och exportera igen.')
    underlag = granskningens_metadata(granskning)
    if underlag['historik'] != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken har ändrats. Granska och exportera ett nytt utkast.')
    kontrollera_aktuell(byramapp, byramapp / BEDOMNINGAR / underlag['bedomning'], rb)
    if rb.metod.omfattning:
        from riskanalys.analys.lagring import las_analys
        from riskanalys.granskning.analysunderlag import las_fryst_analys, registerhinder
        snapshot = las_fryst_analys(granskning)
        # Ett första utkast får sakna lokal analys; en tillagd eller borttagen analys gör det inaktuellt.
        if snapshot.paket is not None or las_analys(byramapp) is not None:
            hinder = registerhinder(byramapp, snapshot)
            if hinder:
                raise RiskanalysFel(' '.join(hinder) + ' Uppdatera Word-utkastet utan nya AI-anrop.')


def las_utkast(byramapp: Path, rb: Regelbas, fil: Path) -> bytes:
    """Håll profil/analys/drift oförändrade från aktualitetskontroll till läst Word-fil."""
    from riskanalys.analys.lagring import analyslas
    with analyslas(byramapp) if rb.metod.omfattning else nullcontext():
        kontrollera_utkast(byramapp, rb, fil)
        return fil.read_bytes()


def uppdatera_export(byramapp: Path, rb: Regelbas, tidigare: Path, *, rapportformat: str | None = None) -> Path:
    from riskanalys.analys.lagring import analyslas
    with analyslas(byramapp) if rb.metod.omfattning else nullcontext():
        return _uppdatera_export_last(byramapp,rb,tidigare,rapportformat=rapportformat)


def _uppdatera_export_last(byramapp: Path, rb: Regelbas, tidigare: Path, *, rapportformat: str | None = None) -> Path:
    """Lokal analys eller utvärdering kan granskas och exporteras från befintlig AI-text."""
    if rapportformat not in (None,'v8','v9','v10','v10-redaktionell'):
        raise RiskanalysFel('Välj rapportformat v8, v9, v10 eller v10-redaktionell.')
    historik = historikens_kontrollsumma(byramapp)
    if verifiera_manifest(tidigare.parent):
        raise RiskanalysFel('Det tidigare utkastet är ändrat. Skapa ett nytt utkast.')
    namn = manifestets_metadata(tidigare.parent, 'granskning')['granskning']
    if not namn or Path(namn).name != namn:
        raise RiskanalysFel('Granskningsreferensen är ogiltig. Skapa ett nytt utkast.')
    gammal = byramapp / GRANSKNING / namn
    kontrollera_kallor(byramapp, gammal)
    underlag = granskningens_metadata(gammal)
    bedomningsmapp = byramapp / BEDOMNINGAR / underlag['bedomning']
    kontrollera_aktuell(byramapp, bedomningsmapp, rb)
    if not underlag['utkast']:
        raise RiskanalysFel('Tidigare AI-riskavsnitt saknas. Skapa ett nytt utkast.')
    from riskanalys.granskning.korning import _kor_granskning_last, las_granskning
    sparat=las_granskning(gammal)[0].formatversion
    valt=rapportformat or {'D-ARB-tjanst-v8':'v8','D-ARB-resultat-v9':'v9','D-ARB-resultat-v10':'v10'}.get(sparat)
    if rapportformat is None and sparat=='D-ARB-resultat-v10':
        from riskanalys.dokument.presentationsval_v10 import las_version
        from riskanalys.dokument.redaktionspresentation_v10 import VERSION
        if las_version(gammal)==VERSION:valt='v10-redaktionell'
    if valt is None:
        raise RiskanalysFel('Det äldre utkastet kräver en uttrycklig ny V8-skrivning före formatbyte.')
    granskning = _kor_granskning_last(byramapp, rb, date.today(), bedomningsmapp=bedomningsmapp,
                               utkastmapp=byramapp / UTKAST / underlag['utkast'],rapportformat=valt)
    if las_granskning(granskning)[0].formatversion=='D-ARB-resultat-v10':
        from riskanalys.dokument.export import exportera_v10_last
        fil=exportera_v10_last(byramapp,date.today(),granskning,regelbas=rb)/UTKASTFIL
    elif las_granskning(granskning)[0].formatversion=='D-ARB-resultat-v9':
        from riskanalys.dokument.export import exportera_v9_last
        fil=exportera_v9_last(byramapp,date.today(),granskning,regelbas=rb)/UTKASTFIL
    elif las_granskning(granskning)[0].formatversion=='D-ARB-tjanst-v8':
        from riskanalys.dokument.export import exportera_v8_last
        fil=exportera_v8_last(byramapp,date.today(),granskning,regelbas=rb)/UTKASTFIL
    else:
        fil = kor_export_utkast(byramapp, date.today(), granskningsmapp=granskning) / UTKASTFIL
    if historik != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken ändrades under exporten. Försök igen.')
    kontrollera_utkast(byramapp, rb, fil)
    return fil

