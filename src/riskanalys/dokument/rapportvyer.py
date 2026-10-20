"""Rena, disjunkta projektioner av det fullständiga V8-dokumentet."""
from dataclasses import dataclass

from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.skrivversion import V8

LASRAPPORT = 'Läsrapport'
UNDERLAG = 'Kompletterande underlagsbilaga'
STRUKTURVERSION = 'D-ARB-v8-tva-delar-1'


@dataclass(frozen=True)
class Rapportvyer:
    lasrapport: Dokument
    underlagsbilaga: Dokument


def bygg_rapportvyer(dokument: Dokument) -> Rapportvyer:
    """Ingen text författas här. Avsnitt och deras innehållssummor är oförändrade."""
    if dokument.formatversion != V8:
        raise ValueError('Rapportvyer kräver ett kanoniskt V8-dokument.')
    if len({a.id for a in dokument.avsnitt}) != len(dokument.avsnitt):
        raise ValueError('V8-avsnittens ID måste vara unika; ID-kollision.')
    if any(a.leveransdel not in ('lasrapport', 'underlagsbilaga') for a in dokument.avsnitt):
        raise ValueError('Varje avsnitt måste ha exakt en leveransdel.')
    b1 = dokument.avsnitt_med_id().get('D-ARB.B1')
    if b1 is None or b1.leveransdel != 'underlagsbilaga':
        raise ValueError('Det kanoniska dokumentet måste ha B1 i underlagsbilagan.')
    if not any(a.leveransdel == 'lasrapport' for a in dokument.avsnitt):
        raise ValueError('Det kanoniska dokumentet måste också innehålla läsrapporten.')
    def vy(del_, titel):
        return Dokument(id=dokument.id, titel=dokument.titel + ' – ' + titel,
                        avsnitt=tuple(a for a in dokument.avsnitt if a.leveransdel == del_))
    return Rapportvyer(vy('lasrapport', LASRAPPORT), vy('underlagsbilaga', UNDERLAG))


def vystruktur(dokument: Dokument) -> dict:
    vyer = bygg_rapportvyer(dokument)
    return {'version': STRUKTURVERSION, 'delar': [
        {'titel': d.titel, 'format': d.formatversion, 'avsnitt': [a.id for a in d.avsnitt]}
        for d in (vyer.lasrapport, vyer.underlagsbilaga)]}
