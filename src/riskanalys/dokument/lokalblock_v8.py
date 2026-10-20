"""Typade lokala byggoperationer; fråga och källfält bestäms före svensk formulering."""
from dataclasses import dataclass

from riskanalys.dokument.modeller import Textstycke
from riskanalys.dokument.lokaltext_v6 import bygg_lokaltext


@dataclass(frozen=True)
class Lokalblock:
    fraga: int
    falt: tuple[str, ...]
    stycke: Textstycke


def lokala_block(a, paket, rb, index, *, profil):
    """Återanvänd fulltextmallarna med explicit ordnings-/fältkontrakt, aldrig prefixklassning."""
    specifikation = []
    def lagg(fraga, *falt):
        specifikation.append((fraga, tuple(falt)))
    lagg(0, 'exponering', 'exponeringsbelagg')
    lagg(0, 'delningsmotivering')
    for n,d in enumerate(a.delanalyser):
        lagg(0, *(f'delanalyser/{n}/{f}' for f in ('id','rubrik','arbetsmoment_och_befogenheter','belagg')))
    lagg(0, *(f'betalningsinsyn/{f}' for f in ('status','motivering','synliga_floden','insynsluckor',
        'avsandare_och_mottagare','underlagens_tillforlitlighet','belagg')))
    lagg(5, *(f'uppdragsprovning/{f}' for f in ('status','kompetens_och_insyn','motivering',
        'handlingsalternativ','beslutsstatus','ansvar','datum','belagg')))
    if a.leverantorsmotivering or a.leverantorer:
        lagg(4, 'leverantorsmotivering','leverantorer')
    for n,v in enumerate(a.leverantorer):
        lagg(4, *(f'leverantorer/{n}/{f}' for f in ('omfattning','leverantorens_kontroller',
            'egen_verifiering','brister_och_motstridigheter','ansvar','belagg')))
    for n,s in enumerate(a.sarbarhetsprovningar):
        lagg(2, *(f'sarbarhetsprovningar/{n}/{f}' for f in ('omrade','relevans','motivering','sarbarheter','scenarier','belagg')))
    lagg(2,'samverkan')
    lagg(2,'erfarenhetsprovning','erfarenhetsbelagg')
    lagg(2,'sektorsjamforelse')
    if a.sanktioner:
        lagg(2,'sanktioner')
    lagg(5,'slutsats')
    for n,g in enumerate(a.gap):
        lagg(5, *(f'gap/{n}/{f}' for f in ('typ','status','beskrivning','motivering','ansvar','tidsfrist','belagg')))
    stycken,_=bygg_lokaltext(a,paket,rb,index,profil=profil)
    if len(stycken)!=len(specifikation):
        raise ValueError('V8:s typade lokalblock behöver uppdateras efter ändrad lokaltextmall.')
    return tuple(Lokalblock(fraga,falt,s) for (fraga,falt),s in zip(specifikation,stycken,strict=True))
