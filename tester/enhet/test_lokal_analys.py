"""Privat analys: syntetiska svar får aldrig bli implicit godkända."""
from datetime import date
import importlib.util

import pytest


def test_lokal_analys_ar_en_separat_typad_utkastvag():
    assert importlib.util.find_spec('riskanalys.analys') is not None, 'Privat analysmodul saknas'


@pytest.fixture
def api():
    if importlib.util.find_spec('riskanalys.analys') is None:
        pytest.skip('RED: analysmodulen saknas')
    from riskanalys.analys import modeller, provning, utkast
    return modeller, provning, utkast


@pytest.fixture
def syntetiskt(api, regelbas, profil_fabrik, real_varden):
    m, p, u = api
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.profil.lagring import profilrevision
    profil = profil_fabrik(regelbas, real_varden)
    b = profil.byra
    resultat = bedom(regelbas, valj(regelbas,b.regelpaket,b.datum,b.lan),profil)
    bindning = m.Analysbindning(byra=b.id, profilrevision=profilrevision(profil),
        bedomningsmanifest='b', utkastmanifest='u', regelbas=regelbas.kontrollsumma,
        kallunderlag='k', historik='', bedomningsdatum=resultat.datum, modell='m')
    return regelbas, profil, resultat, u.forifyll_analys(regelbas,profil,resultat,bindning)


def test_forifyllnad_ar_redigerbart_utkast_utan_attest(api, syntetiskt):
    _, p, _ = api
    rb, profil, b, paket = syntetiskt
    assert paket.beslut == ()
    assert all(t.forfattare is None for t in paket.tjanster)
    assert all(x.bekraftad_summa is None for t in paket.tjanster for x in t.block)
    assert all(not k.bekraftad for t in paket.tjanster for k in t.scenariokopplingar)
    assert p.analysbrister(rb,profil,b,paket)
    assert len(paket.tjanster[0].block) == 16


def test_modelldata_avvisar_fri_riskniva_och_osakra_belaggsreferenser(api):
    m, _, _ = api
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        m.Scenarioanalys(id='s', risk='hög')
    for fil in ('../hemlig', '/etc/passwd', 'https://example.se/x', 'belagg/../../x'):
        with pytest.raises(ValidationError):
            m.Analysbelagg(id='b', dokument=fil, kontrollsumma='sha256:'+'a'*64, datum=date(2026,10,1))


def test_blockbekraftelse_binds_till_svar_och_underlag(api, syntetiskt):
    m,p,_ = api
    _,_,_,paket=syntetiskt
    t=paket.tjanster[0]
    summa=p.blocksumma(paket,t.tjanst,13)
    andrat=t.model_copy(update={'pt_motivering':'Ny självständig motivering'})
    nytt=paket.model_copy(update={'tjanster':(andrat,)})
    assert p.blocksumma(nytt,t.tjanst,13) != summa
    assert p.blocksumma(nytt,t.tjanst,14) == p.blocksumma(paket,t.tjanst,14)
    ny_bindning=paket.bindning.model_copy(update={'utkastmanifest':'nytt'})
    assert p.blocksumma(paket.model_copy(update={'bindning':ny_bindning}),t.tjanst,13)!=summa


def test_senaste_beslut_galler_utan_aterupplivning(api, syntetiskt):
    m,p,_=api
    _,_,_,paket=syntetiskt
    t=paket.tjanster[0].model_copy(update={'forfattare':'Ada'})
    paket=paket.model_copy(update={'tjanster':(t,)})
    def beslut(godkand, namn='Ada'):
        return m.Analysbeslut(tjanst=t.tjanst,revision=paket.revision,
            underlagssumma=p.underlagssumma(paket),svarssumma=p.svarssumma(paket),godkand=godkand,
            namn=namn,roll='ansvarig',datum=date(2026,11,1),kommentar=None if godkand else 'Måste utredas',
            forfattare='förfalskad',egen_granskning=False)
    paket=p.registrera_beslut(paket,beslut(True))
    assert paket.beslut[-1].forfattare=='Ada'
    assert paket.beslut[-1].egen_granskning
    svar=p.svarssumma(paket)
    paket=p.registrera_beslut(paket,beslut(False,'Bo'))
    assert p.svarssumma(paket)==svar
    assert not p.gallande_beslut(paket,t.tjanst).godkand
    assert not paket.beslut[-1].egen_granskning
    aterstalld=paket.model_copy(update={'revision':paket.revision+1})
    assert p.gallande_beslut(aterstalld,t.tjanst) is None


