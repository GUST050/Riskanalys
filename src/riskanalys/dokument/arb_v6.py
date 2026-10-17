"""V6 sammanför skyddad AI-text och lokal prövning utan nya riskbeslut."""
from collections.abc import Mapping
from itertools import accumulate

from riskanalys.analys.modeller import Analyspaket
from riskanalys.analys.provning import analysbrister
from riskanalys.dokument.analysreferenser import bygg_analysreferenser
from riskanalys.dokument.analysbilaga import analysbilaga
from riskanalys.dokument.delskrivning import Tjanstresultat
from riskanalys.dokument.analysstatus import analysstatus, modellstatus
from riskanalys.dokument.analystabeller import scenariorad
from riskanalys.dokument.lokaltext_v6 import bygg_lokaltext
from riskanalys.dokument.gemensam_analys import sammanfor_identisk_lokaltext, sammanfor_identiska_tabelltexter
from riskanalys.dokument.rackvidd_v6 import rackviddsoversikt
from riskanalys.dokument.arb_v5 import stycke
from riskanalys.dokument.foljder_v6 import bygg_foljder_v6
from riskanalys.dokument.tabeller import tabell
from riskanalys.drift.modellrapport import Modellvalidering
from riskanalys.dokument.arb_v5_1 import METODFRAGOR, _rackviddsstycken, _sakkunnigstatus
from riskanalys.dokument.kallhanvisningar import med_kallhanvisningar, utan_kallhanvisning
from riskanalys.dokument.m1_forslag import m1_forslag
from riskanalys.dokument.modeller import Avsnitt, Dokument, Underrubrik
from riskanalys.dokument.nivatext import utfallsforklaring, sektorsmening
from riskanalys.dokument.skrivversion import V6
from riskanalys.dokument.tabeller import bygg_metodmatris, bygg_riskoversikt, bygg_tjansteoversikt
from riskanalys.dokument.tjanstavsnitt_v6 import bygg_tjanstavsnitt_v6, lokaltext
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.drift.historik import Historik
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.granser import metodgransindex

FORMATVERSION = V6
B1_ID = 'D-ARB.B1'
# B1:s navigeringsrubriker i byggarens ordning. De ingår i modellen och därmed i sakgranskningen,
# avsnittets kontrollsumma, struktursumman och v6-återbygget. Delanalyser och analysblock varvas
# tjänst för tjänst och delar därför en rubrik, som nämner delanalyser bara när sådana finns.
B1_DELRUBRIKER = (
    'Profiluppgifter', 'Källversioner', 'Omfattningsregel', 'Gemensamma resonemang per tjänst',
    'Källbunden kontrollräckvidd', 'Lokal analys och belägg', 'Scenarioreferenser', 'Analysblock',
    'Delanalyser och analysblock', 'Kompletteringspunkter', 'Beräkningsunderlag', 'Regelvis sakkunnigstatus',
    'Källregister')
(PROFILUPPGIFTER, KALLVERSIONER, OMFATTNINGSREGEL, GEMENSAMMA_RESONEMANG, KONTROLLRACKVIDD, LOKAL_ANALYS,
 SCENARIOREFERENSER, ANALYSBLOCK, DELANALYSER_OCH_ANALYSBLOCK, KOMPLETTERINGSPUNKTER, BERAKNINGSUNDERLAG,
 SAKKUNNIGSTATUS, KALLREGISTER) = B1_DELRUBRIKER
_DRIFT = 'B1:s {delnamn} har inte den väntade formen; uppdatera delindelningen i arb_v6 så att rubrikerna inte flyttas.'
ALDRE_UTKAST = ("AI-utkastet för {avsnitt} kan inte användas i dokumentformatet {format}. Utkastets identitet visar "
                "att det skrevs i ett äldre format eller inte av den aktuella skrivaren. Kör 'riskanalys skriv' igen "
                "och granska sedan på nytt med 'riskanalys granska'.")


def kontrollera_v6_utkast(resultat: Mapping[str, object]) -> None:
    """Stoppa före bygget om något utkast inte är ett tjänstresultat från den aktuella v6-skrivaren."""
    for avsnitt_id, post in resultat.items():
        if not isinstance(post, Tjanstresultat) or post.formatversion != V6:
            raise RiskanalysFel(ALDRE_UTKAST.format(avsnitt=avsnitt_id, format=V6))


def avsnitt(id, rubrik, stycken=(), tabeller=(), *, kalla='regelbas', underrubriker=()):
    return Avsnitt(id=id, rubrik=rubrik, kalla=kalla, stycken=tuple(stycken), tabeller=tuple(tabeller),
                   underrubriker=tuple(underrubriker), formatversion=V6)


