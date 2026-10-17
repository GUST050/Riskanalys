"""AI-text i v6 får inte återge programmets låsta stycken (spec 8.4.1) och begäran får inte bero på dem (8.4.10).

Endast syntetiska uppgifter och Testleverantor; inga API-anrop.
"""
import json

import pytest

from riskanalys.dokument.analysunderlag import erfarenhetsstycke
from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.delskrivning import kontrollera_resultat, lasta_texter, skriv_tjanst
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.lasta_v6 import erfarenhetsstycke_v6, geografistycke_v6
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.platshallare import ersatt_tal
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.analys import mallfynd
from riskanalys.profil.hantering import personnamn
from riskanalys.regelverk.granser import metodgransindex
from tester.fixturer.arb_kedja import HISTORIK, andrat, bedom_kedja, syntetisk_profil
from tester.fixturer.m2 import godkant_delsvar

RAPPORTER = "P-VERK.antal_rapporter"
AVBOJANDEN = "P-VERK.antal_avbojanden"
V5 = "D-ARB-tjanst-v5"
V6 = "D-ARB-tjanst-v6"


def _bada(profil, **uppdatering):
    return andrat(andrat(profil, RAPPORTER, **uppdatering), AVBOJANDEN, **uppdatering)


def _underlag(rb, profil):
    _, b = bedom_kedja(rb, profil)
    id, t = tjanster_med_avsnitt(b)[0]
    return b, id, t


def _last(rb, profil, t) -> str:
    (s,) = erfarenhetsstycke_v6(rb, profil, t, gransindex=metodgransindex(rb))
    return s.text


def _hot_med(t, tillagg: str, referenser=()):
    """Ett i övrigt godkänt hotsvar där första stycket avslutas med tillägget."""
    hot = godkant_delsvar("hot", t)
    forsta = hot.stycken[0]
    forsta = forsta.model_copy(update={"text": forsta.text + " " + tillagg,
                                       "referenser": [*forsta.referenser, *referenser]})
    return hot.model_copy(update={"stycken": [forsta, *hot.stycken[1:]]})


def _skriv(rb, profil, t, id, hot, *, formatversion=V6):
    lev = Testleverantor([hot, *(godkant_delsvar(d, t) for d in ("sarbarheter", "kontroller", "risknivaer", "slutsatser")
                                 if formatversion == V5 or d == "sarbarheter")])
    r = skriv_tjanst(lev, rb, profil, t, id, effort="medium", personnamn=personnamn(profil, rb),
                     spara=lambda *a: None, formatversion=formatversion)
    return r, [a.model_dump(mode="json") for a in lev.delanrop]


def _forekomster(rb, profil, b, id, r, last: str) -> int:
    d = bygg_arb_v6(rb, profil, b, {id: r}, HISTORIK, analys=None)
    return sum(s.text.count(last) for s in d.avsnitt_med_id()[id].stycken)


@pytest.fixture
def okant(regelbas_v1):
    """Rapporter och avböjanden saknas; det låsta stycket har då inga siffror och klarar AI-valideringen."""
    return _bada(syntetisk_profil(regelbas_v1), status="saknas")


def test_ai_text_som_aterger_erfarenhetsstycket_ersatts_av_mallen(regelbas_v1, okant):
    b, id, t = _underlag(regelbas_v1, okant)
    last = _last(regelbas_v1, okant, t)
    r, anrop = _skriv(regelbas_v1, okant, t, id, _hot_med(t, last))
    assert [a["del_id"] for a in anrop] == ["hot", "sarbarheter"]
    hot = r.del_("hot")
    assert hot.mall and hot.godkant_svar is None and hot.lokal_sparr is None
    assert not r.del_("sarbarheter").mall
    assert _forekomster(regelbas_v1, okant, b, id, r, last) == 1
    (fynd,) = mallfynd(r)
    assert fynd["allvar"] == "blockerande" and "delen hot" in fynd["beskrivning"]


def test_platshallarversion_av_erfarenhetsstycket_ersatts_av_mallen(regelbas_v1):
    # Tio rapporter och avböjanden visas öppet; AI kan då skriva om stycket med platshållare som blir samma text.
    profil = _bada(syntetisk_profil(regelbas_v1), varde=10)
    b, id, t = _underlag(regelbas_v1, profil)
    last = _last(regelbas_v1, profil, t)
    fb = bygg_faktablad(regelbas_v1, profil, t, id)
    omskrivet = (last.replace(f"10 ({fb.perioder()[RAPPORTER]})", "{tal:%s} ({period:%s})" % (RAPPORTER, RAPPORTER), 1)
                 .replace(f"10 ({fb.perioder()[AVBOJANDEN]})", "{tal:%s} ({period:%s})" % (AVBOJANDEN, AVBOJANDEN), 1))
    assert last not in omskrivet and ersatt_tal(omskrivet, fb.numeriska(), fb.perioder()) == last
    r, anrop = _skriv(regelbas_v1, profil, t, id, _hot_med(t, omskrivet, (RAPPORTER, AVBOJANDEN)))
    assert len(anrop) == 2 and r.del_("hot").mall
    assert _forekomster(regelbas_v1, profil, b, id, r, last) == 1


