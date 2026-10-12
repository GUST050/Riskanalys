"""Sammanställer den allmänna riskbedömningen (spec 11). Bara riskavsnitten är skrivna av AI."""

from riskanalys.bedomning.modeller import Bedomning, Tjanstbedomning
from riskanalys.dokument.modeller import Avsnitt, AvsnittsUtkast, Dokument, Textstycke
from riskanalys.dokument.nivatext import nivastycken, sektorsmening
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
    if regelbas.metod.omfattning:
        return _bygg_tjanstvis(regelbas, profil, bedomning, utkast, historik)
    dokument = Dokument(
        id=DOKUMENT_ID,
        titel=TITEL,
        avsnitt=(
            _syfte(regelbas, profil, bedomning),
            *((_metod(regelbas, bedomning),) if regelbas.utokade_krav else ()),
            _tjanster(regelbas, bedomning),
            _hot(regelbas, erbjudna, profil),
            _sarbarheter(regelbas, profil, erbjudna),
            *_riskavsnitt(regelbas, bedomning, utkast),
            _utvardering(historik),
        ),
    )

    from riskanalys.dokument.intagsunderlag import med_intagsunderlag
    return med_intagsunderlag(dokument, regelbas, profil, bedomning)


def _bygg_tjanstvis(rb, profil, bedomning, utkast, historik):
    from riskanalys.dokument.delskrivning import Tjanstresultat
    from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3, bygg_tjanstavsnitt, kontrollstycken, slutsatsstycken
    from riskanalys.dokument.uppfoljning import omfattningsstycke, bevakningsavsnitt, uppfoljningsstycken
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    erbjudna = [t for t in bedomning.tjanster if t.inneboende]
    metod = _metod(rb, bedomning)
    metod = metod.model_copy(update={'stycken': (*metod.stycken, omfattningsstycke(rb, profil, bedomning))})
    hotkallor = sorted({k for t in erbjudna for h in t.hot for k in rb.hot[h].kallor})
    hot = Avsnitt(id='D-ARB.4', rubrik='Myndighetsunderlag och egna erfarenheter', kalla='regelbas', stycken=(
        _stycke('beskrivning', 'Varje tjänsts hotanalys nedan förenar myndigheternas tillvägagångssätt med byråns egen rapportering och erfarenhet. Källunderlag: '+
                '; '.join(f'{rb.kallor[k].titel} ({k})' for k in hotkallor)+'. Källversioner och profilbelägg redovisas i underlagsbilagan.',hotkallor),))
    sarb = Avsnitt(id='D-ARB.5',rubrik='Riskförhållanden och begränsningar',kalla='regelbas',stycken=(
        _stycke('analys','Kundförhållanden, leveranssätt, geografi och organisation prövas och motiveras per tjänst nedan. Byråövergripande indikatorer fördelas konservativt enligt ogranskad metod; de visar inte att varje kund i tjänsten har förhållandet. Ett nej till ett enskilt villkor utesluter inte andra risker. Okända uppgifter ska kompletteras.',[]),))
    kontroller = Avsnitt(id='D-ARB.7',rubrik='Kontroller, utfall och bedömd effekt',kalla='regelbas',
                        stycken=tuple(s for t in erbjudna for s in kontrollstycken(rb,profil,t)))
    risk = tuple(bygg_tjanstavsnitt_v3(rb,profil,t,utkast[id],id) if isinstance(utkast[id],Tjanstresultat) else bygg_tjanstavsnitt(rb,profil,t,utkast[id],id,utokad=bedomning.proportionalitet.niva=='utökad')
                 for id,t in tjanster_med_avsnitt(bedomning) if id in utkast)
    samman = Avsnitt(id='D-ARB.8',rubrik='Tjänstevis risksammanställning',kalla='regelbas',stycken=tuple(
        _stycke('beskrivning',f'{rb.tjanster[t.tjanst].namn}: inneboende penningtvättsrisk {t.inneboende.risk}, kvarstående {t.kvarstaende}; terrorfinansiering {t.terrorfinansiering.risk}. Riskerna redovisas per tjänst; ingen sammanvägd byrånivå beräknas.',[t.tjanst,*t.regelspar]) for t in erbjudna))
    slutsats = Avsnitt(id='D-ARB.9',rubrik='Följder för rutiner, kundkännedom, övervakning och utbildning',kalla='regelbas',
                       stycken=tuple(s for t in erbjudna for s in slutsatsstycken(rb,t)))
    uppfoljning = _utvardering(historik)
    uppfoljning = uppfoljning.model_copy(update={'stycken':(*uppfoljning.stycken,*uppfoljningsstycken(rb,profil))})
    return Dokument(id=DOKUMENT_ID,titel=TITEL,avsnitt=(
        _syfte(rb,profil,bedomning),metod,_tjanster(rb,bedomning),hot,sarb,kontroller,*risk,samman,slutsats,
        uppfoljning,bevakningsavsnitt(rb,profil),bygg_underlagsbilaga(rb,profil)))

def _stycke(typ: str, text: str, referenser: list[str]) -> Textstycke:
    return Textstycke(typ=typ, text=text, referenser=referenser)