def _profil_och_kallversioner(underlag: Avsnitt, rb) -> tuple[tuple, tuple]:
    """Intagsunderlaget slutar med ett stycke per registrerad källa, i regelbasens ordning."""
    grans = len(underlag.stycken) - len(rb.kallor)
    kallor = underlag.stycken[max(grans, 0):]
    if grans < 0 or [s.referenser for s in kallor] != [[id] for id in rb.kallor]:
        raise ValueError(_DRIFT.format(delnamn='källversioner'))
    return underlag.stycken[:grans], kallor


def _analysdelar(analys: Analyspaket | None, poster: tuple, brister: tuple) -> tuple:
    """Analysbilagans poster delade efter hur många poster varje del har i det frysta paketet."""
    if analys is None:
        antal = ((LOKAL_ANALYS, len(poster)),)
    else:
        block = DELANALYSER_OCH_ANALYSBLOCK if any(t.delanalyser for t in analys.tjanster) else ANALYSBLOCK
        antal = (
            (LOKAL_ANALYS, 1 + len(analys.belagg)),
            (SCENARIOREFERENSER, len(analys.gemensamma_scenarier) + sum(len(t.scenarier) for t in analys.tjanster)),
            (block, sum(len(t.delanalyser) + len(t.block) for t in analys.tjanster)),
            (KOMPLETTERINGSPUNKTER, len(brister)),
        )
    granser = tuple(accumulate((n for _, n in antal), initial=0))
    if granser[-1] != len(poster):
        raise ValueError(_DRIFT.format(delnamn='analysbilaga'))
    return tuple((rubrik, poster[start:slut], ()) for (rubrik, _), start, slut in zip(antal, granser, granser[1:]))


def _berakningsdel(rb, bedomning) -> tuple[tuple, tuple]:
    """Ett stycke per tjänst och tjänstens utfallstabell på samma position, räknat från delens början."""
    tjanster = tjanster_med_avsnitt(bedomning)
    poster = tuple(stycke('Beräkningsunderlag för ' + rb.tjanster[t.tjanst].namn + '.', [id]) for id, t in tjanster)
    tabeller = tuple(utfallsforklaring(t, rb).model_copy(update={'fore_stycke': n}) for n, (_, t) in enumerate(tjanster))
    return poster, tabeller


def _sammanfoga_delar(delar) -> tuple[tuple, tuple, tuple]:
    """Stycken, underrubriker och tabeller ur (rubrik, stycken, tabeller) i byggarens ordning.

    En tom del får ingen rubrik. Tabellernas positioner anges inom delen och flyttas med delens början.
    """
    icke_tomma = tuple(d for d in delar if d[1])
    starter = tuple(accumulate((len(poster) for _, poster, _ in icke_tomma), initial=0))
    stycken = tuple(s for _, poster, _ in icke_tomma for s in poster)
    rubriker = tuple(Underrubrik(fore_stycke=start, rubrik=rubrik) for (rubrik, _, _), start in zip(icke_tomma, starter))
    tabeller = tuple(t.model_copy(update={'fore_stycke': start + t.fore_stycke})
                     for (_, _, deltabeller), start in zip(icke_tomma, starter) for t in deltabeller)
    return stycken, rubriker, tabeller


def bilaga_b1_v6(rb, profil, bedomning, analys, *, refindex, brister, tillampningskarta, metodposter, gransindex) -> Avsnitt:
    """B1 före källregistret: varje del får sin rubrik i modellen på delens första stycke."""
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    from riskanalys.dokument.uppfoljning import omfattningsregel_i_bilaga
    underlag = bygg_underlagsbilaga(rb, profil, gransindex=gransindex)
    profiluppgifter, kallversioner = _profil_och_kallversioner(underlag, rb)
    berakning, utfall = _berakningsdel(rb, bedomning)
    status = stycke('Regelvis sakkunnigstatus: ' + '; '.join(f'{r.id}: {_sakkunnigstatus(r)}' for r in metodposter) + '.',
                    [r.id for r in metodposter])
    stycken, rubriker, tabeller = _sammanfoga_delar((
        (PROFILUPPGIFTER, profiluppgifter, ()),
        (KALLVERSIONER, kallversioner, ()),
        (OMFATTNINGSREGEL, omfattningsregel_i_bilaga(rb), ()),
        (GEMENSAMMA_RESONEMANG, tuple(tillampningskarta), ()),
        (KONTROLLRACKVIDD, _rackviddsstycken(rb, bedomning), ()),
        *_analysdelar(analys, analysbilaga(analys, profil, rb, refindex, brister), brister),
        (BERAKNINGSUNDERLAG, berakning, utfall),
        (SAKKUNNIGSTATUS, (status, m1_forslag()), ()),
    ))
    return avsnitt(underlag.id, underlag.rubrik, stycken, tabeller, kalla=underlag.kalla, underrubriker=rubriker)


