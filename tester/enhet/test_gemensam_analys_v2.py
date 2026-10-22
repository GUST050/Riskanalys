import pytest
from riskanalys.analys import modeller as m
from tester.enhet.test_analysschema_v2 import gammal_data


def paket(status='bekraftad'):
    from riskanalys.analys.gemensam import postsumma
    p=m.Analyspaket.model_validate({**gammal_data(),'schemaversion':2})
    g=m.GemensamSarbarhetsprovning(id='kund',omrade='kund',sarbarheter=('S-KUND-01',),
        beskrivning='Gemensam unik kundanalys',motivering='Samma identifierade förhållande för hela byrån',
        hot=('H-03',),relevans='relevant',belagg=(p.belagg[0].id,),status=status,forfattare='Syntetisk författare')
    app=m.Sarbarhetstillampning(post=g.id,stallningstagande='galler',postsumma=postsumma(g),bekraftad=True)
    ts=tuple(t.model_copy(update={'sarbarhetsprovningar':tuple(s for s in t.sarbarhetsprovningar if s.omrade!='kund'),
        'sarbarhetstillampningar':(app,)}) for t in p.tjanster)
    return p.model_copy(update={'tjanster':ts,'gemensamma_sarbarhetsprovningar':(g,)})


def test_en_lagrad_post_tillampas_av_flera_utan_kopierad_lagring():
    from riskanalys.analys.gemensam import effektiv_tjanst
    p=paket()
    fore=p.model_dump_json()
    for t in p.tjanster:
        a=effektiv_tjanst(p,t.tjanst)
        assert any('Gemensam unik kundanalys' in s.motivering and s.belagg for s in a.sarbarhetsprovningar)
    assert p.model_dump_json()==fore
    assert p.model_dump_json().count('Gemensam unik kundanalys')==1


def test_status_belagg_och_forfattare_ingar_i_postsumma():
    from riskanalys.analys.gemensam import postsumma
    p=paket();g=p.gemensamma_sarbarhetsprovningar[0]
    for andring in ({'status':'antagande'},{'belagg':()},{'forfattare':'Annan funktion'}):
        assert postsumma(g)!=postsumma(g.model_copy(update=andring))


def test_explicit_utelamnade_privata_tillampningar_kommer_inte_tillbaka():
    p=paket()
    data=p.model_dump(exclude={'tjanster':{'__all__':{'sarbarhetstillampningar'}}})
    assert all('sarbarhetstillampningar' not in t for t in data['tjanster'])


def test_antagande_blir_inte_faktum_genom_tillampningsbekraftelse():
    from riskanalys.analys.gemensam import effektiv_tjanst
    p=paket('antagande')
    for t in p.tjanster:
        a=effektiv_tjanst(p,t.tjanst)
        g=next(s for s in a.sarbarhetsprovningar if s.id=='gemensam:kund')
        assert g.relevans=='okant' and 'antagande' in g.motivering.lower()
    assert p.gemensamma_sarbarhetsprovningar[0].status=='antagande'


def test_inaktuell_eller_obekraftad_tillampning_arver_inte_text():
    from riskanalys.analys.gemensam import effektiv_tjanst
    p=paket();t=p.tjanster[0]
    for andring in ({'postsumma':'sha256:'+'0'*64},{'bekraftad':False}):
        app=t.sarbarhetstillampningar[0].model_copy(update=andring)
        q=p.model_copy(update={'tjanster':(t.model_copy(update={'sarbarhetstillampningar':(app,)}),)})
        a=effektiv_tjanst(q,t.tjanst)
        assert not any(s.id=='gemensam:kund' for s in a.sarbarhetsprovningar)


def test_andrad_gemensam_post_gor_block_och_paketbeslut_inaktuella():
    from riskanalys.analys.provning import blocksumma, svarssumma, gallande_beslut, underlagssumma
    p=paket();t=p.tjanster[0]
    beslut=m.Analysbeslut(tjanst=t.tjanst,revision=p.revision,underlagssumma=underlagssumma(p),
        svarssumma=svarssumma(p),godkand=True,namn='Syntetisk granskare',roll='FfR',datum=p.bindning.bedomningsdatum)
    p=p.model_copy(update={'beslut':(beslut,)})
    assert gallande_beslut(p,t.tjanst)
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'status':'antagande'})
    q=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,)})
    assert blocksumma(p,t.tjanst,7)!=blocksumma(q,t.tjanst,7)
    assert gallande_beslut(q,t.tjanst) is None


def test_utkastets_schema_ar_uttryckligt(regelbas_v1,tmp_path):
    regelbas=regelbas_v1
    from tester.fixturer.gemensam_analys import bygg_gemensamt_fall
    from riskanalys.analys.utkast import forifyll_analys
    f=bygg_gemensamt_fall(regelbas,tmp_path)
    for schema in (1,2):
        p=forifyll_analys(regelbas,f.profil,f.bedomning,f.paket.bindning,schema=schema)
        assert p.schemaversion==schema
        if schema==2:
            assert {x.omrade for x in p.gemensamma_sarbarhetsprovningar}=={'kund','kanal','geo','verk'}
            assert len(p.gemensamma_verksamhetsposter)==3
            assert not any(a.bekraftad for t in p.tjanster for a in t.sarbarhetstillampningar)
