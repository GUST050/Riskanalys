"""Enbart syntetiska M2-uppgifter, aldrig juridiskt facit eller riktiga byrådata."""
from datetime import date
from riskanalys.profil.modeller import Uppgift,Period
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.dokument.modeller import AvsnittsUtkast,Textstycke
from riskanalys.dokument.underlag import bygg_underlag,tjanster_med_avsnitt
from riskanalys.dokument.validering import validera_utkast

DAG=date(2026,10,10)
PERIOD=Period(fran=date(2026,1,1),till=date(2026,9,30))

def komplett_profil(rb,p):
    upp={}
    for k,f in rb.falt.items():
        if f.alias_for or f.basfalt:upp[k]=Uppgift();continue
        v={'bool':False,'heltal':0,'tal':0.,'text':'Syntetiskt testnamn','datum':DAG,'andel':0.}.get(f.typ)
        if f.typ=='val':v=p.byra.lan if k=='P-ORG.sateslan' else f.val[0]
        if k=='P-ORG.sateslan':v=p.byra.lan
        if k=='P-BEVAKNING.kallor':v='SRC-TS-2026-14, SRC-VAGL-2025-03'
        if k in {'P-VERK.bokforing','P-VERK.skatteradgivning','P-VERK.bolagstjanster','P-TJ.red01_erbjuds','P-TJ.skatt01_erbjuds','P-TJ.bolag01_erbjuds'}:v=True
        if k in {'P-ORG.antal_anstallda','P-ORG.verksamhetsstallen'}:v=1
        if k=='P-KUND.antal_aktiva':v=100
        if k=='P-VERK.omsattning':v=10000.
        if k.endswith('_sektorsmotivering'):v='Syntetisk belagd lokal motivering för denna tjänsts omfattning och kontroller.'
        if k.startswith('P-TJ.') and k.endswith('_antal_kunder'):v=3 if 'bolag01_' in k else 10
        if k.startswith('P-TJ.') and k.endswith('_omsattning'):v=3000.
        upp[k]=Uppgift(varde=v,status='bekräftad',kalla='Syntetisk testkälla',datum=DAG,bekraftad_av='Syntetisk testperson',period=PERIOD if f.periodkrav else None)
    return harled_andelar(p.model_copy(update={'uppgifter':upp}),rb)


def bygg_testsvar(rb,p,b):
    svar=[]
    for id,t in tjanster_med_avsnitt(b):
        u=bygg_underlag(rb,p,t,id)
        text="Tjänstens ekonomiska flöden kan utnyttjas för att föra in osanna underlag och ge brottsvinster ett legalt utseende."
        refs=[u.hot[0].id,u.sarbarheter[0].id]
        a=AvsnittsUtkast(avsnitt=id,stycken=[Textstycke(typ='analys',text=text,referenser=list(u.regelspar)),Textstycke(typ='motivering',text="Tjänstens ekonomiska flöden kan utnyttjas. Sårbarheter i kundunderlagen kräver spårbara kontroller och uppföljning.",referenser=refs)],oklarheter=[])
        assert not validera_utkast(a,u,()),validera_utkast(a,u,())
        svar.append(a.model_dump(mode='json'))
    return svar


from riskanalys.dokument.modeller import AISvar, AIStycke
from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.profil.lagring import spara_profil

FYLLNAD = " Byrån konterar kundernas underlag och stämmer av dem mot bankens uppgifter varje månad." * 10


def tjanst_for_prov(mapp, rb, profil):
    spara_profil(mapp, profil)
    b = las_bedomning(kor_bedomning(mapp, rb))
    return tjanster_med_avsnitt(b)[0]


def godkant_delsvar(del_id, t):
    rb=_regelbas_for_delsvar()
    fyll={
        'T-RED-01':' Bokföraren konterar fakturor och granskar verifikationernas affärshändelser innan periodens bokslut stäms av.',
        'T-SKATT-01':' Skatterådgivaren prövar deklarationsunderlag och skatteupplägg genom att kontrollera transaktionernas skattemässiga syften och konsekvenser.',
        'T-BOLAG-01':' Bolagskonsulten utreder bolagsbildning och ägarbyten genom prövning av aktietecknare, kapitaltillskott samt företrädarnas mandat.',
    }.get(t.tjanst,' '+rb.tjanster[t.tjanst].namn+' analyseras genom prövning av uppdragets särskilda underlag och kundens verksamhet.')*10
    hot=list(t.hot)
    tj=rb.tjanster[t.tjanst]
    sar=list(tj.sarbarheter[:1])
    refs={"hot":[t.tjanst,*hot],"kontroller":[t.tjanst],"risknivaer":[t.tjanst,hot[0],*sar],"slutsatser":[t.tjanst,hot[0]]}
    if del_id=="sarbarheter":
        omraden={}
        for id in tj.sarbarheter:
            omraden.setdefault(rb.sarbarheter[id].omrade,id)
        return AISvar(stycken=[AIStycke(typ="analys",referenser=[t.tjanst,id],text="Underlaget för faktorn ska prövas för denna tjänst."+fyll[:600]) for id in omraden.values()],oklarheter=[])
    extra=" Kundkännedom, övervakning och utbildning anpassas efter hoten." if del_id=="slutsatser" else ""
    return AISvar(stycken=[AIStycke(typ="motivering" if del_id=="risknivaer" else "analys",referenser=refs[del_id],text="Tjänstens flöden kan utnyttjas."+fyll+extra)],oklarheter=[])

from functools import lru_cache

@lru_cache(maxsize=1)
def _regelbas_for_delsvar():
    from riskanalys.regelverk.laddning import ladda_regelbas
    return ladda_regelbas()


def bygg_delsvar(rb, profil, bedomning):
    from riskanalys.dokument.promptar import DELAR
    return [godkant_delsvar(d,t) for _,t in tjanster_med_avsnitt(bedomning) for d in DELAR]