@pytest.fixture
def komplett(api, syntetiskt):
    m,p,_=api
    rb,profil,b,paket=syntetiskt
    # Syntetisk fullständigt lokalt granskad variant: alla hot prövas uttryckligen ej relevanta.
    a=paket.tjanster[0]
    ids=tuple(x.id for x in paket.belagg)
    scenarier=tuple(s.model_copy(update={'relevans':'ej_relevant','motivering':'Uppdragets belagda mandat omfattar inte detta förlopp.',
        'belagg':ids[:1]}) for s in a.scenarier)
    sidor=tuple(s.model_copy(update={'relevans':'ej_relevant','motivering':'Prövat mot belagt uppdrag och aktuella fakta.',
        'belagg':ids[:1]}) for s in a.sarbarhetsprovningar)
    a=a.model_copy(update=dict(forfattare='Ada',scenarier=scenarier,sarbarhetsprovningar=sidor,
        delningsmotivering='Uppdragets arbetsmoment har samma mandat och insyn.',
        betalningsinsyn=m.Betalningsinsyn(status='ej_tillamplig',motivering='Uppdraget omfattar inga betalningsunderlag.'),
        uppdragsprovning=m.Uppdragsprovning(status='hanterbart',kompetens_och_insyn='Belagd kompetens och avgränsad insyn.',
            motivering='Inget genomförande utanför uppdraget.',belagg=ids[:1]),
        samverkan='Belagda begränsningar prövade mot kundmix och uppdragets mandat.',
        erfarenhetsprovning='Noll rapporter utesluter inte hot; tjänstens avgränsning prövas separat.',erfarenhetsbelagg=ids[:1],
        pt_motivering='Separat prövning av PT-utfallet mot uppdraget.',tf_motivering='Separat prövning av TF även med lagligt ursprung.',
        slutsats='Rutinens avgränsning behöver bevaras och följas upp.',
        rutinatgarder=(m.Rutinatgard(id='r1',scenarier=(scenarier[0].id,),atgard='Precisera rutinens avgränsning.',
            utlosare_eller_frekvens='Vid ändrat uppdrag.'),)))
    block=tuple(x.model_copy(update={'aktivering':'aktiv' if x.nummer in p.ALLTID else 'ej_tillamplig',
        'motivering':'Syntetiskt sakligt prövat mandat.'}) for x in a.block)
    a=a.model_copy(update={'block':block})
    paket=paket.model_copy(update={'tjanster':(a,)})
    a=a.model_copy(update={'block':tuple(x.model_copy(update={'bekraftad_summa':p.blocksumma(paket,a.tjanst,x.nummer)})
        if x.aktivering=='aktiv' else x for x in a.block)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    assert not p.analysbrister(rb,profil,b,paket),p.analysbrister(rb,profil,b,paket)
    return rb,profil,b,paket


def test_komplett_lokal_analys_med_avgransningar_kan_provas(api,komplett):
    _,p,_=api
    assert not p.analysbrister(*komplett)


@pytest.mark.parametrize('falt',['samverkan','pt_motivering','tf_motivering','erfarenhetsprovning','delningsmotivering'])
def test_aktiva_sakfragor_maste_besvaras(api,komplett,falt):
    _,p,_=api
    rb,profil,b,paket=komplett
    a=paket.tjanster[0].model_copy(update={falt:' [VERIFIERA] '})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)}))
    assert any('saknar ett färdigt svar' in f for f in fel)


@pytest.mark.parametrize('omrade',['kund','kanal','geo','verk'])
def test_sarbarhetsprovning_kraver_fyra_omraden_och_belagg(api,komplett,omrade):
    _,p,_=api
    rb,profil,b,paket=komplett
    a=paket.tjanster[0]
    a=a.model_copy(update={'sarbarhetsprovningar':tuple(s for s in a.sarbarhetsprovningar if s.omrade!=omrade)})
    assert any('Sårbarhetsområdet '+omrade in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)})))


def test_belagg_kraver_exakt_period_och_aktuell_status(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    belagg=paket.belagg[0]
    from riskanalys.profil.modeller import Period
    andrat=belagg.model_copy(update={'period':Period(fran=date(2020,1,1),till=date(2020,12,31))})
    assert any('period' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'belagg':(andrat,*paket.belagg[1:])})))
    f=belagg.profilfalt[0]
    upp=dict(profil.uppgifter);upp[f]=upp[f].model_copy(update={'inaktuell':True})
    assert any('inte aktuellt bekräftat' in f for f in p.analysbrister(rb,profil.model_copy(update={'uppgifter':upp}),b,paket))


def test_reduktionsprovning_maste_stamma_med_motorutfall(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett
    t=b.tjanster[0]
    if t.inneboende.risk=='låg':
        t=t.model_copy(update={'inneboende':t.inneboende.model_copy(update={'risk':'hög'})})
    t=t.model_copy(update={'kvarstaende':'låg'})
    nytt=b.model_copy(update={'tjanster':(t,)})
    assert any('stämmer inte med motorns faktiska reduktion' in f for f in p.analysbrister(rb,profil,nytt,paket))


def test_hog_risk_ar_inte_automatiskt_avslag(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett
    t=b.tjanster[0]
    t=t.model_copy(update={'inneboende':t.inneboende.model_copy(update={'risk':'hög'}),'kvarstaende':'hög'})
    assert not p.analysbrister(rb,profil,b.model_copy(update={'tjanster':(t,)}),paket)


def test_ohanterbart_uppdrag_kraver_atgard_eller_avgransning(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett
    a=paket.tjanster[0]
    a=a.model_copy(update={'uppdragsprovning':a.uppdragsprovning.model_copy(update={'status':'kan_inte_hanteras'})})
    assert any('får inte fortsätta oförändrat' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)})))


