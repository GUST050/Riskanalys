from pathlib import Path
import importlib.util
import json
import pytest
from tester.enhet.test_arb_v8 import v8fall


def verktyg(namn):
    p=Path(__file__).resolve().parents[2]/'docs/research/verktyg'/namn
    spec=importlib.util.spec_from_file_location('forenklad_slutprov',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


@pytest.mark.parametrize('fall',['fyra_tjanster','med_betalningsmandat'])
def test_slutprovsverktyg_skapar_tva_verkliga_v8_utkast(tmp_path,fall):
    from docx import Document
    m=verktyg('forenklad_slutprov.py');ut=tmp_path.resolve()/'ut'
    assert m.main(['--ut',str(ut),'--fall',fall])==0
    data=json.loads((ut/'slutprov.json').read_text())
    assert data['syntetiskt'] and data['analysschema']==2 and len(data['filer'])==2
    for namn,hash in data['filer'].items():
        assert hash.startswith('sha256:') and Document(ut/namn).paragraphs
    with pytest.raises(SystemExit):m.main(['--ut',str(ut),'--fall',fall])


def test_matning_valjer_schema_med_samma_fakta_och_skrivsvar(capsys):
    m=verktyg('rapportmatning.py');rader=[]
    for schema in (1,2):
        m.main(['fyra_tjanster','--analys-schema',str(schema)])
        out=capsys.readouterr().out
        data=json.loads(next(l.removeprefix('Mätkontrakt: ') for l in out.splitlines() if l.startswith('Mätkontrakt: ')))
        assert data['analys_schema']==schema and 'Ord per leveransdel:' in out
        rader.append(data)
    assert all(rader[0][k]==rader[1][k] for k in ('profil','motor','skrivsvar','regelbas'))


def test_frysta_skrivsvar_undantar_bara_anropstid_och_bevarar_text(v8fall):
    from datetime import timedelta
    from tester.enhet.test_arb_v8 import skriv
    m=verktyg('matkontrakt.py');f,_=v8fall;r=skriv(f);fore={k:v.model_dump_json() for k,v in r.items()}
    data=m.frysta_skrivsvar(r);id=next(iter(r));t=r[id];d=t.delar[0];forsok=d.forsok[0]
    annat=forsok.model_copy(update={'anrop':forsok.anrop.model_copy(update={'tidpunkt':forsok.anrop.tidpunkt+timedelta(days=1)})})
    def med(f):return {**r,id:t.model_copy(update={'delar':(d.model_copy(update={'forsok':(f,*d.forsok[1:])}),*t.delar[1:])})}
    assert m.frysta_skrivsvar(med(annat))==data
    assert m.frysta_skrivsvar(med(forsok.model_copy(update={'text':forsok.text+' Ändrat svar.'})))!=data
    assert {k:v.model_dump_json() for k,v in r.items()}==fore


def test_analyslage_ar_uttryckligt_och_alias_skyddat(capsys):
    m=verktyg('rapportmatning.py')
    with pytest.raises(SystemExit):m.main(['fyra_tjanster','--analys-schema','1','--analyslage','direkt2'])
    assert 'olika arbetssätt' in capsys.readouterr().err


def test_nativt_slutprov_loggar_handlingar_och_noll_tackningsbehov(tmp_path):
    m=verktyg('forenklad_slutprov.py');ut=tmp_path.resolve()/'direkt2'
    assert m.main(['--ut',str(ut),'--fall','fyra_tjanster','--analyslage','direkt2'])==0
    data=json.loads((ut/'slutprov.json').read_text())
    assert data['analyslage']=='direkt2' and data['analysschema']==2 and len(data['filer'])==2
    assert data['arbetsbord']['gemensamma_svar']==7
    assert data['arbetsbord']['tackningsprovningar_kravda']==data['arbetsbord']['tackningsprovningar_utforda']==0
    assert data['matning']['b1']>0 and len(data['matning']['per_del'])==2
