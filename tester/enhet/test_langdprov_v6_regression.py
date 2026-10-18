"""Längdprovets tillfälliga avvikelse får inte dölja andra regressioner."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


@pytest.mark.parametrize('fel', ['byggkrasch', 'analysforlust'])
def test_realistiska_langdprovet_ger_rod_pyteststatus_for_andra_fel(tmp_path, fel):
    """Kör det verkliga läsprovet med fel i byggaren; pytest måste lämna exitkod 1."""
    plugin = tmp_path / 'langdprov_fel.py'
    plugin.write_text(textwrap.dedent(f'''
        import pytest

        @pytest.fixture(autouse=True)
        def fel_i_byggaren(request, monkeypatch):
            modul = request.module
            original = modul.bygg_arb_v6

            def trasigt_bygge(*args, **kwargs):
                if {fel!r} == 'byggkrasch':
                    raise RuntimeError('avsiktlig byggkrasch i regressionsprov')
                dokument = original(*args, **kwargs)
                return dokument.model_copy(update={{'avsnitt': tuple(
                    a.model_copy(update={{'stycken': (), 'tabeller': ()}})
                    for a in dokument.avsnitt)}})

            monkeypatch.setattr(modul, 'bygg_arb_v6', trasigt_bygge)
    '''), encoding='utf-8')
    repo = Path(__file__).resolve().parents[2]
    miljo = {**os.environ, 'PYTHONPATH': os.pathsep.join((str(tmp_path), str(repo / 'src')))}
    miljo.pop('ANTHROPIC_API_KEY', None)
    svar = subprocess.run(
        [sys.executable, '-m', 'pytest', '-p', 'langdprov_fel',
         'tester/enhet/test_lokalt_dokument_v6.py', '-k', 'test_realistiskt_fyrtjanstprov', '-q', '-rx'],
        cwd=repo, env=miljo, capture_output=True, text=True, timeout=60,
    )
    utskrift = svar.stdout + svar.stderr
    assert svar.returncode == 1, utskrift
    assert 'xfailed' not in utskrift, utskrift
    assert ('RuntimeError: avsiktlig byggkrasch' if fel == 'byggkrasch' else 'assert text in huvud') in utskrift
