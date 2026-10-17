"""CLI avvisar farliga flaggkombinationer innan filer eller tjänster används."""
import pytest
from riskanalys.cli import main


def test_import_och_godkannande_far_inte_kombineras(capsys):
    with pytest.raises(SystemExit) as exc:
        main(['analys', 'syntetisk', '--import', 'svar.yaml', '--godkann'])
    assert exc.value.code == 2
    assert 'not allowed with argument' in capsys.readouterr().err


def test_mutation_kraver_revision_fore_nagon_byralasning(capsys):
    assert main(['analys', 'finns-inte', '--forifyll']) == 1
    assert '--revision' in capsys.readouterr().err


def test_godkannande_kraver_identitet_datum_och_tjanst(capsys):
    assert main(['analys', 'finns-inte', '--godkann', '--revision', 'x']) == 1
    fel = capsys.readouterr().err
    assert '--namn' in fel and '--roll' in fel and '--datum' in fel
