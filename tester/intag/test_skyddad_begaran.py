import json
import tempfile
from itertools import product
from pathlib import Path
from typing import get_args

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.bedomning.modeller import Riskdel
from riskanalys.dokument.delskrivning import lasta_texter, skriv_tjanst
from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AIStycke, AISvar
from riskanalys.dokument.nivatext import nivastycken
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.skrivning import kor_skrivning
from riskanalys.dokument.underlag import SKYDDAD_VISNING
from riskanalys.profil.hantering import personnamn
from riskanalys.profil.lagring import spara_profil
from riskanalys.profil.modeller import Uppgift
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.modeller import Konsekvens, Risk, Sannolikhet

from tester.fixturer.m2 import bygg_delsvar, godkant_delsvar, tjanst_for_prov


def begaran(rb, profil, svar=None, bedomd=None):
    """Hela den utgående AI-begäran för första tjänsten: systemprompt, innehåll och schema för varje anrop.
    `bedomd` är profilen motorn bedömer när `profil` inte klarar motorns kontroller men ändå ska prövas mot AI-vyn."""
    with tempfile.TemporaryDirectory() as mapp:
        avsnitt_id, t = tjanst_for_prov(Path(mapp), rb, bedomd or profil)
        svarslista = svar(t) if svar else [godkant_delsvar(d, t) for d in DELAR]
        lev = Testleverantor(svarslista)
        skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=personnamn(profil, rb), spara=lambda d, f: None, formatversion="D-ARB-tjanst-v5")
        return [a.model_dump(mode="json") for a in lev.delanrop]


def test_ai_far_inga_nivaer_eller_regelspar(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    assert "BT-" not in text
    for ord_ in ("inneboende_risk", "kvarstaende_risk", "Sannolikheten bedöms som", "Den kvarstående risken är"):
        assert ord_ not in text


def test_privata_grupper_och_planer_andrar_inte_ai_begaran_eller_omforsok(tmp_path,rb_intag,klar):
    from riskanalys.profil.modeller import Tjansteplan, Kombinationsgrupp
    from tester.fixturer.skrivsvar_v7 import godkant_svar_v7, med_verksamhetsval
    p=med_verksamhetsval(rb_intag,klar)
    avsnitt,t=tjanst_for_prov(tmp_path,rb_intag,p)
    bra=godkant_svar_v7(rb_intag,p,t,avsnitt)
    u=p.uppgifter['P-KUND.antal_aktiva']
    plan=Tjansteplan(id='privat',tjanst=t.tjanst,typ='ny_marknad',beskrivning='PRIVAT PLANANTAGANDE')
    grupp=Kombinationsgrupp(id='privat',tjanst=t.tjanst,population='uppdrag',avgransning='PRIVAT AVGRÄNSNING',beskrivning='PRIVAT KOMBINATION',
        sarbarheter=tuple(rb_intag.tjanster[t.tjanst].sarbarheter[:2]),antal=u.model_copy(update={'varde':8}),bas=u.model_copy(update={'varde':100}))
    andra=p.model_copy(update={'tjansteplaner':(plan,),'kombinationsgrupper':(grupp,)})
    anrop=[]
    for profil in (p,andra):
        lev=Testleverantor(['felaktig JSON',bra])
        skriv_tjanst(lev,rb_intag,profil,t,avsnitt,formatversion='D-ARB-tjanst-v8',effort='medium',personnamn=(),spara=lambda *args:None)
        anrop.append([a.model_dump_json() for a in lev.delanrop])
    assert len(anrop[0])==len(anrop[1])==2
    assert anrop[0]==anrop[1]


def _med(rb, profil, varden: dict):
    """Ny profil med ändrade värden (verkliga fält-ID som nycklar); andelar härleds på nytt ur ändrade antal."""
    upp = dict(profil.uppgifter)
    for falt_id, varde in varden.items():
        upp[falt_id] = upp[falt_id].model_copy(update={"varde": varde})
    ny = profil.model_copy(update={"uppgifter": upp})
    return harled_andelar(ny, rb, frozenset(varden))


def _lika(rb, profiler, svar=None, bedomd=None):
    forsta = begaran(rb, profiler[0], svar, bedomd)
    return all(begaran(rb, p, svar, bedomd) == forsta for p in profiler[1:])


def test_liten_grupp_0_1_3_4_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (0, 1, 3, 4)])


