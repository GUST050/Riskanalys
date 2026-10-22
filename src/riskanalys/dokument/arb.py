"""Sammanställer den allmänna riskbedömningen (spec 11). Bara riskavsnitten är skrivna av AI."""

from riskanalys.regelverk.granser import metodgransindex

from riskanalys.bedomning.modeller import Bedomning, Tjanstbedomning
from riskanalys.dokument.klartext import id_till_namn, kanda_id, kod_till_namn, paketnamn, punkttext
from riskanalys.dokument.modeller import Avsnitt, AvsnittsUtkast, Dokument, Textstycke
from riskanalys.dokument.nivatext import nivastycken, sektorsmening
from riskanalys.dokument.underlag import sarbarhet_status, tjanster_med_avsnitt
from riskanalys.dokument.validering import VERIFIERA
from riskanalys.drift.historik import Historik
from riskanalys.profil.hantering import visa_varde
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas, Sektorsreferens
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
    *,
    gransindex: dict[str, tuple[float, ...]] | None = None,
    analys=None,
    modellrapport=None,
    formatversion=None,
) -> Dokument:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
    from riskanalys.dokument.rapportversion import V9
    from riskanalys.dokument import rapportversion
    if formatversion == V9 or (formatversion is None and rapportversion.AKTUELL_DOKUMENTVERSION == V9
                              and regelbas.metod.omfattning):
        from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
        return bygg_resultatpaket_v9(regelbas,profil,bedomning,utkast,historik,analys=analys,
                                    gransindex=gransindex,modellrapport=modellrapport).dokument
    from riskanalys.dokument.skrivversion import V8
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION
    if formatversion == V8 or (formatversion is None and
            (any(getattr(r, 'formatversion', None) == V8 for r in utkast.values())
             or (not utkast and regelbas.metod.omfattning and AKTUELL_DOKUMENTVERSION == V8))):
        from riskanalys.dokument.arb_v8 import bygg_arb_v8
        return bygg_arb_v8(regelbas, profil, bedomning, utkast, historik, analys=analys, gransindex=gransindex, modellrapport=modellrapport)
    if regelbas.metod.omfattning:
        from riskanalys.dokument.arb_v6 import bygg_arb_v6
        return bygg_arb_v6(regelbas, profil, bedomning, utkast, historik, analys=analys, gransindex=gransindex, modellrapport=modellrapport, formatversion=formatversion)
    erbjudna = [tjanst for tjanst in bedomning.tjanster if tjanst.inneboende is not None]
    dokument = Dokument(
        id=DOKUMENT_ID,
        titel=TITEL,
        avsnitt=(
            _syfte(regelbas, profil, bedomning),
            *((_metod(regelbas, bedomning),) if regelbas.utokade_krav else ()),
            _tjanster(regelbas, bedomning),
            _hot(regelbas, erbjudna, profil, gransindex=gransindex),
            _sarbarheter(regelbas, profil, erbjudna, gransindex=gransindex),
            *_riskavsnitt(regelbas, bedomning, utkast),
            _utvardering(historik),
        ),
    )

    from riskanalys.dokument.intagsunderlag import med_intagsunderlag
    return med_intagsunderlag(dokument, regelbas, profil, bedomning)


def _stycke(typ: str, text: str, referenser: list[str]) -> Textstycke:
    return Textstycke(typ=typ, text=text, referenser=referenser)


def _varde(regelbas: Regelbas, profil: Profil, falt_id: str) -> str:
    if not profil.ar_bekraftad(falt_id):
        return VERIFIERA
    return visa_varde(regelbas.falt[falt_id], profil.uppgifter[falt_id].varde)


