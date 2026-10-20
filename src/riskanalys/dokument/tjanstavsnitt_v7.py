"""Sammanhängande AI-analys med privata utfall och separat lokal nivåmotivering."""
from riskanalys.dokument.delskrivning import kontrollera_resultat
from riskanalys.dokument.lasta_v6 import lasta_stycken_v6
from riskanalys.dokument.modeller import Avsnitt, Underrubrik
from riskanalys.dokument.nivamotivering_v6 import nivamotivering_stycken
from riskanalys.dokument.skrivversion import V7
from riskanalys.dokument.scenariotabell import bygg_scenariotabell
from riskanalys.dokument.tabeller import rad, tabell
from riskanalys.dokument.analystabeller import lokalcell as cell
from riskanalys.dokument.tjanstavsnitt import _ai_stycken
from riskanalys.dokument.tjanstavsnitt_v6 import _mall, lokaltext, sammanfor_identiska_ai_stycken
from riskanalys.dokument.utfall_v6 import OMRADEN, sarbarhetsutfall, utfallsstycken
from riskanalys.intag.fordelning import tjanstefordelning
from riskanalys.regelverk.villkor import falt_i, tolka_villkor

RESERVKATALOG_RUBRIK = 'Katalogunderlag när AI-text saknas'

_STATUS = {'galler': 'gäller', 'ej_uppfyllt': 'ej uppfyllt', 'under_grans': 'under gränsen',
           'okant': 'okänt', 'inaktuellt': 'inaktuellt'}
_RELEVANS = {'relevant': 'Relevant', 'ej_relevant': 'Ej relevant', 'okant': 'Okänd relevans'}
_LOKAL_SAKNAS = ('Lokal analys saknas. Komplettera scenarier, sårbarheternas betydelse och samverkan, egna lärdomar, '
                'kontrolltäckning, separata PT- och TF-motiveringar samt slutsats och rutinåtgärder. [VERIFIERA]')


def reservkatalog(rb, profil, t, *, gransindex):
    """Hela oförändrade katalogtexten från reservvägen, utan dess kompletteringsmarkörer."""
    return (*_mall(rb, profil, t, 'hot', 'analys', gransindex)[1:],
            *_mall(rb, profil, t, 'sarbarheter', 'sårbarhetsanalys', gransindex)[1:])


def reservkatalog_i_b1(rb, profil, bedomning, resultat, *, gransindex):
    """Samla bara byteidentiska katalogtexter och bevara alla tjänst- och avsnittskopplingar."""
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    poster = []
    for id, t in tjanster_med_avsnitt(bedomning):
        post = resultat.get(id)
        if post is None or post.del_('analys').godkant_svar is None:
            poster.extend(s.model_copy(update={'referenser': list(dict.fromkeys((*s.referenser, id)))})
                for s in reservkatalog(rb, profil, t, gransindex=gransindex))
    return sammanfor_identiska_ai_stycken(poster)


def kategorioversikt(rb, profil, t, analys, *, gransindex, position):
    """Kort status och relevans; fulla värden och människans motiveringar återges bara i respektive textdel."""
    provningar = analys.sarbarhetsprovningar if analys else ()
    rader = []
    for omrade, namn in OMRADEN.items():
        ids = tuple(id for id in rb.tjanster[t.tjanst].sarbarheter if rb.sarbarheter[id].omrade == omrade)
        refs = tuple(dict.fromkeys(ref for id in ids for ref in
            (id, *sorted(falt_i(tolka_villkor(rb.sarbarheter[id].villkor, rb.faltdefinitioner()))))))
        statusar = tuple(dict.fromkeys(_STATUS[sarbarhetsutfall(rb, profil, id, gransindex=gransindex)] for id in ids))
        status = ', '.join(statusar) if statusar else 'Inga katalogfaktorer'
        prov = tuple(p for p in provningar if p.omrade == ('tjanst' if omrade == 'tj' else omrade))
        relevans = (', '.join(dict.fromkeys(_RELEVANS[p.relevans] for p in prov)) if prov else
                    'Se uppdragsprövningen' if not ids and omrade == 'tj' else 'Ej prövat. [VERIFIERA]')
        rader.append(rad(cell(namn), cell(status, refs), cell(relevans)))
    return tabell(t.tjanst + '-kategorier', 'Kategoriöversikt', ('Område', 'Utfall', 'Byråns prövning'), rader, position)


def bygg_tjanstavsnitt_v7(rb, profil, t, resultat, avsnitt_id, *, gransindex, lokal=None, tabeller=(), analys=None):
    if resultat is not None:
        kontrollera_resultat(rb, profil, t, resultat, avsnitt_id, gransindex=gransindex, formatversion=V7)
    svar = resultat.del_('analys').godkant_svar if resultat else None
    if svar:
        fb = resultat.faktablad
        ai = sammanfor_identiska_ai_stycken(s.model_copy(update={'proveniens': 'ai'})
            for s in _ai_stycken(svar, fb.numeriska(), fb.perioder()))
    else:
        katalog = reservkatalog(rb, profil, t, gransindex=gransindex)
        refs = tuple(dict.fromkeys((t.tjanst, 'D-ARB.B1', *(ref for s in katalog for ref in s.referenser))))
        ai = (lokaltext('Validerad AI-text saknas för tjänstens analys. Analysen behöver kompletteras och granskas '
            'innan dokumentet kan fastställas. Hela katalogunderlaget med villkor finns i bilaga B1. '
            'Lokala utfall och byråns bedömningar visas nedan. [VERIFIERA]', refs),)
    utfall = (() if t.scenarier else utfallsstycken(rb, profil, t, gransindex=gransindex,
        fordelning=tjanstefordelning(rb, profil, t.tjanst)))
    poster = [*ai, *utfall,
        *(s for del_id in ('hot', 'sarbarheter') for s in lasta_stycken_v6(rb, profil, t, del_id, gransindex=gransindex))]
    kategoristart = len(poster)
    poster.append(lokaltext(
        'Kontrollmål är metodval; faktisk täckning prövas nedan. Lokala faktorutfall och hela beräkningen: bilaga B1.'
        if t.scenarier else 'Utfallen förklaras under Analys; relevansen under Lokal analys.', [t.tjanst, 'D-ARB.B1'] if t.scenarier else [t.tjanst]))
    lokalstart = len(poster)
    poster.extend(lokal or (lokaltext(_LOKAL_SAKNAS, [t.tjanst]),))
    nivastart = len(poster)
    poster.extend(nivamotivering_stycken(rb, t, analys, formatversion=V7))
    return Avsnitt(id=avsnitt_id, rubrik='Analys av ' + rb.tjanster[t.tjanst].namn.lower(), kalla='lokal',
        stycken=tuple(poster), underrubriker=tuple(Underrubrik(fore_stycke=p, rubrik=r) for p, r in (
            (0, 'Analys'), (kategoristart, 'Scenarier' if t.scenarier else 'Kategorier'), (lokalstart, 'Lokal analys och slutsats'), (nivastart, 'Risknivå och motivering'))),
        tabeller=((bygg_scenariotabell(rb, t).model_copy(update={'fore_stycke': kategoristart}) if t.scenarier
                   else kategorioversikt(rb, profil, t, analys, gransindex=gransindex, position=kategoristart)),
            *(tab.model_copy(update={'fore_stycke': lokalstart}) for tab in tabeller)), formatversion=V7)
