"""Avgränsat granskningsunderlag för katalogluckor, aldrig en komplett riskrapport."""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from riskanalys.dokument.modeller import Dokument,Avsnitt
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.profil.omfattning import kompatibilitetsvy

FILNAMN='omfattningsunderlag-OFULLSTANDIGT.docx'
ID='OMFATTNING-OFULLSTANDIGT'
BEGRANSNING=('Känd produktbegränsning: tjänster utanför katalogen kan ännu inte få en fullständig tjänsteanalys i programmet. '
    'Manuell bedömning – ej motorberäknad är ett planerat framtida spår med hot, sårbarheter, motiverad PT/TF-nivå, spårbarhet och sakgranskning. '
    'Det är inte ett lagkrav att använda programmets motor. Detta underlag är ofullständigt och kan inte fastställas som en komplett allmän riskbedömning.')

@dataclass(frozen=True)
class Omfattningsutkast:
    status: Literal['ofullstandigt']
    dokument: Dokument
    hinder: tuple[str,...]


def bygg_omfattningsutkast(rb,profil):
    from riskanalys.dokument.gemensam_provning_v8 import originalstycke
    p=kompatibilitetsvy(profil,rb)
    hinder=['Ofullständigt omfattningsunderlag; fullständig tjänsteanalys, riskbedömning och sakgranskning återstår.']
    stycken=[lokaltext('OFULLSTÄNDIGT – enbart omfattning och bekräftat faktaunderlag. Inga risknivåer är beräknade i denna leverans.'),lokaltext(BEGRANSNING)]
    ref='P-BESK.ovriga_forhallanden';u=p.uppgifter.get(ref)
    besked='ja' if p.ar_bekraftad(ref) and u.varde is True else 'nej' if p.ar_bekraftad(ref) and u.varde is False else 'okänt'
    stycken.append(lokaltext('Andra tjänster eller riskförhållanden utanför katalogens stöd: '+besked+'.',(ref,)))
    ref='P-BESK.ovrigt';u=p.uppgifter.get(ref)
    if p.ar_bekraftad(ref) and isinstance(u.varde,str) and u.varde:
        stycken.append(originalstycke('Byråns exakta beskrivning av det som saknar modellstöd:',(('',u.varde),('Källa: ',u.kalla or 'Saknas')),(ref,)))
    elif besked!='nej':hinder.append('Bekräfta och beskriv vilka ytterligare tjänster eller riskförhållanden som saknar stöd.')
    for t in rb.tjanster.values():
        erbjuds=p.uppgifter.get(t.erbjuds_falt)
        status='erbjuds' if p.ar_bekraftad(t.erbjuds_falt) and erbjuds.varde is True else 'erbjuds inte' if p.ar_bekraftad(t.erbjuds_falt) and erbjuds.varde is False else 'okänt'
        stycken.append(lokaltext(t.namn+': '+status+'.',(t.id,t.erbjuds_falt)))
        if status!='erbjuds':continue
        slug=t.erbjuds_falt.removesuffix('_erbjuds')
        for id,u in p.uppgifter.items():
            if not id.startswith(slug+'_') or id==t.erbjuds_falt or not p.ar_bekraftad(id) or id not in rb.falt or rb.falt[id].personuppgift:continue
            # Faktaredovisning, inga motor-/risknivåer eller automatiska slutsatser.
            from riskanalys.profil.hantering import visa_varde
            varde=visa_varde(rb.falt[id],u.varde) if u.varde is not None else 'Okänt'
            period=f' Period: {u.period.fran}–{u.period.till}.' if u.period else ''
            stycken.append(lokaltext(f'Bekräftat {u.datum or "datum saknas"}; ansvarig: {u.bekraftad_av or "saknas"}.'+period,(id,)))
            stycken.append(originalstycke(rb.falt[id].fraga+' ',(('',varde),(' Källa: ',u.kalla or 'Saknas')),(id,)))
    dokument=Dokument(id=ID,titel='Omfattningsunderlag OFULLSTÄNDIGT',avsnitt=(Avsnitt(id='OMFATTNING.1',rubrik='Omfattning och kända tjänster',kalla='lokal',stycken=tuple(stycken),formatversion='D-ARB-tjanst-v8',leveransdel='lasrapport',visningsnummer='1'),))
    return Omfattningsutkast('ofullstandigt',dokument,tuple(hinder))


def exportera_omfattningsutkast(mapp:Path,rb,*,forvantad_revision=None)->Path:
    import os,shutil,tempfile
    from riskanalys.analys.lagring import analyslas
    from riskanalys.profil.lagring import las_profil,profilrevision
    from riskanalys.profil.text import kontrollera_profiltext
    from riskanalys.dokument.rendering import rendera_docx
    from riskanalys.lagring.korningar import ny_korningsmapp
    from riskanalys.lagring.manifest import skriv_manifest
    with analyslas(mapp):
        profil=las_profil(mapp)
        if forvantad_revision is not None and profilrevision(profil)!=forvantad_revision:
            from riskanalys.fel import RiskanalysFel
            raise RiskanalysFel('Profilen har ändrats. Läs om omfattningsunderlaget före export.')
        kontrollera_profiltext(profil)
        utkast=bygg_omfattningsutkast(rb,profil)
        arbetsmapp=Path(tempfile.mkdtemp(prefix='.omfattningsarbete-',dir=mapp))
        try:
            fil=arbetsmapp/FILNAMN
            rendera_docx(utkast.dokument,profil,'OFULLSTÄNDIGT – får inte fastställas',fil)
            skriv_manifest(arbetsmapp,{'typ':'ofullstandig_omfattning','profil':profilrevision(profil),'regelbas':rb.kontrollsumma,'status':'ofullstandigt'})
            klar=ny_korningsmapp(mapp,'omfattningsunderlag')
            os.replace(arbetsmapp,klar)
            return klar/FILNAMN
        finally:
            if arbetsmapp.exists():shutil.rmtree(arbetsmapp)


def las_omfattningsunderlag(mapp,rb,fil):
    from riskanalys.analys.lagring import analyslas,_mapphandtag,_lasfil
    from riskanalys.profil.lagring import las_profil,profilrevision
    from riskanalys.lagring.manifest import verifiera_manifest,las_manifest
    from riskanalys.fel import RiskanalysFel
    with analyslas(mapp):
        if fil.name!=FILNAMN or fil.parent.parent!=mapp/'omfattningsunderlag' or verifiera_manifest(fil.parent):
            raise RiskanalysFel('Omfattningsunderlaget är ändrat eller felaktigt. Skapa det på nytt.')
        meta=las_manifest(fil.parent).metadata
        if meta.get('typ')!='ofullstandig_omfattning' or meta.get('regelbas')!=rb.kontrollsumma or meta.get('profil')!=profilrevision(las_profil(mapp)):
            raise RiskanalysFel('Omfattningsunderlaget bygger på äldre fakta. Skapa det på nytt.')
        with _mapphandtag(fil.parent) as fd:return _lasfil(fd,fil.name)
