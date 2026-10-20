"""V8:s explicita provväg och begränsade språkregressioner, inte semantisk attest."""
import pytest

from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.delskrivning import Tjanstresultat, kontrollera_resultat, skriv_tjanst
from riskanalys.dokument.faktablad import Faktapost, bygg_faktablad
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AISvar, AIStycke, AIOklarhet
from riskanalys.dokument.promptar import promptsumma
from riskanalys.dokument.skrivversion import V7, delar_for_version
from tester.enhet.test_verksamhetsval_v7 import bas, satt, tjanst
from tester.enhet.test_skrivformat_v7 import svar
from tester.fixturer.skrivsvar_v7 import godkant_svar_v7

V8 = 'D-ARB-tjanst-v8'


def provsvar(rb, p, t):
    return godkant_svar_v7(rb, p, t, 'D-ARB.6.1')


def skriv(rb, p, t, svaren, namn=()):
    lev = Testleverantor(svaren)
    res = skriv_tjanst(lev, rb, p, t, 'D-ARB.6.1', formatversion=V8,
                      effort='medium', personnamn=namn, spara=lambda *args: None)
    return res, tuple(a.model_dump_json().encode() for a in lev.delanrop)


def test_v8_egen_identitet_och_explicit_provvag(bas):
    from riskanalys.dokument.skrivversion import AKTUELL_SKRIVVERSION, AKTUELL_DOKUMENTVERSION
    rb, p = bas
    t = tjanst(rb, p)
    res, anrop = skriv(rb, p, t, [provsvar(rb, p, t)])
    assert delar_for_version(V8) == ('analys',)
    # H7.6:s slutaktivering: explicit V8-väg och normalväg har nu samma kontrakt.
    assert AKTUELL_SKRIVVERSION == AKTUELL_DOKUMENTVERSION == V8
    assert len(anrop) == 1 and res.del_('analys').godkant_svar
    assert Tjanstresultat.model_validate_json(res.model_dump_json()) == res
    kontrollera_resultat(rb, p, t, res, 'D-ARB.6.1', formatversion=V8)
    assert promptsumma('modell', 'analys', formatversion=V8) != promptsumma('modell', 'analys', formatversion=V7)


@pytest.mark.parametrize('text,tillatet', [
    ('Uppdraget omfattar bokföring. Kunden attesterar enligt uppdragsvalet. En kund kan lämna osanna fakturor för bokföring. Bankdata kan normalt visa att en betalning skett, men visar inte att varan levererats.', True),
    ('Vi har kontrollerat mottagaren.', False),
    ('Kontrollens effekt är belagd.', False),
    ('Byrån har beslutat att införa rutinen.', False),
    ('Ledningen har fastställt rutinen.', False),
    ('Kontrollen säkerställer att betalningarna är riktiga.', False),
    ('Risknivån är hög.', False),
    ('Byrån bör besluta vem som följer upp avvikelser.', True),
])
def test_v8_beskriver_modus_och_mandat_utan_lokala_pastaenden(faktablad_exempel, text, tillatet):
    fel = validera_del('analys', svar(text), faktablad_exempel, (), (), formatversion=V8)
    assert bool(fel) is not tillatet, fel


@pytest.mark.parametrize('text', [
    'Fördelningen på tjänstens kunder saknas i den lokala analysen.',
    'Det är okänt hur många av tjänstens kunder som finns i riskbranscher.',
    'Underlaget visar inte hur riskbranschkunderna fördelas på tjänsten.',
    'Byrån saknar kunskap om tjänstefördelningen.',
    'Tjänsten har fem riskbranschkunder.',
    'Ungefär hälften av tjänstens kunder har utlandsanknytning.',
])
def test_v8_spekulerar_inte_om_privata_fordelningar(faktablad_exempel, text):
    fel = validera_del('analys', svar(text), faktablad_exempel, (), (), formatversion=V8)
    assert any('fördelning' in f or 'lokalt antal' in f for f in fel), fel
    # Samma leverantörssvar får inte utlösa nya äldre rättningsinstruktioner.
    assert validera_del('analys', svar(text), faktablad_exempel, (), ()) == []


def test_v8_provar_aven_oklarheters_privata_kunskapspastaenden(faktablad_exempel):
    bra = svar()
    svar_ = bra.model_copy(update={'oklarheter': [AIOklarhet(
        uppgift_id='P-KUND.antal_aktiva', fraga='Fördelningen på tjänstens kunder saknas.') ]})
    assert any('fördelning' in f for f in validera_del('analys', svar_, faktablad_exempel, (), (), formatversion=V8))


