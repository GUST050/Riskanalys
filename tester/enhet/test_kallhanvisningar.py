"""Källnumrering utgår från refererat innehåll, aldrig bilagans inventarium."""
import importlib.util
import pytest
from riskanalys.dokument import modeller as m


def modul():
    assert importlib.util.find_spec('riskanalys.dokument.kallhanvisningar'), 'Källupplösning saknas'
    from riskanalys.dokument import kallhanvisningar
    return kallhanvisningar


def dokument():
    tabell = m.Dokumenttabell(id='test', rubrik='Test', kolumner=('Källa',), fore_stycke=0,
                            rader=(m.Tabellrad(celler=(m.Tabellcell(text='Hot', referenser=('H-1',)),)),))
    return m.Dokument(id='D-ARB', titel='Test', avsnitt=(
        m.Avsnitt(id='D-ARB.1', rubrik='Test', kalla='regelbas', formatversion='D-ARB-tjanst-v5', tabeller=(tabell,),
                  stycken=(m.Textstycke(typ='analys', text='Bedömning.', referenser=['H-1', 'OKAND', 'P-A']),)),
        m.Avsnitt(id='D-ARB.B1', rubrik='Bilaga', kalla='regelbas', stycken=(
            m.Textstycke(typ='beskrivning', text='Inventarium', referenser=['SRC-EXTRA']),)),))


def test_bara_refererade_kallor_numreras_och_okanda_refs_bevaras(minimal_regelbas):
    k = modul()
    extra = minimal_regelbas.kallor['SRC-1'].model_copy(update={'id': 'SRC-EXTRA', 'titel': 'Orefererad'})
    rb = minimal_regelbas.model_copy(update={'kallor': minimal_regelbas.kallor | {'SRC-EXTRA': extra}})
    d = dokument()
    assert k.bygg_kallregister(d, rb) == {'SRC-1': '1'}
    nytt = k.med_kallhanvisningar(d, rb)
    text = nytt.avsnitt[0].stycken[0].text
    assert '[1]' in text and 'bilaga B1' in text and 'sida' not in text
    assert nytt.avsnitt[0].stycken[0].referenser == ['H-1', 'OKAND', 'P-A']
    assert '[1]' in nytt.avsnitt[0].tabeller[0].rader[0].celler[0].text
    assert nytt.avsnitt[0].kontrollsumma() != d.avsnitt[0].kontrollsumma()
    assert k.med_kallhanvisningar(nytt, rb) == nytt


def test_explicit_sida_visas_och_numrering_ar_sorterad(minimal_regelbas):
    k = modul()
    from riskanalys.regelverk.modeller import Kallhanvisning
    hot = minimal_regelbas.hot['H-1'].model_copy(update={'kallhanvisningar': (Kallhanvisning(kalla='SRC-1', avsnitt='Risker', sida=7),)})
    rb = minimal_regelbas.model_copy(update={'hot': {'H-1': hot}})
    nytt = k.med_kallhanvisningar(dokument(), rb)
    assert '[1, s. 7]' in nytt.avsnitt[0].stycken[0].text
    extra = rb.kallor['SRC-1'].model_copy(update={'id': 'AAA'})
    rb = rb.model_copy(update={'kallor': rb.kallor | {'AAA': extra},
                              'hot': {'H-1': hot.model_copy(update={'kallor': ('SRC-1', 'AAA')})}})
    assert k.bygg_kallregister(dokument(), rb) == {'AAA': '1', 'SRC-1': '2'}


def test_aldre_format_forblir_oforandrat(minimal_regelbas):
    k = modul()
    d = m.Dokument(id='D', titel='Test', avsnitt=(m.Avsnitt(id='D.1', rubrik='Test', kalla='regelbas', stycken=(
        m.Textstycke(typ='analys', text='Test.', referenser=['H-1']),)),))
    assert k.med_kallhanvisningar(d, minimal_regelbas) == d


