"""Regressioner för bedömningens frysta profil och modellidentitet."""
import shutil

import pytest

from riskanalys.bedomning import korning
from riskanalys.drift import modellidentitet
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.manifest import las_manifest, skriv_manifest, verifiera_manifest
from riskanalys.profil.hantering import bekrafta
from riskanalys.profil.lagring import PROFILFIL, las_profil, spara_profil
from tester.fixturer.m2 import DAG


@pytest.fixture
def modellkopia(tmp_path, monkeypatch):
    rot = tmp_path / 'isolerad-modell'
    shutil.copytree(modellidentitet.MODELLROT, rot, ignore=shutil.ignore_patterns('__pycache__'))
    monkeypatch.setattr(modellidentitet, 'MODELLROT', rot)
    return rot


def test_samtidig_profilsparning_kan_inte_byta_bedomningens_profilkopia(byra_med_profil, regelbas, monkeypatch):
    """En atomisk sparning mellan beräkning och kopiering ska lämna en korrekt äldre körning."""
    gammal = (byra_med_profil / PROFILFIL).read_bytes()
    profil = las_profil(byra_med_profil)
    original = korning.bedom

    def rakna_och_spara_nya_svar(*args):
        resultat = original(*args)
        ny = bekrafta(profil, regelbas, 'P-TJ.T-RED-01.erbjuds', 'nej', 'Syntetiskt ändrat uppdrag', 'FfR', DAG)
        spara_profil(byra_med_profil, ny)
        return resultat

    monkeypatch.setattr(korning, 'bedom', rakna_och_spara_nya_svar)
    mapp = korning.kor_bedomning(byra_med_profil, regelbas)
    assert korning.las_bedomning(mapp).tjanster[0].erbjuds is True
    assert (mapp / korning.PROFILKOPIA).read_bytes() == gammal
    assert korning.las_bedomningsprofil(mapp) == profil
    assert verifiera_manifest(mapp) == []
    with pytest.raises(RiskanalysFel, match='Profilen har ändrats'):
        korning.kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_ny_bedomning_binder_den_beraknande_modellen(byra_med_profil, regelbas):
    mapp = korning.kor_bedomning(byra_med_profil, regelbas)
    assert las_manifest(mapp).metadata.get('modellbindning') == modellidentitet.modellbindning(regelbas)
    korning.kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_andrad_motor_stoppar_fortsatt_arbete_med_gammal_bedomning(byra_med_profil, regelbas, modellkopia):
    mapp = korning.kor_bedomning(byra_med_profil, regelbas)
    motor = modellkopia / 'bedomning/scenarier.py'
    text = motor.read_text()
    motor.write_text(text.replace('KONTROLLSANKNING = -1', 'KONTROLLSANKNING = 0'))
    assert verifiera_manifest(mapp) == []
    with pytest.raises(RiskanalysFel, match="[Mm]odell.*riskanalys bedom"):
        korning.kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_aldre_bedomning_far_lasas_men_kraver_omrakning_for_fortsatt_arbete(byra_med_profil, regelbas):
    mapp = korning.kor_bedomning(byra_med_profil, regelbas)
    bedomning = korning.las_bedomning(mapp)
    metadata = dict(las_manifest(mapp).metadata)
    metadata.pop('modellbindning', None)
    skriv_manifest(mapp, metadata)
    assert verifiera_manifest(mapp) == []
    assert korning.las_bedomning(mapp) == bedomning
    assert korning.las_bedomningsprofil(mapp) == las_profil(byra_med_profil)
    with pytest.raises(RiskanalysFel, match="[Mm]odell.*riskanalys bedom"):
        korning.kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_presentationsandring_kraver_inte_ny_bedomning(byra_med_profil, regelbas, modellkopia):
    mapp = korning.kor_bedomning(byra_med_profil, regelbas)
    fil = modellkopia / 'dokument/wordstil.py'
    fil.write_text(fil.read_text() + '\n# Syntetisk presentationsändring.\n')
    korning.kontrollera_aktuell(byra_med_profil, mapp, regelbas)


def test_ny_analysbindning_kan_inte_markera_gamla_nivaer_med_ny_modell(tmp_path, regelbas_v1, modellkopia):
    from riskanalys.analys.lagring import bygg_bindning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.skrivning import kor_skrivning
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from tester.fixturer.m2 import komplett_profil, bygg_delsvar

    rb = regelbas_v1
    byra = tmp_path / 'syntetisk'
    profil = komplett_profil(rb, skapa_profil(rb, Byra(id='syntetisk', lan='Västra Götaland', regelpaket='RP-RED-VG', datum=DAG)))
    spara_profil(byra, profil)
    bm = korning.kor_bedomning(byra, rb)
    b = korning.las_bedomning(bm)
    um = kor_skrivning(byra, rb, Testleverantor(bygg_delsvar(rb, profil, b)))
    fore = bygg_bindning(byra, rb, bm, um)
    fil = modellkopia / 'bedomning/scenarier.py'
    fil.write_text(fil.read_text().replace('KONTROLLSANKNING = -1', 'KONTROLLSANKNING = 0'))
    assert modellidentitet.modellbindning(rb) != fore.modell
    with pytest.raises(RiskanalysFel, match='[Mm]odell'):
        bygg_bindning(byra, rb, bm, um)