def test_delat_scenario_kraver_samma_eller_avviker_per_tjanst(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    a=paket.tjanster[0];s=a.scenarier[0]
    paket=paket.model_copy(update={'gemensamma_scenarier':(s,)})
    kop=m.Scenariokoppling(scenario=s.id,tillampning='samma',scenariosumma=p.scenariosumma(s),bekraftad=True)
    a=a.model_copy(update={'scenarier':a.scenarier[1:],'scenariokopplingar':(kop,)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    fel=p.analysbrister(rb,profil,b,paket)
    assert not any('Varje kataloghot' in f or 'Scenariokopplingen' in f for f in fel)
    s=s.model_copy(update={'motivering':'Ändrat gemensamt sakunderlag.'})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'gemensamma_scenarier':(s,)}))
    assert any('inte aktuellt bekräftad' in f for f in fel)
    assert any('Varje kataloghot' in f for f in fel)


def test_rutinatgard_skiljer_forslag_beslut_och_genomforande(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett
    a=paket.tjanster[0];r=a.rutinatgarder[0]
    for status in ('beslutad','genomford'):
        andrat=r.model_copy(update={'status':status,'rutin_id':'R1'})
        nytt=paket.model_copy(update={'tjanster':(a.model_copy(update={'rutinatgarder':(andrat,)}),)})
        fel=p.analysbrister(rb,profil,b,nytt)
        assert any('anges tillsammans' in f for f in fel)
        assert any('ansvar och uppföljning' in f for f in fel)


def test_lokal_analys_tacker_alltid_varje_erbjuden_tjanst(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett
    assert any('tjänsteanalys saknas' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':()})))


def test_forifyllnad_fyrtjanstfall_har_12_scenarier_for_36_kopplingar(api,regelbas_v1,profil_fabrik):
    m,p,u=api
    from tester.fixturer.m2 import komplett_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.profil.lagring import profilrevision
    rb=regelbas_v1
    profil=komplett_profil(rb,skapa_profil(rb,Byra(id='fyra',regelpaket='RP-RED-VG',datum=date(2026,10,15),lan='Västra Götaland')))
    upp=dict(profil.uppgifter)
    for id,t in rb.tjanster.items():
        upp[t.erbjuds_falt]=upp[t.erbjuds_falt].model_copy(update={'varde':id in ('T-RED-01','T-RED-02','T-RED-03','T-RED-04')})
    profil=profil.model_copy(update={'uppgifter':upp})
    b=bedom(rb,valj(rb,'RP-RED-VG',profil.byra.datum,profil.byra.lan),profil)
    bind=m.Analysbindning(byra='fyra',profilrevision=profilrevision(profil),bedomningsmanifest='b',utkastmanifest='u',
        regelbas=rb.kontrollsumma,kallunderlag='k',historik='',bedomningsdatum=b.datum,modell='m')
    paket=u.forifyll_analys(rb,profil,b,bind)
    assert len(paket.tjanster)==4
    assert len(paket.gemensamma_scenarier)==8
    assert sum(len(t.scenarier) for t in paket.tjanster)==4
    assert sum(len(rb.tjanster[t.tjanst].hot) for t in paket.tjanster)==36
    # The same data can display all six conditional blocks without inventing confirmations.
    aktiva=tuple(t.model_copy(update={'block':tuple(x.model_copy(update={'aktivering':'aktiv'}) for x in t.block)}) for t in paket.tjanster)
    assert sum(x.aktivering=='aktiv' for t in aktiva for x in t.block)==64
    assert sum(x.nummer in p.ALLTID for t in aktiva for x in t.block)==40
    assert sum(x.bekraftad_summa is not None for t in aktiva for x in t.block)==0


def test_okand_kallrackvidd_kan_inte_bli_positiv_tackning(api,komplett):
    m,p,_=api
    from riskanalys.regelverk.modeller import Kontrollrackvidd,Kallhanvisning
    rb,profil,b,paket=komplett
    a=paket.tjanster[0];s=a.scenarier[0].model_copy(update={'relevans':'relevant'})
    cid=rb.tjanster[a.tjanst].kontroller[0];c=rb.kontroller[cid]
    r=Kontrollrackvidd(id='syntetisk-rackvidd',tjanst=a.tjanst,hot=s.hot,
        kan_belagga='Uttryckligen okänd räckvidd.',begransningar='Inte utredd.',forutsattningar='Kräver lokal precisering.',
        grund='metodval',kallhanvisningar=(Kallhanvisning(kalla=c.kallor[0],avsnitt='syntetiskt',sida=1),),beskrivningsstatus='okand')
    kontroller=dict(rb.kontroller);kontroller[cid]=c.model_copy(update={'rackvidd':(r,)})
    rb=rb.model_copy(update={'kontroller':kontroller})
    cp=m.Kontrollprovning(scenario=s.id,kontroll=cid,rackvidd=(r.id,),tillampning='Utfört arbete.',
        utfall='Observation av synligt underlag.',belagg=(paket.belagg[0].id,),tackning='delvis',kvarstar='Dolda led.')
    a=a.model_copy(update={'scenarier':(s,*a.scenarier[1:]),'kontroller':(cp,)})
    nytt=paket.model_copy(update={'tjanster':(a,)})
    assert any('positiv täckning saknar beskriven' in f for f in p.analysbrister(rb,profil,b,nytt))
    kontroller[cid]=c.model_copy(update={'rackvidd':(r.model_copy(update={'beskrivningsstatus':'beskriven'}),)})
    assert not any('positiv täckning saknar beskriven' in f for f in p.analysbrister(rb.model_copy(update={'kontroller':kontroller}),profil,b,nytt))


def test_egen_erfarenhet_kraver_faktiskt_bevakningsunderlag(api,komplett):
    _,p,_=api
    from riskanalys.bedomning.modeller import EgenErfarenhet
    rb,profil,b,paket=komplett
    t=b.tjanster[0].model_copy(update={'egen_erfarenhet':EgenErfarenhet(rapporter='saknas',avbojanden='saknas',belagd=False,okanda_uppgifter=('x',))})
    assert any('erfarenhet' in f.lower() and 'underlag' in f.lower() for f in p.analysbrister(rb,profil,b.model_copy(update={'tjanster':(t,)}),paket))


def test_svarblock_binds_till_refererat_lokalt_scenario(api,komplett):
    _,p,_=api
    _,_,_,paket=komplett;a=paket.tjanster[0]
    summa=p.blocksumma(paket,a.tjanst,13)
    s=a.scenarier[0].model_copy(update={'handelseforlopp':'Förändrad mekanism kräver omprövad nivåmotivering.'})
    nytt=paket.model_copy(update={'tjanster':(a.model_copy(update={'scenarier':(s,*a.scenarier[1:])}),)})
    assert p.blocksumma(nytt,a.tjanst,13)!=summa


def test_reduktionsmotivering_utan_relevant_stod_blockerar(api,komplett):
    _,p,_=api
    rb,profil,b,paket=komplett;a=paket.tjanster[0];t=b.tjanster[0]
    t=t.model_copy(update={'inneboende':t.inneboende.model_copy(update={'risk':'hög'}),'kvarstaende':'låg'})
    a=a.model_copy(update={'reduktionsprovning':'motiverad','reduktionsmotivering':'Påstått stöd utan relevant scenario.'})
    assert any('relevant stöd' in f for f in p.analysbrister(rb,profil,b.model_copy(update={'tjanster':(t,)}),paket.model_copy(update={'tjanster':(a,)})))


def test_kallbeskrivning_ar_inte_genomforandebelagg(api,komplett):
    m,p,_=api
    from riskanalys.regelverk.modeller import Kontrollrackvidd,Kallhanvisning
    rb,profil,b,paket=komplett;a=paket.tjanster[0];s=a.scenarier[0].model_copy(update={'relevans':'relevant'})
    cid=rb.tjanster[a.tjanst].kontroller[0];c=rb.kontroller[cid]
    r=Kontrollrackvidd(id='r',tjanst=a.tjanst,hot=s.hot,kan_belagga='Avgränsad observation.',
        begransningar='Begränsat till synligt underlag.',forutsattningar='Prövat uppdrag.',grund='metodval',
        kallhanvisningar=(Kallhanvisning(kalla=c.kallor[0],avsnitt='prov',sida=1),),beskrivningsstatus='beskriven')
    cs=dict(rb.kontroller);cs[cid]=c.model_copy(update={'rackvidd':(r,)})
    rb=rb.model_copy(update={'kontroller':cs})
    ordinary=next(x for x in paket.belagg if c.genomforande_falt not in x.profilfalt)
    cp=m.Kontrollprovning(scenario=s.id,kontroll=cid,rackvidd=('r',),tillampning='Lokal tillämpning.',
        utfall='Påstådd effekt.',belagg=(ordinary.id,),tackning='delvis',kvarstar='Begränsad insyn.')
    a=a.model_copy(update={'scenarier':(s,*a.scenarier[1:]),'kontroller':(cp,)})
    assert any('genomförandebelägg' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)})))
    # A private execution document is eligible only alongside consistent confirmed profile facts.
    from riskanalys.profil.lagring import profilrevision
    upp=dict(profil.uppgifter)
    upp[c.genomforande_falt]=upp[c.genomforande_falt].model_copy(update={'varde':'belagt'})
    profil=profil.model_copy(update={'uppgifter':upp})
    paket=paket.model_copy(update={'bindning':paket.bindning.model_copy(update={'profilrevision':profilrevision(profil)})})
    dokument=m.Analysbelagg(id='utfört',dokument='egen-kontroll.bin',kontrollsumma='sha256:'+'a'*64,datum=date(2026,10,1))
    cp=cp.model_copy(update={'belagg':('utfört',)})
    a=a.model_copy(update={'kontroller':(cp,)})
    assert not any('genomförandebelägg' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'belagg':(*paket.belagg,dokument),'tjanster':(a,)})))


