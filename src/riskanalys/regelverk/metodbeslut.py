"""Ingen beslutsattest får skiljas från sitt faktiska genomförande."""
from pathlib import Path
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.regelverk.modeller import _summa, utan_granskningsmetadata

KODROT=Path(__file__).resolve().parents[3]


def objektindex(rb):
    """Endast sakobjekt; besluten själva får inte skapa cirkulära summor."""
    samlingar=('falt','kallor','lydelser','krav','hot','sarbarheter','kontroller','tjanster','lagre_risk')
    index={id:post for namn in samlingar for id,post in getattr(rb,namn).items()}
    index.update({r.id:r for k in rb.kontroller.values() for r in k.rackvidd})
    index.update({r.id:r for r in (*rb.metod.regler(),*rb.metod.riskmatris)})
    return {id:_summa(utan_granskningsmetadata(post.model_dump(mode='json'))) for id,post in index.items()}


def obligatoriska_filer():
    from riskanalys.drift.modellidentitet import MODELLFILER
    return tuple(sorted(set(MODELLFILER)|{
        'src/riskanalys/drift/modellidentitet.py',
        'src/riskanalys/regelverk/metodbeslut.py',
        'src/riskanalys/regelverk/laddning.py',
        'src/riskanalys/regelverk/sakkunnig.py',
        'src/riskanalys/regelverk/validering.py',
        'src/riskanalys/regelverk/validering_m2.py',
    }))


def aktuella_filer(beslut):
    resultat={}
    for fil in beslut.modellfiler:
        try:resultat[fil]=for_fil(KODROT/fil)
        except OSError:resultat[fil]='saknas'
    return resultat


def beslutssumma(rb,beslut,*,index=None):
    index=objektindex(rb) if index is None else index
    return _summa({'beslut':utan_granskningsmetadata(beslut.model_dump(mode='json')),
        'aktuella_objekt':{id:index.get(id,'saknas') for id in beslut.objekt},
        'aktuella_modellfiler':aktuella_filer(beslut)})


def beslutsfel(rb):
    fel=[];index=objektindex(rb)
    for id,b in rb.metodbeslut.items():
        if set(obligatoriska_filer())-set(b.modellfiler):
            fel.append(f'{id}: genomförandebindningen saknar obligatoriska modell-/attestfiler.')
        if id!=b.id:fel.append(f'{id}: beslutets nyckel och ID avviker.')
        for ref,summa in b.objekt.items():
            if index.get(ref)!=summa:fel.append(f'{id}: bundet objekt {ref} saknas eller har ändrats. Ompröva och bind beslutet på nytt.')
        for fil,summa in aktuella_filer(b).items():
            if b.modellfiler[fil]!=summa:fel.append(f'{id}: modellfil {fil} saknas eller har ändrats. Ompröva och bind beslutet på nytt.')
        for ref in b.kallor:
            if ref not in rb.kallor:fel.append(f'{id}: källan {ref} saknas.')
        if b.sakkunnig.status=='verifierad' and (not b.sakkunnig.av or not b.sakkunnig.datum or not b.sakkunnig.galler(beslutssumma(rb,b,index=index))):
            fel.append(f'{id}: aktuell sakkunnigattest för beslutets hela genomförande saknas.')
    return fel
