"""Syntetiska profiler där valda riskfaktorer (sårbarheter) är uppfyllda, för systematiska nivåjämförelser."""
import math

from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.modeller import Regelbas

from tester.fixturer.arb_kedja import andrat, syntetisk_profil

ETT_HELT = 1.0
BANKDATA = 'P-KANAL.bankdata_andel'


def utlosande_varden(villkor: dict) -> dict:
    """Fältvärden som gör villkoret sant: varje led i `alla`, första ledet i `nagon`."""
    if 'alla' in villkor:
        return {falt: varde for led in villkor['alla'] for falt, varde in utlosande_varden(led).items()}
    if 'nagon' in villkor:
        return utlosande_varden(villkor['nagon'][0])
    falt, op, varde = villkor['falt'], villkor['op'], villkor['varde']
    if op == '==':
        return {falt: varde}
    if op == '>=':
        return {falt: varde}
    if op == '>':
        return {falt: ETT_HELT if varde < ETT_HELT else varde + 1}
    if op == '<':
        return {falt: 0.0}
    raise ValueError(f'Okänd operator i syntetisk faktorprofil: {op}')


def faktorvarden(rb: Regelbas) -> dict[str, dict]:
    """Utlösande värden per byråövergripande sårbarhet. Tjänstens egna (område tj) följer av erbjudandet."""
    return {s.id: utlosande_varden(_som_dict(s.villkor)) for s in rb.sarbarheter.values() if s.omrade != 'tj'}


def faktorprofil(rb: Regelbas, sarbarheter: tuple[str, ...], *, alla_tjanster: bool = False,
                 med_bankdata: bool = False) -> Profil:
    """syntetisk_profil med de angivna faktorerna uppfyllda, och vid behov alla katalogtjänster erbjudna.

    Grundprofilen saknar bankdata, så kombinationsfaktorn S-KOMB-01 ersätter S-KUND-01. Med `med_bankdata`
    har byrån bankdata för alla kunder och riskbranschfaktorn kan prövas ensam.
    """
    profil = syntetisk_profil(rb)
    if alla_tjanster:
        for tjanst in rb.tjanster.values():
            profil = andrat(profil, tjanst.erbjuds_falt, varde=True)
    if alla_tjanster and 'P-TJ.bolag03_tredjemansuppdrag' in rb.falt:
        profil = andrat(profil, 'P-TJ.bolag03_tredjemansuppdrag', varde=True)
    andrade = set()
    if med_bankdata:
        falt, varde = _som_antal(rb, profil, BANKDATA, ETT_HELT)
        profil = andrat(profil, falt, varde=varde)
        andrade.add(falt)
    varden = faktorvarden(rb)
    for sarbarhet in sarbarheter:
        for falt, varde in varden[sarbarhet].items():
            falt, varde = _som_antal(rb, profil, falt, varde)
            profil = andrat(profil, falt, varde=varde)
            andrade.add(falt)
    return harled_andelar(profil, rb, frozenset(andrade))


def _som_antal(rb: Regelbas, profil: Profil, falt: str, andel):
    """En härledd andel sätts via sitt antalsfält, så att motorn ser samma andel som intaget härleder."""
    definition = rb.falt[falt]
    if definition.typ != 'andel' or not definition.antalfalt:
        return falt, andel
    bas = profil.uppgifter[definition.basfalt].varde
    return definition.antalfalt, math.ceil(andel * bas)


def _som_dict(villkor) -> dict:
    return villkor if isinstance(villkor, dict) else villkor.model_dump(mode='json', exclude_none=True)
