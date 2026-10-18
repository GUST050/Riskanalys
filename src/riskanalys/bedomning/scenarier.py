"""Scenarioberäkning (spec 2026-10-18, Modellen steg 1–6): en nivå per tjänst × hot och dimension.

Hotnivå och de sårbarheter som möjliggör hotet ger sannolikheten. Kontroller sänker bara de hot de enligt
katalogen riktar sig mot. Tjänstens nivå är det högsta scenariot; alla scenarier på maxnivån är avgörande.
"""

from riskanalys.bedomning.modeller import Kontrollbedomning, Riskdel, Scenariobedomning
from riskanalys.bedomning.motor import (
    PENNINGTVATT,
    RISKNIVAER,
    SANNOLIKHETER,
    TERRORFINANSIERING,
    TF_KONSEKVENS,
    _riskdel,
    _utan_ersatta,
    _valda_sarbarheter,
    steg,
)
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import (
    Hot,
    Regelbas,
    Risk,
    Sannolikhetsrad,
    Sarbarhet,
    Tjanst,
    hot_dimensioner,
)
from riskanalys.regelverk.villkor import Faltvarde, Kunskap

IAKTTAGET_SUFFIX = "_iakttagna_hot"
TJANSTPREFIX = "P-TJ."
ERBJUDS_SUFFIX = "_erbjuds"
DIMENSIONER = ("pt", "tf")
OMRADEN = {"pt": PENNINGTVATT, "tf": TERRORFINANSIERING}
IAKTTAGELSEHOJNING = 1
KONTROLLSANKNING = -1


def iakttagelsefalt(tjanst: Tjanst) -> str:
    """Det lokala flervalsfältet för hot som byrån iakttagit i tjänsten: P-TJ.{slug}_iakttagna_hot."""
    slug = tjanst.erbjuds_falt.removeprefix(TJANSTPREFIX).removesuffix(ERBJUDS_SUFFIX)
    return f"{TJANSTPREFIX}{slug}{IAKTTAGET_SUFFIX}"


def iakttagna_hot(tjanst: Tjanst, varden: dict[str, Faltvarde], okanda: frozenset[str]) -> frozenset[str]:
    """Kända iakttagna hot i tjänsten. Saknat, okänt eller ogiltigt svar ger inga hot och inget fel."""
    falt_id = iakttagelsefalt(tjanst)
    varde = varden.get(falt_id)
    if falt_id in okanda or varde is None or varde.kunskap is not Kunskap.KAND:
        return frozenset()
    if not isinstance(varde.varde, (list, tuple)):
        return frozenset()
    return frozenset(hot for hot in varde.varde if isinstance(hot, str)) & frozenset(tjanst.hot)


def bedom_scenarier(
    regelbas: Regelbas,
    tjanst: Tjanst,
    varden: dict[str, Faltvarde],
    kontroller: tuple[Kontrollbedomning, ...],
    okanda: frozenset[str],
) -> tuple[Scenariobedomning, ...]:
    """Ett PT-scenario per hot med dimensionen pt, därefter ett TF-scenario per hot med tf, i tjänstens ordning.

    `okanda` är de fält som motorn redan bedömt som okända; ett okänt iakttagelsefält höjer inte.
    """
    if regelbas.metod.scenario is None:
        return ()
    sarbarheter, _ = _valda_sarbarheter(regelbas, tjanst, varden)
    _kontrollera_hotkopplingar(sarbarheter)
    iakttagna = iakttagna_hot(tjanst, varden, okanda)
    scenarier = tuple(
        _scenario(regelbas, tjanst, regelbas.hot[hot_id], dimension, sarbarheter, kontroller, iakttagna)
        for dimension in DIMENSIONER
        for hot_id in tjanst.hot
        if dimension in hot_dimensioner(regelbas.hot[hot_id])
    )
    return _markera_avgorande(scenarier)


def sammanfatta_scenarier(
    scenarier: tuple[Scenariobedomning, ...],
) -> tuple[Riskdel | None, Riskdel | None, Risk | None]:
    """Tjänstens PT inneboende, TF och PT kvarstående risk: högsta scenariot per dimension."""
    pt = tuple(s for s in scenarier if s.dimension == "pt")
    tf = tuple(s for s in scenarier if s.dimension == "tf")
    kvarstaende = max((s.kvarstaende for s in pt if s.kvarstaende), key=RISKNIVAER.index, default=None)
    return _hogsta(pt), _hogsta(tf), kvarstaende


def scenarioregelspar(regelbas: Regelbas, scenarier: tuple[Scenariobedomning, ...]) -> tuple[str, ...]:
    """Scenariometodens regler och använda matrisrader, i första användningens ordning, och aggregeringen."""
    anvanda = dict.fromkeys(regel for scenario in scenarier for regel in scenario.regelspar)
    return (*anvanda, regelbas.metod.scenario.aggregering.id)


def _hogsta(scenarier: tuple[Scenariobedomning, ...]) -> Riskdel | None:
    """Högst risk, vid lika högst sannolikhet, därefter första i katalogordning (max behåller första)."""
    if not scenarier:
        return None
    basta = max(scenarier, key=lambda s: (RISKNIVAER.index(s.risk), SANNOLIKHETER.index(s.sannolikhet)))
    return Riskdel(sannolikhet=basta.sannolikhet, konsekvens=basta.konsekvens, risk=basta.risk)


def _markera_avgorande(scenarier: tuple[Scenariobedomning, ...]) -> tuple[Scenariobedomning, ...]:
    maxrisk = {
        dimension: max(RISKNIVAER.index(s.risk) for s in scenarier if s.dimension == dimension)
        for dimension in {s.dimension for s in scenarier}
    }
    return tuple(
        s.model_copy(update={"avgorande": RISKNIVAER.index(s.risk) == maxrisk[s.dimension]}) for s in scenarier
    )


