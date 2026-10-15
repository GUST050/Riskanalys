"""Syntetiskt HVD-kontrakt. Ingen transport får anropa nätverket."""
import io
import json
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.nyckelfil import ladda_nycklar

ORG = '5299999994'  # Syntetisk identitet i myndighetens exempel.
TOKEN = {'access_token': 'syntetisk-token', 'token_type': 'Bearer', 'expires_in': 3600}


def organisation():
    return {'organisationer': [{
        'organisationsidentitet': {'identitetsbeteckning': ORG},
        'organisationsnamn': {'dataproducent': 'Bolagsverket', 'fel': None,
            'organisationsnamnLista': [{'namn': 'Syntetisk byrå AB',
                'organisationsnamntyp': {'kod': 'FORETAGSNAMN', 'klartext': 'Företagsnamn'}}]},
        'organisationsform': {'kod': 'AB', 'klartext': 'Aktiebolag', 'dataproducent': 'Bolagsverket'},
        'verksamhetsbeskrivning': {'beskrivning': 'Syntetisk redovisningsverksamhet.', 'dataproducent': 'Bolagsverket'},
        'verksamOrganisation': {'kod': 'JA', 'dataproducent': 'SCB'},
        'okant_falt': 'ska inte visas',
    }]}


class Transport:
    def __init__(self, *svar):
        self.svar = list(svar)
        self.anrop = []

    def __call__(self, req, timeout):
        self.anrop.append(req)
        assert timeout > 0
        assert self.svar, 'Oväntat extra anrop'
        svar = self.svar.pop(0)
        if isinstance(svar, Exception):
            raise svar
        return io.BytesIO(svar if isinstance(svar, bytes) else json.dumps(svar).encode())


def klient(transport, **kwargs):
    from riskanalys.foretagsdata.bolagsverket import BolagsverketLeverantor
    return BolagsverketLeverantor('syntetisk-id', 'syntetisk-secret', transport=transport, **kwargs)


def test_nyckelfilen_laddar_bada_bolagsverksuppgifterna(tmp_path):
    p = tmp_path / '.env'
    p.write_text('BOLAGSVERKET_CLIENT_ID=test-id\nBOLAGSVERKET_CLIENT_SECRET=test-secret\n')
    p.chmod(0o600)
    miljo = {}
    ladda_nycklar(p, miljo)
    assert miljo == {'BOLAGSVERKET_CLIENT_ID': 'test-id', 'BOLAGSVERKET_CLIENT_SECRET': 'test-secret'}


def test_hamtar_foretag_och_dokument_med_en_token_utan_att_spara_hemligheter():
    tr = Transport(TOKEN, organisation(), {'dokument': [{'dokumentId': 'syntetisk-doc',
        'filformat': 'iXBRL', 'rapporteringsperiodTom': '2025-12-31', 'registreringstidpunkt': '2026-06-01'}]})
    resultat = klient(tr).hamta(ORG)
    assert resultat['organisationer'][0]['organisationsform']['kod'] == 'AB'
    assert resultat['organisationer'][0]['verksamOrganisation']['dataproducent'] == 'SCB'
    assert resultat['dokument'][0]['rapporteringsperiodTom'] == '2025-12-31'
    assert resultat['orgnr'] == ORG
    assert resultat['hamtad']
    assert len(tr.anrop) == 3
    assert parse_qs(tr.anrop[0].data.decode()) == {
        'grant_type': ['client_credentials'], 'client_id': ['syntetisk-id'],
        'client_secret': ['syntetisk-secret'], 'scope': ['vardefulla-datamangder:read']}
    assert tr.anrop[0].full_url == 'https://portal.api.bolagsverket.se/oauth2/token'
    for req, path in zip(tr.anrop[1:], ('organisationer', 'dokumentlista')):
        assert req.full_url == 'https://gw.api.bolagsverket.se/vardefulla-datamangder/v1/' + path
        assert req.get_header('Authorization') == 'Bearer syntetisk-token'
        assert json.loads(req.data) == {'identitetsbeteckning': ORG}
    text = json.dumps(resultat)
    assert 'syntetisk-token' not in text and 'syntetisk-secret' not in text
    assert 'okant_falt' not in text


