import re

from riskanalys.dokument.delvalidering import LANGD
from riskanalys.dokument.promptar import DELAR, bygg_innehall, delmodul, promptsumma, systemprompt


def _taggar(block):
    return [b["text"].split(">")[0] + ">" for b in block]


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
