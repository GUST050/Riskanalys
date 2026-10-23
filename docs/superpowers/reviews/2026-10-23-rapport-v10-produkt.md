# V10 – produktanpassning efter PDF-godkännande

Användaren svarade ”1” på kontrollfrågan där första alternativet var ”Godkänn rapportförslaget”. Det gäller de två huvudrapporterna i prov10, 19 respektive 20 sidor. Detta är godkännande av rapportförslaget för implementation, ingen sakkunnigattest eller fastställelse.

Nya rapportbyggen använder V10 med kapitel 0–5. Granskning, frysta källor, kravkarta, atomisk tredelsexport, nedladdning och fastställelsekedja har egna V10-vägar. Huvudrapporten kräver samlad sakgranskning med den visade struktursumman. A och B1 granskas fortsatt för sig. Äldre individuella huvudgodkännanden gäller inte. Byte av disposition ändrar struktursumman och kräver ny granskning.

Befintliga V8/V9-utkast behåller format vid vanlig uppdatering. Byte till V10 väljs uttryckligen via CLI eller knapp för kapitel 0–5. V9:s byggare, paketläsare, presentationspolicy och historiska kontrollsummor är oförändrade. AI-skrivformatet är fortfarande V8; inga AI-anrop behövs för formatbytet.

## Utförd byggkontroll

Kopior av båda syntetiska referensfallen har körts genom `kor_granskning` med ny standard V10, aktuell återbyggnad och `kor_export_utkast`. Båda exporter gav tre Word-filer och tom manifestfellista. Fyndantal 430/440 är oförändrat. Reproducerbart utfall finns i `.superpowers/evidens/2026-10-23-v10-produkt/utfall.json`. Källor från det godkända prov10 har inte skrivits över. Syntax- och whitespacekontroll passerar.

Regressioner för paket, samlad granskning, enskilt avvisande, gamla attestposter, formatbyte och tre webbdelar är skrivna. De har ännu inte körts; användaren har begärt samlad testning på slutet. Fastställelse har inte genomförts och inga verkliga sakkunnigstatusar har ändrats.

## Kvar

D:s provisoriska metodval, nya PDF:er efter D för användarens slutkontroll och sedan E samt samlad slutreview/testning. Regelbasen är fortsatt 2.2.0. Ingen push eller merge.
