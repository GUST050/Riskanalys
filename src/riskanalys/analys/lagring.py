"""Privat analysregister: CAS, atomiska kopior och gemensam låsordning."""
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
import fcntl
import os
import stat
import secrets

from pydantic import ValidationError
import yaml

from riskanalys.analys.modeller import Analyspaket, Analysbindning, Analysbeslut
from riskanalys.drift.modellrisk import Modellbelagg
from riskanalys.analys.provning import (analysbrister, registersumma, registrera_beslut,
                                      summa, svarssumma, underlagssumma)
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes, for_fil

ANALYSFIL = Path('analys/analys.yaml')


@contextmanager
def _mapphandtag(sokvag: Path, *, skapa: bool = False):
    """Behåll ett kontrollerat kataloghandtag; följ ingen förälder via sökvägssträng."""
    sokvag=sokvag.absolute()
    if '..' in sokvag.parts:
        raise RiskanalysFel('Den privata sökvägen får inte innehålla föräldrareferenser.')
    fd=os.open(sokvag.anchor,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for del_ in sokvag.parts[1:]:
            if skapa:
                try:os.mkdir(del_,mode=0o700,dir_fd=fd)
                except FileExistsError:pass
            ny=os.open(del_,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=ny
        yield fd
    finally:os.close(fd)


@contextmanager
def _privat_mapp(rot: Path, namn: str):
    with _mapphandtag(rot/namn,skapa=True) as fd:
        yield fd


def _lasfil(mappfd: int, namn: str) -> bytes:
    source=os.open(namn,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=mappfd)
    with os.fdopen(source,'rb') as fil:
        if not stat.S_ISREG(os.fstat(fil.fileno()).st_mode):
            raise RiskanalysFel('Välj en vanlig underlagsfil utan symlänkar.')
        return fil.read()


@contextmanager
def analyslas(byramapp: Path):
    """Håll profil → analys → drift genom aktualitetsprov och slutlig publicering.

    Använd *_last-helpers inne i kontexten; återta aldrig samma flock.
    """
    handtag=[]
    try:
        for namn in ('profil','analys','drift'):
            with _privat_mapp(byramapp,namn) as mappfd:
                fd=os.open('.skrivlas',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600,dir_fd=mappfd)
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                os.close(fd)
                raise RiskanalysFel('Det privata skrivlåset är inte en vanlig fil.')
            handtag.append(fd);fcntl.flock(fd,fcntl.LOCK_EX)
        yield
    except OSError as exc:
        raise RiskanalysFel('Analysens privata filer kunde inte låsas eller sparas. Kontrollera sökväg och behörighet.') from exc
    finally:
        for fd in reversed(handtag):os.close(fd)


def _las_regelratt(fil: Path) -> bytes:
    """Öppna en privat fil och alla dess mappar utan att följa symlänkar."""
    with _mapphandtag(fil.parent) as fd:
        return _lasfil(fd,fil.name)


def _las_vald_kalla(fil: Path) -> bytes:
    """Läs en fil som användaren själv valt utanför byråmappen.

    Mappar ovanför filen får vara symlänkar (t.ex. /tmp på macOS) och löses upp först.
    Själva filen öppnas utan att följa symlänk och måste vara en vanlig fil.
    """
    try:
        mapp=fil.parent.resolve(strict=True)
        with _mapphandtag(mapp) as fd:
            return _lasfil(fd,fil.name)
    except (OSError,RuntimeError) as exc:  # RuntimeError: symlänkslinga i Python 3.12
        raise RiskanalysFel('Den valda filen kunde inte läsas. Välj en befintlig vanlig fil; '
                            'själva filen får inte vara en symlänk.') from exc


def las_analys(byramapp: Path) -> Analyspaket | None:
    try:
        with _mapphandtag(byramapp/'analys') as fd:
            data=_lasfil(fd,'analys.yaml')
        return Analyspaket.model_validate(yaml.safe_load(data))
    except FileNotFoundError:
        return None
    except (OSError,ValueError,ValidationError,yaml.YAMLError) as exc:
        raise RiskanalysFel('Analysregistret kan inte läsas. Återställ den privata kopian eller rätta filen.') from exc


def _atomiskt(mappfd: int, namn: str, data: bytes) -> None:
    temp=None
    try:
        while True:
            kandidat='.'+secrets.token_hex(16)+'.tmp'
            try:
                fd=os.open(kandidat,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=mappfd)
                temp=kandidat
                break
            except FileExistsError:continue
        with os.fdopen(fd,'wb') as fil:
            fil.write(data);fil.flush();os.fsync(fil.fileno())
        os.replace(temp,namn,src_dir_fd=mappfd,dst_dir_fd=mappfd)
        temp=None
        os.fsync(mappfd)
    finally:
        if temp is not None:os.unlink(temp,dir_fd=mappfd)


def _spara_kopia(mappfd: int,namn: str,data: bytes) -> None:
    try:tidigare=_lasfil(mappfd,namn)
    except FileNotFoundError:_atomiskt(mappfd,namn,data)
    else:
        if tidigare!=data:
            raise RiskanalysFel('Den privata underlagskopian är ändrad. Återställ underlaget.')


def spara_analys_last(byramapp: Path,paket: Analyspaket,*,forvantad_summa: str) -> str:
    """CAS under redan hållet analyslas; import får aldrig föra in beslut."""
    gammalt=las_analys(byramapp)
    if (registersumma(gammalt) if gammalt else '')!=forvantad_summa:
        raise RiskanalysFel('Analysen har ändrats i en annan flik. Läs om sidan före nästa svar.')
    if gammalt is None:
        if paket.beslut:raise RiskanalysFel('Importerade svar får inte innehålla godkännanden eller beslut.')
        paket=paket.model_copy(update={'revision':1})
    else:
        if paket.beslut!=gammalt.beslut:
            raise RiskanalysFel('Beslut måste registreras separat efter granskning av aktuella svar.')
        andrat=svarssumma(paket)!=svarssumma(gammalt)
        paket=paket.model_copy(update={'revision':gammalt.revision+int(andrat)})
    _skriv_last(byramapp,paket,gammalt)
    return registersumma(paket)


def _skriv_last(byramapp,paket,gammalt):
    with _privat_mapp(byramapp,'analys') as mappfd:
        if gammalt is not None:
            data=_lasfil(mappfd,'analys.yaml')
            try:os.mkdir('historik',mode=0o700,dir_fd=mappfd)
            except FileExistsError:pass
            hfd=os.open('historik',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=mappfd)
            try:
                namn=for_bytes(data).split(':')[1]+'.yaml'
                try:
                    fd=os.open(namn,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=hfd)
                except FileExistsError:
                    if _lasfil(hfd,namn)!=data:
                        raise RiskanalysFel('Analysens historikkopia är ändrad. Återställ underlaget.')
                else:
                    with os.fdopen(fd,'wb') as fil:
                        fil.write(data);fil.flush();os.fsync(fil.fileno())
                    os.fsync(hfd)
            finally:os.close(hfd)
        _atomiskt(mappfd,'analys.yaml',yaml.safe_dump(paket.model_dump(mode='json'),allow_unicode=True,sort_keys=False).encode())


def spara_analys(byramapp: Path,paket: Analyspaket,*,forvantad_summa: str) -> str:
    with analyslas(byramapp):return spara_analys_last(byramapp,paket,forvantad_summa=forvantad_summa)


def importera_belagg(byramapp: Path,fil: Path) -> tuple[str,str]:
    try:
        data=_las_vald_kalla(fil)
        kontrollsumma=for_bytes(data)
        with analyslas(byramapp):
            with _privat_mapp(byramapp,'analys/belagg') as mappfd:
                namn=kontrollsumma.split(':')[1]+'.bin'
                _spara_kopia(mappfd,namn,data)
        return namn,kontrollsumma
    except OSError as exc:
        raise RiskanalysFel('Belägget kunde inte importeras. Välj en vanlig fil utan symlänkar.') from exc


def las_belaggsfil(byramapp: Path,fil: str,kontrollsumma: str) -> bytes:
    p=PurePosixPath(fil)
    if (p.is_absolute() or '\\' in fil or ':' in fil or any(x in ('','.','..') for x in fil.split('/'))
            or not fil):
        raise RiskanalysFel('Välj ett registrerat privat belägg under analys/belagg.')
    try:
        data=_las_regelratt(byramapp/'analys/belagg'/p)
        if for_bytes(data)!=kontrollsumma:raise RiskanalysFel('Belägget har ändrats. Importera och granska den aktuella kopian.')
        return data
    except OSError as exc:
        raise RiskanalysFel('Beläggskopian saknas eller har en otillåten sökväg. Importera den igen.') from exc


def bygg_bindning(byramapp: Path,rb,bedomningsmapp: Path,utkastmapp: Path) -> Analysbindning:
    from riskanalys.bedomning.korning import kontrollera_aktuell,las_bedomning
    from riskanalys.profil.lagring import las_profil,profilrevision
    from riskanalys.lagring.manifest import MANIFESTNAMN,las_manifest,verifiera_manifest
    from riskanalys.drift.historik import historikens_kontrollsumma
    from riskanalys.drift.modellrisk import modellbindning
    from riskanalys.dokument.skrivning import las_skrivresultat
    from riskanalys.dokument.delskrivning import Tjanstresultat,kontrollera_resultat
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    kontrollera_aktuell(byramapp,bedomningsmapp,rb)
    if verifiera_manifest(utkastmapp):raise RiskanalysFel('AI-utkastets manifest stämmer inte. Skriv om utkastet.')
    if las_manifest(utkastmapp).metadata.get('bedomning')!=bedomningsmapp.name:
        raise RiskanalysFel('AI-utkastet hör till en annan bedömning.')
    b=las_bedomning(bedomningsmapp);p=las_profil(byramapp)
    if b.byra!=p.byra.id:raise RiskanalysFel('Bedömningen hör till en annan byrå.')
    poster=las_skrivresultat(utkastmapp)
    expected=tuple(tjanster_med_avsnitt(b))
    if (any(not isinstance(r,Tjanstresultat) for r in poster) or len(poster)!=len(expected)
            or len({r.avsnitt for r in poster})!=len(poster)):
        raise RiskanalysFel('Skrivresultaten måste innehålla exakt en post per erbjuden tjänst.')
    resultat={r.avsnitt:r for r in poster}
    if set(resultat)!={id for id,_ in expected}:
        raise RiskanalysFel('Skrivresultatens avsnitt stämmer inte med bedömningen.')
    versioner={r.formatversion for r in poster}
    if len(versioner)!=1:
        raise RiskanalysFel('Skrivresultaten blandar olika skrivversioner. Skriv om utkastet.')
    metadata=las_manifest(utkastmapp).metadata
    if metadata.get('format') not in versioner:
        raise RiskanalysFel('Skrivmanifestets format stämmer inte med de sparade resultaten.')
    for id,t in expected:
        r=resultat.get(id)
        if not isinstance(r,Tjanstresultat):raise RiskanalysFel('Validerade skrivdelar saknas. Skriv om utkastet.')
        kontrollera_resultat(rb,p,t,r,id,formatversion=r.formatversion)
    kallunderlag=summa(dict(kallor={k:v.model_dump(mode='json') for k,v in sorted(rb.kallor.items())},
        lydelser={k:v.model_dump(mode='json') for k,v in sorted(rb.lydelser.items())}))
    return Analysbindning(byra=p.byra.id,profilrevision=profilrevision(p),
        bedomningsmanifest=for_fil(bedomningsmapp/MANIFESTNAMN),utkastmanifest=for_fil(utkastmapp/MANIFESTNAMN),
        regelbas=rb.kontrollsumma,kallunderlag=kallunderlag,historik=historikens_kontrollsumma(byramapp),
        bedomningsdatum=b.datum,modell=modellbindning(rb))


def analysaktualitetshinder(byramapp: Path,rb,paket: Analyspaket,datum: date,*,
                           bedomningsmapp: Path,utkastmapp: Path,krav_modellrisk: bool = True) -> tuple[str,...]:
    """Levande bindning och faktiska bytes; inga lås tas här (AB5 kan hålla analyslas)."""
    from riskanalys.drift.modellrisk import modellriskhinder
    fel=[]
    try:
        if bygg_bindning(byramapp,rb,bedomningsmapp,utkastmapp)!=paket.bindning:
            fel.append('Analysens underlag har ändrats. Förnya och granska analysen.')
    except RiskanalysFel as exc:fel.append(str(exc))
    for b in paket.belagg:
        if b.dokument:
            try:las_belaggsfil(byramapp,b.dokument,b.kontrollsumma)
            except RiskanalysFel as exc:fel.append(str(exc))
    if krav_modellrisk:
        fel.extend(modellriskhinder(byramapp,rb,paket.modellrisk,datum))
    return tuple(dict.fromkeys(fel))


def registrera_analysbeslut(byramapp: Path,rb,beslut: Analysbeslut,*,forvantad_summa: str,
                          bedomningsmapp: Path,utkastmapp: Path) -> str:
    """Gemensam CLI/webb-transaktion; importerad godkänd status kan inte kringgå grinden."""
    with analyslas(byramapp):
        return registrera_analysbeslut_last(byramapp,rb,beslut,forvantad_summa=forvantad_summa,
            bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp)


def registrera_analysbeslut_last(byramapp: Path,rb,beslut: Analysbeslut,*,forvantad_summa: str,
                               bedomningsmapp: Path,utkastmapp: Path) -> str:
    from riskanalys.bedomning.korning import las_bedomning
    from riskanalys.profil.lagring import las_profil
    paket=las_analys(byramapp)
    if paket is None or registersumma(paket)!=forvantad_summa:
        raise RiskanalysFel('Analysen har ändrats. Läs om svaren före beslut.')
    hinder=analysaktualitetshinder(byramapp,rb,paket,beslut.datum,
        bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp,krav_modellrisk=beslut.godkand)
    # Underkännande får dokumentera brister utan att behöva ett godkänt modellriskunderlag.
    if beslut.godkand:
        hinder+=analysbrister(rb,las_profil(byramapp),las_bedomning(bedomningsmapp),paket)
    if hinder:raise RiskanalysFel(' '.join(hinder))
    nytt=registrera_beslut(paket,beslut)
    _skriv_last(byramapp,nytt,paket)
    return registersumma(nytt)



@dataclass(frozen=True)
class ImporteradModellrapport:
    projektrapport: Modellbelagg
    valideringsrapport: Modellbelagg
    modellfiler: Modellbelagg


def importera_modellrapport(byramapp: Path,projektmapp: Path) -> ImporteradModellrapport:
    """Verifiera projektleveransen och registrera dess tre oförändrade innehållskopior."""
    from riskanalys.drift.modellrisk import las_modellvalidering
    from riskanalys.drift.modellrapport import kontrollera_rapportkoppling
    rapport=las_modellvalidering(projektmapp)
    data={n:_las_vald_kalla(projektmapp/n) for n in ('modellvalidering.json','modellvalidering.pdf','modellfiler.json')}
    if rapport!=type(rapport).model_validate_json(data['modellvalidering.json']):
        raise RiskanalysFel('Projektets modellrapport har ändrats. Läs in leveransen igen.')
    kontrollera_rapportkoppling(rapport,data['modellfiler.json'],data['modellvalidering.pdf'])
    kopior={}
    with analyslas(byramapp):
        with _privat_mapp(byramapp,'analys/belagg') as mappfd:
            for n,innehall in data.items():
                hash=for_bytes(innehall);namn=hash.split(':')[1]+'.bin'
                _spara_kopia(mappfd,namn,innehall)
                kopior[n]=Modellbelagg(fil=namn,kontrollsumma=hash)
    return ImporteradModellrapport(kopior['modellvalidering.json'],kopior['modellvalidering.pdf'],kopior['modellfiler.json'])


@dataclass(frozen=True)
class Analyssnapshot:
    paket: Analyspaket | None
    registersumma: str
    brister: tuple[str,...]
    filer: tuple[tuple[str,bytes],...]


def analysbelaggsreferenser(paket: Analyspaket) -> tuple[tuple[str,str],...]:
    """Alla privata kopior som ska frysas, med samma rot som AB7:s Modellbelagg."""
    refs=[(b.dokument,b.kontrollsumma) for b in paket.belagg if b.dokument]
    m=paket.modellrisk
    if m:
        refs.extend((b.fil,b.kontrollsumma) for b in (m.rutin,m.valideringsrapport,m.projektrapport,m.modellfiler))
        refs.extend((b.fil,b.kontrollsumma) for f in m.fel for b in f.belagg)
    return tuple(sorted(set(refs)))


def las_analyssnapshot_last(byramapp: Path,rb,datum: date,*,bedomningsmapp: Path,utkastmapp: Path) -> Analyssnapshot:
    """Läs exakt ett paket och dess verifierade bytes under anroparens analyslas.

    Brister gör snapshot till utkast. Historisk återbyggnad använder paket/filer i
    granskningskopian och anropar aldrig denna levande kontroll igen.
    """
    from riskanalys.bedomning.korning import las_bedomning
    from riskanalys.profil.lagring import las_profil
    paket=las_analys(byramapp)
    if paket is None:return Analyssnapshot(None,'',('Lokal analys saknas.',),())
    fel=list(analysaktualitetshinder(byramapp,rb,paket,datum,bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp))
    try:fel.extend(analysbrister(rb,las_profil(byramapp),las_bedomning(bedomningsmapp),paket))
    except RiskanalysFel as exc:fel.append(str(exc))
    filer={}
    for fil,hash in analysbelaggsreferenser(paket):
        try:filer[fil]=las_belaggsfil(byramapp,fil,hash)
        except RiskanalysFel as exc:fel.append(str(exc))
    return Analyssnapshot(paket,registersumma(paket),tuple(dict.fromkeys(fel)),tuple(sorted(filer.items())))


def las_analyssnapshot(byramapp: Path,rb,datum: date,*,bedomningsmapp: Path,utkastmapp: Path) -> Analyssnapshot:
    with analyslas(byramapp):
        return las_analyssnapshot_last(byramapp,rb,datum,bedomningsmapp=bedomningsmapp,utkastmapp=utkastmapp)
