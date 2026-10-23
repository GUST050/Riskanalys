"""H7.1: kontraster i faktaunderlag; inga verkliga byråuppgifter eller AI-anrop."""
from importlib import import_module

import pytest


def bygg(rb, rot, fall):
    try:
        modul = import_module('tester.fixturer.rapportlasprov')
    except ModuleNotFoundError:
        pytest.fail('H7.1:s rapportläsprov saknas')
    return modul.bygg_rapportlasprov(rb, rot, fall)


def test_inaktiv_nollfordelning_bevarar_noll_och_synlig_osakerhet(regelbas_v1, tmp_path):
    """En legitimt inaktiv frivillig fråga får inte skapa falsk inaktualitet."""
    from tester.fixturer.analys_hela_kedjan import skapa_fall
    from riskanalys.dokument.lokaldata_v8 import _giltigt_lokalt_fordelningssvar, inaktiv_frivillig_fordelning, uppgiftsrad
    from riskanalys.intag.fordelning import kan_ateranvandas, underlagsbindning
    f = skapa_fall(regelbas_v1, tmp_path)
    id = 'P-TJ.red01_antal_kontant'
    assert f.profil.uppgifter[id].varde == 0
    assert f.profil.uppgifter['P-KUND.antal_kontant'].varde == 0
    obunden = uppgiftsrad(regelbas_v1, f.profil, id)
    assert 'Registrerat värde 0' in obunden.celler[1].text
    assert 'saknar aktuell underlagsbindning' in obunden.celler[1].text
    assert '[VERIFIERA]' not in obunden.celler[1].text
    u=f.profil.uppgifter[id].model_copy(update={'underlagsbindning':underlagsbindning(regelbas_v1,f.profil,id)})
    profil=f.profil.model_copy(update={'uppgifter':{**f.profil.uppgifter,id:u}})
    assert not kan_ateranvandas(regelbas_v1, profil, id)
    assert inaktiv_frivillig_fordelning(regelbas_v1,profil,id)=='byråns bekräftade faktorbas är 0'
    assert _giltigt_lokalt_fordelningssvar(regelbas_v1,profil,id,u)
    rad = uppgiftsrad(regelbas_v1, profil, id)
    assert '0' in rad.celler[1].text
    assert 'frivillig fördelning är inaktiv' in rad.celler[1].text.lower()
    assert 'inaktuellt eller oförenligt' not in rad.celler[1].text
    assert '[VERIFIERA]' not in rad.celler[1].text
    assert str(profil.uppgifter[id].period.fran) in rad.celler[2].text
    assert profil.uppgifter[id].kalla in rad.celler[3].text
    assert rad.celler[1].referenser == (id,)


def test_inaktiv_fordelning_vid_en_tjanst_och_utelamnad_frivillig_fraga(regelbas_v1, tmp_path):
    from dataclasses import replace
    from riskanalys.dokument.lokaldata_v8 import uppgiftsrad
    from riskanalys.intag.fordelning import kan_ateranvandas, underlagsbindning
    from riskanalys.profil.modeller import Period, Uppgift
    from datetime import date
    f = bygg(regelbas_v1, tmp_path, 'fyra_tjanster')
    id = 'P-TJ.red01_antal_kontant'
    period = Period(fran=date(2026,1,1), till=date(2026,9,30))
    upp = dict(f.profil.uppgifter)
    upp['P-KUND.antal_kontant'] = upp['P-KUND.antal_kontant'].model_copy(update={'varde':2,'period':period})
    for n in range(2,5):
        upp[f'P-TJ.red0{n}_erbjuds'] = upp[f'P-TJ.red0{n}_erbjuds'].model_copy(update={'varde':False})
    upp[id] = upp[id].model_copy(update={'varde':0,'period':period})
    profil = f.profil.model_copy(update={'uppgifter':upp})
    upp = dict(profil.uppgifter)
    upp[id] = upp[id].model_copy(update={'underlagsbindning':underlagsbindning(regelbas_v1,profil,id)})
    profil = profil.model_copy(update={'uppgifter':upp})
    f = replace(f,profil=profil)
    assert not kan_ateranvandas(regelbas_v1,profil,id)
    rad = uppgiftsrad(regelbas_v1,profil,id)
    assert '0' in rad.celler[1].text and '[VERIFIERA]' not in rad.celler[1].text
    assert 'frivillig fördelning är inaktiv' in rad.celler[1].text.lower()

    upp = dict(profil.uppgifter)
    upp[id] = Uppgift()
    utan_svar = profil.model_copy(update={'uppgifter':upp})
    rad = uppgiftsrad(regelbas_v1,utan_svar,id)
    assert 'frivillig fördelning efterfrågas inte' in rad.celler[1].text.lower()
    assert '[VERIFIERA]' not in rad.celler[1].text


