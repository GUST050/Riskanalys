import pytest
from tester.fixturer.resultatrapport import resultatfall
from tester.enhet.test_resultatrapport_v9 import bygg, text


def test_v9_tre_vyer_utgor_hela_dokumentet(resultatfall):
    from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9
    b=bygg(resultatfall);v=bygg_rapportvyer_v9(b.dokument)
    a=(*v.resultatrapport.avsnitt,*v.analysbilaga.avsnitt,*v.underlagsbilaga.avsnitt)
    assert len(a)==len(b.dokument.avsnitt)
    assert {x.id for x in a}=={x.id for x in b.dokument.avsnitt}
    assert len({x.id for x in a})==len(a)
    with pytest.raises(ValueError):bygg_rapportvyer_v9(v.resultatrapport)


def test_v8_sakfalt_bevaras_med_uttommande_metadataundantag(resultatfall):
    b=bygg(resultatfall)
    for a in b.analysdokument.avsnitt:
        after=b.dokument.avsnitt_med_id()[a.id]
        def semantic(a):return a.model_dump(mode='json',exclude={'formatversion','leveransdel','visningsnummer'})
        fore=semantic(a);efter=semantic(after)
        # Endast exakt gammal programförklaring får bytas, aldrig andra sakfält.
        from riskanalys.dokument.arb_v8 import HELHET
        from riskanalys.dokument.arb_v9 import HELHET_V9
        for i,s in enumerate(fore['stycken']):
            ptr=f'/avsnitt/{b.analysdokument.avsnitt.index(a)}/stycken/{i}/text'
            for tr in b.transformationer:
                if tr.pointer==ptr:
                    assert s['text']==tr.fore
                    s['text']=tr.efter
        assert fore==efter
    assert b.transformationer
    assert all(t.orsak in ('format','leveransdel','visningsnummer','tredelsforklaring') for t in b.transformationer)


def test_referenser_och_literala_spann_bevaras(resultatfall):
    b=bygg(resultatfall)
    for a in b.analysdokument.avsnitt:
        n=b.dokument.avsnitt_med_id()[a.id]
        assert [s.referenser for s in a.stycken]==[s.referenser for s in n.stycken]
        assert [s.literala_spann for s in a.stycken]==[s.literala_spann for s in n.stycken]
    assert b.konstruktioner
    from riskanalys.dokument.resultatmodell_v9 import los_referens,kallartefakter
    f=resultatfall;k=kallartefakter(f.regelbas,f.profil,f.bedomning,f.resultat,f.historik,f.analys,b.analysdokument)
    for p in b.konstruktioner:
        assert p.mall and p.placering
        for ref in p.kallor:los_referens(k,ref)


def test_gamla_format_och_blandade_vyer_avvisas(resultatfall):
    from riskanalys.dokument.modeller import Dokument
    from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9
    b=bygg(resultatfall)
    with pytest.raises(ValueError):bygg_rapportvyer_v9(resultatfall.dokument)
    with pytest.raises(ValueError):
        Dokument.model_validate(b.dokument.model_copy(update={'avsnitt':(*b.dokument.avsnitt,resultatfall.dokument.avsnitt[0])}).model_dump())


def test_tredelsundantaget_far_inte_andra_ai_eller_lokal_saktext(resultatfall,monkeypatch):
    from riskanalys.dokument import arb_v9
    from riskanalys.dokument.arb_v8 import HELHET
    from riskanalys.dokument.modeller import Textstycke
    orig=resultatfall.dokument
    aid=next(a.id for a in orig.avsnitt if a.id.startswith('D-ARB.6.'))
    a=orig.avsnitt_med_id()[aid]
    p=Textstycke(typ='analys',text=HELHET,referenser=['H-01'],proveniens='ai')
    a=a.model_copy(update={'stycken':(*a.stycken,p)})
    d=orig.model_copy(update={'avsnitt':tuple(a if x.id==aid else x for x in orig.avsnitt)})
    monkeypatch.setattr(arb_v9,'bygg_arb_v8',lambda *args,**kwargs:d)
    b=bygg(resultatfall)
    assert b.dokument.avsnitt_med_id()[aid].stycken[-1].text==HELHET
