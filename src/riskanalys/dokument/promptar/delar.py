"""En modul per analysdel: mål, krav med skäl och fällor med skäl (spec 8.4.4)."""

from riskanalys.dokument.delvalidering import LANGD

DELAR = ("hot", "sarbarheter", "kontroller", "risknivaer", "slutsatser")

MODULER = {
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
        "Programmet har redan skrivit underlagsstycket för geografin. Bygg vidare på det."
    ),
    "kontroller": (
        "Skriv delen Kontroller och effekt för tjänsten. Programmet har redan skrivit varje kontrolls status och belägg. "
        "Förklara vilken risk varje kontroll riktar sig mot och vad belägget visar. Om effekten inte är belagd ska det "
        "framgå att kontrollen inte sänker risknivån, eftersom vägledningen kräver att effekten bedöms innan riskerna "
        "vägs samman.\n"
        "Skriv bara att en kontroll minskar, begränsar eller reducerar risk när faktabladet visar en belagd effekt. En "
        "beskriven kontroll, någon annans kundkännedom eller ett system ersätter inte en belagd effekt, och hög "
        "inneboende risk kan inte elimineras helt med kontroller."
    ),
    "risknivaer": (
        "Skriv motiveringen under Risknivåer och motivering. Programmet har redan skrivit nivåmeningarna och sektorsreferensen "
        "på källans egen skala; ange inga nivåer själv. Förklara nivån som en kedja: vilka hot som kan utnyttja vilka "
        "sårbarheter, hur tjänstens omfattning påverkar sannolikheten och vilken konsekvensen blir. Pröva tjänstens egna förhållanden "
        "mot sektorsreferensen i faktabladet, utan att likställa skalorna; motivera skillnader med det belagda underlaget, "
        "eftersom föreskrifterna kräver att risknivåerna motiveras.\n"
        "Använd de maskinellt validerade delarna som underlag och upprepa dem inte. Minst ett stycke ska ha typen "
        "motivering och hänvisa till minst ett hot och en sårbarhet eller uppgift."
    ),
    "slutsatser": (
        "Skriv delen Slutsatser för tjänsten. Förklara vad motorns nivå betyder för just den här tjänsten: vilken "
        "kundkännedom som behövs, vad övervakningen ska fokusera på och vad utbildningen ska innehålla, kopplat till de "
        "identifierade hoten. Penningtvättslagen kräver att riskbedömningen ligger till grund för rutiner och utbildning, "
        "och tillsynen kritiserar slutsatser som bara upprepar nivån eller lovar allmänt att rutinerna ska anpassas.\n"
        "Programmet har redan skrivit meningen om byråns ansvar och beslut. Skriv inte att kundkännedom kan utelämnas."
    ),
}


def modultext(del_id: str) -> str:
    """Modulen med delens längdintervall. Gränsen kommer från valideringen så att de inte glider isär."""
    lagst, hogst = LANGD[del_id]
    return f"{MODULER[del_id]}\nSkriv {lagst}–{hogst} ord i delen. Text utanför intervallet underkänns och måste skrivas om."