def test_fordelning_har_eget_omfang_och_period(regelbas_v1, tmp_path):
    from riskanalys.intag.fordelning import tjanstefordelning
    f = bygg(regelbas_v1, tmp_path, 'fyra_tjanster')
    assert f.profil.uppgifter['P-KUND.antal_aktiva'].varde == 120
    assert [f.profil.uppgifter[f'P-TJ.red0{i}_antal_kunder'].varde for i in range(1, 5)] == [100, 110, 100, 45]
    u = f.profil.uppgifter['P-TJ.red04_antal_utland_transaktion']
    assert u.varde == 6
    assert (u.period.fran.isoformat(), u.period.till.isoformat()) == ('2026-01-01', '2026-09-30')
    assert tjanstefordelning(regelbas_v1, f.profil, 'T-RED-04')['P-GEO.antal_utland_transaktion'] == 6
    g = bygg(regelbas_v1, tmp_path/'annan', 'olika_perioder')
    assert 'P-GEO.antal_utland_transaktion' not in tjanstefordelning(regelbas_v1, g.profil, 'T-RED-04')


def test_okant_ar_inte_noll(regelbas_v1, tmp_path):
    from riskanalys.intag.fordelning import tjanstefordelning
    from riskanalys.regelverk.villkor import Kunskap
    f = bygg(regelbas_v1, tmp_path, 'okand_fordelning')
    id = 'P-TJ.red04_antal_utland_transaktion'
    assert f.profil.uppgifter[id].varde is None
    assert not f.profil.ar_bekraftad(id)
    assert f.profil.faltvarden()[id].kunskap == Kunskap.OKAND
    assert 'P-GEO.antal_utland_transaktion' not in tjanstefordelning(regelbas_v1, f.profil, 'T-RED-04')
    assert f.profil.uppgifter['P-GEO.antal_utland_transaktion'].varde == 22


def test_rutin_ar_inte_effektbelagg(regelbas_v1, tmp_path):
    f = bygg(regelbas_v1, tmp_path, 'ingen_belagd_effekt')
    assert f.profil.uppgifter['P-KONTROLL.C-TJ-04.utformning'].varde == 'finns'
    assert f.profil.uppgifter['P-KONTROLL.C-TJ-04.genomforande'].varde == 'belagt'
    assert f.profil.uppgifter['P-KONTROLL.C-TJ-04.effekt'].varde == 'ej_bedömd'
    assert f.profil.uppgifter['P-BESK.rutiner'].varde
    from riskanalys.analys.provning import faktisk_reduktion
    assert all(not faktisk_reduktion(t) for t in f.bedomning.tjanster if t.erbjuds)


@pytest.mark.parametrize('fall', ['fyra_tjanster','utan_betalningsmandat','med_betalningsmandat',
    'okand_fordelning','olika_perioder','ingen_belagd_effekt','motstridig_analys',
    'liten_exponerad_tjanst','tvingat_tjansteoverlapp','ej_tvingat_tjansteoverlapp'])
def test_varje_fall_binder_faktisk_profil_och_omraknad_motor(regelbas_v1, tmp_path, fall):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.profil.lagring import profilrevision
    f = bygg(regelbas_v1, tmp_path, fall)
    p = f.profil
    assert f.bedomning == bedom(regelbas_v1, valj(regelbas_v1, p.byra.regelpaket, p.byra.datum, p.byra.lan), p)
    assert f.analys.bindning.profilrevision == profilrevision(p)
    assert f.analys.beslut == ()
    assert all(b.bekraftad_summa is None for t in f.analys.tjanster for b in t.block)


def test_mandatfallen_skildrar_faktiska_olika_befogenheter(regelbas_v1, tmp_path):
    a = bygg(regelbas_v1, tmp_path/'utan', 'utan_betalningsmandat')
    b = bygg(regelbas_v1, tmp_path/'med', 'med_betalningsmandat')
    assert a.profil.uppgifter['P-TJ.red04_betalningsmandat'].varde == 'inget'
    assert b.profil.uppgifter['P-TJ.red04_betalningsmandat'].varde == 'verkstaller'
    assert a.analys.tjanster[-1].betalningsinsyn != b.analys.tjanster[-1].betalningsinsyn


def test_motsagelse_bevarar_bada_uppgifter_och_oppet_gap(regelbas_v1, tmp_path):
    f = bygg(regelbas_v1, tmp_path, 'motstridig_analys')
    t = next(t for t in f.analys.tjanster if t.tjanst == 'T-RED-04')
    assert f.profil.uppgifter['P-TJ.red04_betalningsmandat'].varde == 'inget'
    assert 'verkställer betalningar' in t.betalningsinsyn.motivering
    assert any(g.typ == 'motstridigt_underlag' and g.status == 'oppet' for g in t.gap)


