# Nivåmotivering, lokala utfall och sammanhängande tjänstetext – genomförandeplan

> **För agentiska utförare:** OBLIGATORISK DELFÄRDIGHET: använd superpowers:subagent-driven-development för att genomföra planen uppgift för uppgift. Stegen har kryssrutor (`- [ ]`).

**Mål:** Huvudrapporten ska förklara varför varje tjänst fick sin nivå, visa byråns lokala utfall i stället för "prövas lokalt" och få en sammanhängande AI-text per tjänst, utan att privata uppgifter når AI eller motorns beräkning ändras.

**Arkitektur:** Fas 1 (uppgift 1–7) ändrar bara lokal dokumentsammansättning, regelbasens frågor och intaget; AI-begäran ändras inte utöver regelbasens etikett i uppgift 1. Fas 2 (uppgift 8–10) inför fasta verksamhetsval och skrivformat v7 med en AI-del per tjänst. Uppgift 11 verifierar hela kedjan, även med riktig AI.

**Teknik:** Python 3, Pydantic, python-docx 1.2, pytest, Anthropic SDK (`claude-opus-5-5`, strukturerade svar).

**Spec:** `docs/superpowers/specs/2026-10-08-riskanalys-design.md`, "Revision 35" sist i filen. Bakgrund: `docs/research/11-kallkontroll-allman-riskbedomning.md` §10–10.8.

## Globala villkor

- AGENTS.md gäller i sin helhet: AI fattar inga beslut; inga personuppgifter eller privata fritexter till AI; regelbasändringar har `kallor`/`kalla` och `grund`, skalor och gränser `metodval`; inga fria uttryck; inga riktiga API-anrop i automatiska tester (använd `Testleverantor`); sakkunnigstatus ändras aldrig till `verifierad`.
- Användartexter på svenska; identifierare på svenska utan å, ä, ö. Funktioner returnerar nya objekt.
- Motorns numeriska utfall (`bedomning/motor.py`, `beslutstabeller/metod.yaml`) ändras inte. Huvudrapporten visar en nivå per dimension, aldrig ett alternativt utfall.
- AI-begäran och omförsök får bara bero på tillåtelselistade värden. Två profiler som skiljer sig endast i icke tillåtelselistade värden ger byte-identisk begäranskedja.
- Äldre v5-, v5.1- och v6-resultat och exporter ska fortsatt kunna läsas och verifieras.
- Regelbasversion höjs till 1.6.0 i första uppgiften som ändrar regelbasen; regelbasvalidering (`.venv/bin/riskanalys regelbas validera`) ska passera efter varje sådan uppgift.
- Testkommando: `.venv/bin/pytest <filer> -q`. Ingen uppgift är klar förrän dess riktade tester och berörda befintliga testfiler är gröna. Fullsviten (`env -u ANTHROPIC_API_KEY .venv/bin/pytest`, cirka 20 min) körs efter uppgift 7 och i uppgift 11.
- **Fortsättning 2026-10-18:** Codex byggde uppgift 4–11 utan commits och granskade mot sparade arbetskopiesnapshots. Användaren beslutade 2026-10-18 att säkra det fullsvitsgröna läget i lokala commits utan push (`6a9e59e`). Ändringarna är sammanflätade mellan uppgifterna, så kodläget committas samlat i stället för per uppgift; otestade mellanlägen committas inte. `research_notes/` lämnas orört.

## Granskningsfokus

1. **Privat variation läcker via ny lokal text:** ett utfallsstycke eller en tjänstefördelning får aldrig påverka AI-begäran eller antal omförsök. Prov läggs i uppgift 5, 6 och 9.
2. **Tidigare nej-svar om sanktioner:** en sparad profil med det gamla nej-svaret ska exporteras med den snävare betydelsen och en synlig notis i B1, utan krasch eller ny rapportering. Prov i uppgift 1.
3. **Byrå utan lokal analys eller med tom PT-motivering:** nivådelen ska visa beräkningen och `[VERIFIERA]`, inte tom text eller undantag. Prov i uppgift 3.
4. **Tjänstefördelning större än byråns eller tjänstens antal:** ska ge en motsägelse i intaget och aldrig visas som giltigt utfall. Prov i uppgift 6.
5. **Äldre v6-skrivresultat i ny byggare:** ett sparat v6-resultat ska fortsatt bygga ett v6-dokument; ett v6-resultat får inte användas som v7-svar. Prov i uppgift 10.

## Integrationspreciseringar 2026-10-18

Förkontroll och beslut finns i arbetsloggen. Spec revision 35 gäller fortsatt; dessa preciseringar genomför dess säkerhets- och läsbarhetskrav.

