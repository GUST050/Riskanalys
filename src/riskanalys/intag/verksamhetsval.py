"""Fasta fakta om uppdragets faktiska mandat, aldrig härledda ur fritext."""
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas, Tjanst

VERKSAMHETSVAL = {
    'attest': {'kund': 'kunden', 'byra': 'byrån', 'bada': 'både kunden och byrån', 'okant': 'okänt'},
    'betalningsmandat': {'inget': 'inget', 'forbereder': 'förbereder betalningar',
                       'verkstaller': 'verkställer betalningar', 'okant': 'okänt'},
    'bankinsyn': {'full': 'full', 'delvis': 'delvis', 'ingen': 'ingen', 'okant': 'okänt'},
}


def verksamhetsval(rb: Regelbas, falt_id: str) -> tuple[Tjanst, str] | None:
    for tjanst in rb.tjanster.values():
        prefix = tjanst.erbjuds_falt.removesuffix('_erbjuds')
        for namn in VERKSAMHETSVAL:
            if falt_id == f'{prefix}_{namn}':
                return tjanst, namn
    return None


def erbjuds_aktuellt(profil: Profil, tjanst: Tjanst) -> bool:
    return profil.ar_bekraftad(tjanst.erbjuds_falt) and profil.uppgifter[tjanst.erbjuds_falt].varde is True