def _fore_rattelsen(r):
    """Ett sparat v6-resultat från före rättelsen, där hotdelen godkändes trots det låsta stycket."""
    return r.model_copy(update={"delar": tuple(d.model_copy(update={"mall": False}) for d in r.delar)})


def test_aterbyggnad_avvisar_sparat_v6_svar_som_aterger_last_stycke(regelbas_v1, okant):
    b, id, t = _underlag(regelbas_v1, okant)
    r, _ = _skriv(regelbas_v1, okant, t, id, _hot_med(t, _last(regelbas_v1, okant, t)))
    gammalt = _fore_rattelsen(r)
    assert gammalt.del_("hot").godkant_svar is not None
    with pytest.raises(RiskanalysFel, match="låst"):
        kontrollera_resultat(regelbas_v1, okant, t, gammalt, id, formatversion=V6)
    with pytest.raises(RiskanalysFel, match="låst"):
        bygg_arb_v6(regelbas_v1, okant, b, {id: gammalt}, HISTORIK, analys=None)


def test_aterbyggnad_avvisar_sparad_platshallarversion(regelbas_v1):
    profil = _bada(syntetisk_profil(regelbas_v1), varde=10)
    _, id, t = _underlag(regelbas_v1, profil)
    fb = bygg_faktablad(regelbas_v1, profil, t, id)
    omskrivet = _last(regelbas_v1, profil, t)
    for falt in (RAPPORTER, AVBOJANDEN):
        omskrivet = omskrivet.replace(f"10 ({fb.perioder()[falt]})", "{tal:%s} ({period:%s})" % (falt, falt), 1)
    r, _ = _skriv(regelbas_v1, profil, t, id, _hot_med(t, omskrivet, (RAPPORTER, AVBOJANDEN)))
    with pytest.raises(RiskanalysFel, match="låst"):
        kontrollera_resultat(regelbas_v1, profil, t, _fore_rattelsen(r), id, formatversion=V6)


def test_v6_jamfor_med_exakt_de_lasta_stycken_som_v6_bygget_infogar(regelbas_v1):
    profil = syntetisk_profil(regelbas_v1)
    _, _, t = _underlag(regelbas_v1, profil)
    index = metodgransindex(regelbas_v1)
    assert lasta_texter(regelbas_v1, profil, t, "hot", formatversion=V6) == (_last(regelbas_v1, profil, t),)
    assert lasta_texter(regelbas_v1, profil, t, "sarbarheter", formatversion=V6) == tuple(
        s.text for s in geografistycke_v6(regelbas_v1, profil, t.tjanst, gransindex=index))
    # Historiska v5 jämför som förut med v5:s låsta stycken.
    assert lasta_texter(regelbas_v1, profil, t, "hot") == (erfarenhetsstycke(regelbas_v1, profil, t, gransindex=index).text,)


def test_v5_skrivning_ar_oforandrad(regelbas_v1, okant):
    _, id, t = _underlag(regelbas_v1, okant)
    r, anrop = _skriv(regelbas_v1, okant, t, id, _hot_med(t, _last(regelbas_v1, okant, t)), formatversion=V5)
    assert len(anrop) == 5 and not any(d.mall for d in r.delar)
    kontrollera_resultat(regelbas_v1, okant, t, r, id, formatversion=V5)


def test_lokal_provning_mot_lasta_stycken_andrar_inte_begaran(regelbas_v1):
    """Källa och bekräftare finns inte i AI-vyn och tre rapporter är en liten grupp, men alla ändrar det låsta
    stycket. Jämfördes AI-svaret med de riktiga låsta texterna före sista anropet skulle återkopplingen och
    antalet anrop avslöja dem (spec 8.4.10 punkt 1); därför prövas de först efter tjänstens alla anrop."""
    grund = syntetisk_profil(regelbas_v1)
    profiler = [andrat(grund, "P-ROLL.ffr_namn", varde="Anna Svensson"),
                andrat(_bada(grund, kalla=" "), "P-ROLL.ffr_namn", varde="Bertil Berg"),
                andrat(_bada(grund, bekraftad_av=" "), "P-ROLL.ffr_namn", varde="Bertil Berg"),
                andrat(_bada(grund, varde=3), "P-ROLL.ffr_namn", varde="Anna Svensson")]
    underlag = [_underlag(regelbas_v1, p) for p in profiler]
    lasta = [_last(regelbas_v1, p, t) for p, (_, _, t) in zip(profiler, underlag)]
    vyer = [bygg_faktablad(regelbas_v1, p, t, id) for p, (_, id, t) in zip(profiler, underlag)]
    assert all(v == vyer[0] for v in vyer) and len(set(lasta)) == 3  # förutsättning: samma AI-vy, olika låsta texter
    korda = [_skriv(regelbas_v1, p, t, id, _hot_med(t, lasta[1])) for p, (_, id, t) in zip(profiler, underlag)]
    forsta = korda[0][1]
    assert len(forsta) == 2 and all(anrop == forsta for _, anrop in korda)
    assert [r.del_("hot").mall for r, _ in korda] == [False, True, True, False]
    text = json.dumps(forsta, ensure_ascii=False)
    for forbjudet in ("Anna Svensson", "Bertil Berg", "Syntetisk testperson", "Syntetisk testkälla", *lasta):
        assert forbjudet not in text
