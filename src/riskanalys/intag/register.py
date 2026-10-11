"""Överför bara uttryckligen bekräftade förslag genom vanlig svarshantering."""
from datetime import date
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.lagring import registerlas, las_bild
from riskanalys.intag.modeller import IntagSvar


def bekrafta_register(tjanst, summa: str, falt: str, roll: str, datum: date, revision: str):
    if not roll.strip() or len(roll)>200:
        raise RiskanalysFel('Ange funktionen som bekräftar uppgiften, högst 200 tecken.')
    with registerlas(tjanst.mapp):
        bild = las_bild(tjanst.mapp)
        if not bild or bild.summa != summa:
            raise RiskanalysFel('Registerunderlaget har ändrats i en annan flik. Läs om förslagen och kontrollera dem igen.')
        if falt not in bild.forslag():
            raise RiskanalysFel('Den uppgiften kan inte bekräftas från registret. Besvara den ordinarie verksamhetsfrågan.')
        if bild.hamtningsdag > tjanst.profil().byra.datum:
            raise RiskanalysFel('En aktuell registerbild kan inte styrka en historisk bedömning. Använd historiskt underlag och den vanliga frågan.')
        if datum < bild.hamtningsdag:
            raise RiskanalysFel('Bekräftelsedatum får inte ligga före hämtningen/importen.')
        return tjanst.spara(IntagSvar(falt=falt,text=str(bild.forslag()[falt]),kalla=bild.hanvisning(),roll=roll,datum=datum),revision)


def valda_falt(data, bild):
    """Värden hämtas alltid ur bilden, aldrig ur klientens textfält."""
    markers={k.removeprefix('val_'):v for k,v in data.items() if k.startswith('val_')}
    if not markers or set(markers)-set(bild.forslag()) or any(v!='ja' for v in markers.values()):
        raise RiskanalysFel('Välj minst ett tillgängligt registerförslag att godkänna.')
    return tuple(id for id in ('P-ORG.sateslan','P-ORG.namn','P-ORG.verksamhetsstallen','P-ORG.koncernmoder') if id in markers)


def registersvar(bild, ids, roll, datum):
    if not roll.strip() or len(roll)>200:
        raise RiskanalysFel('Ange funktionen som bekräftar uppgifterna, högst 200 tecken.')
    if datum < bild.hamtningsdag:
        raise RiskanalysFel('Bekräftelsedatum får inte ligga före hämtningen/importen.')
    return tuple(IntagSvar(falt=id,text=str(bild.forslag()[id]),kalla=bild.hanvisning(),roll=roll,datum=datum) for id in ids)


def bekrafta_samlat(tjanst, data, datum):
    with registerlas(tjanst.mapp):
        bild=las_bild(tjanst.mapp)
        if not bild or bild.summa!=data.get('bildsumma'):
            raise RiskanalysFel('Registerunderlaget har ändrats i en annan flik. Läs om sidan.')
        ids=valda_falt(data,bild)
        p=tjanst.profil()
        from riskanalys.intag.tjanst import profilrevision
        if profilrevision(p)!=data.get('revision'):
            raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan.')
        if bild.hamtningsdag>p.byra.datum:
            raise RiskanalysFel('En aktuell registerbild kan inte styrka en historisk bedömning. Använd historiskt underlag.')
        for id in ids:
            u=p.uppgifter.get(id)
            if u and u.varde is not None and u.varde!=bild.forslag()[id] and data.get('ersatt_'+id)!='ja':
                raise RiskanalysFel('Registerförslaget avviker. Markera uttryckligen att det sparade svaret får ersättas, eller behåll ditt svar.')
        return tjanst.spara_flera(registersvar(bild,ids,data.get('roll',''),datum),data.get('revision',''))