def test_v8_har_samma_offentliga_underlag_och_schema_som_v7(bas):
    from riskanalys.dokument.aischema import ai_schema
    rb, p = bas
    t = tjanst(rb, p)
    fb = bygg_faktablad(rb, p, t, 'D-ARB.6.1', formatversion=V8)
    fb7 = bygg_faktablad(rb, p, t, 'D-ARB.6.1', formatversion=V7)
    assert fb == fb7
    assert any(u.omfang == 'tjanst' for u in fb.poster)
    assert any(k.rackvidd for k in fb.kontroller)
    schema = ai_schema(fb.tillatna_id(), fb.uppgift_id(), formatversion=V8)
    gammalt = ai_schema(fb7.tillatna_id(), fb7.uppgift_id(), formatversion=V7)
    assert schema['properties'] == gammalt['properties']
    assert schema['additionalProperties'] is False


def test_v8_ingen_hard_ordgrans(faktablad_exempel):
    assert validera_del('analys', svar(antal=400), faktablad_exempel, (), (), formatversion=V8) == []


def test_v8_lokal_efterkontroll_ger_tydligt_fynd_utan_nytt_anrop(bas, monkeypatch):
    from riskanalys.dokument import delskrivning
    from riskanalys.granskning.analys import mallfynd
    rb, p = bas
    t = tjanst(rb, p)
    bra = provsvar(rb, p, t)
    text = 'En privat mening från lokalt underlag.'
    bra = bra.model_copy(update={'stycken': [*bra.stycken, AIStycke(
        typ='analys', referenser=[t.tjanst], text=text)]})
    monkeypatch.setattr(delskrivning, 'lasta_texter', lambda *args, **kwargs: (text,))
    res1, anrop1 = skriv(rb, p, t, ['felaktig JSON', bra])
    monkeypatch.setattr(delskrivning, 'lasta_texter', lambda *args, **kwargs: ('Annan privat text.',))
    res2, anrop2 = skriv(rb, p, t, ['felaktig JSON', bra])
    assert anrop1 == anrop2 and len(anrop1) == 2
    assert res1.del_('analys').mall and not res2.del_('analys').mall
    fynd = mallfynd(res1)
    assert len(fynd) == 1 and fynd[0]['allvar'] == 'blockerande'
    assert 'lokalt låst underlag' in fynd[0]['beskrivning']
    assert 'Komplettera' in fynd[0]['atgard']


@pytest.mark.parametrize('text', [
    'Kontrollen säkerställer inte att betalningen har ett legitimt syfte.',
    'Ett möjligt upplägg kan rikta sig mot riskbranschkunder genom osanna fakturor.',
])
def test_v8_tillater_begransning_och_modus_utan_falskt_antal(faktablad_exempel, text):
    assert validera_del('analys', svar(text), faktablad_exempel, (), (), formatversion=V8) == []


@pytest.mark.parametrize('text,feltyp', [
    ('Kontrollen säkerställer inte betalningens syfte.', None),
    ('Kontrollen säkerställer inte betalningens syfte men garanterar att mottagaren är riktig.', 'kontrolleffekt'),
    ('Kontrollen garanterar att mottagaren är riktig men säkerställer inte betalningens syfte.', 'kontrolleffekt'),
    ('Kontrollen säkerställer inte betalningens syfte. Avstämningen garanterar att mottagaren är riktig.', 'kontrolleffekt'),
    ('Kontrollen säkerställer inte betalningens syfte, men vi har kontrollerat mottagaren.', 'genomförd kontroll'),
    ('Kontrollen säkerställer inte betalningens syfte. Vi har kontrollerat mottagaren.', 'genomförd kontroll'),
])
def test_v8_negation_doljer_inte_positiv_effekt_eller_utforande(faktablad_exempel, text, feltyp):
    """Negerat effektverb ger ingen dispens för andra påståenden i samma svar."""
    fel = validera_del('analys', svar(text), faktablad_exempel, (), (), formatversion=V8)
    if feltyp is None:
        assert fel == []
    else:
        assert any(feltyp in f for f in fel), fel


_BANKINSYNSSATS = (
    "Om samma kunder också anlitar byrån för bokslut, begränsar den delvisa bankinsynen i tjänsten "
    "möjligheten att följa pengarna från insättning till slutmottagare."
)
_BANKINSYN_REFERENS = "P-TJ.red01_bankinsyn"


def _fb_med_bankinsyn(faktablad, *, status="bekräftad", varde="delvis", omfang="tjanst",
                      tjanst_id=None, ta_med=True):
    if not ta_med:
        return faktablad
    post = Faktapost(id=_BANKINSYN_REFERENS, etikett="Bankinsyn", visningsvarde=varde,
                     period=None, kalltyp=None, status=status, omfang=omfang,
                     tjanst_id=tjanst_id or faktablad.tjanst_id)
    return faktablad.model_copy(update={"poster": (*faktablad.poster, post)})


def _v8_bankinsynssvar(faktablad, text, *, typ="scenario", referenser=None, antal=0):
    # Tjänstbindningen ska komma från den synliga P-TJ-posten, inte ett extra
    # tjänste-ID i styckets referenser. Faktapostens id och metadata är här
    # konsistenta med faktabladsexemplets T-RED-01.
    refs = referenser or [_BANKINSYN_REFERENS, "H-01", "H-02"]
    return svar(text, refs=refs, typ=typ, antal=antal)


