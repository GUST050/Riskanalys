"""Gemensamt utkastflöde bevarar aktualitet och återanvänder sparade AI-svar."""
from datetime import date
import pytest
from tester.fixturer.resultatkedja import resultatkedja_bas, resultatkedja, DAG
from riskanalys.fel import RiskanalysFel


def _utkast(k):
    from riskanalys.dokument.export import kor_export_utkast, UTKASTFIL
    return kor_export_utkast(k.fall.byramapp, DAG, granskningsmapp=k.granskningsmapp, regelbas=k.fall.regelbas)/UTKASTFIL


def test_uppdatera_till_v10_utan_nytt_ai_anrop(request, monkeypatch):
    from riskanalys import arbetsfloden as a
    k = request.getfixturevalue('resultatkedja')
    fore = _utkast(k)
    gamla = {p.name: p.read_bytes() for p in fore.parent.glob('*.docx')}
    def inget_anrop(*args, **kwargs):
        raise AssertionError('Exportuppdatering får inte köra AI')
    monkeypatch.setattr(a, 'kor_skrivning', inget_anrop)
    fil = a.uppdatera_export(k.fall.byramapp, k.fall.regelbas, fore, rapportformat='v10')
    assert len(list(fil.parent.glob('*.docx'))) == 3
    assert a.las_utkast(k.fall.byramapp, k.fall.regelbas, fil).startswith(b'PK')
    assert gamla == {p.name: p.read_bytes() for p in fore.parent.glob('*.docx')}


def test_andrad_profil_stoppar_uppdatering_fore_export(request):
    from riskanalys import arbetsfloden as a
    from riskanalys.profil.lagring import spara_profil
    k = request.getfixturevalue('resultatkedja')
    fore = _utkast(k)
    p = k.fall.profil
    spara_profil(k.fall.byramapp, p.model_copy(update={'byra': p.byra.model_copy(update={'datum': date(2026, 12, 1)})}))
    exportfore = set((k.fall.byramapp/'export').iterdir())
    with pytest.raises(RiskanalysFel, match='Profilen har ändrats'):
        a.uppdatera_export(k.fall.byramapp, k.fall.regelbas, fore)
    assert set((k.fall.byramapp/'export').iterdir()) == exportfore
