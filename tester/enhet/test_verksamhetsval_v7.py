"""Versionerad faktavy och hela skyddade begäranden för äldre format."""
import pytest

from riskanalys.bedomning.motor import bedom
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.underlag import bygg_underlag
from riskanalys.profil.modeller import Uppgift
from riskanalys.regelverk.urval import valj
from tester.fixturer.m2 import komplett_profil

V7 = 'D-ARB-tjanst-v7'


@pytest.fixture
def bas(regelbas_v1, profil_fabrik):
    rb = regelbas_v1
    p = komplett_profil(rb, profil_fabrik(rb, {}))
    p = p.model_copy(update={'byra': p.byra.model_copy(update={'regelpaket': 'RP-RED-VG'})})
    return rb, p


def tjanst(rb, p, id='T-RED-01'):
    return next(t for t in bedom(rb, valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan), p).tjanster if t.tjanst == id)


def satt(p, **varden):
    mall = p.uppgifter['P-TJ.red01_erbjuds']
    return p.model_copy(update={'uppgifter': {**p.uppgifter,
        **{k:mall.model_copy(update={'varde':v}) for k,v in varden.items()}}})


def test_v7_visar_bara_egen_tjansts_tre_val_med_omfang(bas):
    rb, p = bas
    p = satt(p, **{'P-TJ.red04_erbjuds':True, 'P-TJ.red01_attest':'kund',
        'P-TJ.red04_attest':'byra', 'P-TJ.red01_betalningsmandat':'inget',
        'P-TJ.red04_betalningsmandat':'verkstaller', 'P-TJ.red04_bankinsyn':'delvis'})
    fb = bygg_faktablad(rb, p, tjanst(rb,p,'T-RED-04'), 'D-ARB.6.4', formatversion=V7)
    poster = {u.id:u for u in fb.poster}
    assert {k for k in poster if k.endswith(('_attest','_betalningsmandat','_bankinsyn'))} == {
        'P-TJ.red04_attest','P-TJ.red04_betalningsmandat','P-TJ.red04_bankinsyn'}
    assert poster['P-TJ.red04_attest'].visningsvarde == 'byrån'
    assert poster['P-TJ.red04_betalningsmandat'].visningsvarde == 'verkställer betalningar'
    assert poster['P-TJ.red04_bankinsyn'].visningsvarde == 'delvis'
    assert poster['P-KUND.antal_aktiva'].omfang == 'byra'
    assert poster['P-KUND.antal_aktiva'].tjanst_id is None
    assert poster['P-TJ.red04_attest'].omfang == 'tjanst'
    assert poster['P-TJ.red04_attest'].tjanst_id == 'T-RED-04'
    assert all(u.omfang in ('byra','tjanst') for u in fb.poster)


@pytest.mark.parametrize('uppgift', [Uppgift(), Uppgift(varde='okant',status='bekräftad'),
    Uppgift(varde='full',status='bekräftad',inaktuell=True)])
def test_v7_saknat_inaktuellt_och_semantiskt_okant_ar_okand(bas, uppgift):
    rb, p = bas
    p = p.model_copy(update={'uppgifter':{**p.uppgifter,'P-TJ.red01_bankinsyn':uppgift}})
    fb = bygg_faktablad(rb,p,tjanst(rb,p),'D-ARB.6.1',formatversion=V7)
    post = next(u for u in fb.poster if u.id=='P-TJ.red01_bankinsyn')
    assert (post.visningsvarde,post.status)==('okänt','okänd')


@pytest.mark.parametrize(('suffix','varde','visning'), [
    ('attest','kund','kunden'), ('attest','byra','byrån'), ('attest','bada','både kunden och byrån'),
    ('betalningsmandat','inget','inget'), ('betalningsmandat','forbereder','förbereder betalningar'),
    ('betalningsmandat','verkstaller','verkställer betalningar'),
    ('bankinsyn','full','full'), ('bankinsyn','delvis','delvis'), ('bankinsyn','ingen','ingen'),
])
def test_v7_anvander_klartextetiketter(bas,suffix,varde,visning):
    rb,p=bas
    id='P-TJ.red01_'+suffix
    p=satt(p,**{id:varde})
    fb=bygg_faktablad(rb,p,tjanst(rb,p),'D-ARB.6.1',formatversion=V7)
    assert next(u.visningsvarde for u in fb.poster if u.id==id)==visning


@pytest.mark.parametrize('version',['D-ARB-tjanst-v5','D-ARB-tjanst-v6'])
def test_aldre_hela_begaran_inklusive_omforsok_ser_inte_nya_val_eller_privata_texter(bas,version):
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.leverantor import Testleverantor
    rb,p=bas
    lista=rb.tillatelselistor['risk_per_tjanst']
    aldre=rb.model_copy(update={'tillatelselistor':{lista.id:lista.model_copy(update={
        'falt':tuple(k for k in lista.falt if not k.endswith(('_attest','_betalningsmandat','_bankinsyn')))})}})
    profiler=[p,satt(p,**{'P-TJ.red01_attest':'byra','P-TJ.red01_betalningsmandat':'verkstaller',
        'P-TJ.red01_bankinsyn':'full','P-TJ.red01_arbetssatt':'PRIVAT FRITEXT',
        'P-TJ.red01_antal_utland_transaktion':2})]
    kedjor=[]
    for regelbas,profil in [(aldre,p),(rb,profiler[0]),(rb,profiler[1])]:
        t=tjanst(regelbas,profil)
        fb=bygg_faktablad(regelbas,profil,t,'D-ARB.6.1')
        assert all('omfang' not in u and 'tjanst_id' not in u for u in fb.model_dump()['poster'])
        lev=Testleverantor(['ogiltig JSON']*15)
        skriv_tjanst(lev,regelbas,profil,t,'D-ARB.6.1',formatversion=version,
            effort='medium',personnamn=(),spara=lambda *args:None)
        assert len(lev.delanrop)==(15 if version.endswith('v5') else 6)
        kedjor.append(tuple(a.model_dump_json().encode() for a in lev.delanrop))
    assert kedjor[0]==kedjor[1]==kedjor[2]
    assert b'PRIVAT' not in b''.join(kedjor[2])


