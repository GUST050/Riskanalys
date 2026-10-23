"""Samlad sakgranskning av exakt visad R-struktur; ingen attest av A/B1."""
from datetime import date
import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg


def presentation(f):
    from riskanalys.dokument.presentation_v9 import bygg_presentation_v9
    b=bygg(f)
    return b.dokument,bygg_presentation_v9(b,analys=f.analys,fynd=(),bedomning=f.bedomning,profil=f.profil)


def test_samlad_r_granskning_omfattar_exakt_alla_r_avsnitt(resultatfall):
    from riskanalys.faststallelse.resultatgranskning import registrera_resultatgranskning
    from riskanalys.faststallelse.sakgranskning import struktur_summa,galler_sakgranskning
    f=resultatfall;d,p=presentation(f)
    poster=registrera_resultatgranskning((),d,f.profil,presentation=p,visad_struktursumma=struktur_summa(d,presentation=p),
        analysbindning='syntetisk-bindning',godkand=True,roll='FfR',namn='Syntetisk',datum=date(2026,10,23))
    assert tuple(x.avsnitt for x in poster)==tuple(a.id for a in d.avsnitt if a.leveransdel=='resultatrapport')
    assert all(galler_sakgranskning(poster,a,f.profil,d,analysbindning='syntetisk-bindning',presentation=p) is None for a in d.avsnitt if a.leveransdel!='resultatrapport')
    # Ändring av presentation gör också tidigare R-attester ogiltiga.
    annan=p.model_copy(update={'version':'ändrad'})
    assert all(galler_sakgranskning(poster,a,f.profil,d,analysbindning='syntetisk-bindning',presentation=annan) is None for a in d.avsnitt)


def test_andrad_analys_efter_visning_sparar_inga_r_attester(resultatfall):
    from riskanalys.faststallelse.resultatgranskning import registrera_resultatgranskning
    from riskanalys.fel import RiskanalysFel
    f=resultatfall;d,p=presentation(f)
    with pytest.raises(RiskanalysFel,match='visad|ändrat|Läs'):
        registrera_resultatgranskning((),d,f.profil,presentation=p,visad_struktursumma='gammal',
            analysbindning='syntetisk-bindning',godkand=True,roll='FfR',namn='Syntetisk',datum=date(2026,10,23))


def test_formathinder_provar_sparat_format_och_inte_ny_standard(resultatfall,monkeypatch):
    from riskanalys.faststallelse.faststall import formathinder
    from riskanalys.dokument import rapportversion
    f=resultatfall;d,p=presentation(f)
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V9)
    assert formathinder(f.regelbas,d)==[]
    assert formathinder(f.regelbas,f.dokument)==[]
    a=d.avsnitt_med_id()['D-ARB.6.1'].model_copy(update={'formatversion':rapportversion.V8})
    mixed=d.model_copy(update={'avsnitt':tuple(a if x.id==a.id else x for x in d.avsnitt)})
    assert formathinder(f.regelbas,mixed)


def test_v8_attester_galler_inte_for_v9_struktur(resultatfall):
    from riskanalys.dokument.presentation_v8 import bygg_presentation
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,galler_sakgranskning
    f=resultatfall;d,p=presentation(f);old=f.dokument
    p8=bygg_presentation(old,analys=f.analys,fynd=(),bedomning=f.bedomning,profil=f.profil)
    a=old.avsnitt[0];poster=registrera_sakgranskning((),old,f.profil,a.id,True,'FfR','Syntetisk',date(2026,10,23),presentation=p8)
    assert galler_sakgranskning(poster,d.avsnitt_med_id()[a.id],f.profil,d,presentation=p) is None