@pytest.mark.parametrize(('version', 'forvantad'), [
    ('D-ARB-tjanst-v5', {'SRC-1': set()}),
    ('D-ARB-tjanst-v5.1', {'SRC-1': set()}),
    ('D-ARB-tjanst-v6', {}),
])
def test_tjanstens_katalogkalla_foljs_bara_i_historiska_format(minimal_regelbas, version, forvantad):
    k = modul()
    assert k._kallor(['T-1'], minimal_regelbas, k._poster(minimal_regelbas), formatversion=version) == forvantad


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v5', 'D-ARB-tjanst-v5.1', 'D-ARB-tjanst-v6'])
def test_samma_suffix_i_foljd_kortas_bara_i_v6_och_referenser_bevaras(minimal_regelbas, version):
    k = modul()
    refs = (['H-1', 'P-A'], ['H-1', 'P-A'], ['H-1', 'P-A'], [], ['H-1', 'P-A'], ['H-1'])
    stycken = tuple(m.Textstycke(typ='analys', text=f'Analys {nr}.', referenser=r) for nr, r in enumerate(refs))
    avsnitt = tuple(m.Avsnitt(id=f'D-ARB.{nr}', rubrik='Analys', kalla='regelbas',
        formatversion=version, stycken=stycken) for nr in (1, 2))
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=avsnitt)
    nytt = k.med_kallhanvisningar(d, minimal_regelbas)
    for a in nytt.avsnitt[:2]:
        assert [s.referenser for s in a.stycken] == list(refs)
        assert [k.utan_kallhanvisning(s.text, genererad_etikett=(
            ' Gemensamma hänvisningar inom avsnittet.' if version.endswith('v6') and i == 0 else ''))
            for i, s in enumerate(a.stycken)] == [s.text for s in stycken]
        assert ['Källor:' in s.text for s in a.stycken] == (
            [True, False, False, False, False, False] if version.endswith('v6')
            else [True, True, True, False, True, True])
    assert k.med_kallhanvisningar(nytt, minimal_regelbas) == nytt


def test_v6_kallregister_bevarar_hotkalla_men_inte_enbart_tjanstinventarium(minimal_regelbas):
    k = modul()
    def bygg(refs):
        return m.Dokument(id='D-ARB', titel='Test', avsnitt=(m.Avsnitt(id='D-ARB.1', rubrik='Analys',
            kalla='regelbas', formatversion='D-ARB-tjanst-v6', stycken=(
                m.Textstycke(typ='analys', text='Analys.', referenser=refs),)),))
    assert k.bygg_kallregister(bygg(['T-1']), minimal_regelbas) == {}
    assert k.bygg_kallregister(bygg(['T-1', 'H-1']), minimal_regelbas) == {'SRC-1': '1'}


def test_v6_nya_sidor_och_profilbelagg_visas_utan_att_tidigare_sidor_upprepas(minimal_regelbas):
    from riskanalys.regelverk.modeller import Kallhanvisning
    k = modul()
    hot = {f'H-{n}': minimal_regelbas.hot['H-1'].model_copy(update={'id': f'H-{n}',
        'kallhanvisningar': (Kallhanvisning(kalla='SRC-1', avsnitt='Risker', sida=sida),)})
        for n, sida in enumerate((7, 8, 7), 1)}
    rb = minimal_regelbas.model_copy(update={'hot': hot})
    refs = (['H-1'], ['H-2'], ['H-3', 'P-A'], ['H-1', 'P-A'])
    a = m.Avsnitt(id='D-ARB.1', rubrik='Analys', kalla='regelbas', formatversion='D-ARB-tjanst-v6',
        stycken=tuple(m.Textstycke(typ='analys', text=f'Analys {n}.', referenser=r) for n, r in enumerate(refs)))
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=(a,))
    nytt = k.med_kallhanvisningar(d, rb)
    texter = [s.text for s in nytt.avsnitt[0].stycken]
    assert '[1, s. 7]' in texter[0] and 'Gemensamma hänvisningar inom avsnittet.' in texter[0]
    assert '[1, s. 8]' in texter[1] and 's. 7' not in texter[1]
    assert 'Profilbelägg: bilaga B1.' in texter[2] and 'Källor:' not in texter[2]
    assert texter[3] == 'Analys 3.'
    assert [s.referenser for s in nytt.avsnitt[0].stycken] == list(refs)
    assert k.med_kallhanvisningar(nytt, rb) == nytt


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v5', 'D-ARB-tjanst-v5.1'])
def test_historisk_forfattartext_tolkats_inte_som_ny_hanvisningsetikett(minimal_regelbas, version):
    k = modul()
    text = 'Byråns kommentar. Gemensamma hänvisningar inom avsnittet.'
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=(m.Avsnitt(id='D-ARB.1', rubrik='Analys',
        kalla='regelbas', formatversion=version, stycken=(
            m.Textstycke(typ='analys', text=text, referenser=['H-1']),)),))
    nytt = k.med_kallhanvisningar(d, minimal_regelbas)
    assert nytt.avsnitt[0].stycken[0].text == text + ' Källor: [1].'


