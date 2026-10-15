"""Mätning av skrivkörningar: förstaförsök, omförsök, felklasser och tokens (spec 8.4.7–8.4.8)."""

from collections import Counter
from collections.abc import Iterable

from riskanalys.dokument.modeller import Last

_KLASSER = (("talet", "tal"), ("anger en nivå", "niva"), ("Oklarhet", "oklarhet"), ("hänvisar till", "referens"),
            ("schemat", "schema"), ("platshållare", "platshallare"))


class Skrivsammanfattning(Last):
    avsnitt: int
    godkanda_forsta_forsoket: int
    anrop: int
    indata_token: int
    utdata_token: int
    felklasser: dict[str, int]
    cache_lasning_token: int = 0
    cache_skrivning_token: int = 0


def felklass(fel: str) -> str:
    return next((klass for nyckel, klass in _KLASSER if nyckel in fel), "ovrigt")


def sammanfatta(resultat: Iterable) -> Skrivsammanfattning:
    lista = list(resultat)
    delar = [d for r in lista for d in r.delar] if lista and hasattr(lista[0], "delar") else lista
    forsok = [f for r in delar for f in r.forsok]
    poster = [p for f in forsok for p in f.anrop.anvandning]
    return Skrivsammanfattning(
        avsnitt=len(delar),
        godkanda_forsta_forsoket=sum(1 for r in delar if r.forsok and not r.forsok[0].fel and not getattr(r, "mall", False)),
        anrop=len(forsok),
        indata_token=sum(p.indata_token for p in poster),
        utdata_token=sum(p.utdata_token for p in poster),
        cache_lasning_token=sum(p.cache_lasning_token for p in poster),
        cache_skrivning_token=sum(p.cache_skrivning_token for p in poster),
        felklasser=dict(Counter(felklass(fel) for f in forsok for fel in f.fel)
                       + Counter(r.lokal_sparr for r in delar if getattr(r, "lokal_sparr", None))),
    )


def kostnad_usd(s: Skrivsammanfattning, indatapris: float, utdatapris: float, *, cache_laspris: float | None = None, cache_skrivpris: float | None = None) -> float:
    """Pris i USD per miljon token."""
    laspris=indatapris if cache_laspris is None else cache_laspris
    skrivpris=indatapris if cache_skrivpris is None else cache_skrivpris
    return round((s.indata_token*indatapris+s.utdata_token*utdatapris+s.cache_lasning_token*laspris+s.cache_skrivning_token*skrivpris)/1e6,4)
