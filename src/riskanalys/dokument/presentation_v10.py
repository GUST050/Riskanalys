"""Fryst presentation efter slutlig fyndlista; inga nya fakta eller riskbeslut."""
from types import SimpleNamespace
from typing import Literal
from pydantic import BaseModel,ConfigDict,model_serializer
from riskanalys.analys.modeller import Rutinatgard,Analyspaket
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.leverans_v10 import LeveransmallV10,DELAR
from riskanalys.dokument.resultatmodell_v9 import ResultatunderlagV9,TransformationV9,summa
from riskanalys.dokument.resultatmodell_v10 import ResultatbyggeV10,KonstruktionV10
from riskanalys.dokument.presentation_v8 import (
    Presentationsrad,presentationsrader,fulla_atgarder,fyndlista,
)
from riskanalys.granskning.modeller import Fynd
from riskanalys.fel import RiskanalysFel
from riskanalys.dokument.resultatmodell_v10 import RedaktionV10

PRESENTATIONSVERSION='D-ARB-v10-presentation-1'
RENDERINGSPOLICY='V10-lokala-original-1'


class Fryst(BaseModel):
    model_config=ConfigDict(frozen=True,extra='forbid')


class AtgardsmedlemV10(Fryst):
    pointer: str
    tjanst: str
    post: Rutinatgard


class ListdelV10(Fryst):
    leveransdel: Literal['resultatrapport','underlagsbilaga']
    placering: Literal['slut:fynd','slut:rutinatgarder']
    rader: tuple[Presentationsrad,...]


class HanvisningV10(Fryst):
    avsnitt: str
    maldel: Literal['resultatrapport','analysbilaga','underlagsbilaga']
    mal: tuple[str,...]


class VyV10(Fryst):
    titel: str
    format: Literal['D-ARB-resultat-v10']
    avsnitt: tuple[str,...]


class VystrukturV10(Fryst):
    version: Literal['D-ARB-v10-tre-delar-1']='D-ARB-v10-tre-delar-1'
    delar: tuple[VyV10,VyV10,VyV10]


class PresentationV10(Fryst):
    version: str
    renderingspolicy: str
    leveransmall: LeveransmallV10
    bygge: str
    dokument: str
    profil: str
    analys: str
    bedomning: str
    fynd: str
    underlag: ResultatunderlagV9
    transformationer: tuple[TransformationV9,...]
    konstruktioner: tuple[KonstruktionV10,...]
    konstruktioner_summa: str
    vysummor: tuple[str,str,str]
    vystruktur: VystrukturV10
    literala: tuple[str,...]
    renderade: tuple[Dokument,Dokument,Dokument]
    hanvisningar: tuple[HanvisningV10,...]
    atgardskalla: tuple[AtgardsmedlemV10,...]
    fyndkalla: tuple[Fynd,...]
    delar: tuple[ListdelV10,...]
    redaktion: RedaktionV10 | None = None

    @model_serializer(mode='wrap')
    def serialisera(self,handler):
        data=handler(self)
        if self.redaktion is None:data.pop('redaktion',None)
        return data


def renderade_vyer(vyer,profil):
    from riskanalys.dokument.rendering import renderat_avsnitt
    return tuple(getattr(vyer,del_).model_copy(update={'avsnitt':tuple(
        renderat_avsnitt(a,profil) for a in getattr(vyer,del_).avsnitt)}) for del_ in DELAR)


def fyndindex_v10(word,fynd):
    from collections import Counter
    from riskanalys.granskning.fyndgrupper import gruppera_fynd
    word.add_heading('Maskinell granskning',level=1)
    grupper=gruppera_fynd(fynd)
    word.add_paragraph(f'{len(fynd)} maskinfynd, åtskilda från de lokala analysluckorna i 5.1. '
        f'Alla ID, originaltexter, åtgärder och hänvisningar finns i underlagsbilagans fullständiga fyndkälla, '
        f'fyndgrupp 1–{len(grupper)}. Gruppering ändrar inga beslut eller fastställelsespärrar.')
    for (allvar,status),antal in Counter((f.allvar,f.status) for f in fynd).items():
        forklaring=' Blockerande fynd hindrar fastställelse.' if allvar=='blockerande' else ''
        word.add_paragraph(f'{antal} fynd: allvar {allvar}; status {status}.'+forklaring)


