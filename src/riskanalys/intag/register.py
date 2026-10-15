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
        if falt in ('P-ORG.utlandsk_filial', 'P-BESK.verksamhet', 'P-VERK.omsattning'):
            raise RiskanalysFel('Använd samlat godkännande för Bolagsverkets förslag och period.')
        if falt not in bild.forslag():
            raise RiskanalysFel('Den uppgiften kan inte bekräftas från registret. Besvara den ordinarie verksamhetsfrågan.')
        if bild.hamtningsdag > tjanst.profil().byra.datum:
            raise RiskanalysFel('En aktuell registerbild kan inte styrka en historisk bedömning. Använd historiskt underlag och den vanliga frågan.')
        if datum < bild.hamtningsdag:
            raise RiskanalysFel('Bekräftelsedatum får inte ligga före hämtningen/importen.')
        return tjanst.spara(IntagSvar(falt=falt,text=str(bild.forslag()[falt]),kalla=bild.hanvisning(),roll=roll,datum=datum),revision)


def tillgangliga_forslag(bild, profil=None):
    resultat = bild.forslag()
    if 'P-VERK.omsattning' in resultat and profil:
        period = bild.bolagsverket.bokslut.period
        andra_perioder = [u.period for id, u in profil.uppgifter.items()
                          if id != 'P-VERK.omsattning' and id.startswith(('P-KUND.', 'P-TJ.'))
                          and u.period and profil.ar_bekraftad(id)]
        if period.till > profil.byra.datum or any(p != period for p in andra_perioder):
            resultat.pop('P-VERK.omsattning')
    return resultat


def valda_falt(data, bild, profil=None):
    """Värden hämtas alltid ur bilden, aldrig ur klientens textfält."""
    markers={k.removeprefix('val_'):v for k,v in data.items() if k.startswith('val_')}
    if not markers or set(markers)-set(tillgangliga_forslag(bild, profil)) or any(v!='ja' for v in markers.values()):
        raise RiskanalysFel('Välj minst ett tillgängligt registerförslag att godkänna.')
    return tuple(id for id in ('P-ORG.sateslan','P-ORG.utlandsk_filial','P-ORG.namn','P-ORG.verksamhetsstallen','P-ORG.koncernmoder','P-VERK.omsattning','P-BESK.verksamhet') if id in markers)


def registersvar(bild, ids, roll, datum, data=None):
    if not roll.strip() or len(roll)>200:
        raise RiskanalysFel('Ange funktionen som bekräftar uppgifterna, högst 200 tecken.')
    if datum < bild.hamtningsdag:
        raise RiskanalysFel('Bekräftelsedatum får inte ligga före hämtningen/importen.')
    data = data or {}
    resultat = []
    for id in ids:
        text = str(bild.forslag()[id])
        kalla = bild.faltkalla(id)
        period = None
        if id == 'P-VERK.omsattning':
            if data.get('bokslutsperiod') != 'ja':
                raise RiskanalysFel('Bekräfta att bokslutsperioden är den statistikperiod som ska användas.')
            period = bild.bolagsverket.bokslut.period
        if id == 'P-BESK.verksamhet':
            text = data.get('verksamhetstext', text).strip()
            kalla += '; registrerad beskrivning granskad och kompletterad av uppgiftslämnaren'
        resultat.append(IntagSvar(falt=id, text=text, kalla=kalla, roll=roll, datum=datum, period=period))
    return tuple(resultat)


def bekrafta_samlat(tjanst, data, datum):
    with registerlas(tjanst.mapp):
        bild=las_bild(tjanst.mapp)
        if not bild or bild.summa!=data.get('bildsumma'):
            raise RiskanalysFel('Registerunderlaget har ändrats i en annan flik. Läs om sidan.')
        p=tjanst.profil()
        ids=valda_falt(data,bild,p)
        from riskanalys.intag.tjanst import profilrevision
        if profilrevision(p)!=data.get('revision'):
            raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan.')
        if bild.hamtningsdag>p.byra.datum:
            raise RiskanalysFel('En aktuell registerbild kan inte styrka en historisk bedömning. Använd historiskt underlag.')
        svar = registersvar(bild, ids, data.get('roll',''), datum, data)
        for id in ids:
            u=p.uppgifter.get(id)
            nytt = next(v for v in svar if v.falt == id)
            nytt_varde = nytt.text if id == 'P-BESK.verksamhet' else bild.forslag()[id]
            if u and u.varde is not None and (u.varde != nytt_varde or u.period != nytt.period) and data.get('ersatt_'+id)!='ja':
                raise RiskanalysFel('Registerförslaget avviker. Markera uttryckligen att det sparade svaret får ersättas, eller behåll ditt svar.')
        return tjanst.spara_flera(svar,data.get('revision',''))
