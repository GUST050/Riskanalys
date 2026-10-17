"""Privat modellriskunderlag och fullständighetsgrind, utan automatisk attest."""
import os
import stat
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import Field

from riskanalys.drift.historik import lagg_till_manader
from riskanalys.drift.modellidentitet import (  # noqa: F401 -- publikt AB7-kontrakt
    Modellfil, Modellfilmanifest, Modellmiljo, modellbindning, modellfilmanifest, modellmiljo,
)
from riskanalys.drift.modellrapport import (  # noqa: F401 -- publikt AB7-kontrakt
    Modellvalidering, Text, kontrollera_rapportkoppling, exportera_modellvalidering,
    las_modellvalidering, valideringens_innehallssumma,
)
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.kontrollsumma import for_bytes
from riskanalys.regelverk.modeller import KONTROLLSUMMA, Regelbas, Strikt


class Modellbelagg(Strikt):
    fil: str
    kontrollsumma: str = Field(pattern=KONTROLLSUMMA)


class Modellfel(Strikt):
    id: Text
    datum: date
    beskrivning: Text
    allvar: Literal['vasentligt', 'ovrigt']
    status: Literal['oppet', 'atgardat']
    atgard_och_omprovning: str
    belagg: tuple[Modellbelagg, ...]


class Modellriskunderlag(Strikt):
    modellansvarig: Text
    modellbindning: str = Field(pattern=KONTROLLSUMMA)
    rutin: Modellbelagg
    valideringsrapport: Modellbelagg
    projektrapport: Modellbelagg
    modellfiler: Modellbelagg
    utvarderad: date
    nasta_genomgang: date
    feluppfoljning: Text
    fel: tuple[Modellfel, ...]
    godkand: bool
    beslutad_av: Text
    beslutsdatum: date


def _belaggsbytes(byramapp: Path, belagg: Modellbelagg) -> bytes:
    """Läs via kataloghandtag utan att följa länkar eller öppna specialfiler."""
    namn = PurePosixPath(belagg.fil)
    if (not belagg.fil or namn.is_absolute() or '\\' in belagg.fil
            or any(del_ in {'', '.', '..'} for del_ in belagg.fil.split('/'))):
        raise RiskanalysFel('Modellbelägget har en otillåten sökväg. Importera en privat dokumentkopia.')
    handtag = []
    try:
        fd = os.open(byramapp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handtag.append(fd)
        for del_ in ('analys', 'belagg', *namn.parts[:-1]):
            fd = os.open(del_, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            handtag.append(fd)
        fil = os.open(namn.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(fil, 'rb') as indata:
            if not stat.S_ISREG(os.fstat(indata.fileno()).st_mode):
                raise RiskanalysFel('Modellbelägget är inte en vanlig fil. Importera dokumentkopian igen.')
            data = indata.read()
        if for_bytes(data) != belagg.kontrollsumma:
            raise RiskanalysFel('Modellbelägget har ändrats. Importera kopian och pröva användningsbeslutet igen.')
        return data
    finally:
        for fd in reversed(handtag):
            os.close(fd)


def modellriskhinder(byramapp: Path, rb: Regelbas,
                     underlag: Modellriskunderlag | None, datum: date) -> tuple[str, ...]:
    if underlag is None:
        return ('Modellriskunderlag saknas. Importera projektets rapport och dokumentera byråns användningsbeslut.',)
    try:
        u = Modellriskunderlag.model_validate(underlag.model_dump(mode='json'))
    except ValueError:
        return ('Modellriskunderlaget är ofullständigt. Komplettera ansvar, belägg och uppföljning.',)
    hinder = []
    try:
        aktuell = modellbindning(rb)
        if u.modellbindning != aktuell:
            hinder.append('Modellen har ändrats. Pröva en rapport för den aktuella modellen.')
        _belaggsbytes(byramapp, u.rutin)
        rapport = Modellvalidering.model_validate_json(_belaggsbytes(byramapp, u.projektrapport))
        inventarium = kontrollera_rapportkoppling(
            rapport, _belaggsbytes(byramapp, u.modellfiler), _belaggsbytes(byramapp, u.valideringsrapport))
        if (rapport.modellbindning != aktuell or rapport.modellbindning != u.modellbindning
                or inventarium.regelbas_kontrollsumma != rb.kontrollsumma):
            hinder.append('Projektets rapport gäller inte den aktuella modellen. Importera rätt rapport.')
        sakkunnig = rapport.sakkunnig
        if (rapport.m1_beslut != 'godkant'
                or not sakkunnig.galler(valideringens_innehallssumma(rapport))
                or not sakkunnig.av or not sakkunnig.av.strip() or sakkunnig.datum is None):
            hinder.append('Projektets rapport saknar giltig sakkunnigprövning med uttryckligt M1-beslut.')
        if (rapport.datum > u.utvarderad or rapport.datum > datum
                or (sakkunnig.datum is not None
                    and (sakkunnig.datum < rapport.datum or sakkunnig.datum > u.utvarderad))):
            hinder.append('Modellrapportens datum eller sakkunnigprövning ligger efter byråns utvärdering.')
    except (RiskanalysFel, OSError, ValueError):
        hinder.append('Modellens rapport eller privata belägg saknas, är ändrade eller har fel koppling. Importera rätt frysta underlag.')
    if not u.godkand:
        hinder.append('Byrån har inte godkänt användningen av projektets modellrapport.')
    if (u.utvarderad > datum
            or not (u.utvarderad < u.nasta_genomgang <= lagg_till_manader(u.utvarderad, 12))):
        hinder.append('Nästa modellgenomgång ska ligga efter utvärderingen och högst tolv månader senare.')
    if datum > u.nasta_genomgang:
        hinder.append('Modellens uppföljningsdatum har passerat. Genomför en ny utvärdering.')
    if u.utvarderad > u.beslutsdatum or u.beslutsdatum > datum:
        hinder.append('Modellriskbeslutets datum måste ligga efter utvärderingen och senast på prövningsdagen.')
    if len({fel.id for fel in u.fel}) != len(u.fel):
        hinder.append('Modellfelens id ska vara unika. Rätta felregistret.')
    for fel in u.fel:
        if fel.datum > datum:
            hinder.append(f'Modellfel {fel.id} har ett framtida datum. Rätta felregistret.')
        if fel.allvar == 'vasentligt':
            if fel.status == 'oppet':
                hinder.append(f'Väsentligt modellfel {fel.id} är öppet. Rätta och ompröva modellen.')
            elif not fel.atgard_och_omprovning.strip() or not fel.belagg or fel.datum > u.utvarderad:
                hinder.append(f'Väsentligt modellfel {fel.id} saknar dokumenterad rättning och aktuell omprövning.')
        for belagg in fel.belagg:
            try:
                _belaggsbytes(byramapp, belagg)
            except (OSError, RiskanalysFel):
                hinder.append(f'Modellfel {fel.id} har saknat eller ändrat åtgärdsbelägg. Importera rätt dokumentkopia.')
    return tuple(hinder)
