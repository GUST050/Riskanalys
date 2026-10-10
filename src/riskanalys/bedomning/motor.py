"""Deterministisk riskmotor (spec 7). Samma regelbas och profil ger alltid samma resultat."""

from riskanalys.bedomning.modeller import Bedomning, Kontrollbedomning, Riskdel, Tjanstbedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Konsekvens, Kontroll, MatrisRad, Regelbas, Risk, Sannolikhet, Sarbarhet, Tjanst
from riskanalys.regelverk.urval import Urval
from riskanalys.regelverk.villkor import Faltvarde, Kunskap, Sanning, Utfall, tolka_villkor, utvardera

SANNOLIKHETER: tuple[Sannolikhet, ...] = ("låg", "medel", "hög")
RISKNIVAER: tuple[Risk, ...] = ("låg", "måttlig", "hög", "mycket hög")
TF_KONSEKVENS: Konsekvens = "allvarlig"
PENNINGTVATT = frozenset({"penningtvatt", "bada"})
TERRORFINANSIERING = frozenset({"terrorfinansiering", "bada"})
_OKAND = Faltvarde(Kunskap.OKAND)


def steg(niva: str, antal: int, skala: tuple[str, ...]) -> str:
    """Flyttar en nivå i skalan, som lägst till första och som högst till sista nivån."""
    index = min(max(skala.index(niva) + antal, 0), len(skala) - 1)
    return skala[index]


def bedom(regelbas: Regelbas, urval: Urval, profil: Profil) -> Bedomning:
    tjanster = tuple(bedom_tjanst(regelbas, regelbas.tjanster[tjanst_id], profil) for tjanst_id in urval.tjanster)
    preliminar = any(tjanst.status == "preliminär" for tjanst in tjanster)
    return Bedomning(
        byra=profil.byra.id,
        regelpaket=urval.regelpaket.id,
        datum=urval.datum,
        lan=urval.lan,
        regelbas_version=regelbas.version,
        regelbas_kontrollsumma=regelbas.kontrollsumma,
        status="preliminär" if preliminar else "slutlig",
        tjanster=tjanster,
    )


def bedom_tjanst(regelbas: Regelbas, tjanst: Tjanst, profil: Profil) -> Tjanstbedomning:
    varden = profil.faltvarden()
    erbjuds = varden.get(tjanst.erbjuds_falt, _OKAND)
    if erbjuds.kunskap is Kunskap.EJ_TILLAMPLIG or (erbjuds.kunskap is Kunskap.KAND and erbjuds.varde is False):
        return _erbjuds_inte(tjanst)
    okant_erbjudande = frozenset({tjanst.erbjuds_falt}) if erbjuds.kunskap is Kunskap.OKAND else frozenset()
    sarbarheter, okanda_sarbarheter = _tillampade_sarbarheter(regelbas, tjanst, varden)
    kontroller, okanda_kontroller = _kontroller(regelbas, tjanst, varden)
    hojning = _hojning(sarbarheter, PENNINGTVATT)
    inneboende, rad = _riskdel(regelbas, tjanst.grund_sannolikhet, tjanst.grund_konsekvens, hojning)
    tf_hojning = _hojning(sarbarheter, TERRORFINANSIERING)
    terrorfinansiering, tf_rad = _riskdel(regelbas, tjanst.grund_tf_sannolikhet, TF_KONSEKVENS, tf_hojning)
    kvarstaende, kvar_regel = _kvarstaende(regelbas, inneboende.risk, kontroller)
    okanda = okant_erbjudande | okanda_sarbarheter | okanda_kontroller
    metod = regelbas.metod
    return Tjanstbedomning(
        tjanst=tjanst.id,
        erbjuds=None if okant_erbjudande else True,
        status="preliminär" if okanda else "slutlig",
        hot=tjanst.hot,
        tillampade_sarbarheter=tuple(sarbarhet.id for sarbarhet in sarbarheter),
        inneboende=inneboende,
        terrorfinansiering=terrorfinansiering,
        kontroller=kontroller,
        kvarstaende=kvarstaende,
        regelspar=(metod.sannolikhet.id, metod.konsekvens.id, rad.id, metod.terrorfinansiering.id, tf_rad.id, kvar_regel),
        okanda_uppgifter=tuple(sorted(okanda)),
    )


