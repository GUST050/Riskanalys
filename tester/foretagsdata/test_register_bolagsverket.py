"""Samlad registerbild bevarar SCB-källor och gamla checksummor."""
from datetime import datetime, timezone
import json
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.scb import tolka_scb
from tester.foretagsdata.test_scb import ORG, post
from tester.foretagsdata.test_arsredovisning import paket


def bv(form='AB'):
    return {'orgnr':ORG,'hamtad':datetime.now(timezone.utc).isoformat(),'organisationer':[{
        'organisationsform':{'kod':form,'dataproducent':'Bolagsverket'},
        'verksamhetsbeskrivning':{'beskrivning':'Syntetisk redovisningsverksamhet.'},
        'organisationsnamn':{'organisationsnamnLista':[{'namn':'Syntetisk byrå AB','organisationsnamntyp':{'kod':'FORETAGSNAMN'}}]},
    }], 'dokument':[{'dokumentId':'doc','rapporteringsperiodTom':'2024-12-31','filformat':'iXBRL'}]}

class Leverantor:
    def __init__(self,data=None,raw=None):self.data=data or bv();self.raw=raw or paket()
    def hamta(self,orgnr):return self.data
    def hamta_dokument(self,id):return self.raw


def samlad(tmp_path, data=None, raw=None):
    from riskanalys.foretagsdata.samlad import komplettera_bolagsverket
    return komplettera_bolagsverket(tolka_scb(post(),ORG,'scb_api'),Leverantor(data,raw),tmp_path)


def test_samlad_bild_med_kallor_och_privata_original(tmp_path):
    b=samlad(tmp_path)
    assert b.schema_version==4
    assert b.forslag()['P-ORG.utlandsk_filial'] is False
    assert b.forslag()['P-BESK.verksamhet']=='Syntetisk redovisningsverksamhet.'
    assert b.forslag()['P-VERK.omsattning']==1234567
    assert b.bolagsverket.bokslut.medelantal==7
    assert b.faltkalla('P-ORG.namn').startswith('SCB AFR API;')
    assert b.faltkalla('P-VERK.omsattning').startswith('Bolagsverket HVD;')
    files=list(tmp_path.rglob('*.zip'))
    assert len(files)==1 and files[0].read_bytes()==paket()
    assert files[0].stat().st_mode & 0o777 == 0o600

@pytest.mark.parametrize('form,expected',[('AB',False),('FL',True),('HB',None),('',None)])
def test_filial_endast_verifierade_koder(tmp_path,form,expected):
    assert samlad(tmp_path,bv(form)).forslag().get('P-ORG.utlandsk_filial') is expected


def test_olastbart_bokslut_bevarar_register_men_ger_inget_belopp(tmp_path):
    b=samlad(tmp_path,raw=b'inte zip')
    assert 'P-VERK.omsattning' not in b.forslag()
    assert b.bolagsverket.bokslutsnotis
    assert b.forslag()['P-ORG.utlandsk_filial'] is False


def test_fel_bolag_kan_inte_sammanfogas(tmp_path):
    d=bv();d['orgnr']='5299999994'
    with pytest.raises(RiskanalysFel):samlad(tmp_path,d)
    assert not list(tmp_path.rglob('*.zip'))


def test_aldre_bild_bevarar_serialisering():
    from riskanalys.foretagsdata.modeller import Registerbild
    b=tolka_scb(post(),ORG,'scb_api')
    before=b.model_dump_json()
    assert 'bolagsverket' not in json.loads(before)
    assert Registerbild.model_validate_json(before).model_dump_json()==before


def test_flera_dokument_for_senaste_period_ger_inte_gissning(tmp_path):
    d=bv();d['dokument'].append({**d['dokument'][0],'dokumentId':'annat'})
    b=samlad(tmp_path,d)
    assert b.bolagsverket.bokslut is None and b.bolagsverket.bokslutsnotis