def test_maskerat_litet_komplement_ger_samma_begaran(rb_intag, klar):
    # 96, 97 och 99 av 100 visas som skyddat värde; även 100 prövas separat.
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-KUND.antal_riskbransch": n}) for n in (96, 97, 99)])


def test_hela_kundbasen_visas_oppet(tmp_path, rb_intag, klar):
    profil = _med(rb_intag, klar, {"P-KUND.antal_riskbransch": 100})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    # Hela kundbasen får visas enligt det uttryckliga beslutet.
    assert next(p for p in fb.poster if p.id == "P-KUND.andel_riskbransch").visningsvarde == "100 %"
    assert next(s for s in fb.sarbarheter if s.id == "S-KUND-01").galler == "ja"


def test_litet_komplement_ger_utfallet_provas_lokalt(tmp_path, rb_intag, klar):
    # 99 av 100 visas som skyddat värde; villkoret kan då inte avgöras i den synliga vyn.
    profil = _med(rb_intag, klar, {"P-KUND.antal_riskbransch": 99})
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, profil)
    fb = bygg_faktablad(rb_intag, profil, t, avsnitt_id)
    assert next(p for p in fb.poster if p.id == "P-KUND.andel_riskbransch").visningsvarde == SKYDDAD_VISNING
    assert next(s for s in fb.sarbarheter if s.id == "S-KUND-01").galler == "prövas lokalt"


def test_liten_grupp_och_liten_restgrupp_ger_samma_begaran(rb_intag, klar):
    # 3 av 100 är en liten grupp och 97 av 100 en liten restgrupp; AI ska inte se vilken sida (spec 8.4.10 punkt 8).
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-KUND.antal_riskbransch": n}) for n in (3, 97)])


def test_smagruppsfalt_utanfor_tillatelselistan_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_agare_utanfor_ees": n}) for n in (0, 1, 3, 4)])


def test_ja_nej_uppgift_utanfor_tillatelselistan_ger_samma_begaran(rb_intag, klar):
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-RISK.pep": v}) for v in (True, False)])


def test_saknad_bas_ger_samma_begaran(rb_intag, klar):
    def utan_bas(andel):
        upp = dict(klar.uppgifter)
        upp["P-GEO.antal_utland_transaktion"] = Uppgift()
        upp["P-GEO.andel_utland_transaktion"] = upp["P-KUND.antal_aktiva"].model_copy(update={"varde": andel})
        return klar.model_copy(update={"uppgifter": upp})
    # Motorn avvisar en andel utan bekräftat antal; tjänstbedömningen byggs därför ur den giltiga profilen
    # och bara AI-vyn byggs ur de ändrade uppgifterna.
    assert _lika(rb_intag, [utan_bas(0.0), utan_bas(0.03)], bedomd=klar)


def test_omforsok_ger_samma_begaran(rb_intag, klar):
    def svar(t):
        dalig = AISvar(stycken=[AIStycke(typ="analys", referenser=[t.tjanst], text="Risken är hög.")], oklarheter=[])
        return [dalig] + [godkant_delsvar(d, t) for d in DELAR]
    assert _lika(rb_intag, [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (0, 3)], svar)


