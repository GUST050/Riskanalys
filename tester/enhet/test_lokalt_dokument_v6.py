"""Lokala resonemang och bevismetadata följer med utan AI-beslut eller filinläsning."""
from datetime import date
import pytest
from riskanalys.analys import modeller as m
from riskanalys.analys.provning import registrera_beslut, svarssumma, underlagssumma
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.dokument.arb_v6 import bygg_arb_v6
from riskanalys.dokument.rendering import synliga_texter
from riskanalys.profil.lagring import profilrevision
from tester.enhet.test_arb_v6 import v6underlag
from tester.fixturer.lokal_analys import bekraftat_utkast


def texter(d, *, huvud=False):
    return '\n'.join(text for a in d.avsnitt if not huvud or a.id != 'D-ARB.B1' for text in synliga_texter(a))


@pytest.fixture
def lokal(v6underlag):
    rb, profil, b, resultat, h = v6underlag
    bindning = m.Analysbindning(byra=profil.byra.id, profilrevision=profilrevision(profil),
        bedomningsmanifest='bedömning', utkastmanifest='utkast', regelbas=rb.kontrollsumma,
        kallunderlag='källor', historik='historik', bedomningsdatum=b.datum, modell='sha256:'+'a'*64)
    paket = bekraftat_utkast(forifyll_analys(rb, profil, b, bindning), rb)
    t = paket.tjanster[0]
    belagg = m.Analysbelagg(id='lokalt-prov', dokument='hemlig-kundakt.bin', kontrollsumma='sha256:'+'f'*64, datum=b.datum)
    scenario = m.Scenarioanalys(id='lokalt-scenario', rubrik='Fakturor utan leverans', hot=tuple(rb.tjanster[t.tjanst].hot[:1]),
        handelseforlopp='En faktura döljer en utebliven leverans.', relevans='relevant', motivering='Fakturainsynen gäller affärens underlag.',
        belagg=(belagg.id,), delanalyser=('faktura',))
    t = t.model_copy(update={'scenarier': (*t.scenarier, scenario),
        'delanalyser': (m.Delanalys(id='faktura', rubrik='Fakturabokföring', arbetsmoment_och_befogenheter='Kontering med begränsad betalningsinsyn.', belagg=(belagg.id,)),),
        'delningsmotivering': 'Fakturor och utlandsflöden kräver skilda resonemang.',
        'betalningsinsyn': m.Betalningsinsyn(status='bedomd', synliga_floden='Synligt bankkonto stäms av.', insynsluckor='Utländska mellanled saknas.',
            avsandare_och_mottagare='Affärsmotparter kan inte alltid följas.', underlagens_tillforlitlighet='Kontoutdrag styrker betalning men inte leverans.', motivering='Uppdraget ger begränsad insyn.', belagg=(belagg.id,)),
        'kontroller': (m.Kontrollprovning(scenario=scenario.id, kontroll=rb.tjanster[t.tjanst].kontroller[0], tillampning='Bankrader jämförs med reskontra.', utfall='En avvikelse återstår.',
            belagg=(belagg.id,), tackning='delvis', kvarstar='Leveransens existens är fortfarande osäker.'),),
        'sarbarhetsprovningar': tuple(s.model_copy(update={'motivering': 'Lokal betydelse för '+s.omrade, 'scenarier': (scenario.id,)}) for s in t.sarbarhetsprovningar),
        'samverkan': 'Ofullständiga fakturor och osynliga mellanled förstärker osäkerheten.',
        'pt_motivering': 'PT kräver prövning av fakturornas ekonomiska innebörd.', 'tf_motivering': 'TF kräver separat prövning av betalningsändamålet.',
        'rutinatgarder': (m.Rutinatgard(id='rutin', scenarier=(scenario.id,), atgard='Begär leveransunderlag före avslut.', rutin_id='RUT-FAKTURA', rutin_version='2', rutinbelagg=belagg.id,
            status='beslutad', ansvar='Kontrollansvarig', utlosare_eller_frekvens='Vid leveransavvikelse.', uppfoljning=date(2026,12,1), belagg=(belagg.id,)),),
        'slutsats': 'Uppdragets insynsluckor kräver dokumenterad uppföljning.'})
    return paket.model_copy(update={'belagg': (*paket.belagg, belagg), 'tjanster': (t,*paket.tjanster[1:])})