def test_liten_tjanst_bevarar_exponeringens_lokala_namnare(regelbas_v1, tmp_path):
    from riskanalys.intag.fordelning import tjanstefordelning
    f = bygg(regelbas_v1, tmp_path, 'liten_exponerad_tjanst')
    assert f.profil.uppgifter['P-TJ.red04_antal_kunder'].varde == 6
    assert f.profil.uppgifter['P-KUND.antal_aktiva'].varde == 120
    assert tjanstefordelning(regelbas_v1, f.profil, 'T-RED-04')['P-GEO.antal_utland_transaktion'] == 6


@pytest.mark.parametrize('fall,antal,grans', [('tvingat_tjansteoverlapp',24,12), ('ej_tvingat_tjansteoverlapp',10,0)])
def test_overlapp_ar_en_harledd_grans_utan_exakt_antal_eller_identiteter(regelbas_v1, tmp_path, fall, antal, grans):
    f = bygg(regelbas_v1, tmp_path, fall)
    from tester.fixturer.rapportlasprov import overlappsunderlag
    u = overlappsunderlag(f)
    assert u['aktiva_kunder'] == 60
    assert u['tjansteantal'] == [antal]*4
    assert u['tjanstekopplingar'] == antal*4
    assert u['minst_flera_tjanster'] == grans
    assert u['exakt_antal'] is None
    assert u['kundidentiteter'] is None
    assert u['specifika_tjanstepar'] is None
    assert u['riskkategori_overlapp'] is None
    assert u['antaganden'] and u['berakning']
    # Oberoende konkret vittne: 12 fyrtjänstkunder + 48 entjänstkunder.
    if grans:
        kunder = [[1,1,1,1]]*12 + [[1,0,0,0]]*12 + [[0,1,0,0]]*12 + [[0,0,1,0]]*12 + [[0,0,0,1]]*12
    else:
        kunder = [[1,0,0,0]]*10 + [[0,1,0,0]]*10 + [[0,0,1,0]]*10 + [[0,0,0,1]]*10 + [[0,0,0,0]]*20
    assert len(kunder) == 60
    assert [sum(k[i] for k in kunder) for i in range(4)] == [antal]*4
    assert sum(sum(k)>1 for k in kunder) == grans


def test_okant_fall_avvisas(regelbas_v1, tmp_path):
    with pytest.raises(ValueError, match='Okänt'):
        bygg(regelbas_v1, tmp_path, 'felskrivet')


def test_baslinje_fryser_offline_skript_begaran_motor_analys_och_v7_export(regelbas_v1, tmp_path):
    import json
    from hashlib import sha256
    f = bygg(regelbas_v1, tmp_path/'fall', 'fyra_tjanster')
    from tester.fixturer.rapportlasprov import frys_b_offline
    mapp = frys_b_offline(f, tmp_path/'fryst')
    manifest = json.loads((mapp/'manifest.json').read_text())
    assert manifest['baslinje'] == 'B-offline'
    assert manifest['format'] == 'D-ARB-tjanst-v7'
    assert {'profil.json','bedomning.json','analys.json','testleverantor-skript.json','forvantade-anropsbytes.json','dokument.json','V7-UTKAST.docx'} <= manifest['filer'].keys()
    for fil, summa in manifest['filer'].items():
        assert sha256((mapp/fil).read_bytes()).hexdigest() == summa
    assert len(json.loads((mapp/'forvantade-anropsbytes.json').read_text())) == 4
    assert manifest['regelbas'] == regelbas_v1.kontrollsumma
    assert manifest['ai_text'] == 'Testleverantor; inte B-live:s verkliga AI-text'
    with pytest.raises(FileExistsError):
        frys_b_offline(f, mapp)


def test_mandatvariant_har_inga_oavsiktliga_motsagelser(regelbas_v1,tmp_path):
    a=bygg(regelbas_v1,tmp_path/'utan','utan_betalningsmandat')
    b=bygg(regelbas_v1,tmp_path/'med','med_betalningsmandat')
    assert 'Kunden genomför löneutbetalningen' in a.profil.uppgifter['P-TJ.red04_arbetssatt'].varde
    assert 'Kunden genomför löneutbetalningen' not in b.profil.uppgifter['P-TJ.red04_arbetssatt'].varde
    assert 'Byrån verkställer betalningar' in b.profil.uppgifter['P-TJ.red04_arbetssatt'].varde
    assert 'Kunden godkänner och genomför alla betalningar' not in b.profil.uppgifter['P-BESK.verksamhet'].varde