def test_v7_underlag_utesluter_privata_fordelningar_och_fritext(bas):
    rb,p=bas
    p=satt(p,**{'P-TJ.red01_arbetssatt':'PRIVAT ARBETSSÄTT', 'P-TJ.red01_antal_utland_transaktion':2})
    t=tjanst(rb,p)
    u=bygg_underlag(rb,p,t,'D-ARB.6.1',formatversion=V7)
    assert not any(x.id.endswith('_antal_utland_transaktion') for x in u.uppgifter)
    assert 'PRIVAT' not in bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7).model_dump_json()


def test_saknade_val_tillfor_inga_b1_verifiera_eller_kritiska_falt(bas):
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    from riskanalys.profil.hantering import saknade_kritiska
    rb,p=bas
    val=lambda id:id.endswith(('_attest','_betalningsmandat','_bankinsyn'))
    p=p.model_copy(update={'uppgifter':{k:u for k,u in p.uppgifter.items() if not val(k)}})
    aldre=rb.model_copy(update={'falt':{k:f for k,f in rb.falt.items() if not val(k)}})
    assert bygg_underlagsbilaga(rb,p).model_dump_json()==bygg_underlagsbilaga(aldre,p).model_dump_json()
    assert not saknade_kritiska(p,rb,valj(rb,p.byra.regelpaket,p.byra.datum,p.byra.lan))


def test_handredigerat_fritextval_blir_okant_utan_att_skickas_till_ai(bas):
    rb,p=bas
    p=satt(p,**{'P-TJ.red01_attest':'PRIVAT otillåten fritext'})
    fb=bygg_faktablad(rb,p,tjanst(rb,p),'D-ARB.6.1',formatversion=V7)
    post=next(u for u in fb.poster if u.id=='P-TJ.red01_attest')
    assert (post.visningsvarde,post.status)==('okänt','okänd')
    assert 'PRIVAT' not in fb.model_dump_json()


@pytest.mark.parametrize('version', ['D-ARB-tjanst-v6', V7])
def test_sparat_underlag_foljer_vald_version_och_egen_tjanst(bas, tmp_path, version):
    import json
    from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.skrivning import UNDERLAGSFIL, kor_skrivning, las_skrivresultat
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.profil.lagring import spara_profil
    from tester.fixturer.m2 import bygg_delsvar
    from tester.fixturer.skrivsvar_v7 import med_verksamhetsval
    rb, p = bas
    p = med_verksamhetsval(rb, p)
    p = satt(p, **{'P-TJ.red04_erbjuds': True, 'P-TJ.red04_attest': 'byra',
        'P-TJ.red04_betalningsmandat': 'verkstaller', 'P-TJ.red04_bankinsyn': 'delvis',
        'P-TJ.red04_arbetssatt': 'PRIVAT ARBETSSÄTT'})
    from riskanalys.profil.omfattning import harled_andelar
    p = harled_andelar(p.model_copy(update={'uppgifter': {**p.uppgifter,
        'P-TJ.red04_omsattning': p.uppgifter['P-TJ.red04_omsattning'].model_copy(update={'varde': 1000.})}}), rb)
    spara_profil(tmp_path, p)
    b = las_bedomning(kor_bedomning(tmp_path, rb))
    lev = Testleverantor(bygg_delsvar(rb, p, b, formatversion=version))
    mapp = kor_skrivning(tmp_path, rb, lev, formatversion=version)
    assert all(not d.mall for r in las_skrivresultat(mapp) for d in r.delar)
    for id, t in tjanster_med_avsnitt(b):
        sparat = json.loads((mapp / id / UNDERLAGSFIL).read_text(encoding='utf-8'))
        val = {u['id']: u['varde'] for u in sparat['uppgifter']
               if u['id'].endswith(('_attest', '_betalningsmandat', '_bankinsyn'))}
        if version == V7:
            prefix = rb.tjanster[t.tjanst].erbjuds_falt.removesuffix('_erbjuds')
            assert set(val) == {prefix + suffix for suffix in ('_attest', '_betalningsmandat', '_bankinsyn')}
            if t.tjanst == 'T-RED-04':
                assert val == {'P-TJ.red04_attest': 'byrån',
                    'P-TJ.red04_betalningsmandat': 'verkställer betalningar', 'P-TJ.red04_bankinsyn': 'delvis'}
            if t.tjanst == 'T-RED-01':
                assert val == {'P-TJ.red01_attest': 'kunden', 'P-TJ.red01_betalningsmandat': 'inget',
                    'P-TJ.red01_bankinsyn': 'full'}
        else:
            assert val == {}
    assert 'PRIVAT ARBETSSÄTT' not in ''.join(a.model_dump_json() for a in lev.delanrop)
