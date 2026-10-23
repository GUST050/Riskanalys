"""R7: uttryckligt formatval och fulltext även vid långa huvudrapporter."""
import json
import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg


def test_matning_valjer_format_utan_att_byta_analyslage(capsys):
    from docs.research.verktyg.rapportmatning import main
    main(['fyra_tjanster','--analyslage','direkt2','--rapportformat','v9'])
    s=capsys.readouterr().out
    rad=next(x.removeprefix('Mätkontrakt: ') for x in s.splitlines() if x.startswith('Mätkontrakt:'))
    m=json.loads(rad)
    assert m['format']=='D-ARB-resultat-v9' and m['analyslage']=='direkt2' and m['analys_schema']==2
    rad=next(x for x in s.splitlines() if x.startswith('Ord per leveransdel:'))
    assert all(x in rad for x in ('resultatrapport','analysbilaga','underlagsbilaga','totalt'))


def test_langtext_far_varning_utan_trunkering(resultatfall):
    from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
    f=resultatfall;text=f.analys.tjanster[0].pt_motivering+' Dokumenterat långt underlag.'*1800
    t=f.analys.tjanster[0].model_copy(update={'pt_motivering':text})
    a=f.analys.model_copy(update={'tjanster':(t,*f.analys.tjanster[1:])})
    b=bygg_resultatpaket_v9(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,analys=a)
    assert any(text in s.text for av in b.dokument.avsnitt if av.leveransdel=='resultatrapport' for s in av.stycken)
    assert any('Redaktionell längdvarning' in s.text for s in b.dokument.avsnitt[0].stycken)


def test_tomt_utkast_med_v9_standard_byggs_som_v9_och_aldrig_v6(resultatfall,monkeypatch):
    from riskanalys.dokument import rapportversion,arb_v6
    from riskanalys.dokument.arb import bygg_arb
    f=resultatfall
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V9)
    def forbjudet(*a,**kw):pytest.fail('Tomt V9-utkast föll tillbaka till V6')
    monkeypatch.setattr(arb_v6,'bygg_arb_v6',forbjudet)
    d=bygg_arb(f.regelbas,f.profil,f.bedomning,{},f.historik,analys=f.analys)
    assert d.formatversion==rapportversion.V9
    assert any('[VERIFIERA]' in s.text for a in d.avsnitt for s in a.stycken)


def test_nya_granskningar_valjer_v10_men_historiska_paket_bevaras(resultatfall):
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION,V10
    from riskanalys.dokument.skrivversion import AKTUELL_SKRIVVERSION,V8
    from riskanalys.dokument.arb import bygg_arb
    f=resultatfall;fore=f.dokument.model_dump_json()
    assert AKTUELL_DOKUMENTVERSION==V10 and AKTUELL_SKRIVVERSION==V8
    d=bygg_arb(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,analys=f.analys)
    assert d.formatversion==V10
    assert f.dokument.model_dump_json()==fore and f.dokument.formatversion==V8


def test_kompletteringspunkter_ar_stabila_mellan_ordningar(resultatfall,monkeypatch):
    from riskanalys.dokument import arb_v8
    f=resultatfall;ursprung=arb_v8.analysbrister(f.regelbas,f.profil,f.bedomning,f.analys)
    assert len(ursprung)>1
    monkeypatch.setattr(arb_v8,'analysbrister',lambda *a:ursprung)
    fore=bygg(f)
    monkeypatch.setattr(arb_v8,'analysbrister',lambda *a:tuple(reversed(ursprung)))
    efter=bygg(f)
    assert efter==fore
