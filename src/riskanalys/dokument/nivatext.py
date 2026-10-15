"""Risknivåmeningar skrivs av programmet, aldrig av AI (spec 8.4.1)."""

from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.modeller import Dokumenttabell, Tabellcell, Tabellrad, Textstycke
from riskanalys.regelverk.modeller import Regelbas, Sektorsreferens


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


def _sparbegransning(t: Tjanstbedomning, rb: Regelbas) -> str:
    """Kräv identifierbara regler innan en beräkningsförklaring lämnas."""
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
    rader = []
    for namn, delrisk, grund, omraden in (
        ('Penningtvätt', t.inneboende, katalog.grund_sannolikhet if katalog else None, {'penningtvatt', 'bada'}),
        ('Terrorfinansiering', t.terrorfinansiering, katalog.grund_tf_sannolikhet if katalog else None, {'terrorfinansiering', 'bada'}),
    ):
        if delrisk is None:
            berakning, utfall = 'Inget sparat motorutfall.', 'Ej bedömt'
        elif begransning or katalog is None:
            berakning = begransning or 'Begränsning: tjänstens basnivå saknas i regelbasen.'
            utfall = _reduktion(delrisk.risk, t.kvarstaende) if namn == 'Penningtvätt' else delrisk.risk
        else:
            faktorer = [rb.sarbarheter[s] for s in t.tillampade_sarbarheter if rb.sarbarheter[s].galler in omraden]
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
