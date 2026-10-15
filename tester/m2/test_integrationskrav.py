from datetime import date
import pytest
from riskanalys.profil.hantering import skapa_profil,bekrafta
from riskanalys.profil.modeller import Byra,Uppgift,Period
from riskanalys.regelverk.tillsyn import rattlig_omfattning
from riskanalys.bedomning.motor import bedom_tjanst
from riskanalys.dokument.underlag import SKYDDAD_VISNING, bygg_underlag
from riskanalys.dokument.arb import bygg_arb
from riskanalys.bedomning.motor import bedom
from riskanalys.regelverk.urval import valj
from riskanalys.drift.historik import Historik

def profil(rb):
 p=skapa_profil(rb,Byra(id='syntetisk',regelpaket='RP-RED-VG',datum=date(2026,10,10),lan='Västra Götaland'))
 return p

def u(v):return Uppgift(varde=v,status='bekräftad',kalla='Syntetisk källa',datum=date(2026,10,10),bekraftad_av='Test')

def test_alias_har_samma_semantik_utan_omskrivning(regelbas_v1):
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.T-RED-01.erbjuds':u(True)}})
 assert bedom_tjanst(regelbas_v1,regelbas_v1.tjanster['T-RED-01'],p).erbjuds is True
 assert p.uppgifter['P-TJ.red01_erbjuds'].status=='saknas'

def test_faktisk_bokforing_kan_inte_kombineras_med_falsk_roll(regelbas_v1):
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.red01_erbjuds':u(True),'P-VERK.bokforing':u(False),'P-VERK.auktoriserad_revision':u(False)}})
 assert any('T-RED-01' in h for h in rattlig_omfattning(regelbas_v1,p).hinder)

def test_deterministiskt_dokument_visar_metod_tre_dimensioner_sektorreferens(regelbas_v1):
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.red01_erbjuds':u(True)}})
 b=bedom(regelbas_v1,valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
 d=bygg_arb(regelbas_v1,p,b,{},Historik())
 text=' '.join(s.text for a in d.avsnitt for s in a.stycken)
 assert 'D-ARB.2' in d.avsnitt_med_id()
 assert 'Sanktionsrisk' in text and 'för sektorn' in text

def test_underlag_filtrerar_inaktiva_uppgifter_och_doljer_liten_andel(regelbas_v1):
 p=profil(regelbas_v1)
 ups={**p.uppgifter,'P-TJ.red01_erbjuds':u(True),'P-TJ.bolag01_erbjuds':u(False)}
 period=Period(fran=date(2026,1,1),till=date(2026,9,30))
 ups['P-KUND.antal_aktiva']=u(13).model_copy(update={'period':period})
 ups['P-KUND.antal_riskbransch']=u(3).model_copy(update={'period':period})
 p=p.model_copy(update={'uppgifter':ups})
 from riskanalys.profil.omfattning import harled_andelar
 p=harled_andelar(p,regelbas_v1)
 t=bedom_tjanst(regelbas_v1,regelbas_v1.tjanster['T-RED-01'],p)
 a=bygg_underlag(regelbas_v1,p,t,'D-ARB.6.1');f={v.id:v for v in a.uppgifter}
 assert f['P-KUND.andel_riskbransch'].varde==SKYDDAD_VISNING and f['P-KUND.andel_riskbransch'].bas is None
 assert not any(k.startswith('P-TJ.bolag01_') and k!='P-TJ.bolag01_erbjuds' for k in f)

def test_ffr_ej_tillamplig_kraver_belagt_ansvar_men_skapar_inte_falsk_verifiera(regelbas_v1):
 from riskanalys.dokument.rendering import renderat_avsnitt
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-ROLL.ffr_namn':Uppgift(status='ej_tillämplig',motivering='Syntetiskt organisationsbeslut om ansvarsfördelningen',datum=date(2026,10,10),bekraftad_av='Test'),'P-ROLL.ansvarsfunktion':u('Syntetisk ansvarig')}})
 b=bedom(regelbas_v1,valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
 text=' '.join(s.text for s in renderat_avsnitt(bygg_arb(regelbas_v1,p,b,{},Historik()).avsnitt_med_id()['D-ARB.1'],p).stycken)
 assert '[VERIFIERA: FfR]' not in text and 'Syntetisk ansvarig' in text

@pytest.mark.parametrize('felt,varde',[('K-D.skalig_misstanke','false'),('K-SAKNAS',True)])
def test_kundindata_med_typfel_eller_okant_falt_avvisas(regelbas_v1,felt,varde):
 from riskanalys.fel import RiskanalysFel
 from riskanalys.regelverk.villkor import Faltvarde,Kunskap
 from riskanalys.bedomning.kundmodell.utvardering import utvardera_kundmall
 with pytest.raises(RiskanalysFel):utvardera_kundmall(regelbas_v1.kundmall,{felt:Faltvarde(Kunskap.KAND,varde)},date(2026,10,10))

def test_tjansteintakt_i_liten_kundgrupp_doljs(regelbas_v1):
 from tester.fixturer.m2 import komplett_profil
 p=komplett_profil(regelbas_v1,profil(regelbas_v1))
 t=bedom_tjanst(regelbas_v1,regelbas_v1.tjanster['T-BOLAG-01'],p)
 a=bygg_underlag(regelbas_v1,p,t,'D-ARB.6.1');f={v.id:v for v in a.uppgifter}
 assert f['P-TJ.bolag01_omsattning'].varde==SKYDDAD_VISNING
 assert f['P-TJ.bolag01_andel_omsattning'].varde==SKYDDAD_VISNING

def test_harledning_skriver_inte_aliasvyn_till_profil(regelbas_v1):
 from riskanalys.profil.omfattning import harled_andelar
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.T-RED-01.erbjuds':u(True)}})
 assert harled_andelar(p,regelbas_v1).uppgifter['P-TJ.red01_erbjuds'].status=='saknas'

def test_alias_red05_har_samma_sarbarhetsstatus_i_dokument_och_motor(regelbas_v1):
 from riskanalys.dokument.underlag import sarbarhet_status
 p=profil(regelbas_v1);p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.T-RED-05.erbjuds':u(True)}})
 assert sarbarhet_status(regelbas_v1,p,'S-TJ-01')=='ja'

def test_sanktionskontroll_och_nivaer_foljer_med_till_skrivning_och_sakgranskning(regelbas_v1):
 from riskanalys.kommandon.sakgranska_kommando import beskriv_motorns_nivaer
 p=profil(regelbas_v1)
 p=p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.red01_erbjuds':u(True),'P-GEO.sanktionsanknytning':u(False),'P-KONTROLL.C-SANK.utformning':u('finns'),'P-KONTROLL.C-SANK.genomforande':u('belagt')}})
 t=bedom_tjanst(regelbas_v1,regelbas_v1.tjanster['T-RED-01'],p)
 a=bygg_underlag(regelbas_v1,p,t,'D-ARB.6.1')
 status=next(k for k in a.kontroller if k.id=='C-SANK').status
 assert 'effekt okänd' in status and 'ingen riskreduktion är belagd' in status
 text=beskriv_motorns_nivaer(t)
 assert f'sanktionsrisk {t.sanktionsrisk.inneboende.risk}' in text.lower()
 assert f'kvarstående sanktionsrisk {t.sanktionsrisk.kvarstaende}' in text