def test_forifyllnad_exponering_har_tjansteomfattning_och_lasbar_period(api,regelbas_v1):
    m,_,u=api
    from tester.fixturer.m2 import komplett_profil
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    rb=regelbas_v1
    profil=komplett_profil(rb,skapa_profil(rb,Byra(id='omfattning',regelpaket='RP-RED-VG',datum=date(2026,10,15),lan='Västra Götaland')))
    b=bedom(rb,valj(rb,'RP-RED-VG',profil.byra.datum,profil.byra.lan),profil)
    bind=m.Analysbindning(byra='omfattning',profilrevision='p',bedomningsmanifest='b',utkastmanifest='u',regelbas=rb.kontrollsumma,
        kallunderlag='k',historik='',bedomningsdatum=b.datum,modell='m')
    paket=u.forifyll_analys(rb,profil,b,bind)
    a=next(t for t in paket.tjanster if t.tjanst=='T-RED-01')
    assert 'P-TJ.' not in a.exponering and 'Period(' not in a.exponering
    assert '2026-01-01' in a.exponering and '2026-09-30' in a.exponering
    assert any('P-TJ.red01_antal_kunder' in x.profilfalt for x in paket.belagg if x.id in a.exponeringsbelagg)
    assert all('P-KUND.antal_aktiva' not in x.profilfalt for x in paket.belagg if x.id in a.exponeringsbelagg)


