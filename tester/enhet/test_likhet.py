from riskanalys.dokument.likhet import likhet


def test_lika_texter_far_hog_likhet_och_olika_lag():
    text = "Kunden kan lämna fakturor från bolag utan verklig verksamhet för bokföring som vanliga kostnader."
    assert likhet(text, text) == 1.0
    assert likhet(text, "Lönehanteringen kan användas för att betala ut ersättning till personer som inte arbetar.") < 0.2
