"""Regressioner för Claude Codes granskning 2026-10-10. Endast syntetiska data."""
from datetime import datetime, timedelta, timezone
from argparse import Namespace
from io import BytesIO
import pytest
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.svar import besvara
from riskanalys.profil.lagring import spara_profil, profilrevision
from tester.fixturer.m2 import DAG
from tester.intag.test_webb import webb, anrop, starta
from tester.foretagsdata.test_scb import post, ORG


def svar(falt, **kw):
    return IntagSvar(falt=falt, text='Syntetiskt svar', kalla='Testunderlag', datum=DAG, roll='Test', **kw)


@pytest.mark.parametrize('tecken', ['\x00', '\x0b', '\ud800', '\ufffe'])
def test_1_intag_avvisar_xml_ogiltig_text(klar, rb_intag, tecken):
    with pytest.raises((RiskanalysFel, ValueError), match='styrtecken|XML'):
        besvara(rb_intag, klar, svar('P-TJ.red01_arbetssatt', **{}).model_copy(update={'text':'Rad ett'+tecken+'Rad två'}))


def test_1_cli_avvisar_xml_ogiltigt_underlag(klar, rb_intag):
    from riskanalys.profil.hantering import bekrafta
    with pytest.raises(RiskanalysFel, match='styrtecken|XML'):
        bekrafta(klar, rb_intag, 'P-TJ.red01_arbetssatt', 'Rad\x0bTvå', 'Test', 'Test', DAG)


def test_1_handediterad_profil_stoppas_fore_ai(webb, klar, monkeypatch):
    from riskanalys.intag import dokument
    s,t=webb
    u=klar.uppgifter['P-TJ.red01_arbetssatt'].model_copy(update={'varde':'Rad\x0bTvå'})
    p=klar.model_copy(update={'uppgifter':{**klar.uppgifter,'P-TJ.red01_arbetssatt':u}})
    spara_profil(t.mapp,p)
    anrop=[]
    monkeypatch.setattr(dokument,'kor_skrivning',lambda *a: anrop.append(a))
    with pytest.raises(RiskanalysFel,match='styrtecken|XML'):
        dokument.skapa_utkast(t.mapp,t.rb,object())
    assert not anrop


def test_2_samma_skrivformular_far_inte_kora_ai_tva_ganger(webb,klar,monkeypatch):
    import re
    from riskanalys.intag import webb as modul
    s,t=webb;spara_profil(t.mapp,klar);s.leverantor=object()
    html=anrop(s,'?oversikt=1')[1]
    token=re.search(r'name="skrivtoken" value="([^"]+)"',html)
    assert token, 'Skrivformuläret saknar engångstoken'
    anrop_ai=[]
    def skapa(*a):
        anrop_ai.append(a)
        raise RiskanalysFel('Syntetiskt exportfel efter skrivning')
    monkeypatch.setattr(modul,'skapa_utkast',skapa)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),skrivtoken=token[1])
    assert anrop(s,'skriv',d)[0]==400
    status,html,_=anrop(s,'skriv',d)
    assert status==409 and 'redan' in html
    assert len(anrop_ai)==1


def cli_args():
    return Namespace(byra='syntetisk',regelbas=None,falt='P-TJ.red01_arbetssatt',varde='Ändrat syntetiskt arbetssätt',kalla='Test',roll='Test',datum=DAG,period_fran=None,period_till=None,ej_tillampligt=False,motivering=None)


@pytest.mark.parametrize('argument,grans', [
    ('varde', 12000), ('--roll', 200), ('--kalla', 2000), ('--motivering', 2000),
])
def test_3_cli_for_langt_intagssvar_ger_fel_utan_profilandring(
    tmp_path, monkeypatch, klar, rb_intag, capsys, argument, grans,
):
    from riskanalys.cli import main
    from riskanalys.kommandon import profil_kommando as k
    from riskanalys.lagring.datamapp import byramapp
    from riskanalys.profil.lagring import PROFILFIL
    monkeypatch.setenv('RISKANALYS_DATA', str(tmp_path))
    monkeypatch.setattr(k, 'ladda_giltig_regelbas', lambda _: rb_intag)
    mapp = byramapp('syntetisk')
    spara_profil(mapp, klar)
    fore = (mapp / PROFILFIL).read_bytes()
    for_langt = 'X' * (grans + 1)
    args = ['bekrafta', 'syntetisk', 'P-TJ.red01_arbetssatt',
            for_langt if argument == 'varde' else 'Syntetiskt svar', '--kalla', 'Test']
    if argument != 'varde':
        args += [argument, for_langt]
    assert main(args) == 1
    fel = capsys.readouterr().err
    assert fel.startswith('Fel:') and str(grans) in fel
    assert ('värdet' if argument == 'varde' else argument) in fel
    assert 'Traceback' not in fel and 'ValidationError' not in fel and for_langt not in fel
    assert (mapp / PROFILFIL).read_bytes() == fore
    assert not (mapp / PROFILFIL.parent / 'historik').exists()


