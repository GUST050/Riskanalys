"""Frivilliga strukturerade fakta, utan inferens från privata beskrivningar."""
import pytest

from riskanalys.fel import RiskanalysFel
from riskanalys.intag.fragor import fragor
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.svar import besvara
from riskanalys.intag.tackning import tackning
from riskanalys.profil.modeller import Uppgift
from tester.fixturer.m2 import DAG
from tester.intag.test_webb import webb, anrop

VAL = {
    'attest': ('kund', 'byra', 'bada', 'okant'),
    'betalningsmandat': ('inget', 'forbereder', 'verkstaller', 'okant'),
    'bankinsyn': ('full', 'delvis', 'ingen', 'okant'),
}


def test_alla_tjansters_fasta_val_ar_frivilliga_och_kallbundna(rb_intag, klar):
    for tj in rb_intag.tjanster.values():
        prefix = tj.erbjuds_falt.removesuffix('_erbjuds')
        for suffix, alternativ in VAL.items():
            f = rb_intag.falt[prefix + '_' + suffix]
            assert f.typ == 'val' and f.val == alternativ
            assert not f.kritisk and not f.intag.obligatorisk
            assert f.intag.grund == 'metodval'
            assert f.intag.kallor == ('SRC-TS-2026-14', 'SRC-14FS-2024-11')
            if tj.id in ('T-RED-08', 'T-RED-09'):
                assert f.id not in rb_intag.tillatelselistor['risk_per_tjanst'].falt
            else:
                assert f.id in rb_intag.tillatelselistor['risk_per_tjanst'].falt
    p = klar.model_copy(update={'uppgifter': {k:u for k,u in klar.uppgifter.items()
        if not any(k.endswith('_' + suffix) for suffix in VAL)}})
    assert tackning(rb_intag, p).komplett


@pytest.mark.parametrize(('suffix', 'varde'), [
    ('attest', 'kund'), ('attest', 'byra'), ('attest', 'bada'), ('attest', 'okant'),
    ('betalningsmandat', 'inget'), ('betalningsmandat', 'forbereder'),
    ('betalningsmandat', 'verkstaller'), ('betalningsmandat', 'okant'),
    ('bankinsyn', 'full'), ('bankinsyn', 'delvis'), ('bankinsyn', 'ingen'), ('bankinsyn', 'okant'),
])
def test_fasta_val_kan_bekraftas(rb_intag, klar, suffix, varde):
    id = 'P-TJ.red01_' + suffix
    p = besvara(rb_intag, klar, IntagSvar(falt=id, text=varde, kalla='Syntetiskt avtal', roll='Ansvarig', datum=DAG))
    assert p.uppgifter[id].varde == varde
    assert p.ar_bekraftad(id)


@pytest.mark.parametrize('suffix', VAL)
def test_fritext_accepteras_inte_som_val(rb_intag, klar, suffix):
    with pytest.raises(RiskanalysFel):
        besvara(rb_intag, klar, IntagSvar(falt='P-TJ.red01_' + suffix, text='kunden betalar själv',
            kalla='Syntetiskt avtal', roll='Ansvarig', datum=DAG))


@pytest.mark.parametrize('erbjudande', [Uppgift(), Uppgift(varde=True, status='bekräftad', inaktuell=True),
    Uppgift(varde=False, status='bekräftad')])
def test_val_doljs_och_kan_inte_besvaras_utan_aktuellt_erbjudande(rb_intag, tom, erbjudande):
    p = tom.model_copy(update={'uppgifter': {**tom.uppgifter, 'P-TJ.red01_erbjuds': erbjudande}})
    assert 'P-TJ.red01_attest' not in {q.falt.id for q in fragor(rb_intag, p)}
    with pytest.raises(RiskanalysFel, match='inte tillämplig'):
        besvara(rb_intag, p, IntagSvar(falt='P-TJ.red01_attest', text='kund', kalla='Avtal', roll='Ansvarig', datum=DAG))


def test_frivilliga_val_nas_i_webboversikt_och_sparas(webb, klar):
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.intag.tjanst import profilrevision
    s, t = webb
    t.skapa('Västra Götaland', False, DAG, 'Syntetisk källa', 'Ansvarig')
    spara_profil(t.mapp, klar)
    status, html, _ = anrop(s, '?oversikt=1')
    assert status == 200
    assert 'P-TJ.red01_attest' in html
    status, html, _ = anrop(s, '?falt=P-TJ.red01_attest')
    assert status == 200 and 'Vem attesterar underlagen?' in html
    assert 'Svaret är valfritt' in html
    status, html, _ = anrop(s, 'svar', dict(csrf=s.csrf, revision=profilrevision(t.profil()),
        falt='P-TJ.red01_attest', text='bada', status='bekräftad', kalla='Syntetiskt avtal', roll='Ansvarig', datum=str(DAG)))
    assert status == 200
    assert t.profil().uppgifter['P-TJ.red01_attest'].varde == 'bada'
