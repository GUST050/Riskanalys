"""H3/H4/M1–M4 och H5 med endast syntetiska uppgifter."""
import json
import pytest
from pydantic import ValidationError
from docx import Document
from riskanalys.dokument.modeller import Avsnitt, Textstycke
from riskanalys.dokument.rendering import rendera_docx, utkaststatus
from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.granskning.kontroller import granska
from tester.regelkontrakt.test_arb_erfarenhet_motivering import profil, andrat, kedja, HISTORIK
from tester.fixturer.m2 import DAG
FAKTORER = ('nara_relation','pep','komplex_agare','utlandsk_agare','ideell','kortlivad','overtagen','utan_mote','ombud','extern_kyc','hogrisktredjeland','korruption','svagt_aml','utsatt_omrade','utan_utbildning','ensam_roller','kundberoende','utkontraktering')
RUBRIKER = ('Beskrivning och omfattning','Hot och egna erfarenheter','Sårbarheter och motivering','Kontroller och effekt','Risknivåer och motivering','Slutsatser')
@pytest.mark.parametrize('faktor', FAKTORER)
def test_ny_faktor_har_kalla_falt_och_verkligt_motorutfall(regelbas_v1, profil, faktor):
    f='P-RISK.'+faktor
    assert f in regelbas_v1.falt
    post=next(s for s in regelbas_v1.sarbarheter.values() if s.id.startswith('S-ARB-') and f in str(s.villkor))
    assert post.grund=='metodval' and post.kallhanvisningar and post.sakkunnig.status=='ej_granskad'
    assert regelbas_v1.falt[f].intag.kallor
    _,b,_=kedja(regelbas_v1,andrat(profil,f,varde=True))
    assert all(post.id in t.tillampade_sarbarheter for t in b.tjanster if t.erbjuds)
    _,b,_=kedja(regelbas_v1,andrat(profil,f,status='saknas'))
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
    from riskanalys.dokument.modeller import Underrubrik
    s=Textstycke(typ='analys',text='Syntetiskt.',referenser=[])
    a=Avsnitt(id='D-ARB.6.1',rubrik='Tjänst',kalla='regelbas',stycken=(s,),underrubriker=(Underrubrik(fore_stycke=0,rubrik='Hot'),))
    assert a.kontrollsumma()!=a.model_copy(update={'underrubriker':(Underrubrik(fore_stycke=0,rubrik='Sårbarheter'),)}).kontrollsumma()
    with pytest.raises(ValidationError):
        Avsnitt(id=a.id,rubrik=a.rubrik,kalla='regelbas',stycken=(s,),underrubriker=(Underrubrik(fore_stycke=1,rubrik='Utanför'),))
    from riskanalys.lagring.kontrollsumma import for_text
    gammalt=Avsnitt(id=a.id,rubrik=a.rubrik,kalla='regelbas',stycken=(s,))
    data=gammalt.model_dump(mode='json');data.pop('underrubriker')
    assert gammalt.kontrollsumma()==for_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))

