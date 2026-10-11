import json
from io import BytesIO
from urllib.error import HTTPError, URLError
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.scb import SCBLeverantor, tolka_scb, organisationsnummer

ORG = '5599991238'  # Syntetiskt nummer med kontrollsiffra; ingen verklig byrå.

def post(**extra):
    return dict(peOrgNr='16'+ORG, orgNr=ORG, namn='Syntetisk byrå AB', lanSate='14',
                aeAnt=2, anstKl='2', omsKl='4', omsAr=2024, jurform='49', ftgStat='1',
                naringsgrenar=[dict(rangordning=1,naringsgren='69201',andelProcent=100,avdelningsKod='N')],
                epost='ska-inte-sparas@example.invalid', tel='ska inte sparas', **extra)


def test_identitet_minimalprojektion_och_inga_klassinferenser():
    b=tolka_scb(post(),ORG,'scb_api')
    assert b.orgnr==ORG and b.lan=='Västra Götaland'
    assert b.forslag()=={'P-ORG.namn':'Syntetisk byrå AB','P-ORG.sateslan':'Västra Götaland','P-ORG.verksamhetsstallen':2}
    assert b.anstalldaklass=='2' and b.omsattningsar==2024 and b.sni==('69201',)
    assert 'ska-inte-sparas' not in b.model_dump_json()
    assert b.uppgiftsdatum is None


@pytest.mark.parametrize('v',['559999-1238','165599991238',ORG])
def test_normalisera_orgnr(v):
    assert organisationsnummer(v)==ORG


@pytest.mark.parametrize('v',['5599991230','19900101-1234','199001011234','5599991238/evil','１２３４５６７８９０','123',''])
def test_ogiltigt_orgnr(v):
    with pytest.raises(RiskanalysFel):organisationsnummer(v)


@pytest.mark.parametrize('extra',[{'orgNr':'5599991246'}, {'peOrgNr':'165599991246'}, {'orgNr':None}, {'namn':''}, {'aeAnt':True}, {'aeAnt':-1}, {'lanSate':'99'}, {'naringsgrenar':[{'naringsgren':'<script>'}]}])
def test_saknad_felaktig_eller_avvikande_identitet(extra):
    d=post();d.update(extra)
    with pytest.raises(RiskanalysFel):tolka_scb(d,ORG,'scb_api')


def test_saknade_uppgifter_blir_inte_noll_eller_nej():
    b=tolka_scb({'orgNr':ORG,'peOrgNr':'16'+ORG,'namn':'Syntetisk'},ORG,'lokal_json')
    assert b.forslag()=={'P-ORG.namn':'Syntetisk'}
    assert b.arbetsstallen is None and b.anstalldaklass is None
    assert b.ursprung=='lokal_json'


def test_nyckel_saknas_utan_natverk(monkeypatch):
    monkeypatch.delenv('RISKANALYS_SCB_API_KEY',raising=False)
    def stopp(*a,**k):pytest.fail('Nätverk utan nyckel')
    with pytest.raises(RiskanalysFel,match='Registrera'):
        SCBLeverantor(transport=stopp).hamta(ORG)


def test_verifierat_endpoint_header_och_identitet():
    anrop=[]
    def transport(req,timeout):
        anrop.append((req,timeout));return BytesIO(json.dumps(post()).encode())
    b=SCBLeverantor(nyckel='hemlig',transport=transport).hamta(ORG)
    req,t=anrop[0]
    assert req.full_url=='https://apiafr.scb.se/v1/juridiskaenheter/16'+ORG+'/full'
    assert req.get_header('X-api-key')=='hemlig' and t==15
    assert b.ursprung=='scb_api' and 'hemlig' not in b.model_dump_json()


@pytest.mark.parametrize('kod',[301,302,307,400,401,403,404,429,500,503])
def test_api_fel_visar_inte_hemligheter(kod):
    def transport(req,timeout):
        raise HTTPError(req.full_url,kod,'hemlig',{},BytesIO(b'hemlig'))
    with pytest.raises(RiskanalysFel) as e:SCBLeverantor(nyckel='hemlig',transport=transport).hamta(ORG)
    assert 'hemlig' not in str(e.value)


@pytest.mark.parametrize('body',[b'<html>bad</html>', b'[]',b'x'*131073])
def test_ogiltig_eller_overstor_respons(body):
    with pytest.raises(RiskanalysFel):
        SCBLeverantor(nyckel='hemlig',transport=lambda *a,**k:BytesIO(body)).hamta(ORG)


def test_natfel_redigeras():
    def transport(*a,**k):raise URLError('hemlig')
    with pytest.raises(RiskanalysFel) as e:SCBLeverantor(nyckel='hemlig',transport=transport).hamta(ORG)
    assert 'hemlig' not in str(e.value)


