"""Redaktionell vy prövas mot de faktiska frysta källorna; ingen produktkod ändras."""
from copy import deepcopy
import json
from pathlib import Path
import pytest

BAS=Path(__file__).parents[1]/'fixturer/redaktionell_v10_d8a91a1.json.gz'

@pytest.fixture(scope='module')
def data():
    import gzip
    d=json.loads(gzip.decompress(BAS.read_bytes()))
    return d['kallor'],d['presentation']

def test_svenska_faltvarden_period_och_roll(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;f=Lasformat(k)
    assert f.varde('P-VERK.omsattning')=='5,4 mnkr'
    assert f.varde('P-KUND.antal_aktiva')=='120'
    assert f.varde('P-ROLL.ffr_namn')=='Funktionen för regelefterlevnad'
    assert '2026-01-01–2026-09-30' in f.fakta('P-VERK.antal_rapporter')
    assert 'Antal egna misstankerapporter: 0' in f.fakta('P-VERK.antal_rapporter')
    assert f.ord('kan_tala_for_lagre')=='kan tala för lägre risk'
    assert f.ord('ej_granskad')=='ej sakkunniggranskad'
    assert f.ord('bada')=='PT och TF'

def test_programprosa_ar_inte_enumvarden(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;f=Lasformat(k)
    assert f.program('Ingen bärande reduktion. En kund har full insyn.')=='Ingen bärande reduktion. En kund har full insyn.'

def test_katalogkod_med_foregaende_namn_ar_redan_lasbar(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;f=Lasformat(k)
    assert f.program('Bankavstämning mot underlag (C-07)')=='Bankavstämning mot underlag (C-07)'

def test_scenariocell_upprepar_inte_redan_angivet_hotnamn(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;f=Lasformat(k)
    text='R4-1 Oförklarade in- och utflöden PT\nH-03'
    assert f.program(text)=='scenario 1 Oförklarade in- och utflöden PT\nH-03'
    text='R4-1 H-03 PT\nOförklarade in- och utflöden'
    assert f.program(text)=='scenario 1 H-03 PT\nOförklarade in- och utflöden'

def test_samtliga_kodord_med_understreck_upptacks():
    from docs.research.verktyg.redaktionell_v10 import ravarden,ORD
    assert all(ravarden(x) for x in ORD if '_' in x)

def test_kallkoder_visas_som_titlar_och_originalet_bevaras_i_b1(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,synlig_text,ravarden
    k,p=data;r=bygg(k,p);text=synlig_text(r['renderade'][0]);b1=synlig_text(r['renderade'][2])
    assert not any(id in text for id in k['regelbas']['kallor'])
    assert ravarden('SRC-TS-2026-14')
    assert k['regelbas']['kallor']['SRC-TS-2026-14']['titel'] in text
    assert k['profil']['uppgifter']['P-BEVAKNING.kallor']['varde'] in b1

def test_offline_bevarar_kallor_original_och_sankningar(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,verifiera_flyttar,synlig_text,ravarden
    k,p=data;fore=json.dumps([k,p],sort_keys=True)
    r=bygg(k,p);text=synlig_text(r['renderade'][0]);allt=synlig_text(r['renderade'])
    assert not ravarden(text)
    assert '5,4 mnkr' in text and '5400000.0' not in text
    assert 'Gemensam bedömning för kunder' in text
    assert 'inte godtagen' in text and 'Sänkningen hög → måttlig' in text
    for a in k['analys']['tjanster']:
        assert a['pt_motivering'] in allt and a['tf_motivering'] in allt
    assert verifiera_flyttar(p,r)==[]
    assert json.dumps([k,p],sort_keys=True)==fore

def test_andrat_flyttmal_avvisas(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,verifiera_flyttar,satt_pointer
    k,p=data;r=bygg(k,p);t=next(t for t in r['transformationer'] if t['typ']=='flytt')
    satt_pointer(r,t['mal'],'Borttappat original')
    assert verifiera_flyttar(p,r)

def test_fritext_med_tekniska_ord_skrivs_aldrig_om(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;k=deepcopy(k);v='Ordagrant P-KUND.antal_aktiva; K1 byra:kund och {roll:FfR}.'
    k['profil']['uppgifter']['P-BESK.verksamhet']['varde']=v
    assert Lasformat(k).varde('P-BESK.verksamhet')==v

def test_nya_kataloghot_flyttas_till_gemensam_matris(data):
    from docs.research.verktyg.redaktionell_v10 import bygg
    k,p=data;r=bygg(k,p)
    rows=[t for a in r['renderade'][0]['avsnitt'] if a['id']=='D-ARB.R4.2' for t in a['tabeller'] if t['id']=='red-katalogscenarier']
    assert len(rows)==1 and len(rows[0]['rader'])==4
    assert len(r['scenariomedlemskap'])==16
    assert all(len(x['tjanster'])==4 for x in r['scenariogrupper'])

def test_lokal_variant_far_inte_grupperas(data):
    from docs.research.verktyg.redaktionell_v10 import bygg
    k,p=deepcopy(data);k['analys']['tjanster'][0]['scenarier'].append({'id':'egen','hot':['H-MOD-06'],
        'handelseforlopp':'En faktisk egen variant','relevans':'relevant','motivering':'Belagd variant'})
    r=bygg(k,p)
    assert not any(g['hot']=='H-MOD-06' for g in r['scenariogrupper'])

def test_olika_avgorande_status_far_inte_grupperas(data):
    from docs.research.verktyg.redaktionell_v10 import bygg
    k,p=deepcopy(data)
    sc=next(s for s in k['bedomning']['tjanster'][1]['scenarier'] if s['hot']=='H-MOD-06')
    sc['avgorande']=False
    r=bygg(k,p)
    assert not any(g['hot']=='H-MOD-06' for g in r['scenariogrupper'])

def test_insyn_och_mandat_har_skilda_ord(data):
    from docs.research.verktyg.redaktionell_v10 import Lasformat
    k,_=data;f=Lasformat(k)
    assert f.varde('P-TJ.red04_bankinsyn')=='ingen insyn'
    assert f.varde('P-TJ.red04_betalningsmandat')=='inget mandat'

def test_aven_rubriker_och_hanvisningar_saknar_interna_id(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,synlig_text,ravarden
    k,p=data;text=synlig_text(bygg(k,p)['renderade'][0])
    assert 'T-RED-' not in text and 'D-ARB.' not in text
    assert ravarden('T-RED-01') and ravarden('D-ARB.E17')

def test_faktaperioder_hamtas_fran_varje_falt(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,synlig_text
    k,p=deepcopy(data)
    k['profil']['uppgifter']['P-RISK.nara_relation']['period']={'fran':'2025-01-01','till':'2025-12-31'}
    a=next(a for a in bygg(k,p)['renderade'][0]['avsnitt'] if a['id']=='D-ARB.R3.1')
    assert '2025-01-01–2025-12-31' in synlig_text({'avsnitt':[a]})

def test_kontrolltabell_omfattar_aven_sankta_scenarier_under_max(data):
    from docs.research.verktyg.redaktionell_v10 import bygg,synlig_text
    k,p=data
    a=next(a for a in bygg(k,p)['renderade'][0]['avsnitt'] if a['id']=='D-ARB.R4.4')
    text=synlig_text({'avsnitt':[a]})
    for t in k['bedomning']['tjanster']:
        if not t['erbjuds']:continue
        for s in t['scenarier']:
            if not s['tackande_kontroller']:continue
            for c in s['tackande_kontroller']:assert k['regelbas']['kontroller'][c]['namn'] in text
            assert k['regelbas']['hot'][s['hot']]['namn'] in text
    assert 'måttlig → låg' in text and '4.3.1' in text
