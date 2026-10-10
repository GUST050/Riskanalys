"""Gemensamma fixturer. Alla uppgifter är syntetiska."""

import shutil
from pathlib import Path
import copy
from datetime import date

import pytest
import yaml

from riskanalys.lagring.kontrollsumma import for_text

LYDELSETEXT = "Verksamhetsutövaren ska göra en allmän\nriskbedömning. Syntetisk testtext.\n"
LYDELSESUMMA = for_text(" ".join(LYDELSETEXT.split()))


def _matris() -> list[dict]:
    nivaer = [
        ("låg", "begränsad", "låg"),
        ("låg", "betydande", "måttlig"),
        ("låg", "allvarlig", "måttlig"),
        ("medel", "begränsad", "måttlig"),
        ("medel", "betydande", "måttlig"),
        ("medel", "allvarlig", "hög"),
        ("hög", "begränsad", "måttlig"),
        ("hög", "betydande", "hög"),
        ("hög", "allvarlig", "mycket hög"),
    ]
    return [
        {
            "id": f"BT-MATRIS-{nummer:02d}",
            "sannolikhet": sannolikhet,
            "konsekvens": konsekvens,
            "risk": risk,
            "grund": "metodval",
            "forklaring": f"{sannolikhet} sannolikhet och {konsekvens} konsekvens ger {risk} risk.",
        }
        for nummer, (sannolikhet, konsekvens, risk) in enumerate(nivaer, start=1)
    ]


def _regel(regel_id: str) -> dict:
    return {"id": regel_id, "grund": "metodval", "forklaring": "Testregel."}


METOD = {
    "riskmatris": _matris(),
    "sannolikhet": _regel("BT-SANN-01"),
    "konsekvens": _regel("BT-KONS-01"),
    "terrorfinansiering": _regel("BT-TF-01"),
    "kvarstaende_ej_belagd": _regel("BT-KVAR-01"),
    "kvarstaende_sankning": _regel("BT-KVAR-02"),
}

