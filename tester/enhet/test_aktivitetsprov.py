"""Aktivering prövas som förut, men definitioner och värden byggs en gång per profilvy."""
import sys

import pytest

from riskanalys.dokument.underlag import bygg_underlag, tjanster_med_avsnitt
from riskanalys.bedomning.motor import bedom
from riskanalys.intag.fragor import fragor
from riskanalys.intag.kvalitet import kvalitetsbrister
from riskanalys.intag.tackning import tackning
from riskanalys.profil import omfattning
from riskanalys.profil.modeller import Byra, Profil, Uppgift
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.regelverk.villkor import Sanning, tolka_villkor, utvardera
from tester.fixturer.m2 import DAG, komplett_profil


@pytest.fixture(scope='module')
def rb():
    return ladda_regelbas()


@pytest.fixture(scope='module')
def full(rb):
    bas = Profil(byra=Byra(id='syntetisk', regelpaket='RP-RED-VG', lan='Västra Götaland', datum=DAG), uppgifter={})
    return komplett_profil(rb, bas)


def _referens(falt, profil, rb):
    # Tidigare genomförande: allt byggdes om vid varje prövning.
    if falt.kritisk_om is None:
        return True
    return utvardera(tolka_villkor(falt.kritisk_om, rb.faltdefinitioner()), profil.faltvarden()).sanning is not Sanning.FALSKT


def _alias_nej(full):
    # Bara det äldre aliasfältet säger nej; den kanoniska uppgiften saknas.
    u = full.uppgifter['P-TJ.red01_erbjuds']
    return full.model_copy(update={'uppgifter': {**full.uppgifter, 'P-TJ.red01_erbjuds': Uppgift(),
                                                 'P-TJ.T-RED-01.erbjuds': u.model_copy(update={'varde': False})}})


def _varianter(rb, full):
    bekr = [k for k, u in full.uppgifter.items() if u.status == 'bekräftad']
    inaktuell = {**full.uppgifter, **{k: full.uppgifter[k].model_copy(update={'inaktuell': True}) for k in bekr[::3]}}
    return (full.model_copy(update={'uppgifter': {}}), full,
            full.model_copy(update={'uppgifter': inaktuell}), _alias_nej(full))


def _aktiva(prov, rb):
    return [f.id for f in rb.falt.values() if prov(f)]


def test_samma_aktivering_som_tidigare_for_profil_och_kompatibilitetsvy(rb, full):
    for p in _varianter(rb, full):
        for vy in (p, omfattning.kompatibilitetsvy(p, rb)):
            prov = omfattning.aktivitetsprov(vy, rb)
            assert [prov(f) for f in rb.falt.values()] == [_referens(f, vy, rb) for f in rb.falt.values()]
            assert all(omfattning.aktivt(f, vy, rb) == prov(f) for f in rb.falt.values())


def test_vyn_avgor_aktiveringen_for_aldre_alias(rb, full):
    p = _alias_nej(full)
    original = _aktiva(omfattning.aktivitetsprov(p, rb), rb)
    vy = _aktiva(omfattning.aktivitetsprov(omfattning.kompatibilitetsvy(p, rb), rb), rb)
    assert set(vy) < set(original)


def test_senare_profilandring_paverkar_nasta_prov_men_inte_tidigare(rb, full):
    fore = omfattning.aktivitetsprov(full, rb)
    u = full.uppgifter['P-TJ.red01_erbjuds']
    efter_profil = full.model_copy(update={'uppgifter': {**full.uppgifter, 'P-TJ.red01_erbjuds': u.model_copy(update={'varde': False})}})
    efter = omfattning.aktivitetsprov(efter_profil, rb)
    assert set(_aktiva(efter, rb)) < set(_aktiva(fore, rb))
    assert _aktiva(fore, rb) == _aktiva(omfattning.aktivitetsprov(full, rb), rb)


def _rakna(monkeypatch, *, bara_aktivering=False):
    # Med bara_aktivering räknas byggen från aktiveringsprövningen; sårbarhetsstatus ligger utanför.
    antal = {'definitioner': 0, 'varden': 0}
    for klass, metod, nyckel in ((Regelbas, 'faltdefinitioner', 'definitioner'), (Profil, 'faltvarden', 'varden')):
        original = getattr(klass, metod)
        def raknad(self, _o=original, _n=nyckel):
            if not bara_aktivering or sys._getframe(1).f_code.co_filename == omfattning.__file__:
                antal[_n] += 1
            return _o(self)
        monkeypatch.setattr(klass, metod, raknad)
    return antal


def test_ett_prov_bygger_definitioner_och_varden_en_gang(rb, full, monkeypatch):
    antal = _rakna(monkeypatch)
    prov = omfattning.aktivitetsprov(full, rb)
    for f in rb.falt.values():
        prov(f)
    assert antal == {'definitioner': 1, 'varden': 1}


# Övre gräns per operation. Före rättningen byggdes båda om för varje villkorsstyrt fält.
ANROPSGRANS = 10


@pytest.mark.parametrize('operation', ['fragor', 'tackning', 'kvalitet', 'omfattning', 'harledning', 'underlag'])
def test_operationer_bygger_inte_om_per_falt(rb, full, monkeypatch, operation):
    tjanster = tjanster_med_avsnitt(bedom(rb, valj(rb, 'RP-RED-VG', DAG, 'Västra Götaland'), full))
    antal = _rakna(monkeypatch, bara_aktivering=True)
    {'fragor': lambda: fragor(rb, full), 'tackning': lambda: tackning(rb, full),
     'kvalitet': lambda: kvalitetsbrister(rb, full), 'omfattning': lambda: omfattning.omfattningsbrister(full, rb),
     'harledning': lambda: omfattning.harled_andelar(full, rb),
     'underlag': lambda: bygg_underlag(rb, full, tjanster[0][1], tjanster[0][0])}[operation]()
    assert sum(1 for f in rb.falt.values() if f.kritisk_om) > ANROPSGRANS
    assert antal['varden'] <= ANROPSGRANS, antal