def test_v6_bevarar_lokala_resonemang_och_tydliga_rutinstatusar(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    huvud = texter(d, huvud=True)
    for text in ('Ofullständiga fakturor och osynliga mellanled', 'Lokal betydelse för kund', 'Lokal betydelse för kanal',
                 'Lokal betydelse för geo', 'Lokal betydelse för verk', 'PT kräver prövning', 'TF kräver separat',
                 'Fakturabokföring', 'Utländska mellanled saknas.', 'Leveransens existens är fortfarande osäker.',
                 'Begär leveransunderlag före avslut.', 'RUT-FAKTURA', '2026-12-01', 'beslutad'):
        assert text in huvud
    a = d.avsnitt_med_id()[next(iter(v6underlag[3]))]
    assert any(t.id.endswith('-scenarier') for t in a.tabeller)
    assert any(s.proveniens == 'lokal' and lokal.tjanster[0].samverkan in s.text for s in a.stycken)
    assert not any(s.proveniens == 'ai' and lokal.tjanster[0].samverkan in s.text for s in a.stycken)


def test_v6_gemensamt_scenario_visas_en_gang_med_tjanstkoppling(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    s = lokal.gemensamma_scenarier[0]
    assert texter(d).count(s.handelseforlopp) == 1
    assert 'gemensamma scenarier' in texter(d, huvud=True).lower()
    for id in v6underlag[3]:
        assert any(t.id.endswith('-scenarier') for t in d.avsnitt_med_id()[id].tabeller)


def test_v6_b1_visar_hash_datum_och_kalla_utan_privata_filvagar(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    text = texter(d)
    b1 = '\n'.join(synliga_texter(d.avsnitt_med_id()['D-ARB.B1']))
    assert 'sha256:'+'f'*64 in b1
    assert 'hemlig-kundakt.bin' not in text
    assert 'Syntetisk testkälla' in b1
    assert not any('hemlig-kundakt.bin' in ref for a in d.avsnitt for s in a.stycken for ref in s.referenser)


def test_v6_visar_egen_granskning_och_inaktuell_analys(v6underlag, lokal):
    t = lokal.tjanster[0]
    beslut = m.Analysbeslut(tjanst=t.tjanst, revision=lokal.revision, underlagssumma=underlagssumma(lokal),
        svarssumma=svarssumma(lokal), godkand=True, namn=t.forfattare, roll='Ansvarig', datum=v6underlag[2].datum)
    paket = registrera_beslut(lokal, beslut)
    d = bygg_arb_v6(*v6underlag, analys=paket)
    assert 'samma person' in '\n'.join(s.text for s in d.avsnitt_med_id()['D-ARB.8'].stycken).lower()
    paket = paket.model_copy(update={'bindning': paket.bindning.model_copy(update={'profilrevision': 'gammal'})})
    d = bygg_arb_v6(*v6underlag, analys=paket)
    assert 'Profilen har ändrats' in texter(d)
    assert '[VERIFIERA]' in texter(d, huvud=True)


def test_identiska_kontrollprovningar_grupperas_med_alla_scenariokopplingar(v6underlag, lokal):
    t = lokal.tjanster[0]
    k = t.kontroller[0]
    annan = t.scenarier[0].id
    paket = lokal.model_copy(update={'tjanster': (t.model_copy(update={'kontroller': (k, k.model_copy(update={'scenario': annan}))}), *lokal.tjanster[1:])})
    d = bygg_arb_v6(*v6underlag, analys=paket)
    tab = next(tab for a in d.avsnitt for tab in a.tabeller if tab.id == t.tjanst+'-kontrollprovning')
    assert len(tab.rader) == 1
    refs = set(ref for c in tab.rader[0].celler for ref in c.referenser)
    assert {'ANALYS:scenario:'+k.scenario, 'ANALYS:scenario:'+annan} <= refs
    andrad = t.model_copy(update={'kontroller': (k, k.model_copy(update={'scenario': annan, 'utfall': 'Ett annat faktiskt utfall.'}))})
    d = bygg_arb_v6(*v6underlag, analys=lokal.model_copy(update={'tjanster': (andrad, *lokal.tjanster[1:])}))
    tab = next(tab for a in d.avsnitt for tab in a.tabeller if tab.id == t.tjanst+'-kontrollprovning')
    assert len(tab.rader) == 2


def test_faktisk_m1_rapportstatus_och_begransningar_visas_utan_felakter(v6underlag, lokal):
    from riskanalys.drift.modellrapport import Modellvalidering, valideringens_innehallssumma
    from riskanalys.drift.modellrisk import Modellbelagg, Modellriskunderlag, Modellfel
    from riskanalys.regelverk.modeller import Sakkunnig
    dag = v6underlag[2].datum
    belagg = Modellbelagg(fil='privat-rapport.pdf', kontrollsumma='sha256:'+'b'*64)
    descriptor = Modellbelagg(fil='privat-rapport.json', kontrollsumma='sha256:'+'c'*64)
    rapport = Modellvalidering(modellbindning=lokal.bindning.modell, modellfiler_kontrollsumma=belagg.kontrollsumma,
        rapport_kontrollsumma=belagg.kontrollsumma, rapportversion='syntetisk-1', datum=dag, tillampningsomrade='Syntetiska tjänster.',
        fall_och_facit='Syntetiskt facit.', faktiska_utfall='Provade fall.', avvikelser='Dokumenterade.',
        begransningar='Gäller bara det dokumenterade syntetiska urvalet.', verkliga_driftobservationer='Inga verkliga driftobservationer.', m1_beslut='godkant')
    rapport = rapport.model_copy(update={'sakkunnig': Sakkunnig(status='verifierad', av='Syntetisk expert', datum=dag, kontrollsumma=valideringens_innehallssumma(rapport))})
    mr = Modellriskunderlag(modellansvarig='Syntetisk ansvarig', modellbindning=lokal.bindning.modell, rutin=belagg,
        valideringsrapport=belagg, projektrapport=descriptor, modellfiler=belagg, utvarderad=dag, nasta_genomgang=date(2027,10,1),
        feluppfoljning='Privat arbetsrutin.', godkand=True, beslutad_av='Syntetisk Ada', beslutsdatum=dag,
        fel=(Modellfel(id='privat-fel', datum=dag, beskrivning='KUNDIDENTIFIERANDE-FELAKT', allvar='vasentligt', status='oppet', atgard_och_omprovning='Privat feltext.', belagg=(belagg,)),))
    paket = lokal.model_copy(update={'modellrisk': mr})
    d = bygg_arb_v6(*v6underlag, analys=paket, modellrapport=rapport)
    text = texter(d)
    assert 'M1 godkänt' in text and 'giltigt sakkunnigverifierad' in text
    assert rapport.begransningar in text
    assert 'KUNDIDENTIFIERANDE-FELAKT' not in text and 'privat-rapport.pdf' not in text
    assert 'öppet väsentligt modellfel' in text.lower()
    utan = bygg_arb_v6(*v6underlag, analys=paket)
    assert 'M1 och rapportens sakkunnigstatus är inte styrkta' in texter(utan)
    utan_identitet = rapport.model_copy(update={'sakkunnig': Sakkunnig(status='verifierad', kontrollsumma=valideringens_innehallssumma(rapport))})
    d = bygg_arb_v6(*v6underlag, analys=paket, modellrapport=utan_identitet)
    assert 'inte giltigt sakkunnigverifierad' in texter(d)
    annan_modell = rapport.model_copy(update={'modellbindning': 'sha256:'+'d'*64})
    d = bygg_arb_v6(*v6underlag, analys=paket, modellrapport=annan_modell)
    assert 'M1 är inte styrkt' in texter(d)


def test_exakt_gemensam_lokaltext_bevarar_per_tjanst_tillampning_och_refs(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    text = lokal.tjanster[0].erfarenhetsprovning
    assert texter(d, huvud=True).count(text) == 1
    gem = d.avsnitt_med_id()['D-ARB.5']
    assert any(text in s.text for s in gem.stycken)
    for id in v6underlag[3]:
        a = d.avsnitt_med_id()[id]
        assert any('D-ARB.5' in s.referenser and 'gäller för denna tjänst' in s.text for s in a.stycken)
    t = lokal.tjanster[0].model_copy(update={'erfarenhetsprovning': 'En helt annan tjänstespecifik lärdom om kunders betalningsändamål.'})
    d = bygg_arb_v6(*v6underlag, analys=lokal.model_copy(update={'tjanster': (t,*lokal.tjanster[1:])}))
    a = d.avsnitt_med_id()[next(iter(v6underlag[3]))]
    assert any(t.erfarenhetsprovning in s.text for s in a.stycken)


def test_gemensamma_samma_kopplingar_grupperas_utan_att_forlora_bekraftelser(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    t = lokal.tjanster[1]
    a = d.avsnitt_med_id()[list(v6underlag[3])[1]]
    tab = next(t for t in a.tabeller if t.id.endswith('-scenarier'))
    assert len(tab.rader) == len(t.scenarier) + 1
    refs = set(r for rad in tab.rader for c in rad.celler for r in c.referenser)
    assert {'ANALYS:scenario:'+k.scenario for k in t.scenariokopplingar} <= refs
    # En enda ändrad/inaktuell koppling får en egen synlig kompletteringsmarkering.
    kop = t.scenariokopplingar[0].model_copy(update={'bekraftad': False})
    t = t.model_copy(update={'scenariokopplingar': (kop,*t.scenariokopplingar[1:])})
    paket = lokal.model_copy(update={'tjanster': (lokal.tjanster[0],t,*lokal.tjanster[2:])})
    d = bygg_arb_v6(*v6underlag, analys=paket)
    tab = next(tab for a in d.avsnitt for tab in a.tabeller if tab.id == t.tjanst+'-scenarier')
    assert any('Obekräftad' in c.text for r in tab.rader for c in r.celler)


def test_v6_tabellrad_har_kallsuffix_en_gang_och_bevarade_cellreferenser(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    a = d.avsnitt_med_id()[next(iter(v6underlag[3]))]
    for tab in a.tabeller:
        for rad in tab.rader:
            assert sum('Källor:' in c.text for c in rad.celler) <= 1
    assert any(ref.startswith('ANALYS:scenario:') for tab in a.tabeller for rad in tab.rader for c in rad.celler for ref in c.referenser)


def test_v6_katalogdetaljer_i_b1_med_synlig_rackviddsstatus(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    a = d.avsnitt_med_id()['D-ARB.7']
    assert any('bilaga B1' in s.text for s in a.stycken)
    rb = v6underlag[0]
    alla = texter(d)
    b1 = '\n'.join(synliga_texter(d.avsnitt_med_id()['D-ARB.B1']))
    for t in v6underlag[2].tjanster:
        if t.erbjuds is False:
            continue
        for k in t.kontroller:
            for r in rb.kontroller[k.id].rackvidd:
                if r.tjanst == t.tjanst:
                    assert r.kan_belagga in b1 and r.begransningar in b1
    assert 'okänd' in ' '.join(s.text for s in a.stycken).lower()


def test_delanalysreferenser_ar_tjanstbundna_aven_vid_samma_lokala_id(v6underlag, lokal):
    t = lokal.tjanster[1]
    t = t.model_copy(update={'delanalyser': (m.Delanalys(id='faktura', rubrik='Skattebeslut', arbetsmoment_och_befogenheter='Separat skattemandat.'),),
        'scenarier': tuple(s.model_copy(update={'delanalyser': ('faktura',)}) for s in t.scenarier)})
    paket = lokal.model_copy(update={'tjanster': (lokal.tjanster[0],t,*lokal.tjanster[2:])})
    d = bygg_arb_v6(*v6underlag, analys=paket)
    a = d.avsnitt_med_id()[list(v6underlag[3])[0]]
    b = d.avsnitt_med_id()[list(v6underlag[3])[1]]
    for rad in next(tab for tab in a.tabeller if tab.id.endswith('-scenarier')).rader:
        assert all('Skattebeslut' not in cell.text for cell in rad.celler)
    refs_a = {ref for s in a.stycken for ref in s.referenser}
    refs_b = {ref for s in b.stycken for ref in s.referenser}
    assert 'ANALYS:delanalys:'+lokal.tjanster[0].tjanst+':faktura' in refs_a
    assert 'ANALYS:delanalys:'+t.tjanst+':faktura' in refs_b


def test_v6_ren_byggare_laser_aldrig_privata_belaggsfiler(v6underlag, lokal, monkeypatch):
    from pathlib import Path
    def otillaten(*args, **kwargs):
        raise AssertionError('Dokumentbyggaren får inte läsa filer.')
    for namn in ('open', 'read_bytes', 'read_text'):
        monkeypatch.setattr(Path, namn, otillaten)
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    assert lokal.tjanster[0].samverkan in texter(d, huvud=True)


# Planens redaktionella ordbudget för fyrtjänstfallet (designval, inte lagkrav eller fastställelsespärr).
HUVUDTEXTMAL_MIN = 3500
HUVUDTEXTMAL_MAX = 5000
RIKTBUDGET = 4700
AI_MAX_ORD = 4 * (160 + 220)
LANGDVARNING = 'Redaktionell längdvarning'


def _fyrtjanstprov(tmp_path, rb, *, variation, maxord):
    from tester.fixturer.analys_hela_kedjan import skapa_fall, skriv_fall
    from riskanalys.drift.historik import Historik
    fall = skapa_fall(rb, tmp_path.resolve() / 'syntetiskt-fall', variation=variation)
    resultat, anrop = skriv_fall(fall, maxord=maxord)
    assert len(anrop) == 8
    aitexter = tuple(s.text for r in resultat.values() for del_ in r.delar for s in del_.godkant_svar.stycken)
    d = bygg_arb_v6(fall.regelbas, fall.profil, fall.bedomning, resultat, Historik(), analys=fall.analys)
    return fall, d, aitexter


def _bevarar_all_analys_och_varnar_vid_overskridande(fall, d, aitexter):
    """Ingen text kapas för att nå målet; över riktbudgeten krävs den synliga varningen."""
    from riskanalys.dokument.matning import dokumentord
    huvud = texter(d, huvud=True)
    for t in fall.analys.tjanster:
        for text in (t.samverkan, t.pt_motivering, t.tf_motivering, t.erfarenhetsprovning, t.slutsats):
            assert text in huvud
    for text in aitexter:
        assert text in huvud
    ordantal = dokumentord(d, fall.profil)
    assert (LANGDVARNING in huvud) == (ordantal['huvudtext'] > RIKTBUDGET)
    return ordantal


@pytest.fixture
def realistiskt_fyrtjanstprov(tmp_path, regelbas_v1):
    """Bygge, analysbevarande, varning och undre längdgräns får aldrig vara väntade fel."""
    fall, d, aitexter = _fyrtjanstprov(tmp_path, regelbas_v1, variation=False, maxord=False)
    assert sum(len(text.split()) for text in aitexter) < AI_MAX_ORD
    ordantal = _bevarar_all_analys_och_varnar_vid_overskridande(fall, d, aitexter)
    print({'fall': 'normal', 'variation': False, **ordantal})
    assert HUVUDTEXTMAL_MIN <= ordantal['huvudtext']
    return ordantal


def test_realistiskt_fyrtjanstprov_bevarar_analys_och_varnar_normalt(realistiskt_fyrtjanstprov):
    assert realistiskt_fyrtjanstprov['huvudtext'] >= HUVUDTEXTMAL_MIN


def test_realistiskt_fyrtjanstprov_haller_ovre_huvudtextmalet(realistiskt_fyrtjanstprov):
    huvudord = realistiskt_fyrtjanstprov['huvudtext']
    assert huvudord <= HUVUDTEXTMAL_MAX


@pytest.mark.parametrize('eftertext', ['', ' Byråns egna tillägg står exakt kvar.\nÄven nästa rad.'])
def test_bara_automatiskt_exponeringsprefix_kortas_och_egen_text_bevaras(v6underlag, lokal, eftertext):
    from riskanalys.dokument.exponeringsmetadata_v6 import kort_exponering
    rb, p, b, _, _ = v6underlag
    paket = forifyll_analys(rb, p, b, lokal.bindning)
    t = paket.tjanster[0]
    text = t.exponering + eftertext
    t = t.model_copy(update={'exponering': text})
    nytt = kort_exponering(t, paket, rb, p)
    assert len(nytt.split()) < len(text.split())
    assert nytt.endswith(eftertext) if eftertext else True
    assert 'Kunder:' in nytt and 'Kundandel:' in nytt and 'Omsättning (SEK):' in nytt and 'Omsättningsandel:' in nytt
    assert 'erbjudandet är bekräftat' in nytt
    assert t.exponering == text


@pytest.mark.parametrize('andring', ['helt_egen', 'andrat_prefix'])
def test_handskriven_exponering_och_andrat_automatiskt_prefix_lamnas_ororda(v6underlag, lokal, andring):
    from riskanalys.dokument.exponeringsmetadata_v6 import kort_exponering
    rb, p, b, _, _ = v6underlag
    paket = forifyll_analys(rb, p, b, lokal.bindning)
    t = paket.tjanster[0]
    text = 'Byråns egen bedömning av uppdraget.' if andring == 'helt_egen' else t.exponering.replace('Period ', 'Vår period ', 1)
    t = t.model_copy(update={'exponering': text})
    assert kort_exponering(t, paket, rb, p) == text


def test_kort_exponering_bevarar_skilda_perioder_datum_och_belagg(v6underlag, lokal):
    from riskanalys.dokument.exponeringsmetadata_v6 import kort_exponering
    from riskanalys.profil.modeller import Period
    rb, p, b, _, _ = v6underlag
    id = 'P-TJ.red01_omsattning'
    u = p.uppgifter[id].model_copy(update={'datum': date(2026, 10, 9),
        'period': Period(fran=date(2025, 1, 1), till=date(2025, 12, 31))})
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, id: u}})
    paket = forifyll_analys(rb, p, b, lokal.bindning)
    t = paket.tjanster[0]
    nytt = kort_exponering(t, paket, rb, p)
    assert '2025-01-01–2025-12-31' in nytt and '2026-01-01–2026-09-30' in nytt
    assert '2026-10-09' in nytt and '2026-10-10' in nytt
    assert t.exponeringsbelagg == paket.tjanster[0].exponeringsbelagg


def test_identiska_ai_stycken_samordnas_med_alla_referenser_och_ordalydelsen_kvar():
    from riskanalys.dokument.tjanstavsnitt_v6 import sammanfor_identiska_ai_stycken
    from riskanalys.dokument.modeller import Textstycke
    ursprung = (
        Textstycke(typ='analys', text='Identisk analys med oförändrad ordalydelse.', referenser=['H-01'], proveniens='ai'),
        Textstycke(typ='analys', text='En annan analys.', referenser=['H-03'], proveniens='ai'),
        Textstycke(typ='analys', text='Identisk analys med oförändrad ordalydelse.', referenser=['H-02', 'P-A'], proveniens='ai'),
    )
    nytt = sammanfor_identiska_ai_stycken(ursprung)
    assert [s.text for s in nytt] == ['Identisk analys med oförändrad ordalydelse.', 'En annan analys.']
    assert nytt[0].referenser == ['H-01', 'H-02', 'P-A']
    assert nytt[1] == ursprung[1]
    assert all(s.proveniens == 'ai' for s in nytt)
    assert ursprung[0].referenser == ['H-01']
    # Två separata delanrop får ingen gemensam historik som kan radera andra delens text.
    assert sammanfor_identiska_ai_stycken((ursprung[0],)) == (ursprung[0],)
    assert sammanfor_identiska_ai_stycken((ursprung[2],)) == (ursprung[2],)


def test_byggd_v6_bevarar_varje_ai_text_och_referens_inom_ratt_tjanst_och_del(v6underlag, lokal):
    from riskanalys.dokument.kallhanvisningar import utan_kallhanvisning
    from riskanalys.dokument.tjanstavsnitt import _ai_stycken
    resultat = v6underlag[3]
    fore = {id: r.model_dump_json() for id, r in resultat.items()}
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    for id, r in resultat.items():
        a = d.avsnitt_med_id()[id]
        for del_id, rubrik in (('hot', 'Hot'), ('sarbarheter', 'Sårbarheter')):
            start = next(u.fore_stycke for u in a.underrubriker if u.rubrik == rubrik)
            slut = next((u.fore_stycke for u in a.underrubriker if u.fore_stycke > start), len(a.stycken))
            faktiska = [s for s in a.stycken[start:slut] if s.proveniens == 'ai']
            ursprungliga = _ai_stycken(r.del_(del_id).godkant_svar, r.faktablad.numeriska(), r.faktablad.perioder())
            etikett = ' Gemensamma hänvisningar inom avsnittet.'
            # Här är etiketten genererad: den förekommer inte i fixturens ursprungliga AI-text.
            assert all(not s.text.endswith(etikett) for s in ursprungliga)
            for s in ursprungliga:
                traffar = [nytt for nytt in faktiska if utan_kallhanvisning(nytt.text, genererad_etikett=etikett) == s.text]
                assert len(traffar) == 1
                assert set(s.referenser) <= set(traffar[0].referenser)
            assert {utan_kallhanvisning(s.text, genererad_etikett=etikett) for s in faktiska} == {s.text for s in ursprungliga}
    assert {id: r.model_dump_json() for id, r in resultat.items()} == fore


def test_v6_omvarldsbevakning_visar_kalltitel_en_gang_aldre_visning_behalls(v6underlag):
    from riskanalys.dokument.uppfoljning import bevakningsavsnitt
    rb, p, _, _, _ = v6underlag
    historisk = bevakningsavsnitt(rb, p, gransindex={})
    nytt = bevakningsavsnitt(rb, p, gransindex={}, kort=True)
    for id in ('SRC-TS-2026-14', 'SRC-VAGL-2025-03'):
        titel = rb.kallor[id].titel
        assert historisk.stycken[0].text.count(titel) == 2
        assert nytt.stycken[0].text.count(titel) == 1
    assert nytt.stycken[0].referenser == historisk.stycken[0].referenser
    for id in ('P-BEVAKNING.ansvarig', 'P-BEVAKNING.relevans'):
        assert str(p.uppgifter[id].varde) in nytt.stycken[0].text


@pytest.mark.parametrize(('antal_ord', 'samordnas'), [(12, False), (39, False), (40, True), (41, True)])
def test_bara_langa_identiska_tabellceller_samordnas(antal_ord, samordnas):
    from riskanalys.dokument.gemensam_analys import sammanfor_identiska_tabelltexter
    from riskanalys.dokument.modeller import Avsnitt, Dokumenttabell, Tabellcell, Tabellrad
    text = ' '.join(['Resonemang'] * antal_ord)
    celler = tuple(Tabellcell(text=text, referenser=(ref,), proveniens='lokal') for ref in ('H-01', 'H-02'))
    a = Avsnitt(id='D-ARB.6.1', rubrik='Analys', kalla='lokal', formatversion='D-ARB-tjanst-v6', stycken=(),
        tabeller=(Dokumenttabell(id='tabell', rubrik='Prövning', kolumner=('Analys',), fore_stycke=0,
            rader=tuple(Tabellrad(celler=(c,)) for c in celler)),))
    nytt, gemensamma = sammanfor_identiska_tabelltexter((a,))
    assert bool(gemensamma) is samordnas
    for ursprunglig, rad in zip(celler, nytt[0].tabeller[0].rader):
        assert set(ursprunglig.referenser) <= set(rad.celler[0].referenser)
        if samordnas:
            assert rad.celler[0].text == 'Tabellresonemang 1'
            assert text in gemensamma[0].text
        else:
            assert rad.celler[0] == ursprunglig


@pytest.mark.parametrize('variation', [False, True])
def test_utvecklat_fyrtjanstprov_bevarar_resonemang_och_mater_ai_max(tmp_path, regelbas_v1, variation):
    fall, d, aitexter = _fyrtjanstprov(tmp_path, regelbas_v1, variation=variation, maxord=True)
    assert sum(len(text.split()) for text in aitexter) == AI_MAX_ORD
    ordantal = _bevarar_all_analys_och_varnar_vid_overskridande(fall, d, aitexter)
    print({'fall': 'ai-max', 'variation': variation, **ordantal})


@pytest.mark.parametrize(('nummer', 'text'), [
    ((), ''), ((4,), '4'), ((1, 2), '1, 2'), ((3, 1, 2), '1–3'), ((9, 1, 2, 3, 4, 5, 6, 7, 8), '1–9'),
    ((1, 2, 3, 5, 7, 8, 9, 12, 13), '1–3, 5, 7–9, 12, 13'), ((2, 2, 3, 4), '2–4'),
])
def test_nummerintervall_ar_entydigt_och_bevarar_varje_nummer(nummer, text):
    from riskanalys.dokument.analystabeller import nummerintervall
    assert nummerintervall(nummer) == text


def test_scenarioetikett_visar_intervall_och_behaller_okanda_synliga():
    from riskanalys.dokument.analysreferenser import Analysreferenser, analysref
    from riskanalys.dokument.analystabeller import scenarioetikett
    index = Analysreferenser({}, {analysref('scenario', f's{n}'): f'Scenario {n}' for n in range(1, 6)})
    assert scenarioetikett(index, ('s3',)) == 'Scenario 3'
    assert scenarioetikett(index, ('s5', 's1', 's2', 's3', 's1')) == 'Scenarier 1–3, 5'
    assert scenarioetikett(index, ('s2', 'okand')) == 'Scenario 2; Okänd lokal referens (scenario). [VERIFIERA]'
    assert scenarioetikett(index, ()) == 'Inga angivna'


def _utvidgade_nummer(text):
    import re
    assert re.fullmatch(r'\d+(?:–\d+)?(?:, \d+(?:–\d+)?)*', text), text
    tal = set()
    for del_ in text.split(', '):
        start, _, slut = del_.partition('–')
        tal.update(range(int(start), int(slut or start) + 1))
    return tal


def _scenariocell(cell, scenariorefs):
    """Synlig scenarioetikett utan källsuffix; varje visat nummer ska ha sin fulla referens i cellen."""
    import re
    text = cell.text.split(' Källor:')[0]
    traff = re.fullmatch(r'Scenario (\d+)|Scenarier (.+)', text)
    assert traff, text
    visade = {int(traff[1])} if traff[1] else _utvidgade_nummer(traff[2])
    assert len(visade) > 1 or traff[1]
    assert {scenariorefs[n] for n in visade} <= set(cell.referenser)
    return {scenariorefs[n] for n in visade}


@pytest.mark.parametrize('variation', [False, True])
def test_forkortade_listor_bar_varje_referens_i_referenser(tmp_path, regelbas_v1, variation):
    import re
    from riskanalys.dokument.analysreferenser import analysref, bygg_analysreferenser
    from riskanalys.dokument.analystabeller import nummerintervall
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    fall, d, _ = _fyrtjanstprov(tmp_path, regelbas_v1, variation=variation, maxord=False)
    korta = bygg_analysreferenser(fall.analys).korta
    scenariorefs = {int(etikett.removeprefix('Scenario ')): ref for ref, etikett in korta.items()}
    b1 = d.avsnitt_med_id()['D-ARB.B1']
    assert not re.search(r'Scenario \d+; Scenario', texter(d))
    avsnittsid = {t.tjanst: id for id, t in tjanster_med_avsnitt(fall.bedomning)}
    for t in fall.analys.tjanster:
        a = d.avsnitt_med_id()[avsnittsid[t.tjanst]]
        tabeller = {tab.id.removeprefix(t.tjanst + '-'): tab for tab in a.tabeller}
        # Grupperade kontrollprovningar: intervallet visas, varje scenario finns kvar som full referens.
        visade = set().union(*(_scenariocell(rad.celler[0], scenariorefs) for rad in tabeller['kontrollprovning'].rader))
        assert visade == {analysref('scenario', k.scenario) for k in t.kontroller}
        # Grupperade kopplingar till gemensamma scenarier, och en lokal variant med kort etikett.
        kopplingsrader = [rad for rad in tabeller['scenarier'].rader if rad.celler[1].text.startswith('Händelseförlopp: se Gemensamma')]
        visade = set().union(*(_scenariocell(rad.celler[0], scenariorefs) for rad in kopplingsrader))
        assert visade == {analysref('scenario', k.scenario) for k in t.scenariokopplingar}
        for k in t.scenariokopplingar:
            if k.lokal_scenario:
                lokal = analysref('scenario', k.lokal_scenario)
                assert any(f'Lokal variant: {korta[lokal]}.' in rad.celler[2].text and lokal in rad.celler[2].referenser
                           for rad in kopplingsrader)
        # Tillämpningskartan: intervallet motsvarar exakt tjänstens poster i B1, med oförändrade avsnittsreferenser.
        karta = next(s for s in a.stycken if 'gäller för denna tjänst' in s.text)
        traff = re.fullmatch(r'Gemensamma resonemang (.+) gäller för denna tjänst\. Fältkoppling och belägg: bilaga B1\.', karta.text)
        assert traff, karta.text
        kartposter = {int(n) for s in b1.stycken if a.id in s.referenser and 'D-ARB.5' in s.referenser
                      for n in re.findall(r': gemensamt resonemang (\d+)\.$', s.text)}
        assert _utvidgade_nummer(traff[1]) == kartposter
        assert traff[1] == nummerintervall(kartposter)
        assert {'D-ARB.5', 'D-ARB.B1', a.id} <= set(karta.referenser)


def test_word_lokala_tabellreferenser_lankar_till_befintliga_bokmarken(v6underlag, lokal, tmp_path):
    import docx
    from docx.oxml.ns import qn
    from riskanalys.dokument.rendering import rendera_docx
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    word = docx.Document(rendera_docx(d, v6underlag[1], 'UTKAST', tmp_path/'lokal.docx'))
    lankar = word.element.xpath('.//w:tbl//w:hyperlink')
    assert lankar
    mal = {x.get(qn('w:name')) for x in word.element.xpath('.//w:bookmarkStart')}
    assert all(x.get(qn('w:anchor')) in mal for x in lankar)
    assert all(x.get(qn('r:id')) is None for x in lankar)


def test_v6_ogiltig_tjanstreferens_ger_lasbar_kompletteringspunkt(v6underlag, lokal):
    okand = m.Tjansteanalys(tjanst='T-OKAND', block=(m.Analysblock(nummer=1, aktivering='okand'),))
    paket = lokal.model_copy(update={'tjanster': (*lokal.tjanster, okand)})
    d = bygg_arb_v6(*v6underlag, analys=paket)
    assert 'tjänsten saknas i bedömningen' in texter(d)


def test_v6_bevarar_rattslig_omfattning_lanshinder_sektorskallor_och_bevakning(v6underlag):
    from riskanalys.bedomning.motor import bedom
    from riskanalys.regelverk.urval import valj
    from riskanalys.dokument.klartext import faltnamn
    rb, p, b, r, h = v6underlag
    d = bygg_arb_v6(rb, p, b, r, h, analys=None)
    metod = d.avsnitt_med_id()['D-ARB.2']
    assert 'Rättslig omfattning: punkterna 19 och 20' in metod.stycken[0].text
    assert any('Uppdateringsgrunder:' in s.text for s in d.avsnitt_med_id()['D-ARB.10'].stycken)
    assert 'D-ARB.11' in d.avsnitt_med_id()
    for t in b.tjanster:
        if t.inneboende:
            ref = rb.sektorsreferenser[rb.tjanster[t.tjanst].sektorreferens]
            assert any(ref.id in s.referenser and rb.kallor[ref.kalla].titel in s.text for s in metod.stycken)
    p = p.model_copy(update={'uppgifter': {**p.uppgifter, 'P-ORG.sateslan': p.uppgifter['P-ORG.sateslan'].model_copy(update={'status': 'saknas'})}})
    b = bedom(rb, valj(rb, p.byra.regelpaket, b.datum, p.byra.lan), p)
    d = bygg_arb_v6(rb, p, b, {}, h, analys=None)
    s = d.avsnitt_med_id()['D-ARB.2'].stycken[0]
    assert 'P-ORG.sateslan' in s.referenser
    assert faltnamn(rb, 'P-ORG.sateslan').lower() in s.text.lower()


def test_v6_pt_och_tf_motivering_star_i_nivadelen_och_inte_i_lokal_analys(v6underlag, lokal):
    d = bygg_arb_v6(*v6underlag, analys=lokal)
    a = d.avsnitt_med_id()[next(iter(v6underlag[3]))]
    t = lokal.tjanster[0]
    niva = a.stycken[a.underrubriker[-1].fore_stycke:]
    assert a.underrubriker[-1].rubrik == 'Risknivå och motivering'
    assert any(s.text == 'Byråns bedömning av TF-risken: ' + t.tf_motivering for s in niva)
    assert any(s.text.startswith('Byråns bedömning av penningtvättsrisken: ' + t.pt_motivering) for s in niva)
    assert not any(s.text.startswith(('Motivering av PT-utfallet', 'Separat TF-prövning')) for s in a.stycken)