def test_komplettering_binder_oforandrad_baslinje_och_alla_fynd(regelbas_v1,tmp_path):
    import json
    from hashlib import sha256
    from tester.fixturer.rapportlasprov import frys_b_offline
    f=bygg(regelbas_v1,tmp_path/'fall','fyra_tjanster')
    rot=frys_b_offline(f,tmp_path/'bas')
    assert (rot/'fynd.json').is_file()
    fynd=json.loads((rot/'fynd.json').read_text())
    assert fynd and all(p['status']=='öppen' for p in fynd)
    assert all(p['id'] in (rot/'fyndpresentation.json').read_text() for p in fynd)
    assert json.loads((rot/'granskning.json').read_text())['blockerande'] > 0
    from tester.fixturer.rapportlasprov import komplettera_b_offline
    fore={p.name:p.read_bytes() for p in rot.iterdir() if p.is_file()}
    extra=komplettera_b_offline(f,rot,tmp_path/'komplement')
    manifest=json.loads((extra/'manifest.json').read_text())
    assert manifest['ursprungsmanifest_sha256']==sha256(fore['manifest.json']).hexdigest()
    assert all((rot/namn).read_bytes()==data for namn,data in fore.items())
    assert json.loads((extra/'fynd.json').read_text()) == fynd


def test_v7_frysta_anropsbytes_och_motor_bestaar(regelbas_v1,tmp_path):
    """Fryst kompatibilitetsprov: ändrat offentligt AI-kontrakt/motor syns."""
    import json
    from tester.fixturer.rapportlasprov import frys_b_offline
    # Frysta bytes använder sin ursprungliga katalog, inte senare metodbeslut.
    import gzip
    from pathlib import Path
    from riskanalys.regelverk.modeller import Regelbas
    regelbas_v1=Regelbas.model_validate_json(gzip.decompress(
        (Path(__file__).parents[1]/"fixturer/promptar_v5_v6_regelbas_2_0_0.json.gz").read_bytes()))
    f=bygg(regelbas_v1,tmp_path/'fall','fyra_tjanster')
    rot=frys_b_offline(f,tmp_path/'fryst')
    h=json.loads((rot/'manifest.json').read_text())['filer']
    assert h['forvantade-anropsbytes.json']=='9c043a4d83c7aaa0a54f57e68f023db9a5ca12cbc5a937992828cb69fe8bdb47'
    # Källbunden katalogmetadata ändrar bindningen, inte den frysta motorberäkningen.
    from hashlib import sha256
    bedomning=json.loads((rot/'bedomning.json').read_text())
    assert bedomning['regelbas_kontrollsumma']==regelbas_v1.kontrollsumma
    bedomning['regelbas_kontrollsumma']='sha256:7e0f77726a35b5e9fd47b8d324b43236cbeab5ded78c107ccfe54570cc97285f'
    gamla_bytes=(json.dumps(bedomning,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    assert sha256(gamla_bytes).hexdigest()=='09b519f8d5f7ef960ff6dc5cb324a85753ff9ccb825f51e98ff1986ef2c15d39'
    assert h['profil.json']=='5d105915d92480d8fbdff77f077fd0c342c7f38a840c9dbbb219f869348f9caa'


def test_mandatvariantens_hela_analys_foljer_mandat_utan_pahittad_kontrolleffekt(regelbas_v1,tmp_path):
    import json
    utan=bygg(regelbas_v1,tmp_path/'utan','utan_betalningsmandat')
    med=bygg(regelbas_v1,tmp_path/'med','med_betalningsmandat')
    a=next(t for t in utan.analys.tjanster if t.tjanst=='T-RED-04')
    b=next(t for t in med.analys.tjanster if t.tjanst=='T-RED-04')
    assert 'Byrån verkställer' in b.scenarier[0].handelseforlopp
    assert all('Byrån verkställer' in c.tillampning for c in b.kontroller)
    assert 'betalningsmandat' in b.sektorsjamforelse and 'förfogar inte' not in b.sektorsjamforelse
    assert 'kontoutdrag' in b.betalningsinsyn.synliga_floden
    assert 'inga kontoutdrag' not in b.betalningsinsyn.synliga_floden
    text=json.dumps(b.model_dump(mode='json'),ensure_ascii=False)
    for motsagelse in ('Kunden genomför löneutbetalningen',
        'Faktisk utbetalning och slutmottagare syns inte i tjänsten',
        'Byrån förfogar inte över kundmedel eller betalningsmandat'):
        assert motsagelse not in text
    assert [c.utfall for c in b.kontroller] == [c.utfall for c in a.kontroller]
    assert [c.tackning for c in b.kontroller] == [c.tackning for c in a.kontroller]
    assert 'inte' in b.betalningsinsyn.motivering and 'kontroll' in b.betalningsinsyn.motivering
    assert 'återringning' in b.gap[0].beskrivning and b.gap[0].status=='oppet'
    assert b.rutinatgarder[0].status=='foreslagen'
    assert med.profil.uppgifter['P-KONTROLL.C-TJ-04.effekt'] == utan.profil.uppgifter['P-KONTROLL.C-TJ-04.effekt']