def _varde(regelbas: Regelbas, profil: Profil, falt_id: str) -> str:
    if not profil.ar_bekraftad(falt_id):
        return VERIFIERA
    return visa_varde(regelbas.falt[falt_id], profil.uppgifter[falt_id].varde)


def _syfte(regelbas: Regelbas, profil: Profil, bedomning: Bedomning) -> Avsnitt:
    paket = regelbas.regelpaket[bedomning.regelpaket]
    roll = ROLL_FFR if profil.ar_bekraftad(FALT_FFR) else VERIFIERA
    ansvarstext = f"Funktionen för regelefterlevnad utövas av {roll}. Funktionen ansvarar för att riskbedömningen utvärderas och hålls aktuell."
    if regelbas.utokade_krav:
        special = profil.uppgifter.get("P-ORG.sarskilda_funktioner")
        ffr = profil.uppgifter.get(FALT_FFR)
        if (special and special.status == "bekräftad" and special.varde is True) or (ffr and ffr.status == "ej_tillämplig"):
            roll = "{roll:Ansvarsfunktion}" if profil.ar_bekraftad("P-ROLL.ansvarsfunktion") else VERIFIERA
            motiv = ffr.motivering if ffr and ffr.status == "ej_tillämplig" else "Särskilda funktioner har dokumenterats."
            ansvarstext = f"Dokumenterad ansvarsfunktion: {roll}. Ansvarsfördelning: {motiv}. Den rättsliga lämpligheten ska sakgranskas."

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
            ansvarstext,
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


def _hot(regelbas: Regelbas, erbjudna: list[Tjanstbedomning], profil: Profil) -> Avsnitt:
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
    from riskanalys.dokument.analysunderlag import erfarenhetsstycke
    egna = tuple(erfarenhetsstycke(regelbas, profil, t) for t in erbjudna if t.egen_erfarenhet is not None)
    return Avsnitt(id="D-ARB.4", rubrik="Hot", kalla="regelbas", stycken=(*stycken, *egna))


def _sarbarheter(regelbas: Regelbas, profil: Profil, erbjudna: list[Tjanstbedomning]) -> Avsnitt:
    from riskanalys.dokument.analysunderlag import sarbarhetsstycke
    # Bevara den frysta M1-kedjans historiska dokumentformat.
    if not regelbas.utokade_krav:
        definitioner = regelbas.faltdefinitioner()
        stycken = tuple(
            _stycke(
                "analys",
                f"{s.namn} ({regelbas.tjanster[t.tjanst].namn}): {_SARBARHETSTEXT[sarbarhet_status(regelbas, profil, s.id)]}",
                [s.id, *sorted(falt_i(tolka_villkor(s.villkor, definitioner)))],
            )
            for t in erbjudna
            for s in (regelbas.sarbarheter[id] for id in regelbas.tjanster[t.tjanst].sarbarheter)
        )
        return Avsnitt(id="D-ARB.5", rubrik="Sårbarheter", kalla="regelbas", stycken=stycken)
    stycken = tuple(
        sarbarhetsstycke(regelbas, profil, tjanst.tjanst, sarbarhet.id)
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
            stycken=(*nivastycken(tjanst), *utkast[avsnitt_id].stycken),
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


def _metod(regelbas: Regelbas, bedomning: Bedomning) -> Avsnitt:
    text = "Metoden skiljer inneboende risk före åtgärder från kvarstående risk efter belagda kontroller. Penningtvätt, terrorfinansiering och sanktionsrisk beräknas separat. Grundnivåer, kombinationer och skalor är metodval som kräver sakkunniggranskning. "
    if bedomning.omfattning:
        text += f"Rättslig omfattning: punkter {bedomning.omfattning.punkter}; status {bedomning.omfattning.status}. "
        text += " ".join(bedomning.omfattning.hinder)
    stycken = [_stycke("beskrivning", text, [])]
    for t in bedomning.tjanster:
        if t.inneboende is None:
            continue
        ref = regelbas.sektorsreferenser.get(regelbas.tjanster[t.tjanst].sektorreferens)
        stycken.append(_stycke("beskrivning", _tjanstens_metodtext(regelbas, t, ref), [t.tjanst]))
    return Avsnitt(id="D-ARB.2", rubrik="Metod, omfattning och referensrisk", kalla="regelbas", stycken=tuple(stycken))


def _tjanstens_metodtext(regelbas: Regelbas, t: Tjanstbedomning, ref) -> str:
    # Den frysta M1-kedjan behåller sitt historiska dokumentformat; klartext gäller från utökade krav (spec 8.4.9).
    namn = regelbas.tjanster[t.tjanst].namn if regelbas.utokade_krav else t.tjanst
    text = f"{namn}: penningtvätt {t.inneboende.risk}, kvarstående {t.kvarstaende}; terrorfinansiering {t.terrorfinansiering.risk}. "
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        text += f"Sanktionsrisk {t.sanktionsrisk.inneboende.risk}, kvarstående {t.sanktionsrisk.kvarstaende}. "
    if not ref:
        return text
    if regelbas.utokade_krav:
        return text + sektorsmening(regelbas, ref)
    return text + f"Sektorsreferens {ref.id}: {ref.niva} på källans skala {ref.skala}, {ref.kalla}, sida {ref.sida}, version {ref.referensversion}. Källans skala är separat från byråns motor."