def test_token_fornyas_nar_giltigheten_tar_slut():
    tid = [0.0]
    tr = Transport(TOKEN, organisation(), {'dokument': []}, TOKEN, organisation(), {'dokument': []})
    k = klient(tr, klocka=lambda: tid[0])
    k.hamta(ORG)
    tid[0] = 3601
    k.hamta(ORG)
    assert sum(r.full_url.endswith('/token') for r in tr.anrop) == 2


def test_401_pa_data_fornyar_token_en_gang():
    tr = Transport(TOKEN, HTTPError('url', 401, 'hemligt', {}, None), TOKEN, organisation(), {'dokument': []})
    assert klient(tr).hamta(ORG)['orgnr'] == ORG
    assert len(tr.anrop) == 5


def test_upprepad_401_stannar_efter_en_fornyelse():
    tr = Transport(TOKEN, HTTPError('url', 401, '', {}, None), TOKEN, HTTPError('url', 401, '', {}, None))
    with pytest.raises(RiskanalysFel, match='autentiseringen'):
        klient(tr).hamta(ORG)
    assert len(tr.anrop) == 4


def test_403_pa_data_fornyar_inte_token():
    tr = Transport(TOKEN, HTTPError('url', 403, '', {}, None))
    with pytest.raises(RiskanalysFel, match='åtkomst'):
        klient(tr).hamta(ORG)
    assert len(tr.anrop) == 2


@pytest.mark.parametrize('svar', [{}, {'dokument': None}, {'dokument': [{}]}, {'dokument': [{'dokumentId': 123}]}])
def test_felaktig_dokumentlista_blir_inte_tom_lista(svar):
    with pytest.raises(RiskanalysFel, match='dokumentlista'):
        klient(Transport(TOKEN, organisation(), svar)).hamta(ORG)


def test_saknad_nyckel_anropar_inte_natverket(monkeypatch):
    from riskanalys.foretagsdata.bolagsverket import BolagsverketLeverantor
    monkeypatch.delenv('BOLAGSVERKET_CLIENT_ID', raising=False)
    monkeypatch.delenv('BOLAGSVERKET_CLIENT_SECRET', raising=False)
    tr = Transport()
    with pytest.raises(RiskanalysFel, match='nyckelfilen'):
        BolagsverketLeverantor(transport=tr).hamta(ORG)
    assert not tr.anrop


@pytest.mark.parametrize('fel', [HTTPError('url', c, 'syntetisk-secret', {}, None) for c in (400, 401, 403, 429, 500)] + [URLError('syntetisk-secret')])
def test_fel_ar_begripliga_utan_hemligheter_eller_anropsstorm(fel):
    tr = Transport(fel)
    with pytest.raises(RiskanalysFel, match='Bolagsverket') as e:
        klient(tr).hamta(ORG)
    assert 'syntetisk-secret' not in str(e.value)
    assert len(tr.anrop) == 1


@pytest.mark.parametrize('token', [{}, {'access_token': 'x\ny', 'expires_in': 10, 'token_type': 'Bearer'},
    {**TOKEN, 'expires_in': -1}, {**TOKEN, 'expires_in': True}, {**TOKEN, 'token_type': 'Other'}, []])
def test_felaktig_token_stoppas_fore_dataanrop(token):
    tr = Transport(token)
    with pytest.raises(RiskanalysFel):
        klient(tr).hamta(ORG)
    assert len(tr.anrop) == 1


