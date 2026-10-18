"""V7:s korta automatiska upprepningar; författad analys och historiska format lämnas kvar."""


def utan_redundant_hotkolumn(tab):
    """Ta bara bort kolumnen när varje rad uttryckligen har samma hot som rubriken."""
    if 'Hot' not in tab.kolumner or not tab.rader:
        return tab
    n = tab.kolumner.index('Hot')
    if not all(rad.celler[n].text == 'Samma hot som scenariots rubrik' for rad in tab.rader):
        return tab
    rader = []
    for rad in tab.rader:
        celler = tuple(c for i, c in enumerate(rad.celler) if i != n)
        forsta = celler[0].model_copy(update={'referenser': tuple(dict.fromkeys((*celler[0].referenser, *rad.celler[n].referenser)))})
        rader.append(rad.model_copy(update={'celler': (forsta, *celler[1:])}))
    return tab.model_copy(update={'kolumner': tuple(k for i, k in enumerate(tab.kolumner) if i != n), 'rader': tuple(rader)})


def grupperade_profilbelagg(rb, profil, ids, etiketter, *, gransindex):
    """Gruppera endast identisk, redan renderad metadata. Skilda källor, datum och perioder står kvar."""
    from riskanalys.bedomning.erfarenheter import belagd_uppgift
    from riskanalys.dokument.klartext import _kalltext, uppgiftstext
    grupper = {}
    for id in ids:
        text = uppgiftstext(rb, profil, id, namn=etiketter[id], gransindex=gransindex)
        metadata = None
        if belagd_uppgift(rb, profil, id):
            u = profil.uppgifter[id]
            delar = [f'period {u.period.fran}–{u.period.till}'] if u.period else []
            delar += [f'källa: {_kalltext(u.kalla)}', f'bekräftad {u.datum}']
            suffix = ' (' + '; '.join(delar) + ').'
            if text.endswith(suffix):
                text, metadata = text[:-len(suffix)], suffix
        grupper.setdefault(metadata, []).append(text)
    return ' '.join('; '.join(texter) + metadata if metadata else ' '.join(texter)
                    for metadata, texter in grupper.items())


def samla_konstant_betydelse(tab):
    """En identisk full prövning gäller uttryckligen alla rader; avvikelse behåller hela kolumnen."""
    from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
    if 'Betydelse' not in tab.kolumner or len(tab.rader) < 2:
        return tab, None
    n = tab.kolumner.index('Betydelse')
    celler = tuple(rad.celler[n] for rad in tab.rader)
    if not celler[0].text or any(c.text != celler[0].text for c in celler):
        return tab, None
    refs = tuple(dict.fromkeys(ref for c in celler for ref in c.referenser))
    stycke = lokaltext('För samtliga scenarier i tabellen: ' + celler[0].text, refs)
    ny = tab.model_copy(update={'kolumner': tuple(k for i, k in enumerate(tab.kolumner) if i != n),
        'rader': tuple(rad.model_copy(update={'celler': tuple(c for i, c in enumerate(rad.celler) if i != n)}) for rad in tab.rader)})
    return ny, stycke


def samma_tabellkallor(tabeller, kallor, rb):
    """Källtitelinventariet kan utgå bara när varje källa verkligen belägger tabelltexten."""
    from riskanalys.dokument.kallhanvisningar import _kallor, _poster
    poster = _poster(rb, rackvidd=True)
    anvanda = {id for tab in tabeller for rad in tab.rader for c in rad.celler
               for id in _kallor(c.referenser, rb, poster, formatversion='D-ARB-tjanst-v7')}
    return anvanda == set(kallor)