def test_docx_har_sex_delar_per_tjanst_och_underlag_i_bilaga(tmp_path,regelbas_v1,profil):
    p=andrat(profil,'P-TJ.red01_arbetssatt',varde='SYNTETISKT_LOKALT_ARBETSSATT')
    _,b,d=kedja(regelbas_v1,p)
    ids=[a.id for a in d.avsnitt]
    assert ids.index('D-ARB.7') < next(i for i,id in enumerate(ids) if id.startswith('D-ARB.6.'))
    assert ids[-1]=='D-ARB.B1' and 'D-ARB.11' in ids
    for id,t in tjanster_med_avsnitt(b):
        a=d.avsnitt_med_id()[id]
        assert tuple(u.rubrik for u in a.underrubriker)==RUBRIKER
        assert any('Noll rapporter' in s.text for s in a.stycken)
        assert any('S-GEO-01' in s.referenser and 'Sårbarheten gäller om' in s.text for s in a.stycken)
        assert any(t.kvarstaende in s.text for s in a.stycken)
    huvud='\n'.join(s.text for a in d.avsnitt if a.id!='D-ARB.B1' for s in a.stycken)
    assert 'SYNTETISKT_LOKALT_ARBETSSATT' in huvud
    assert regelbas_v1.falt['P-VERK.antal_rapporter'].fraga not in huvud
    assert '(P-VERK.antal_rapporter)' not in huvud
    assert f"{regelbas_v1.falt['P-VERK.antal_rapporter'].etikett} (P-VERK.antal_rapporter): " in '\n'.join(s.text for s in d.avsnitt_med_id()['D-ARB.B1'].stycken)
    for id,t in tjanster_med_avsnitt(b):
        assert 'SYNTETISKT_LOKALT_ARBETSSATT' not in bygg_underlag(regelbas_v1,p,t,id).model_dump_json()
    fil=rendera_docx(d,p,utkaststatus(DAG),tmp_path/'syntetisk.docx')
    word=Document(fil)
    assert sum(p.style.name=='Heading 2' for p in word.paragraphs)==6*sum(t.erbjuds is True for t in b.tjanster)

@pytest.mark.parametrize('effekt',['begränsad','verkningslös','ej_bedömd'])
def test_genomford_kontroll_utan_verksam_effekt_sanker_inte_risk(regelbas_v1,profil,effekt):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.effekt',varde=effekt)
    _,b,_=kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd and t.kvarstaende==t.inneboende.risk

@pytest.mark.parametrize('fel',[{'status':'saknas'},{'inaktuell':True},{'period':None},{'kalla':None},{'varde':'   '}])
def test_effektens_underlag_maste_vara_aktuellt(regelbas_v1,profil,fel):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.utfall',**fel)
    _,b,d=kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd and t.kvarstaende==t.inneboende.risk
    assert any('[VERIFIERA]' in s.text for s in d.avsnitt_med_id()['D-ARB.7'].stycken)

def test_omfattning_slutsatser_och_uppfoljning_ar_motiverade(regelbas_v1,profil):
    _,_,d=kedja(regelbas_v1,profil)
    a=d.avsnitt_med_id()
    text=' '.join(s.text for s in a['D-ARB.2'].stycken)
    assert 'Storlek' in text and 'Art' in text and 'vald omfattning' in text
    for term in ('kundkännedom','övervakning','utbildning','rutiner'):
        assert term in ' '.join(s.text for s in a['D-ARB.9'].stycken).lower()
    for term in ('hot eller hämnd','högrisktredjeländer','spridning','goAML','tillsyn'):
        assert term in ' '.join(s.text for s in a['D-ARB.10'].stycken)

def test_hamtad_kalla_ar_inte_byra_bevakning_och_bilaga_kravs(regelbas_v1,profil):
    p=andrat(profil,'P-BEVAKNING.relevans',status='saknas')
    u,b,d=kedja(regelbas_v1,p)
    text=' '.join(s.text for s in d.avsnitt_med_id()['D-ARB.11'].stycken)
    assert '[VERIFIERA]' in text and 'hämtning' in text
    assert any(f.avsnitt=='D-ARB.11' for f in granska(regelbas_v1,u,p,b,d,HISTORIK,DAG))
    d=d.model_copy(update={'avsnitt':tuple(a for a in d.avsnitt if a.id!='D-ARB.B1')})
    assert any(f.avsnitt=='D-ARB.B1' and f.allvar=='blockerande' for f in granska(regelbas_v1,u,p,b,d,HISTORIK,DAG))

@pytest.mark.parametrize('falt,varde,niva',[('P-ORG.antal_anstallda',10,'utökad'),('P-ORG.verksamhetsstallen',2,'utökad'),('P-VERK.omsattning',10000000.,'utökad')])
def test_proportionalitet_foljer_kallbundet_metodval(regelbas_v1,profil,falt,varde,niva):
    _,b,_=kedja(regelbas_v1,andrat(profil,falt,varde=varde))
    assert b.proportionalitet.niva==niva
    assert regelbas_v1.metod.omfattning.id in b.proportionalitet.regelspar
    assert regelbas_v1.metod.omfattning.sakkunnig.status=='ej_granskad'