- Uppgift 4: M1-förslaget kräver att dess vägledningskälla finns i det tillförda, versionsbundna källunderlaget. En äldre fryst regelbas ändras aldrig för att lägga till en saknad källa. Ett tillfälligt budgetundantag får bara omfatta övre ordgränsen efter godkänt bygge/bevarande/varningskontroll; uppgift 7 tar bort det.
- Uppgift 6: fördelningsfält är uttryckligen valfria och inte kritiska. Frågorna måste vara åtkomliga i intagsflödet. Användning förutsätter aktuella bekräftade baser, samma statistikperiod och giltig aktivering. Tjänsters kunder kan överlappa och summeras inte. Felaktiga eller inaktuella antal visas inte som giltigt varav. Källor/grund placeras enligt Intagsfalt-schemat, inte som ogiltiga top-level-fält.
- Uppgift 8–9: nya verksamhetsval får påverka V7-underlaget, medan historiska V5/V6-begäranden behåller sin versionerade vy. V7 skiljer uttryckligen byråfakta från tjänstefakta och använder bara den aktuella tjänstens verksamhetsval. Saknat eller valt okant är okänt. Katalogens kontrollbeskrivning och källbundna räckvidd/avgränsning tillförs endast som offentligt regelbasunderlag i den nya versionens skrivkontrakt; privata kontrollutfall skickas aldrig. Om beskrivningsstöd saknas ska modellen inte fylla luckan själv.
- Uppgift 9: befintliga tillämpliga sakskydd för TF, hotreferenser, obelagda samband, rapporteringsslutsatser, kontrollminskning och sanktionsundantag överförs till delen analys. Nya ordregler ersätter inte dessa skydd. Namn-/privatberoende lokal efterprövning sker först efter alla externa anrop.
- Uppgift 10: fullständiga lokala utfall återges en gång. Kategoritabellen visar kort status/relevans och hänvisning inom samma tjänst, utan att kopiera fulla värde-/periodmeningar eller lokala motiveringar. En verklig kort introduktionsmening bär tabellens rubrikposition. Aktuell Tjansteanalys skickas till nivåmotiveringen.
- Uppgift 10 omfattar också slutna dokumentmodeller, matning, sakgranskning, senaste-underkännande, kronologi och fastställelse. V7 får samma skydd som V6; gamla paket förblir verifierbara. Blandade V6/V7-svar avvisas, inte märks om. V7-standard väljs först när både skrivning och dokumentkedja stöder den.
- Ord- och sidmål höjs inte. Normala prov ska nå 3 500–5 000 huvudord med bevarad sakmotivering; maxprov bevarar allt och visar längdvarning. Fullsvitsresultat avser ett identifierat och oförändrat kodläge.

---

## Fas 1 – lokal sammansättning

### Uppgift 1: Sanktionsbetydelse

**Filer:**
- Ändra: `regelbas/falt.yaml` (posten `P-GEO.sanktionsanknytning`, rad cirka 800), `regelbas/kallor.yaml`, `regelbas/version.yaml`
- Ändra: `src/riskanalys/dokument/delvalidering.py`
- Ändra: den kod som bygger B1:s profilavsnitt (sök `Profilunderlag` i `src/riskanalys/dokument/`)
- Test: `tester/enhet/test_delvalidering.py`, `tester/enhet/test_arb_v6.py`, `tester/regelkontrakt/` (befintliga kontrakt för fältet)

**Gränssnitt:**
- Producerar: konstanten `SANKTION_OMFORMULERAD = '2026-10-17'` och regexen `_SANKTIONSUNDANTAG` i `delvalidering.py`.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_ai_text_som_avstar_sanktionsprovning_underkanns():
    # stycke: "Ingen anknytning behöver prövas mot internationella sanktioner."
    assert any('sanktion' in f.lower() for f in validera_del('sarbarheter', svar, fb, (), ()))

def test_ingen_identifierad_anknytning_godkanns():
    # stycke: "Ingen aktuell sanktionsanknytning har identifierats i underlaget."
    assert not [f for f in validera_del('sarbarheter', svar, fb, (), ()) if 'sanktion' in f.lower()]

def test_sanktionsfaltets_fraga_galler_identifierad_anknytning(regelbas):
    falt = regelbas.falt['P-GEO.sanktionsanknytning']
    assert 'identifierat' in falt.fraga and 'behöver prövas' not in falt.fraga
    assert falt.etikett == 'Identifierad sanktionsanknytning'

def test_b1_visar_att_sanktionsfragan_omformulerats(v6_dokument_med_nej_svar):
    assert 'omformulerades 2026-10-17' in b1_text(v6_dokument_med_nej_svar)
```

- [ ] **Steg 2: Kör testerna och se att de fallerar**

Kör: `.venv/bin/pytest tester/enhet/test_delvalidering.py tester/enhet/test_arb_v6.py -q -k sanktion`. Förväntat: FAIL.

- [ ] **Steg 3: Ändra regelbasen**

`fraga`: `Har byrån identifierat kund-, ägar- eller transaktionsanknytning till länder, personer eller företag som omfattas av internationella sanktioner?` `etikett`: `Identifierad sanktionsanknytning`. `varfor`: `Ett nej betyder att ingen sådan anknytning har identifierats i underlaget. Sanktionsreglerna gäller ändå och prövas enligt byråns rutin.` Lägg till källa `SRC-FI-SANKTIONER` (Finansinspektionen, Internationella sanktioner, https://www.fi.se/sv/forsakring/internationella-sanktioner/, i samma format som övriga poster i `kallor.yaml`) i fältets `kallor`. Höj `regelbas_version` till 1.6.0 och uppdatera kontrollsumma och de tester som pekar ut versionen.

- [ ] **Steg 4: Inför `_SANKTIONSUNDANTAG` i `delvalidering.py`**

Den ska matcha en negation (`ingen|inte|inga`) följd inom samma mening av `behöver` + `prövas` + `sanktion`. Felmeddelande: `Texten påstår att sanktioner inte behöver prövas. Skriv att ingen anknytning har identifierats.` Regeln ska gälla i `_gemensamma` för alla skrivversioner som valideras lokalt.

- [ ] **Steg 5: Lägg in B1-notisen**

Vid profilfältet i B1: `Frågan omformulerades 2026-10-17. Tidigare svar läses som att ingen anknytning har identifierats.` Visas bara när fältet har ett svar.

- [ ] **Steg 6: Kör testerna och regelbasvalideringen**

Kör: `.venv/bin/pytest tester/enhet/test_delvalidering.py tester/enhet/test_arb_v6.py tester/regelkontrakt -q && .venv/bin/riskanalys regelbas validera`. Förväntat: PASS.

- [ ] **Steg 7: Commit** `fix: sanktionsfrågan avser identifierad anknytning`

### Uppgift 2: Upprepad geografi och metodtext

**Filer:**
- Ändra: `src/riskanalys/dokument/lasta_v6.py:20` och `geografistycke_v6`
- Ändra: `src/riskanalys/dokument/arb_v6.py:180`
- Test: `tester/enhet/test_lasta_v6.py`, `tester/enhet/test_arb_v6.py`

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_identisk_tjanstegeografi_skrivs_en_gang(regelbas, profil_med_lika_geografi):
    (s,) = geografistycke_v6(regelbas, profil_med_lika_geografi, 'TJ-RED-01', gransindex={})
    assert s.text.count('Kundernas verksamheter finns') == 1
    assert {'P-BESK.geografi', 'P-TJ.red01_geografi'} <= set(s.referenser)

def test_olika_tjanstegeografi_skrivs_ut(regelbas, profil_med_olika_geografi):
    (s,) = geografistycke_v6(regelbas, profil_med_olika_geografi, 'TJ-RED-01', gransindex={})
    assert 'Tjänstens geografi' in s.text

def test_metodfragor_samlas_i_en_mening(v6_dokument):
    metod = avsnitt_med_id(v6_dokument, 'D-ARB.2')
    assert sum('metodprövning och rapportstatus' in s.text for s in metod.stycken) == 0
    assert sum(s.text.startswith('Öppna metodfrågor:') for s in metod.stycken) == 1
```

