"""H3/H4/M1–M4 och H5 med endast syntetiska uppgifter.

Nya dokument byggs i D-ARB-tjanst-v6. Prov som bara gäller motorn bygger inget
dokument. Historisk v5-verifiering prövas uttryckligen med bygg_arb_v5.
"""
import json
from collections import Counter
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from pydantic import ValidationError

from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.modeller import Avsnitt, Textstycke, Underrubrik
from riskanalys.dokument.rendering import rendera_docx, utkaststatus
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.faststallelse.sakgranskning import galler_sakgranskning, registrera_sakgranskning
from riskanalys.granskning.kontroller import granska
from riskanalys.profil.modeller import Period
from riskanalys.regelverk.urval import valj
from tester.enhet.test_arb_v6 import v6underlag  # noqa: F401  pytest-fixtur
from tester.enhet.test_lokalt_dokument_v6 import lokal  # noqa: F401  pytest-fixtur
from tester.fixturer.arb_kedja import (
    ai_begaran, andrat, bedom_kedja, bekraftad_analys, granska_kedja, med_avsnitt, v5_kedja, v6_kedja,
)
from tester.fixturer.m2 import DAG
from tester.regelkontrakt.test_arb_erfarenhet_motivering import profil  # noqa: F401  pytest-fixtur

FAKTORER = ('nara_relation','pep','komplex_agare','utlandsk_agare','ideell','kortlivad','overtagen','utan_mote','ombud','extern_kyc','hogrisktredjeland','korruption','svagt_aml','utsatt_omrade','utan_utbildning','ensam_roller','kundberoende','utkontraktering')
# Historiska v5-tjänstavsnitt har sex underrubriker; v6 har två AI-delar och en lokal del.
RUBRIKER_V5 = ('Beskrivning och omfattning','Hot och egna erfarenheter','Sårbarheter och motivering','Kontroller och effekt','Scenarier och osäkerheter','Slutsatser')
RUBRIKER_V6 = ('Hot','Sårbarheter','Lokal analys och slutsats')
DELNAMN = ['Sårbarheter och motivering','Kontroller och effekt','Slutsatser','underrubrik']
PASTAENDE_UTAN_BELAGG = 'Den inneboende risken är låg. Ett påstående utan belägg.'


def risk_rad(d, tjanst):
    return next(r for r in d.avsnitt_med_id()['D-ARB.8'].tabeller[0].rader if tjanst in r.celler[0].referenser)


def texter_med_ref(d, ref):
    stycken = [s.text for a in d.avsnitt for s in a.stycken if ref in s.referenser]
    celler = [c.text for a in d.avsnitt for tab in a.tabeller for r in tab.rader for c in r.celler if ref in c.referenser]
    return [*stycken, *celler]


@pytest.mark.parametrize('faktor', FAKTORER)
def test_ny_faktor_har_kalla_falt_och_verkligt_motorutfall(regelbas_v1, profil, faktor):
    f='P-RISK.'+faktor
    assert f in regelbas_v1.falt
    post=next(s for s in regelbas_v1.sarbarheter.values() if s.id.startswith('S-ARB-') and f in str(s.villkor))
    assert post.grund=='metodval' and post.kallhanvisningar and post.sakkunnig.status=='ej_granskad'
    assert regelbas_v1.falt[f].intag.kallor
    _,b=bedom_kedja(regelbas_v1,andrat(profil,f,varde=True))
    assert all(post.id in t.tillampade_sarbarheter for t in b.tjanster if t.erbjuds)
    _,b=bedom_kedja(regelbas_v1,andrat(profil,f,status='saknas'))
    assert all(f in t.okanda_uppgifter for t in b.tjanster if t.erbjuds)

def test_hot_ar_tjanstkopplade_med_konkreta_tf_modus(regelbas_v1):
    anvanda={id for t in regelbas_v1.tjanster.values() for id in t.hot}
    assert {'H-01','H-02'}<=anvanda
    for t in regelbas_v1.tjanster.values():
        assert len(t.hot)>=4
        assert any(regelbas_v1.hot[h].galler_tf and h.startswith('H-TF-') for h in t.hot)
    for id in ('H-TF-01','H-TF-02','H-TF-03','H-MOD-01','H-MOD-02','H-MOD-03'):
        h=regelbas_v1.hot[id]
        assert h.kallhanvisningar and h.grund=='metodval' and h.sakkunnig.status=='ej_granskad'

