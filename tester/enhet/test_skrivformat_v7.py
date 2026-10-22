"""V7:s sammanhängande analys och externa integritetsgräns."""
import pytest

from riskanalys.dokument.delvalidering import validera_del
from riskanalys.dokument.modeller import AISvar, AIStycke
from riskanalys.dokument.promptar import promptsumma, systemprompt
from riskanalys.dokument.promptar.delar import modultext
from riskanalys.dokument.skrivversion import V5, V6, V7, delar_for_version
from tester.enhet.test_verksamhetsval_v7 import bas, satt, tjanst


def svar(text='Underlaget behöver bedömas mot dokumenterade affärshändelser.', refs=None, typ='scenario', antal=180):
    text += ' underlag' * max(0, antal-len(text.split()))
    return AISvar(stycken=[AIStycke(typ=typ, referenser=refs or ['H-01','H-02','P-KUND.antal_aktiva'], text=text)], oklarheter=[])


def test_v7_en_del_med_bevarade_aldre_delar_och_v8_som_ny_default():
    assert delar_for_version(V7) == ('analys',)
    assert delar_for_version(V6) == ('hot','sarbarheter')
    assert len(delar_for_version(V5)) == 5
    from riskanalys.dokument.skrivversion import AKTUELL_SKRIVVERSION, V8
    from riskanalys.dokument.rapportversion import AKTUELL_DOKUMENTVERSION
    assert AKTUELL_SKRIVVERSION == AKTUELL_DOKUMENTVERSION == V8


def test_v7_prompt_kedja_omfang_och_kallbunden_kontroll():
    text=modultext('analys',formatversion=V7)
    for krav in ('uppdraget','utnyttjas','omständigheter','normalt inte visar','prövas lokalt','nämn',
                 'omfang','byra','tjanst','fördelningen','käll','160–320'):
        assert krav in text
    assert 'Skriv aldrig att sanktioner inte behöver prövas' in systemprompt('modell',formatversion=V7)
    assert systemprompt('modell',formatversion=V6)==systemprompt('modell')
    assert promptsumma('modell','analys',formatversion=V7)!=promptsumma('modell','hot',formatversion=V6)


@pytest.mark.parametrize('antal,giltig',[(159,False),(160,True),(320,True),(321,False)])
def test_v7_langd_motsvarar_verkligt_svar(faktablad_exempel,antal,giltig):
    fel=validera_del('analys',svar(antal=antal),faktablad_exempel,(),())
    assert (not any('ord;' in f for f in fel)) is giltig


@pytest.mark.parametrize('text,felord',[
    ('Riskbranscher prövas lokalt.','prövas lokalt'),
    ('Vi kontrollerar alltid kontoändringar.','kontroll'),
    ('Byrån stämmer av underlagen.','kontroll'),
    ('Vi har verifierat mottagaren.','kontroll'),
    ('Byrån har granskat bankflödet.','kontroll'),
    ('Kontrollen har varit effektiv.','effekt'),
    ('Avstämningen minskar risken.','minsk'),
    ('Sanktioner behöver inte prövas.','sanktioner'),
    ('Inga rapporter visar att hot saknas.','rapporter'),
])
def test_v7_forbjudna_lokala_utforande_och_effektpastaenden(faktablad_exempel,text,felord):
    fel=validera_del('analys',svar(text),faktablad_exempel,(),())
    assert any(felord in f.lower() for f in fel), fel


@pytest.mark.parametrize('text',[
    'En avstämning kan normalt visa skillnader mellan bokföring och bankdata.',
    'Om underlaget manipuleras kan en kontroll missa vem som faktiskt äger pengarna.',
    'Byrån bör granska kontounderlaget före ett beslut.',
    'Vi rekommenderar att byrån granskar avvikande transaktioner.',
    'Ingen anknytning till sanktioner har identifierats.',
])
def test_v7_tillater_generellt_kallbundet_resonemang_och_rad(faktablad_exempel,text):
    if 'sanktioner' in text:
        from riskanalys.dokument.faktablad import Faktapost
        nej=Faktapost(id='P-GEO.sanktionsanknytning',etikett='Identifierad sanktionsanknytning',
            visningsvarde='nej',status='bekräftad',period=None,kalltyp=None)
        faktablad_exempel=faktablad_exempel.model_copy(update={'poster':(*faktablad_exempel.poster,nej)})
    assert validera_del('analys',svar(text),faktablad_exempel,(),())==[]