@pytest.mark.parametrize('etikett', ['Hänvisningar.', 'Gemensamma hänvisningar inom avsnittet.'])
def test_egen_slutmening_utan_genererat_suffix_bevaras(etikett):
    text = 'Författad analys. ' + etikett
    assert modul().utan_kallhanvisning(text) == text


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v6', 'D-ARB-tjanst-v7'])
@pytest.mark.parametrize('etikett', ['Hänvisningar.', 'Gemensamma hänvisningar inom avsnittet.'])
@pytest.mark.parametrize('refs', [[], ['H-1'], ['P-A'], ['H-1', 'P-A']])
def test_forfattad_slutmening_och_genererade_suffix_roundtrip(minimal_regelbas, version, etikett, refs):
    k = modul()
    text = 'Författad analys. ' + etikett
    tabell = m.Dokumenttabell(id='test', rubrik='Test', kolumner=('Analys',), fore_stycke=0,
        rader=(m.Tabellrad(celler=(m.Tabellcell(text=text, referenser=tuple(refs)),)),))
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=(
        m.Avsnitt(id='D-ARB.1', rubrik='Stycke', kalla='regelbas', formatversion=version,
            stycken=(m.Textstycke(typ='analys', text=text, referenser=refs),)),
        m.Avsnitt(id='D-ARB.2', rubrik='Cell', kalla='regelbas', formatversion=version,
            stycken=(), tabeller=(tabell,)),))
    nytt = k.med_kallhanvisningar(d, minimal_regelbas)
    stycke = nytt.avsnitt[0].stycken[0]
    cell = nytt.avsnitt[1].tabeller[0].rader[0].celler[0]
    for post in (stycke, cell):
        assert post.text.startswith(text)
        genererad = (' Hänvisningar.' if version.endswith('v7') else ' Gemensamma hänvisningar inom avsnittet.') if refs else ''
        assert k.utan_kallhanvisning(post.text, genererad_etikett=genererad) == text
        assert ('Källor:' in post.text) == ('H-1' in refs)
        assert ('Profilbelägg: bilaga B1.' in post.text) == ('P-A' in refs)
        assert tuple(post.referenser) == tuple(refs)
    assert k.med_kallhanvisningar(nytt, minimal_regelbas) == nytt


