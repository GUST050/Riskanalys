"""Risknivåmeningar skrivs av programmet, aldrig av AI (spec 8.4.1)."""

from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.modeller import Dokumenttabell, Tabellcell, Tabellrad, Textstycke
from riskanalys.regelverk.modeller import Regelbas, Sarbarhet, Sektorsreferens

PT_OMRADEN = frozenset({'penningtvatt', 'bada'})
TF_OMRADEN = frozenset({'terrorfinansiering', 'bada'})


def nivastycken(t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    """Motorns nivåer med formuleringar som valideringens mönster känner igen."""
    refs = [t.tjanst, *t.regelspar]
    rader = [
        f"Sannolikheten bedöms som {t.inneboende.sannolikhet}. Konsekvensen är {t.inneboende.konsekvens}. "
        f"Den inneboende risken är {t.inneboende.risk}.",
        f"Sannolikheten för terrorfinansiering bedöms som {t.terrorfinansiering.sannolikhet}. "
        f"Konsekvensen för terrorfinansiering är {t.terrorfinansiering.konsekvens}. "
        f"Risken för finansiering av terrorism bedöms som {t.terrorfinansiering.risk}.",
    ]
    if t.kvarstaende:
        rader.append(f"Den kvarstående risken är {t.kvarstaende}.")
    if t.sanktionsrisk and t.sanktionsrisk.inneboende:
        rader.append(f"Sanktionsrisken är {t.sanktionsrisk.inneboende.risk}.")
        if t.sanktionsrisk.kvarstaende:
            rader.append(f"Den kvarstående sanktionsrisken är {t.sanktionsrisk.kvarstaende}.")
    return tuple(Textstycke(typ="beskrivning", text=rad, referenser=refs) for rad in rader)


def sektorsmening(rb: Regelbas, ref: Sektorsreferens) -> str:
    """Sektorsreferensen med källans titel, nivå, skala och sida, utan ID eller koder (spec 8.4.9 punkt 4)."""
    return (f"{rb.kallor[ref.kalla].titel} anger risknivån {ref.niva} för sektorn {ref.sektor} på sin egen skala "
            f"({', '.join(ref.skala)}), sida {ref.sida}. Källans skala är separat från byråns motor och likställs "
            "inte med tjänstens risknivå.")


def sektorsstycken(rb: Regelbas, t: Tjanstbedomning) -> tuple[Textstycke, ...]:
    ref = rb.sektorsreferenser.get(rb.tjanster[t.tjanst].sektorreferens)
    if not ref:
        return ()
    text = f"{sektorsmening(rb, ref)} Motiveringen ska pröva tjänstens egna förhållanden mot denna sektorsreferens."
    return (Textstycke(typ="beskrivning", text=text, referenser=[t.tjanst, ref.id, ref.kalla]),)


def tillampade_faktorer(t: Tjanstbedomning, rb: Regelbas, omraden: frozenset[str]) -> tuple[Sarbarhet, ...]:
    """Sparade tillämpade sårbarheter som gäller riskområdet, i resultatets ordning."""
    return tuple(rb.sarbarheter[s] for s in t.tillampade_sarbarheter if rb.sarbarheter[s].galler in omraden)


def _sparbegransning(t: Tjanstbedomning, rb: Regelbas) -> str:
    """Kräv identifierbara regler innan en beräkningsförklaring lämnas."""
    if t.scenarier:
        return _scenariosparbegransning(t, rb)
    m = rb.metod
    krav = {m.sannolikhet.id, m.konsekvens.id, m.terrorfinansiering.id}
    kanda = rb.alla_id()
    if (not krav <= set(t.regelspar) or any(r not in kanda for r in t.regelspar)
            or not {m.kvarstaende_sankning.id, m.kvarstaende_ej_belagd.id}.intersection(t.regelspar)
            or any(s not in rb.sarbarheter for s in t.tillampade_sarbarheter)):
        return 'Begränsning: saknat eller okänt regelspår; beräkningen kan inte förklaras säkert.'
    for delrisk in (t.inneboende, t.terrorfinansiering):
        if delrisk and not any(r.id in t.regelspar and r.sannolikhet == delrisk.sannolikhet
                               and r.konsekvens == delrisk.konsekvens and r.risk == delrisk.risk
                               for r in m.riskmatris):
            return 'Begränsning: regelspåret saknar en matchande matrisrad för sparat utfall.'
    return ''


def _scenariosparbegransning(t: Tjanstbedomning, rb: Regelbas) -> str:
    """Scenariospår behöver egna metod- och matrisrader, inte den äldre summeringsregeln."""
    m = rb.metod
    metod = m.scenario
    fel = 'Begränsning: saknat eller okänt regelspår; beräkningen kan inte förklaras säkert.'
    if metod is None or metod.aggregering.id not in t.regelspar or any(r not in rb.alla_id() for r in t.regelspar):
        return fel
    for s in t.scenarier:
        krav = {metod.hotniva.id, metod.sarbarhetsniva.id,
                m.konsekvens.id if s.dimension == 'pt' else m.terrorfinansiering.id}
        if (not krav <= set(s.regelspar) or not set(s.regelspar) <= set(t.regelspar)
                or s.hot not in rb.hot or any(id not in rb.sarbarheter for id in s.sarbarheter)
                or any(id not in rb.kontroller for id in s.tackande_kontroller)):
            return fel
        if s.dimension == 'pt' and not {metod.kvarstaende.id, m.kvarstaende_ej_belagd.id}.intersection(s.regelspar):
            return fel
        if not any(r.id in s.regelspar and (r.hot, r.sarbarhet, r.sannolikhet) ==
                   (s.hotniva, s.sarbarhetsniva, s.sannolikhet) for r in metod.sannolikhetsmatris):
            return 'Begränsning: regelspåret saknar en matchande sannolikhetsrad för scenariot.'
        if not any(r.id in s.regelspar and (r.sannolikhet, r.konsekvens, r.risk) ==
                   (s.sannolikhet, s.konsekvens, s.risk) for r in m.riskmatris):
            return 'Begränsning: regelspåret saknar en matchande matrisrad för sparat scenario.'
    return ''


def _scenariorader(t: Tjanstbedomning, rb: Regelbas, begransning: str) -> list[Tabellrad]:
    from riskanalys.dokument.scenariotabell import (scenarioforklaring, kontrollmening, hotnamn,
                                                    scenarioreferenser)
    rader = []
    for s in t.scenarier:
        refs = scenarioreferenser(t, s)
        text = ((begransning + ' ') if begransning else '') + scenarioforklaring(rb, t, s, vikter=True)
        text += ' ' + kontrollmening(rb, s)
        text += ' Sårbarhetsskalan begränsas till låg–hög. Metodval; kontrollmål ersätter inte lokal täckningsprövning.'
        text += ' Regelspår: ' + ', '.join(s.regelspar) + '.'
        namn = s.dimension.upper() + ': ' + hotnamn(rb, s) + (' – avgör nivån' if s.avgorande else '')
        utfall = _reduktion(s.risk, s.kvarstaende) if s.dimension == 'pt' else s.risk + '; ingen kontrollreduktion (TF)'
        rader.append(Tabellrad(celler=(Tabellcell(text=namn, referenser=refs),
                                      Tabellcell(text=text, referenser=refs), Tabellcell(text=utfall, referenser=refs))))
    maxnamn = ', '.join(hotnamn(rb, s) for s in t.scenarier if s.dimension == 'pt' and s.kvarstaende == t.kvarstaende)
    text = (f'Högsta scenario per dimension. PT före kontroll {t.inneboende.risk if t.inneboende else "saknas"}; '
            f'TF {t.terrorfinansiering.risk if t.terrorfinansiering else "saknas"}. '
            f'Högsta kvarstående PT-risk {t.kvarstaende}: {maxnamn}. Regelspår: {rb.metod.scenario.aggregering.id if rb.metod.scenario else "saknas"}.')
    refs = tuple(dict.fromkeys((t.tjanst, *t.regelspar)))
    rader.append(Tabellrad(celler=(Tabellcell(text='Tjänstens maxnivåer'), Tabellcell(text=text, referenser=refs),
                                  Tabellcell(text=t.kvarstaende or 'Saknas', referenser=refs))))
    return rader


def _reduktion(fran: str, till: str | None) -> str:
    if till is None:
        return f'{fran}; kvarstående risk saknas'
    skala = ('låg', 'måttlig', 'hög', 'mycket hög')
    antal = skala.index(fran) - skala.index(till)
    return f'{fran} → {till}; faktisk kontrollreduktion {antal} steg'


def utfallsforklaring(t: Tjanstbedomning, regelbas: Regelbas) -> Dokumenttabell:
    """Återge sparat resultat och låsta faktorer; utvärdera inga profilvillkor."""
    rb = regelbas
    refs = tuple(dict.fromkeys((t.tjanst, *t.regelspar, *t.tillampade_sarbarheter)))
    begransning = _sparbegransning(t, rb)
    katalog = rb.tjanster.get(t.tjanst)
    rader = _scenariorader(t, rb, begransning) if t.scenarier else []
    for namn, delrisk, grund, omraden in (() if t.scenarier else (
        ('Penningtvätt', t.inneboende, katalog.grund_sannolikhet if katalog else None, PT_OMRADEN),
        ('Terrorfinansiering', t.terrorfinansiering, katalog.grund_tf_sannolikhet if katalog else None, TF_OMRADEN),
    )):
        if delrisk is None:
            berakning, utfall = 'Inget sparat motorutfall.', 'Ej bedömt'
        elif begransning or katalog is None:
            berakning = begransning or 'Begränsning: tjänstens basnivå saknas i regelbasen.'
            utfall = _reduktion(delrisk.risk, t.kvarstaende) if namn == 'Penningtvätt' else delrisk.risk
        else:
            faktorer = tillampade_faktorer(t, rb, omraden)
            faktortext = '; '.join(f'{s.namn} +{s.effekt.sannolikhet}' for s in faktorer) or 'inga tillämpade faktorer'
            berakning = (f'Bas {grund}; {faktortext}; tak hög. Sparad sannolikhet {delrisk.sannolikhet}; '
                         f'konsekvens {delrisk.konsekvens}. Metodval, inte en rättsligt föreskriven riskvikt.')
            utfall = delrisk.risk
            if namn == 'Penningtvätt':
                kontroller = [rb.kontroller[k.id].namn if k.id in rb.kontroller else k.id
                              for k in t.kontroller if k.fungerar_och_ar_belagd]
                berakning += (' Motorn registrerar belagd funktion för ' + ', '.join(kontroller) + '.' if kontroller
                              else ' Ingen kontroll med belagd funktion i resultatet.')
                berakning += ' Detta visar inte att kontrollen täcker varje hot.'
                utfall = _reduktion(delrisk.risk, t.kvarstaende)
        radrefs = tuple(dict.fromkeys((*refs, *(k.id for k in t.kontroller)))) if namn == 'Penningtvätt' else refs
        rader.append(Tabellrad(celler=(Tabellcell(text=namn), Tabellcell(text=berakning, referenser=radrefs),
                                      Tabellcell(text=utfall, referenser=radrefs))))
    sank = t.sanktionsrisk
    srefs = tuple(dict.fromkeys((t.tjanst, *(sank.regelspar if sank else ()))))
    if not sank or not sank.inneboende:
        forklaring, utfall = 'Inget sparat motorutfall.', 'Ej bedömt'
    else:
        utfall = _reduktion(sank.inneboende.risk, sank.kvarstaende)
        metod = rb.sanktionsmetod
        if (not metod or metod.id not in sank.regelspar or metod.kontroll not in sank.regelspar
                or sank.kontroll is None or sank.kontroll.id != metod.kontroll
                or any(r not in rb.alla_id() for r in sank.regelspar)
                or not any(r.id in sank.regelspar and r.sannolikhet == sank.inneboende.sannolikhet
                           and r.konsekvens == sank.inneboende.konsekvens and r.risk == sank.inneboende.risk
                           for r in rb.metod.riskmatris)):
            forklaring = 'Begränsning: saknat eller okänt regelspår för sanktioner.'
        else:
            valda = [f'{r.id}: {r.sannolikhet}' for r in metod.rader if r.id in sank.regelspar]
            forklaring = (f'Bas {metod.grund_sannolikhet}; högsta nivå bland sparade regelträffar: '
                          f'{", ".join(valda) or "inga"}; tak hög. Sparad sannolikhet {sank.inneboende.sannolikhet}; '
                          f'konsekvens {sank.inneboende.konsekvens}. Metodval; kontrollreduktion visar inte täckning av varje hot.')
    rader.append(Tabellrad(celler=(Tabellcell(text='Sanktioner'), Tabellcell(text=forklaring, referenser=srefs),
                                  Tabellcell(text=utfall, referenser=srefs))))
    return Dokumenttabell(id=f'{t.tjanst}-utfall', rubrik='Motorns beräkning och sparade utfall',
                          kolumner=('Riskområde', 'Motorns beräkning', 'Sparat utfall'), rader=tuple(rader), fore_stycke=0)