def test_v7_kraver_hot_tf_och_samband(faktablad_exempel):
    fb=faktablad_exempel.model_copy(update={'tf_hot':('H-02',)})
    fel=validera_del('analys',svar(refs=['H-01']),fb,(),())
    assert any('minst två hot' in f for f in fel)
    assert any('terrorfinansiering' in f for f in fel)
    assert any('hot och en sårbarhet eller uppgift' in f for f in fel)
    fel=validera_del('analys',svar('Faktorerna samverkar.',refs=['H-01','H-02','P-KUND.antal_aktiva','T-RED-01'],typ='analys'),fb,(),())
    # Ett byråantal belägger inte ett överlapp mellan två faktorer.
    from riskanalys.dokument.modeller import UnderlagSarbarhet
    fb=fb.model_copy(update={'sarbarheter':(UnderlagSarbarhet(id='S-A',namn='Faktor',galler='ja'),)})
    fel=validera_del('analys',svar('Faktorerna samverkar.',refs=['H-01','H-02','S-A','P-KUND.antal_aktiva'],typ='analys'),fb,(),())
    assert any('kombination utan belagt överlapp' in f for f in fel)


def test_v7_kontrollrackvidd_ar_offentlig_kallbunden_och_tjanstbunden(bas):
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    t=tjanst(rb,p)
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    for k in fb.kontroller:
        katalog=rb.kontroller[k.id]
        assert k.beskrivning==katalog.beskrivning
        assert k.kallor==katalog.kallor
        assert len(k.rackvidd)==len([r for r in katalog.rackvidd if r.tjanst==t.tjanst])
        for r in k.rackvidd:
            original=next(x for x in katalog.rackvidd if x.id==r.id)
            assert r.kan_belagga==original.kan_belagga
            assert r.begransningar==original.begransningar
            assert r.forutsattningar==original.forutsattningar
            assert r.kallhanvisningar==original.kallhanvisningar
            assert r.hot==original.hot
            assert r.tjanst==t.tjanst
            assert 'sakkunnig' not in r.model_dump()
    old=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V6)
    assert all(set(k)=={'id','namn','status'} for k in old.model_dump()['kontroller'])


def skriv(rb,p,t,texter,namn=()):
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.delskrivning import skriv_tjanst
    lev=Testleverantor(texter)
    res=skriv_tjanst(lev,rb,p,t,'D-ARB.6.1',formatversion=V7,effort='medium',personnamn=namn,spara=lambda *args:None)
    return res,tuple(a.model_dump_json().encode() for a in lev.delanrop)


def test_v7_ett_anrop_godkant_resultat_och_aterlasning(bas):
    from riskanalys.dokument.delskrivning import Tjanstresultat, kontrollera_resultat
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    t=tjanst(rb,p)
    # Katalogens TF-hot ska vara med; ingen privat eller obekräftad referens behövs.
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    refs=[h.id for h in fb.hot]+[s.id for s in fb.sarbarheter if s.galler != 'prövas lokalt']+['P-KUND.antal_aktiva']
    res,kedja=skriv(rb,p,t,[svar(refs=refs)])
    assert len(kedja)==1 and res.del_('analys').godkant_svar
    assert Tjanstresultat.model_validate_json(res.model_dump_json())==res
    assert any(u.omfang=='tjanst' for u in res.faktablad.poster)
    kontrollera_resultat(rb,p,t,res,'D-ARB.6.1',formatversion=V7)