def test_sektorsavvikelse_far_inte_gommas_som_inaktivt_block(api,regelbas_v1):
    m,p,u=api
    from tester.fixturer.m2 import komplett_profil
    from tester.fixturer.lokal_analys import bekraftat_utkast
    from riskanalys.profil.hantering import skapa_profil
    from riskanalys.profil.modeller import Byra
    from riskanalys.profil.lagring import profilrevision
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    rb=regelbas_v1
    profil=komplett_profil(rb,skapa_profil(rb,Byra(id='sektor',regelpaket='RP-RED-VG',datum=date(2026,10,15),lan='Västra Götaland')))
    b=bedom(rb,valj(rb,'RP-RED-VG',profil.byra.datum,profil.byra.lan),profil)
    bind=m.Analysbindning(byra='sektor',profilrevision=profilrevision(profil),bedomningsmanifest='b',utkastmanifest='u',
        regelbas=rb.kontrollsumma,kallunderlag='k',historik='',bedomningsdatum=b.datum,modell='m')
    paket=bekraftat_utkast(u.forifyll_analys(rb,profil,b,bind),rb)
    paket=paket.model_copy(update={'tjanster':tuple(t.model_copy(update={'block':tuple(x.model_copy(update={'aktivering':'ej_tillamplig'}) if x.nummer==15 else x for x in t.block)}) for t in paket.tjanster)})
    assert any('sektors' in f.lower() and 'aktiver' in f.lower() for f in p.analysbrister(rb,profil,b,paket))


def test_genomforandebelagg_maste_galla_samma_scenario_och_period(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    # A control execution field with mismatched period is not current merely because it is confirmed.
    from riskanalys.profil.modeller import Period
    cid=rb.tjanster[paket.tjanster[0].tjanst].kontroller[0]
    f=rb.kontroller[cid].genomforande_falt
    u=profil.uppgifter[f]
    belagg=m.Analysbelagg(id='gen',profilfalt=(f,),datum=u.datum,period=Period(fran=date(2020,1,1),till=date(2020,12,31)))
    assert any('period' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'belagg':(*paket.belagg,belagg)})))


def test_okand_betalningsinsyn_far_inte_doljas_som_inaktiv(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett;a=paket.tjanster[0]
    a=a.model_copy(update={'betalningsinsyn':m.Betalningsinsyn(status='okand')})
    assert any('Betalningsinsyn' in f and 'avgräns' in f for f in p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)})))


def test_begransad_bedomd_insyn_kraver_inte_samtliga_kundkonton(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett;a=paket.tjanster[0]
    insyn=m.Betalningsinsyn(status='bedomd',synliga_floden='Endast kundens valda lönekonto.',
        insynsluckor='Andra konton och parallella bankengagemang är inte synliga.',
        avsandare_och_mottagare='Lönemottagare framgår av det avtalade underlaget.',
        underlagens_tillforlitlighet='Prövat mot registrerat underlag.',motivering='Avgränsat löneuppdrag utan kundens övriga konton.',
        belagg=(paket.belagg[0].id,))
    a=a.model_copy(update={'betalningsinsyn':insyn,'block':tuple(x.model_copy(update={'aktivering':'aktiv'}) if x.nummer==3 else x for x in a.block)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    a=a.model_copy(update={'block':tuple(x.model_copy(update={'bekraftad_summa':p.blocksumma(paket,a.tjanst,x.nummer)}) if x.aktivering=='aktiv' else x for x in a.block)})
    assert not p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)}))


