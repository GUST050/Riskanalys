import re

from riskanalys.dokument.delvalidering import LANGD
from riskanalys.dokument.promptar import DELAR, bygg_innehall, delmodul, promptsumma, systemprompt


def _taggar(block):
    return [b["text"].split(">")[0] + ">" for b in block]


def test_v7_uppgift_preciserar_synliga_kategorier_omfang_och_redaktionell_langd():
    from riskanalys.dokument.skrivversion import V7
    text = delmodul('analys', formatversion=V7)
    for krav in ('kund = kunder', 'kanal = distributionskanaler', 'geo = geografi',
                 'tj = tjänstespecifika', 'verk = verksamhetsspecifika',
                 'S-ID', 'ja, nej eller okänt', 'P-ID ersätter inte',
                 'nej är en avgränsning', 'inte frånvaro av hot',
                 '240–280 ord', '160–320 ord', 'utgivningsår', 'sidnummer',
                 'referenser', 'inom just tjänsten', 'fullständiga lokala analysen',
                 'avsiktligt', 'fördelningen skrivs lokalt', 'lokala låsta delen',
                 'Återberätta inte rapporteringsantal', 'överlåt dem till programmet',
                 'rapporteringsantal inte mäter den faktiska exponeringen'):
        assert krav in text, krav


def test_v5_v6_hela_begaran_och_retryfeedback_bevaras():
    """Frysta historiska bytekedjor från före V7:s skrivprecisering, inklusive två feltyper."""
    import hashlib
    import json
    import gzip
    from pathlib import Path
    from riskanalys.regelverk.modeller import Regelbas
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.skrivversion import V5, V6, delar_for_version
    from tester.fixturer.arb_kedja import syntetisk_profil, bedom_kedja
    from tester.fixturer.m2 import godkant_delsvar
    # Historiska begärandebytes prövas med sin regelbas, inte senare kataloger.
    # Fryst från godkända 48991af; befintliga request-hashar behålls orörda.
    fil = Path(__file__).parents[1] / 'fixturer/promptar_v5_v6_regelbas_2_0_0.json.gz'
    rb = Regelbas.model_validate_json(gzip.decompress(fil.read_bytes()))
    assert rb.kontrollsumma == 'sha256:b4dc7018b05b340e746d31efd0a49ee837fa1312c126a24f5571445a27132a58'
    p = syntetisk_profil(rb)
    _, bedomning = bedom_kedja(rb, p)
    t = next(t for t in bedomning.tjanster if t.tjanst == 'T-RED-01')
    hot = godkant_delsvar('hot', t)
    hot = hot.model_copy(update={'stycken': [s.model_copy(update={
        'text': s.text + ' Inga rapporter visar att hotet saknas.'}) for s in hot.stycken]})
    for version, fryst in {
        V5: 'ad9459abeaadb1323f52e7dc30edf2f063f60980f3c61c6f7604228da9aee934',
        V6: '7d48d0a710f885a35b7e28d5407bd0c88b5dde231ff8b65b469bb8c8b5d78bdb',
    }.items():
        lev = Testleverantor(['fel', hot, 'fel'] + ['fel'] * (3 * (len(delar_for_version(version)) - 1)))
        res = skriv_tjanst(lev, rb, p, t, 'D-ARB.6.1', formatversion=version,
                          effort='medium', personnamn=(), spara=lambda *args: None)
        assert len(lev.delanrop) == 3 * len(delar_for_version(version))
        assert any('rapporter' in f for d in res.delar for a in d.forsok for f in a.fel)
        kedja = {'requests': [a.model_dump_json() for a in lev.delanrop],
                 'feedback': [[list(a.fel) for a in d.forsok] for d in res.delar]}
        data = json.dumps(kedja, ensure_ascii=False, sort_keys=True).encode()
        assert hashlib.sha256(data).hexdigest() == fryst


def test_systemprompten_ar_fast_lang_nog_och_utan_datum():
    text = systemprompt("claude-opus-5-5")
    assert text == systemprompt("claude-opus-5-5")
    assert len(text) >= 2400  # cirka 512 token eller mer, så att den kan cachas
    assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text)
    assert "MUST" not in text and "VIKTIGT" not in text


def test_sonnetraden_bara_for_sonnet():
    assert systemprompt("claude-sonnet-5-5").endswith("Think the problem through before you answer.")
    assert "Think the problem" not in systemprompt("claude-opus-5-5")


