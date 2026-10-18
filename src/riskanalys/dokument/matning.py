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


def dokumentord(dokument, profil) -> dict[str, int]:
    """Synlig modelltext efter lokal substitution; Word-fältens cache räknas inte dubbelt."""
    from riskanalys.dokument.rendering import renderat_avsnitt, synliga_texter
    huvud=len(dokument.titel.split()); bilaga=0
    for a in dokument.avsnitt:
        antal=sum(len(text.split()) for text in synliga_texter(renderat_avsnitt(a,profil)))
        if a.id.startswith('D-ARB.B'):
            bilaga+=antal
        else:
            huvud+=antal
    return {'huvudtext':huvud,'bilaga':bilaga,'totalt':huvud+bilaga}


def med_langdvarning(dokument, profil):
    """Redaktionellt mål, aldrig trunkering eller ett nytt fastställelsekrav."""
    from riskanalys.dokument.modeller import Textstycke
    grans = 4700 if dokument.formatversion in ('D-ARB-tjanst-v6', 'D-ARB-tjanst-v7') else 5000
    gransnamn = '4 700' if grans == 4700 else '5 000'
    varningstext=(f'Redaktionell längdvarning: huvudtexten överstiger riktmärket {gransnamn} ord för fyra tjänster. '
        'Gör en redaktionell genomgång; inga underlag har kapats för att uppfylla målet.')
    avsnitt=tuple(a.model_copy(update={'stycken':tuple(s for s in a.stycken if s.text!=varningstext or s.referenser)})
                  for a in dokument.avsnitt)
    ren=dokument.model_copy(update={'avsnitt':avsnitt})
    if not avsnitt or dokumentord(ren,profil)['huvudtext']<=grans:
        return ren
    varning=Textstycke(typ='beskrivning',text=varningstext,referenser=[])
    for index,a in enumerate(avsnitt):
        if not a.id.startswith('D-ARB.B'):
            return ren.model_copy(update={'avsnitt':(*avsnitt[:index],a.model_copy(update={'stycken':(*a.stycken,varning)}),*avsnitt[index+1:])})
    return ren