def test_underrubrik_valideras_och_binds_till_sakgranskning():
    s=Textstycke(typ='analys',text='Syntetiskt.',referenser=[])
    a=Avsnitt(id='D-ARB.6.1',rubrik='Tjänst',kalla='regelbas',stycken=(s,),underrubriker=(Underrubrik(fore_stycke=0,rubrik='Hot'),))
    assert a.kontrollsumma()!=a.model_copy(update={'underrubriker':(Underrubrik(fore_stycke=0,rubrik='Sårbarheter'),)}).kontrollsumma()
    with pytest.raises(ValidationError):
        Avsnitt(id=a.id,rubrik=a.rubrik,kalla='regelbas',stycken=(s,),underrubriker=(Underrubrik(fore_stycke=1,rubrik='Utanför'),))
    from riskanalys.lagring.kontrollsumma import for_text
    gammalt=Avsnitt(id=a.id,rubrik=a.rubrik,kalla='regelbas',stycken=(s,))
    data=gammalt.model_dump(mode='json');data.pop('underrubriker')
    assert gammalt.kontrollsumma()==for_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))

def test_docx_har_v6_delar_per_tjanst_och_underlag_i_bilaga(tmp_path,regelbas_v1,profil):
    # Ersätter H5:s sex underrubriker per tjänst (v2–v5; historisk v5 prövas i
    # test_andrad_deterministisk_tjanstanalys_blockeras_i_historisk_v5) med planens
    # v6-läsordning: risköversikt direkt efter syftet, två AI-delar och en lokal analysdel
    # per tjänst, nivåer i översikten och beräkningar i B1. Låsta erfarenhets- och
    # geografistycken prövas för varje tjänst i test_arb_erfarenhet_motivering.
    # Tjänstebeskrivningen i huvudtexten är v6:s lokala "Uppdrag och exponering";
    # profilens fritext om arbetssätt redovisas i B1.
    rb=regelbas_v1
    p=andrat(profil,'P-TJ.red01_arbetssatt',varde='SYNTETISKT_LOKALT_ARBETSSATT')
    _,b=bedom_kedja(rb,p)
    analys=bekraftad_analys(rb,p,b)
    forsta=analys.tjanster[0]
    forsta=forsta.model_copy(update={'exponering':forsta.exponering+' SYNTETISK_LOKAL_EXPONERING.'})
    k=v6_kedja(rb,p,analys=analys.model_copy(update={'tjanster':(forsta,*analys.tjanster[1:])}))
    d=k.dokument
    ids=[a.id for a in d.avsnitt]
    assert ids[:2]==['D-ARB.1','D-ARB.8']
    assert ids.index('D-ARB.7') < next(i for i,id in enumerate(ids) if id.startswith('D-ARB.6.'))
    assert ids[-1]=='D-ARB.B1' and 'D-ARB.11' in ids
    b1=d.avsnitt_med_id()['D-ARB.B1']
    for id,t in tjanster_med_avsnitt(b):
        a=d.avsnitt_med_id()[id]
        assert tuple(u.rubrik for u in a.underrubriker)==RUBRIKER_V6
        assert risk_rad(d,t.tjanst).celler[2].text.split(' Källor:')[0]==t.kvarstaende
        utfall=next(tab for tab in b1.tabeller if tab.id==t.tjanst+'-utfall')
        assert t.kvarstaende in next(r for r in utfall.rader if r.celler[0].text.startswith('Penningtvätt')).celler[2].text
    # Lokal fritext står i huvudtexten som lokal analys; ingen fritext når AI.
    tjanst=d.avsnitt_med_id()[tjanster_med_avsnitt(b)[0][0]]
    assert any(s.proveniens=='lokal' and 'SYNTETISK_LOKAL_EXPONERING' in s.text for s in tjanst.stycken)
    huvud='\n'.join(s.text for a in d.avsnitt if a.id!='D-ARB.B1' for s in a.stycken)
    assert regelbas_v1.falt['P-VERK.antal_rapporter'].fraga not in huvud
    assert '(P-VERK.antal_rapporter)' not in huvud
    bilagetext='\n'.join(s.text for s in b1.stycken)
    assert f"{regelbas_v1.falt['P-VERK.antal_rapporter'].etikett} (P-VERK.antal_rapporter): " in bilagetext
    assert '(P-TJ.red01_arbetssatt): SYNTETISKT_LOKALT_ARBETSSATT' in bilagetext
    for id,t in tjanster_med_avsnitt(b):
        assert 'SYNTETISKT_LOKALT_ARBETSSATT' not in bygg_underlag(regelbas_v1,p,t,id).model_dump_json()
    assert k.delanrop and all(x not in ai_begaran(k) for x in ('SYNTETISKT_LOKALT_ARBETSSATT','SYNTETISK_LOKAL_EXPONERING'))
    fil=rendera_docx(d,p,utkaststatus(DAG),tmp_path/'syntetisk.docx')
    word=Document(fil)
    antal=sum(t.erbjuds is True for t in b.tjanster)
    rubriker=Counter(x.text for x in word.paragraphs if x.style.name=='Heading 2')
    assert rubriker==Counter({'Innehåll':1,**{r:antal for r in RUBRIKER_V6}})

