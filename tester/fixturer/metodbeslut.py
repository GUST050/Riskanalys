"""Explicit ombindning i syntetiska regelkopior före deras testattest."""
from pathlib import Path
import yaml
from riskanalys.regelverk.laddning import ladda_regelbas,STANDARD_REGELBAS
from riskanalys.regelverk.metodbeslut import objektindex


def bind_om_testbeslut(rot:Path):
    assert rot.resolve()!=STANDARD_REGELBAS.resolve(), 'Produktens regelbas får inte ändras av testfixturen.'
    fil=rot/'beslutstabeller/metodbeslut.yaml'
    if not fil.exists():return
    data=yaml.safe_load(fil.read_text());index=objektindex(ladda_regelbas(rot))
    for b in data:
        b['objekt']={id:index[id] for id in b['objekt']}
        b['sakkunnig']={'status':'ej_granskad'}
    fil.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