def _erbjuds_inte(tjanst: Tjanst) -> Tjanstbedomning:
    return Tjanstbedomning(
        tjanst=tjanst.id,
        erbjuds=False,
        status="slutlig",
        hot=(),
        tillampade_sarbarheter=(),
        inneboende=None,
        terrorfinansiering=None,
        kontroller=(),
        kvarstaende=None,
        regelspar=(),
        okanda_uppgifter=(),
    )


def _tillampade_sarbarheter(
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde]
) -> tuple[tuple[Sarbarhet, ...], frozenset[str]]:
    definitioner = regelbas.faltdefinitioner()
    utfall = [
        (sarbarhet, utvardera(tolka_villkor(sarbarhet.villkor, definitioner), varden))
        for sarbarhet in (regelbas.sarbarheter[sarbarhet_id] for sarbarhet_id in tjanst.sarbarheter)
    ]
    tillampade = tuple(sarbarhet for sarbarhet, resultat in utfall if _galler(sarbarhet, resultat))
    okanda = frozenset().union(*(resultat.okanda for _, resultat in utfall))
    return tillampade, okanda


def _galler(sarbarhet: Sarbarhet, utfall: Utfall) -> bool:
    if utfall.sanning is Sanning.OKANT:
        return sarbarhet.vid_okant == "preliminart_galler"
    return utfall.sanning is Sanning.SANT


def _hojning(sarbarheter: tuple[Sarbarhet, ...], galler: frozenset[str]) -> int:
    return sum(sarbarhet.effekt.sannolikhet for sarbarhet in sarbarheter if sarbarhet.galler in galler)


def _riskdel(regelbas: Regelbas, grund: str, konsekvens: str, hojning: int) -> tuple[Riskdel, MatrisRad]:
    sannolikhet = steg(grund, hojning, SANNOLIKHETER)
    rad = next(
        rad
        for rad in regelbas.metod.riskmatris
        if rad.sannolikhet == sannolikhet and rad.konsekvens == konsekvens
    )
    return Riskdel(sannolikhet=sannolikhet, konsekvens=konsekvens, risk=rad.risk), rad


def _kontroller(
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde]
) -> tuple[tuple[Kontrollbedomning, ...], frozenset[str]]:
    resultat = [_kontroll(regelbas.kontroller[kontroll_id], varden) for kontroll_id in tjanst.kontroller]
    return tuple(bedomning for bedomning, _ in resultat), frozenset().union(*(okanda for _, okanda in resultat))


def _kontroll(kontroll: Kontroll, varden: dict[str, Faltvarde]) -> tuple[Kontrollbedomning, frozenset[str]]:
    utformning = varden.get(kontroll.utformning_falt, _OKAND)
    genomforande = varden.get(kontroll.genomforande_falt, _OKAND)
    okanda = frozenset(
        falt_id
        for falt_id, varde in ((kontroll.utformning_falt, utformning), (kontroll.genomforande_falt, genomforande))
        if varde.kunskap is Kunskap.OKAND
    )
    bedomning = Kontrollbedomning(
        id=kontroll.id,
        utformning=_kant(utformning),
        genomforande=_kant(genomforande),
        fungerar_och_ar_belagd=_kant(utformning) == "finns" and _kant(genomforande) == "belagt",
    )
    return bedomning, okanda


def _kant(varde: Faltvarde) -> str | None:
    return varde.varde if varde.kunskap is Kunskap.KAND else None


def _kvarstaende(regelbas: Regelbas, risk: str, kontroller: tuple[Kontrollbedomning, ...]) -> tuple[str, str]:
    if any(kontroll.fungerar_och_ar_belagd for kontroll in kontroller):
        return steg(risk, -1, RISKNIVAER), regelbas.metod.kvarstaende_sankning.id
    return risk, regelbas.metod.kvarstaende_ej_belagd.id
