import json
import threading
import pytest
from riskanalys.foretagsdata.scb import SCBLeverantor
from riskanalys.foretagsdata.lagring import las_bild
from riskanalys.intag.webb import skapa_server
from riskanalys.intag.tjanst import Intagstjanst, profilrevision
from tester.foretagsdata.test_scb import ORG,post
from tester.intag.test_webb import anrop,starta
from tester.fixturer.m2 import DAG
from io import BytesIO

@pytest.fixture
def webb(tmp_path,monkeypatch,rb_intag):
    monkeypatch.setenv('RISKANALYS_DATA',str(tmp_path));monkeypatch.delenv('RISKANALYS_SCB_API_KEY',raising=False)
    t=Intagstjanst('syntetisk',rb_intag)
    provider=SCBLeverantor(nyckel='endast-test',transport=lambda *a,**k:BytesIO(json.dumps(post()).encode()))
    s=skapa_server(t,foretagsleverantor=provider)
    trad=threading.Thread(target=s.serve_forever,daemon=True);trad.start()
    yield s,t
    s.shutdown();s.server_close();trad.join(timeout=2)


def hamta(s):return anrop(s,'registerhamta',dict(csrf=s.csrf,orgnr=ORG))


def test_hamtning_fore_start_med_bekraftelse_och_utan_ai(webb):
    s,t=webb
    assert 'Hämta företagsuppgifter' in anrop(s)[1]
    status,html,_=hamta(s)
    assert status==200 and 'Syntetisk byrå AB' in html and '1–4 anställda' in html and '2024' in html
    assert not t.finns()
    b=las_bild(t.mapp)
    d=dict(csrf=s.csrf,bildsumma=b.summa,filial='nej',datum=str(DAG),roll='Test',**{'val_P-ORG.sateslan':'ja'})
    assert anrop(s,'skapa',d)[0]==400
    d['ratt_byra']='ja';d['filialkalla']='Syntetiskt eget registreringsbevis'
    assert anrop(s,'skapa',d)[0]==200
    p=t.profil()
    assert p.byra.lan=='Västra Götaland' and not p.ar_bekraftad('P-ORG.namn')
    assert b.summa in p.uppgifter['P-ORG.sateslan'].kalla
    assert 'SCB' in anrop(s,'register')[1]
    assert 'endast-test' not in html


def test_hamtning_bevarar_svar_konflikt_visas_och_bekraftelse_kraver_ratt_byra(webb):
    s,t=webb;starta(s);p=t.profil()
    assert p.byra.lan=='Skåne'
    assert hamta(s)[0]==200 and t.profil()==p
    status,html,_=anrop(s,'register')
    assert status==200 and 'Skåne' in html and 'Avviker' in html and 'Västra Götaland' in html
    b=las_bild(t.mapp)
    d=dict(csrf=s.csrf,bildsumma=b.summa,falt='P-ORG.sateslan',revision=profilrevision(p),roll='Test',datum=str(DAG))
    assert anrop(s,'registerbekrafta',d)[0]==400
    d['ratt_byra']='ja'
    assert anrop(s,'registerbekrafta',d)[0]==200
    assert t.profil().byra.lan=='Västra Götaland'
    assert anrop(s,'registerbekrafta',d)[0]==409


def test_lokal_json_ursprung_marks_och_html_escapas(webb):
    s,t=webb
    d=post();d['namn']='<script>syntetisk</script>'
    status,html,_=anrop(s,'registerimport',dict(csrf=s.csrf,orgnr=ORG,jsontext=json.dumps(d)))
    assert status==200 and 'ursprung ej verifierat' in html
    assert '&lt;script&gt;' in html and '<script>syntetisk' not in html
    assert las_bild(t.mapp).ursprung=='lokal_json'
    assert not t.finns()


def test_gammal_registerbild_stoppar_start(webb):
    s,t=webb;hamta(s);b=las_bild(t.mapp);hamta(s)
    d=dict(csrf=s.csrf,bildsumma=b.summa,ratt_byra='ja',filial='nej',datum=str(DAG),roll='Test')
    assert anrop(s,'skapa',d)[0]==409 and not t.finns()


def test_fel_och_skydd_utan_mutation(webb):
    s,t=webb
    assert anrop(s,'registerhamta',dict(csrf='fel',orgnr=ORG))[0]==403
    assert anrop(s,'registerimport',dict(csrf=s.csrf,orgnr=ORG,jsontext='[]'))[0]==400
    assert anrop(s,'registerimport',dict(csrf=s.csrf,orgnr=ORG,jsontext='{'))[0]==400
    assert not t.finns() and las_bild(t.mapp) is None
    s.foretagsleverantor=SCBLeverantor()
    status,html,_=hamta(s)
    assert status==400 and 'Registrera' in html and not t.finns()


def test_djupt_ogiltigt_json_ger_atgarderbart_fel(webb):
    s,t=webb
    import sys
    tidigare=sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(1000)
        status,html,_=anrop(s,'registerimport',dict(csrf=s.csrf,orgnr=ORG,jsontext='['*5000+']'*5000))
    finally:sys.setrecursionlimit(tidigare)
    assert status==400 and 'JSON' in html
    assert las_bild(t.mapp) is None


def test_skadat_register_ger_felsida_aven_vid_post(webb):
    s,t=webb;hamta(s);b=las_bild(t.mapp)
    (t.mapp/'register'/f'{b.summa}.json').write_text('{}')
    status,html,_=hamta(s)
    assert status==400 and 'kontrollsumma' in html
    assert not t.finns()
