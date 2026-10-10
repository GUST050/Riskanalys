"""Sammanställer den allmänna riskbedömningen (spec 11). Bara riskavsnitten är skrivna av AI."""

from riskanalys.bedomning.modeller import Bedomning, Tjanstbedomning
from riskanalys.dokument.modeller import Avsnitt, AvsnittsUtkast, Dokument, Textstycke
from riskanalys.dokument.underlag import sarbarhet_status, tjanster_med_avsnitt
from riskanalys.dokument.validering import VERIFIERA
from riskanalys.drift.historik import Historik
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import falt_i, tolka_villkor

DOKUMENT_ID = "D-ARB"
TITEL = "Allmän riskbedömning"
ROLL_FFR = "{roll:FfR}"
FALT_NAMN = "P-ORG.namn"
FALT_ANSTALLDA = "P-ORG.antal_anstallda"
FALT_VERKSAMHETSSTALLEN = "P-ORG.verksamhetsstallen"
FALT_FFR = "P-ROLL.ffr_namn"
_SARBARHETSTEXT = {
    "ja": "Gäller enligt byråns uppgifter.",
    "nej": "Gäller inte enligt byråns uppgifter.",
    "okänt": f"Okänt, eftersom uppgifter saknas. {VERIFIERA}",
}


def bygg_arb(
    regelbas: Regelbas,
    profil: Profil,
    bedomning: Bedomning,
    utkast: dict[str, AvsnittsUtkast],
    historik: Historik,
) -> Dokument:
    erbjudna = [tjanst for tjanst in bedomning.tjanster if tjanst.inneboende is not None]
    return Dokument(
        id=DOKUMENT_ID,
        titel=TITEL,
        avsnitt=(
            _syfte(regelbas, profil, bedomning),
            _tjanster(regelbas, bedomning),
            _hot(regelbas, erbjudna),
            _sarbarheter(regelbas, profil, erbjudna),
            *_riskavsnitt(regelbas, bedomning, utkast),
            _utvardering(historik),
        ),
    )


def _stycke(typ: str, text: str, referenser: list[str]) -> Textstycke:
    return Textstycke(typ=typ, text=text, referenser=referenser)


def _varde(regelbas: Regelbas, profil: Profil, falt_id: str) -> str:
    if not profil.ar_bekraftad(falt_id):
        return VERIFIERA
    return visa_varde(regelbas.falt[falt_id], profil.uppgifter[falt_id].varde)


def _syfte(regelbas: Regelbas, profil: Profil, bedomning: Bedomning) -> Avsnitt:
    paket = regelbas.regelpaket[bedomning.regelpaket]
    roll = ROLL_FFR if profil.ar_bekraftad(FALT_FFR) else VERIFIERA
    stycken = (
        _stycke(
            "beskrivning",
            f"Den här allmänna riskbedömningen gäller {_varde(regelbas, profil, FALT_NAMN)}. "
            f"Antal personer i verksamheten, inklusive ägare: {_varde(regelbas, profil, FALT_ANSTALLDA)}. "
            f"Antal verksamhetsställen: {_varde(regelbas, profil, FALT_VERKSAMHETSSTALLEN)}.",
            [FALT_NAMN, FALT_ANSTALLDA, FALT_VERKSAMHETSSTALLEN],
        ),
        _stycke(
            "beskrivning",
            f"Bedömningen följer regelpaketet {paket.namn} för {bedomning.lan} och gäller regelverket per "
            f"{bedomning.datum.isoformat()}. Den bygger på regelbas version {bedomning.regelbas_version}.",
            [],
        ),
        _stycke(
            "beskrivning",
            f"Funktionen för regelefterlevnad utövas av {roll}. Funktionen ansvarar för att riskbedömningen "
            "utvärderas och hålls aktuell.",
            [FALT_FFR],
        ),
    )
    return Avsnitt(id="D-ARB.1", rubrik="Syfte, omfattning och ansvar", kalla="regelbas", stycken=stycken)