def _scenario(
    regelbas: Regelbas,
    tjanst: Tjanst,
    hot: Hot,
    dimension: str,
    sarbarheter: tuple[Sarbarhet, ...],
    kontroller: tuple[Kontrollbedomning, ...],
    iakttagna: frozenset[str],
) -> Scenariobedomning:
    metod = regelbas.metod
    ar_pt = dimension == "pt"
    iakttaget = hot.id in iakttagna
    hotniva = steg(_hotniva(hot), IAKTTAGELSEHOJNING if iakttaget else 0, SANNOLIKHETER)
    mojliggorande = _mojliggorande(sarbarheter, hot, dimension)
    bas = tjanst.grund_sannolikhet if ar_pt else tjanst.grund_tf_sannolikhet
    sarbarhetsniva = steg(bas, sum(s.effekt.sannolikhet for s in mojliggorande), SANNOLIKHETER)
    sannolikhetsrad = _sannolikhetsrad(regelbas, hotniva, sarbarhetsniva)
    konsekvens = tjanst.grund_konsekvens if ar_pt else TF_KONSEKVENS
    riskdel, riskrad = _riskdel(regelbas, sannolikhetsrad.sannolikhet, konsekvens, 0)
    tackande = _tackande_kontroller(regelbas, tjanst, hot, kontroller) if ar_pt else ()
    kvarstaende, kvar_regel = _kvarstaende(regelbas, riskdel.risk, tackande) if ar_pt else (None, ())
    konsekvensregel = metod.konsekvens.id if ar_pt else metod.terrorfinansiering.id
    return Scenariobedomning(
        hot=hot.id,
        dimension=dimension,
        hotniva=hotniva,
        iakttaget=iakttaget,
        sarbarheter=tuple(s.id for s in mojliggorande),
        sarbarhetsniva=sarbarhetsniva,
        sannolikhet=riskdel.sannolikhet,
        konsekvens=konsekvens,
        risk=riskdel.risk,
        tackande_kontroller=tackande,
        kvarstaende=kvarstaende,
        avgorande=False,
        regelspar=(metod.scenario.hotniva.id, metod.scenario.sarbarhetsniva.id, sannolikhetsrad.id,
                   konsekvensregel, riskrad.id, *kvar_regel),
    )


def _mojliggorande(sarbarheter: tuple[Sarbarhet, ...], hot: Hot, dimension: str) -> tuple[Sarbarhet, ...]:
    """Valda sårbarheter som möjliggör hotet i dimensionen; ersättning (ersatter) gäller bara inom scenariot.

    En sårbarhet A som ersätter B tar bort B bara där A själv är vald, kopplad till hotet och omfattar dimensionen.
    """
    i_scenariot = tuple(s for s in sarbarheter if hot.id in s.hot and s.galler in OMRADEN[dimension])
    return _utan_ersatta(i_scenariot)


def _hotniva(hot: Hot) -> str:
    if hot.niva is None:
        raise RiskanalysFel(
            f"{hot.id}: hotet saknar hotnivå. Ange niva (låg, medel eller hög) med källa och nivamotivering "
            f"i kataloger/hot.yaml och validera regelbasen."
        )
    return hot.niva


def _kontrollera_hotkopplingar(sarbarheter: tuple[Sarbarhet, ...]) -> None:
    """En tillämpad sårbarhet utan hot skulle inte höja något scenario; det får aldrig ske tyst."""
    for sarbarhet in sarbarheter:
        if not sarbarhet.hot:
            raise RiskanalysFel(
                f"{sarbarhet.id}: sårbarheten saknar koppling till hot. Ange de hot den möjliggör i "
                f"kataloger/sarbarheter.yaml och validera regelbasen, annars kan risken sänkas tyst."
            )


def _sannolikhetsrad(regelbas: Regelbas, hotniva: str, sarbarhetsniva: str) -> Sannolikhetsrad:
    rad = next(
        (r for r in regelbas.metod.scenario.sannolikhetsmatris if r.hot == hotniva and r.sarbarhet == sarbarhetsniva),
        None,
    )
    if rad is None:
        raise RiskanalysFel(
            f"Sannolikhetsmatrisen saknar raden för hotnivå {hotniva} och sårbarhetsnivå {sarbarhetsniva}. "
            f"Rätta scenario.sannolikhetsmatris i beslutstabeller/metod.yaml och validera regelbasen."
        )
    return rad


def _tackande_kontroller(
    regelbas: Regelbas, tjanst: Tjanst, hot: Hot, kontroller: tuple[Kontrollbedomning, ...]
) -> tuple[str, ...]:
    """Kontroller med belagd utformning, genomförande och verksam effekt som enligt katalogen riktar sig mot hotet."""
    return tuple(
        kontroll.id
        for kontroll in kontroller
        if kontroll.fungerar_och_ar_belagd
        and kontroll.effekt_belagd is True
        and any(
            riktning.tjanst == tjanst.id and hot.id in riktning.hot
            for riktning in regelbas.kontroller[kontroll.id].riktar_sig_mot
        )
    )


def _kvarstaende(regelbas: Regelbas, risk: str, tackande: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    """Högst ett stegs sänkning, som lägst låg (BT-KVAR-03); annars lika med inneboende (BT-KVAR-01)."""
    if tackande:
        return steg(risk, KONTROLLSANKNING, RISKNIVAER), (regelbas.metod.scenario.kvarstaende.id,)
    return risk, (regelbas.metod.kvarstaende_ej_belagd.id,)
