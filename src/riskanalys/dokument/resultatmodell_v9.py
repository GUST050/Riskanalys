"""Frysta källor och urvalsbeslut för V9; inga alternativa riskberäkningar."""
import json
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from riskanalys.bedomning.modeller import Scenariobedomning
from riskanalys.lagring.kontrollsumma import for_text


class Fryst(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')


def summa(value):
    return for_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def kallartefakter(rb, profil, bedomning, resultat, historik, analys, analysdokument):
    return {namn: value.model_dump(mode='json') if value is not None else None
            for namn, value in (('regelbas',rb),('profil',profil),('bedomning',bedomning),
                                ('historik',historik),('analys',analys),('analysdokument',analysdokument))} | {
        'skrivresultat':{id:r.model_dump(mode='json') for id,r in resultat.items()}}


def pointerdel(value):
    return str(value).replace('~','~0').replace('/','~1')


def los_pointer(data, pointer):
    if pointer == '':
        return data
    if not pointer.startswith('/'):
        raise ValueError('Källpointer ska börja med / eller vara tom.')
    for part in pointer[1:].split('/'):
        import re
        if re.search(r'~(?![01])',part):
            raise ValueError('Felaktig RFC 6901-escape.')
        part = part.replace('~1','/').replace('~0','~')
        if isinstance(data,list):
            if not part.isdigit() or (len(part)>1 and part.startswith('0')):
                raise ValueError('Felaktigt listindex i källpointer.')
            data = data[int(part)]
        else:
            data = data[part]
    return data


class Kallreferens(Fryst):
    artefakt: Literal['profil','bedomning','analys','skrivresultat','historik','regelbas','analysdokument']
    pointer: str
    summa: str = Field(pattern=r'^sha256:[0-9a-f]{64}$')


def referens(kallor, artefakt, pointer=''):
    return Kallreferens(artefakt=artefakt,pointer=pointer,summa=summa(los_pointer(kallor[artefakt],pointer)))


def los_referens(kallor, ref):
    try:
        value = los_pointer(kallor[ref.artefakt],ref.pointer)
        if summa(value) != ref.summa:
            raise ValueError('Källvärdet har ändrats.')
        return value
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise ValueError(f'Kontrollera källan {ref.artefakt}{ref.pointer}: {e}') from e


class Urvalspost(Fryst):
    id: str
    tjanst: str | None = None
    hot: tuple[str,...] = ()
    dimension: Literal['pt','tf'] | None = None
    riskled: Literal['inneboende','kvarstaende'] | None = None
    hantering: Literal['sammanfattas','hanvisas'] = 'sammanfattas'
    skal: tuple[Literal['avgor_fore','avgor_efter','egen_sarbarhet','avvikelse','osakerhet',
                        'erfarenhet','atgard','oppet_gap','ej_relevant','metoduppfoljning'],...]
    kallor: tuple[Kallreferens,...]


class Presentationsbrist(Fryst):
    kod: str
    avsnitt: str
    beskrivning: str
    kallor: tuple[Kallreferens,...] = ()


class ScenariocellV9(Fryst):
    tjanst: str
    scenario: Scenariobedomning | None
    status: Literal['beraknad','ej_relevant','saknas','okant']
    medlemmar: tuple[str,...]
    kallor: tuple[Kallreferens,...]

    @model_validator(mode='after')
    def giltig(self):
        if (self.status == 'beraknad') != (self.scenario is not None):
            raise ValueError('Beräknad cell kräver sitt oförändrade motorresultat.')
        return self


class ScenarioradV9(Fryst):
    id: str
    hot: str
    dimension: Literal['pt','tf']
    mekanismkallor: tuple[Kallreferens,...]
    celler: tuple[ScenariocellV9,...]


class ResultatunderlagV9(Fryst):
    poster: tuple[Urvalspost,...]
    brister: tuple[Presentationsbrist,...]
    matris: tuple[ScenarioradV9,...] = ()
    kallsummor: tuple[tuple[str,str],...] = ()


class TransformationV9(Fryst):
    pointer: str
    fore: str
    efter: str
    orsak: Literal['format','leveransdel','visningsnummer','tredelsforklaring']


class KonstruktionV9(Fryst):
    placering: str
    mall: str
    kallor: tuple[Kallreferens,...]


from riskanalys.dokument.modeller import Dokument


class ResultatbyggeV9(Fryst):
    dokument: Dokument
    analysdokument: Dokument
    underlag: ResultatunderlagV9
    transformationer: tuple[TransformationV9,...]
    konstruktioner: tuple[KonstruktionV9,...] = ()