def listdelar(atgarder,fynd):
    """Återanvänd rena, befintliga fulltextbyggare mot enbart de frysta posterna."""
    delar=[];tjanster={}
    for a in atgarder:tjanster.setdefault(a.tjanst,[]).append(a.post)
    if atgarder:
        analys=SimpleNamespace(tjanster=tuple(SimpleNamespace(tjanst=t,rutinatgarder=tuple(p)) for t,p in tjanster.items()))
        delar.append(ListdelV10(leveransdel='underlagsbilaga',placering='slut:rutinatgarder',rader=presentationsrader(fulla_atgarder,analys)))
    if fynd:
        for del_,full in (('resultatrapport',False),('underlagsbilaga',True)):
            delar.append(ListdelV10(leveransdel=del_,placering='slut:fynd',rader=presentationsrader(fyndlista,fynd,full=True) if full else presentationsrader(fyndindex_v10,fynd)))
    return tuple(delar)


def vystruktur(docs):
    return VystrukturV10(delar=tuple(VyV10(titel=d.titel,format=d.formatversion,
        avsnitt=tuple(a.id for a in d.avsnitt)) for d in docs))


def hanvisningar_for(docs):
    mal={a.id:a.leveransdel for doc in docs for a in doc.avsnitt}
    hanvisningar=[]
    for a in (a for doc in docs for a in doc.avsnitt):
        refs=tuple(dict.fromkeys(r for s in a.stycken for r in s.referenser))
        refs=tuple(dict.fromkeys((*refs,*(r for t in a.tabeller for row in t.rader for c in row.celler for r in c.referenser))))
        for d in DELAR:
            andra=tuple(r for r in refs if mal.get(r)==d and d!=a.leveransdel)
            if andra:hanvisningar.append(HanvisningV10(avsnitt=a.id,maldel=d,mal=andra))
    return tuple(hanvisningar)


def _bygg_presentation_1(bygge:ResultatbyggeV10,*,analys:Analyspaket|None,
                         fynd:tuple[Fynd,...],bedomning:Bedomning,profil:Profil) -> PresentationV10:
    from riskanalys.dokument import leverans_v10
    from riskanalys.dokument.rapportvyer_v10 import bygg_rapportvyer_v10
    from riskanalys.dokument.rendering import bokstavliga_positioner
    kallor=dict(bygge.underlag.kallsummor)
    if any(summa(v.model_dump(mode='json') if v is not None else None)!=kallor.get(n)
           for n,v in (('analys',analys),('profil',profil),('bedomning',bedomning),('analysdokument',bygge.analysdokument))):
        raise RiskanalysFel('Presentationskällan avviker från byggunderlaget. Bygg och granska alla tre delarna på nytt.')
    vyer=bygg_rapportvyer_v10(bygge.dokument)
    docs=tuple(getattr(vyer,d) for d in DELAR)
    atgarder=tuple(AtgardsmedlemV10(pointer=f'/tjanster/{i}/rutinatgarder/{j}',tjanst=a.tjanst,post=p)
        for i,a in enumerate(analys.tjanster) for j,p in enumerate(a.rutinatgarder)) if analys else ()
    fynd=tuple(fynd)
    return PresentationV10(version=PRESENTATIONSVERSION,renderingspolicy=RENDERINGSPOLICY,
        leveransmall=leverans_v10.LEVERANSMALL_V10,bygge=summa(bygge.model_dump(mode='json')),
        dokument=summa(bygge.dokument.model_dump(mode='json')),profil=summa(profil.model_dump(mode='json')),
        analys=summa(analys.model_dump(mode='json') if analys else None),
        bedomning=summa(bedomning.model_dump(mode='json')),fynd=summa([f.model_dump(mode='json') for f in fynd]),
        underlag=bygge.underlag,transformationer=bygge.transformationer,konstruktioner=bygge.konstruktioner,
        konstruktioner_summa=summa([k.model_dump(mode='json') for k in bygge.konstruktioner]),
        vysummor=tuple(summa(d.model_dump(mode='json')) for d in docs),vystruktur=vystruktur(docs),
        literala=tuple(p for d in docs for a in d.avsnitt for p in bokstavliga_positioner(a)),
        renderade=renderade_vyer(vyer,profil),hanvisningar=hanvisningar_for(docs),
        atgardskalla=atgarder,fyndkalla=fynd,delar=listdelar(atgarder,fynd))


def bygg_presentation_v10(bygge,*,analys,fynd,bedomning,profil,regelbas=None,presentationsversion=PRESENTATIONSVERSION):
    from riskanalys.dokument.redaktionspresentation_v10 import VERSION,skapa
    if presentationsversion not in (PRESENTATIONSVERSION,VERSION):
        raise RiskanalysFel('Okänd V10-presentation. Välj ett känt format och granska alla tre delarna.')
    p=_bygg_presentation_1(bygge,analys=analys,fynd=fynd,bedomning=bedomning,profil=profil)
    if presentationsversion==PRESENTATIONSVERSION:return p
    if regelbas is None:raise RiskanalysFel('Den redaktionella presentationen kräver sin frysta regelbas.')
    return skapa(p,regelbas,analys,bedomning,profil)
