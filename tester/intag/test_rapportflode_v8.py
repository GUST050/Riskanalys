"""H7.8: verkligt standardintag, öppna brister och båda Word-delarnas innehåll."""
from collections import Counter
from dataclasses import replace
import json

import docx
from docx.oxml.ns import qn
import pytest
from datetime import date

from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.skrivversion import V8
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.korning import las_granskning
from riskanalys.intag.dokument import skapa_utkast, uppdatera_export, las_utkast
from riskanalys.lagring.manifest import verifiera_manifest
from riskanalys.profil.lagring import spara_profil
from tester.fixturer.analys_hela_kedjan import placera_privat_analys
from tester.fixturer.rapportlasprov import FALL, bygg_rapportlasprov
from tester.fixturer.skrivsvar_v7 import tjanstspecifikt_svar_v7


@pytest.fixture(autouse=True)
def intagsklocka(monkeypatch):
    """H7.1:s frysta dag ersätter M2-katalogens äldre 10 oktober."""
    from importlib import import_module
    class Provdatum(date):
        @classmethod
        def today(cls):
            return date(2026, 10, 19)
    for namn in ('kvalitet', 'dokument'):
        monkeypatch.setattr(import_module('riskanalys.intag.' + namn), 'date', Provdatum)


def wordtexter(path):
    """Alla OOXML-stycken, även celler, i ordning och med dubbletter."""
    w = docx.Document(path)
    def text(node):
        return ''.join(n.text or '' if n.tag == qn('w:t') else
                       '\n' if n.tag == qn('w:br') else
                       '\t' if n.tag == qn('w:tab') else '' for n in node.iter())
    return [text(p) for p in w.element.body.iter(qn('w:p'))]


def fulla_fynd(texter):
    """Återskapa fulla medlemmar ur Word, inte ur presentationsobjektet."""
    grupper = []
    for text in texter:
        if text.startswith('Fyndgrupp '):
            grupper.append({'falt': {}})
        elif grupper and text.startswith('Medlems-ID:n: '):
            grupper[-1]['id'] = json.loads(text.split(': ', 1)[1])
        elif grupper and text.startswith('Källpositioner: '):
            grupper[-1]['positioner'] = json.loads(text.split(': ', 1)[1])
        elif grupper and ': ' in text:
            key, value = text.split(': ', 1)
            grupper[-1]['falt'][key] = json.loads(value)
    return sorted((pos, {'id': id, **g['falt']}) for g in grupper
                  for pos, id in zip(g['positioner'], g['id'], strict=True))


@pytest.fixture(autouse=True)
def historiskt_v8_flode(monkeypatch):
    from riskanalys.dokument import rapportversion
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V8)


def bygg_flode(rb, rot, namn, *, reserv=False, maxtext=False, leverantorstyp=Testleverantor):
    f = bygg_rapportlasprov(rb, rot, namn)
    # JSON:s Any-värden saknar datumtyp; vanligt intag lagrar riktiga date-objekt.
    upp = {id: u.model_copy(update={'varde': date.fromisoformat(u.varde)})
           if id in rb.falt and rb.falt[id].typ == 'datum' and isinstance(u.varde, str)
           else u for id, u in f.profil.uppgifter.items()}
    f = replace(f, profil=f.profil.model_copy(update={'uppgifter': upp}))
    spara_profil(f.byramapp, f.profil)
    svar = [tjanstspecifikt_svar_v7(rb, f.profil, t, id)
            for id, t in tjanster_med_avsnitt(f.bedomning)]
    if maxtext:
        # Lång giltig text: inget kort ordtak får tyst kapa AI-svaret.
        svar = [s.model_copy(update={'stycken': [p.model_copy(update={
            'text': p.text + ' Underlaget behöver följas tillbaka till affärshändelsen.' * 80})
            for p in s.stycken]}) for s in svar]
    lev = leverantorstyp(['Ogiltigt svar'] * 3 + svar[1:] if reserv else svar)
    if namn == 'olika_perioder':
        with pytest.raises(RiskanalysFel, match='samma statistikperiod'):
            skapa_utkast(f.byramapp, rb, lev)
        assert not lev.delanrop
        # Det felaktiga intaget får inte passera. Ordinarie lågkommandon får
        # ändå skapa ett tydligt bristutkast för granskarens innehållsprov.
        from riskanalys.bedomning.korning import kor_bedomning
        from riskanalys.dokument.skrivning import kor_skrivning
        from riskanalys.granskning.korning import kor_granskning
        from riskanalys.dokument.export import kor_export_utkast, UTKASTFIL
        bm = kor_bedomning(f.byramapp, rb)
        um = kor_skrivning(f.byramapp, rb, lev)
        gm = kor_granskning(f.byramapp, rb, date(2026, 10, 19), bedomningsmapp=bm, utkastmapp=um)
        fil = kor_export_utkast(f.byramapp, date(2026, 10, 19), granskningsmapp=gm) / UTKASTFIL
    else:
        fil = skapa_utkast(f.byramapp, rb, lev)
    placera_privat_analys(f)
    # Registrerade ogranskade svar får visas; inget sakgodkännande fabriceras.
    fil = uppdatera_export(f.byramapp, rb, fil)
    d, fynd = las_granskning(fil.parent / 'granskning')
    return f, lev, fil, d, fynd


