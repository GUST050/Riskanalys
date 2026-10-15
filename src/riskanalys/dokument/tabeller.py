"""Lokala H6-tabeller från bekräftad profil och sparade motorutfall."""
from riskanalys.bedomning.erfarenheter import belagd_uppgift
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.dokument.modeller import Dokumenttabell, Tabellcell, Tabellrad
from riskanalys.profil.hantering import visa_varde_klartext
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.granser import metodgranser, metodgransindex
from riskanalys.regelverk.modeller import Regelbas


def cell(text, refs=()):
    return Tabellcell(text=str(text), referenser=tuple(dict.fromkeys(refs)))


def rad(*celler):
    return Tabellrad(celler=tuple(celler))


def tabell(id, rubrik, kolumner, rader, position=0):
    return Dokumenttabell(id=id, rubrik=rubrik, kolumner=tuple(kolumner),
                         rader=tuple(rader), fore_stycke=position)


def kort_varde(rb, profil, id, *, period=False, gransindex=None):
    """Kort visning; fulla belägg finns i B1. Samma precisionsregler som övrig lokal text."""
    if id not in rb.falt or not belagd_uppgift(rb, profil, id):
        return 'Aktuellt underlag saknas. [VERIFIERA]'
    u=profil.uppgifter[id]
    index=gransindex if gransindex is not None else metodgransindex(rb)
    text=str(visa_varde_klartext(rb.falt[id], u.varde, metodgranser(rb,id,index)))
    if period and u.period:
        text+=f' ({u.period.fran}–{u.period.till})'
    return text


def bygg_riskoversikt(bedomning: Bedomning, regelbas: Regelbas) -> Dokumenttabell:
    rader=[]
    for t in bedomning.tjanster:
        if t.erbjuds is False:
            continue
        sank=t.sanktionsrisk
        refs=(t.tjanst,*t.regelspar)
        namn=regelbas.tjanster[t.tjanst].namn
        if t.erbjuds is None:
            namn+=': preliminär, okänt om tjänsten erbjuds. [VERIFIERA]'
        elif t.status=='preliminär':
            namn+=': preliminär bedömning. [VERIFIERA]'
        rader.append(rad(cell(namn,(t.tjanst,)),
            cell(t.inneboende.risk if t.inneboende else 'Ej bedömt',refs),
            cell(t.kvarstaende or 'Ej bedömt',refs),
            cell(t.terrorfinansiering.risk if t.terrorfinansiering else 'Ej bedömt',refs),
            cell(sank.kvarstaende if sank and sank.kvarstaende else 'Ej bedömt',
                 (t.tjanst,*(sank.regelspar if sank else ())))))
    return tabell('TAB-RISK','Risk per tjänst',('Tjänst','PT före kontroll','PT efter kontroll','TF','Sanktionsrisk efter kontroll'),rader)


