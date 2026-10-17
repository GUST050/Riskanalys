from argparse import Namespace

import pytest

from riskanalys.dokument.matning import sammanfatta
from riskanalys.granskning.analys import mallfynd
from tester.intag.test_v3_grind import v3


def namnstopp(res):
    return res.model_copy(update={"delar": tuple(
        d.model_copy(update={"mall": True, "lokal_sparr": "personnamn"}) if d.del_id == "hot" else d
        for d in res.delar)})


def test_namnstopp_raknas_inte_som_godkant_forstaforsok(v3):
    res = namnstopp(v3[3])
    sammanfattning = sammanfatta([res])
    assert sammanfattning.godkanda_forsta_forsoket == 4
    assert sammanfattning.anrop == 5
    assert sammanfattning.felklasser == {"personnamn": 1}


def test_namnfynd_ger_konkret_atgard_utan_att_roja_namnet(v3):
    fynd = mallfynd(namnstopp(v3[3]))[0]
    assert "roll" in fynd["atgard"].lower()
    assert "personnamn" in fynd["atgard"].lower()
    assert "sakgranska" in fynd["atgard"].lower()


def test_cli_redovisar_lokal_sparr_och_ratt_antal(v3, monkeypatch, tmp_path, capsys):
    from riskanalys.kommandon import skriv_kommando as cli
    rb, profil, t, res, avsnitt = v3
    monkeypatch.setattr(cli, "befintlig_byramapp", lambda _: tmp_path)
    monkeypatch.setattr(cli, "ladda_giltig_regelbas", lambda _: rb)
    monkeypatch.setattr(cli, "valj_leverantor", lambda _: None)
    monkeypatch.setattr(cli, "kor_skrivning", lambda *a, **k: tmp_path)
    monkeypatch.setattr(cli, "las_skrivresultat", lambda _: [namnstopp(res)])
    assert cli.kor_skriv(Namespace(byra="syntetisk", regelbas=None, effort="medium")) == 2
    text = capsys.readouterr().out
    assert "personnamn" in text.lower()
    assert "godkända direkt: 4" in text
    assert "roll" in text.lower()


def test_omforsok_aterger_inte_namn_i_felskriven_platshallare(rb_intag, klar):
    import json
    from riskanalys.dokument.promptar import DELAR
    from tester.fixturer.m2 import godkant_delsvar
    from tester.intag.test_skyddad_begaran import begaran

    def svar(t):
        forsta = godkant_delsvar("hot", t)
        stycken = list(forsta.stycken)
        stycken[0] = stycken[0].model_copy(update={"text": stycken[0].text + " {Anna Svensson} {tal:AnnaSvensson} P-NAMN.AnnaSvensson."})
        dalig = forsta.model_copy(update={"stycken": stycken})
        return [dalig] + [godkant_delsvar(d, t) for d in DELAR]

    anrop = begaran(rb_intag, klar, svar)
    assert len(anrop) == 6
    assert "Anna Svensson" not in json.dumps(anrop, ensure_ascii=False)
    assert "AnnaSvensson" not in json.dumps(anrop, ensure_ascii=False)


def test_namnstopp_hela_vagen_till_dokument_och_blockerande_fynd(tmp_path, rb_intag, klar):
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.granskning.korning import kor_granskning, las_granskning
    from tester.fixturer.m2 import bygg_delsvar, DAG

    namn = klar.uppgifter["P-ROLL.ffr_namn"].model_copy(update={"varde": "Testa Testsson"})
    klar = klar.model_copy(update={"uppgifter": {**klar.uppgifter, "P-ROLL.ffr_namn": namn}})
    spara_profil(tmp_path, klar)
    b = las_bedomning(kor_bedomning(tmp_path, rb_intag))
    svar = bygg_delsvar(rb_intag, klar, b)
    hot = svar[0]
    from riskanalys.dokument.promptar import DELAR
    assert DELAR[0] == 'hot'
    svar[0] = hot.model_copy(update={'stycken': [hot.stycken[0].model_copy(update={
        'text': 'Testa Testssons rutin följs. ' + hot.stycken[0].text}), *hot.stycken[1:]]})
    kor_skrivning(tmp_path, rb_intag, Testleverantor(svar))
    dokument, fynd = las_granskning(kor_granskning(tmp_path, rb_intag, DAG))
    namnfynd = [f for f in fynd if 'innehöll ett bekräftat personnamn' in f.beskrivning]
    assert len(namnfynd) == 1 and namnfynd[0].allvar == 'blockerande'
    assert all('Testa Testssons rutin' not in s.text for a in dokument.avsnitt for s in a.stycken)
    hottext = rb_intag.hot[b.tjanster[0].hot[0]].beskrivning
    assert any(hottext in s.text for a in dokument.avsnitt for s in a.stycken)


@pytest.mark.parametrize("hela_dokumentet", [False, True])
def test_gransindex_beraknas_en_gang_per_bygge(v3, monkeypatch, tmp_path, hela_dokumentet):
    import sys
    from riskanalys.regelverk import granser
    from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
    from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
    rb, profil, t, res, id = v3
    bedomning = las_bedomning(kor_bedomning(tmp_path, rb))
    original = granser.metodgransindex
    anrop = []
    def rakna(rb):
        anrop.append(rb)
        return original(rb)
    # Fånga både direktimporter och metodgranser-funktionens återfall.
    for namn, modul in tuple(sys.modules.items()):
        if namn.startswith('riskanalys.') and getattr(modul, 'metodgransindex', None) is original:
            monkeypatch.setattr(modul, 'metodgransindex', rakna)
    if hela_dokumentet:
        from riskanalys.dokument.arb_v5 import bygg_arb_v5
        from riskanalys.drift.historik import Historik
        bygg_arb_v5(rb, profil, bedomning, {id: res}, Historik())
    else:
        bygg_tjanstavsnitt_v3(rb, profil, t, res, id)
    assert len(anrop) == 1
