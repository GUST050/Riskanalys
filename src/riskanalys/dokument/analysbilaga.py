"""Enbart lokal proveniens och beläggsmetadata; inga privata dokumentbytes."""
from riskanalys.analys.provning import registersumma, svarssumma, underlagssumma
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext


def analysbilaga(paket, profil, rb, index, brister):
    if paket is None:
        return (lokaltext('Fryst analysstatus: saknas. Ingen lokal analyskopia låg till grund för dokumentet. [VERIFIERA]'),)
    poster = [lokaltext(f'Lokal analysrevision {paket.revision}. Paketsumma: {registersumma(paket)}. '
        f'Svarssumma: {svarssumma(paket)}. Underlagsbindning: {underlagssumma(paket)}.')]
    for b in paket.belagg:
        referenser = index.refs('belagg', (b.id,))
        period = f' Period {b.period.fran}–{b.period.till}.' if b.period else ''
        text = f'{index.namn("belagg", b.id)}. Registrerat {b.datum}.{period}'
        if b.dokument:
            text += f' Privat dokumentkopia registrerad, SHA256 {b.kontrollsumma}. Sakinnehåll återges inte här.'
        for id in b.profilfalt:
            falt = rb.falt.get(id)
            u = profil.uppgifter.get(id)
            rubrik = (falt.etikett or falt.fraga) if falt else 'Okänt profilfält. [VERIFIERA]'
            text += f' Profilunderlag: {rubrik}.'
            if u:
                text += f' Källa: {u.kalla}; bekräftat {u.datum}.'
        poster.append(lokaltext(text, (*referenser, *b.profilfalt)))
    for s in (*paket.gemensamma_scenarier, *(s for t in paket.tjanster for s in t.scenarier)):
        poster.append(lokaltext('Scenarioreferens: '+index.namn('scenario', s.id)+'. Belägg: '+index.lista('belagg', s.belagg)+'.',
            (*index.refs('scenario', (s.id,)), *index.refs('belagg', s.belagg))))
    for t in paket.tjanster:
        for d in t.delanalyser:
            poster.append(lokaltext('Delanalysreferens: '+index.namn('delanalys', t.tjanst+':'+d.id)+'.', index.refs('delanalys', (t.tjanst+':'+d.id,))))
        tjanstnamn = rb.tjanster[t.tjanst].namn if t.tjanst in rb.tjanster else 'Okänd tjänst. [VERIFIERA]'
        for b in t.block:
            poster.append(lokaltext(f'{tjanstnamn}, analysblock {b.nummer}: {b.aktivering}. {b.motivering} '
                + ('Innehållsbekräftelse registrerad: '+b.bekraftad_summa+'.' if b.bekraftad_summa else 'Ingen innehållsbekräftelse registrerad.')))
    for brist in sorted(brister):
        poster.append(lokaltext('Kompletteringspunkt: '+brist+' [VERIFIERA]'))
    return tuple(poster)