@pytest.fixture(params=FALL)
def rapportfall(request, rb_intag, tmp_path):
    return bygg_flode(rb_intag, tmp_path, request.param)


def test_tio_standardfloden_bevarar_kropp_radata_och_alla_fynd(rapportfall):
    """Tappar exporten ett stycke, cell, fritt svar eller fyndmedlem blir provet rött."""
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    from riskanalys.dokument.rendering import renderat_avsnitt
    from riskanalys.dokument.radata_v8 import fria_analysfalt
    f, lev, fil, d, fynd = rapportfall
    assert d.formatversion == V8 and len(lev.delanrop) == 4
    assert all(a.max_tokens == 64000 for a in lev.delanrop)
    assert verifiera_manifest(fil.parent) == []
    underlag = fil.parent / 'underlagsbilaga-UTKAST.docx'
    assert las_utkast(f.byramapp, f.regelbas, fil)
    assert las_utkast(f.byramapp, f.regelbas, underlag)
    vyer = bygg_rapportvyer(d)
    for vy, path in zip((vyer.lasrapport, vyer.underlagsbilaga), (fil, underlag), strict=True):
        kvar = wordtexter(path)
        for a in vy.avsnitt:
            a = renderat_avsnitt(a, f.profil)
            # Konsumera en förekomst per förväntad post; inga mängder döljer bortfall.
            for text in [*(s.text for s in a.stycken),
                         *(c.text for t in a.tabeller for r in t.rader for c in r.celler)]:
                i = next(i for i, rad in enumerate(kvar) if rad.startswith(text))
                kvar.pop(i)
    huvud = '\n'.join(wordtexter(fil))
    bilaga = wordtexter(underlag)
    for falt in fria_analysfalt(f.analys):
        assert falt.text in '\n'.join(bilaga), falt.sokvag
        assert falt.sokvag in '\n'.join(bilaga)
    expected = [p.model_dump(mode='json') for p in fynd]
    ater = fulla_fynd(bilaga)
    assert [pos for pos, _ in ater] == list(range(1, len(fynd) + 1))
    assert [p for _, p in ater] == expected
    assert Counter(p['id'] for _, p in ater) == Counter(p.id for p in fynd)
    assert any(p.allvar == 'blockerande' for p in fynd)
    assert not (f.byramapp / 'faststallda').exists()
    for aid, t in tjanster_med_avsnitt(f.bedomning):
        section = d.avsnitt_med_id()[aid]
        assert len(section.underrubriker) == 6
        lokal = next(a for a in f.analys.tjanster if a.tjanst == t.tjanst)
        for text in (lokal.pt_motivering, lokal.tf_motivering, lokal.slutsats,
                     lokal.samverkan, lokal.reduktionsmotivering):
            if text:
                assert text in huvud
        motor = next(tab for tab in d.avsnitt_med_id()['D-ARB.B1'].tabeller if tab.id == t.tjanst + '-motorscenarier')
        assert len(motor.rader) == len(t.scenarier)
        kontroll = next(tab for tab in section.tabeller if tab.id.endswith('-kontrollprovning'))
        assert len(kontroll.rader) == (2 if t.tjanst == 'T-RED-01' else 1)
        for post in lokal.kontroller:
            match = [rad for rad in kontroll.rader if post.kontroll in rad.celler[0].referenser
                     and post.tillampning in rad.celler[1].text and post.utfall in rad.celler[1].text
                     and post.kvarstar in rad.celler[2].text]
            assert len(match) == 1, (t.tjanst, post.kontroll, post.scenario)
            assert sum(text.startswith(match[0].celler[1].text) for text in wordtexter(fil)) == 1
            for belagg in post.belagg:
                assert belagg in match[0].celler[3].text
        for scenario in t.scenarier:
            if scenario.avgorande or (scenario.dimension == 'pt' and scenario.kvarstaende == t.kvarstaende):
                # A matching hot elsewhere cannot satisfy this service's analysis.
                eget = renderat_avsnitt(section, f.profil)
                egna_texter = [s.text for s in eget.stycken]
                egna_texter.extend(c.text for tab in eget.tabeller for rad in tab.rader for c in rad.celler)
                assert f.regelbas.hot[scenario.hot].namn in '\n'.join(egna_texter)
                motor_rad = next(rad for rad in motor.rader
                    if scenario.hot in rad.celler[0].referenser and scenario.dimension.upper() in rad.celler[0].text)
                if scenario.avgorande:
                    assert 'avgör före' in motor_rad.celler[5].text.lower()
                if scenario.dimension == 'pt' and scenario.kvarstaende == t.kvarstaende:
                    assert 'avgör efter' in motor_rad.celler[6].text.lower()
        fakta = next(tab for tab in section.tabeller if tab.id.endswith('-lokala-fakta'))
        from riskanalys.intag.fordelning import aktiverad, kan_ateranvandas
        from riskanalys.dokument.lokaldata_v8 import inaktiv_frivillig_fordelning, _giltigt_lokalt_fordelningssvar
        for rad in fakta.rader:
            id = rad.celler[1].referenser[0]
            u = f.profil.uppgifter[id]
            if u.varde is not None:
                assert str(u.varde) in rad.celler[1].text
            aktiv_obesvarad = (
                f.regelbas.falt[id].intag is not None
                and not f.regelbas.falt[id].intag.obligatorisk
                and aktiverad(f.regelbas, f.profil, id)
                and u.varde is None and not u.inaktuell
                and not f.profil.ar_bekraftad(id)
            )
            if aktiv_obesvarad:
                assert 'Frivillig fördelning har inte lämnats; aktuellt antal är okänt.' in rad.celler[1].text
                assert '[VERIFIERA]' not in rad.celler[1].text
            elif not kan_ateranvandas(f.regelbas, f.profil, id):
                inaktiv=inaktiv_frivillig_fordelning(f.regelbas,f.profil,id)
                if inaktiv and (u.varde is None and not u.inaktuell or _giltigt_lokalt_fordelningssvar(f.regelbas,f.profil,id,u)):
                    assert '[VERIFIERA]' not in rad.celler[1].text
                    assert 'frivillig fördelning' in rad.celler[1].text.lower()
                else:
                    assert 'Aktuellt antal okänt' in rad.celler[1].text
        assert 'Exakt kundöverlapp är okänt' in huvud
        for gap in lokal.gap:
            assert gap.beskrivning in huvud and gap.motivering in huvud
            if gap.id == 'H7.1:mandatkonflikt':
                assert 'Byrån verkställer betalningar från kundens konto enligt separat mandat.' in huvud
                assert 'Kunden' in huvud and 'utan betalningsmandat' in huvud