def test_v7_kategorichecklista_kvarstar_nar_retrybyter_fel(bas):
    import json
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb, p = bas
    p = p.model_copy(update={'uppgifter': {**p.uppgifter,
        **{id: p.uppgifter[id].model_copy(update={'varde': varde}) for id, varde in {
            'P-KANAL.bankdata_andel': 0.75, 'P-KANAL.andel_digitalt_underlag': 0.75,
            'P-KANAL.antal_bankdata': 75, 'P-KANAL.antal_digitalt_underlag': 75}.items()}}})
    t = tjanst(rb, p)
    fb = bygg_faktablad(rb, p, t, 'D-ARB.6.1', formatversion=V7)
    synliga = [s for s in fb.sarbarheter if s.galler != 'prövas lokalt']
    nej = [s.id for s in synliga if s.galler == 'nej' and fb.sarbarhetsomraden[s.id] in ('kanal', 'verk')]
    assert {fb.sarbarhetsomraden[id] for id in nej} == {'kanal', 'verk'}
    refs = [h.id for h in fb.hot] + [s.id for s in synliga] + ['P-KUND.antal_aktiva']
    res, kedja = skriv(rb, p, t, [svar(refs=[r for r in refs if r not in nej]),
                               svar(refs=refs, antal=321), svar(refs=refs, antal=240)])
    forsok = res.del_('analys').forsok
    assert len(forsok) == len(kedja) == 3
    assert any('kategori kanal' in f for f in forsok[0].fel)
    assert any('kategori verk' in f for f in forsok[0].fel)
    assert all('kategori' not in f for f in forsok[1].fel)
    assert any('321 ord' in f for f in forsok[1].fel)
    assert res.del_('analys').godkant_svar and not forsok[2].fel
    uppgifter = []
    for begaran in kedja:
        block = json.loads(begaran)['innehall']
        uppgift = next(b['text'] for b in block if b['text'].startswith('<uppgift'))
        for krav in ('S-ID', 'ja, nej eller okänt', 'kund = kunder', 'kanal = distributionskanaler',
                     'geo = geografi', 'tj = tjänstespecifika', 'verk = verksamhetsspecifika',
                     '240–280 ord', '160–320 ord', 'Återberätta inte rapporteringsantal',
                     'lokala låsta delen', 'överlåt dem till programmet'):
            assert krav in uppgift, krav
        uppgifter.append(uppgift)
    assert uppgifter[0] == uppgifter[1] == uppgifter[2]
    senaste = json.loads(kedja[2])['innehall'][-1]['text']
    assert senaste.startswith('<aterkoppling>') and '321 ord' in senaste and 'kategori' not in senaste


RAPPORTAVGRANSNING = 'Få eller inga misstankerapporter visar inte att uppläggen saknas hos byrån.'


def rapportsvar(text, efter=()):
    # Fyll före meningen så att regressionen behåller verkliga försökets meningsgräns.
    return AISvar(stycken=[AIStycke(typ='analys', referenser=['H-01', 'H-02', 'P-KUND.antal_aktiva'],
        text='Underlaget behöver prövas. ' + 'Underlag kräver prövning. ' * 54 + text),
        *[AIStycke(typ='motivering', referenser=['H-01'], text=t) for t in efter]], oklarheter=[])


@pytest.mark.parametrize('fore', ['',
    'Bankdata visar att en lön har betalats, men inte att den anställde finns eller har arbetat. '
    'Konsulter med kort erfarenhet arbetar inte självständigt. '])
def test_v7_rapporteringsavgransning_har_kvar_konservativ_sparr(faktablad_exempel, fore):
    # Känd falskpositiv: prompten överlåter egenrapportering till den lokala låsta delen.
    # En språklig dispens skulle även kunna dölja senare osäkra slutsatser.
    analys = rapportsvar(fore + RAPPORTAVGRANSNING, efter=(
        'Katalogens kontroll beskriver prövning av underlag. Scenariotäckningen är okänd.',))
    assert validera_del('analys', analys, faktablad_exempel, (), ()) == [
        'Få eller inga rapporter får inte användas som belägg för att hotet är litet.']


@pytest.mark.parametrize('text,efter', [
    ('Få rapporter visar att hot saknas.', ()),
    ('Noll rapporter innebär låg risk.', ()),
    ('Inga rapporter tyder på att uppläggen saknas.', ()),
    ('Få rapporter visar inte att hot finns.', ()),
    ('Få rapporter visar inte att risken är hög.', ()),
    (RAPPORTAVGRANSNING + ' Därför kan hoten avfärdas.', ()),
    (RAPPORTAVGRANSNING + ' Därför är risken låg.', ()),
    (RAPPORTAVGRANSNING[:-1] + ', men därför kan hoten avfärdas.', ()),
    (RAPPORTAVGRANSNING[:-1] + '; därför kan hoten avfärdas.', ()),
    (RAPPORTAVGRANSNING, ('Därför kan hoten avfärdas.',)),
    (RAPPORTAVGRANSNING, ('Därför är risken låg.',)),
    (RAPPORTAVGRANSNING, ('Hoten kan avfärdas.',)),
    (RAPPORTAVGRANSNING, ('Uppläggen saknas hos byrån.',)),
    (RAPPORTAVGRANSNING, ('Det finns inga hot hos byrån.',)),
    (RAPPORTAVGRANSNING, ('Risken är låg.',)),
    (RAPPORTAVGRANSNING, ('Uppläggen kan uteslutas.',)),
    (RAPPORTAVGRANSNING, ('Byrån saknar sådana hot.',)),
    (RAPPORTAVGRANSNING, ('Få rapporter visar att hot saknas.',)),
    ('Inga rapporter visar att hot saknas. ' + RAPPORTAVGRANSNING, ()),
    ('Det är fel att säga: ' + RAPPORTAVGRANSNING, ()),
])
def test_v7_rapporteringsavgransning_doljer_inte_osaker_slutsats(faktablad_exempel, text, efter):
    fel = validera_del('analys', rapportsvar(text, efter), faktablad_exempel, (), ())
    assert any('rapporter' in f.lower() for f in fel), fel


