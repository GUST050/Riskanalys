"""Tre disjunkta V10-vyer; sammanfattningens källöverlappp är explicit spårad."""
from dataclasses import dataclass
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.rapportversion import V10


@dataclass(frozen=True)
class RapportvyerV10:
    resultatrapport: Dokument
    analysbilaga: Dokument
    underlagsbilaga: Dokument


def bygg_rapportvyer_v10(dokument: Dokument) -> RapportvyerV10:
    if dokument.formatversion != V10:
        raise ValueError('Tre vyer kräver ett fullständigt V10-dokument.')
    ids=[a.id for a in dokument.avsnitt]
    if len(ids)!=len(set(ids)):
        raise ValueError('V10-avsnittens ID måste vara unika.')
    delar=('resultatrapport','analysbilaga','underlagsbilaga')
    if any(a.leveransdel not in delar for a in dokument.avsnitt):
        raise ValueError('V10 kräver en giltig leveransdel för varje avsnitt.')
    if any(not any(a.leveransdel==del_ for a in dokument.avsnitt) for del_ in delar):
        raise ValueError('Det kanoniska V10-dokumentet kräver alla tre delar.')
    if dokument.avsnitt_med_id().get('D-ARB.B1') is None or dokument.avsnitt_med_id()['D-ARB.B1'].leveransdel!='underlagsbilaga':
        raise ValueError('Det kanoniska V10-dokumentet kräver B1 i underlagsbilagan.')
    namn=('Resultatrapport','Bilaga A Analys','Bilaga B1 Underlag')
    return RapportvyerV10(*(Dokument(id=dokument.id,titel=dokument.titel+' '+titel,
        avsnitt=tuple(a for a in dokument.avsnitt if a.leveransdel==del_)) for del_,titel in zip(delar,namn,strict=True)))


def vystruktur_v10(dokument):
    v=bygg_rapportvyer_v10(dokument)
    return {'version':'D-ARB-v10-tre-delar-1','delar':[
        {'titel':d.titel,'format':d.formatversion,'avsnitt':[a.id for a in d.avsnitt]}
        for d in (v.resultatrapport,v.analysbilaga,v.underlagsbilaga)]}