def test_varje_del_har_modul_och_egen_summa():
    assert len({promptsumma("claude-opus-5-5", d) for d in DELAR}) == len(DELAR)
    for d in DELAR:
        assert len(delmodul(d)) > 400


def test_innehallet_har_fast_ordning_och_cachebrytpunkt(faktablad_exempel):
    block = bygg_innehall(faktablad_exempel, "hot", ("Låst mening.",), (), ())
    assert block[0]["cache_control"] == {"type": "ephemeral"}
    assert _taggar(block) == ["<faktablad>", "<lasta_meningar>", '<uppgift del="hot">']
    med = bygg_innehall(faktablad_exempel, "risknivaer", (), ("Godkänd text.",), ("Fel 1.",))
    assert _taggar(med) == ["<faktablad>", "<maskinellt_validerat>", '<uppgift del="risknivaer">', "<aterkoppling>"]


def test_sarbarhetsuppgiften_forklarar_alla_fem_kategorier(faktablad_exempel):
    block = bygg_innehall(faktablad_exempel, 'sarbarheter', (), (), ())
    uppgift = next(b['text'] for b in block if b['text'].startswith('<uppgift'))
    for kod, namn in [('kund', 'kunder'), ('kanal', 'distributionskanaler'), ('geo', 'geografi'),
                      ('tj', 'tjänstespecifika förhållanden'), ('verk', 'verksamhetsspecifika förhållanden')]:
        assert kod + ' = ' + namn in uppgift


def test_varje_delmodul_anger_sitt_langdintervall():
    for d in DELAR:
        lagst, hogst = LANGD[d]
        assert f"{lagst}–{hogst} ord" in delmodul(d)


def test_uppgiftsblocket_innehaller_langdintervallet(faktablad_exempel):
    block = bygg_innehall(faktablad_exempel, "hot", (), (), ())
    lagst, hogst = LANGD["hot"]
    assert f"{lagst}–{hogst} ord" in next(b["text"] for b in block if b["text"].startswith('<uppgift del="hot">'))


def test_promptarna_foreslar_formuleringen_som_valideringen_godtar():
    assert "ingen belagd kombination finns" in systemprompt("claude-opus-5-5")
    assert "ingen belagd kombination finns" in delmodul("sarbarheter")
    assert "varje sårbarhet i ett eget stycke" not in delmodul("sarbarheter")
    assert "varje kategori i ett eget stycke" in delmodul("sarbarheter")


def test_systemprompten_ber_om_lokal_granskning_i_stallet_for_kommentarer_om_underlaget():
    assert "underlaget behöver granskas lokalt" in systemprompt("claude-opus-5-5")


def test_sarbarhetsmodulen_styr_formuleringen_under_gransen():
    assert "förekommer men ligger under metodens gräns" in delmodul("sarbarheter")
    assert "utan att ange gränsens värde" in delmodul("sarbarheter")
    assert "andelen skrivs som {tal:ID}" in delmodul("sarbarheter")


def test_risknivamodulen_sager_att_ai_inte_ser_nivaerna():
    assert "du ser inte motorns nivåer" in delmodul("risknivaer")
    assert "motorns nivå" not in delmodul("slutsatser")


def test_modulerna_beskriver_utfallet_provas_lokalt():
    assert "prövas lokalt" in delmodul("sarbarheter")
    assert "prövas lokalt" in delmodul("risknivaer")


def test_kontrollmodulen_sager_att_riskreduktion_avgors_lokalt():
    assert "avgör programmet lokalt" in delmodul("kontroller")


def test_kontrollmodulen_forbjuder_alla_fyra_verben():
    # Samma verb som valideringen i kontrolldelen underkänner (delvalidering._MINSKNING).
    assert "minskar, begränsar, reducerar eller sänker risk" in " ".join(delmodul("kontroller").split())


def test_riskdelens_uppgift_ar_kvalitativ_syntes(faktablad_exempel):
    block=bygg_innehall(faktablad_exempel,'risknivaer',(),(),())
    text=next(b['text'] for b in block if b['text'].startswith('<uppgift'))
    assert 'Scenarier och osäkerheter' in text
    assert 'kvalitativ syntes' in text
    assert 'inte varför en viss nivå är riktig' in text
    assert 'villkorliga scenarier' in text
    assert 'motivera skillnader' not in text