@pytest.mark.parametrize('typ', ('ny_analys', 'andrad_period', 'underkand', 'gammal', 'saknat_underlag'))
def test_andrat_lokalt_underlag_stoppar_bada_nedladdningar(rb_intag, tmp_path, typ):
    from datetime import date
    from riskanalys.analys.modeller import Analysbeslut
    f, _, fil, _, _ = bygg_flode(rb_intag, tmp_path, 'fyra_tjanster')
    a = f.analys
    if typ == 'ny_analys':
        a = a.model_copy(update={'revision': a.revision + 1})
    elif typ == 'andrad_period':
        n = next(n for n, b in enumerate(a.belagg) if b.period is not None)
        andra = a.belagg[n].model_copy(update={'period': a.belagg[n].period.model_copy(
            update={'fran': date(2025, 1, 1)})})
        a = a.model_copy(update={'belagg': tuple(andra if i == n else b for i, b in enumerate(a.belagg))})
    elif typ == 'underkand':
        a = a.model_copy(update={'beslut': (Analysbeslut(tjanst=a.tjanster[0].tjanst,
            revision=a.revision, underlagssumma='nej', svarssumma='nej', godkand=False,
            namn='Syntetisk granskare', roll='Testroll', datum=date(2026, 10, 19),
            kommentar='Underlaget underkänns i det negativa provet.'),)})
    elif typ == 'gammal':
        a = a.model_copy(update={'bindning': a.bindning.model_copy(update={'bedomningsmanifest': 'gammal'})})
    else:
        a = a.model_copy(update={'tjanster': ()})
    placera_privat_analys(replace(f, analys=a))
    for path in (fil, fil.parent / 'underlagsbilaga-UTKAST.docx'):
        with pytest.raises(RiskanalysFel, match='Analys|analys'):
            las_utkast(f.byramapp, rb_intag, path)


