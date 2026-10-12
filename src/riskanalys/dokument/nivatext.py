"""Risknivåmeningar skrivs av programmet, aldrig av AI (spec 8.4.1)."""

from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.modeller import Textstycke


def nivastycken(t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    """Motorns nivåer med formuleringar som valideringens mönster känner igen."""
    refs = [t.tjanst, *t.regelspar]
    rader = [
        f"Sannolikheten bedöms som {t.inneboende.sannolikhet}. Konsekvensen är {t.inneboende.konsekvens}. "
        f"Den inneboende risken är {t.inneboende.risk}.",
        f"Sannolikheten för terrorfinansiering bedöms som {t.terrorfinansiering.sannolikhet}. "
        f"Konsekvensen för terrorfinansiering är {t.terrorfinansiering.konsekvens}. "
        f"Risken för finansiering av terrorism bedöms som {t.terrorfinansiering.risk}.",
    ]
    if t.kvarstaende:
        rader.append(f"Den kvarstående risken är {t.kvarstaende}.")
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        rader.append(f"Sanktionsrisken är {t.sanktionsrisk.inneboende.risk}.")
        if t.sanktionsrisk.kvarstaende:
            rader.append(f"Den kvarstående sanktionsrisken är {t.sanktionsrisk.kvarstaende}.")
    return tuple(Textstycke(typ="beskrivning", text=rad, referenser=refs) for rad in rader)


def sektorsstycken(rb,t: Tjanstbedomning) -> tuple[Textstycke,...]:
    ref=rb.sektorsreferenser.get(rb.tjanster[t.tjanst].sektorreferens)
    if not ref:
        return ()
    text=(f"Sektorsreferens {ref.id}: {ref.niva} på källans skala {ref.skala}, sida {ref.sida}, "
          f"version {ref.referensversion}. Källans skala är separat från byråns motor och likställs inte med tjänstens risknivå. "
          "Motiveringen ska pröva tjänstens egna förhållanden mot denna sektorsreferens.")
    return (Textstycke(typ="beskrivning",text=text,referenser=[t.tjanst,ref.id,ref.kalla]),)