def test_proportionalitet_med_okand_storlek_ar_preliminar(regelbas_v1,profil):
    _,b,_=kedja(regelbas_v1,andrat(profil,'P-ORG.antal_anstallda',status='saknas'))
    assert b.proportionalitet.status=='preliminär'

@pytest.mark.parametrize('kallor',['OKANT-ID','SRC-FATF-TF-2025','SRC-TS-2026-14, OKANT-ID'])
def test_bevakning_kraver_registrerad_kallversion(regelbas_v1,profil,kallor):
    p=andrat(profil,'P-BEVAKNING.kallor',varde=kallor)
    _,_,d=kedja(regelbas_v1,p)
    assert '[VERIFIERA]' in ' '.join(s.text for s in d.avsnitt_med_id()['D-ARB.11'].stycken)


def test_kontrolleffekt_med_annan_period_ger_ingen_reduktion(regelbas_v1,profil):
    from riskanalys.profil.modeller import Period
    from datetime import date
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt')
    p=andrat(p,'P-KONTROLL.C-TJ-08.utfall',period=Period(fran=date(2025,1,1),till=date(2025,12,31)))
    _,b,_=kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert t.kvarstaende==t.inneboende.risk and not t.kontroller[0].fungerar_och_ar_belagd


def test_sakgodkannande_ogiltigt_efter_andrad_underrubrik_och_bilaga(regelbas_v1,profil):
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, galler_sakgranskning
    from riskanalys.dokument.modeller import Underrubrik
    _,_,d=kedja(regelbas_v1,profil)
    for id in ['D-ARB.6.1','D-ARB.B1']:
        a=d.avsnitt_med_id()[id]
        poster=registrera_sakgranskning((),d,profil,id,True,'FfR','Syntetisk granskare',DAG)
        if id=='D-ARB.B1':ny=a.model_copy(update={'stycken':(*a.stycken,Textstycke(typ='analys',text='Ändrat underlag',referenser=[]))})
        else:ny=a.model_copy(update={'underrubriker':(Underrubrik(fore_stycke=0,rubrik='Ändrad struktur'),*a.underrubriker[1:])})
        assert galler_sakgranskning(poster,ny,profil) is None

@pytest.mark.parametrize('fel',['ordning','titel','bilaga'])
def test_hela_dispositionen_binds_till_sakgodkannandet(regelbas_v1,profil,fel):
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,galler_sakgranskning
    _,_,d=kedja(regelbas_v1,profil)
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
    _,b,_=kedja(regelbas_v1,p)
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
    _,b,_=kedja(regelbas_v1,p)
    post=next(s for s in regelbas_v1.sarbarheter.values() if s.id.startswith('S-ARB-') and 'P-RISK.'+faktor in str(s.villkor))
    assert all(post.id in t.tillampade_sarbarheter for t in b.tjanster if t.erbjuds)

@pytest.mark.parametrize('fel',[{'period':None},{'kalla':None},{'inaktuell':True}])
def test_genomforandets_belagg_kravs_ocksa_for_reduktion(regelbas_v1,profil,fel):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.utformning',varde='finns')
    p=andrat(p,'P-KONTROLL.C-TJ-08.genomforande',varde='belagt',**fel)
    _,b,_=kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert not t.kontroller[0].fungerar_och_ar_belagd


def test_dokumentformat_ar_explicit_och_foljer_med_faststallelsen(regelbas_v1,profil):
    from types import SimpleNamespace
    from riskanalys.faststallelse.faststall import _metadata
    from riskanalys.faststallelse.modeller import Beslut
    from pathlib import Path
    _,b,d=kedja(regelbas_v1,profil)
    assert d.formatversion=='D-ARB-tjanst-v2'
    u=SimpleNamespace(dokument=d,bedomning=b,regelbas=regelbas_v1)
    beslut=Beslut(organ='styrelsen',namn='Syntetisk',roll='FfR',datum=DAG)
    assert _metadata(u,beslut,1,Path('syntetisk'))['dokumentformat']==d.formatversion


