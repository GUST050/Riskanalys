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
        u=bygg_underlag(rb,p,t,id);n=u.nivaer
        text=f"Den inneboende risken är {n['inneboende_risk']}. Risken för finansiering av terrorism bedöms som {n['terrorfinansiering_risk']}. Den kvarstående risken är {n['kvarstaende_risk']}. Sanktionsrisken är {n['sanktioner_risk']}. Den kvarstående sanktionsrisken är {n['kvarstaende_sanktioner_risk']}."
        refs=[u.hot[0].id,u.sarbarheter[0].id]
        a=AvsnittsUtkast(avsnitt=id,stycken=[Textstycke(typ='analys',text=text,referenser=list(u.regelspar)),Textstycke(typ='motivering',text=f"Tjänstens ekonomiska flöden kan utnyttjas. Sårbarheter i kundunderlagen kräver spårbara kontroller och uppföljning. Risken är {n['inneboende_risk']}.",referenser=refs)],oklarheter=[])
        assert not validera_utkast(a,u,()),validera_utkast(a,u,())
        svar.append(a.model_dump(mode='json'))
    return svar
