"""Deterministisk riskmotor (spec 7). Samma regelbas och profil ger alltid samma resultat."""

from riskanalys.bedomning.modeller import Bedomning, Kontrollbedomning, Riskdel, Tjanstbedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Konsekvens, Kontroll, MatrisRad, Regelbas, Risk, Sannolikhet, Sarbarhet, Tjanst
from riskanalys.regelverk.urval import Urval
from riskanalys.regelverk.tillsyn import rattlig_omfattning
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
    from riskanalys.profil.omfattning import harled_andelar
    profil = harled_andelar(profil, regelbas)
    tjanster = tuple(bedom_tjanst(regelbas, regelbas.tjanster[tjanst_id], profil) for tjanst_id in urval.tjanster)
    omfattning = rattlig_omfattning(regelbas, profil) if regelbas.utokade_krav else None
    from riskanalys.bedomning.omfattning import bedom_omfattning
    proportionalitet = bedom_omfattning(regelbas, profil, tjanster)
    preliminar = bool(omfattning and omfattning.hinder) or any(tjanst.status == "preliminär" for tjanst in tjanster)
    preliminar |= bool(proportionalitet and proportionalitet.status == "preliminär")
    return Bedomning(
        byra=profil.byra.id,
        regelpaket=urval.regelpaket.id,
        datum=urval.datum,
        lan=urval.lan,
        regelbas_version=regelbas.version,
        regelbas_kontrollsumma=regelbas.kontrollsumma,
        status="preliminär" if preliminar else "slutlig",
        tjanster=tjanster,
        omfattning=omfattning,
        proportionalitet=proportionalitet,
    )


def bedom_tjanst(regelbas: Regelbas, tjanst: Tjanst, profil: Profil) -> Tjanstbedomning:
    from riskanalys.profil.omfattning import kompatibilitetsvy
    profil = kompatibilitetsvy(profil, regelbas)
    varden = profil.faltvarden()
    from riskanalys.bedomning.erfarenheter import belagd_uppgift
    for id in regelbas.falt:
        if id.startswith("P-RISK.") and not belagd_uppgift(regelbas, profil, id):
            varden[id] = _OKAND
    erbjuds = varden.get(tjanst.erbjuds_falt, _OKAND)
    if erbjuds.kunskap is Kunskap.EJ_TILLAMPLIG or (erbjuds.kunskap is Kunskap.KAND and erbjuds.varde is False):
        return _erbjuds_inte(tjanst)
    okant_erbjudande = frozenset({tjanst.erbjuds_falt}) if erbjuds.kunskap is Kunskap.OKAND else frozenset()
    sarbarheter, okanda_sarbarheter = _tillampade_sarbarheter(regelbas, tjanst, varden)
    kontroller, okanda_kontroller = _kontroller(regelbas, tjanst, varden, profil)
    okanda = okant_erbjudande | okanda_sarbarheter | okanda_kontroller
    if regelbas.metod.scenario is None:
        inneboende, terrorfinansiering, kvarstaende, regelspar = _aldre_nivaer(regelbas, tjanst, sarbarheter, kontroller)
        scenarier = ()
    else:
        from riskanalys.bedomning.scenarier import bedom_scenarier, sammanfatta_scenarier, scenarioregelspar
        scenarier = bedom_scenarier(regelbas, tjanst, varden, kontroller, okanda)
        inneboende, terrorfinansiering, kvarstaende = sammanfatta_scenarier(scenarier)
        regelspar = scenarioregelspar(regelbas, scenarier)
    from riskanalys.bedomning.sanktioner import bedom_sanktionsrisk
    sanktioner = bedom_sanktionsrisk(regelbas, tjanst, profil) if regelbas.utokade_krav else None
    if sanktioner:
        okanda |= frozenset(sanktioner.okanda_uppgifter)
    from riskanalys.bedomning.erfarenheter import bedom_egen_erfarenhet
    erfarenhet = bedom_egen_erfarenhet(regelbas, profil)
    if erfarenhet:
        okanda |= frozenset(erfarenhet.okanda_uppgifter)
    return Tjanstbedomning(
        tjanst=tjanst.id,
        egen_erfarenhet=erfarenhet,
        sanktionsrisk=sanktioner,
        erbjuds=None if okant_erbjudande else True,
        status="preliminär" if okanda else "slutlig",
        hot=tjanst.hot,
        tillampade_sarbarheter=tuple(sarbarhet.id for sarbarhet in sarbarheter),
        inneboende=inneboende,
        terrorfinansiering=terrorfinansiering,
        kontroller=kontroller,
        kvarstaende=kvarstaende,
        regelspar=regelspar,
        okanda_uppgifter=tuple(sorted(okanda)),
        scenarier=scenarier,
    )