def _har_riskminskningsfel(fel):
    return any("säger att risken minskar" in f for f in fel)


def test_v8_tillater_enbart_observerad_bankinsynstraff_med_synligt_tjanstfalt(faktablad_exempel):
    fb = _fb_med_bankinsyn(faktablad_exempel)
    ai_svar = _v8_bankinsynssvar(fb, _BANKINSYNSSATS)
    assert fb.tjanst_id not in ai_svar.stycken[0].referenser
    fel = validera_del("analys", ai_svar, fb, (), (), formatversion=V8)
    assert fel == []


@pytest.mark.parametrize("verb", ["minskar", "begränsar", "reducerar", "sänker"])
def test_v8_andra_riskminskningstraffar_underkanns(verb, faktablad_exempel):
    text = f"Rutinen {verb} risken för osanna fakturor."
    fel = validera_del("analys", svar(text, typ="scenario", antal=0), faktablad_exempel, (), (), formatversion=V8)
    assert _har_riskminskningsfel(fel), fel


@pytest.mark.parametrize("text", [
    _BANKINSYNSSATS[:-1] + ", och risken blir lägre.",
    _BANKINSYNSSATS[:-1] + ", och risken minskar.",
    "Om risken minskar i scenariot, " + _BANKINSYNSSATS[3:],
    _BANKINSYNSSATS + " Risken minskar.",
])
def test_v8_bankinsynstraff_ger_inte_dispens_for_koordinerad_eller_annan_riskminskning(text, faktablad_exempel):
    fb = _fb_med_bankinsyn(faktablad_exempel)
    fel = validera_del("analys", _v8_bankinsynssvar(fb, text), fb, (), (), formatversion=V8)
    assert _har_riskminskningsfel(fel), fel


def test_v8_bankinsynstraff_ger_inte_dispens_i_nasta_stycke(faktablad_exempel):
    fb = _fb_med_bankinsyn(faktablad_exempel)
    forsta = _v8_bankinsynssvar(fb, _BANKINSYNSSATS)
    andra = svar("Rutinen minskar risken i ett annat scenario.", refs=[fb.tjanst_id, "H-01", "H-02"], typ="scenario", antal=0)
    sammansatt = AISvar(stycken=[forsta.stycken[0], andra.stycken[0]], oklarheter=[])
    fel = validera_del("analys", sammansatt, fb, (), (), formatversion=V8)
    assert _har_riskminskningsfel(fel), fel


@pytest.mark.parametrize("status,varde,omfang,tjanst_id,ta_med,typ,med_referens", [
    ("okänd", "delvis", "tjanst", None, True, "scenario", True),
    ("bekräftad", "full", "tjanst", None, True, "scenario", True),
    ("bekräftad", "delvis", "byra", None, True, "scenario", True),
    ("bekräftad", "delvis", "tjanst", "T-RED-02", True, "scenario", True),
    ("bekräftad", "delvis", "tjanst", None, False, "scenario", True),
    ("bekräftad", "delvis", "tjanst", None, True, "analys", True),
    ("bekräftad", "delvis", "tjanst", None, True, "scenario", False),
])
def test_v8_bankinsynsundantag_kraver_synlig_tjanstbindning(
        faktablad_exempel, status, varde, omfang, tjanst_id, ta_med, typ, med_referens):
    fb = _fb_med_bankinsyn(faktablad_exempel, status=status, varde=varde, omfang=omfang,
                           tjanst_id=tjanst_id, ta_med=ta_med)
    refs = ["H-01", "H-02"]
    if med_referens:
        refs.append(_BANKINSYN_REFERENS)
    fel = validera_del("analys", _v8_bankinsynssvar(fb, _BANKINSYNSSATS, typ=typ, referenser=refs),
                       fb, (), (), formatversion=V8)
    assert _har_riskminskningsfel(fel), fel


@pytest.mark.parametrize("formatversion", ["D-ARB-tjanst-v5", "D-ARB-tjanst-v6", V7])
def test_bankinsynstraffens_aldre_versioner_bevarar_breda_forbud(formatversion, faktablad_exempel):
    fb = _fb_med_bankinsyn(faktablad_exempel)
    svar_ = _v8_bankinsynssvar(fb, _BANKINSYNSSATS, antal=180)
    fel = validera_del("analys", svar_, fb, (), (), formatversion=formatversion)
    assert _har_riskminskningsfel(fel), fel


@pytest.mark.parametrize("tillagg,forvantat", [
    (" Vi har verifierat mottagaren.", "genomförd kontroll"),
    (" Kontrollen är effektiv.", "kontrolleffekt"),
])
def test_v8_bankinsynsundantag_undantar_inte_pastaenden_om_utforande_eller_effekt(
        faktablad_exempel, tillagg, forvantat):
    fb = _fb_med_bankinsyn(faktablad_exempel)
    fel = validera_del("analys", _v8_bankinsynssvar(fb, _BANKINSYNSSATS + tillagg),
                       fb, (), (), formatversion=V8)
    assert any(forvantat in f for f in fel), fel