def _tjanster(regelbas: Regelbas, bedomning: Bedomning) -> Avsnitt:
    stycken = tuple(_tjanststycke(regelbas, tjanst) for tjanst in bedomning.tjanster)
    return Avsnitt(id="D-ARB.3", rubrik="Byråns tjänster", kalla="regelbas", stycken=stycken)


def _tjanststycke(regelbas: Regelbas, tjanstbedomning: Tjanstbedomning) -> Textstycke:
    tjanst = regelbas.tjanster[tjanstbedomning.tjanst]
    if tjanstbedomning.erbjuds is False:
        text = f"{tjanst.namn}: erbjuds inte."
    elif tjanstbedomning.erbjuds is None:
        text = f"{tjanst.namn}: okänt om tjänsten erbjuds. {VERIFIERA}"
    else:
        text = f"{tjanst.namn}: erbjuds. {tjanst.beskrivning}"
    return _stycke("beskrivning", text, [tjanst.id, tjanst.erbjuds_falt])


def _hot(regelbas: Regelbas, erbjudna: list[Tjanstbedomning]) -> Avsnitt:
    stycken = tuple(
        _stycke(
            "analys",
            f"{hot.namn} ({regelbas.tjanster[tjanst.tjanst].namn}). {hot.beskrivning} "
            f"Källor: {', '.join(regelbas.kallor[kalla].titel for kalla in hot.kallor)}.",
            [hot.id, tjanst.tjanst, *hot.kallor],
        )
        for tjanst in erbjudna
        for hot in (regelbas.hot[hot_id] for hot_id in tjanst.hot)
    )
    return Avsnitt(id="D-ARB.4", rubrik="Hot", kalla="regelbas", stycken=stycken)


def _sarbarheter(regelbas: Regelbas, profil: Profil, erbjudna: list[Tjanstbedomning]) -> Avsnitt:
    definitioner = regelbas.faltdefinitioner()
    stycken = tuple(
        _stycke(
            "analys",
            f"{sarbarhet.namn} ({regelbas.tjanster[tjanst.tjanst].namn}): "
            f"{_SARBARHETSTEXT[sarbarhet_status(regelbas, profil, sarbarhet.id)]}",
            [sarbarhet.id, *sorted(falt_i(tolka_villkor(sarbarhet.villkor, definitioner)))],
        )
        for tjanst in erbjudna
        for sarbarhet in (regelbas.sarbarheter[sid] for sid in regelbas.tjanster[tjanst.tjanst].sarbarheter)
    )
    return Avsnitt(id="D-ARB.5", rubrik="Sårbarheter", kalla="regelbas", stycken=stycken)


def _riskavsnitt(regelbas: Regelbas, bedomning: Bedomning, utkast: dict[str, AvsnittsUtkast]) -> tuple[Avsnitt, ...]:
    return tuple(
        Avsnitt(
            id=avsnitt_id,
            rubrik=f"Risk i {regelbas.tjanster[tjanst.tjanst].namn.lower()}",
            kalla="ai",
            stycken=tuple(utkast[avsnitt_id].stycken),
        )
        for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning)
        if avsnitt_id in utkast
    )


def _utvardering(historik: Historik) -> Avsnitt:
    senaste, nasta = historik.senaste_utvardering(), historik.nasta_genomgang()
    if senaste is None or nasta is None:
        text = f"Datum för utvärdering saknas. {VERIFIERA}"
    else:
        text = (
            f"Riskbedömningen utvärderades senast {senaste.isoformat()}. Nästa utvärdering görs senast "
            f"{nasta.isoformat()}, och alltid innan byrån erbjuder nya eller väsentligt ändrade tjänster, riktar "
            "sig till nya marknader eller gör andra förändringar som är relevanta för verksamheten."
        )
    return Avsnitt(
        id="D-ARB.10",
        rubrik="Utvärdering och uppdatering",
        kalla="regelbas",
        stycken=(_stycke("beskrivning", text, []),),
    )
