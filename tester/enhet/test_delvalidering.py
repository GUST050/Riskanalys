from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.modeller import AIStycke, AISvar

FYLLNAD = " Byrån konterar kundernas underlag och stämmer av dem mot bankens uppgifter varje månad." * 10


def _svar(*stycken):
    return AISvar(stycken=[AIStycke(typ=t, referenser=r, text=x) for t, r, x in stycken], oklarheter=[])


def test_hot_kraver_tva_hot_id(faktablad_exempel):
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01"], "Hotet gäller." + FYLLNAD)), faktablad_exempel, (), ())
    assert any("minst två hot" in f for f in fel)


def test_noll_rapporter_far_inte_bli_argument(faktablad_exempel):
    text = "Inga rapporter har lämnats, vilket visar att hotet är litet." + FYLLNAD
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], text)), faktablad_exempel, (), ())
    assert any("rapporter" in f for f in fel)


def test_siffror_utanfor_platshallare_underkanns(faktablad_exempel):
    fel = validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], "Tjänsten har 120 kunder." + FYLLNAD)),
                       faktablad_exempel, (), ())
    assert any("siffror" in f for f in fel)


def test_slutsatser_maste_namna_kundkannedom_overvakning_utbildning(faktablad_exempel):
    fel = validera_del("slutsatser", _svar(("analys", ["T-RED-01", "H-01"], "Byrån följer upp." + FYLLNAD)), faktablad_exempel, (), ())
    assert any("kundkännedom" in f for f in fel)


def test_last_mening_far_inte_upprepas(faktablad_exempel):
    last = "Den kvarstående risken är hög."
    fel = validera_del("risknivaer", _svar(("motivering", ["T-RED-01", "H-01", "P-KUND.antal_aktiva"], last + FYLLNAD)),
                       faktablad_exempel, (), (last,))
    assert any("låst mening" in f for f in fel)


def test_godkand_del_ger_inga_fel(faktablad_exempel):
    text = "Osanna fakturor kan bokföras som kostnader och brottsvinster kan redovisas som intäkter." + FYLLNAD
    assert validera_del("hot", _svar(("analys", ["T-RED-01", "H-01", "H-02"], text)), faktablad_exempel, (), ()) == []

from riskanalys.dokument.modeller import UnderlagKontroll, UnderlagSarbarhet
from riskanalys.dokument.underlag import kontrollstatus
from riskanalys.bedomning.modeller import Kontrollbedomning


def test_riskminskning_kraver_belagd_refererad_kontroll(faktablad_exempel):
    k = Kontrollbedomning(id='C-07', utformning='finns', genomforande='belagt', fungerar_och_ar_belagd=False)
    fb = faktablad_exempel.model_copy(update={'kontroller': (UnderlagKontroll(id=k.id, namn='Kontroll', status=kontrollstatus(k)),)})
    text = 'Kontrollen minskar risken för osanna fakturor.' + FYLLNAD
    assert any('belagd effekt' in f for f in validera_del('kontroller', _svar(('analys', ['C-07'], text)), fb, (), ()))


def test_belagd_kontroll_fran_motorn_far_beskrivas(faktablad_exempel):
    k = Kontrollbedomning(id='C-07', utformning='finns', genomforande='belagt', effekt='effektiv', effekt_belagd=True, fungerar_och_ar_belagd=True)
    fb = faktablad_exempel.model_copy(update={'kontroller': (UnderlagKontroll(id=k.id, namn='Kontroll', status=kontrollstatus(k)),)})
    assert not validera_del('kontroller', _svar(('analys', ['C-07'], 'Kontrollen minskar risken för osanna fakturor.' + FYLLNAD)), fb, (), ())


