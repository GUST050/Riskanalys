"""Dela endast exakt identiska lokala resonemang med uttrycklig tjänstetillämpning."""
from riskanalys.dokument.analystabeller import nummerintervall
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext


def sammanfor_identisk_lokaltext(avsnitt):
    grupper = {}
    for a in avsnitt:
        for s in a.stycken:
            if s.proveniens == 'lokal' and ':' in s.text and len(s.text.split()) >= 10 and '[VERIFIERA]' not in s.text:
                grupper.setdefault(s.text, []).append((a, s))
    delade = {text: poster for text, poster in grupper.items() if len({a.id for a, _ in poster}) > 1}
    nummer = {text: n for n, text in enumerate(delade, 1)}
    gemensamt = []
    for text, poster in delade.items():
        refs = tuple(dict.fromkeys(ref for _, s in poster for ref in s.referenser))
        gemensamt.append(lokaltext(f'Gemensamt resonemang {nummer[text]}. {text}', refs))
    resultat = []
    kartposter = []
    for a in avsnitt:
        valda = [s for s in a.stycken if s.text in delade]
        stycken = []
        infogad = False
        for s in a.stycken:
            if s.text not in delade:
                stycken.append(s)
                continue
            if not infogad:
                karta = nummerintervall(nummer[x.text] for x in valda)
                refs = ['D-ARB.5', 'D-ARB.B1', a.id]
                stycken.append(lokaltext('Gemensamma resonemang '+karta+' gäller för denna tjänst. Fältkoppling och belägg: bilaga B1.', refs))
                infogad = True
            kartposter.append(lokaltext(a.rubrik+'. '+s.text.split(':', 1)[0]+': gemensamt resonemang '+str(nummer[s.text])+'.',
                (*s.referenser, a.id, 'D-ARB.5')))
        resultat.append(a.model_copy(update={'stycken': tuple(stycken)}))
    return tuple(resultat), tuple(gemensamt), tuple(kartposter)


def sammanfor_identiska_tabelltexter(avsnitt):
    """Bevara samma saktext en gång, med explicita hänvisningar från varje berörd cell."""
    grupper = {}
    for a in avsnitt:
        for tab in a.tabeller:
            for rad in tab.rader:
                for cell in rad.celler:
                    if cell.proveniens == 'lokal' and len(cell.text.split()) >= 12 and '[VERIFIERA]' not in cell.text:
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
