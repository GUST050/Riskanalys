import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from riskanalys.analys import modeller as m
from riskanalys.analys.provning import registersumma, summa


def gammal_data():
    return json.loads((Path(__file__).parents[1]/'fixturer/rapportlasprov_bas.json').read_text())['analys']


def test_schema_ett_bevarar_hela_serialiseringen_och_summan():
    data = gammal_data()
    p = m.Analyspaket.model_validate(data)
    assert p.model_dump(mode='json') == data
    assert registersumma(p) == summa(data)


def test_schema_tva_ar_uttryckligt_och_frozen():
    p = m.Analyspaket.model_validate({**gammal_data(), 'schemaversion': 2})
    assert p.schemaversion == 2
    assert p.model_dump(mode='json')['gemensamma_sarbarhetsprovningar'] == []
    assert p.model_dump(mode='json')['tjanster'][0]['tackningsprovningar'] == []
    with pytest.raises(ValidationError):
        p.schemaversion = 1


def test_schema_tva_respekterar_begransad_serialisering():
    p=m.Analyspaket.model_validate({**gammal_data(),'schemaversion':2})
    assert 'tjanster' not in p.model_dump(exclude={'tjanster'})
    assert p.model_dump(include={'schemaversion'})=={'schemaversion':2}


def test_schema_ett_far_inte_innehalla_nya_svar():
    data = {**gammal_data(), 'gemensamma_sarbarhetsprovningar': [dict(id='egen', omrade='kund', beskrivning='Egen risk')]}
    with pytest.raises(ValidationError):
        m.Analyspaket.model_validate(data)


def test_nya_referenser_ar_unika_och_tackning_borjar_som_oklar():
    post = m.GemensamSarbarhetsprovning(id='kund', omrade='kund')
    with pytest.raises(ValidationError):
        m.Analyspaket.model_validate({**gammal_data(), 'schemaversion':2,
            'gemensamma_sarbarhetsprovningar':[post.model_dump(),post.model_dump()]})
    prov = m.Tackningsprovning(ursprung='lokal', post='egen', hot='H-03', dimension='pt')
    assert prov.stallningstagande == 'oklar' and prov.visad_summa is None
    assert m.Riktningsval().riktning == 'oklar'
