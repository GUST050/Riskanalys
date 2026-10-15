"""Källnumrering utgår från refererat innehåll, aldrig bilagans inventarium."""
import importlib.util
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
