"""B-09/B-10/B-15 kontrollerar belägg och lokal analys, inte juridisk fullständighet."""
from riskanalys.bedomning.erfarenheter import ERFARENHETSFALT
from riskanalys.dokument.analysunderlag import erfarenhetsstycke, sarbarhetsstycke
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.dokument.modeller import AvsnittsUtkast
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt


def _tjanstanalys_stammer(regelbas, profil, bedomning, tjanst, avsnitt):
    """AI-delen granskas vid skrivning; övrig analys måste följa det belagda underlaget."""
    if not avsnitt or len(avsnitt.underrubriker) != 6:
        return False
    start, slut = (r.fore_stycke for r in avsnitt.underrubriker[4:])
    if not 0 <= start < slut < len(avsnitt.stycken):
        return False
    utkast = AvsnittsUtkast(avsnitt=avsnitt.id, stycken=list(avsnitt.stycken[start:slut]), oklarheter=[])
    expected = bygg_tjanstavsnitt(regelbas, profil, tjanst, utkast, avsnitt.id,
                                 utokad=bedomning.proportionalitet.niva == "utökad")
    return avsnitt.kontrollsumma() == expected.kontrollsumma()


def analysfynd(regelbas, bedomning, profil, dokument):
    avsnitt = dokument.avsnitt_med_id()
    hot = avsnitt.get("D-ARB.4")
    sarbarheter = avsnitt.get("D-ARB.5")
    resultat = []
    tjanstavsnitt = {t.tjanst: id for id, t in tjanster_med_avsnitt(bedomning)}
    nytt_format = bool(regelbas.metod.omfattning)
    if nytt_format and "D-ARB.B1" not in avsnitt:
        resultat.append(dict(typ="tackning", allvar="blockerande", grund="metodval", avsnitt="D-ARB.B1",
                              beskrivning="Underlagsbilagan som ingår i sakgranskningen saknas.",
                              atgard="Återskapa det fullständiga dokumentet med underlagsbilaga och sakgranska på nytt."))

    def fynd(regel, avsnitt_id, beskrivning, atgard):
        post = regelbas.bristmonster[regel]
        resultat.append(dict(typ="bristmonster", regel=regel, allvar="blockerande", grund=post.grund,
                             avsnitt=avsnitt_id, beskrivning=beskrivning, atgard=atgard))

    def innehaller(avsnitt, stycke):
        return bool(avsnitt and any(s.text == stycke.text and set(stycke.referenser) <= set(s.referenser)
                                    for s in avsnitt.stycken))

    for t in bedomning.tjanster:
        if t.inneboende is None:
            continue
        hot_id = tjanstavsnitt[t.tjanst] if nytt_format else "D-ARB.4"
        sarb_id = tjanstavsnitt[t.tjanst] if nytt_format else "D-ARB.5"
        hot = avsnitt.get(hot_id)
        sarbarheter = avsnitt.get(sarb_id)
        if nytt_format and not _tjanstanalys_stammer(regelbas, profil, bedomning, t, hot):
            resultat.append(dict(typ="tackning", allvar="blockerande", grund="metodval", avsnitt=hot_id,
                                  beskrivning=f"{t.tjanst}: tjänstens sex analysdelar avviker från det belagda underlaget.",
                                  atgard="Återskapa tjänstanalysen från aktuell profil, bedömning och validerat AI-utkast. Sakgranska på nytt."))
        if all(id in regelbas.falt for id in ERFARENHETSFALT):
            egen = erfarenhetsstycke(regelbas, profil, t)
            if t.egen_erfarenhet is None or not t.egen_erfarenhet.belagd or "[VERIFIERA]" in egen.text or not innehaller(hot, egen):
                fynd("B-15", hot_id, f"{t.tjanst}: belagd egen rapportering och erfarenhet saknas i hotanalysen.",
                     "Bekräfta rapporter, avböjanden och egna erfarenheter med källa/period. Bedöm och skriv om dokumentet.")
        for id in regelbas.tjanster[t.tjanst].sarbarheter:
            if regelbas.sarbarheter[id].omrade != "geo" or "P-BESK.geografi" not in regelbas.falt:
                continue
            stycke = sarbarhetsstycke(regelbas, profil, t.tjanst, id)
            if "[VERIFIERA]" in stycke.text:
                fynd("B-09", sarb_id, f"{t.tjanst}/{id}: geografins aktuella underlag är ofullständigt.",
                     "Bekräfta faktiska länder och områden, även svenska anknytningar, och tjänstens geografiska underlag.")
            if not innehaller(sarbarheter, stycke):
                fynd("B-10", sarb_id, f"{t.tjanst}/{id}: den geografiska sårbarheten saknar spårbar underlagsmotivering.",
                     "Återskapa sårbarhetsanalysen med villkor, bekräftade värden, perioder och källor. Sakgranska slutsatsen.")
    return resultat