Fixturprofilerna bygger på befintlig `tester/fixturer/v6_analys.py`; tjänstens geografifält får samma respektive annan text än `P-BESK.geografi`, med samma källa och period.

- [ ] **Steg 2: Kör testerna och se att de fallerar**

- [ ] **Steg 3: Implementera**

I `geografistycke_v6`: hoppa över tjänstens beskrivning när dess visade text, källa och period är identiska med byråns, men behåll referensen. I `arb_v6.py` ersätts de fyra raderna av ett stycke: `Öppna metodfrågor: kontrollernas räckvidd, TF som egen dimension, enstaka exponering kontra omfattning samt summering, tak och dubbelräkning. Ingen av dem är sakkunnigprövad; risköversikten visar vad det betyder för nivåerna.` Om någon metodfråga får giltig sakkunnigstatus (`_sakkunnigstatus`) ska den inte räknas som öppen.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/enhet/test_lasta_v6.py tester/enhet/test_arb_v6.py tester/enhet/test_lokalt_dokument_v6.py -q`. Förväntat: PASS. Uppdatera låsta B-09/B-10-förväntningar bara där texten avsiktligt ändrats.

- [ ] **Steg 5: Commit** `fix: skriv identisk geografi och metodstatus en gång`

### Uppgift 3: Risknivå och motivering i tjänsteavsnittet

**Filer:**
- Skapa: `src/riskanalys/dokument/nivamotivering_v6.py`
- Ändra: `src/riskanalys/dokument/tjanstavsnitt_v6.py`, `src/riskanalys/dokument/lokaltext_v6.py:36-38`, `src/riskanalys/dokument/gemensam_analys.py`, `src/riskanalys/dokument/arb_v6.py:169`
- Test: skapa `tester/enhet/test_nivamotivering_v6.py`; ändra `tester/enhet/test_lokalt_dokument_v6.py`

**Gränssnitt:**
- Konsumerar: `Tjanstbedomning` (`inneboende`, `terrorfinansiering`, `kvarstaende`, `tillampade_sarbarheter`, `kontroller`, `regelspar`), `Tjansteanalys.pt_motivering`, `tf_motivering`, `reduktionsprovning`, `reduktionsmotivering`; samma regelbasdata som `nivatext.utfallsforklaring`.
- Producerar: `berakningsmotivering(t: Tjanstbedomning, rb: Regelbas) -> tuple[str, ...]` (en mening per dimension: PT före kontroll, PT kvarstående, TF, sanktion när den finns) och `nivamotivering_stycken(rb: Regelbas, t: Tjanstbedomning, a: Tjansteanalys | None) -> tuple[Textstycke, ...]`. Alla stycken har `typ='motivering'`.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_berakningen_namner_alla_tillampade_faktorer_och_taket(regelbas, tjanst_med_tak):
    pt = berakningsmotivering(tjanst_med_tak, regelbas)[0]
    for sid in tjanst_med_tak.tillampade_sarbarheter:
        if regelbas.sarbarheter[sid].galler in {'penningtvatt', 'bada'}:
            assert regelbas.sarbarheter[sid].namn in pt
    assert 'taket hög' in pt and 'ändrar inte nivån' in pt

def test_kvarstaende_sankning_markeras_som_ogranskat_metodval(regelbas, tjanst_med_sankning):
    kvar = berakningsmotivering(tjanst_med_sankning, regelbas)[1]
    assert 'ogranskat metodval' in kvar and 'scenariotäckning' in kvar
    assert 'BT-KVAR-02' not in kvar  # regel-ID står i referenserna, inte i texten

def test_byrans_bedomning_star_skild_fran_berakningen(regelbas, tjanst, analys):
    texter = [s.text for s in nivamotivering_stycken(regelbas, tjanst, analys)]
    assert any(t.startswith('Byråns bedömning av penningtvättsrisken: ') for t in texter)
    assert any(t.startswith('Byråns bedömning av TF-risken: ') for t in texter)

def test_saknad_motivering_ger_verifiera(regelbas, tjanst):
    texter = ' '.join(s.text for s in nivamotivering_stycken(regelbas, tjanst, None))
    assert '[VERIFIERA]' in texter and 'Sannolikheten' in texter

def test_motiveringar_samordnas_inte(v6_dokument_med_lika_motiveringar):
    for a in tjansteavsnitt(v6_dokument_med_lika_motiveringar):
        assert any(s.text.startswith('Byråns bedömning av penningtvättsrisken: ') for s in a.stycken)

def test_tjanst_har_underrubriken_risknivå_och_motivering(v6_dokument):
    for a in tjansteavsnitt(v6_dokument):
        assert [u.rubrik for u in a.underrubriker][-1] == 'Risknivå och motivering'
```

