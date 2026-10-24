"""Befintliga utkast byter bara disposition genom ett uttryckligt formatval."""
import json
from riskanalys.dokument.presentation_v10 import PRESENTATIONSVERSION
from riskanalys.dokument.redaktionspresentation_v10 import VERSION
from riskanalys.fel import RiskanalysFel


def las_version(granskning):
    from riskanalys.lagring.manifest import verifiera_manifest
    try:
        if verifiera_manifest(granskning):raise ValueError('Ändrat manifest')
        version=json.loads((granskning/'presentation.json').read_text())['version']
        if version not in (PRESENTATIONSVERSION,VERSION):raise ValueError('Okänd presentation')
        return version
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise RiskanalysFel('Den tidigare presentationen kan inte läsas. Återställ den före formatbyte.') from exc


def valj(byramapp,bedomning,rapportformat):
    if rapportformat=='v10':return PRESENTATIONSVERSION
    if rapportformat=='v10-redaktionell':return VERSION
    from riskanalys.lagring.korningar import avslutade_korningar
    from riskanalys.lagring.manifest import las_manifest
    for g in reversed(avslutade_korningar(byramapp,'granskning')):
        meta=las_manifest(g).metadata
        if meta.get('bedomning')==bedomning and meta.get('dokumentformat')=='D-ARB-resultat-v10':
            return las_version(g)
    return VERSION