def med_kallregisterrubrik(dokument: Dokument, bilaga: Avsnitt) -> Dokument:
    """Källregistret läggs sist i B1 av med_kallhanvisningar; rubriken står före dess första post."""
    def med_rubrik(a: Avsnitt) -> Avsnitt:
        if a.id != B1_ID:
            return a
        ofarglagda = tuple(s.model_copy(update={'text': utan_kallhanvisning(s.text)}) for s in a.stycken[:len(bilaga.stycken)])
        if ofarglagda != bilaga.stycken or a.underrubriker != bilaga.underrubriker:
            raise ValueError(_DRIFT.format(delnamn='källregister'))
        if len(a.stycken) == len(bilaga.stycken):
            return a
        rubrik = Underrubrik(fore_stycke=len(bilaga.stycken), rubrik=KALLREGISTER)
        return a.model_copy(update={'underrubriker': (*a.underrubriker, rubrik)})
    return dokument.model_copy(update={'avsnitt': tuple(med_rubrik(a) for a in dokument.avsnitt)})


def utvarderingsavsnitt_v6(historik: Historik) -> Avsnitt:
    utvarderad = historik.senaste_utvardering()
    uppdaterad = historik.senaste_uppdatering()
    nasta = historik.nasta_genomgang()
    return avsnitt('D-ARB.10', 'Utvärdering och uppdatering', (
        lokaltext(f'Senaste utvärdering: {utvarderad}.' if utvarderad else 'Ingen registrerad utvärdering. [VERIFIERA]'),
        lokaltext(f'Senaste separata uppdatering: {uppdaterad}.' if uppdaterad else 'Ingen registrerad separat uppdatering.'),
        lokaltext(f'Nästa genomgång senast {nasta}. Uppdateringar flyttar inte denna frist.' if nasta else 'Nästa genomgång kan inte bestämmas utan utvärderingsdatum. [VERIFIERA]'),
    ), kalla='lokal')


def _oppna_metodfragor(fragor: tuple[str, ...]) -> str:
    """En mening för alla öppna metodfrågor. Ingen per-fråga-status finns (en objektattest avgör inte frågan), så alla är öppna."""
    gemena = [f[0].lower() + f[1:] if not f.startswith('TF ') else f for f in fragor]
    uppraknade = f"{', '.join(gemena[:-1])} samt {gemena[-1]}"
    return (f'Öppna metodfrågor: {uppraknade}. Ingen av dem är sakkunnigprövad; '
            'risköversikten visar vad det betyder för nivåerna.')