- [ ] **Steg 2: Kör testerna och se att de fallerar**

- [ ] **Steg 3: Implementera `nivamotivering_v6.py`**

Formuleringar (exakt mönster, värden insatta):
- PT: `Penningtvättsrisk före kontroller: {risk}. Sannolikheten utgår från tjänstens grundnivå {bas} och höjs av {namn (+n), …}{; taket hög nåddes, så ytterligare faktorer ändrar inte nivån}. Konsekvensen är {konsekvens} enligt tjänstekatalogen.` Utan faktorer: `… och ingen tillämpad faktor höjer den.` Taket nås när grundnivåns index plus summan av effekterna överstiger `hög`.
- Kvarstående: vid sänkning `Kvarstående penningtvättsrisk: {kvar}. Motorn sänker ett steg eftersom {kontrollnamn} har belagd utformning och genomförande. Det är ett ogranskat metodval som inte kräver belagd scenariotäckning; den lokala reduktionsprövningen är {status}.`; utan sänkning `Kvarstående penningtvättsrisk: {kvar}. Ingen kontroll har belagd funktion, så motorn sänker inte nivån.`
- TF: samma mönster med TF-grundnivå och faktorer med `galler` i `{'terrorfinansiering', 'bada'}`, och `Konsekvensen för TF är alltid allvarlig enligt metoden.`
- Byråns bedömning: `Byråns bedömning av penningtvättsrisken: {pt_motivering}` respektive `Byråns bedömning av TF-risken: {tf_motivering}`; tom text eller `a is None` ger `Saknas; förklara vilka förhållanden i tjänsten som motiverar nivån. [VERIFIERA]`. Om `reduktionsmotivering` finns läggs den till i PT-stycket som `Reduktionsprövning: {text}`.
- Referenser: tjänst, regelspår och tillämpade sårbarheter, samt `D-ARB.B1`.

- [ ] **Steg 4: Koppla in**

`bygg_tjanstavsnitt_v6` lägger underrubriken `Risknivå och motivering` sist och ersätter raden `Motorns beräkning och fullständiga regelspår finns i bilaga B1.` med `nivamotivering_stycken`. Ta bort PT-, TF- och reduktionsraderna ur `bygg_lokaltext`. `sammanfor_identisk_lokaltext` hoppar över stycken med `typ='motivering'`. Första meningen i `D-ARB.8` blir: `Nivåerna är motorns utfall. Varje tjänsteavsnitt förklarar vilka faktorer som avgör nivån och byråns egen bedömning. Hela beräkningen finns i bilaga B1.`

- [ ] **Steg 5: Kör testerna**

Kör: `.venv/bin/pytest tester/enhet/test_nivamotivering_v6.py tester/enhet/test_lokalt_dokument_v6.py tester/enhet/test_arb_v6.py tester/enhet/test_utfallsforklaring.py tester/enhet/test_sakgranskning.py -q`. Förväntat: PASS.

- [ ] **Steg 6: Commit** `feat: motivera risknivån i varje tjänsteavsnitt`

### Uppgift 4: M1-förslag i sakkunnigens beslutsunderlag

