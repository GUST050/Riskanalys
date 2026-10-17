"""Två AI-delar med programmets låsta stycken och en separat lokal analys per tjänst i v6."""
from riskanalys.dokument.analysunderlag import sarbarhetsstycke
from riskanalys.dokument.delskrivning import kontrollera_resultat
from riskanalys.dokument.lasta_v6 import lasta_stycken_v6
from riskanalys.dokument.modeller import Avsnitt, Textstycke, Underrubrik
from riskanalys.dokument.nivamotivering_v6 import nivamotivering_stycken
from riskanalys.dokument.skrivversion import V6
from riskanalys.dokument.tjanstavsnitt import _ai_stycken

AI_DELAR = (('hot', 'Hot'), ('sarbarheter', 'Sårbarheter'))


def lokaltext(text, refs=(), *, typ='analys'):
    return Textstycke(typ=typ, text=text, referenser=list(dict.fromkeys(refs)), proveniens='lokal')


def _mall(rb, profil, t, del_id, rubrik, gransindex):
    """Programmets mall när validerad AI-text saknas; geografin står redan i det låsta stycket."""
    poster = [lokaltext(f'Komplettera tjänstens {rubrik.lower()}; validerad AI-text saknas. [VERIFIERA]', [t.tjanst])]
    if del_id == 'hot':
        poster.extend(Textstycke(typ='beskrivning', text=f'{rb.hot[id].namn}: {rb.hot[id].beskrivning}',
            referenser=[t.tjanst, id, *rb.hot[id].kallor], proveniens='regelbas') for id in t.hot)
    else:
        poster.extend(sarbarhetsstycke(rb, profil, t.tjanst, id, gransindex=gransindex).model_copy(
            update={'proveniens': 'regelbas'}) for id in rb.tjanster[t.tjanst].sarbarheter if rb.sarbarheter[id].omrade != 'geo')
    return tuple(poster)


def _ai_del(rb, profil, t, resultat, del_id, rubrik, gransindex):
    """AI-text eller mall, följd av programmets låsta stycken i samma del (spec 8.4.1)."""
    svar = resultat.del_(del_id).godkant_svar if resultat is not None else None
    if svar:
        fb = resultat.faktablad
        text = tuple(s.model_copy(update={'proveniens': 'ai'}) for s in _ai_stycken(svar, fb.numeriska(), fb.perioder()))
    else:
        text = _mall(rb, profil, t, del_id, rubrik, gransindex)
    return (*text, *lasta_stycken_v6(rb, profil, t, del_id, gransindex=gransindex))


def bygg_tjanstavsnitt_v6(rb, profil, t, resultat, avsnitt_id, *, gransindex, lokal=None, tabeller=(), analys=None):
    poster = []
    rubriker = []
    if resultat is not None:
        kontrollera_resultat(rb, profil, t, resultat, avsnitt_id, gransindex=gransindex, formatversion=V6)
    for del_id, rubrik in AI_DELAR:
        rubriker.append(Underrubrik(fore_stycke=len(poster), rubrik=rubrik))
        poster.extend(_ai_del(rb, profil, t, resultat, del_id, rubrik, gransindex))
    lokalstart = len(poster)
    rubriker.append(Underrubrik(fore_stycke=lokalstart, rubrik='Lokal analys och slutsats'))
    poster.extend(lokal or (lokaltext(
        'Lokal analys saknas. Komplettera scenarier, sårbarheternas betydelse och samverkan, egna lärdomar, '
        'kontrolltäckning, separata PT- och TF-motiveringar samt slutsats och rutinåtgärder. [VERIFIERA]', [t.tjanst]),))
    rubriker.append(Underrubrik(fore_stycke=len(poster), rubrik='Risknivå och motivering'))
    poster.extend(nivamotivering_stycken(rb, t, analys))
    return Avsnitt(id=avsnitt_id, rubrik='Analys av ' + rb.tjanster[t.tjanst].namn.lower(), kalla='lokal',
        stycken=tuple(poster), underrubriker=tuple(rubriker),
        tabeller=tuple(t.model_copy(update={'fore_stycke': lokalstart}) for t in tabeller), formatversion=V6)
