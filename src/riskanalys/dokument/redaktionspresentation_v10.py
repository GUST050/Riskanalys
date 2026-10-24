"""Återbygg den nya presentationen och bind alla källor utan att ändra analysen."""
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.redaktionmodell_v10 import RedaktionV10
from riskanalys.dokument.resultatmodell_v9 import summa
from riskanalys.fel import RiskanalysFel

VERSION='D-ARB-v10-presentation-2'
POLICY='V10-redaktionell-original-2'


def omforma(docs,profil,redaktion,underlag):
    from riskanalys.dokument.redaktionell_v10 import bygg
    k={'regelbas':redaktion.regelbas.model_dump(mode='json'),
       'analys':redaktion.analys.model_dump(mode='json') if redaktion.analys else None,
       'bedomning':redaktion.bedomning.model_dump(mode='json'),'profil':profil.model_dump(mode='json')}
    bundna=dict(underlag.kallsummor)
    if any(summa(v)!=bundna.get(n) for n,v in k.items()):
        raise RiskanalysFel('Den redaktionella presentationens källor har ändrats. Granska paketet på nytt.')
    r=bygg(k,{'renderade':[d.model_dump(mode='json') for d in docs]},regelbas=redaktion.regelbas,profil=profil)
    if r['flyttfel'] or r['ravarden']:
        raise RiskanalysFel('Resultatrapporten innehåller råa uppgifter eller en bruten flytt. '
            'Kontrollera originaltext och källregister innan rapporten granskas. Originalet skrivs inte om.')
    return tuple(Dokument.model_validate(d) for d in r['renderade']),r


def skapa(p,regelbas,analys,bedomning,profil):
    red=RedaktionV10(regelbas=regelbas,analys=analys,bedomning=bedomning,
        flyttar=(),scenariogrupper=(),scenariomedlemskap=())
    docs,r=omforma(p.renderade,profil,red,p.underlag)
    red=red.model_copy(update={'flyttar':tuple(r['transformationer']),
        'scenariogrupper':tuple(r['scenariogrupper']),'scenariomedlemskap':tuple(r['scenariomedlemskap'])})
    return p.model_copy(update={'version':VERSION,'renderingspolicy':POLICY,'redaktion':red,'renderade':docs})


def kontrollera(p,docs,profil):
    if not p.redaktion or p.version!=VERSION or p.renderingspolicy!=POLICY:
        raise RiskanalysFel('Den redaktionella presentationsversionen är ogiltig.')
    if (summa(p.redaktion.bedomning.model_dump(mode='json'))!=p.bedomning or
        summa(p.redaktion.analys.model_dump(mode='json') if p.redaktion.analys else None)!=p.analys):
        raise RiskanalysFel('Presentationens analys eller bedömning har ändrats.')
    nya,r=omforma(docs,profil,p.redaktion,p.underlag)
    if (nya!=p.renderade or tuple(r['transformationer'])!=p.redaktion.flyttar or
        tuple(r['scenariogrupper'])!=p.redaktion.scenariogrupper or
        tuple(r['scenariomedlemskap'])!=p.redaktion.scenariomedlemskap):
        raise RiskanalysFel('Den redaktionella presentationen eller flyttregistret har ändrats.')