def test_kombination_utan_belagt_overlapp_maste_vara_scenario(faktablad_exempel):
    fb = faktablad_exempel.model_copy(update={'sarbarheter': tuple(UnderlagSarbarhet(id=i, namn=i, galler='ja') for i in ['S-KUND-01', 'S-KANAL-01'])})
    text = 'Faktorerna kan samverka om samma kund berörs.' + FYLLNAD
    assert any('överlapp' in f for f in validera_del('sarbarheter', _svar(('analys', ['S-KUND-01','S-KANAL-01'], text)), fb, (), ()))
    assert not validera_del('sarbarheter', _svar(('scenario', ['S-KUND-01','S-KANAL-01'], text)), fb, (), ())


def test_obekraftad_referens_kraver_aven_oklarhet(faktablad_exempel):
    fb=faktablad_exempel.model_copy(update={'poster':tuple(p.model_copy(update={'status':'okänd','tal':None,'visningsvarde':'okänt'}) for p in faktablad_exempel.poster)})
    s=_svar(('motivering',['H-01','P-KUND.antal_aktiva'],'Omfattningen är okänd. [VERIFIERA]'+FYLLNAD))
    assert any('Oklarhet' in f for f in validera_del('risknivaer',s,fb,(),()))


def test_felskriven_verifiera_och_personnamn_i_oklarhet_stoppar(faktablad_exempel):
    from riskanalys.dokument.modeller import AIOklarhet
    s=_svar(('analys',['H-01','H-02'],'Kontrollera underlaget [VERIFIERA: saknas]'+FYLLNAD))
    s=s.model_copy(update={'oklarheter':[AIOklarhet(uppgift_id='P-KUND.antal_aktiva',fraga='Fråga Kim Testsson')]})
    fel=validera_del('hot',s,faktablad_exempel,('Kim Testsson',),())
    assert any('VERIFIERA' in f for f in fel) and any('personnamn' in f for f in fel)


def test_terrorhot_och_alla_sarbarhetskategorier_kravs(faktablad_exempel):
    from riskanalys.dokument.modeller import UnderlagHot
    fb=faktablad_exempel.model_copy(update={'tf_hot':('H-TF-01',),'hot':(*faktablad_exempel.hot,UnderlagHot(id='H-TF-01',namn='TF',beskrivning='Legala medel')),'sarbarhetsomraden':{'S-GEO-01':'geo','S-KUND-01':'kund'}})
    assert any('terrorfinansiering' in f for f in validera_del('hot',_svar(('analys',['H-01','H-02'],'Hot finns.'+FYLLNAD)),fb,(),()))
    assert any('kategori' in f for f in validera_del('sarbarheter',_svar(('analys',['S-KUND-01'],'Kunderna berörs.'+FYLLNAD)),fb,(),()))


def test_pahittat_artal_ar_inte_ett_tillatet_tal(faktablad_exempel):
    assert any('siffror' in f for f in validera_del('hot',_svar(('analys',['H-01','H-02'],'Byrån rapporterade under 2025.'+FYLLNAD)),faktablad_exempel,(),()))


def test_obelagd_kontroll_far_beskrivas_som_att_den_inte_sanker_nivan(faktablad_exempel):
    k=UnderlagKontroll(id='C-07',namn='Kontroll',status='Effekt inte belagd')
    fb=faktablad_exempel.model_copy(update={'kontroller':(k,)})
    svar=_svar(('analys',['C-07'],'Kontrollen sänker inte risknivån eftersom effekten inte är belagd.'+FYLLNAD))
    assert not validera_del('kontroller',svar,fb,(),())

import pytest

@pytest.mark.parametrize('text',['Hög risk för penningtvätt finns bland dessa kunder.','Konsekvenserna är allvarliga.','En låg sannolikhet för penningtvätt föreligger.','Riskerna är höga.','Höga risker finns bland kunderna.'])
def test_ai_far_inte_satta_niva_med_annan_ordfoljd(text,faktablad_exempel):
    fel=validera_del('hot',_svar(('analys',['H-01','H-02'],text+FYLLNAD)),faktablad_exempel,(),())
    assert any('anger en nivå' in f for f in fel)


