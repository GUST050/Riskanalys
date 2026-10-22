"""CLI-gränsen utan ny Pythonprocess; isolerad miljö och fångad utdata."""
from contextlib import redirect_stderr,redirect_stdout
from io import StringIO
import os
from subprocess import CompletedProcess
from unittest.mock import patch
from riskanalys.cli import main


def kor_direkt(env,*args,expected=0):
    nyckelfil=env.get('RISKANALYS_NYCKELFIL') or os.environ.get('RISKANALYS_NYCKELFIL')
    if not nyckelfil:raise ValueError('Testet måste ha en isolerad obefintlig nyckelfil.')
    out,err=StringIO(),StringIO()
    with patch.dict(os.environ,{**env,'RISKANALYS_NYCKELFIL':nyckelfil},clear=True),redirect_stdout(out),redirect_stderr(err):
        kod=main(list(args))
    r=CompletedProcess(args,kod,out.getvalue(),err.getvalue())
    assert r.returncode==expected,r.stdout+'\n'+r.stderr
    assert 'Traceback' not in r.stderr
    return r