@pytest.mark.parametrize('argument,grans', [('varde', 12000), ('roll', 200)])
def test_3_cli_intagssvar_vid_langdgransen_sparas(tmp_path, monkeypatch, klar, rb_intag, argument, grans):
    from riskanalys.kommandon import profil_kommando as k
    from riskanalys.lagring.datamapp import byramapp
    from riskanalys.profil.lagring import las_profil
    monkeypatch.setenv('RISKANALYS_DATA', str(tmp_path))
    monkeypatch.setattr(k, 'ladda_giltig_regelbas', lambda _: rb_intag)
    mapp = byramapp('syntetisk')
    spara_profil(mapp, klar)
    args = cli_args()
    setattr(args, argument, 'X' * grans)
    assert k.kor_bekrafta(args) == 0
    uppgift = las_profil(mapp).uppgifter[args.falt]
    assert uppgift.varde == args.varde and uppgift.bekraftad_av == 'roll:' + args.roll


def test_3_cli_andring_gor_belaggen_inaktuella(webb,klar,monkeypatch):
    from riskanalys.kommandon import profil_kommando as k
    s,t=webb;spara_profil(t.mapp,klar)
    monkeypatch.setattr(k,'ladda_giltig_regelbas',lambda _:t.rb)
    assert k.kor_bekrafta(cli_args())==0
    assert t.profil().uppgifter['P-KONTROLL.C-TJ-01.belagg'].inaktuell
    assert t.profil().uppgifter['P-KONTROLL.C-TJ-01.genomforande'].inaktuell


def test_3_cli_skriver_inte_over_samtidigt_webbsvar(webb,klar,monkeypatch):
    from riskanalys.kommandon import profil_kommando as k
    from riskanalys.profil import forandringar as f
    s,t=webb;spara_profil(t.mapp,klar)
    monkeypatch.setattr(k,'ladda_giltig_regelbas',lambda _:t.rb)
    spar=f.spara_profil
    def konkurrens(mapp,p,**kw):
        ny=besvara(t.rb,t.profil(),svar('P-ORG.namn').model_copy(update={'text':'Nyare webbsvar'}))
        spar(mapp,ny)
        return spar(mapp,p,**kw)
    monkeypatch.setattr(f,'spara_profil',konkurrens)
    with pytest.raises(RiskanalysFel,match='ändrats'):
        k.kor_bekrafta(cli_args())
    assert t.profil().uppgifter['P-ORG.namn'].varde=='Nyare webbsvar'


def test_4_registerstart_kraver_egen_filialkalla(webb):
    import json
    from riskanalys.foretagsdata.lagring import las_bild
    s,t=webb
    assert anrop(s,'registerimport',dict(csrf=s.csrf,orgnr=ORG,jsontext=json.dumps(post())))[0]==200
    b=las_bild(t.mapp)
    d=dict(csrf=s.csrf,bildsumma=b.summa,ratt_byra='ja',filial='nej',datum=str(DAG),roll='Test',**{'val_P-ORG.sateslan':'ja'})
    assert anrop(s,'skapa',d)[0]==400 and not t.finns()
    d['filialkalla']='Byråns eget registreringsbevis'
    assert anrop(s,'skapa',d)[0]==200
    assert t.profil().uppgifter['P-ORG.utlandsk_filial'].kalla==d['filialkalla']
    assert b.summa in t.profil().uppgifter['P-ORG.sateslan'].kalla


def test_5_senare_registerbild_ersatter_inte_anvandbar(webb):
    from riskanalys.foretagsdata.scb import tolka_scb
    from riskanalys.foretagsdata.lagring import spara_bild,las_bild
    s,t=webb;starta(s)
    b=tolka_scb(post(),ORG,'lokal_json')
    spara_bild(t.mapp,b)
    senare=b.model_copy(update={'hamtad':datetime.combine(DAG+timedelta(days=1),datetime.min.time(),tzinfo=timezone.utc)})
    with pytest.raises(RiskanalysFel,match='bedömningsdatum|historisk'):
        spara_bild(t.mapp,senare)
    assert las_bild(t.mapp)==b


def test_6_vet_inte_bevarar_tidigare_belagg(klar,rb_intag):
    id='P-TJ.red01_arbetssatt';gammal=klar.uppgifter[id]
    ny=besvara(rb_intag,klar,svar(id,status='okänt',motivering='Kontrollera uppgiften igen'))
    u=ny.uppgifter[id]
    assert (u.varde,u.kalla,u.bekraftad_av,u.datum,u.period)==(gammal.varde,gammal.kalla,gammal.bekraftad_av,gammal.datum,gammal.period)
    assert not ny.ar_bekraftad(id)
    assert ny.uppgifter['P-KONTROLL.C-TJ-01.belagg'].inaktuell


def test_7_vet_inte_utan_roll_gar_att_spara(webb):
    s,t=webb;starta(s)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),falt='P-ORG.namn',status='okänt',text='',kalla='',roll='',datum=str(DAG),motivering='Kontrolleras senare')
    status,html,_=anrop(s,'svar',d)
    assert status==200,html
    assert not t.profil().ar_bekraftad('P-ORG.namn')