def test_ej_bedomd_effekt_ar_okand_och_stoppar_faststallelse(regelbas_v1,profil):
    p=andrat(profil,'P-KONTROLL.C-TJ-08.effekt',varde='ej_bedömd')
    u,b,d=kedja(regelbas_v1,p)
    assert b.status=='preliminär'
    assert 'P-KONTROLL.C-TJ-08.effekt' in next(t for t in b.tjanster if t.tjanst=='T-SKATT-01').okanda_uppgifter
    from types import SimpleNamespace
    from riskanalys.faststallelse.grindar import _bedomning
    assert any('preliminär' in h for h in _bedomning(SimpleNamespace(bedomning=b)))

@pytest.mark.parametrize('delnamn',['Sårbarheter och motivering','Kontroller och effekt','Slutsatser','underrubrik'])
def test_andrad_deterministisk_tjanstanalys_blockeras(regelbas_v1,profil,delnamn):
    u,b,d=kedja(regelbas_v1,profil)
    a=d.avsnitt_med_id()['D-ARB.6.1']
    if delnamn=='underrubrik':
        ny=a.model_copy(update={'underrubriker':a.underrubriker[:-1]})
    else:
        i=next(r.fore_stycke for r in a.underrubriker if r.rubrik==delnamn)
        stycken=list(a.stycken);stycken[i]=stycken[i].model_copy(update={'text':'Den inneboende risken är låg. Ett påstående utan belägg.'})
        ny=a.model_copy(update={'stycken':tuple(stycken)})
    d=d.model_copy(update={'avsnitt':tuple(ny if s.id==ny.id else s for s in d.avsnitt)})
    assert any(f.avsnitt==a.id and f.allvar=='blockerande' for f in granska(regelbas_v1,u,profil,b,d,HISTORIK,DAG))


def test_historisk_faktor_far_inte_presenteras_som_aktuell(regelbas_v1,profil):
    from datetime import date
    from riskanalys.profil.modeller import Period
    p=andrat(profil,'P-RISK.pep',varde=False,period=Period(fran=date(2020,1,1),till=date(2020,12,31)))
    u,b,d=kedja(regelbas_v1,p)
    assert b.status=='preliminär'
    assert all('P-RISK.pep' in t.okanda_uppgifter for t in b.tjanster if t.erbjuds)
    assert any('[VERIFIERA]' in s.text for a in d.avsnitt if a.id.startswith('D-ARB.6.') for s in a.stycken if 'P-RISK.pep' in s.referenser)


def test_hawala_hanvisar_till_bada_originalsidorna(regelbas_v1):
    refs=regelbas_v1.hot['H-TF-02'].kallhanvisningar
    assert {r.sida for r in refs if r.kalla=='SRC-FIPO-TF-2025'} >= {1,2}


def test_gemensamt_historiskt_kontrollutfall_far_inte_sanka_aktuell_risk(regelbas_v1,profil):
    from datetime import date
    from riskanalys.profil.modeller import Period
    old=Period(fran=date(2020,1,1),till=date(2020,12,31))
    p=profil
    for suffix,v in [('utformning','finns'),('genomforande','belagt'),('effekt','verksam'),('utfall','Syntetiskt historiskt prov.')]:
        p=andrat(p,'P-KONTROLL.C-TJ-08.'+suffix,varde=v,period=old)
    _,b,_=kedja(regelbas_v1,p)
    t=next(t for t in b.tjanster if t.tjanst=='T-SKATT-01')
    assert t.status=='preliminär' and not t.kontroller[0].fungerar_och_ar_belagd
    assert t.kvarstaende==t.inneboende.risk
