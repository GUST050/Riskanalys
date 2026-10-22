"""Hela privata schema-2-paketet får inte påverka begäranden, inte ens omförsök."""
import json
from dataclasses import replace
import pytest
from tester.conftest import regelbas_v1
from tester.fixturer.analys_hela_kedjan import skapa_fall,skriv_fall,placera_privat_analys
from riskanalys.analys import modeller as m
from riskanalys.analys.gemensam import forifyll_gemensamt,postsumma


@pytest.mark.parametrize('skript,antal',[('normal',8),('omforsok',9),('reserv',10)])
def test_hela_schema_tva_privata_begaran_ar_bytevis_oforandrad(regelbas_v1,tmp_path,monkeypatch,skript,antal):
    f=skapa_fall(regelbas_v1,tmp_path.resolve());baseline,requests=skriv_fall(f,skript=skript)
    assert len(requests)==antal
    def forbjuden(*args,**kwargs):pytest.fail('Skrivkedjan försökte läsa privat analys')
    monkeypatch.setattr('riskanalys.analys.lagring.las_analys',forbjuden)
    for riktning in ('lagre','mojlig_underskattning'):
        p=forifyll_gemensamt(f.regelbas,f.analys)
        g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={
            'beskrivning':'PRIVAT-SCHEMA2-KUND-X','motivering':'PRIVAT-SCHEMA2-MEKANISM-X',
            'forfattare':'PRIVAT-SCHEMA2-FORFATTARE-X','status':'bekraftad','relevans':'relevant','belagg':(p.belagg[0].id,)})
        v=p.gemensamma_verksamhetsposter[0].model_copy(update={'text':'PRIVAT-SCHEMA2-LEVERANTOR-X','forfattare':'PRIVAT-SCHEMA2-ANSVAR-X',
            'leverantorer':(m.Leverantorsprovning(id='privat-leverantor',omfattning='PRIVAT-SCHEMA2-OMFATTNING-X',
                egen_verifiering='PRIVAT-SCHEMA2-EGENKONTROLL-X',ansvar='PRIVAT-SCHEMA2-ANSVAR-X'),)})
        app=m.Sarbarhetstillampning(post=g.id,postsumma=postsumma(g),bekraftad=True,stallningstagande='galler_annorlunda',
            motivering='PRIVAT-SCHEMA2-AVVIKELSE-X',belagg=g.belagg,hotkopplingar=(m.Hotanknytning(hot='H-03',dimension='tf'),),
            riktningsval=m.Riktningsval(riktning=riktning,motivering='PRIVAT-SCHEMA2-RIKTNING-X',belagg=g.belagg))
        prov=m.Tackningsprovning(ursprung='gemensam',post=g.id,hot='H-03',dimension='pt',stallningstagande='tacks_av_scenario',
            jamforelseniva='hög',lokalt_scenario='gem:H-03',motivering='PRIVAT-SCHEMA2-TACKNING-X',
            referensmotivering='PRIVAT-SCHEMA2-REFERENS-X',forfattare='PRIVAT-SCHEMA2-GRANSKARE-X',belagg=g.belagg,visad_summa='sha256:'+'a'*64)
        t=p.tjanster[0].model_copy(update={'sarbarhetstillampningar':(app,),'tackningsprovningar':(prov,)})
        p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,*p.gemensamma_sarbarhetsprovningar[1:]),
            'gemensamma_verksamhetsposter':(v,*p.gemensamma_verksamhetsposter[1:]),'tjanster':(t,*p.tjanster[1:])})
        variant=replace(f,analys=p);placera_privat_analys(variant)
        resultat,andra=skriv_fall(variant,skript=skript)
        assert andra==requests and len(resultat)==len(baseline)
        assert 'PRIVAT-' not in json.dumps(andra,ensure_ascii=False)