@pytest.mark.parametrize('del_id', ['hot', 'sarbarheter'])
def test_aldre_delar_behover_inte_nytt_rapporteringsundantag(faktablad_exempel, del_id):
    fel = validera_del(del_id, rapportsvar(RAPPORTAVGRANSNING), faktablad_exempel, (), ())
    assert any('rapporter' in f.lower() for f in fel) is (del_id == 'hot')


def test_v7_hela_begaran_inklusive_retry_identisk_vid_privata_variationer(bas):
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    p2=satt(p,**{'P-TJ.red01_arbetssatt':'PRIVAT MARKÖR', 'P-TJ.red01_antal_utland_transaktion':2})
    from riskanalys.profil.omfattning import HARLEDNING
    from riskanalys.intag.underlag import EGEN_KANNEDOM
    p2=p2.model_copy(update={'uppgifter':{id:u.model_copy(update={
        'kalla':u.kalla if not u.kalla or u.kalla.startswith(HARLEDNING) or u.kalla==EGEN_KANNEDOM else 'PRIVAT KÄLLA',
        'bekraftad_av':'Privat Namn'}) for id,u in p2.uppgifter.items()}})
    t=tjanst(rb,p)
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    bra=svar('Privat Namn kan förekomma i lokal dokumentation.',refs=[h.id for h in fb.hot]+[s.id for s in fb.sarbarheter if s.galler != 'prövas lokalt']+['P-KUND.antal_aktiva'])
    res1,k1=skriv(rb,p,t,['felaktig JSON',bra])
    res2,k2=skriv(rb,p2,tjanst(rb,p2),['felaktig JSON',bra],namn=('Privat Namn',))
    assert len(k1)==len(k2)==2 and k1==k2
    assert not res1.del_('analys').mall
    assert res2.del_('analys').mall and res2.del_('analys').lokal_sparr=='personnamn'
    assert b'PRIVAT' not in b''.join(k2)


def test_v7_schema_version_och_kallreferenser_finns_i_faktabladet(bas):
    from riskanalys.dokument.aischema import ai_schema
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    fb=bygg_faktablad(rb,p,tjanst(rb,p),'D-ARB.6.1',formatversion=V7)
    schema=ai_schema(fb.tillatna_id(),fb.uppgift_id(),formatversion=V7)
    assert schema != ai_schema(fb.tillatna_id(),fb.uppgift_id(),formatversion=V6)
    ids=schema['properties']['stycken']['items']['properties']['referenser']['items']['enum']
    for k in fb.kontroller:
        for id in (*k.kallor,*(r.id for r in k.rackvidd)):
            assert id in ids


def test_v7_saknat_kallstod_ger_explicit_okand_rackvidd(bas):
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    t=tjanst(rb,p)
    k=rb.kontroller[t.kontroller[0].id]
    rb=rb.model_copy(update={'kontroller':{**rb.kontroller,k.id:k.model_copy(update={'kallor':(),'rackvidd':()})}})
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    kontroll=next(x for x in fb.kontroller if x.id==k.id)
    assert kontroll.rackviddsstatus=='okand'
    assert kontroll.beskrivning is None and kontroll.rackvidd==()
    assert 'rackviddsstatus' in kontroll.model_dump()
    assert 'okand' in modultext('analys',formatversion=V7)


def test_v7_privata_och_skyddade_referenser_far_inte_skrivas(faktablad_exempel):
    from riskanalys.dokument.modeller import UnderlagSarbarhet
    from riskanalys.dokument.faktablad import Faktapost
    fb=faktablad_exempel.model_copy(update={
        'sarbarheter':(UnderlagSarbarhet(id='S-LOKAL',namn='Lokalt prövad',galler='prövas lokalt'),),
        'poster':(*faktablad_exempel.poster,Faktapost(id='P-SKYDDAD',etikett='Skyddad',visningsvarde='skyddat',period=None,kalltyp=None,status='skyddad'))})
    for id in ('S-LOKAL','P-SKYDDAD'):
        fel=validera_del('analys',svar(refs=['H-01','H-02',id]),fb,(),())
        assert any('Utelämna' in f for f in fel)