def _syfte(regelbas: Regelbas, profil: Profil, bedomning: Bedomning, *, bevara_original: bool = False) -> Avsnitt:
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

    stycken = [
        _stycke(
            "beskrivning",
            f"Den här allmänna riskbedömningen gäller {_varde(regelbas, profil, FALT_NAMN)}. "
            f"Antal personer i verksamheten, inklusive ägare: {_varde(regelbas, profil, FALT_ANSTALLDA)}. "
            f"Antal verksamhetsställen: {_varde(regelbas, profil, FALT_VERKSAMHETSSTALLEN)}.",
            [FALT_NAMN, FALT_ANSTALLDA, FALT_VERKSAMHETSSTALLEN],
        ),
        _stycke(
            "beskrivning",
            f"Bedömningen följer regelpaketet {paketnamn(paket)} för {bedomning.lan} och gäller regelverket per "
            f"{bedomning.datum.isoformat()}. Den bygger på regelbas version {bedomning.regelbas_version}.",
            [],
        ),
        _stycke(
            "beskrivning",
            ansvarstext,
            [FALT_FFR],
        ),
    ]
    if bevara_original:
        from riskanalys.dokument.profiloriginal_v8 import spann_for_original, ansvarsmotiveringsspann
        uppgifter=profil.uppgifter
        for falt_id in (FALT_NAMN,FALT_ANSTALLDA,FALT_VERKSAMHETSSTALLEN):
            u=uppgifter.get(falt_id)
            if u and u.status=='bekräftad' and not u.inaktuell and isinstance(u.varde,str):
                stycken[0]=stycken[0].model_copy(update={'literala_spann':(*stycken[0].literala_spann,
                    *spann_for_original(stycken[0].text,u.varde))})
        ffr=uppgifter.get(FALT_FFR)
        if ffr and ffr.status=='ej_tillämplig' and ffr.motivering:
            ansvar = ('{roll:Ansvarsfunktion}' if profil.ar_bekraftad('P-ROLL.ansvarsfunktion') else VERIFIERA)
            spann = ansvarsmotiveringsspann(stycken[2].text, ansvar, ffr.motivering)
            stycken[2]=stycken[2].model_copy(update={'literala_spann':spann})
    return Avsnitt(id="D-ARB.1", rubrik="Syfte, omfattning och ansvar", kalla="regelbas", stycken=tuple(stycken))


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


def _hot(regelbas: Regelbas, erbjudna: list[Tjanstbedomning], profil: Profil, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> Avsnitt:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
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
    egna = tuple(erfarenhetsstycke(regelbas, profil, t, gransindex=gransindex) for t in erbjudna if t.egen_erfarenhet is not None)
    return Avsnitt(id="D-ARB.4", rubrik="Hot", kalla="regelbas", stycken=(*stycken, *egna))


def _sarbarheter(regelbas: Regelbas, profil: Profil, erbjudna: list[Tjanstbedomning], *, gransindex: dict[str, tuple[float, ...]] | None = None) -> Avsnitt:
    if gransindex is None:
        gransindex = metodgransindex(regelbas)
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
        sarbarhetsstycke(regelbas, profil, tjanst.tjanst, sarbarhet.id, gransindex=gransindex)
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
    referenser: tuple[str, ...] = ()
    if bedomning.omfattning:
        hinder = " ".join(bedomning.omfattning.hinder)
        text += f"Rättslig omfattning: {punkttext(bedomning.omfattning.punkter)}; status {bedomning.omfattning.status}. "
        text += kod_till_namn(regelbas, id_till_namn(regelbas, hinder))
        referenser = kanda_id(regelbas, hinder)
    stycken = [_stycke("beskrivning", text, list(referenser))]
    for t in bedomning.tjanster:
        if t.inneboende is None:
            continue
        ref = regelbas.sektorsreferenser.get(regelbas.tjanster[t.tjanst].sektorreferens)
        refs = [t.tjanst, ref.id, ref.kalla] if ref else [t.tjanst]
        stycken.append(_stycke("beskrivning", _tjanstens_metodtext(regelbas, t, ref), refs))
    return Avsnitt(id="D-ARB.2", rubrik="Metod, omfattning och referensrisk", kalla="regelbas", stycken=tuple(stycken))


def _tjanstens_metodtext(regelbas: Regelbas, t: Tjanstbedomning, ref: Sektorsreferens | None) -> str:
    text = f"{regelbas.tjanster[t.tjanst].namn}: penningtvätt {t.inneboende.risk}, kvarstående {t.kvarstaende}; terrorfinansiering {t.terrorfinansiering.risk}. "
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        text += f"Sanktionsrisk {t.sanktionsrisk.inneboende.risk}, kvarstående {t.sanktionsrisk.kvarstaende}. "
    return (text + sektorsmening(regelbas, ref)) if ref else text