@pytest.mark.parametrize('svar', [{'organisationer': []}, {'organisationer': [{'organisationsidentitet': {'identitetsbeteckning': 'fel'}}]}, [], {'organisationer': 'fel'}])
def test_identitetsfel_eller_saknat_foretag_stoppas(svar):
    tr = Transport(TOKEN, svar)
    with pytest.raises(RiskanalysFel):
        klient(tr).hamta(ORG)
    assert len(tr.anrop) == 2


def test_delfel_visas_som_fel_inte_som_saknade_risker():
    data = organisation()
    data['organisationer'][0]['verksamhetsbeskrivning'] = {'fel': {'typ': 'TIMEOUT', 'felBeskrivning': 'intern hemlig text'}, 'beskrivning': 'opålitlig text'}
    r = klient(Transport(TOKEN, data, {'dokument': []})).hamta(ORG)
    assert r['organisationer'][0]['verksamhetsbeskrivning'] == {'status': 'uppgiftsfel'}
    assert 'opålitlig' not in json.dumps(r) and 'intern hemlig' not in json.dumps(r)


@pytest.mark.parametrize('raw', [b'not json', b'x' * 1048577], ids=['olastbart', 'for-stort'])
def test_olastbart_eller_for_stort_svar_stoppas(raw):
    with pytest.raises(RiskanalysFel):
        klient(Transport(TOKEN, raw)).hamta(ORG)


@pytest.mark.parametrize('orgnr', ['199001011234', 'abc', '5299999995'])
def test_personnummer_och_ogiltiga_nummer_anropas_inte(orgnr):
    tr = Transport()
    with pytest.raises(RiskanalysFel):
        klient(tr).hamta(orgnr)
    assert not tr.anrop


def test_omdirigering_ska_inte_vidarebefordra_hemligheten():
    from riskanalys.foretagsdata.bolagsverket import IngaOmdirigeringar
    assert IngaOmdirigeringar().redirect_request(None, None, 302, '', {}, 'https://example.invalid') is None


def test_cli_visar_resultat_utan_att_skapa_profil(monkeypatch, tmp_path, capsys):
    from riskanalys.cli import main
    from riskanalys.foretagsdata import bolagsverket
    monkeypatch.setenv('BOLAGSVERKET_CLIENT_ID', 'syntetisk-id')
    monkeypatch.setenv('BOLAGSVERKET_CLIENT_SECRET', 'syntetisk-secret')
    monkeypatch.setenv('RISKANALYS_DATA', str(tmp_path))
    monkeypatch.setattr(bolagsverket, 'transport', Transport(TOKEN, organisation(), {'dokument': []}))
    assert main(['bolagsverket', ORG]) == 0
    out = capsys.readouterr().out
    assert 'Syntetisk byrå AB' in out and 'Inga profilsvar' in out
    assert 'syntetisk-secret' not in out
    assert not list(tmp_path.iterdir())


def test_tomma_sni_rader_filtreras():
    from riskanalys.foretagsdata.bolagsverket_svar import tolka_organisationer
    data=organisation()
    data['organisationer'][0]['naringsgrenOrganisation']={'sni':[{'kod':'     ','klartext':''},{'kod':'69201','klartext':'Test'}]}
    assert tolka_organisationer(data,ORG)[0]['naringsgrenOrganisation']['sni']==[{'kod':'69201','klartext':'Test'}]


def test_zip_hamtas_som_bytes_med_urlkodad_identitet_och_401_fornyelse():
    tr=Transport(TOKEN,HTTPError('url',401,'',{},None),TOKEN,b'PKsyntetisk')
    raw=klient(tr).hamta_dokument('id/med mellanslag')
    assert raw==b'PKsyntetisk'
    assert tr.anrop[-1].full_url.endswith('/dokument/id%2Fmed%20mellanslag')
    assert tr.anrop[-1].get_method()=='GET'


def test_for_stort_dokument_avvisas():
    tr=Transport(TOKEN,b'x'*(20*1024*1024+1))
    with pytest.raises(RiskanalysFel,match='stort'):klient(tr).hamta_dokument('doc')
