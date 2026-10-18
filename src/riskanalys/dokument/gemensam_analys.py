"""Dela endast exakt identiska lokala resonemang med uttrycklig tjänstetillämpning."""
from riskanalys.dokument.analystabeller import nummerintervall
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext


def _delbar(s):
    """Byråns nivåmotivering (typ motivering) står alltid kvar i sin tjänst och delas aldrig."""
    return (s.proveniens == 'lokal' and s.typ != 'motivering' and ':' in s.text and len(s.text.split()) >= 10
            and '[VERIFIERA]' not in s.text)


def _flytta_positioner(a, nya):
    """Underrubriker och tabeller pekar på samma innehåll efter att delade stycken ersatts."""
    return a.model_copy(update={
        'underrubriker': tuple(u.model_copy(update={'fore_stycke': nya[u.fore_stycke]}) for u in a.underrubriker),
        'tabeller': tuple(t.model_copy(update={'fore_stycke': nya[t.fore_stycke]}) for t in a.tabeller)})


def sammanfor_identisk_lokaltext(avsnitt):
    grupper = {}
    for a in avsnitt:
        for s in a.stycken:
            if _delbar(s):
                grupper.setdefault(s.text, []).append((a, s))
    delade = {text: poster for text, poster in grupper.items() if len({a.id for a, _ in poster}) > 1}
    nummer = {text: n for n, text in enumerate(delade, 1)}
    gemensamt = []
    for text, poster in delade.items():
        refs = tuple(dict.fromkeys(ref for _, s in poster for ref in s.referenser))
        prefix = '' if poster[0][0].formatversion == 'D-ARB-tjanst-v7' else 'Gemensamt resonemang '
        gemensamt.append(lokaltext(f'{prefix}{nummer[text]}. {text}', refs))
    resultat = []
    kartposter = []
    for a in avsnitt:
        valda = [s for s in a.stycken if _delbar(s) and s.text in delade]
        stycken = []
        nya = []
        infogad = False
        delstarter = {u.fore_stycke for u in a.underrubriker} if a.formatversion == 'D-ARB-tjanst-v7' else set()
        for i, s in enumerate(a.stycken):
            if i in delstarter:
                infogad = False
            nya.append(len(stycken))
            if not _delbar(s) or s.text not in delade:
                stycken.append(s)
                continue
            if not infogad:
                karta = nummerintervall(nummer[x.text] for x in valda)
                refs = ['D-ARB.5', 'D-ARB.B1', a.id]
                belaggsmening = '' if a.formatversion == 'D-ARB-tjanst-v7' and any(
                    ref.startswith('P-') for s in a.stycken for ref in s.referenser) else ' Fältkoppling och belägg: bilaga B1.'
                text = ('Se gemensamma resonemang '+karta+'.' if a.formatversion == 'D-ARB-tjanst-v7' else
                        'Gemensamma resonemang '+karta+' gäller för denna tjänst.')
                stycken.append(lokaltext(text+belaggsmening, refs))
                infogad = True
            kartposter.append(lokaltext(a.rubrik+'. '+s.text.split(':', 1)[0]+': gemensamt resonemang '+str(nummer[s.text])+'.',
                (*s.referenser, a.id, 'D-ARB.5')))
        nya.append(len(stycken))
        resultat.append(_flytta_positioner(a, nya).model_copy(update={'stycken': tuple(stycken)}))
    return tuple(resultat), tuple(gemensamt), tuple(kartposter)


def sammanfor_identiska_tabelltexter(avsnitt):
    """Bevara samma saktext en gång, med explicita hänvisningar från varje berörd cell."""
    grupper = {}
    for a in avsnitt:
        for tab in a.tabeller:
            for rad in tab.rader:
                for cell in rad.celler:
                    if cell.proveniens == 'lokal' and len(cell.text.split()) >= 40 and '[VERIFIERA]' not in cell.text:
                        grupper.setdefault(cell.text, []).append(cell)
    delade = {text: poster for text, poster in grupper.items() if len(poster) > 1}
    nummer = {text: n for n, text in enumerate(delade, 1)}
    texter = tuple(lokaltext(f'Tabellresonemang {nummer[text]}. {text}',
        tuple(dict.fromkeys(ref for c in celler for ref in c.referenser))) for text, celler in delade.items())
    resultat = []
    for a in avsnitt:
        tabeller = tuple(tab.model_copy(update={'rader': tuple(rad.model_copy(update={'celler': tuple(
            cell.model_copy(update={'text': f'Tabellresonemang {nummer[cell.text]}',
                'referenser': tuple(dict.fromkeys(('D-ARB.5', *cell.referenser)))}) if cell.text in delade else cell
            for cell in rad.celler)}) for rad in tab.rader)}) for tab in a.tabeller)
        resultat.append(a.model_copy(update={'tabeller': tabeller}))
    return tuple(resultat), texter
