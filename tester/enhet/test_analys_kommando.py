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


def test_schema_tva_accepteras_for_utkast_innan_byralasning(capsys):
    assert main(['analys','finns-inte','--forifyll','--schema','2'])==1
    assert '--revision' in capsys.readouterr().err


@pytest.mark.parametrize('flagga',['--bekrafta-tillampningar','--tillampningsfil','--tackningsprovning'])
def test_nya_typade_handlingar_kraver_revision(flagga,capsys):
    assert main(['analys','finns-inte',flagga,'saknas.yaml'])==1
    assert '--revision' in capsys.readouterr().err


def test_bekraftelse_och_import_ar_olika_handlingar(capsys):
    with pytest.raises(SystemExit) as exc:main(['analys','syntetisk','--import','svar.yaml','--bekrafta-tillampningar','refs.yaml'])
    assert exc.value.code==2
