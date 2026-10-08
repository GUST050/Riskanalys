"""Summarise sanction decisions: scope of review and fee amount per decision."""
import re, sys
from collections import Counter
from pathlib import Path

rows = []
for path in sys.argv[1:]:
    text = Path(path).read_text()
    blocks = re.split(r"\n### ?\n", text)
    for b in blocks[1:]:
        b = re.sub(r"\s+", " ", b)
        name = b.strip().split(" meddelas")[0][:60]
        m = re.search(r"sanktionsavgift (?:om|på) ([\d  ]+) kronor", b)
        amount = int(re.sub(r"\D", "", m.group(1))) if m else None
        if "i någon del" in b:
            scope = "ALLT"
        elif "allmänna riskbedömningen samt" in b or "riskbedömning samt" in b:
            scope = "ARB+rutiner"
        elif "allmänna riskbedömning" in b:
            scope = "ARB"
        else:
            scope = "övrigt"
        kind = "upphöra/vite" if "upphöra" in b else ("sanktionsavgift" if amount else ("anmärkning/varning" if "varning" in b or "anmärkning" in b else "annat"))
        year = re.search(r"(20\d\d)", b)
        rows.append((Path(path).name[:12], year.group(1) if year else "?", scope, kind, amount, name))
for r in rows:
    print(r)
print("\nScope:", Counter(r[2] for r in rows))
print("Kind:", Counter(r[3] for r in rows))
amts = sorted(r[4] for r in rows if r[4])
print("N amounts", len(amts), "min", amts[0], "median", amts[len(amts)//2], "max", amts[-1])
