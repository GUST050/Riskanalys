"""Paragraftexter ur hämtade primärkällor (researchverktyg, inte en del av programmet).

Läser föreskrifternas text (pdftotext -layout) eller PTL:s text från rkrattsbaser och delar upp den i
paragrafer. Rubriker och allmänna råd ingår inte i paragraftexten. Kontrollsumman räknas som i
riskanalys.regelverk.laddning.lydelsetextens_kontrollsumma: alla blanktecken ihopslagna till ett mellanslag.

Användning:
  python3 -I lydelsetexter.py fs <fil.txt> <lagrum> [<lagrum> ...]
  python3 -I lydelsetexter.py sfs <fil.txt> <lagrum> [<lagrum> ...]
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

_SIDHUVUD = re.compile(r"^\s*(\d{1,3}|\d{2}FS \d{4}:\d+|[A-ZÅÄÖ][a-zåäö]+ läns författningssamling)\s*$")
_HOGERKOLUMN = re.compile(r"\s{3,}(\d{2}FS \d{4}:\d+|Utkom från trycket|den \d+ \w+ \d{4}\.?)\s*$")
_KAPITEL = re.compile(r"^\s{0,3}(\d+ (?:a )?kap\.)\s+[A-ZÅÄÖ]")
_PARAGRAF = re.compile(r"^\s{0,3}(\d+(?: [a-z])?) §\s+(?=\S)")
_ALLMANNA_RAD = re.compile(r"^\s{0,3}Allmänna råd\s*$")


def kontrollsumma(text: str) -> str:
    return "sha256:" + hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def _rader_fs(text: str) -> list[str]:
    rader = []
    for rad in text.replace("\f", "\n").split("\n"):
        if _SIDHUVUD.match(rad) or re.fullmatch(r"\s*_{3,}\s*", rad):
            continue
        rader.append(_HOGERKOLUMN.sub("", rad.rstrip()))
    return rader


def _ar_rubrik(rad: str, nasta: str) -> bool:
    """En rubrik är en kort rad utan slutpunkt som följs av en ny paragraf eller en ny rubrik."""
    s = rad.strip()
    return bool(s) and not s.endswith((".", ",", ";", ":")) and len(s) < 70 and not s.startswith(("–", "-")) and (
        bool(_PARAGRAF.match(nasta)) or bool(_KAPITEL.match(nasta))
    )


def paragrafer_fs(text: str) -> dict[str, str]:
    """Föreskrifternas paragrafer som {"2 kap. 3 §": text}, utan rubriker och allmänna råd."""
    rader = [rad for rad in _rader_fs(text)]
    icke_tomma = [rad for rad in rader if rad.strip()]
    paragrafer: dict[str, list[str]] = {}
    kapitel, aktuell, senast = None, None, None
    for index, rad in enumerate(icke_tomma):
        nasta = icke_tomma[index + 1] if index + 1 < len(icke_tomma) else ""
        if rad.strip().startswith("1. Dessa föreskrifter träder i kraft"):
            break
        kap = _KAPITEL.match(rad)
        if kap:
            kapitel, aktuell, senast = kap.group(1), None, None
            continue
        if _ALLMANNA_RAD.match(rad):
            aktuell = None
            continue
        par = _PARAGRAF.match(rad)
        if par and kapitel and _nasta_i_ordning(senast, par.group(1)):
            aktuell, senast = f"{kapitel} {par.group(1)} §", par.group(1)
            paragrafer[aktuell] = [rad[par.end():]]
            continue
        if aktuell is None or _ar_rubrik(rad, nasta):
            continue
        paragrafer[aktuell].append(rad)
    return {lagrum: _foga(delar) for lagrum, delar in paragrafer.items()}


def _nasta_i_ordning(senast: str | None, nummer: str) -> bool:
    """En ny paragraf har nästa nummer i kapitlet, eller samma nummer med bokstav (8 a §).

    Det skiljer en paragraf från en hänvisning som råkar börja en rad, till exempel "3 § dessa föreskrifter".
    """
    siffra, _, bokstav = nummer.partition(" ")
    if senast is None:
        return siffra == "1"
    forra = senast.split(" ")[0]
    return int(siffra) == int(forra) + 1 or (int(siffra) == int(forra) and bool(bokstav))


def _foga(rader: list[str]) -> str:
    """Fogar rader till stycken. Avstavning vid radslut tas bort; ett nytt stycke börjar med indrag eller tankstreck."""
    stycken: list[str] = []
    for rad in rader:
        s = rad.strip()
        foregaende = stycken[-1] if stycken else ""
        if re.search(r"[a-zåäö]-$", foregaende):
            stycken[-1] = foregaende[:-1] + s
        elif re.search(r"[A-ZÅÄÖ]-$", foregaende) or (foregaende.endswith("–") and s[:1].isdigit()):
            stycken[-1] = foregaende + s
        elif not stycken or s.startswith("–") or (rad.startswith("   ") and foregaende.endswith((".", ":", ";"))):
            stycken.append(s)
        else:
            stycken[-1] = foregaende + " " + s
    return "\n".join(stycken) + "\n"


_SFS_KAPITEL = re.compile(r"^(\d+ (?:a )?kap\.)\s+[A-ZÅÄÖ]")
_SFS_PARAGRAF = re.compile(r"^(\d+(?: [a-z])?) §(?:\s+/(Upphör att gälla|Träder i kraft) ([UI]:\d{4}-\d{2}-\d{2})/)?(?:\s+|$)")
_ANDRINGSNOT = re.compile(r"\s*((?:Lag|Förordning) \(\d{4}:\d+\)\.)\s*$")


def _sfs_rubrik(rader: list[str], index: int) -> bool:
    """En rubrik saknar slutpunkt och följs, eventuellt via fler rubriker, av en ny paragraf eller ett nytt kapitel."""
    if not rader[index].strip()[:1].isupper():
        return False
    for rad in rader[index : index + 4]:
        s = rad.strip()
        if _SFS_PARAGRAF.match(s) or _SFS_KAPITEL.match(s):
            return rad is not rader[index]
        if not s or s.endswith((".", ",", ";", ":")) or len(s) > 95:
            return False
    return False


def paragrafer_sfs(text: str) -> dict[str, dict[str, str]]:
    """Paragrafer ur en SFS-text från rkrattsbaser: {"3 kap. 1 §": {"text": ..., "inford_genom": ...}}.

    En paragraf med två lydelser får nycklarna "1 kap. 2 § [U:2026-11-20]" och "1 kap. 2 § [I:2026-11-20]".
    """
    rader = [rad.rstrip() for rad in text.split("\n")]
    rader = [rad for rad in rader if rad.strip()]
    med_kapitel = any(_SFS_KAPITEL.match(rad.strip()) for rad in rader)
    forsta = (lambda s: _SFS_KAPITEL.match(s)) if med_kapitel else (lambda s: s.startswith("1 § "))
    start = next(i for i, rad in enumerate(rader) if forsta(rad.strip()))
    paragrafer: dict[str, list[str]] = {}
    kapitel, aktuell, senast = (None if med_kapitel else ""), None, None
    for index in range(start, len(rader)):
        s = rader[index].strip()
        if s.startswith("Övergångsbestämmelser"):
            break
        kap = _SFS_KAPITEL.match(s)
        if kap:
            kapitel, aktuell, senast = kap.group(1), None, None
            continue
        par = _SFS_PARAGRAF.match(s)
        if par and kapitel is not None and (
            _nasta_i_ordning(senast, par.group(1)) or (par.group(3) and par.group(1) == senast)
        ):
            senast = par.group(1)
            aktuell = f"{kapitel} {par.group(1)} §".strip() + (f" [{par.group(3)}]" if par.group(3) else "")
            paragrafer[aktuell] = [s[par.end():]]
            continue
        if aktuell is None or _sfs_rubrik(rader, index):
            continue
        paragrafer[aktuell].append(s)
    resultat = {}
    for lagrum, delar in paragrafer.items():
        text_ = " ".join(" ".join(delar).split())
        not_ = _ANDRINGSNOT.search(text_)
        resultat[lagrum] = {
            "text": (text_[: not_.start()] if not_ else text_) + "\n",
            "inford_genom": not_.group(1).rstrip(".") if not_ else "",
        }
    return resultat


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slag", choices=("fs", "sfs"), help="Källformat: fs eller sfs")
    parser.add_argument("fil", type=Path, help="Källtext i UTF-8")
    parser.add_argument("lagrum", nargs="+", help="Paragraf, inklusive eventuell datumlydelse")
    args = parser.parse_args(argv)
    try:
        text = args.fil.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Kan inte läsa källfilen: {exc}. Kontrollera sökväg och UTF-8-kodning.", file=sys.stderr)
        return 1
    try:
        alla = (
            paragrafer_fs(text) if args.slag == "fs"
            else {namn: post["text"] for namn, post in paragrafer_sfs(text).items()}
        )
    except StopIteration:
        print("Inga paragrafer hittades. Kontrollera källformatet och den extraherade texten.", file=sys.stderr)
        return 1
    saknas = False
    for namn in args.lagrum:
        if namn in alla:
            print(namn, kontrollsumma(alla[namn]))
        else:
            print(namn, "SAKNAS")
            saknas = True
    return 1 if saknas else 0


if __name__ == "__main__":
    sys.exit(main())