def bygg_arb_v6(rb, profil, bedomning, resultat, historik, *, analys: Analyspaket | None, gransindex=None, modellrapport: Modellvalidering | None = None) -> Dokument:
    from riskanalys.dokument.arb import _syfte, _metod
    from riskanalys.dokument.uppfoljning import bevakningsavsnitt, kort_omfattningsstycke, uppfoljningsstycken
    kontrollera_v6_utkast(resultat)
    index = gransindex if gransindex is not None else metodgransindex(rb)
    refindex = bygg_analysreferenser(analys)
    brister = analysbrister(rb, profil, bedomning, analys) if analys is not None else ()
    metodposter = (*rb.metod.regler(), *rb.metod.riskmatris)
    status = f'Metodstatus: {sum(_sakkunnigstatus(r) == "verifierad" for r in metodposter)} av {len(metodposter)} regelobjekt har giltig sakkunnigverifiering. Objektattester avgör inte i sig öppna metodfrågor.'
    syfte = _syfte(rb, profil, bedomning).model_copy(update={'formatversion': V6})
    oversikt = avsnitt('D-ARB.8', 'Tjänstevis risksammanställning', (
        stycke('Nivåerna är motorns utfall. Varje tjänsteavsnitt förklarar vilka faktorer som avgör nivån och byråns egen bedömning. '
              'Hela beräkningen finns i bilaga B1. Ingen sammanvägd byrånivå beräknas.', ['D-ARB.B1']),
        stycke(status),
        *analysstatus(rb, bedomning, analys, brister),
        *modellstatus(analys, modellrapport),
    ), (bygg_riskoversikt(bedomning, rb),))
    sektorer = sorted({rb.tjanster[t.tjanst].sektorreferens for t in bedomning.tjanster if t.inneboende and rb.tjanster[t.tjanst].sektorreferens})
    metod = avsnitt('D-ARB.2', 'Metod och begränsningar', (
        _metod(rb, bedomning).stycken[0],
        stycke('PT avser penningtvätt och TF finansiering av terrorism. Faktisk scenariotäckning prövas lokalt.'),
        *(stycke(sektorsmening(rb, rb.sektorsreferenser[id]), [id, rb.sektorsreferenser[id].kalla]) for id in sektorer),
        kort_omfattningsstycke(rb, profil, bedomning, gransindex=index),
        stycke(_oppna_metodfragor(METODFRAGOR)),
    ), (bygg_metodmatris(rb),))
    tjanster = avsnitt('D-ARB.3', 'Byråns tjänster', (stycke('Kundantal överlappar mellan tjänster och summeras inte till unika kunder.'),),
        (bygg_tjansteoversikt(rb, profil, bedomning, gransindex=index),))
    kontroller = avsnitt('D-ARB.7', 'Källbunden kontrollräckvidd', rackviddsoversikt(rb, bedomning))
    analyser = {a.tjanst: a for a in analys.tjanster} if analys else {}
    risk = []
    for id, t in tjanster_med_avsnitt(bedomning):
        a = analyser.get(t.tjanst)
        lokal, tabeller = bygg_lokaltext(a, analys, rb, refindex) if a is not None else (None, ())
        risk.append(bygg_tjanstavsnitt_v6(rb, profil, t, resultat.get(id), id, gransindex=index, lokal=lokal,
                                          tabeller=tabeller, analys=a))
    risk, gemensamma_resonemang, tillampningskarta = sammanfor_identisk_lokaltext(risk)
    myndighetskallor = sorted({k for t in bedomning.tjanster if t.inneboende for id in t.hot for k in rb.hot[id].kallor})
    gemensamt = avsnitt('D-ARB.4', 'Gemensamma scenarier', (
        stycke('Myndighetsunderlag: '+'; '.join(rb.kallor[id].titel for id in myndighetskallor)+'. Händelseförloppen återges en gång. Relevans, samma/avviker och lokala begränsningar prövas uttryckligen vid varje tjänst.', myndighetskallor),
    ), (tabell('gemensamma-scenarier', 'Gemensamma händelseförlopp', ('Scenario', 'Händelseförlopp', 'Betydelse', 'Hot', 'Belägg'),
        (scenariorad(s, rb, refindex) for s in analys.gemensamma_scenarier)),) if analys and analys.gemensamma_scenarier else ())
    tabellavsnitt, tabellresonemang = sammanfor_identiska_tabelltexter((gemensamt, *risk))
    gemensamt, *risk = tabellavsnitt
    gemensam_analys = avsnitt('D-ARB.5', 'Gemensamma lokala resonemang', (*gemensamma_resonemang, *tabellresonemang), kalla='lokal')
    bilaga = bilaga_b1_v6(rb, profil, bedomning, analys, refindex=refindex, brister=brister,
                          tillampningskarta=tillampningskarta, metodposter=metodposter, gransindex=index)
    uppfoljning = utvarderingsavsnitt_v6(historik)
    uppfoljning = uppfoljning.model_copy(update={'stycken': (*uppfoljning.stycken, *uppfoljningsstycken(rb, profil, gransindex=index))})
    # D-ARB.9 står direkt efter tjänsternas åtgärdstabeller och före utvärderingen (planens disposition 8–10).
    foljder = bygg_foljder_v6(rb, bedomning, analys, refindex)
    poster = (syfte, oversikt, metod, tjanster, gemensamt, gemensam_analys, kontroller, *risk, foljder, uppfoljning, bevakningsavsnitt(rb, profil, gransindex=index), bilaga)
    poster = tuple(a.model_copy(update={'formatversion': V6, 'visningsnummer': 'B1' if a.id == B1_ID else str(n)}) for n, a in enumerate(poster, 1))
    from riskanalys.dokument.matning import med_langdvarning
    dokument = med_kallhanvisningar(Dokument(id='D-ARB', titel='Allmän riskbedömning', avsnitt=poster), rb)
    return med_langdvarning(med_kallregisterrubrik(dokument, bilaga), profil)
