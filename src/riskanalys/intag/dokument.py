"""Hela befintliga dokumentkedjan, utan att attestera eller fastställa något."""
from datetime import date
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


def skapa_utkast(byramapp: Path, rb, leverantor) -> Path:
    from riskanalys.profil.text import kontrollera_profiltext
    profil = las_profil(byramapp)
    kontrollera_profiltext(profil)
    t = tackning(rb, profil)
    if not t.komplett:
        raise RiskanalysFel('Komplettera intaget före skrivning: ' + ', '.join(t.saknade) + '\n' + '\n'.join(t.hinder))
    historik = historikens_kontrollsumma(byramapp)
    kor_bedomning(byramapp,rb)
    mapp=kor_skrivning(byramapp,rb,leverantor)
    if any(isinstance(p,Skrivresultat) and not p.godkant_utkast for p in las_skrivresultat(mapp)):
        raise RiskanalysFel('AI-texten underkändes. Se de sparade skrivförsöken och rätta underlaget före ett nytt försök.')
    bedomningsnamn = manifestets_metadata(mapp, 'bedomning')['bedomning']
    granskning = kor_granskning(byramapp,rb,date.today(),
                               bedomningsmapp=byramapp / BEDOMNINGAR / bedomningsnamn, utkastmapp=mapp)
    fil = kor_export_utkast(byramapp,date.today(),granskningsmapp=granskning) / UTKASTFIL
    if historik != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken ändrades under skrivningen. Skapa ett nytt utkast.')
    kontrollera_utkast(byramapp, rb, fil)
    return fil


def kontrollera_utkast(byramapp: Path, rb, fil: Path) -> None:
    if verifiera_manifest(fil.parent):
        raise RiskanalysFel('Exporten är ändrad. Skapa ett nytt utkast.')
    metadata = manifestets_metadata(fil.parent, 'granskning')
    namn = metadata['granskning']
    if not namn or Path(namn).name != namn:
        raise RiskanalysFel('Exportens granskningsreferens är ogiltig. Skapa ett nytt utkast.')
    granskning = byramapp / GRANSKNING / namn
    kontrollera_kallor(byramapp, granskning)
    underlag = granskningens_metadata(granskning)
    if underlag['historik'] != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken har ändrats. Granska och exportera ett nytt utkast.')
    kontrollera_aktuell(byramapp, byramapp / BEDOMNINGAR / underlag['bedomning'], rb)


def uppdatera_export(byramapp: Path, rb, tidigare: Path) -> Path:
    """En ändrad utvärdering kräver granskning och export, inte ny AI-text."""
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
    granskning = kor_granskning(byramapp, rb, date.today(), bedomningsmapp=bedomningsmapp,
                               utkastmapp=byramapp / UTKAST / underlag['utkast'])
    fil = kor_export_utkast(byramapp, date.today(), granskningsmapp=granskning) / UTKASTFIL
    if historik != historikens_kontrollsumma(byramapp):
        raise RiskanalysFel('Utvärderingshistoriken ändrades under exporten. Försök igen.')
    kontrollera_utkast(byramapp, rb, fil)
    return fil
