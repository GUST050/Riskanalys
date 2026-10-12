from datetime import date
from riskanalys.bedomning.motor import bedom
from riskanalys.profil.modeller import Profil, Byra, Uppgift
from riskanalys.regelverk.urval import valj

def fall(rb):
    p=Profil(byra=Byra(id="test",regelpaket="RP-RED-VG",datum=date(2026,10,10),lan="Västra Götaland"),uppgifter={t.erbjuds_falt:Uppgift(varde=t.id=="T-RED-01",status="bekräftad",kalla="Test",datum=date(2026,10,10),bekraftad_av="Test") for t in rb.tjanster.values()})
    return p,bedom(rb,valj(rb,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)

def test_ogranskad_skala_kraver_mansklig_motivering_aven_vid_hog_niva(regelbas_v1):
    from riskanalys.bedomning.sektorsrisk import sektorsavvikelser
    p,b=fall(regelbas_v1)
    av=sektorsavvikelser(regelbas_v1,b,p)
    assert len(av)==1 and not av[0].motiverad
    assert av[0].referens=="SEKTOR-REDOVISNING"
    assert regelbas_v1.sektorsreferenser[av[0].referens].skala==("låg","medel","betydande","hög")
    assert regelbas_v1.sektorsreferenser[av[0].referens].niva=="hög"

def test_lokal_motivering_med_belagg_undanrojer_bara_saknadsfynd(regelbas_v1):
    from riskanalys.bedomning.sektorsrisk import sektorsavvikelser
    p,b=fall(regelbas_v1)
    id="P-TJ.red01_sektorsmotivering"
    u=Uppgift(varde="Syntetisk förklaring av kundkrets och skillnaden mellan skalorna.",status="bekräftad",kalla="Granskat metodbeslut",datum=date(2026,10,10),bekraftad_av="FfR")
    p=p.model_copy(update={"uppgifter":{**p.uppgifter,id:u}})
    assert sektorsavvikelser(regelbas_v1,b,p)[0].motiverad
    # En föreslagen eller utan belägg markerad motivering räcker inte.
    for bad in (u.model_copy(update={"status":"föreslagen"}),u.model_copy(update={"kalla":None}),u.model_copy(update={"varde":"hög"})):
        assert not sektorsavvikelser(regelbas_v1,b,p.model_copy(update={"uppgifter":{**p.uppgifter,id:bad}}))[0].motiverad


def test_signerad_mappning_jamfor_inneboende_inte_kvarstaende(regelbas_v1):
    from riskanalys.bedomning.sektorsrisk import sektorsavvikelser
    from riskanalys.regelverk.modeller import Sakkunnig, _summa
    p,b=fall(regelbas_v1)
    # Mappningen är explicit syntetisk; samma nivå som inneboende kräver ingen avvikelsemotivering.
    risk=next(t.inneboende.risk for t in b.tjanster if t.inneboende)
    metod=regelbas_v1.skalmappning.model_copy(update={'mappning':{**regelbas_v1.skalmappning.mappning,'hög':risk}})
    metod=metod.model_copy(update={'sakkunnig':Sakkunnig(status='verifierad',av='Test',datum=date(2026,10,10),kontrollsumma=_summa(metod.model_dump(mode='json',exclude={'sakkunnig'})))})
    rb=regelbas_v1.model_copy(update={'skalmappning':metod})
    assert not sektorsavvikelser(rb,b,p)
    # En låg kvarstående nivå skapar inte ett falskt fynd om sektorn och inneboende är jämförbara.
    b=b.model_copy(update={'tjanster':tuple(t.model_copy(update={'kvarstaende':'låg'}) if t.inneboende else t for t in b.tjanster)})
    assert not sektorsavvikelser(rb,b,p)
    # Ändrat metodinnehåll utan ny attest måste åter kräva mänsklig motivering.
    rb=rb.model_copy(update={'skalmappning':metod.model_copy(update={'forklaring':'Ändrad metodtolkning'})})
    assert not sektorsavvikelser(rb,b,p)[0].motiverad


def test_b13_behaller_katalogens_rattsliga_grund(regelbas_v1):
    from riskanalys.granskning.sektorsrisk import sektorsfynd
    p,b=fall(regelbas_v1)
    fynd=sektorsfynd(regelbas_v1,b,p)
    assert fynd and fynd[0]['grund']=='tillsynspraxis'