@pytest.mark.parametrize('etikett', ['Hänvisningar.', 'Gemensamma hänvisningar inom avsnittet.'])
def test_stringhelper_bevarar_egen_etikett_fore_kallsuffix_utan_genererad_kontext(etikett):
    original = 'Författad analys. ' + etikett
    assert modul().utan_kallhanvisning(original + ' Källor: [1].') == original


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v6', 'D-ARB-tjanst-v7'])
@pytest.mark.parametrize('etikett', ['Hänvisningar.', 'Gemensamma hänvisningar inom avsnittet.'])
@pytest.mark.parametrize('plats', ['senare_stycke', 'forsta_cell', 'senare_rad', 'annan_cell'])
@pytest.mark.parametrize('refs', [['SRC-2'], ['P-A'], ['SRC-2', 'P-A']])
def test_senare_hanvisning_bevarar_egen_etikett_och_ar_idempotent(minimal_regelbas, version, etikett, plats, refs):
    k = modul()
    extra = minimal_regelbas.kallor['SRC-1'].model_copy(update={'id': 'SRC-2'})
    rb = minimal_regelbas.model_copy(update={'kallor': {**minimal_regelbas.kallor, 'SRC-2': extra}})
    original = 'Författad analys. ' + etikett
    tidigare = m.Textstycke(typ='analys', text='Första analysen.', referenser=['SRC-1'])
    mal = m.Textstycke(typ='analys', text=original, referenser=refs)
    stycken = (tidigare, mal) if plats == 'senare_stycke' else (tidigare,)
    rader = ()
    if plats != 'senare_stycke':
        celler = (m.Tabellcell(text=original, referenser=tuple(refs)),)
        if plats == 'annan_cell':
            celler = (m.Tabellcell(text='Radrubrik.'), *celler)
        rader = (m.Tabellrad(celler=celler),)
        if plats == 'senare_rad':
            rader = (m.Tabellrad(celler=(m.Tabellcell(text='Tidigare rad.', referenser=('SRC-1',)),)), *rader)
    tabeller = (m.Dokumenttabell(id='test', rubrik='Test', kolumner=('Analys', 'Kommentar') if plats == 'annan_cell' else ('Analys',),
        fore_stycke=1, rader=rader),) if rader else ()
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=(m.Avsnitt(id='D-ARB.1', rubrik='Analys',
        kalla='regelbas', formatversion=version, stycken=stycken, tabeller=tabeller),))
    nytt = k.med_kallhanvisningar(d, rb)
    a = nytt.avsnitt[0]
    post = a.stycken[1] if plats == 'senare_stycke' else a.tabeller[0].rader[-1].celler[-1]
    assert post.text.startswith(original)
    assert k.med_kallhanvisningar(nytt, rb) == nytt
    assert k.utan_kallhanvisning(post.text) == original
    assert tuple(post.referenser) == tuple(refs)
    radtext = post.text if plats == 'senare_stycke' else ' '.join(c.text for c in a.tabeller[0].rader[-1].celler)
    assert ('Källor: [2].' in radtext) == ('SRC-2' in refs)
    assert ('Profilbelägg: bilaga B1.' in radtext) == ('P-A' in refs)


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v7', 'D-ARB-tjanst-v6'])
def test_bara_v7_reservkatalogens_modellpositioner_far_lasbara_kallnummer_i_word(minimal_regelbas, profil_fabrik, tmp_path, version):
    import docx
    from docx.oxml.ns import qn
    from riskanalys.dokument.rendering import rendera_docx
    k = modul()
    extra = minimal_regelbas.kallor['SRC-1'].model_copy(update={'id': 'SRC-2', 'titel': 'Andra tydliga källan'})
    rb = minimal_regelbas.model_copy(update={'kallor': {**minimal_regelbas.kallor, 'SRC-2': extra}})
    egna = ('Oförändrad första katalogtext. Hänvisningar.',
            'Oförändrad andra katalogtext. Gemensamma hänvisningar inom avsnittet.')
    katalog = tuple(m.Textstycke(typ='beskrivning', text=text, referenser=[f'SRC-{n}', 'T-1', 'D-ARB.6.1'],
        proveniens='regelbas') for n, text in enumerate(egna, 1))
    ovrig = m.Textstycke(typ='beskrivning', text='Katalogunderlag när AI-text saknas. Denna text hör till en annan del.',
        referenser=['SRC-1'], proveniens='regelbas')
    b1 = m.Avsnitt(id='D-ARB.B1', rubrik='Bilaga', kalla='regelbas', formatversion=version,
        stycken=(ovrig, *katalog, ovrig), underrubriker=(
            m.Underrubrik(fore_stycke=0, rubrik='Profiluppgifter'),
            m.Underrubrik(fore_stycke=1, rubrik='Katalogunderlag när AI-text saknas'),
            m.Underrubrik(fore_stycke=3, rubrik='Annan del')))
    d = m.Dokument(id='D-ARB', titel='Test', avsnitt=(m.Avsnitt(id='D-ARB.6.1', rubrik='Analys', kalla='lokal',
        formatversion=version, stycken=(m.Textstycke(typ='analys', text='Reservtext. [VERIFIERA]',
            referenser=['SRC-1', 'SRC-2', 'D-ARB.B1']),)), b1))
    nytt = k.med_kallhanvisningar(d, rb)
    fil = rendera_docx(nytt, profil_fabrik(rb, {}), 'UTKAST', tmp_path / 'reservkallor.docx')
    word = docx.Document(fil)
    synligt = '\n'.join(''.join(t.text or '' for t in p.iter(qn('w:t'))) for p in word.element.body.iter(qn('w:p')))
    for n, text in enumerate(egna, 1):
        kopplad = text + f' Källor: [{n}].'
        if version.endswith('v7'):
            assert kopplad in synligt
        else:
            assert kopplad not in synligt and text in synligt
        titel = rb.kallor[f'SRC-{n}'].titel
        assert f'Källregister [{n}]: {titel}.' in synligt
        post = nytt.avsnitt_med_id()['D-ARB.B1'].stycken[n]
        assert post.referenser == katalog[n-1].referenser and post.proveniens == 'regelbas'
        assert k.utan_kallhanvisning(post.text) == text
    assert nytt.avsnitt_med_id()['D-ARB.B1'].stycken[0] == ovrig
    assert nytt.avsnitt_med_id()['D-ARB.B1'].stycken[3] == ovrig
    assert nytt.avsnitt_med_id()['D-ARB.B1'].underrubriker == b1.underrubriker
    assert k.med_kallhanvisningar(nytt, rb) == nytt