def test_8_djupt_scb_svar_ger_atgarderbart_fel():
    from riskanalys.foretagsdata.scb import SCBLeverantor
    provider=SCBLeverantor(nyckel='endast-test',transport=lambda *a,**kw:BytesIO(('['*30000+']'*30000).encode()))
    with pytest.raises(RiskanalysFel,match='JSON'):
        provider.hamta(ORG)


def test_1_webbfel_pekar_pa_texten_och_inte_datum(webb):
    s,t=webb;starta(s)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),falt='P-ORG.namn',status='bekräftad',text='Rad\x0bTvå',kalla='Test',roll='Test',datum=str(DAG))
    status,html,_=anrop(s,'svar',d)
    assert status==400 and 'styrtecken' in html and 'Skriv datum som' not in html
    assert not t.profil().ar_bekraftad('P-ORG.namn')


def test_10_exportfel_visas_inte_som_datumfel(webb,klar,monkeypatch):
    from riskanalys.intag import webb as modul
    s,t=webb;spara_profil(t.mapp,klar);s.leverantor=object()
    def fel(*a):raise ValueError('All strings must be XML compatible')
    monkeypatch.setattr(modul,'skapa_utkast',fel)
    d=dict(csrf=s.csrf,revision=profilrevision(t.profil()),skrivtoken=s.skrivtoken(profilrevision(t.profil())))
    status,html,_=anrop(s,'skriv',d)
    assert status==400 and 'Word-utkastet kunde inte skapas' in html
    assert 'Skriv datum som' not in html


def test_okant_bevarar_period_och_visar_tidigare_kalla(webb,klar):
    from riskanalys.intag import vyer
    s,t=webb;spara_profil(t.mapp,klar)
    id='P-KUND.antal_aktiva';fore=t.profil().uppgifter[id]
    t.spara(svar(id,status='okänt',motivering='Kontrollera perioden igen'),profilrevision(t.profil()))
    u=t.profil().uppgifter[id]
    assert u.period==fore.period and u.datum==fore.datum
    html=vyer.fragesida(s,id)
    assert str(fore.varde) in html and fore.kalla in html and str(fore.period.fran) in html
    assert 'Tidigare värde och belägg' in html


def test_lansbyte_ar_tillatet_men_omprovar_underlaget(klar,rb_intag):
    from riskanalys.regelverk.tillsyn import rattlig_omfattning
    p=besvara(rb_intag,klar,svar('P-ORG.sateslan').model_copy(update={'text':'Skåne'}))
    assert p.byra.lan=='Skåne' and p.byra.regelpaket=='RP-RED-SKANE'
    assert p.uppgifter['P-TJ.red01_arbetssatt'].inaktuell
    assert not any('låst' in h or 'säteslän' in h for h in rattlig_omfattning(rb_intag,p).hinder)


def test_scb_klasser_ar_avstamda_mot_variabelbeskrivning():
    from riskanalys.intag.registervy import klass,ANST,OMS
    assert len(ANST)==17 and len(OMS)==13
    assert klass('0',ANST)=='Uppgift saknas'
    assert klass('1',ANST)=='0 anställda'
    assert klass('2',ANST)=='1–4 anställda'
    assert klass('16',ANST)=='10 000 eller fler anställda'
    assert klass('0',OMS,' tkr')=='under 1 tkr'
    assert klass('1',OMS,' tkr')=='1–499 tkr'
    assert klass('12',OMS,' tkr')=='över 9 999 999 tkr'


def test_ovrigt_svar_laker_inte_handredigerad_lanskonflikt(klar,rb_intag):
    from riskanalys.regelverk.tillsyn import rattlig_omfattning
    u=klar.uppgifter['P-ORG.sateslan'].model_copy(update={'varde':'Stockholm'})
    p=klar.model_copy(update={'uppgifter':{**klar.uppgifter,'P-ORG.sateslan':u}})
    assert rattlig_omfattning(rb_intag,p).hinder
    ny=besvara(rb_intag,p,svar('P-TJ.red01_arbetssatt').model_copy(update={'text':'Annan syntetisk arbetsbeskrivning'}))
    assert ny.byra==p.byra
    assert any('stämmer inte' in h for h in rattlig_omfattning(rb_intag,ny).hinder)


def test_aterbekraftat_lan_omprovar_belagg_vid_paketbyte(klar,rb_intag):
    u=klar.uppgifter['P-ORG.sateslan'].model_copy(update={'varde':'Stockholm'})
    p=klar.model_copy(update={'uppgifter':{**klar.uppgifter,'P-ORG.sateslan':u}})
    ny=besvara(rb_intag,p,svar('P-ORG.sateslan').model_copy(update={'text':'Stockholm'}))
    assert ny.byra.lan=='Stockholm' and ny.byra.regelpaket=='RP-RED-STHLM'
    assert ny.uppgifter['P-TJ.red01_arbetssatt'].inaktuell
    assert ny.uppgifter['P-KONTROLL.C-TJ-01.belagg'].inaktuell