def test_namn_med_forbjudna_kontrolltecken_avvisas():
    d=post();d['namn']='Syntetisk\x00byrå'
    with pytest.raises(RiskanalysFel):tolka_scb(d,ORG,'scb_api')


def test_riktig_transport_foljer_inte_redirect_med_nyckeln():
    import threading
    from http.server import HTTPServer,BaseHTTPRequestHandler
    from urllib.request import Request
    from riskanalys.foretagsdata.scb import _transport
    anrop=[]
    class H(BaseHTTPRequestHandler):
        def log_message(self,*a):pass
        def do_GET(self):
            anrop.append(self.path)
            self.send_response(302 if self.path=='/start' else 200)
            self.send_header('Location','/mal');self.end_headers()
    server=HTTPServer(('127.0.0.1',0),H)
    trad=threading.Thread(target=server.serve_forever,daemon=True);trad.start()
    try:
        with pytest.raises(HTTPError):_transport(Request(f'http://127.0.0.1:{server.server_port}/start',headers={'X-API-Key':'syntetisk'}),timeout=2)
        assert anrop==['/start']
    finally:server.shutdown();server.server_close();trad.join(timeout=2)


@pytest.mark.parametrize('vid_lasning',[False,True])
def test_trasigt_http_protokoll_redigeras(vid_lasning):
    from http.client import IncompleteRead
    class TrasigtSvar(BytesIO):
        def read(self,*a):raise IncompleteRead(b'hemlig',100)
    def transport(*a,**k):
        if vid_lasning:return TrasigtSvar()
        raise IncompleteRead(b'hemlig',100)
    with pytest.raises(RiskanalysFel) as e:SCBLeverantor(nyckel='hemlig',transport=transport).hamta(ORG)
    assert 'hemlig' not in str(e.value)


def test_extra_skattestatus_ar_bakgrund_inte_intagssvar():
    b=tolka_scb(post(fSkattStat='1',momsStat='3',arbGivStat='9'),ORG,'scb_api')
    assert b.schema_version==3
    assert (b.fskatt_status,b.moms_status,b.arbetsgivar_status)==('1','3','9')
    assert set(b.forslag())=={'P-ORG.namn','P-ORG.sateslan','P-ORG.verksamhetsstallen'}


def test_v1_registerbild_behaller_ursprunglig_summa():
    import hashlib
    from riskanalys.foretagsdata.modeller import Registerbild
    raw='{"schema_version":1,"orgnr":"5599991238","namn":"Syntetisk","lan":null,"arbetsstallen":null,"anstalldaklass":null,"omsattningsklass":null,"omsattningsar":null,"juridisk_form":null,"foretagsstatus":null,"sni":[],"ursprung":"scb_api","hamtad":"2026-10-10T10:00:00Z","uppgiftsdatum":null,"kalla":"https://apiafr.scb.se/scalar/"}'
    b=Registerbild.model_validate_json(raw)
    assert b.summa==hashlib.sha256(raw.encode()).hexdigest()
    assert b.fskatt_status is None
    assert Registerbild.model_validate_json(b.model_dump_json()).summa==b.summa


@pytest.mark.parametrize('kod,foreslas',[('41',True),('42',False),('50',False),('99',False),(None,False)])
def test_agarkontroll_utan_koncern_ger_bara_avgransat_nejforslag(kod,foreslas):
    b=tolka_scb(post(agKat=kod),ORG,'scb_api')
    assert b.schema_version==3 and b.agarkontroll==kod
    assert ('P-ORG.koncernmoder' in b.forslag())==foreslas
    if foreslas:assert b.forslag()['P-ORG.koncernmoder'] is False
    assert 'P-ORG.utlandsk_filial' not in b.forslag()


def test_v2_registerbild_behaller_summa_och_forslag():
    import hashlib
    from riskanalys.foretagsdata.modeller import Registerbild
    raw='{"schema_version":2,"orgnr":"5599991238","namn":"Syntetisk","lan":null,"arbetsstallen":null,"anstalldaklass":null,"omsattningsklass":null,"omsattningsar":null,"juridisk_form":null,"foretagsstatus":null,"sni":[],"ursprung":"scb_api","hamtad":"2026-10-10T10:00:00Z","uppgiftsdatum":null,"kalla":"https://apiafr.scb.se/scalar/","fskatt_status":"1","moms_status":"1","arbetsgivar_status":"9"}'
    b=Registerbild.model_validate_json(raw)
    assert b.model_dump_json()==raw and b.summa==hashlib.sha256(raw.encode()).hexdigest()
    assert b.agarkontroll is None and 'P-ORG.koncernmoder' not in b.forslag()
