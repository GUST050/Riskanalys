"""Intagsreferenser valideras utan att likställa frågetäckning med uppfyllda krav."""
from riskanalys.regelverk.modeller import Regelbas


def intagskontraktsfel(rb: Regelbas) -> list[str]:
    if tuple(map(int, rb.version.split('.'))) < (1, 1, 0) and not any(f.intag for f in rb.falt.values()):
        return []  # äldre regelbaser
    fel = []
    for f in rb.falt.values():
        if f.alias_for or f.basfalt:
            continue
        if not f.intag:
            fel.append(f'{f.id}: intagskoppling saknas.')
            continue
        for refs, register in ((f.intag.krav, rb.krav), (f.intag.kallor, rb.kallor),
                               (f.intag.avsnitt, rb.maldefinitioner), (f.intag.beroenden, rb.falt)):
            for ref in refs:
                if ref not in register:
                    fel.append(f'{f.id}: okänd intagsreferens {ref}.')
    def cykel(id, stig):
        if id in stig:
            return True
        f = rb.falt.get(id)
        return bool(f and f.intag and any(cykel(ref, stig | {id}) for ref in f.intag.beroenden))
    for f in rb.falt.values():
        if cykel(f.id, set()):
            fel.append(f'{f.id}: cykliska intagsberoenden.')
    kopplade = {k for f in rb.falt.values() if f.intag for k in f.intag.krav}
    for k in rb.krav.values():
        if any(m.id.startswith('D-ARB.') for m in k.mal) and k.id not in kopplade:
            fel.append(f'{k.id}: frågekoppling saknas för riskbedömningen.')
    return fel