@pytest.mark.parametrize('effekt',['begränsad','verkningslös','ej_bedömd'])
def test_genomford_kontroll_utan_verksam_effekt_sanker_inte_risk(regelbas_v1,profil,effekt):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.effekt',varde=effekt)
    _,b=bedom_kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd and t.kvarstaende==t.inneboende.risk

@pytest.mark.parametrize('fel',[{'status':'saknas'},{'inaktuell':True},{'period':None},{'kalla':None},{'varde':'   '}])
def test_effektens_underlag_maste_vara_aktuellt(regelbas_v1,profil,fel):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.utfall',**fel)
    k=v6_kedja(regelbas_v1,p)
    t=next(t for t in k.bedomning.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd and t.kvarstaende==t.inneboende.risk
    # V6:s D-ARB.7 beskriver bara källbunden räckvidd. Kontrollens effektbelägg redovisas
    # i B1 och tjänsten märks som preliminär i risköversikten; båda ska flagga bristen.
    utfall=[s for s in k.dokument.avsnitt_med_id()['D-ARB.B1'].stycken if 'P-KONTROLL.C-TJ-08.utfall' in s.referenser]
    assert utfall and all('[VERIFIERA]' in s.text for s in utfall)
    assert '[VERIFIERA]' in risk_rad(k.dokument,'T-SKATT-01').celler[0].text

def test_omfattning_slutsatser_och_uppfoljning_ar_motiverade(regelbas_v1,profil):
    a=v6_kedja(regelbas_v1,profil).dokument.avsnitt_med_id()
    for term in ('hot eller hämnd','högrisktredjeländer','spridning','goAML','tillsyn'):
        assert term in ' '.join(s.text for s in a['D-ARB.10'].stycken)
    # Planen för v6: "Bevara motiveringen av omfattningen efter byråns storlek och art."
    text=' '.join(s.text for s in a['D-ARB.2'].stycken)
    assert 'Storlek' in text and 'Art' in text and 'vald omfattning' in text.lower(), 'V6:s metodavsnitt saknar motiveringen efter storlek och art.'
    # D-ARB.9 (stabilt id): konkreta följder för rutiner, kundkännedom, övervakning och utbildning.
    assert 'D-ARB.9' in a, 'V6 saknar avsnittet om följder för rutiner, kundkännedom, övervakning och utbildning.'
    for term in ('kundkännedom','övervakning','utbildning','rutiner'):
        assert term in ' '.join(s.text for s in a['D-ARB.9'].stycken).lower()

def test_hamtad_kalla_ar_inte_byra_bevakning_och_bilaga_kravs(regelbas_v1,profil):
    p=andrat(profil,'P-BEVAKNING.relevans',status='saknas')
    k=v6_kedja(regelbas_v1,p)
    text=' '.join(s.text for s in k.dokument.avsnitt_med_id()['D-ARB.11'].stycken)
    assert '[VERIFIERA]' in text and 'hämtning' in text
    assert any(f.avsnitt=='D-ARB.11' for f in granska_kedja(regelbas_v1,k,p))
    d=k.dokument.model_copy(update={'avsnitt':tuple(a for a in k.dokument.avsnitt if a.id!='D-ARB.B1')})
    assert any(f.avsnitt=='D-ARB.B1' and f.allvar=='blockerande' for f in granska_kedja(regelbas_v1,k,p,d))

@pytest.mark.parametrize('falt,varde,niva',[('P-ORG.antal_anstallda',10,'utökad'),('P-ORG.verksamhetsstallen',2,'utökad'),('P-VERK.omsattning',10000000.,'utökad')])
def test_proportionalitet_foljer_kallbundet_metodval(regelbas_v1,profil,falt,varde,niva):
    _,b=bedom_kedja(regelbas_v1,andrat(profil,falt,varde=varde))
    assert b.proportionalitet.niva==niva
    assert regelbas_v1.metod.omfattning.id in b.proportionalitet.regelspar
    assert regelbas_v1.metod.omfattning.sakkunnig.status=='ej_granskad'


def test_proportionalitet_med_okand_storlek_ar_preliminar(regelbas_v1,profil):
    _,b=bedom_kedja(regelbas_v1,andrat(profil,'P-ORG.antal_anstallda',status='saknas'))
    assert b.proportionalitet.status=='preliminär'

@pytest.mark.parametrize('kallor',['OKANT-ID','SRC-FATF-TF-2025','SRC-TS-2026-14, OKANT-ID'])
def test_bevakning_kraver_registrerad_kallversion(regelbas_v1,profil,kallor):
    p=andrat(profil,'P-BEVAKNING.kallor',varde=kallor)
    d=v6_kedja(regelbas_v1,p).dokument
    assert '[VERIFIERA]' in ' '.join(s.text for s in d.avsnitt_med_id()['D-ARB.11'].stycken)


def test_kontrolleffekt_med_annan_period_ger_ingen_reduktion(regelbas_v1,profil):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.utfall',period=Period(fran=date(2025,1,1),till=date(2025,12,31)))
    _,b=bedom_kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert t.kvarstaende==t.inneboende.risk and not t.kontroller[0].fungerar_och_ar_belagd


def test_sakgodkannande_ogiltigt_efter_andrad_underrubrik_och_bilaga(regelbas_v1,profil):
    d=v6_kedja(regelbas_v1,profil).dokument
    for id in ['D-ARB.6.1','D-ARB.B1']:
        a=d.avsnitt_med_id()[id]
        poster=registrera_sakgranskning((),d,profil,id,True,'FfR','Syntetisk granskare',DAG)
        if id=='D-ARB.B1':ny=a.model_copy(update={'stycken':(*a.stycken,Textstycke(typ='analys',text='Ändrat underlag',referenser=[]))})
        else:ny=a.model_copy(update={'underrubriker':(Underrubrik(fore_stycke=0,rubrik='Ändrad struktur'),*a.underrubriker[1:])})
        # V6 binder även dispositionen; godkännandet prövas därför mot hela dokumentet.
        assert galler_sakgranskning(poster,a,profil,d) is not None
        assert galler_sakgranskning(poster,ny,profil,med_avsnitt(d,ny)) is None
        assert galler_sakgranskning(poster,ny,profil) is None

@pytest.mark.parametrize('fel',['ordning','titel','bilaga'])
def test_hela_dispositionen_binds_till_sakgodkannandet(regelbas_v1,profil,fel):
    d=v6_kedja(regelbas_v1,profil).dokument
    a=d.avsnitt_med_id()['D-ARB.6.1']
    poster=registrera_sakgranskning((),d,profil,a.id,True,'FfR','Syntetisk granskare',DAG)
    if fel=='ordning':ny=d.model_copy(update={'avsnitt':tuple(reversed(d.avsnitt))})
    elif fel=='titel':ny=d.model_copy(update={'titel':'Ändrad helhet'})
    else:ny=d.model_copy(update={'avsnitt':tuple(s for s in d.avsnitt if s.id!='D-ARB.B1')})
    assert galler_sakgranskning(poster,a,profil,d) is not None
    assert galler_sakgranskning(poster,a,profil,ny) is None


def test_ai_kontrollstatus_ar_tydlig_om_utebliven_effekt(regelbas_v1,profil):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.effekt',varde='verkningslös')
    _,b=bedom_kedja(regelbas_v1,p)
    id,t=next((id,t) for id,t in tjanster_med_avsnitt(b) if t.tjanst=='T-SKATT-01')
    u=bygg_underlag(regelbas_v1,p,t,id)
    assert 'verkningslös' in u.kontroller[0].status and 'ingen riskreduktion' in u.kontroller[0].status

@pytest.mark.parametrize('antal,faktor', [
    ('P-KUND.antal_utan_mote','utan_mote'),
    ('P-GEO.antal_agare_utanfor_ees','utlandsk_agare'),
    ('P-GEO.antal_hogrisktredjeland','hogrisktredjeland'),
    ('P-GEO.antal_utsatt_omrade','utsatt_omrade'),
])
def test_bekraftat_antal_kan_inte_doljas_av_nej_indikator(regelbas_v1, profil, antal, faktor):
    p=andrat(profil,antal,varde=1)
    _,b=bedom_kedja(regelbas_v1,p)
    post=next(s for s in regelbas_v1.sarbarheter.values() if s.id.startswith('S-ARB-') and 'P-RISK.'+faktor in str(s.villkor))
    assert all(post.id in t.tillampade_sarbarheter for t in b.tjanster if t.erbjuds)

@pytest.mark.parametrize('fel',[{'period':None},{'kalla':None},{'inaktuell':True}])
def test_genomforandets_belagg_kravs_ocksa_for_reduktion(regelbas_v1,profil,fel):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt',**fel)
    _,b=bedom_kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd


def test_dokumentformat_ar_explicit_och_foljer_med_faststallelsen(regelbas_v1,profil):
    from riskanalys.faststallelse.faststall import _metadata
    from riskanalys.faststallelse.modeller import Beslut
    beslut=Beslut(organ='styrelsen',namn='Syntetisk',roll='FfR',datum=DAG)
    # Nya dokument är v6; ett historiskt v5-paket behåller sitt eget format.
    for k,format in ((v6_kedja(regelbas_v1,profil),'D-ARB-tjanst-v6'),(v5_kedja(regelbas_v1,profil),'D-ARB-tjanst-v5')):
        assert k.dokument.formatversion==format
        u=SimpleNamespace(dokument=k.dokument,bedomning=k.bedomning,regelbas=regelbas_v1,analysbindning=None)
        assert _metadata(u,beslut,1,Path('syntetisk'))['dokumentformat']==format


def test_ej_bedomd_effekt_ar_okand_och_stoppar_faststallelse(regelbas_v1,profil):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.effekt',varde='ej_bedömd')
    _,b=bedom_kedja(regelbas_v1,p)
    assert b.status=='preliminär'
    assert 'P-KONTROLL.C-TJ-08.effekt' in next(t for t in b.tjanster if t.tjanst=='T-SKATT-01').okanda_uppgifter
    from riskanalys.faststallelse.grindar import _bedomning
    assert any('preliminär' in h for h in _bedomning(SimpleNamespace(bedomning=b)))

@pytest.mark.parametrize('delnamn',DELNAMN)
def test_andrad_deterministisk_tjanstanalys_blockeras(regelbas_v1,v6underlag,lokal,delnamn):
    # V6-delar: Sårbarheter och motivering -> AI-delen Sårbarheter; Kontroller och effekt ->
    # tjänstens lokala tabell över faktisk kontroll; Slutsatser -> det lokala Slutsats-stycket.
    rb,p,b,resultat,h=v6underlag
    urval=valj(rb,p.byra.regelpaket,b.datum,p.byra.lan)
    d=bygg_arb(rb,p,b,resultat,h,analys=lokal)
    def blockerat(dokument,id):
        return any(f.avsnitt==id and f.allvar=='blockerande' for f in
                   granska(rb,urval,p,b,dokument,h,DAG,skrivresultat=resultat,analys=lokal))
    a=d.avsnitt_med_id()['D-ARB.6.1']
    assert tuple(u.rubrik for u in a.underrubriker)==RUBRIKER_V6 and not blockerat(d,a.id)
    if delnamn=='underrubrik':
        ny=a.model_copy(update={'underrubriker':a.underrubriker[:-1]})
    elif delnamn=='Kontroller och effekt':
        tab=next(t for t in a.tabeller if t.id.endswith('-kontrollprovning'))
        rad=tab.rader[0]
        rad=rad.model_copy(update={'celler':(*rad.celler[:3],rad.celler[3].model_copy(update={'text':PASTAENDE_UTAN_BELAGG}),*rad.celler[4:])})
        tab=tab.model_copy(update={'rader':(rad,*tab.rader[1:])})
        ny=a.model_copy(update={'tabeller':tuple(tab if t.id==tab.id else t for t in a.tabeller)})
    else:
        i=(next(i for i,s in enumerate(a.stycken) if s.text.startswith('Slutsats:')) if delnamn=='Slutsatser'
           else next(r.fore_stycke for r in a.underrubriker if r.rubrik=='Sårbarheter'))
        stycken=list(a.stycken);stycken[i]=stycken[i].model_copy(update={'text':PASTAENDE_UTAN_BELAGG})
        ny=a.model_copy(update={'stycken':tuple(stycken)})
    assert blockerat(med_avsnitt(d,ny),a.id)

@pytest.mark.parametrize('delnamn',DELNAMN)
def test_andrad_deterministisk_tjanstanalys_blockeras_i_historisk_v5(regelbas_v1,profil,delnamn):
    # Historiska v5-paket har kvar sex underrubriker; verifieringen ska fortsatt blockera.
    k=v5_kedja(regelbas_v1,profil)
    a=k.dokument.avsnitt_med_id()['D-ARB.6.1']
    assert tuple(u.rubrik for u in a.underrubriker)==RUBRIKER_V5
    if delnamn=='underrubrik':
        ny=a.model_copy(update={'underrubriker':a.underrubriker[:-1]})
    else:
        i=next(r.fore_stycke for r in a.underrubriker if r.rubrik==delnamn)
        stycken=list(a.stycken);stycken[i]=stycken[i].model_copy(update={'text':PASTAENDE_UTAN_BELAGG})
        ny=a.model_copy(update={'stycken':tuple(stycken)})
    fynd=granska_kedja(regelbas_v1,k,profil,med_avsnitt(k.dokument,ny))
    assert any(f.avsnitt==a.id and f.allvar=='blockerande' for f in fynd)


def test_historisk_faktor_far_inte_presenteras_som_aktuell(regelbas_v1,profil):
    p=andrat(profil,'P-RISK.pep',varde=False,period=Period(fran=date(2020,1,1),till=date(2020,12,31)))
    k=v6_kedja(regelbas_v1,p)
    b=k.bedomning
    assert b.status=='preliminär'
    assert all('P-RISK.pep' in t.okanda_uppgifter for t in b.tjanster if t.erbjuds)
    # V6 redovisar faktorns underlag i B1 och AI-delarna får den bara som okänd. Ingen
    # presentation av P-RISK.pep får sakna [VERIFIERA]; översikten märker tjänsterna preliminära.
    texter=texter_med_ref(k.dokument,'P-RISK.pep')
    assert texter and all('[VERIFIERA]' in x for x in texter)
    for r in k.resultat.values():
        post=next((x for x in r.faktablad.poster if x.id=='P-RISK.pep'),None)
        assert post is None or post.status=='okänd'
    assert all('[VERIFIERA]' in risk_rad(k.dokument,t.tjanst).celler[0].text for t in b.tjanster if t.erbjuds)


def test_hawala_hanvisar_till_bada_originalsidorna(regelbas_v1):
    refs=regelbas_v1.hot['H-TF-02'].kallhanvisningar
    assert {r.sida for r in refs if r.kalla=='SRC-FIPO-TF-2025'} >= {1,2}


def test_gemensamt_historiskt_kontrollutfall_far_inte_sanka_aktuell_risk(regelbas_v1,profil):
    old=Period(fran=date(2020,1,1),till=date(2020,12,31))
    p=profil
    for suffix,v in [('utformning','finns'),('genomforande','belagt'),('effekt','verksam'),('utfall','Syntetiskt historiskt prov.')]:
        p=andrat(p,'P-KONTROLL.C-TJ-08.'+suffix,varde=v,period=old)
    _,b=bedom_kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert t.status=='preliminär' and not t.kontroller[0].fungerar_och_ar_belagd
    assert t.kvarstaende==t.inneboende.risk