**Filer:**
- Ändra: `regelbas/kallor.yaml` (lägg till `SRC-LST-GOR-ARB`: Länsstyrelsen, Gör en allmän riskbedömning, https://www.lansstyrelsen.se/skane/samhalle/betalning-ekonomi-och-pengar/forhindra-penningtvatt-och-finansiering-av-terrorism/gor-en-allman-riskbedomning.html, och `SRC-LST-SK-3647-2026`: beslut om sanktionsavgift 3647-2026, Forvis Mazars Accounting Int AB, med URL och SHA-256 `05328ec72451ef4cdb6fed529e729196d1a14dfcbcaca03246df00fb99afd0dc`)
- Ändra: B1:s metodavsnitt i `src/riskanalys/dokument/arb_v6.py` (`bilaga_b1_v6`) eller den modul som skriver B1:s metodposter
- Test: `tester/enhet/test_arb_v6.py`, `tester/enhet/test_b1_delrubriker_v6.py`

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_m1_forslaget_star_bara_i_b1(v6_dokument):
    assert 'Förslag till sakkunnig, M1' in b1_text(v6_dokument)
    assert 'Förslag till sakkunnig, M1' not in huvudtext(v6_dokument)

def test_m1_forslaget_hanvisar_till_vagledningen(v6_dokument):
    s = stycke_som_borjar(b1(v6_dokument), 'Förslag till sakkunnig, M1')
    assert 'SRC-LST-GOR-ARB' in s.referenser
```

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera med exakt text**

`Förslag till sakkunnig, M1 (inte beslutat): kvarstående risk sänks först när relevant räckvidd för tjänstens scenarier och kontrollens faktiska effekt under perioden är belagda lokalt. Länsstyrelsens vägledning anger att åtgärdernas effektivitet ska bedömas innan riskerna vägs samman. Dokumentets nivåer beräknas fortfarande med nuvarande regel tills sakkunnig har prövat metoden.` Referenser: `SRC-LST-GOR-ARB`, `BT-KVAR-01`, `BT-KVAR-02`, `D-ARB.B1`. Placera under B1:s metodrubrik.

- [ ] **Steg 4: Kör testerna och regelbasvalideringen.** Förväntat: PASS.

- [ ] **Steg 5: Commit** `docs: lägg M1-förslaget i sakkunnigens beslutsunderlag`

### Uppgift 5: Lokala utfallsstycken för skyddade faktorer

**Filer:**
- Skapa: `src/riskanalys/dokument/utfall_v6.py`
- Ändra: `src/riskanalys/dokument/tjanstavsnitt_v6.py` (`_ai_del` för `sarbarheter`)
- Test: skapa `tester/enhet/test_utfall_v6.py`; ändra `tester/enhet/test_underlag.py`

**Gränssnitt:**
- Konsumerar: `underlag.provas_lokalt`, `underlag.SKYDDAD_VISNING`, `klartext.under_grans`, `klartext.gransmening`, `tabeller.kort_varde`, `regelverk.villkor.utvardera`, `Uppgift.inaktuell`.
- Producerar: `Utfall = Literal['galler','ej_uppfyllt','under_grans','okant','inaktuellt']`; `sarbarhetsutfall(rb, profil, sarbarhet_id, *, gransindex) -> Utfall`; `utfallsstycken(rb, profil, t: Tjanstbedomning, *, gransindex, fordelning: Mapping[str, int] | None = None) -> tuple[Textstycke, ...]`. Uppgift 6 skickar `fordelning` (fält-ID → antal i tjänsten).

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
@pytest.mark.parametrize('utfall,fras', [
    ('galler', 'gäller'), ('ej_uppfyllt', 'villkoret är inte uppfyllt'),
    ('under_grans', 'under metodens gräns'), ('okant', '[VERIFIERA]'), ('inaktuellt', 'inaktuellt underlag')])
def test_utfallet_formuleras_per_status(utfall, fras, profil_for):
    text = ' '.join(s.text for s in utfallsstycken(rb, profil_for(utfall), t, gransindex={}))
    assert fras in text

def test_ej_uppfyllt_beskrivs_inte_som_frånvaro_av_risk(profil_for):
    text = ' '.join(s.text for s in utfallsstycken(rb, profil_for('ej_uppfyllt'), t, gransindex={}))
    assert 'Ett villkor som inte är uppfyllt visar inte att risken saknas.' in text
    assert 'gäller inte' not in text

def test_ett_stycke_per_omrade_och_bara_lokalt_provade(profil_med_skyddade):
    stycken = utfallsstycken(rb, profil_med_skyddade, t, gransindex={})
    assert len({s.text.split(':')[0] for s in stycken}) == len(stycken)
    assert all(s.proveniens == 'lokal' for s in stycken)

def test_ai_begaran_oforandrad_av_privata_utfall(profil_a, profil_b_bara_privat_skillnad):
    assert begaranskedja(profil_a) == begaranskedja(profil_b_bara_privat_skillnad)
```

`begaranskedja` kör `skriv` med `Testleverantor` och jämför samtliga sparade begäranden byte för byte, även omförsök.

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera**

Ett stycke per område (`Kunder`, `Distributionskanaler`, `Geografi`, `Egen verksamhet`, `Tjänstespecifika förhållanden`) som har minst en sårbarhet som `provas_lokalt` eller vars värde är skyddat. Form: `{Område} enligt byråns underlag: {namn} {fras} ({värde}, {period}); …` följt av meningen om ej uppfyllt villkor en gång när den behövs. Med `fordelning` läggs `, varav {n} i tjänsten` till efter värdet. Infoga styckena efter AI-texten och före de låsta styckena i sårbarhetsdelen. Ändra inte faktabladet eller prompten.

- [ ] **Steg 4: Kör testerna**

Kör: `.venv/bin/pytest tester/enhet/test_utfall_v6.py tester/enhet/test_underlag.py tester/enhet/test_lokalt_dokument_v6.py tester/enhet/test_skrivning.py -q`. Förväntat: PASS.

- [ ] **Steg 5: Commit** `feat: visa lokala utfall för skyddade sårbarheter`

### Uppgift 6: Tjänstefördelning av byråövergripande faktorer

**Filer:**
- Ändra: `regelbas/falt.yaml` (nya per-tjänst-fält, skapade med samma mekanism som `{slug}_geografi`; sök efter hur dessa genereras i `src/riskanalys/regelverk/` eller `docs/research/verktyg/`)
- Ändra: `src/riskanalys/intag/fragor.py` (villkorad fråga), `src/riskanalys/intag/kvalitet.py` (motsägelse)
- Ändra: `src/riskanalys/dokument/tjanstavsnitt_v6.py` (skicka `fordelning` till `utfallsstycken`)
- Test: `tester/intag/` (frågor och kvalitet), `tester/enhet/test_utfall_v6.py`, test att tillåtelselistan är oförändrad

**Gränssnitt:**
- Producerar: fält `P-TJ.{slug}_antal_utland_transaktion`, `_antal_utland_agare`, `_antal_riskbransch`, `_antal_kontant` (typ `heltal`, `grund: metodval`, `kallor: [SRC-14FS-2024-11, SRC-TS-2026-14, SRC-LST-SK-3647-2026]`, avsnitt `D-ARB.5`); `tjanstefordelning(rb, profil, tjanst) -> dict[str, int]` som returnerar byråfält-ID → bekräftat antal i tjänsten.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_fragan_stalls_bara_nar_faktorn_finns_och_flera_tjanster(intag_med_6_utlandskunder_och_4_tjanster):
    assert 'P-TJ.red04_antal_utland_transaktion' in aktiva_fragor(intag_med_6_utlandskunder_och_4_tjanster)

def test_fragan_stalls_inte_vid_en_tjanst_eller_noll(intag_en_tjanst, intag_noll_utland):
    assert not any(f.endswith('_antal_utland_transaktion') for f in aktiva_fragor(intag_en_tjanst))
    assert not any(f.endswith('_antal_utland_transaktion') for f in aktiva_fragor(intag_noll_utland))

def test_fordelning_over_byrans_eller_tjanstens_antal_ar_motsagelse(profil_7_av_6):
    assert any('fler än' in m.text for m in motsagelser(profil_7_av_6))

def test_fordelningen_visas_i_utfallet(profil_2_av_6_i_lon):
    assert 'varav 2 i tjänsten' in sarbarhetsdel_text(profil_2_av_6_i_lon, 'TJ-RED-04')

def test_tillatelselistan_innehaller_inga_fordelningsfalt(regelbas):
    assert not [f for f in regelbas.tillatelselistor['risk_per_tjanst'].falt if '_antal_utland' in f or '_antal_riskbransch' in f or '_antal_kontant' in f]
```

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera fält, villkor och motsägelse.** Frågetext: `{Tjänst}: Hur många av byråns {n} kunder med {faktor} använder tjänsten?` Motsägelse: `{Tjänst}: fler kunder med {faktor} än byrån har totalt eller än tjänsten har; rätta antalet.` Ett obesvarat fält ger inget `varav` och ingen spärr.

- [ ] **Steg 4: Kör testerna, regelbasvalideringen och intagsproven.** Kör: `.venv/bin/pytest tester/intag tester/enhet/test_utfall_v6.py tester/enhet/test_underlag.py -q && .venv/bin/riskanalys regelbas validera`. Förväntat: PASS.

- [ ] **Steg 5: Commit** `feat: fråga hur byråövergripande faktorer fördelas på tjänster`

### Uppgift 7: Färre hänvisningsrader

**Filer:**
- Ändra: `src/riskanalys/dokument/kallhanvisningar.py` (`_kallor`, `med_kallhanvisningar`), `src/riskanalys/dokument/rendering.py:321-328`, `src/riskanalys/dokument/gemensam_analys.py` (`sammanfor_identiska_tabelltexter`)
- Test: `tester/enhet/test_kallhanvisningar.py`, `tester/enhet/test_rendering_v6.py`, `tester/enhet/test_lokalt_dokument_v6.py`, `tester/enhet/test_ordbudget.py`

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_tjanst_id_ger_ingen_kallhanvisning(regelbas):
    assert _kallor(['TJ-RED-01'], regelbas, _poster(regelbas)) == {}

def test_samma_kallsuffix_i_foljd_visas_en_gang(v6_dokument):
    for a in v6_dokument.avsnitt:
        suffix = [kallsuffix(s.text) for s in a.stycken]
        assert all(x is None or x != y for x, y in zip(suffix, suffix[1:]))

def test_b1_lank_hogst_en_gang_per_avsnitt(renderad_docx):
    assert max(b1_lankar_per_avsnitt(renderad_docx).values()) <= 1

def test_korta_tabellceller_samordnas_inte(v6_dokument):
    assert 'Tabellresonemang' not in huvudtext_utan_celler_over_40_ord(v6_dokument)
```

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera.** `_kallor` följer inte poster ur `rb.tjanster` (tjänstens katalogkälla visas där katalogtext återges via hot-, scenario- eller sektorsreferens). `med_kallhanvisningar` utelämnar ett suffix som är identiskt med närmast föregående stycke i samma avsnitt; referenserna bevaras i modellen. Renderingen lägger B1-länken efter avsnittets sista stycke som refererar B1. Tröskeln i `sammanfor_identiska_tabelltexter` höjs från 12 till 40 ord. Gäller v6 och senare; v5/v5.1 renderas oförändrat.

- [ ] **Steg 4: Kör testerna och mät**

Kör de riktade testerna och därefter fullsviten: `env -u ANTHROPIC_API_KEY .venv/bin/pytest`. Förväntat: alla passerar utom bortvalt livetest. Bygg det befintliga fyrtjänstprovet (`tester/fixturer/v6_analys.py`) och redovisa huvudord före/efter fas 1 i commitmeddelandet.

- [ ] **Steg 5: Commit** `refactor: färre upprepade käll- och bilagehänvisningar`

---

## Fas 2 – sammanhängande AI-text

### Uppgift 8: Fasta verksamhetsval

**Filer:**
- Ändra: `regelbas/falt.yaml`, `regelbas/tillatelselistor.yaml`, `src/riskanalys/intag/fragor.py`, `src/riskanalys/analys/guide.py` (om valen visas i analysvyn)
- Test: `tester/intag/`, `tester/enhet/test_underlag.py`, `tester/enhet/test_aischema.py`

**Gränssnitt:**
- Producerar: per tjänst `P-TJ.{slug}_attest` (`kund|byra|bada|okant`), `P-TJ.{slug}_betalningsmandat` (`inget|forbereder|verkstaller|okant`), `P-TJ.{slug}_bankinsyn` (`full|delvis|ingen|okant`); typ `val`, `grund: metodval`, `kallor: [SRC-TS-2026-14, SRC-14FS-2024-11]`. Alla tre läggs i `risk_per_tjanst.falt`.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_verksamhetsval_finns_i_faktabladet(fb_lon):
    assert {'P-TJ.red04_attest', 'P-TJ.red04_betalningsmandat', 'P-TJ.red04_bankinsyn'} <= fb_lon.uppgift_id()

def test_verksamhetsval_accepterar_bara_fasta_varden(intag):
    with pytest.raises(RiskanalysFel):
        spara_svar(intag, 'P-TJ.red04_betalningsmandat', 'kunden betalar själv')

def test_okant_val_visas_som_okant(fb_utan_val):
    assert post(fb_utan_val, 'P-TJ.red04_bankinsyn').status == 'okänd'
```

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera.** Frågetexter: `{Tjänst}: Vem attesterar underlagen?`, `{Tjänst}: Vilket betalningsmandat har byrån?`, `{Tjänst}: Vilken insyn har byrån i kundens bankkonton?` Förifyll inte från fritext. Värdena visas för AI med klartextetiketter (`kunden`, `byrån`, `både kunden och byrån`, `okänt`; `inget`, `förbereder betalningar`, `verkställer betalningar`; `full`, `delvis`, `ingen`).

- [ ] **Steg 4: Kör testerna och regelbasvalideringen.** Förväntat: PASS.

- [ ] **Steg 5: Commit** `feat: fasta verksamhetsval per tjänst`

### Uppgift 9: Skrivformat v7 med en AI-del per tjänst

**Filer:**
- Ändra: `src/riskanalys/dokument/skrivversion.py` (`V7 = 'D-ARB-tjanst-v7'`, `DELAR_V7 = ('analys',)`, `AKTUELL_SKRIVVERSION = V7`)
- Ändra: `src/riskanalys/dokument/promptar/delar.py` (modul `analys`), `src/riskanalys/dokument/promptar/system.py`, `src/riskanalys/dokument/delvalidering.py` (`LANGD['analys'] = (160, 320)`), `src/riskanalys/dokument/delskrivning.py`, `src/riskanalys/dokument/skrivning.py`
- Test: `tester/enhet/test_promptar.py`, `tester/enhet/test_delvalidering.py`, `tester/enhet/test_skrivning.py`, `tester/enhet/test_langdkontrakt.py`

**Gränssnitt:**
- Konsumerar: `Faktablad` med verksamhetsvalen från uppgift 8; `_SANKTIONSUNDANTAG` från uppgift 1.
- Producerar: `delar_for_version(V7) == ('analys',)`; ett v7-skrivresultat med en godkänd del `analys` per tjänst.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_v7_har_en_del_per_tjanst():
    assert delar_for_version(V7) == ('analys',)

def test_analysmodulen_beskriver_kedjan_och_forbjuder_kontrollpastaenden():
    m = modultext('analys', formatversion=V7)
    for ord_ in ('uppdraget', 'utnyttjas', 'omständigheter', 'normalt inte visar'):
        assert ord_ in m
    assert 'prövas lokalt' in m and 'nämn' in m

def test_v7_underkanner_prövas_lokalt_och_genomforda_kontroller(fb):
    fel = validera_del('analys', svar_med('Riskbranscher prövas lokalt. Vi kontrollerar alltid kontoändringar.'), fb, (), ())
    assert any('prövas lokalt' in f for f in fel) and any('kontroll' in f for f in fel)

def test_v7_begaran_oforandrad_under_privat_variation(profil_a, profil_b_bara_privat_skillnad):
    assert begaranskedja(profil_a, version=V7) == begaranskedja(profil_b_bara_privat_skillnad, version=V7)

def test_v6_resultat_lases_fortfarande(sparat_v6_resultat):
    assert delar_for_version(sparat_v6_resultat.formatversion) == ('hot', 'sarbarheter')
```

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Skriv modulen `analys`** med exakt innehåll i denna ordning: (1) börja med uppdraget utifrån tjänstens verksamhetsval och kundantal; (2) beskriv två till tre konkreta sätt tjänsten kan utnyttjas hos byrån, med TF när faktabladet har TF-hot, och skilj möjliga scenarier från iakttagna händelser; (3) koppla till kund-, kanal- och geografiförhållanden som faktabladet visar gäller; (4) förklara vad katalogens kontroller normalt prövar och vad de normalt inte visar, utan att påstå att byrån utfört dem eller att de varit effektiva; (5) nämn inte sårbarheter med utfallet prövas lokalt eller skyddade värden – programmet skriver deras utfall; (6) gissa inte om byråövergripande faktorer gäller tjänstens kunder – programmet skriver fördelningen. Skäl anges i en mening per regel, som i befintliga moduler. Systemprompten får regeln: `Skriv aldrig att sanktioner inte behöver prövas; skriv att ingen anknytning har identifierats.`

- [ ] **Steg 4: Validering.** För v7: `_PROVAS_LOKALT` (`prövas lokalt`) och `_GENOMFORD_KONTROLL` (första person eller byrån som subjekt följt av `kontrollerar|stämmer av|verifierar|granskar`) ger fel med åtgärdstext. Befintliga gemensamma regler gäller. Längd 160–320 ord.

- [ ] **Steg 5: Delskrivning.** Ett anrop per tjänst; omförsök enligt befintlig policy, oberoende av privata värden. Prompt- och schemaidentitet versioneras så att v6-svar inte kan återanvändas som v7.

- [ ] **Steg 6: Kör testerna.** Kör: `.venv/bin/pytest tester/enhet/test_promptar.py tester/enhet/test_delvalidering.py tester/enhet/test_skrivning.py tester/enhet/test_langdkontrakt.py tester/enhet/test_aldre_skrivvag.py tester/enhet/test_claude.py -q`. Förväntat: PASS.

- [ ] **Steg 7: Commit** `feat: skrivformat v7 med sammanhängande analys per tjänst`

### Uppgift 10: Dokument v7

**Filer:**
- Skapa: `src/riskanalys/dokument/tjanstavsnitt_v7.py`
- Ändra: `src/riskanalys/dokument/arb_v6.py` (välj tjänstebyggare efter skrivresultatets version; dokumentversion `D-ARB-tjanst-v7` när resultatet är v7), `src/riskanalys/dokument/skrivversion.py` (`AKTUELL_DOKUMENTVERSION = V7`), `src/riskanalys/granskning/` (v7 accepteras där v6 accepteras), `src/riskanalys/dokument/kallhanvisningar.py` och `rendering.py` (v7 behandlas som v6)
- Test: skapa `tester/enhet/test_arb_v7.py`; kör `tester/enhet/test_arb_v6.py`, `tester/enhet/test_exportera_kommando.py`, `tester/enhet/test_faststall.py`, `tester/m2/`

**Gränssnitt:**
- Konsumerar: `nivamotivering_stycken` (uppgift 3), `utfallsstycken` och `tjanstefordelning` (uppgift 5–6), `lasta_stycken_v6`.
- Producerar: `bygg_tjanstavsnitt_v7(rb, profil, t, resultat, avsnitt_id, *, gransindex, lokal, tabeller) -> Avsnitt` med underrubrikerna `Analys`, `Kategorier`, `Lokal analys och slutsats`, `Risknivå och motivering`.

- [ ] **Steg 1: Skriv de fallerande testerna**

```python
def test_v7_tjanst_har_fyra_delar_i_ordning(v7_dokument):
    for a in tjansteavsnitt(v7_dokument):
        assert [u.rubrik for u in a.underrubriker] == ['Analys', 'Kategorier', 'Lokal analys och slutsats', 'Risknivå och motivering']

def test_kategoriöversikten_tacker_lagens_faktorer(v7_dokument):
    tab = tabell(tjansteavsnitt(v7_dokument)[0], 'kategorier')
    assert [r.celler[0].text for r in tab.rader] == ['Kunder', 'Distributionskanaler', 'Geografi', 'Egen verksamhet', 'Tjänstespecifika förhållanden']

def test_v6_resultat_ger_v6_dokument(sparat_v6_resultat):
    assert bygg(sparat_v6_resultat).formatversion == 'D-ARB-tjanst-v6'

def test_v6_resultat_kan_inte_bli_v7(sparat_v6_resultat):
    with pytest.raises(RiskanalysFel):
        bygg(sparat_v6_resultat, formatversion=V7)

def test_v7_hela_kedjan_till_word_och_verifiering(tmp_path):
    # intag → bedöm → skriv (Testleverantor) → granska → exportera → verifiera
    assert kor_kedja(tmp_path, version=V7).verifiering_ok
```

Kategoritabellen har per område kolumnerna `Område`, `Utfall` (från `sarbarhetsutfall`, samlat per område) och `Byråns prövning` (relevans ur `Sarbarhetsprovning`). Den ersätter inga låsta stycken eller granskningsregler.

- [ ] **Steg 2: Kör och se att de fallerar**

- [ ] **Steg 3: Implementera v7-byggaren.** Ordning i delen Analys: AI-stycken, utfallsstycken, låsta stycken (egen rapportering, geografi). Mallen vid saknat AI-svar följer `_mall` i v6.

- [ ] **Steg 4: Kör testerna och fullsviten.** Förväntat: alla passerar utom bortvalt livetest.

- [ ] **Steg 5: Commit** `feat: dokumentformat v7 med kategoriöversikt och nivåmotivering`

### Uppgift 11: Slutprov och dokumentation

**Filer:**
- Skapa privat: `~/.local/share/riskanalys/provkorningar/v7-kontrast-20261017/` (utanför Git)
- Ändra: `docs/STATUS.md`, spec revision 35 (genomförandestatus), denna plan (utfall)

- [ ] **Steg 1: Säkerhetsprov.** Kör befintliga och nya prov för begäranskedjan under privat variation, smågruppsskydd och namnstopp. Förväntat: PASS.

- [ ] **Steg 2: Två påhittade byråer.** Bygg i provmappen två sammanhängande fiktiva byråer: A med beräkning utan betalningsmandat och delvis bankinsyn; B med lönehantering där byrån verkställer betalningar, full bankinsyn och utlandskunder i lönetjänsten. Lokala svar skrivs per tjänst och skiljer sig i sak; inga attester eller sakkunnigstatus sätts. Rimlighetskontroll: beskrivna branscher stämmer med antal i riskbransch.

- [ ] **Steg 3: Riktig AI.** Kör `ClaudeLeverantor` med standardmodell och effort för båda byråerna (användaren har godkänt kostnaden). Spara anrop, svar, omförsök och kostnad. Inga privata svar får finnas i begärandena (kontrollera mot provets privata texter).

- [ ] **Steg 4: Mät och läs.** Huvudord, sidor (LibreOffice-rendering), B1-ord, antal `[VERIFIERA]`, `prövas lokalt` (mål 0 i AI-text), `Källor:` och B1-länkar, jämfört med Lindvikenprovet. Läs varje tjänsteavsnitt mot frågorna: vilket hot utnyttjar vilken sårbarhet, vad kontrollen inte visar, varför nivån blev som den blev, vad byrån ska göra. Skriv fynden i `LAS-MIG.md` i provmappen.

- [ ] **Steg 5: Fullsvit och dokumentation.** Kör `env -u ANTHROPIC_API_KEY .venv/bin/pytest`; uppdatera STATUS med verifiering och kvarstående frågor (M1–M4, sakkunnig, Microsoft Word, medarbetarläsprov).

- [ ] **Steg 6: Commit** `docs: v7 slutprov och status`
