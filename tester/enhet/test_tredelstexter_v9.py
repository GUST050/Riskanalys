"""Kända tvådelsprogramtexter får inte läcka från V8 till V9."""
import re
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg

TVA=re.compile(r'\b(?:läsrapport(?:en)?|båda delar(?:na)?)\b',re.I)


def test_all_synlig_v9_programtext_ar_tredelad(resultatfall):
    b=bygg(resultatfall)
    for a in b.dokument.avsnitt:
        assert not TVA.search(a.rubrik)
        for s in a.stycken:
            # Hela lokala/AI-original och explicit markerade originalspann undantas.
            if s.proveniens=='ai':continue
            text=s.text
            for start,slut in sorted(s.literala_spann,reverse=True):text=text[:start]+text[slut:]
            assert not TVA.search(text),(a.id,text)
        for t in a.tabeller:
            assert not TVA.search(t.rubrik)
            for rad in t.rader:
                for c in rad.celler:
                    text=c.text
                    for start,slut in sorted(getattr(c,'literala_spann',()),reverse=True):text=text[:start]+text[slut:]
                    assert not TVA.search(text),(a.id,text)


def test_tredelsundantag_bevarar_byrans_egna_original(resultatfall,monkeypatch):
    from riskanalys.dokument import arb_v9
    from riskanalys.dokument.modeller import Textstycke
    from riskanalys.dokument.radata_v8 import komplettera_radata
    orig=resultatfall.dokument;a=orig.avsnitt_med_id()['D-ARB.B1']
    text='Läsrapport och kompletterande underlagsbilaga utgör tillsammans hela riskbedömningens dokumentation.'
    s=Textstycke(typ='analys',text=text,referenser=[],proveniens='lokal',literala_spann=((0,len(text)),))
    a=a.model_copy(update={'stycken':(*a.stycken,s)})
    monkeypatch.setattr(arb_v9,'bygg_arb_v8',lambda *args,**kwargs:orig.model_copy(update={'avsnitt':tuple(a if x.id==a.id else x for x in orig.avsnitt)}))
    assert bygg(resultatfall).dokument.avsnitt_med_id()[a.id].stycken[-1]==s
