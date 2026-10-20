"""En modul per analysdel: mål, krav med skäl och fällor med skäl (spec 8.4.4)."""

from riskanalys.dokument.delvalidering import LANGD
from riskanalys.dokument.skrivversion import V5, V6, V7, V8, DELAR_V5, delar_for_version

DELAR = DELAR_V5  # Historiskt offentligt femdelarskontrakt. Ny skrivning väljer version explicit.

MODULER = {
    "analys": (
        "Skriv en sammanhängande analys för tjänsten i följande ordning. Börja med uppdraget utifrån "
        "tjänstens aktuella verksamhetsval och kundantal, eftersom mandat och insyn avgör hur uppdraget kan utnyttjas. "
        "Beskriv mandat, attest och bankinsyn inom just tjänsten; ett tjänstbundet nej till betalningsmandat "
        "belägger inte att byrån saknar betalningsmandat i andra tjänster. "
        "Saknade eller okända val markeras med [VERIFIERA] och en oklarhet; fyll aldrig i ett mandat själv.\n"
        "Beskriv två till tre konkreta sätt som tjänsten kan utnyttjas för penningtvätt eller finansiering av terrorism "
        "hos byrån, med TF när faktabladet har TF-hot, eftersom allmänna hot inte visar hur uppdraget används. "
        "Hänvisa till minst två hot och knyt minst ett hot till en sårbarhet eller faktauppgift i samma stycke. "
        "Skilj möjliga scenarier från iakttagna händelser, eftersom kataloghot inte bevisar att något har inträffat.\n"
        "Koppla scenarierna till de kund-, kanal- och geografiomständigheter som faktabladet visar gäller, eftersom "
        "analysen ska avse belagd exponering. Varje faktapost har omfang byra eller tjanst och tjänstposter har "
        "tjanst_id; tillskriv aldrig tjänsten byråns antal eller andelar eftersom fördelningen skrivs lokalt av programmet. "
        "Faktabladet är ett avsiktligt avgränsat urval, inte den fullständiga lokala analysen. "
        "Påstå därför inte att den lokala analysen saknar tjänstfördelning när faktabladet inte visar den. "
        "Ange byråomfånget utan att gissa fördelning eller beskriva det som en lokal kunskapslucka. "
        "Beskriv en kombination som villkorligt scenario när överlapp inte är belagt, eftersom skilda byråfaktorer "
        "inte visar att samma kunder berörs.\n"
        "Kontrollera kategorierna före svaret: kund = kunder, kanal = distributionskanaler, geo = geografi, "
        "tj = tjänstespecifika förhållanden och verk = verksamhetsspecifika förhållanden. "
        "För varje kategori med synligt utfall ja, nej eller okänt krävs minst ett synligt S-ID i referenser; "
        "ett P-ID ersätter inte kategorins S-ID. Kategorin tj krävs bara om den finns synlig. "
        "Ett känt nej är en avgränsning av metodvillkoret, inte frånvaro av hot eller skäl att avstå kontrollprövning. "
        "Beskriv negativa villkor kort och sakligt med rätt S-ID; flera kan behandlas tillsammans. "
        "Skyddade värden och sårbarheter med utfallet prövas lokalt är undantagna från checklistan och får inte refereras.\n"
        "Förklara vad katalogens kontroller normalt prövar och normalt inte visar utifrån beskrivning, kan_belagga, "
        "begransningar och forutsattningar med källhänvisningar, eftersom kontrollens räckvidd måste kunna spåras. "
        "Beskriv bara den tjänst- och hotkoppling som uttryckligen finns i räckvidden; saknas källbundet stöd ska du "
        "utelämna påståendet eftersom katalogens namn inte belägger räckvidd. "
        "rackviddsstatus okand betyder att källbundet räckviddsunderlag saknas; även källbundet_underlag är en "
        "generell beskrivning och faktisk scenariotäckning är fortfarande okänd. "
        "Påstå aldrig att byrån utför eller har utfört kontrollen eller att den är effektiv eller minskar risk, eftersom "
        "lokal tillämpning och effekt avgörs av programmet och byrån.\n"
        "nämn inte sårbarheter med utfallet prövas lokalt eller skyddade värden och skriv aldrig orden prövas lokalt, "
        "eftersom programmet skriver dessa utfall och deras lokala belägg. "
        "Ange inga nivåer eller motorutfall eftersom regelmotorn skriver dem. "
        "Programmet återger byråns egen rapportering och slutsatserna av den i den lokala låsta delen. "
        "Återberätta inte rapporteringsantal eller slutsatser av egen rapportering i AI-texten; överlåt dem till programmet. "
        "Få eller inga rapporter är inte "
        "belägg för frånvaro av hot eftersom rapporteringsantal inte mäter den faktiska exponeringen.\n"
        "Sikta på 240–280 ord för att rymma analys och referenser inom den hårda ordgränsen. "
        "Lägg käll-ID i referenser, inte utgivningsår, sidnummer eller uppräkningar av källtitlar i löptexten. "
        "Behåll exakt sak- och källstöd; tal och perioder följer fortfarande platshållarkontraktet."
    ),
    "hot": (
        "Skriv delen Hot och egna erfarenheter för tjänsten. Beskriv minst två konkreta sätt som just den här tjänsten "
        "kan utnyttjas hos byrån, utifrån hoten i faktabladet och tjänstens kunder. Ta med finansiering av terrorism när "
        "faktabladet har sådana hot, och beskriv tillvägagångssättet, inte bara att risken finns. Förklara att byrån kan "
        "utnyttjas omedvetet, genom att någon ser mellan fingrarna eller genom medverkan, eftersom penningtvättslagen "
        "kräver att hotet analyseras utifrån hur verksamheten faktiskt kan användas.\n"
        "Programmet har redan skrivit meningen om byråns egen rapportering. Hänvisa till den men upprepa den inte.\n"
        "Undvik allmänna hot som skulle gälla alla tjänster, eftersom tillsynen kritiserar just det.\n"
        "Exempel, illustrativt: \"En kund kan lämna fakturor från bolag utan verklig verksamhet för bokföring som vanliga "
        "kostnader. Eftersom byrån konterar underlagen löpande kan sådana fakturor ge brottsvinster ett legalt utseende "
        "innan någon stämmer av dem mot leveranser.\""
    ),
    "sarbarheter": (
        "Skriv delen Sårbarheter och motivering för tjänsten. Använd faktabladets fem kategorier: "
        "kund = kunder, kanal = distributionskanaler, geo = geografi, tj = tjänstespecifika förhållanden och "
        "verk = verksamhetsspecifika förhållanden. Hänvisa till minst en sårbarhet i varje kategori som finns i faktabladet. "
        "Säg för varje kategori om sårbarheterna i faktabladet gäller, inte gäller "
        "eller är okända, varför, och hur stor andel som berörs. Föreskrifterna kräver att sårbarheterna analyseras per "
        "kategori, och ett \"gäller inte\" utan skäl räknas som en brist.\n"
        "Geografin omfattar mer än sanktionslistor: ägare, verksamhet och betalningsflöden, även inom Sverige. Att "
        "kunderna är svenska utesluter inte geografisk risk. Långa kundrelationer är ingen trygghet i sig; nära relationer "
        "kan minska vaksamheten.\n"
        "Beskriv samverkan mellan faktorer som belagd bara när faktabladet visar att de gäller samma kunder; annars "
        "skriver du ett villkorligt scenario med stycketypen scenario.\n"
        "Behandla gärna varje kategori i ett eget stycke. I stycken av typen analys använder du inte orden samverkar, "
        "tillsammans, kombination eller förstärker, eftersom de påstår ett samband som faktabladet inte kan belägga. "
        "Ett möjligt samband skriver du som ett stycke av typen scenario. Saknas belagt samband skriver du att ingen "
        "belagd kombination finns.\n"
        "Om faktabladet säger att en faktor förekommer men ligger under metodens gräns, skriver du det utan att ange "
        "gränsens värde; andelen skrivs som {tal:ID}. Skriv inte att faktorn saknas eller att sårbarheten inte berör "
        "byrån.\n"
        "Om en sårbarhets utfall är prövas lokalt skriver du att den prövas lokalt, utan att säga om den gäller.\n"
        "Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."
    ),
    "kontroller": (
        "Skriv delen Kontroller och effekt för tjänsten. Programmet har redan skrivit varje kontrolls status och belägg. "
        "Förklara vilken risk varje kontroll riktar sig mot och vad utformning, genomförande och bedömd effekt innebär "
        "för tjänsten, eftersom vägledningen kräver att effekten bedöms innan riskerna vägs samman.\n"
        "Om en kontroll räknas som riskreducerande avgör programmet lokalt. Skriv därför aldrig att en kontroll minskar, "
        "begränsar, reducerar eller sänker risk. En beskriven kontroll, någon annans kundkännedom eller ett system ersätter inte "
        "en belagd effekt, och hög inneboende risk kan inte elimineras helt med kontroller."
    ),
    "risknivaer": (
        "Skriv en kort kvalitativ syntes under Scenarier och osäkerheter. Programmet skriver den lokala "
        "beräkningstabellen; du ser inte motorns nivåer och anger inga nivåer själv. Förklara inte varför en viss nivå är riktig "
        "eller avviker från sektorns nivå. Den lokala tabellen ensam beskriver basnivå, faktorer, tak, konsekvens, "
        "kontrollreduktion och utfall.\n"
        "Beskriv endast samband som stöds av faktabladet eller uttryckligt villkorliga scenarier: hur ett hot kan "
        "utnyttja en sårbarhet och vilka osäkerheter som behöver prövas lokalt. Gör inte obelagda antaganden om att "
        "faktorer gäller samma kunder. Sårbarheter med utfallet prövas lokalt beskriver du inte som gällande eller inte gällande.\n"
        "Använd de maskinellt validerade delarna som underlag utan att upprepa hotdelens scenariobeskrivningar. "
        "Minst ett stycke ska ha typen motivering och hänvisa till minst ett hot och en sårbarhet eller uppgift. "
        "Stycketypen motivering avser här kvalitativt resonemang, inte nivåmotivering."
    ),
    "slutsatser": (
        "Skriv delen Slutsatser för tjänsten. Förklara vad riskbilden betyder för just den här tjänsten: vilken "
        "kundkännedom som behövs, vad övervakningen ska fokusera på och vad utbildningen ska innehålla, kopplat till de "
        "identifierade hoten. Penningtvättslagen kräver att riskbedömningen ligger till grund för rutiner och utbildning, "
        "och tillsynen kritiserar slutsatser som bara upprepar riskbilden eller lovar allmänt att rutinerna ska anpassas.\n"
        "Programmet har redan skrivit meningen om byråns ansvar och beslut. Skriv inte att kundkännedom kan utelämnas."
    ),
}


