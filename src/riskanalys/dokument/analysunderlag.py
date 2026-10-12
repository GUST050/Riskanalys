"""Lokala motiveringar med källor; fritext skickas aldrig vidare till AI."""
from riskanalys.bedomning.erfarenheter import ERFARENHETSFALT
from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.klartext import VERIFIERA, gransmening, under_grans, uppgiftstext, villkorstext
from riskanalys.dokument.modeller import Textstycke
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor, utvardera, Sanning


def _belagg(regelbas: Regelbas, profil: Profil, id: str) -> str:
    return uppgiftstext(regelbas, profil, id)


def erfarenhetsstycke(regelbas: Regelbas, profil: Profil, tjanst: Tjanstbedomning) -> Textstycke:
    e = tjanst.egen_erfarenhet
    text = f"Egen erfarenhet i hotanalysen för {regelbas.tjanster[tjanst.tjanst].namn}. "
    text += " ".join(_belagg(regelbas, profil, id) for id in ERFARENHETSFALT)
    if e is None or not e.belagd:
        text += f" Rapporteringens underlag är ofullständigt och kan inte bedömas. {VERIFIERA}"
    elif e.rapporter == "inga":
        text += " Noll rapporter visar att ingen rapport lämnats under perioden, inte frånvaro av hot eller misstankar."
    else:
        text += " Rapporter har lämnats efter identifierade misstankar; de relevanta tillvägagångssätten behöver prövas mot tjänstens hot."
    if e and e.avbojanden == "finns":
        text += " Misstankebaserade avböjanden visar också egna observationer, men är inte i sig lämnade misstankerapporter."
    text += " Antalen gäller hela byrån och får inte tillskrivas just denna tjänst eller användas som riskpoäng."
    refs = [tjanst.tjanst, *ERFARENHETSFALT]
    slug = regelbas.tjanster[tjanst.tjanst].erbjuds_falt.removesuffix("_erbjuds")
    for id, rubrik in (("P-BESK.erfarenheter", "Byråns egna erfarenheter"),
                       (slug + "_ovriga_risker", "Byråns erfarenheter i tjänsten")):
        if id not in regelbas.falt:
            continue
        refs.append(id)
        text += " " + uppgiftstext(regelbas, profil, id, namn=rubrik)
    return Textstycke(typ="analys", text=text, referenser=refs)


def sarbarhetsstycke(regelbas: Regelbas, profil: Profil, tjanst: str, id: str) -> Textstycke:
    profil = kompatibilitetsvy(profil, regelbas)
    s = regelbas.sarbarheter[id]
    villkor = tolka_villkor(s.villkor, regelbas.faltdefinitioner())
    utfall = utvardera(villkor, profil.faltvarden())
    status = {Sanning.SANT: "uppfyllt", Sanning.FALSKT: "inte uppfyllt", Sanning.OKANT: "okänt"}[utfall.sanning]
    text = (f"{s.namn} ({regelbas.tjanster[tjanst].namn}): Sårbarheten gäller om {villkorstext(s.villkor, regelbas)}. "
            f"Villkoret är {status}. ")
    refs = [tjanst, id, *sorted(falt_i(villkor))]
    meningar = [gransmening(regelbas, profil, g) for g in under_grans(profil, s.villkor)]
    meningar += [_belagg(regelbas, profil, ref) for ref in sorted(falt_i(villkor))]
    text += " ".join(meningar)
    if s.beskrivning:
        text += f" Betydelse för tjänsten: {s.beskrivning} {s.metodmotivering}"
    if utfall.sanning is Sanning.OKANT:
        text += f" Komplettera underlaget innan sårbarheten kan bedömas. {VERIFIERA}"
    if s.omrade == "geo":
        text += " Villkoret prövar denna faktor och utesluter inte andra geografiska risker, inklusive risker inom Sverige."
        slug = regelbas.tjanster[tjanst].erbjuds_falt.removesuffix("_erbjuds")
        for ref in ("P-BESK.geografi", slug + "_geografi"):
            if ref in regelbas.falt:
                refs.append(ref)
                text += " " + _belagg(regelbas, profil, ref)
    return Textstycke(typ="analys", text=text, referenser=refs)
