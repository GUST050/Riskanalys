import os


def test_cli_i_process_bevarar_miljon_och_samma_felkod(tmp_path,monkeypatch):
    from tester.fixturer.cli_process import kor_direkt
    monkeypatch.setenv('RISKANALYS_DATA','ursprunglig')
    r=kor_direkt({'RISKANALYS_DATA':str(tmp_path)},'verifiera','saknas','1',expected=1)
    assert r.returncode==1 and 'saknas' in r.stderr and 'Traceback' not in r.stderr
    assert os.environ['RISKANALYS_DATA']=='ursprunglig'
