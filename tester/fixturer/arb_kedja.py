"""Syntetisk motor- och D-ARB-kedja för regelkontrakten.

Endast syntetiska uppgifter och Testleverantor; inga riktiga byrådata och inga API-anrop.
Nya dokument byggs via bygg_arb i D-ARB-tjanst-v6 med de två AI-delarna hot och
sårbarheter. Historisk v5 byggs bara uttryckligen, för att verifieringen av äldre
paket ska fortsätta vara prövad.
"""
import json
from dataclasses import dataclass

from riskanalys.analys.modeller import Analysbindning, Analyspaket
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.arb import bygg_arb
from riskanalys.dokument.arb_v5 import bygg_arb_v5
from riskanalys.dokument.delskrivning import Tjanstresultat, skriv_tjanst
from riskanalys.dokument.leverantor import Delanrop, Testleverantor
from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.skrivversion import V5, V6, delar_for_version
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.drift.historik import Handelse, Historik
from riskanalys.granskning.kontroller import granska
from riskanalys.granskning.modeller import Fynd
from riskanalys.profil.hantering import skapa_profil
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.modeller import Byra, Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import Urval, valj
from tester.fixturer.lokal_analys import bekraftat_utkast
from tester.fixturer.m2 import DAG, godkant_delsvar, komplett_profil

HISTORIK = Historik().med(Handelse(datum=DAG, typ="utvärdering", beskrivning="Syntetiskt prov."))


@dataclass(frozen=True)
class Kedja:
    """Ett byggt syntetiskt underlag: motorutfall, validerade skrivdelar och dokument."""

    urval: Urval
    bedomning: Bedomning
    resultat: dict[str, Tjanstresultat]
    dokument: Dokument
    delanrop: tuple[Delanrop, ...]
    analys: Analyspaket | None = None


def syntetisk_profil(rb: Regelbas) -> Profil:
    byra = Byra(id="syntetisk", regelpaket="RP-RED-VG", lan="Västra Götaland", datum=DAG)
    return komplett_profil(rb, skapa_profil(rb, byra))


def andrat(profil: Profil, falt: str, **uppdatering) -> Profil:
    """Ny profil där en uppgift har ändrats; originalet lämnas orört."""
    uppgift = profil.uppgifter[falt].model_copy(update=uppdatering)
    return profil.model_copy(update={"uppgifter": {**profil.uppgifter, falt: uppgift}})


def bedom_kedja(rb: Regelbas, profil: Profil) -> tuple[Urval, Bedomning]:
    """Bara regelurval och motor. Prov som gäller motorutfall bygger inget dokument."""
    urval = valj(rb, profil.byra.regelpaket, DAG, profil.byra.lan)
    return urval, bedom(rb, urval, profil)


def skriv(rb: Regelbas, profil: Profil, bedomning: Bedomning, *,
          formatversion: str = V6) -> tuple[dict[str, Tjanstresultat], tuple[Delanrop, ...]]:
    """Kör den riktiga delskrivningen mot Testleverantor, en leverantör per tjänst."""
    resultat: dict[str, Tjanstresultat] = {}
    anrop: list[Delanrop] = []
    for avsnitt_id, tjanst in tjanster_med_avsnitt(bedomning):
        leverantor = Testleverantor([godkant_delsvar(d, tjanst) for d in delar_for_version(formatversion)])
        resultat[avsnitt_id] = skriv_tjanst(leverantor, rb, profil, tjanst, avsnitt_id, effort="medium",
                                            personnamn=(), spara=lambda *args: None, formatversion=formatversion)
        anrop.extend(leverantor.delanrop)
    return resultat, tuple(anrop)


def v6_kedja(rb: Regelbas, profil: Profil, *, analys: Analyspaket | None = None,
             historik: Historik = HISTORIK) -> Kedja:
    """Nytt dokument genom den publika byggvägen; den ska alltid ge v6."""
    urval, bedomning = bedom_kedja(rb, profil)
    resultat, anrop = skriv(rb, profil, bedomning)
    dokument = bygg_arb(rb, profil, bedomning, resultat, historik, analys=analys)
    assert dokument.formatversion == V6, dokument.formatversion
    return Kedja(urval, bedomning, resultat, dokument, anrop, analys)


def v5_kedja(rb: Regelbas, profil: Profil, *, historik: Historik = HISTORIK) -> Kedja:
    """Historiskt v5-dokument med femdelars skrivresultat, för verifiering av äldre paket."""
    urval, bedomning = bedom_kedja(rb, profil)
    resultat, anrop = skriv(rb, profil, bedomning, formatversion=V5)
    return Kedja(urval, bedomning, resultat, bygg_arb_v5(rb, profil, bedomning, resultat, historik), anrop)


def granska_kedja(rb: Regelbas, kedja: Kedja, profil: Profil, dokument: Dokument | None = None, *,
                  historik: Historik = HISTORIK) -> tuple[Fynd, ...]:
    """Granska kedjans eller ett ändrat dokument mot samma frysta skrivresultat och analys."""
    return granska(rb, kedja.urval, profil, kedja.bedomning, dokument or kedja.dokument, historik, DAG,
                   skrivresultat=kedja.resultat, analys=kedja.analys)


def med_avsnitt(dokument: Dokument, avsnitt: Avsnitt) -> Dokument:
    """Nytt dokument där avsnittet med samma id är utbytt."""
    return dokument.model_copy(update={"avsnitt": tuple(avsnitt if a.id == avsnitt.id else a for a in dokument.avsnitt)})


def ai_begaran(kedja: Kedja) -> str:
    """Allt som AI faktiskt fick i kedjans delanrop, som en sökbar text."""
    return json.dumps([a.model_dump(mode="json", by_alias=True) for a in kedja.delanrop], ensure_ascii=False)


def bekraftad_analys(rb: Regelbas, profil: Profil, bedomning: Bedomning) -> Analyspaket:
    """Förifylld och syntetiskt bekräftad lokal analys utan filer, attest eller beslut."""
    bindning = Analysbindning(byra=profil.byra.id, profilrevision=profilrevision(profil),
                              bedomningsmanifest="syntetisk-bedömning", utkastmanifest="syntetiskt-utkast",
                              regelbas=rb.kontrollsumma, kallunderlag="syntetiska-källor",
                              historik="syntetisk-historik", bedomningsdatum=bedomning.datum,
                              modell="sha256:" + "a" * 64)
    return bekraftat_utkast(forifyll_analys(rb, profil, bedomning, bindning), rb)
