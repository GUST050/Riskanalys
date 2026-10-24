"""En liten läsversion med identiska kopior ur ett verifierat expertunderlag."""
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_fil
from riskanalys.lagring.manifest import las_manifest,skriv_manifest,verifiera_manifest,MANIFESTNAMN

GEMENSAMMA=(
    'sakkunniggranskning.md','objektgenomgang.md','granskningsmall.yaml',
    'metod/sammanstallning.md','metod/beslut-och-beroenden.json','metod/fore-efter.json',
    *(f'referensrapporter/{c}/{d}.pdf' for c in ('fyra_tjanster','med_betalningsmandat')
      for d in ('allman-riskbedomning-UTKAST','analysbilaga-UTKAST','underlagsbilaga-UTKAST')),
)


def skapa_lasversion(full:Path,ut:Path)->Path:
    full,ut=Path(full),Path(ut)
    if ut.exists():raise RiskanalysFel('Läsversionens mapp finns redan. Välj en ny utmapp.')
    fel=verifiera_manifest(full)
    if fel:raise RiskanalysFel('Det fullständiga sakkunnigpaketet är ändrat: '+'; '.join(fel))
    manifest=las_manifest(full);bindning=for_fil(full/MANIFESTNAMN)
    if manifest.metadata.get('typ')!='sakkunnigunderlag':
        raise RiskanalysFel('Välj ett fullständigt sakkunnigunderlag som teknisk grund.')
    if any(n not in manifest.filer or not (full/n).is_file() or (full/n).is_symlink() for n in GEMENSAMMA):
        raise RiskanalysFel('Läsversionen kräver guide, objekt, metod, mall och båda referensfallen med tre PDF-delar.')
    ut.parent.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(prefix='.lasversion-',dir=ut.parent) as tmp:
        arbetsmapp=Path(tmp)/'paket';arbetsmapp.mkdir()
        for n in GEMENSAMMA:
            dest=arbetsmapp/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(full/n,dest)
            if for_fil(dest)!=manifest.filer[n]:raise RiskanalysFel('En gemensam fil ändrades under kopieringen: '+n)
        (arbetsmapp/'LAS-MIG.md').write_text(
            '# Börja här\n\nLäs sakkunniggranskning.md, objektgenomgang.md och metod/sammanstallning.md, '
            'därefter referensrapporterna. Beslut lämnas i den obesvarade granskningsmallen.\n\n'
            'Den fullständiga versionen är den tekniska grunden. Läsversionen innehåller byteidentiska '
            'kopior av de gemensamma filerna; den ersätter inte den fullständiga regelbasen, '
            'källoriginalen, historiska beräkningsfilerna eller genomförandekoden. '
            'Teknisk validering är inte sakkunniggodkännande. Fullpaketets manifestbindning står i lasversion.json.\n',encoding='utf-8')
        data={'fullstandigt_paket':full.name,'fullstandigt_manifest':bindning,
            'gemensamma':{n:manifest.filer[n] for n in GEMENSAMMA},'antal_filer':15,'storlek_byte':0}
        for _ in range(8):
            (arbetsmapp/'lasversion.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            skriv_manifest(arbetsmapp,{'typ':'sakkunnig-lasversion','fullstandigt_manifest':bindning})
            storlek=sum(p.stat().st_size for p in arbetsmapp.rglob('*') if p.is_file())
            if storlek==data['storlek_byte']:break
            data['storlek_byte']=storlek
        else:raise RiskanalysFel('Läsversionens storlekskontroll kunde inte avslutas.')
        if (for_fil(full/MANIFESTNAMN)!=bindning or verifiera_manifest(full) or verifiera_manifest(arbetsmapp)):
            raise RiskanalysFel('Sakkunnigunderlaget ändrades under bygget. Bygg läsversionen på nytt.')
        arbetsmapp.rename(ut)
    return ut