def modultext(del_id: str, *, formatversion: str = V5) -> str:
    """Modulen med delens längdintervall. Gränsen kommer från valideringen så att de inte glider isär."""
    if del_id not in delar_for_version(formatversion):
        raise ValueError("Analysdelen ingår inte i skrivformatet.")
    if formatversion == V8:
        return MODUL_V8
    lagst, hogst = LANGD[del_id]
    versionstext = "Skrivformat v6: endast hot och sårbarheter genereras. Övrig analys skrivs lokalt.\n" if formatversion == V6 else ""
    return f"{versionstext}{MODULER[del_id]}\nSkriv {lagst}–{hogst} ord i delen. Text utanför intervallet underkänns och måste skrivas om."


# Eget kontrakt: ändringar här får aldrig ändra V7:s historiska modulbytes.
MODUL_V8 = (
    "Skrivformat v8: Skriv en sammanhängande tjänsteanalys med uppdrag, mandat och insyn utifrån synliga "
    "verksamhetsval. Ett tjänstbundet nej belägger inget om andra tjänster. Okända synliga val markeras "
    "med [VERIFIERA] och en oklarhet för faktaraden; fyll inte i ett mandat själv. "
    "Beskriv två till tre konkreta möjliga missbruksprocesser, med terrorfinansiering när TF-hot finns. "
    "Hänvisa till minst två H-ID och knyt minst ett hot till ett synligt S-ID eller P-ID i samma stycke. "
    "Kataloghot bevisar inga inträffade händelser. "
    "För varje kategori med synligt ja, nej eller okänt behövs minst ett S-ID: kund = kunder, "
    "kanal = distributionskanaler, geo = geografi, tj = tjänstespecifika och verk = verksamhetsspecifika "
    "förhållanden. P-ID ersätter inte S-ID. Kategorier utan synligt utfall undantas. Ett nej är en "
    "avgränsning, ingen frånvaro av hot. Nämn eller referera inte skyddade värden eller sårbarheter med "
    "utfallet prövas lokalt; programmet skriver dessa. "
    "Faktapostens omfang anger byra eller tjanst, med tjanst_id. Byråantal får aldrig tillskrivas tjänsten. "
    "Privata tjänstefördelningar, lokala antal och kunskapsstatus infogas av programmet. Påstå inte att "
    "lokal fördelning saknas, är okänd eller behöver kompletteras utifrån faktabladets avgränsning. "
    "Gissa varken antal med talord eller andelar som hälften. Beskriv faktoröverlapp endast som "
    "villkorligt scenario när samma kunder inte är belagda; använd stycketypen scenario. "
    "Beskriv kontrollernas generella räckvidd, vad de normalt kan visa och relevant begränsning enligt "
    "beskrivning, kan_belagga, begransningar och forutsattningar med källreferenser. Använd bara den "
    "tjänst- och hotkoppling som uttryckligen finns. rackviddsstatus okand innebär saknat källstöd; "
    "kallbundet_underlag intygar ingen lokal scenariotäckning. Hitta inte på utförda åtgärder, "
    "kontrolleffekt, riskreduktion, fattade beslut, utförd bevakning eller sakkunnigattest. "
    "Råd och möjliga scenarier ska framgå som sådana. Programmet skriver samtliga nivåer och motorutfall "
    "samt egen rapportering; återberätta inte detta. "
    "Använd AISvar med stycken och oklarheter. Tal och perioder följer platshållarkontraktet; "
    "referenser bär käll-ID, inte löptexten. Skriv så långt analysen behöver utan hård ordgräns; "
    "längd är rådgivande och inget resonemang ska kapas."
)