@pytest.mark.parametrize('text',[
    'I uppdraget granskar byrån bankflödena.',
    'Därför verifierar vi betalningsmottagaren.',
    'Vi har alltid kontrollerat mottagarens konto.',
])
def test_v7_fangar_omvand_ordfoljd_for_utford_kontroll(faktablad_exempel,text):
    assert any('genomförd kontroll' in f for f in validera_del('analys',svar(text),faktablad_exempel,(),()))


@pytest.mark.parametrize('text',[
    'Om byrån granskar underlaget kan en differens upptäckas.',
    'Vid en tänkt avstämning verifierar byrån mottagaren om underlag finns.',
])
def test_v7_tillater_uttryckligt_hypotetiska_kontrollbeskrivningar(faktablad_exempel,text):
    assert validera_del('analys',svar(text),faktablad_exempel,(),())==[]


def test_testleverantor_far_riktiga_v7_svar_utan_att_aldre_svar_andras(bas):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from tester.fixturer.m2 import bygg_delsvar, godkant_delsvar
    rb,p=bas
    b=bedom(rb,valj(rb,p.byra.regelpaket,p.byra.datum,p.byra.lan),p)
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    tjanster=[t for _,t in tjanster_med_avsnitt(b)]
    aldre=[godkant_delsvar(d,t).model_dump_json() for t in tjanster for d in ('hot','sarbarheter')]
    v7=bygg_delsvar(rb,p,b,formatversion=V7)
    assert len(v7)==len(tjanster)
    for t,text in zip(tjanster,v7):
        res,kedja=skriv(rb,p,t,[text])
        assert len(kedja)==1 and res.del_('analys').godkant_svar
    assert aldre==[godkant_delsvar(d,t).model_dump_json() for t in tjanster for d in ('hot','sarbarheter')]


@pytest.mark.parametrize('version',[V5,V6])
def test_aldre_resultat_lases_och_serialiseras_identiskt(bas,tmp_path,version):
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.delskrivning import skriv_tjanst, Tjanstresultat
    from riskanalys.dokument.skrivning import las_skrivresultat
    rb,p=bas
    t=tjanst(rb,p)
    res=skriv_tjanst(Testleverantor(['felaktig JSON']*15),rb,p,t,'D-ARB.6.1',formatversion=version,
        effort='medium',personnamn=(),spara=lambda *args:None)
    data=res.model_dump_json()
    (tmp_path/'resultat.json').write_text(data)
    assert las_skrivresultat(tmp_path)==[res]
    assert Tjanstresultat.model_validate_json(data).model_dump_json()==data
    assert all(set(k)=={'id','namn','status'} for k in res.faktablad.model_dump()['kontroller'])


def test_v7_lasta_privata_meningar_provas_forst_efter_alla_anrop(bas,monkeypatch):
    from riskanalys.dokument import delskrivning
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    t=tjanst(rb,p)
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    refs=[h.id for h in fb.hot]+[s.id for s in fb.sarbarheter if s.galler!='prövas lokalt']+['P-KUND.antal_aktiva']
    bra=svar('En privat men oskyldig låst mening.',refs=refs)
    # Isolera just efterkontrollens ordning; övriga tester använder riktiga lokala byggare.
    anropade=[]
    def lasta(*args,**kwargs):
        anropade.append(True)
        return ('En privat men oskyldig låst mening.',)
    monkeypatch.setattr(delskrivning,'lasta_texter',lasta)
    res1,k1=skriv(rb,p,t,['ogiltig JSON',bra])
    assert anropade and res1.del_('analys').mall
    monkeypatch.setattr(delskrivning,'lasta_texter',lambda *args,**kwargs:('Annan privat mening.',))
    res2,k2=skriv(rb,p,t,['ogiltig JSON',bra])
    assert k1==k2 and len(k1)==2 and not res2.del_('analys').mall


def test_v7_far_inte_markas_om_till_v6(bas):
    from riskanalys.dokument.delskrivning import Tjanstresultat
    from pydantic import ValidationError
    rb,p=bas
    res,_=skriv(rb,p,tjanst(rb,p),['ogiltig JSON']*3)
    with pytest.raises(ValidationError,match='ordning'):
        Tjanstresultat.model_validate({**res.model_dump(),'formatversion':V6})