def bygg_kontrolloversikt(bedomning: Bedomning, regelbas: Regelbas, profil: Profil, *, gransindex=None) -> Dokumenttabell:
    grupper={}
    for t in bedomning.tjanster:
        if t.erbjuds is False:
            continue
        kontroller=(*t.kontroller,*((t.sanktionsrisk.kontroll,) if t.sanktionsrisk and t.sanktionsrisk.kontroll else ()))
        for k in kontroller:
            grupper.setdefault(k.id,[]).append((t,k))
    rader=[]; index=gransindex if gransindex is not None else metodgransindex(regelbas)
    for id, poster in grupper.items():
        k=regelbas.kontroller[id]
        # Skilda bedömningar behålls tjänstevis; välj aldrig den bästa effekten.
        status={p.model_dump_json() for _,p in poster}
        def beskriv(p):
            return (f'Utformning: {p.utformning or "okänd"}; genomförande: {p.genomforande or "okänt"}; effekt: {p.effekt or "ej bedömd"}. '
                    f'Riskreducerande enligt metodvillkoren: {"ja" if p.fungerar_och_ar_belagd else "nej"}.')
        text=beskriv(poster[0][1]) if len(status)==1 else ' '.join(
            f'{regelbas.tjanster[t.tjanst].namn}: {beskriv(p)}' for t,p in poster)
        refs=[id,k.utformning_falt,k.genomforande_falt,*[x for x in (k.effekt_falt,k.utfall_falt) if x]]
        utfall=kort_varde(regelbas,profil,k.utfall_falt,period=True,gransindex=index) if k.utfall_falt else 'Effektbelägg saknar eget fält i denna metod.'
        belagg=((k.utformning_falt,'utformning'),(k.genomforande_falt,'genomförande'),
                (k.effekt_falt,'effektbedömning'),(k.utfall_falt,'utfall'))
        saknas=[namn for falt,namn in belagg if falt and not belagd_uppgift(regelbas,profil,falt)]
        if saknas:
            utfall+=' Aktuellt belägg saknas för '+', '.join(saknas)+'. [VERIFIERA]'
        rader.append(rad(cell(k.namn,(id,)),cell(', '.join(regelbas.tjanster[t.tjanst].namn for t,_ in poster),(t.tjanst for t,_ in poster)),
                         cell(text,refs),cell(utfall,refs)))
    return tabell('TAB-KONTROLL','Kontroller och effektbelägg',('Kontroll','Tjänster','Utformning, genomförande och effekt','Utfall, period och begränsningar'),rader)


def bygg_tjansteoversikt(rb, profil, bedomning, *, gransindex=None):
    rader=[]; index=gransindex if gransindex is not None else metodgransindex(rb)
    for t in bedomning.tjanster:
        if t.erbjuds is False:
            continue
        tj=rb.tjanster[t.tjanst]; slug=tj.erbjuds_falt.removesuffix('_erbjuds')
        def v(suffix):
            id=slug+suffix
            return cell(kort_varde(rb,profil,id,period=True,gransindex=index),(id,) if id in rb.falt else ())
        rader.append(rad(cell(tj.namn,(t.tjanst,)),v('_antal_kunder'),v('_omsattning'),v('_kundtyper')))
    return tabell('TAB-TJANSTER','Tjänsternas omfattning',('Tjänst','Kunder och period','Omsättning och period','Kundtyper'),rader)


def bygg_atgardsoversikt(rb, bedomning):
    rader=[]; sedda=set()
    for t in bedomning.tjanster:
        if not t.inneboende:
            continue
        kontroller=(*t.kontroller,*((t.sanktionsrisk.kontroll,) if t.sanktionsrisk and t.sanktionsrisk.kontroll else ()))
        for k in kontroller:
            if k.fungerar_och_ar_belagd or k.id in sedda:
                continue
            sedda.add(k.id)
            rader.append(rad(cell(rb.kontroller[k.id].namn,(k.id,)),
                cell('Pröva kontrollens täckning och dokumentera verkan och kvarstående brister.',(k.id,)),
                cell('Ej beslutat'),cell('Ej beslutat'),cell('Följ upp genomförande och effektbelägg.')))
    if not rader:
        rader.append(rad(cell('Kontrolluppföljning'),cell('Följ upp faktisk effekt; inga ytterligare åtgärder är beslutade här.'),
                         cell('Ej beslutat'),cell('Ej beslutat'),cell('Dokumentera utvärderingen.')))
    return tabell('TAB-ATGARDER','Föreslaget fortsatt åtgärdsarbete',('Kontroll/brist','Föreslagen åtgärd','Ansvarig','Tidsfrist','Uppföljning'),rader)


def bygg_metodmatris(rb):
    rows=[]
    for s in ('låg','medel','hög'):
        vals=[next(r for r in rb.metod.riskmatris if r.sannolikhet==s and r.konsekvens==k) for k in ('begränsad','betydande','allvarlig')]
        rows.append(rad(cell(s),*(cell(r.risk,(r.id,)) for r in vals)))
    return tabell('TAB-MATRIS','Befintlig riskmatris – ogranskat metodval',('Sannolikhet / konsekvens','Begränsad','Betydande','Allvarlig'),rows)