@pytest.mark.parametrize('variant', ('reserv', 'maxtext'))
def test_reserv_och_lang_ai_text_genom_bada_word(rb_intag, tmp_path, variant):
    f, lev, fil, d, fynd = bygg_flode(rb_intag, tmp_path, 'fyra_tjanster',
                                    reserv=variant == 'reserv', maxtext=variant == 'maxtext')
    assert fil.is_file() and (fil.parent / 'underlagsbilaga-UTKAST.docx').is_file()
    if variant == 'reserv':
        assert len(lev.delanrop) == 6
        assert any(p.allvar == 'blockerande' and 'mall' in p.beskrivning for p in fynd)
    else:
        assert len(lev.delanrop) == 4
        marker = 'Underlaget behöver följas tillbaka till affärshändelsen.'
        # Fyra tjänster × fyra svarsstycken × 80 markörer; samtliga ska ut.
        assert sum(p.text.count(marker) for a in d.avsnitt for p in a.stycken) == 1280
        assert '\n'.join(wordtexter(fil)).count(marker) == 1280
    assert not (f.byramapp / 'faststallda').exists()


def test_nya_literal_original_gar_genom_omexport_utan_nya_ai_anrop(rb_intag, tmp_path):
    f, lev, fil, _, _ = bygg_flode(rb_intag, tmp_path, 'fyra_tjanster')
    original = 'Ordagrant {roll:FfR} | {roll:OkandRoll} | {tal:P-X} | {period:P-X} Källor:[1]'
    t = f.analys.tjanster[0].model_copy(update={'pt_motivering': original})
    a = f.analys.model_copy(update={'tjanster': (t, *f.analys.tjanster[1:])})
    placera_privat_analys(replace(f, analys=a))
    ny = uppdatera_export(f.byramapp, rb_intag, fil)
    assert len(lev.delanrop) == 4
    for path in (ny, ny.parent / 'underlagsbilaga-UTKAST.docx'):
        assert original in '\n'.join(wordtexter(path))
        assert las_utkast(f.byramapp, rb_intag, path)


def test_providerreserv_bevarar_svarsmodell_och_bada_word(rb_intag, tmp_path):
    from riskanalys.dokument.skrivning import las_skrivresultat
    from riskanalys.lagring.manifest import manifestets_metadata

    class Reservleverantor(Testleverantor):
        def skriv_del(self, anrop):
            svar = super().skriv_del(anrop)
            return svar.model_copy(update={'anrop': svar.anrop.model_copy(update={
                'svarsmodell': 'syntetisk-providerreserv', 'reservmodell_svarade': True})})

    f, lev, fil, _, _ = bygg_flode(rb_intag, tmp_path, 'fyra_tjanster', leverantorstyp=Reservleverantor)
    gm = fil.parent / 'granskning'
    um = f.byramapp / 'utkast' / manifestets_metadata(gm, 'utkast')['utkast']
    resultat = las_skrivresultat(um)
    assert len(lev.delanrop) == 4
    for r in resultat:
        assert r.del_('analys').godkant_svar is not None
        anrop = r.del_('analys').forsok[-1].anrop
        assert anrop.reservmodell_svarade and anrop.svarsmodell == 'syntetisk-providerreserv'
        for s in r.del_('analys').godkant_svar.stycken:
            assert s.text in '\n'.join(wordtexter(fil))
    assert las_utkast(f.byramapp, rb_intag, fil.parent / 'underlagsbilaga-UTKAST.docx')