def test_utfallet_provas_lokalt_i_faktabladet(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    # Faktabladet ligger som JSON-text i innehållet, så citationstecknen är maskerade i den serialiserade begäran.
    assert 'galler\\": \\"prövas lokalt\\"' in text


def _nivakandidater(t):
    """Alla nivåmeningar programmet kan skriva för tjänsten, med programmets egen formulering. En av dem är den
    riktiga. Ett svar som innehåller dem avslöjar nivån om återkopplingen jämförs mot de riktiga låsta meningarna."""
    texter = set()
    for sannolikhet, konsekvens, risk, kvarstaende in product(
            get_args(Sannolikhet), get_args(Konsekvens), get_args(Risk), get_args(Risk)):
        delen = Riskdel(sannolikhet=sannolikhet, konsekvens=konsekvens, risk=risk)
        sanktion = t.sanktionsrisk.model_copy(update={"inneboende": delen, "kvarstaende": kvarstaende}) if t.sanktionsrisk else None
        variant = t.model_copy(update={"inneboende": delen, "terrorfinansiering": delen,
                                       "kvarstaende": kvarstaende, "sanktionsrisk": sanktion})
        texter.update(stycke.text for stycke in nivastycken(variant))
    return sorted(texter)


def _nivakandidatsvar(t):
    """Ett första svar på risknivåerna med varje kandidatmening i ett eget stycke, så att stycketalet i en
    återkoppling visar vilken mening som matchade."""
    mall = godkant_delsvar("risknivaer", t).stycken[0]
    return AISvar(stycken=[mall.model_copy(update={"text": text}) for text in _nivakandidater(t)], oklarheter=[])


def _svar_med_nivakandidater(t):
    return [svar for d in DELAR for svar in
            ([_nivakandidatsvar(t)] if d == "risknivaer" else []) + [godkant_delsvar(d, t)]]


def _med_andra_nivaer(t):
    """Tjänstbedömningen med varje nivåfält och varje regelspår bytt mot värden som motorn aldrig ger."""
    def riskdel(delen):
        return delen.model_copy(update={"sannolikhet": "SENTINEL", "konsekvens": "SENTINEL", "risk": "SENTINEL"}) if delen else None
    sanktion = t.sanktionsrisk
    if sanktion:
        sanktion = sanktion.model_copy(update={"inneboende": riskdel(sanktion.inneboende), "kvarstaende": "SENTINEL",
                                               "regelspar": ("BT-SENTINEL-SANKTION",)})
    return t.model_copy(update={
        "inneboende": riskdel(t.inneboende), "terrorfinansiering": riskdel(t.terrorfinansiering),
        "kvarstaende": "SENTINEL", "sanktionsrisk": sanktion, "regelspar": ("BT-SENTINEL-1",)})


def test_nivakandidaterna_avslojar_nivan_mot_riktiga_lasta_texter(tmp_path, rb_intag, klar):
    # Förutsättning för de två proven nedan: jämförs återkopplingen mot de riktiga låsta meningarna skiljer den sig åt.
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    fb = bygg_faktablad(rb_intag, klar, t, avsnitt_id)
    kandidater = _nivakandidatsvar(t)

    def fel(tjanst):
        return validera_del("risknivaer", kandidater, fb, (), lasta_texter(rb_intag, klar, tjanst, "risknivaer"))

    assert fel(t) != fel(_med_andra_nivaer(t))


def test_motorns_nivaer_och_regelspar_paverkar_inte_begaran(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    dalig = AISvar(stycken=[AIStycke(typ="analys", referenser=[t.tjanst], text="Risken är hög.")], oklarheter=[])
    svar = [dalig, *_svar_med_nivakandidater(t)]

    def kor(tj):
        lev = Testleverantor(svar)
        skriv_tjanst(lev, rb_intag, klar, tj, avsnitt_id, effort="medium", personnamn=personnamn(klar, rb_intag), spara=lambda d, f: None, formatversion="D-ARB-tjanst-v5")
        return [a.model_dump(mode="json") for a in lev.delanrop]

    kord = kor(t)
    assert len(kord) == len(svar)  # både risknivåerna och det första delsvaret gick om
    assert kord == kor(_med_andra_nivaer(t))


def test_uppgift_utanfor_tillatelselistan_som_andrar_nivan_ger_samma_begaran_vid_omforsok(tmp_path, rb_intag, klar):
    # Nära relation (S-ARB-01) höjer bland annat H-02, som ingen av tjänstens kontroller riktar sig mot i
    # regelbas 2.0.0; därför ändras kvarstående risk. PEP höjer bara det kontrolltäckta H-03 och räcker inte längre.
    profiler = [_med(rb_intag, klar, {"P-RISK.nara_relation": v}) for v in (True, False)]
    kvarstaende = set()
    for nummer, profil in enumerate(profiler):
        mapp = tmp_path / str(nummer)
        mapp.mkdir()
        kvarstaende.add(tjanst_for_prov(mapp, rb_intag, profil)[1].kvarstaende)
    assert len(kvarstaende) == 2  # förutsättning: motorns kvarstående risk skiljer sig åt
    assert _lika(rb_intag, profiler, _svar_med_nivakandidater)


def test_kontrollernas_utfallstext_ger_samma_begaran(rb_intag, klar):
    # Samma kategorier (utformning, genomförande, effekt); bara den otillåtna utfallstexten skiljer.
    kontroller = rb_intag.tjanster["T-RED-01"].kontroller
    utfall = [rb_intag.kontroller[k].utfall_falt for k in kontroller if rb_intag.kontroller[k].utfall_falt]
    ifylld = klar
    tom = klar.model_copy(update={"uppgifter": {**klar.uppgifter, **{f: Uppgift() for f in utfall}}})
    assert utfall and _lika(rb_intag, [ifylld, tom])


def test_ai_far_ingen_bedomning_av_belagd_riskreduktion(rb_intag, klar):
    text = json.dumps(begaran(rb_intag, klar), ensure_ascii=False)
    assert "belagd riskreducerande verkan" not in text and "ingen riskreduktion är belagd" not in text


class RiktigTestleverantor(Testleverantor):
    """Heter som en riktig AI-leverantör men gör inga anrop."""

    namn = "claude"


def test_riktig_leverantor_stoppas_inte_av_sparren_med_omfattningsmetod(tmp_path, rb_intag, klar):
    assert rb_intag.metod.omfattning
    spara_profil(tmp_path, klar)
    bedomning = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    leverantor = RiktigTestleverantor(bygg_delsvar(rb_intag, klar, bedomning))
    mapp = kor_skrivning(tmp_path, rb_intag, leverantor)
    assert mapp.is_dir() and leverantor.delanrop and not leverantor.anrop


def _skriv_med_namn(rb, profil, svar):
    """Utgående begäran och tjänstresultat med profilens verkliga personnamn."""
    with tempfile.TemporaryDirectory() as mapp:
        avsnitt_id, t = tjanst_for_prov(Path(mapp), rb, profil)
        lev = Testleverantor(svar(t))
        res = skriv_tjanst(lev, rb, profil, t, avsnitt_id, effort="medium", personnamn=personnamn(profil, rb),
                           spara=lambda d, f: None, formatversion="D-ARB-tjanst-v5")
        return [a.model_dump(mode="json") for a in lev.delanrop], res


def _svar_med_namn(t):
    """Godkända svar, men hotdelen nämner Anna Svensson i genitiv."""
    hot = godkant_delsvar("hot", t)
    forsta = hot.stycken[0].model_copy(update={"text": "Anna Svenssons arbetsrutin följs. " + hot.stycken[0].text})
    return [AISvar(stycken=[forsta, *hot.stycken[1:]], oklarheter=[]) if d == "hot" else godkant_delsvar(d, t)
            for d in DELAR]


def _anna_och_bertil(rb, klar):
    anna = _med(rb, klar, {"P-ROLL.ffr_namn": "Anna Svensson"})
    bertil = _med(rb, klar, {"P-ROLL.ffr_namn": "Bertil Berg"})
    assert "Anna Svensson" in personnamn(anna, rb) and "Bertil Berg" in personnamn(bertil, rb)
    return anna, bertil


def test_personnamn_paverkar_varken_aterkoppling_eller_antal_anrop(rb_intag, klar):
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    kord_anna, _ = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    kord_bertil, _ = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    assert len(kord_anna) == len(DELAR) and kord_anna == kord_bertil


def test_del_med_personnamn_i_genitiv_ersatts_av_mallen_lokalt(rb_intag, klar):
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    _, res_anna = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    _, res_bertil = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    hot = res_anna.del_("hot")
    assert hot.mall and hot.lokal_sparr == "personnamn" and hot.godkant_svar is None
    assert not res_bertil.del_("hot").mall and res_bertil.del_("hot").lokal_sparr is None


def test_sparat_tjanstresultat_utan_lokal_sparr_kan_lasas(rb_intag, klar):
    _, res = _skriv_med_namn(rb_intag, klar, lambda t: [godkant_delsvar(d, t) for d in DELAR])
    data = json.loads(res.model_dump_json())
    for d in data["delar"]:
        d.pop("lokal_sparr")
    assert type(res).model_validate(data) == res


def test_personnamn_innehaller_bara_bekraftade_namnfalt(rb_intag, klar):
    profil = _med(rb_intag, klar, {"P-ROLL.ffr_namn": "Anna Svensson", "P-ROLL.ansvarsfunktion": "VD"})
    assert personnamn(profil, rb_intag) == ("Anna Svensson",)


def test_rolltext_orsakar_inte_lokal_namnsparr(rb_intag, klar):
    profil = _med(rb_intag, klar, {"P-ROLL.ffr_namn": "Bo", "P-ROLL.ansvarsfunktion": "VD"})
    def svar(t):
        alla = [godkant_delsvar(d, t) for d in DELAR]
        hot = alla[0]
        forsta = hot.stycken[0].model_copy(update={"text": "VD granskar avdrag och bokföring. " + hot.stycken[0].text})
        alla[0] = hot.model_copy(update={"stycken": [forsta, *hot.stycken[1:]]})
        return alla
    anrop, resultat = _skriv_med_namn(rb_intag, profil, svar)
    assert len(anrop) == len(DELAR)
    assert all(not d.mall and d.lokal_sparr is None for d in resultat.delar)


def test_kedjan_ar_identisk_for_olika_namn_och_paverkas_inte_av_namnkontrollen(rb_intag, klar):
    # Beslut 2026-10-14 (spec 8.4.10 punkt 9): AI:s egen text får följa med i kedjan, men den lokala
    # namnkontrollens resultat får aldrig påverka nästa anrop.
    anna, bertil = _anna_och_bertil(rb_intag, klar)
    anrop_anna, res_anna = _skriv_med_namn(rb_intag, anna, _svar_med_namn)
    anrop_bertil, res_bertil = _skriv_med_namn(rb_intag, bertil, _svar_med_namn)
    assert anrop_anna == anrop_bertil and len(anrop_anna) == len(DELAR)
    risknivaer = next(a for a in anrop_anna if a["del_id"] == "risknivaer")
    assert "Anna Svenssons arbetsrutin följs." in json.dumps(risknivaer, ensure_ascii=False)
    assert res_anna.del_("hot").lokal_sparr == "personnamn" and res_bertil.del_("hot").lokal_sparr is None


def test_kedjan_innehaller_bara_godkand_ai_text(rb_intag, klar):
    anrop, res = _skriv_med_namn(rb_intag, klar, lambda t: [godkant_delsvar(d, t) for d in DELAR])
    def text(*ids):
        return "\n\n".join(s.text for id in ids for s in res.del_(id).godkant_svar.stycken)
    innehall = {a["del_id"]: json.dumps(a, ensure_ascii=False) for a in anrop}
    assert json.dumps(text("hot", "sarbarheter", "kontroller"), ensure_ascii=False)[1:-1] in innehall["risknivaer"]
    assert json.dumps(text("risknivaer"), ensure_ascii=False)[1:-1] in innehall["slutsatser"]
    assert "Testa Testsson" not in innehall["risknivaer"] + innehall["slutsatser"]


def test_restgrupp_pa_synligt_geografifalt(tmp_path, rb_intag, klar):
    oppen = _med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": 90})
    avsnitt_id,t = tjanst_for_prov(tmp_path, rb_intag, oppen)
    fb = bygg_faktablad(rb_intag, oppen, t, avsnitt_id)
    assert next(p for p in fb.poster if p.id == "P-GEO.andel_utland_transaktion").visningsvarde == "90 %"
    profiler = [_med(rb_intag, klar, {"P-GEO.antal_utland_transaktion": n}) for n in (3,96,97,99)]
    assert _lika(rb_intag,profiler)
    assert _lika(rb_intag,profiler,_svar_med_nivakandidater)


def test_v8_privata_variationer_bevarar_hela_begaran_och_retry(tmp_path, rb_intag, klar):
    """Ändrat privat innehåll får ändra lokala fynd men inga externa bytes eller försök."""
    from tester.fixturer.skrivsvar_v7 import godkant_svar_v7, med_verksamhetsval
    version = 'D-ARB-tjanst-v8'
    p = med_verksamhetsval(rb_intag, klar)
    avsnitt, t = tjanst_for_prov(tmp_path, rb_intag, p)
    bra = godkant_svar_v7(rb_intag, p, t, avsnitt)
    bra = bra.model_copy(update={'stycken': [*bra.stycken, AIStycke(
        typ='analys', referenser=[t.tjanst], text='Anna Svenssons roll behöver hållas åtskild från kunden.') ]})
    fel = bra.model_copy(update={'stycken': [*bra.stycken, AIStycke(
        typ='analys', referenser=[t.tjanst], text='Fördelningen på tjänstens kunder saknas.') ]})
    andra = _med(rb_intag, p, {
        'P-TJ.red01_arbetssatt': 'PRIVAT ARBETSSÄTT',
        'P-TJ.red01_antal_riskbransch': 7,
        'P-TJ.red01_antal_kontant': 9,
        'P-ROLL.ffr_namn': 'Anna Svensson',
    })
    utfall = [rb_intag.kontroller[k].utfall_falt for k in rb_intag.tjanster[t.tjanst].kontroller
              if rb_intag.kontroller[k].utfall_falt]
    luckor = andra.model_copy(update={'uppgifter': {**andra.uppgifter,
        'P-TJ.red01_antal_riskbransch': Uppgift(),
        **{id: Uppgift() for id in utfall}}})
    varianter = [p, andra, luckor]
    begaranden = []
    resultat = []
    assert utfall and p.uppgifter[utfall[0]] != luckor.uppgifter[utfall[0]]
    for nummer, profil in enumerate(varianter):
        plats = tmp_path / f"privat-variant-{nummer}"
        plats.mkdir()
        avsnitt_variant, t_variant = tjanst_for_prov(plats, rb_intag, profil)
        lev = Testleverantor([fel, 'felaktig JSON', bra])
        res = skriv_tjanst(lev, rb_intag, profil, t_variant, avsnitt_variant, formatversion=version,
            effort='medium', personnamn=personnamn(profil, rb_intag), spara=lambda *args: None)
        begaranden.append([a.model_dump_json() for a in lev.delanrop])
        resultat.append(res.del_('analys'))
    assert len(begaranden[0]) == len(begaranden[1]) == len(begaranden[2]) == 3
    assert begaranden[0] == begaranden[1] == begaranden[2]
    assert all([f.fel for f in d.forsok] == [f.fel for f in resultat[0].forsok] for d in resultat[1:])
    assert any('fördelning' in f for f in resultat[0].forsok[0].fel)
    assert not resultat[0].mall and resultat[1].mall and resultat[2].mall
    assert resultat[1].lokal_sparr == resultat[2].lokal_sparr == 'personnamn'
    assert 'PRIVAT ARBETSSÄTT' not in ''.join(begaranden[0])
    assert all(d.forsok[-1].svar for d in resultat)
