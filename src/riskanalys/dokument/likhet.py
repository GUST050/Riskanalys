"""Signal för text som inte är tjänstespecifik (tillsynsbrist B-04). Ett fynd, inte ett underkännande."""


def _trigram(text: str) -> set[tuple[str, ...]]:
    ord_ = text.lower().split()
    return {tuple(ord_[i:i + 3]) for i in range(max(len(ord_) - 2, 0))}


def likhet(a: str, b: str) -> float:
    x, y = _trigram(a), _trigram(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def likhetsfynd(resultat: list, grans: float = 0.6) -> list[dict]:
    """Gränsen är ett metodval som prövas i piloten."""
    fynd = []
    for i, a in enumerate(resultat):
        for b in resultat[i + 1:]:
            for d in a.delar:
                sa, sb = d.godkant_svar, b.del_(d.del_id).godkant_svar
                if sa and sb and likhet(" ".join(s.text for s in sa.stycken), " ".join(s.text for s in sb.stycken)) >= grans:
                    fynd.append(dict(typ="tackning", allvar="hög", grund="metodval", avsnitt=a.avsnitt,
                                     beskrivning=f"Delen {d.del_id} är nästan likadan för {a.tjanst} och {b.tjanst}.",
                                     atgard="Skriv om delen så att den beskriver varje tjänsts egna förhållanden."))
    return fynd