@pytest.mark.parametrize('varde,visning,status',[(True,'ja','bekräftad'),(False,'nej','bekräftad'),(None,'okänt','okänd')])
def test_v7_sanktionspolicy_kraver_belagg_aven_vid_ja_och_okant(bas,varde,visning,status):
    import json
    rb,p=bas
    id=next(id for id in rb.falt if 'sanktion' in id.lower() and rb.falt[id].typ=='bool')
    u=p.uppgifter[id].model_copy(update={'varde':varde,'status':status})
    p=p.model_copy(update={'uppgifter':{**p.uppgifter,id:u}})
    res,kedja=skriv(rb,p,tjanst(rb,p),['ogiltig JSON']*3)
    post=next(u for u in res.faktablad.poster if u.id==id)
    assert (post.visningsvarde,post.status)==(visning,status)
    for begaran in kedja:
        text=json.loads(begaran)['system']
        assert 'bara när faktabladet belägger' in text
        assert 'ja eller okänd' in text


def test_v7_systemexempel_respekterar_byraomfang():
    text=systemprompt('modell',formatversion=V7)
    assert '{tal:P-KUND.andel_riskbransch} av kunderna i tjänsten' not in text
    assert '{tal:P-KUND.andel_riskbransch} av byråns kunder' in text


@pytest.mark.parametrize('text',[
    'Kontrollen har genomförts på kundernas betalningar.',
    'Avstämningen är utförd.',
    'Kontrollens effekt är belagd.',
])
def test_v7_avvisar_passiva_utforande_och_effektpastaenden(faktablad_exempel,text):
    assert any('kontroll' in f.lower() for f in validera_del('analys',svar(text),faktablad_exempel,(),()))


@pytest.mark.parametrize('varde',[True,False,None])
def test_v7_sanktionsutlost_omforsok_fornekar_inte_ja_eller_okant(bas,varde):
    import json
    from riskanalys.dokument.faktablad import bygg_faktablad
    rb,p=bas
    id='P-GEO.sanktionsanknytning'
    u=p.uppgifter[id].model_copy(update={'varde':varde,'status':'bekräftad' if varde is not None else 'okänd'})
    p=p.model_copy(update={'uppgifter':{**p.uppgifter,id:u}})
    t=tjanst(rb,p)
    fb=bygg_faktablad(rb,p,t,'D-ARB.6.1',formatversion=V7)
    refs=[h.id for h in fb.hot]+[s.id for s in fb.sarbarheter if s.galler!='prövas lokalt']+['P-KUND.antal_aktiva']
    felaktigt=svar('Sanktioner behöver inte prövas.',refs=refs)
    franvaro=svar('Ingen anknytning till sanktioner har identifierats.',refs=refs)
    neutralt=svar('Sanktionsreglerna gäller fortfarande och prövningen får inte utelämnas.',refs=refs)
    resultat,kedja=skriv(rb,p,t,[felaktigt,franvaro,neutralt])
    assert len(kedja)==(2 if varde is False else 3)
    del_=resultat.del_('analys')
    assert del_.godkant_svar==(franvaro if varde is False else neutralt)
    for begaran in kedja[1:]:
        feedback=next(b['text'] for b in json.loads(begaran)['innehall'] if b['text'].startswith('<aterkoppling>'))
        assert 'Skriv att ingen anknytning har identifierats.' not in feedback
    if varde is not False:
        assert any('belagt nej' in f for f in del_.forsok[1].fel)


@pytest.mark.parametrize('text',[
    'Ingen anknytning till sanktioner har identifierats.',
    'Ingen sanktionsanknytning har identifierats.',
    'Ingen anknytning har identifierats.',
])
@pytest.mark.parametrize('varde',[True,None,False])
def test_v7_sanktionsfranvaro_kraver_offentligt_bekraftat_nej(faktablad_exempel,text,varde):
    from riskanalys.dokument.faktablad import Faktapost
    post=Faktapost(id='P-GEO.sanktionsanknytning',etikett='Identifierad sanktionsanknytning',
        visningsvarde='ja' if varde else 'nej' if varde is False else 'okänt',
        status='bekräftad' if varde is not None else 'okänd',period=None,kalltyp=None)
    fb=faktablad_exempel.model_copy(update={'poster':(*faktablad_exempel.poster,post)})
    fel=validera_del('analys',svar(text),fb,(),())
    assert any('belagt nej' in f for f in fel) is (varde is not False)