def test_kand_kontrollbrist_kan_ha_motiverad_uppfoljning(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett;a=paket.tjanster[0];s=a.scenarier[0].model_copy(update={'relevans':'relevant'})
    gap=m.Analysgap(id='g',typ='kontrollbrist',beskrivning='Avgränsad kontroll saknas för ett känt led.',
        status='accepterad_kvarstaende_risk',motivering='Känd kvarstående risk med beslutad uppföljning.',ansvar='Ada',tidsfrist=date(2026,12,1))
    cp=m.Kontrollprovning(scenario=s.id,kontroll=rb.tjanster[a.tjanst].kontroller[0],tillampning='Kontrollen utförs inte i uppdraget.',
        utfall='Ingen faktisk effekt åberopas.',tackning='saknas',kvarstar='Det angivna scenariot kvarstår.')
    a=a.model_copy(update={'scenarier':(s,*a.scenarier[1:]),'kontroller':(cp,),'gap':(gap,),
        'block':tuple(x.model_copy(update={'aktivering':'aktiv'}) if x.nummer in (10,11) else x for x in a.block)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    a=a.model_copy(update={'block':tuple(x.model_copy(update={'bekraftad_summa':p.blocksumma(paket,a.tjanst,x.nummer)}) if x.aktivering=='aktiv' else x for x in a.block)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    assert not p.analysbrister(rb,profil,b,paket)
    # A method conflict cannot be re-labelled as accepted remaining risk.
    andrat=gap.model_copy(update={'typ':'metodkonflikt'})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a.model_copy(update={'gap':(andrat,)}),)}))
    assert any('bara känd kontrollbrist' in f for f in fel)
    okand=cp.model_copy(update={'tackning':'okand'})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a.model_copy(update={'kontroller':(okand,)}),)}))
    assert any('effekt är okänd' in f for f in fel)


def test_delanalys_far_inte_lana_annan_tjansts_arbetsmoment(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett;a=paket.tjanster[0];s=a.scenarier[0].model_copy(update={'relevans':'relevant','delanalyser':('annan-tjansts-moment',)})
    d=m.Delanalys(id='eget-moment',rubrik='Gränsöverskridande bokföring',arbetsmoment_och_befogenheter='Avgränsad bokföring utan betalningsmandat.',belagg=(paket.belagg[0].id,))
    a=a.model_copy(update={'delanalyser':(d,),'scenarier':(s,*a.scenarier[1:])})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)}))
    assert any('annan eller okänd delanalys' in f for f in fel)
    assert any('Varje delanalys behöver' in f for f in fel)


def test_beslut_kan_inte_foredatera_bedomning_eller_belagg(api,komplett):
    m,p,_=api
    from riskanalys.fel import RiskanalysFel
    _,_,_,paket=komplett
    d=m.Analysbeslut(tjanst=paket.tjanster[0].tjanst,revision=paket.revision,
        underlagssumma=p.underlagssumma(paket),svarssumma=p.svarssumma(paket),godkand=True,
        namn='Ada',roll='ansvarig',datum=date(2020,1,1))
    with pytest.raises(RiskanalysFel):p.registrera_beslut(paket,d)


def test_samverkan_och_slutsats_binds_till_andrad_sarbarhetsprovning(api,komplett):
    _,p,_=api
    _,_,_,paket=komplett;a=paket.tjanster[0]
    s=a.sarbarhetsprovningar[0].model_copy(update={'motivering':'Ändrad kundmix förändrar faktorernas samspel.'})
    nytt=paket.model_copy(update={'tjanster':(a.model_copy(update={'sarbarhetsprovningar':(s,*a.sarbarhetsprovningar[1:])}),)})
    for n in (8,13,14,16):assert p.blocksumma(nytt,a.tjanst,n)!=p.blocksumma(paket,a.tjanst,n)


@pytest.mark.parametrize('varde,status,inaktuell,med_dokument,tillaten',[
    ('ej_belagt','bekräftad',False,False,False),
    ('ej_belagt','bekräftad',False,True,False),
    (None,'saknas',False,False,False),
    (None,'saknas',False,True,False),
    ('belagt','bekräftad',True,False,False),
    ('belagt','bekräftad',True,True,False),
    ('belagt','bekräftad',False,False,True),
    ('belagt','bekräftad',False,True,True),
])
def test_positiv_tackning_kraver_belagt_genomforande_utan_profilmotsagelse(
        api,komplett,varde,status,inaktuell,med_dokument,tillaten):
    m,p,_=api
    from riskanalys.regelverk.modeller import Kontrollrackvidd,Kallhanvisning
    from riskanalys.profil.lagring import profilrevision
    rb,profil,b,paket=komplett;a=paket.tjanster[0];s=a.scenarier[0].model_copy(update={'relevans':'relevant'})
    cid=rb.tjanster[a.tjanst].kontroller[0];c=rb.kontroller[cid];f=c.genomforande_falt
    r=Kontrollrackvidd(id='r-p1',tjanst=a.tjanst,hot=s.hot,kan_belagga='Syntetisk observation.',
        begransningar='Endast synligt underlag.',forutsattningar='Prövat mandat.',grund='metodval',
        kallhanvisningar=(Kallhanvisning(kalla=c.kallor[0],avsnitt='syntetiskt',sida=1),),beskrivningsstatus='beskriven')
    cs=dict(rb.kontroller);cs[cid]=c.model_copy(update={'rackvidd':(r,)})
    rb=rb.model_copy(update={'kontroller':cs})
    upp=dict(profil.uppgifter);upp[f]=upp[f].model_copy(update={'varde':varde,'status':status,'inaktuell':inaktuell})
    profil=profil.model_copy(update={'uppgifter':upp})
    # Do not leave an unrelated inactive profile evidence reference that masks the actual control check.
    belagg=tuple(x for x in paket.belagg if f not in x.profilfalt)
    if med_dokument:
        be=m.Analysbelagg(id='utfort-p1',dokument='egenkontroll.bin',kontrollsumma='sha256:'+'a'*64,datum=date(2026,10,1))
    else:
        be=m.Analysbelagg(id='utfort-p1',profilfalt=(f,),datum=upp[f].datum,period=upp[f].period)
    paket=paket.model_copy(update={'bindning':paket.bindning.model_copy(update={'profilrevision':profilrevision(profil)}),
        'belagg':(*belagg,be)})
    cp=m.Kontrollprovning(scenario=s.id,kontroll=cid,rackvidd=(r.id,),tillampning='Utfört syntetiskt arbetsmoment.',
        utfall='Avgränsad verifierad observation.',belagg=(be.id,),tackning='delvis',kvarstar='Osynliga flöden kvarstår.')
    a=a.model_copy(update={'scenarier':(s,*a.scenarier[1:]),'kontroller':(cp,),
        'block':tuple(x.model_copy(update={'aktivering':'aktiv'}) if x.nummer in (10,11) else x for x in a.block)})
    paket=paket.model_copy(update={'tjanster':(a,)})
    a=a.model_copy(update={'block':tuple(x.model_copy(update={'bekraftad_summa':p.blocksumma(paket,a.tjanst,x.nummer)})
        if x.aktivering=='aktiv' else x for x in a.block)})
    fel=p.analysbrister(rb,profil,b,paket.model_copy(update={'tjanster':(a,)}))
    if tillaten:
        assert fel==()
    else:
        assert any('genomförand' in x.lower() for x in fel),fel