MINIMAL = {
    "version.yaml": {"regelbas_version": "0.0.1"},
    "falt.yaml": [
        {"id": "P-TJ.T-1.erbjuds", "typ": "bool", "fraga": "Erbjuds tjänsten?", "varfor": "Test."},
        {"id": "P-A", "typ": "andel", "fraga": "Hur stor andel?", "varfor": "Test."},
        {"id": "P-NAMN", "typ": "text", "fraga": "Namn?", "varfor": "Test.", "personuppgift": True},
        {"id": "P-C.utf", "typ": "val", "fraga": "Finns kontrollen?", "varfor": "Test.", "val": ["finns", "saknas"]},
        {"id": "P-C.gen", "typ": "val", "fraga": "Är den belagd?", "varfor": "Test.", "val": ["belagt", "ej_belagt"]},
    ],
    "kallor.yaml": [
        {
            "id": "SRC-1",
            "titel": "Testkälla",
            "typ": "föreskrift",
            "utgivare": "Test",
            "url": "https://example.se",
            "hamtad": date(2026, 10, 1),
            "geografi": ["Västra Götaland"],
            "paragrafer": ["1 kap. 1 §", "2 kap. 1 §", "2 kap. 2 §"],
        }
    ],
    "lydelser.yaml": [
        {
            "id": "LYD-1",
            "kalla": "SRC-1",
            "lagrum": "2 kap. 1 §",
            "ikraft": date(2024, 7, 1),
            "primarkalla": "test",
            "text_kontrollsumma": LYDELSESUMMA,
        }
    ],
    "lydelsetexter/LYD-1.txt": LYDELSETEXT,
    "krav/test.yaml": [
        {
            "id": "KRV-1",
            "kalla": "SRC-1",
            "lagrum": "2 kap. 1 §",
            "lydelser": ["LYD-1"],
            "grund": "ska_krav",
            "text": "Testkrav.",
            "galler_om": {"alla": []},
            "belagg": ["dokument"],
            "uppfylls_i": ["D-ARB.1"],
        }
    ],
    "kataloger/hot.yaml": [{"id": "H-1", "namn": "Testhot", "beskrivning": "Test.", "kallor": ["SRC-1"]}],
    "kataloger/sarbarheter.yaml": [
        {
            "id": "S-1",
            "namn": "Testsårbarhet",
            "omrade": "kund",
            "grund": "metodval",
            "villkor": {"falt": "P-A", "op": ">=", "varde": 0.2},
            "effekt": {"sannolikhet": 1},
            "kallor": ["SRC-1"],
        }
    ],
    "kataloger/kontroller.yaml": [
        {
            "id": "C-1",
            "namn": "Testkontroll",
            "beskrivning": "Test.",
            "utformning_falt": "P-C.utf",
            "genomforande_falt": "P-C.gen",
        }
    ],
    "kataloger/tjanster.yaml": [
        {
            "id": "T-1",
            "namn": "Testtjänst",
            "sektor": "redovisning",
            "beskrivning": "Test.",
            "erbjuds_falt": "P-TJ.T-1.erbjuds",
            "hot": ["H-1"],
            "sarbarheter": ["S-1"],
            "kontroller": ["C-1"],
            "grund_sannolikhet": "medel",
            "grund_konsekvens": "betydande",
            "grund_tf_sannolikhet": "låg",
            "kallor": ["SRC-1"],
        }
    ],
    "kataloger/bristmonster.yaml": [
        {
            "id": "B-1",
            "namn": "Testbrist",
            "upptacks": "Test.",
            "automatiserad": False,
            "allvar": "medel",
            "grund": "tillsynspraxis",
            "kallor": ["SRC-1"],
        }
    ],
    "tillatelselistor.yaml": [{"id": "risk_per_tjanst", "falt": ["P-A"], "undvik": ["B-1"]}],
    "beslutstabeller/metod.yaml": METOD,
    "regelpaket/test.yaml": {
        "id": "RP-1",
        "namn": "Testpaket",
        "sektor": "redovisning",
        "lan": ["Västra Götaland"],
        "kallor": ["SRC-1"],
        "krav": ["KRV-1"],
        "tjanster": ["T-1"],
        "paragrafkarta": {
            "giltig_fran": date(2024, 7, 1),
            "omfattning": [{"kalla": "SRC-1", "kapitel": ["2 kap."]}],
            "rader": [
                {"kalla": "SRC-1", "lagrum": "2 kap. 1 §", "krav": ["KRV-1"]},
                {"kalla": "SRC-1", "lagrum": "2 kap. 2 §", "ej_tillamplig": "Testmotivering."},
            ],
        },
    },
}


@pytest.fixture
def minimal_filer():
    """En kopia av den minimala regelbasen som testet får ändra i."""
    return copy.deepcopy(MINIMAL)


