"""Typade filadaptrar för gemensamma analysoperationer, aldrig import av attester."""
from pydantic import TypeAdapter
from riskanalys.analys import modeller as m
from riskanalys.fel import RiskanalysFel
from riskanalys.lagring.yamlfil import las_yaml


def las(fil):
    try:return las_yaml(fil)
    except (OSError,ValueError) as exc:
        raise RiskanalysFel('Välj en befintlig YAML- eller JSON-fil med analysens typade fält.') from exc


def referenser(fil):
    return TypeAdapter(tuple[m.GemensamReferens,...]).validate_python(las(fil))


def tillampning(fil):
    raw=las(fil)
    if not isinstance(raw,dict) or set(raw)!={'referens','tillampning'}:
        raise RiskanalysFel('Tillämpningsfilen ska innehålla referens och tillampning.')
    ref=m.GemensamReferens.model_validate(raw['referens'])
    modell=m.Sarbarhetstillampning if ref.slag=='sarbarhet' else m.GemensamTillampning
    return ref,modell.model_validate(raw['tillampning'])


def tackning(fil):
    return m.Tackningsprovning.model_validate(las(fil))


def visa_tackning(tjanst,fil,id,forfattare):
    from riskanalys.analys.gemensam import tackningssumma
    import yaml
    status=tjanst.status();p=status.paket
    if p is None or p.schemaversion!=2:raise RiskanalysFel('Starta eller överför till schema 2 först.')
    t=next((t for t in status.bedomning.tjanster if t.tjanst==id),None)
    if t is None:raise RiskanalysFel('Välj tjänst med --tjanst.')
    prov=tackning(fil).model_copy(update={'forfattare':tjanst._forfattare(forfattare)})
    prov=prov.model_copy(update={'visad_summa':tackningssumma(tjanst.rb,p,t,prov)})
    print(yaml.safe_dump(prov.model_dump(mode='json'),allow_unicode=True,sort_keys=False))