# Kronologi: daterat underlag för ett godkännande får inte ligga efter godkännandet.
# Frister och uppföljningsdatum är framåtblickande och får ligga i framtiden.
FRAMTID=date(2099,1,1)


def _bekraftad(p,paket):
    a=paket.tjanster[0]
    a=a.model_copy(update={'block':tuple(x.model_copy(update={'bekraftad_summa':p.blocksumma(paket,a.tjanst,x.nummer)})
        if x.aktivering=='aktiv' else x for x in a.block)})
    return paket.model_copy(update={'tjanster':(a,)})


def _med_uppdragsbeslut(p,paket,status,datum):
    a=paket.tjanster[0]
    u=a.uppdragsprovning.model_copy(update={'status':status,'handlingsalternativ':'begransa',
        'beslutsstatus':'beslutad','ansvar':'Ada','datum':datum})
    return _bekraftad(p,paket.model_copy(update={'tjanster':(a.model_copy(update={'uppdragsprovning':u}),)}))


def _attestdag(paket):
    return max([paket.bindning.bedomningsdatum,*[b.datum for b in paket.belagg]])


def _attest(m,p,paket,datum,godkand=True):
    return m.Analysbeslut(tjanst=paket.tjanster[0].tjanst,revision=paket.revision,
        underlagssumma=p.underlagssumma(paket),svarssumma=p.svarssumma(paket),godkand=godkand,
        namn='Bo',roll='ansvarig',datum=datum,kommentar=None if godkand else 'Uppdragsbeslutets datum måste rättas.')


def _lagrad_attest(m,p,paket,datum):
    """Som ett register sparat före kronologiregeln: godkännandet finns redan."""
    return paket.model_copy(update={'beslut':(_attest(m,p,paket,datum).model_copy(update={'forfattare':'Ada'}),)})


def _modellrisk(datum,**andring):
    from datetime import timedelta
    from riskanalys.drift.modellrisk import Modellbelagg,Modellriskunderlag
    ref=Modellbelagg(fil='syntetisk.bin',kontrollsumma='sha256:'+'a'*64)
    data=dict(modellansvarig='Syntetisk ansvarig',modellbindning='sha256:'+'b'*64,rutin=ref,
        valideringsrapport=ref,projektrapport=ref,modellfiler=ref,utvarderad=datum,
        nasta_genomgang=datum+timedelta(days=365),feluppfoljning='Syntetisk månatlig uppföljning.',fel=(),
        godkand=True,beslutad_av='Syntetisk beslutsfattare',beslutsdatum=datum)
    return Modellriskunderlag(**{**data,**andring})


@pytest.mark.parametrize('status',['kraver_atgard','kan_inte_hanteras'])
def test_framtida_uppdragsbeslut_bar_inte_godkannande(api,komplett,status):
    m,p,_=api
    from riskanalys.fel import RiskanalysFel
    rb,profil,b,paket=komplett
    dag=_attestdag(paket)
    paket=_med_uppdragsbeslut(p,paket,status,FRAMTID)
    # Innehållet är i övrigt komplett; bara kronologin stoppar godkännandet.
    assert p.analysbrister(rb,profil,b,paket)==()
    with pytest.raises(RiskanalysFel,match='uppdragsbeslutet har datum 2099-01-01'):
        p.registrera_beslut(paket,_attest(m,p,paket,dag))


