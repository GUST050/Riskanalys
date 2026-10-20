"""V8:s frysta presentationskälla och begränsade leveransmetadata."""
from datetime import date
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from riskanalys.dokument.presentation_v8 import Presentation, bygg_presentation, kallsumma
from riskanalys.fel import RiskanalysFel

PRESENTATIONSFIL = 'presentation.json'
LEVERANSFIL = 'leverans.json'


class Leverans(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    format: Literal['D-ARB-v8-leverans-1'] = 'D-ARB-v8-leverans-1'
    datum: date
    bedomning: str
    granskning: str
    version: int | None = Field(default=None, ge=1)
    organ: str | None = None

    @model_validator(mode='after')
    def beslut(self):
        if (self.version is None) != (self.organ is None):
            raise ValueError('Fastställd leverans kräver både version och beslutsorgan.')
        return self

    @property
    def filnamn(self) -> tuple[str, str]:
        from riskanalys.dokument.leverans_v8 import LEVERANSMALL
        return LEVERANSMALL.filnamn_for(self)

    @property
    def statusrad(self) -> str:
        from riskanalys.dokument.leverans_v8 import LEVERANSMALL
        return LEVERANSMALL.status_for(self)

    def inledning(self, del_) -> str:
        from riskanalys.dokument.leverans_v8 import LEVERANSMALL
        return LEVERANSMALL.inledning_for(self, del_)


def _regelbas_for_aktuell_presentation(bedomning, regelbas=None):
    if regelbas is None:
        from riskanalys.regelverk.laddning import STANDARD_REGELBAS, ladda_regelbas
        regelbas = ladda_regelbas(STANDARD_REGELBAS)
    if (regelbas.version != bedomning.regelbas_version
            or regelbas.kontrollsumma != bedomning.regelbas_kontrollsumma):
        raise ValueError('Aktuell presentation kräver bedömningens exakt bundna regelbas.')
    return regelbas


def las_presentation(granskningsmapp: Path, bedomning, profil, *, aktuell=True, regelbas=None) -> Presentation:
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.granskning.analysunderlag import las_fryst_analys
    try:
        p=Presentation.model_validate_json((granskningsmapp/PRESENTATIONSFIL).read_text(encoding='utf-8'))
        d,fynd=las_granskning(granskningsmapp)
        analys=las_fryst_analys(granskningsmapp).paket
        expected=(kallsumma(d.model_dump(mode='json')),kallsumma(analys.model_dump(mode='json') if analys else None),
                  kallsumma([f.model_dump(mode='json') for f in fynd]),kallsumma(bedomning.model_dump(mode='json')))
        if (p.dokument,p.analys,p.fynd,p.bedomning)!=expected:
            raise ValueError('Presentationskällan avviker')
        if aktuell:
            from riskanalys.dokument.profiloriginal_v8 import kontrollera_aktuella_originaloperationer
            regelbas = _regelbas_for_aktuell_presentation(bedomning,regelbas)
            kontrollera_aktuella_originaloperationer(d,profil,regelbas,bedomning)
            if p!=bygg_presentation(d,analys=analys,fynd=fynd,bedomning=bedomning,profil=profil):
                raise ValueError('Presentationens text, medlemmar eller placering har ändrats')
        return p
    except (OSError,ValueError) as exc:
        raise RiskanalysFel('V8-presentationen är ändrad eller saknas. Granska båda delarna på nytt.') from exc


def verifiera_rapportpaket(mapp: Path, manifest) -> list[str]:
    """Versionsgrund från den frysta dokumentkällan, aldrig bara yttre versionshint.

    Historiska paket kontrolleras mot sina sparade bytes, utan ny rendering.
    Befintlig manifestintegritet är hotmodellen, inte en ny signaturtjänst.
    """
    from riskanalys.dokument.modeller import Dokument
    from riskanalys.dokument.skrivversion import V8
    from riskanalys.lagring.manifest import verifiera_manifest
    from riskanalys.bedomning.korning import las_bedomning, las_bedomningsprofil
    gm=mapp/'granskning'
    if not (gm/'dokument.json').is_file():
        if (mapp/LEVERANSFIL).exists() or (manifest.metadata.get('dokumentformat')==V8 and manifest.metadata.get('typ') in ('export_utkast','faststallt_paket')):
            return ['V8-paketets frysta dokumentkälla saknas.']
        return []
    try:
        fel=[f'Fryst källa granskning: {rad}' for rad in verifiera_manifest(gm)]
        if fel:return fel
        d=Dokument.model_validate_json((gm/'dokument.json').read_text(encoding='utf-8'))
        if d.formatversion!=V8:
            return ['Leveransens V8-format avviker från dokumentkällan.'] if (mapp/LEVERANSFIL).exists() else []
        fel=[f'Fryst källa bedomning: {rad}' for rad in verifiera_manifest(mapp/'bedomning')]
        if fel:return fel
        b=las_bedomning(mapp/'bedomning')
        presentation = las_presentation(gm,b,las_bedomningsprofil(mapp/'bedomning'),aktuell=False)
        leverans=Leverans.model_validate_json((mapp/LEVERANSFIL).read_text(encoding='utf-8'))
        if presentation.leveransmall is None:
            # Enbart historisk byteverifiering av V8-prov före mallbindningen.
            # Ingen aktuell mall/default får påverka dessa ursprungliga filnamn.
            suffix = 'UTKAST' if leverans.version is None else f'v{leverans.version}'
            filnamn = (f'allman-riskbedomning-{suffix}.docx', f'underlagsbilaga-{suffix}.docx')
        else:
            filnamn = presentation.leveransmall.filnamn_for(leverans)
        for namn in filnamn:
            if namn not in manifest.filer or not (mapp/namn).is_file():
                fel.append(f'Obligatorisk V8-del saknas i paketet eller manifestet: {namn}')
        return fel
    except (OSError,ValueError,RiskanalysFel) as exc:
        return [f'V8-paketets frysta källa eller leveransbindning är skadad: {exc}']