@pytest.fixture
def skriv_minimal_regelbas():
    """Skriver den minimala regelbasen, med valfria ersättningar per fil, till en mapp.

    Filer som slutar på .txt skrivs som text, övriga som YAML.
    """

    def skriv(rot, ersattningar=None):
        filer = copy.deepcopy(MINIMAL)
        filer.update(ersattningar or {})
        for relativ, innehall in filer.items():
            sokvag = rot / relativ
            sokvag.parent.mkdir(parents=True, exist_ok=True)
            if relativ.endswith(".txt"):
                sokvag.write_text(innehall, encoding="utf-8")
            else:
                sokvag.write_text(yaml.safe_dump(innehall, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return rot

    return skriv


@pytest.fixture
def minimal_rot(tmp_path, skriv_minimal_regelbas):
    return skriv_minimal_regelbas(tmp_path / "regelbas")


@pytest.fixture
def minimal_regelbas(minimal_rot):
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(minimal_rot)


REPO_REGELBAS = Path(__file__).resolve().parent / "fixturer" / "regelbas_v0"


@pytest.fixture(scope="session")
def regelbas():
    """Fryst M1-regelbas: gamla regressionskontrakt körs mot sin avsedda version."""
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(REPO_REGELBAS)


@pytest.fixture
def datamapp(tmp_path, monkeypatch):
    """En tom datamapp utanför repot, bara för testet."""
    mapp = tmp_path / "data"
    monkeypatch.setenv("RISKANALYS_DATA", str(mapp))
    return mapp


REAL_VARDEN = {
    "P-ORG.namn": "Testbyrån AB",
    "P-ORG.antal_anstallda": 8,
    "P-ORG.verksamhetsstallen": 1,
    "P-ROLL.ffr_namn": "Testa Testsson",
    "P-TJ.T-RED-01.erbjuds": True,
    "P-KUND.andel_riskbransch": 0.3,
    "P-KUND.andel_kontant": 0.05,
    "P-KANAL.andel_digitalt_underlag": 0.8,
    "P-KANAL.bankdata_andel": 0.4,
    "P-VERK.juniora_konsulter": False,
    "P-KONTROLL.C-07.utformning": "finns",
    "P-KONTROLL.C-07.genomforande": "ej_belagt",
}

REAL_VARDEN_TEXT = [
    ("P-ORG.namn", "Testbyrån AB"),
    ("P-ORG.antal_anstallda", "8"),
    ("P-ORG.verksamhetsstallen", "1"),
    ("P-ROLL.ffr_namn", "Testa Testsson"),
    ("P-TJ.T-RED-01.erbjuds", "ja"),
    ("P-KUND.andel_riskbransch", "30 %"),
    ("P-KUND.andel_kontant", "5 %"),
    ("P-KANAL.andel_digitalt_underlag", "0,8"),
    ("P-KANAL.bankdata_andel", "40%"),
    ("P-VERK.juniora_konsulter", "Nej"),
    ("P-KONTROLL.C-07.utformning", "finns"),
    ("P-KONTROLL.C-07.genomforande", "ej_belagt"),
]


@pytest.fixture
def real_varden():
    """Det verklighetsnära testfallet. Alla uppgifter är syntetiska."""
    return dict(REAL_VARDEN)


@pytest.fixture
def real_varden_text():
    """Samma värden som de skrivs på kommandoraden, med blandade svenska format."""
    return list(REAL_VARDEN_TEXT)


@pytest.fixture
def profil_fabrik():
    """Bygger en profil där givna värden är bekräftade och övriga saknas."""
    from riskanalys.profil.modeller import Byra, Profil, Uppgift

    testdag = date(2026, 10, 1)

    def uppgift(falt_id, varden, okanda, ej_tillampliga):
        if falt_id in ej_tillampliga:
            return Uppgift(
                status="ej_tillämplig", motivering="Syntetiskt testfall.", datum=testdag, bekraftad_av="roll:FfR"
            )
        if falt_id in varden and falt_id not in okanda:
            return Uppgift(
                varde=varden[falt_id],
                status="bekräftad",
                kalla="Syntetiskt testfall",
                datum=testdag,
                bekraftad_av="roll:FfR",
            )
        return Uppgift()

    def fabrik(regelbas, varden, okanda=(), ej_tillampliga=()):
        paket = next(iter(regelbas.regelpaket.values()))
        byra = Byra(id="testbyra", regelpaket=paket.id, datum=date(2026, 11, 1), lan="Västra Götaland")
        uppgifter = {falt_id: uppgift(falt_id, varden, okanda, ej_tillampliga) for falt_id in regelbas.falt}
        return Profil(byra=byra, uppgifter=uppgifter)

    return fabrik


@pytest.fixture
def byra_med_profil(datamapp, regelbas, profil_fabrik, real_varden):
    """En byrå i datamappen där alla uppgifter i det verklighetsnära testfallet är bekräftade."""
    from riskanalys.lagring.datamapp import skapa_byramapp
    from riskanalys.profil.lagring import spara_profil

    mapp = skapa_byramapp("testbyra")
    spara_profil(mapp, profil_fabrik(regelbas, real_varden))
    return mapp


@pytest.fixture
def underlag_fabrik(regelbas):
    """Bygger AI-underlaget för den enda tjänsten i repots regelbas utifrån en profil."""
    from riskanalys.bedomning.motor import bedom
    from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
    from riskanalys.regelverk.urval import valj

    def fabrik(profil):
        byra = profil.byra
        bedomning = bedom(regelbas, valj(regelbas, byra.regelpaket, byra.datum, byra.lan), profil)
        ((avsnitt_id, tjanst),) = tjanster_med_avsnitt(bedomning)
        return bygg_underlag(regelbas, profil, tjanst, avsnitt_id)

    return fabrik


@pytest.fixture
def real_underlag(underlag_fabrik, regelbas, profil_fabrik, real_varden):
    return underlag_fabrik(profil_fabrik(regelbas, real_varden))


@pytest.fixture
def giltigt_utkast():
    """Ett AI-utkast för löpande bokföring som klarar valideringen mot real_underlag."""
    from riskanalys.dokument.modeller import AvsnittsUtkast

    return AvsnittsUtkast.model_validate(
        {
            "avsnitt": "D-ARB.6.1",
            "stycken": [
                {
                    "typ": "analys",
                    "text": (
                        "Löpande bokföring hanterar kundernas verifikationer och ligger närmast deras transaktioner. "
                        "Osanna fakturor och brottsvinster som redovisas som intäkter kan därför passera genom "
                        "byråns bokföring."
                    ),
                    "referenser": ["T-RED-01", "H-01", "H-02"],
                },
                {
                    "typ": "motivering",
                    "text": (
                        "Sannolikheten bedöms som hög eftersom 30 % av kunderna finns i riskbranscher och 80 % av "
                        "underlaget kommer in digitalt medan bankdata bara finns för 40 % av kunderna. "
                        "Konsekvensen är betydande. Risken är hög."
                    ),
                    "referenser": [
                        "H-01",
                        "S-KUND-01",
                        "S-KANAL-01",
                        "P-KUND.andel_riskbransch",
                        "P-KANAL.andel_digitalt_underlag",
                        "P-KANAL.bankdata_andel",
                        "BT-MATRIS-08",
                    ],
                },
                {
                    "typ": "analys",
                    "text": (
                        "Risken för finansiering av terrorism bedöms som måttlig. Bankavstämningen mot underlag finns "
                        "i rutinerna men är inte belagd, så den kvarstående risken är hög."
                    ),
                    "referenser": ["BT-MATRIS-03", "C-07", "BT-KVAR-01"],
                },
                {
                    "typ": "scenario",
                    "text": (
                        "En byggkund laddar upp leverantörsfakturor via en app och byrån saknar bankdata för kunden. "
                        "Ett upplägg med osanna fakturor kan då pågå utan att avvikelser syns i avstämningen."
                    ),
                    "referenser": ["H-01", "S-KUND-01", "S-KANAL-01"],
                },
            ],
            "oklarheter": [],
        }
    )


@pytest.fixture
def testsvarsfil(tmp_path, giltigt_utkast):
    """En fil med förberedda svar för --leverantor test."""
    fil = tmp_path / "testsvar.json"
    fil.write_text("[" + giltigt_utkast.model_dump_json() + "]", encoding="utf-8")
    return fil


def kor_till_skrivning(byramapp, regelbas, utkast):
    """Kör bedömning och skrivning med testleverantören och registrerar en utvärdering 2026-11-01."""
    from riskanalys.bedomning.korning import kor_bedomning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.drift.historik import Handelse, las_historik, spara_historik

    kor_bedomning(byramapp, regelbas)
    kor_skrivning(byramapp, regelbas, Testleverantor([utkast]))
    handelse = Handelse(datum=date(2026, 11, 1), typ="utvärdering", beskrivning="Första riskbedömningen.")
    spara_historik(byramapp, las_historik(byramapp).med(handelse))


@pytest.fixture
def skriven_byra(byra_med_profil, regelbas, giltigt_utkast):
    """En byrå med bedömning, godkänt AI-utkast och registrerad utvärdering."""
    kor_till_skrivning(byra_med_profil, regelbas, giltigt_utkast)
    return byra_med_profil


SAKKUNNIG_TEST = {"status": "verifierad", "av": "Testsakkunnig", "datum": date(2026, 10, 1)}
UTANFOR_TESTFALLET = "Syntetiskt testfall: paragrafen ligger utanför den tunna kedjans omfattning."


def _skriv_yaml(fil, data):
    fil.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


@pytest.fixture
def signerad_regelbas_rot(tmp_path):
    """En kopia av repots regelbas som en påhittad sakkunnig har gjort komplett och verifierat.

    Bara för tester. Repots regelbas ändras aldrig. Paragrafer utanför testfallet markeras som
    ej tillämpliga, vilket en riktig sakkunnig inte skulle göra.
    """
    from riskanalys.regelverk.laddning import ladda_regelbas

    rot = tmp_path / "signerad_regelbas"
    shutil.copytree(REPO_REGELBAS, rot)
    paketfiler = sorted((rot / "regelpaket").glob("*.yaml"))
    for fil in paketfiler:
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        rader = [
            rad if rad.get("krav") else {**rad, "ej_tillamplig": UTANFOR_TESTFALLET}
            for rad in paket["paragrafkarta"]["rader"]
        ]
        _skriv_yaml(fil, {**paket, "paragrafkarta": {**paket["paragrafkarta"], "rader": rader}})
    regelbas = ladda_regelbas(rot)
    for fil in (rot / "krav").glob("*.yaml"):
        poster = yaml.safe_load(fil.read_text(encoding="utf-8"))
        signerade = [
            {**post, "sakkunnig": {**SAKKUNNIG_TEST, "kontrollsumma": regelbas.kravets_innehallssumma(post["id"])}}
            for post in poster
        ]
        _skriv_yaml(fil, signerade)
    for fil in paketfiler:
        paket = yaml.safe_load(fil.read_text(encoding="utf-8"))
        summa = regelbas.kartans_innehallssumma(paket["id"])
        karta = {**paket["paragrafkarta"], "sakkunnig": {**SAKKUNNIG_TEST, "kontrollsumma": summa}}
        _skriv_yaml(fil, {**paket, "paragrafkarta": karta})
    return rot


@pytest.fixture
def signerad_regelbas(signerad_regelbas_rot):
    from riskanalys.regelverk.laddning import ladda_regelbas

    return ladda_regelbas(signerad_regelbas_rot)


def kor_kedja(byramapp, regelbas, utkast):
    """Kör kedjan fram till och med godkänd sakgranskning av varje avsnitt."""
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, spara_sakgranskningar
    from riskanalys.granskning.korning import granskningens_profil, kor_granskning, las_granskning

    kor_till_skrivning(byramapp, regelbas, utkast)
    granskningsmapp = kor_granskning(byramapp, regelbas, date(2026, 11, 2))
    dokument, _ = las_granskning(granskningsmapp)
    profil = granskningens_profil(byramapp, granskningsmapp)
    sakgranskningar = ()
    for avsnitt in dokument.avsnitt:
        sakgranskningar = registrera_sakgranskning(
            sakgranskningar, dokument, profil, avsnitt.id, True, "FfR", "Testa Testsson", date(2026, 11, 3)
        )
    spara_sakgranskningar(byramapp, sakgranskningar)


@pytest.fixture
def kedja(byra_med_profil, signerad_regelbas, giltigt_utkast):
    """En byrå där hela kedjan fram till sakgranskning är körd med den signerade regelbasen."""
    kor_kedja(byra_med_profil, signerad_regelbas, giltigt_utkast)
    return byra_med_profil


@pytest.fixture
def osignerad_kedja(byra_med_profil, regelbas, giltigt_utkast):
    """Samma kedja med repots regelbas, som inte är sakkunniggranskad. Den får aldrig gå att fastställa."""
    kor_kedja(byra_med_profil, regelbas, giltigt_utkast)
    return byra_med_profil


# Codex 2026-10-10, P1: ett godkänt AI-utkast med en öppen fråga i oklarheterna.
OPPEN_FRAGA = {"fraga": "Har byrån bankkoppling för alla kunder?", "saknad_uppgift": "P-KANAL.bankdata_andel"}


@pytest.fixture
def utkast_med_oppen_fraga(giltigt_utkast):
    from riskanalys.dokument.modeller import Oklarhet

    return giltigt_utkast.model_copy(update={"oklarheter": [Oklarhet(**OPPEN_FRAGA)]})


@pytest.fixture
def skriven_byra_med_oppen_fraga(byra_med_profil, regelbas, utkast_med_oppen_fraga):
    kor_till_skrivning(byra_med_profil, regelbas, utkast_med_oppen_fraga)
    return byra_med_profil


@pytest.fixture
def kedja_med_oppen_fraga(byra_med_profil, signerad_regelbas, utkast_med_oppen_fraga):
    kor_kedja(byra_med_profil, signerad_regelbas, utkast_med_oppen_fraga)
    return byra_med_profil

@pytest.fixture(scope="session")
def regelbas_v1():
    """Den verkliga, aktuella regelbasen för M2:s kontrakt."""
    from riskanalys.regelverk.laddning import ladda_regelbas, STANDARD_REGELBAS
    return ladda_regelbas(STANDARD_REGELBAS)
