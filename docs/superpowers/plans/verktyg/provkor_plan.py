"""Bygger projektet ur en implementeringsplan, steg för steg, i en tom mapp.

Skriptet följer planens steg i ordning: "Skriv `fil`" skriver kodblocket till filen, "Lägg till ... sist i
`fil`" lägger till kodblocket sist (och importer som steget nämner), och "Registrera ... i `cli.py`" ersätter
kommandolistan. Övriga steg (körningar, commit, ändringar i dokumentation) hoppas över och listas.

Användning: python3 -I provkor_plan.py <plan.md> <tom utmapp> [--till-task N] [--repo REPOROT]

--repo anger repots rot, där de filer i REPOFILER som testerna läser hämtas. Standard är tre nivåer
ovanför planfilen, vilket stämmer när planen ligger i docs/superpowers/plans/.
"""

import re
import shutil
import sys
from pathlib import Path

# Filer i repot som planens tester läser men som planen inte skriver.
REPOFILER = ("docs/research/typfall/tillsyn-2026.json",)

STEG = re.compile(r"^- \[ \] \*\*Step (\d+[a-z]?): (.+)\*\*\s*$")
TASK = re.compile(r"^### Task (\d+):")
SKRIV = re.compile(r"^Skriv [^`]*`([^`]+)`$")
SOKVAG_FORE_BLOCK = re.compile(r"^`([^`]+)`:\s*$")
STAKET = re.compile(r"^(`{3,})(\w*)\s*$")


def block_i(rader):
    """Returnerar [(föregående icke-tomma rad, språk, innehåll)] för kodblocken i ett steg."""
    block, i, foregaende = [], 0, ""
    while i < len(rader):
        m = STAKET.match(rader[i])
        if m:
            staket, sprak = m.group(1), m.group(2)
            j = i + 1
            while not rader[j].startswith(staket) or rader[j].strip() != staket:
                j += 1
            block.append((foregaende, sprak, "\n".join(rader[i + 1 : j]) + "\n"))
            i = j + 1
            continue
        if rader[i].strip():
            foregaende = rader[i].strip()
        i += 1
    return block


def tillamp(rubrik, rader, rot, logg):
    block = block_i(rader)
    text = "\n".join(rader)
    skriv = SKRIV.match(rubrik)
    if skriv:
        sokvag = rot / skriv.group(1)
        sokvag.parent.mkdir(parents=True, exist_ok=True)
        sokvag.write_text(block[0][2], encoding="utf-8")
        logg.append(f"skriv {skriv.group(1)}")
        for foregaende, _, innehall in block[1:]:
            extra = SOKVAG_FORE_BLOCK.match(foregaende)
            if extra:
                (rot / extra.group(1)).parent.mkdir(parents=True, exist_ok=True)
                (rot / extra.group(1)).write_text(innehall, encoding="utf-8")
                logg.append(f"skriv {extra.group(1)}")
        return
    if rubrik.startswith("Skriv lydelsetexterna"):
        for foregaende, _, innehall in block:
            m = SOKVAG_FORE_BLOCK.match(foregaende)
            (rot / m.group(1)).parent.mkdir(parents=True, exist_ok=True)
            (rot / m.group(1)).write_text(innehall, encoding="utf-8")
            logg.append(f"skriv {m.group(1)}")
        return
    m = re.search(r"`([^`]+\.py)`", rubrik)
    if rubrik.startswith("Lägg till") and m:
        sokvag = rot / m.group(1)
        innehall = sokvag.read_text(encoding="utf-8")
        for importrad in re.findall(r"Lägg till `((?:from|import) [^`]+)` bland importerna", text):
            innehall = _lagg_till_import(innehall, importrad)
        for _, sprak, nytt in block:
            if sprak == "python":
                innehall = innehall.rstrip("\n") + "\n\n\n" + nytt
        sokvag.write_text(innehall, encoding="utf-8")
        logg.append(f"utöka {m.group(1)}")
        return
    if rubrik.startswith("Registrera") and m:
        sokvag = rot / m.group(1)
        innehall = sokvag.read_text(encoding="utf-8")
        if "Ersätt raderna" in text:
            gammalt, nytt = block[0][2], block[1][2]
            assert gammalt in innehall, (rubrik, gammalt)
            innehall = innehall.replace(gammalt, nytt)
        else:
            innehall = re.sub(r"from riskanalys\.kommandon import .*?\nKOMMANDON = \[[^\]]*\]\n", block[0][2], innehall, flags=re.S)
        sokvag.write_text(innehall, encoding="utf-8")
        logg.append(f"registrera i {m.group(1)}")
        return
    logg.append(f"(hoppar över) {rubrik}")


def _lagg_till_import(innehall, importrad):
    rader = innehall.split("\n")
    sista = max(i for i, rad in enumerate(rader) if rad.startswith(("import ", "from ")))
    forsta = min(i for i, rad in enumerate(rader) if rad.startswith(("import ", "from ")))
    if importrad.startswith("import ") or importrad.split()[1] in {"datetime", "pathlib", "collections", "typing"}:
        rader.insert(forsta, importrad)
    else:
        rader.insert(sista + 1, importrad)
    return "\n".join(rader)


def main():
    plan, rot = Path(sys.argv[1]), Path(sys.argv[2])
    till = int(sys.argv[sys.argv.index("--till-task") + 1]) if "--till-task" in sys.argv else 99
    repo = Path(sys.argv[sys.argv.index("--repo") + 1]) if "--repo" in sys.argv else plan.resolve().parents[3]
    rader = plan.read_text(encoding="utf-8").split("\n")
    logg, task, i = [], 0, 0
    steg = []
    i_block = [False] * len(rader)
    staket = None
    for k, rad in enumerate(rader):
        m = STAKET.match(rad)
        if staket is None and m:
            staket = m.group(1)
            i_block[k] = True
        elif staket is not None:
            i_block[k] = True
            if rad.strip() == staket:
                staket = None
    def gräns(k):
        return not i_block[k] and (STEG.match(rader[k]) or TASK.match(rader[k]) or rader[k].startswith("## "))
    while i < len(rader):
        t = TASK.match(rader[i]) if not i_block[i] else None
        if t:
            task = int(t.group(1))
        s = STEG.match(rader[i]) if not i_block[i] else None
        if s:
            j = i + 1
            while j < len(rader) and not gräns(j):
                j += 1
            steg.append((task, s.group(2), rader[i + 1 : j]))
            i = j
            continue
        i += 1
    for task, rubrik, steginnehall in steg:
        if task > till:
            break
        tillamp(rubrik, steginnehall, rot, logg)
    for relativ in REPOFILER:
        kalla = repo / relativ
        if not kalla.is_file():
            logg.append(f"VARNING: {kalla} saknas. Ange repots rot med --repo, annars fallerar tester som läser filen.")
            continue
        (rot / relativ).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(kalla, rot / relativ)
        logg.append(f"kopiera från repot {relativ}")
    print("\n".join(logg))


main()