def _aldre_nivaer(
    regelbas: Regelbas, tjanst: Tjanst, sarbarheter: tuple[Sarbarhet, ...], kontroller: tuple[Kontrollbedomning, ...]
) -> tuple[Riskdel, Riskdel, str, tuple[str, ...]]:
    """Metod 1 utan scenarier (BT-SANN-01, BT-TF-01, BT-KVAR-01/02), oförändrad för äldre regelbaser."""
    metod = regelbas.metod
    hojning = _hojning(sarbarheter, PENNINGTVATT)
    inneboende, rad = _riskdel(regelbas, tjanst.grund_sannolikhet, tjanst.grund_konsekvens, hojning)
    tf_hojning = _hojning(sarbarheter, TERRORFINANSIERING)
    terrorfinansiering, tf_rad = _riskdel(regelbas, tjanst.grund_tf_sannolikhet, TF_KONSEKVENS, tf_hojning)
    kvarstaende, kvar_regel = _kvarstaende(regelbas, inneboende.risk, kontroller)
    regelspar = (metod.sannolikhet.id, metod.konsekvens.id, rad.id, metod.terrorfinansiering.id, tf_rad.id, kvar_regel)
    return inneboende, terrorfinansiering, kvarstaende, regelspar


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
    valda, okanda = _valda_sarbarheter(regelbas, tjanst, varden)
    return _utan_ersatta(valda), okanda


def _valda_sarbarheter(
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde]
) -> tuple[tuple[Sarbarhet, ...], frozenset[str]]:
    """Sårbarheter vars villkor gäller, före kombinationsreglerna (ersatter)."""
    definitioner = regelbas.faltdefinitioner()
    utfall = [
        (sarbarhet, utvardera(tolka_villkor(sarbarhet.villkor, definitioner), varden))
        for sarbarhet in (regelbas.sarbarheter[sarbarhet_id] for sarbarhet_id in tjanst.sarbarheter)
    ]
    valda = tuple(sarbarhet for sarbarhet, resultat in utfall if _galler(sarbarhet, resultat))
    okanda = frozenset().union(*(resultat.okanda for _, resultat in utfall))
    return valda, okanda


def _utan_ersatta(valda: tuple[Sarbarhet, ...]) -> tuple[Sarbarhet, ...]:
    """Kombinationsregel: en vald sårbarhet tar bort de sårbarheter den ersätter bland de valda."""
    ersatta = {id for s in valda for id in s.ersatter}
    return tuple(s for s in valda if s.id not in ersatta)


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
    regelbas: Regelbas, tjanst: Tjanst, varden: dict[str, Faltvarde], profil: Profil
) -> tuple[tuple[Kontrollbedomning, ...], frozenset[str]]:
    resultat = [_kontroll(regelbas.kontroller[kontroll_id], varden, regelbas, profil) for kontroll_id in tjanst.kontroller]
    return tuple(bedomning for bedomning, _ in resultat), frozenset().union(*(okanda for _, okanda in resultat))


def _kontroll(kontroll: Kontroll, varden: dict[str, Faltvarde], regelbas: Regelbas | None = None,
              profil: Profil | None = None) -> tuple[Kontrollbedomning, frozenset[str]]:
    utformning = varden.get(kontroll.utformning_falt, _OKAND)
    genomforande = varden.get(kontroll.genomforande_falt, _OKAND)
    okanda = frozenset(
        falt_id
        for falt_id, varde in ((kontroll.utformning_falt, utformning), (kontroll.genomforande_falt, genomforande))
        if varde.kunskap is Kunskap.OKAND
    )
    effekt = None
    effekt_belagd = None
    if kontroll.effekt_falt or kontroll.utfall_falt:
        from riskanalys.bedomning.erfarenheter import belagd_uppgift
        refs = (kontroll.utformning_falt, kontroll.genomforande_falt,
                kontroll.effekt_falt, kontroll.utfall_falt)
        saknas = {id for id in refs if not id or not regelbas or not profil
                  or not belagd_uppgift(regelbas, profil, id)}
        if not saknas:
            perioder = {profil.uppgifter[id].period for id in refs
                        if regelbas.falt[id].periodkrav}
            if len(perioder) != 1:
                saknas.update(refs)
        okanda |= frozenset(id for id in saknas if id)
        effekt = _kant(varden.get(kontroll.effekt_falt, _OKAND))
        if effekt == "ej_bedömd":
            okanda |= frozenset({kontroll.effekt_falt})
        effekt_belagd = not saknas and effekt == "verksam"
    bedomning = Kontrollbedomning(
        id=kontroll.id,
        effekt=effekt,
        effekt_belagd=effekt_belagd,
        utformning=_kant(utformning),
        genomforande=_kant(genomforande),
        fungerar_och_ar_belagd=_kant(utformning) == "finns" and _kant(genomforande) == "belagt"
        and effekt_belagd is not False,
    )
    return bedomning, okanda


def _kant(varde: Faltvarde) -> str | None:
    return varde.varde if varde.kunskap is Kunskap.KAND else None


def _kvarstaende(regelbas: Regelbas, risk: str, kontroller: tuple[Kontrollbedomning, ...]) -> tuple[str, str]:
    if any(kontroll.fungerar_och_ar_belagd for kontroll in kontroller):
        return steg(risk, -1, RISKNIVAER), regelbas.metod.kvarstaende_sankning.id
    return risk, regelbas.metod.kvarstaende_ej_belagd.id