@pytest.mark.parametrize('periodtext', ['under {period:P-KUND.antal_aktiva}', 'under statistikperioden'])
def test_statistikperiod_kan_beskrivas_utan_fria_datum(periodtext, faktablad_exempel):
    svar = _svar(('analys', ['H-01', 'H-02', 'P-KUND.antal_aktiva'],
        'Byrån stämmer av kundernas underlag ' + periodtext + '.' + FYLLNAD))
    assert validera_del('hot', svar, faktablad_exempel, (), ()) == []


@pytest.mark.parametrize('galler,text', [
    (('nej', 'nej'), 'Varken riskbranscher eller kontanthantering gäller.'),
    (('nej', 'nej'), 'Byrån redovisar riskbranscher och kontanthantering var för sig.'),
    (('nej', 'ja'), 'Kontanthantering förekommer, men inga riskbranscher förekommer.'),
    (('nej', 'okänt'), 'Kontanthantering är okänd, men inga riskbranscher förekommer.'),
])
def test_tva_s_referenser_ar_inte_kombination_nar_hogst_en_galler(galler, text, faktablad_exempel):
    ids = ['S-KUND-01', 'S-KUND-02']
    fb = faktablad_exempel.model_copy(update={'sarbarheter': tuple(
        UnderlagSarbarhet(id=id, namn=id, galler=g) for id, g in zip(ids, galler))})
    svar = _svar(('analys', ids, text + FYLLNAD))
    assert not validera_del('sarbarheter', svar, fb, (), ())


@pytest.mark.parametrize('galler', [('ja', 'ja'), ('ja', 'okänt'), ('okänt', 'okänt')])
def test_tva_gallande_eller_okanda_sarbarheter_kraver_scenario(galler, faktablad_exempel):
    ids = ['S-KUND-01', 'S-KUND-02']
    fb = faktablad_exempel.model_copy(update={'sarbarheter': tuple(
        UnderlagSarbarhet(id=id, namn=id, galler=g) for id, g in zip(ids, galler))})
    assert any('överlapp' in f for f in validera_del('sarbarheter',
        _svar(('analys', ids, 'Byrån redovisar kundernas egenskaper.' + FYLLNAD)), fb, (), ()))


@pytest.mark.parametrize('samverkan', ['samverkar', 'i kombination', 'tillsammans', 'förstärker'])
def test_samverkansord_kraver_scenario_aven_med_nej(samverkan, faktablad_exempel):
    ids = ['S-KUND-01', 'S-KUND-02']
    fb = faktablad_exempel.model_copy(update={'sarbarheter': tuple(
        UnderlagSarbarhet(id=id, namn=id, galler='nej') for id in ids)})
    svar = _svar(('analys', ids, 'Faktorerna ' + samverkan + ' påverkar granskningen.' + FYLLNAD))
    assert any('överlapp' in f for f in validera_del('sarbarheter', svar, fb, (), ()))


def test_skyddad_bekraftad_faktapost_kraver_inte_verifiera_eller_oklarhet(faktablad_exempel):
    fb = faktablad_exempel.model_copy(update={'poster': tuple(
        p.model_copy(update={'status': 'skyddad', 'tal': None, 'visningsvarde': 'färre än 5'})
        for p in faktablad_exempel.poster)})
    svar = _svar(('analys', ['H-01', 'H-02', 'P-KUND.antal_aktiva'],
        'Byrån beskriver omfattningen genom maskerad statistik.' + FYLLNAD))
    assert validera_del('hot', svar, fb, (), ()) == []


def test_skyddat_tal_far_fortfarande_inte_anvandas_i_platshallare(faktablad_exempel):
    fb = faktablad_exempel.model_copy(update={'poster': tuple(
        p.model_copy(update={'status': 'skyddad', 'tal': None, 'visningsvarde': 'färre än 5'})
        for p in faktablad_exempel.poster)})
    svar = _svar(('analys', ['H-01', 'H-02', 'P-KUND.antal_aktiva'],
        'Byrån har {tal:P-KUND.antal_aktiva} kunder.' + FYLLNAD))
    fel = validera_del('hot', svar, fb, (), ())
    assert any('okänt eller skyddat' in f for f in fel)
    assert not any('obekräftad' in f for f in fel)
