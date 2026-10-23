"""Kolumnbredder för den nya dispositionen; samma minsta textstorlek som V9."""
from docx.oxml.ns import qn
from docx.shared import Pt


def anpassa_tabeller(word):
    normal = word.styles['Normal'].paragraph_format
    normal.line_spacing = 1.0
    normal.space_after = Pt(3)
    vikter = {
        'Dokumentfakta': (27, 73),
        'Bekräftade verksamhetsuppgifter': (33, 43, 12, 12),
        'Tjänsternas innehåll och arbetssätt': (17, 33, 8, 12, 10, 20),
        'Hotbild': (25, 7, 47, 21),
        'Riskindikatorer': (25, 11, 29, 35),
        'Indikatorer på potentiellt lägre risk': (23, 9, 26, 14, 28),
        'PTL 2 kap. 4–5 §§, punkt för punkt': (12, 38, 16, 34),
        'Faktiska rutinhänvisningar': (20, 18, 10, 22, 15, 15),
    }
    bredd = word.sections[0].page_width - word.sections[0].left_margin - word.sections[0].right_margin
    for table in word.tables:
        fore = table._tbl.getprevious()
        rubrik = ''.join(fore.itertext()) if fore is not None else ''
        # OOXML itertext kan återge samma rubrik flera gånger. Jämför ingående titel.
        vikt = next((v for k, v in vikter.items() if k in rubrik), None)
        if not vikt or len(vikt) != len(table.columns):
            continue
        for col, v in zip(table.columns, vikt, strict=True):
            col.width = int(bredd * v / sum(vikt))
        for row in table.rows:
            for cell, v in zip(row.cells, vikt, strict=True):
                cell.width = int(bredd * v / sum(vikt))
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing = 1.0
                for margin in cell._tc.xpath('./w:tcPr/w:tcMar/*'):
                    if margin.tag in (qn('w:top'), qn('w:bottom')):
                        margin.set(qn('w:w'), '45')