@pytest.mark.parametrize('status',['kraver_atgard','kan_inte_hanteras'])
def test_lagrat_godkannande_med_framtida_uppdragsbeslut_ar_analysbrist(api,komplett,status):
    m,p,_=api
    from riskanalys.granskning.dokument_v6 import analyshinder
    rb,profil,b,paket=komplett
    paket=_lagrad_attest(m,p,_med_uppdragsbeslut(p,paket,status,FRAMTID),_attestdag(paket))
    assert p.gallande_beslut(paket,paket.tjanster[0].tjanst).godkand
    text='uppdragsbeslutet har datum 2099-01-01'
    assert any(text in f for f in p.analysbrister(rb,profil,b,paket))
    assert any(text in f for f in analyshinder(rb,profil,b,paket))


def test_uppdragsbeslut_samma_dag_som_godkannandet_godtas(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    dag=_attestdag(paket)
    paket=_med_uppdragsbeslut(p,paket,'kraver_atgard',dag)
    nytt=p.registrera_beslut(paket,_attest(m,p,paket,dag))
    assert p.gallande_beslut(nytt,paket.tjanster[0].tjanst).godkand
    assert p.analysbrister(rb,profil,b,nytt)==()


def test_framtida_uppfoljning_och_frist_hindrar_inte_godkannande(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    dag=_attestdag(paket)
    a=paket.tjanster[0]
    rutin=a.rutinatgarder[0].model_copy(update={'status':'beslutad','ansvar':'Ada','uppfoljning':FRAMTID})
    gap=m.Analysgap(id='g',typ='kontrollbrist',beskrivning='Känd avgränsad kontrollbrist.',
        status='accepterad_kvarstaende_risk',motivering='Kvarstående risk med ansvar och frist.',ansvar='Ada',tidsfrist=FRAMTID)
    paket=_bekraftad(p,paket.model_copy(update={'tjanster':(a.model_copy(update={'rutinatgarder':(rutin,),'gap':(gap,)}),)}))
    paket=_med_uppdragsbeslut(p,paket,'kraver_atgard',dag)
    nytt=p.registrera_beslut(paket,_attest(m,p,paket,dag))
    assert p.gallande_beslut(nytt,paket.tjanster[0].tjanst).godkand
    assert p.analysbrister(rb,profil,b,nytt)==()


def test_underkannande_far_dokumentera_framtida_uppdragsbeslut(api,komplett):
    m,p,_=api
    _,_,_,paket=komplett
    paket=_med_uppdragsbeslut(p,paket,'kraver_atgard',FRAMTID)
    nytt=p.registrera_beslut(paket,_attest(m,p,paket,_attestdag(paket),godkand=False))
    assert not p.gallande_beslut(nytt,paket.tjanster[0].tjanst).godkand


@pytest.mark.parametrize('falt,text',[
    ('beslutsdatum','modellriskbeslutet har datum'),
    ('utvarderad','modellutvärderingen har datum'),
    ('fel','modellfelet f1 har datum'),
])
def test_modellriskunderlag_efter_godkannandet_bar_inte_godkannande(api,komplett,falt,text):
    m,p,_=api
    from datetime import timedelta
    from riskanalys.drift.modellrisk import Modellfel
    from riskanalys.fel import RiskanalysFel
    rb,profil,b,paket=komplett
    dag=_attestdag(paket);senare=dag+timedelta(days=1)
    andring={'fel':{'fel':(Modellfel(id='f1',datum=senare,beskrivning='Syntetiskt övrigt fel.',allvar='ovrigt',
                status='atgardat',atgard_och_omprovning='Syntetiskt rättat.',belagg=()),)},
        'utvarderad':{'utvarderad':senare,'beslutsdatum':senare},
        'beslutsdatum':{'beslutsdatum':senare}}[falt]
    mr=_modellrisk(dag,**andring)
    paket=_bekraftad(p,paket.model_copy(update={'modellrisk':mr}))
    with pytest.raises(RiskanalysFel,match=text):
        p.registrera_beslut(paket,_attest(m,p,paket,dag))
    assert any(text in f for f in p.analysbrister(rb,profil,b,_lagrad_attest(m,p,paket,dag)))


def test_modellgenomgang_i_framtiden_hindrar_inte_godkannande(api,komplett):
    m,p,_=api
    rb,profil,b,paket=komplett
    dag=_attestdag(paket)
    paket=_bekraftad(p,paket.model_copy(update={'modellrisk':_modellrisk(dag)}))
    nytt=p.registrera_beslut(paket,_attest(m,p,paket,dag))
    assert p.gallande_beslut(nytt,paket.tjanster[0].tjanst).godkand
    assert p.analysbrister(rb,profil,b,nytt)==()


def test_lagrat_godkannande_fore_belagg_ar_analysbrist(api,komplett):
    m,p,_=api
    from datetime import timedelta
    rb,profil,b,paket=komplett
    dag=_attestdag(paket)
    senare=m.Analysbelagg(id='senare',dokument='senare.bin',kontrollsumma='sha256:'+'c'*64,datum=dag+timedelta(days=1))
    paket=_bekraftad(p,paket.model_copy(update={'belagg':(*paket.belagg,senare)}))
    assert any('belägget senare har datum' in f for f in p.analysbrister(rb,profil,b,_lagrad_attest(m,p,paket,dag)))
