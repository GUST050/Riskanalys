"""De två rena projektionerna är tillsammans det kanoniska dokumentet."""
from collections import Counter
import pytest
from tester.enhet.test_arb_v8 import v8fall, bygg


def test_rapportvyer_bevarar_samtliga_avsnitt_och_summor(v8fall):
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    f, r = v8fall
    d = bygg(f, r)
    vyer = bygg_rapportvyer(d)
    alla = (*vyer.lasrapport.avsnitt, *vyer.underlagsbilaga.avsnitt)
    assert Counter(a.id for a in alla) == Counter(a.id for a in d.avsnitt)
    assert not set(a.id for a in vyer.lasrapport.avsnitt) & set(a.id for a in vyer.underlagsbilaga.avsnitt)
    assert all(a.kontrollsumma() == d.avsnitt_med_id()[a.id].kontrollsumma() for a in alla)
    assert all(a is d.avsnitt_med_id()[a.id] for a in alla)
    assert 'D-ARB.B1' in vyer.underlagsbilaga.avsnitt_med_id()
    assert vyer.lasrapport.formatversion == vyer.underlagsbilaga.formatversion == d.formatversion


def test_v8_placering_binds_och_id_kollision_vagras(v8fall):
    from riskanalys.faststallelse.sakgranskning import struktur_summa
    from riskanalys.dokument.modeller import Dokument
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    f, r = v8fall
    d = bygg(f, r)
    flyttat = d.model_copy(update={'avsnitt': (d.avsnitt[0].model_copy(update={'leveransdel': 'underlagsbilaga'}), *d.avsnitt[1:])})
    assert struktur_summa(d) != struktur_summa(flyttat)
    with pytest.raises(ValueError, match='unika|kollision'):
        Dokument.model_validate(d.model_copy(update={'avsnitt': (*d.avsnitt, d.avsnitt[0])}).model_dump())
    with pytest.raises(ValueError):
        bygg_rapportvyer(d.model_copy(update={'avsnitt': (*d.avsnitt, d.avsnitt[0])}))


def test_v8_delvy_eller_flyttad_b1_ar_inte_kanoniskt_underlag(v8fall):
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    f,r=v8fall
    d=bygg(f,r)
    with pytest.raises(ValueError,match='B1|kanonisk'):
        bygg_rapportvyer(bygg_rapportvyer(d).lasrapport)
    fel=d.model_copy(update={'avsnitt':tuple(a.model_copy(update={'leveransdel':'lasrapport'}) if a.id=='D-ARB.B1' else a for a in d.avsnitt)})
    with pytest.raises(ValueError,match='B1|underlagsbilaga'):
        bygg_rapportvyer(fel)


def test_v7_far_inte_tyst_acceptera_v8_placering(v8fall):
    from riskanalys.dokument.modeller import Avsnitt
    from riskanalys.dokument.skrivversion import V7
    with pytest.raises(ValueError,match='leveransdel|V8'):
        Avsnitt(id='D-ARB.1',rubrik='Prov',kalla='lokal',stycken=(),formatversion=V7,leveransdel='lasrapport')
