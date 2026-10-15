from datetime import date

import pytest
from pydantic import ValidationError

from riskanalys.dokument import modeller as m
from riskanalys.dokument.rendering import har_verifiera, renderat_avsnitt
from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning, galler_sakgranskning


def tabell(**kwargs):
    assert hasattr(m, 'Dokumenttabell'), 'Lokala typade tabeller saknas'
    return m.Dokumenttabell(**dict(id='TAB-1', rubrik='Kontroller', kolumner=('Kontroll',),
        rader=(m.Tabellrad(celler=(m.Tabellcell(text='Kontrolltext'),)),), fore_stycke=0) | kwargs)


def avsnitt(**kwargs):
    return m.Avsnitt(**dict(id='D-ARB.1', rubrik='Syfte', kalla='regelbas', stycken=(),
        formatversion='D-ARB-tjanst-v5', tabeller=(tabell(),)) | kwargs)


@pytest.mark.parametrize('update', [dict(kolumner=()), dict(kolumner=(' ',)), dict(kolumner=('A','B')), dict(fore_stycke=-1)])
def test_tabell_vagrar_olasbara_eller_felformade_rader(update):
    with pytest.raises(ValidationError):
        tabell(**update)


def test_position_och_id_valideras_aven_utan_prosa():
    a = avsnitt()
    assert a.tabeller[0].fore_stycke == 0
    with pytest.raises(ValidationError):
        avsnitt(tabeller=(tabell(fore_stycke=1),))
    with pytest.raises(ValidationError):
        avsnitt(tabeller=(tabell(),tabell()))
    with pytest.raises(ValidationError):
        avsnitt(formatversion='D-ARB-tjanst-v4')


@pytest.mark.parametrize('version,checksum', [(None,'4fd88e93be98f25c28886e98d131a9b5c4c564338a815935005e9c67929e589b'),
    ('D-ARB-tjanst-v3','a478f9d45e58acec0dfc1a23b53209634290d8e02c35c8057e17f1d6d44f608e'),
    ('D-ARB-tjanst-v4','791ae73de8408502ec4ee9de5d0a17708c49c32fc64610253ca77a6f2dea43be')])
def test_historiska_summor_och_serialisering(version, checksum):
    a = m.Avsnitt(id='D-ARB.1',rubrik='Syfte',kalla='regelbas',stycken=(m.Textstycke(typ='beskrivning',text='Historisk text.',referenser=['K-1']),),formatversion=version)
    expected='{"id":"D-ARB.1","rubrik":"Syfte","kalla":"regelbas","stycken":[{"typ":"beskrivning","text":"Historisk text.","referenser":["K-1"]}],"underrubriker":[]'
    expected += (',"formatversion":"'+version+'"}' if version else '}')
    assert a.model_dump_json() == expected
    assert a.kontrollsumma() == 'sha256:'+checksum


def test_allt_synligt_renderas_och_blockerar(regelbas, profil_fabrik, real_varden):
    profil=profil_fabrik(regelbas, real_varden)
    a=avsnitt(rubrik='{roll:FfR}', tabeller=(tabell(rubrik='{roll:FfR}',kolumner=('{roll:FfR}',),rader=(m.Tabellrad(celler=(m.Tabellcell(text='{roll:Okand}'),)),)),))
    r=renderat_avsnitt(a,profil)
    assert r.rubrik == 'Testa Testsson'
    assert r.tabeller[0].rubrik == 'Testa Testsson'
    assert r.tabeller[0].kolumner == ('Testa Testsson',)
    assert r.tabeller[0].rader[0].celler[0].text == '[VERIFIERA: Okand]'
    assert har_verifiera(a,profil)


def test_andrad_cell_referens_ordning_och_nummer_ogiltigforklarar(regelbas, profil_fabrik, real_varden):
    profil=profil_fabrik(regelbas,real_varden)
    a=avsnitt(tabeller=(tabell(),tabell(id='TAB-2')))
    doc=m.Dokument(id='D-ARB',titel='Test',avsnitt=(a,avsnitt(id='D-ARB.B1',tabeller=())))
    poster=registrera_sakgranskning((),doc,profil,a.id,True,'FfR','Test',date(2026,10,14))
    assert galler_sakgranskning(poster,a,profil,doc)
    for changed in [a.model_copy(update={'visningsnummer':'2'}),a.model_copy(update={'tabeller':tuple(reversed(a.tabeller))}),
        a.model_copy(update={'tabeller':(tabell(rader=(m.Tabellrad(celler=(m.Tabellcell(text='Ny text'),)),)),)}),
        a.model_copy(update={'tabeller':(tabell(rader=(m.Tabellrad(celler=(m.Tabellcell(text='Kontrolltext',referenser=('K-1',)),)),)),)})]:
        assert galler_sakgranskning(poster,changed,profil,doc) is None
    assert galler_sakgranskning(poster,a,profil,doc.model_copy(update={'avsnitt':(a,)})) is None


@pytest.mark.parametrize('location', ['rubrik','visningsnummer','tabellrubrik','kolumn','cell','underrubrik'])
def test_verifieramarkering_i_varje_synlig_yta_stoppar(location,regelbas,profil_fabrik,real_varden):
    profil=profil_fabrik(regelbas,real_varden)
    t=tabell()
    changes={}
    if location in ('rubrik','visningsnummer'):
        changes[location]='{roll:Okand}'
    elif location=='tabellrubrik':
        t=tabell(rubrik='{roll:Okand}')
    elif location=='kolumn':
        t=tabell(kolumner=('{roll:Okand}',))
    elif location=='cell':
        t=tabell(rader=(m.Tabellrad(celler=(m.Tabellcell(text='{roll:Okand}'),)),))
    else:
        changes.update(stycken=(m.Textstycke(typ='analys',text='Text',referenser=[]),),underrubriker=(m.Underrubrik(fore_stycke=0,rubrik='{roll:Okand}'),))
    assert har_verifiera(avsnitt(tabeller=(t,),**changes),profil)
