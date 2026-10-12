from datetime import date
from riskanalys.regelverk.urval import valj,andringar_mellan

def test_lydelsegrans_kraver_omprovning(regelbas_v1):
 u=valj(regelbas_v1,'RP-RED-VG',date(2026,11,19),'Västra Götaland')
 assert not andringar_mellan(regelbas_v1,u,date(2026,11,19))
 a=andringar_mellan(regelbas_v1,u,date(2026,11,20))
 assert any(x.lydelse.id=='LYD-PTL-1-2-2026-11-20' for x in a)

def test_borttaget_krav_kraver_omprovning(regelbas_v1):
 rb=regelbas_v1
 krav=next(iter(rb.krav.values())).model_copy(update={'upphor':date(2026,11,1)})
 rb=rb.model_copy(update={'krav':{**rb.krav,krav.id:krav}})
 u=valj(rb,'RP-RED-VG',date(2026,10,10),'Västra Götaland')
 assert any(a.krav_id==krav.id for a in andringar_mellan(rb,u,date(2026,11,2)))

def test_kundtabellens_datumgrans_kraver_omprovning(regelbas_v1):
 rb=regelbas_v1
 rader=tuple(r.model_copy(update={'ikraft':date(2026,11,1)}) if r.id=='KA-SANK-UTRED' else r for r in rb.kundmall.rader)
 rb=rb.model_copy(update={'kundmall':rb.kundmall.model_copy(update={'rader':rader})})
 u=valj(rb,'RP-RED-VG',date(2026,10,10),'Västra Götaland')
 assert not andringar_mellan(rb,u,u.datum)
 assert any(a.krav_id=='KA-SANK-UTRED' for a in andringar_mellan(rb,u,date(2026,11,2)))

def test_kundlydelsens_upphorande_kraver_omprovning(regelbas_v1):
 rb=regelbas_v1;id='LYD-EU269-ART2-2025-10-23'
 mall=rb.kundmall.model_copy(update={'lydelser':{**rb.kundmall.lydelser,id:rb.kundmall.lydelser[id].model_copy(update={'upphor':date(2026,11,1)})}})
 rb=rb.model_copy(update={'kundmall':mall})
 u=valj(rb,'RP-RED-VG',date(2026,10,10),'Västra Götaland')
 assert any(a.krav_id=='KA-SANK-STOPP' for a in andringar_mellan(rb,u,date(2026,11,2)))


def test_aldre_sparad_bedomning_utan_m2_dimensioner_stoppas(regelbas_v1):
 from riskanalys.faststallelse.grindar import Faststallelseunderlag,hinder_for_faststallelse
 from riskanalys.bedomning.motor import bedom
 from riskanalys.dokument.modeller import Dokument
 from riskanalys.drift.historik import Historik
 from riskanalys.profil.modeller import Byra
 from riskanalys.profil.hantering import skapa_profil
 from tester.fixturer.m2 import komplett_profil
 p=komplett_profil(regelbas_v1,skapa_profil(regelbas_v1,Byra(id='syntetisk',regelpaket='RP-RED-VG',datum=date(2026,10,10),lan='Västra Götaland')))
 u=valj(regelbas_v1,p.byra.regelpaket,p.byra.datum,p.byra.lan)
 b=bedom(regelbas_v1,u,p)
 b=b.model_copy(update={'omfattning':None,'tjanster':tuple(t.model_copy(update={'sanktionsrisk':None}) for t in b.tjanster)})
 d=Dokument(id='D-ARB',titel='Syntetiskt dokument',avsnitt=())
 underlag=Faststallelseunderlag(regelbas_v1,u,p,b,d,(),(),Historik(),p.byra.datum)
 hinder=hinder_for_faststallelse(underlag,p.byra.datum)
 assert any('saknar rättslig omfattning' in h for h in hinder)
 assert any('sanktionsdimension saknas' in h for h in hinder)
