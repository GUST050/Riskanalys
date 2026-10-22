"""Uttryckligt planavslut som sparas atomiskt tillsammans med profilen.

Genomförande är en historisk registrering, aldrig en slutsats av dagens
erbjudandeflagga eller av avsett datum. Den bevarar planinnehåll och den
utvärdering som gällde vid genomförandet; nutida byråfakta ingår inte i kontrollen.
"""
from datetime import date
import hashlib
import json
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Plangenomforande


def planinnehallssumma(plan):
    data=plan.model_dump(mode='json',exclude={'genomforande'})
    return 'sha256:'+hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def genomforandebrist(plan):
    g=plan.genomforande
    if g and g.planinnehallssumma != planinnehallssumma(plan):
        return f'{plan.id}: genomförd plan har ändrats. Återställ historiken och registrera en ny plan för den nya förändringen.'
    return None


def med_genomforande(rb,profil,plan_id,historik,datum,ansvarig,fore_revision):
    from riskanalys.profil.planering import plansumma
    from riskanalys.profil.text import kontrollera_text
    plan=next((p for p in profil.tjansteplaner if p.id==plan_id),None)
    if plan is None or plan.genomforande is not None:
        raise RiskanalysFel('Välj en ännu inte genomförd plan. Genomförd historik får inte skrivas om.')
    if datum>date.today() or not ansvarig.strip() or len(ansvarig)>200:
        raise RiskanalysFel('Ange genomförandets datum senast idag och ansvarig funktion (högst 200 tecken).')
    kontrollera_text(ansvarig)
    summa=plansumma(rb,profil,plan.id)
    tidigare=[h for h in historik.handelser if h.typ=='utvärdering' and h.plan_id==plan.id
              and h.plansumma==summa and h.beskrivning.strip()]
    if not tidigare:
        raise RiskanalysFel('Genomför och bind en aktuell utvärdering före genomföranderegistreringen.')
    giltiga=[h for h in tidigare if h.datum<=datum]
    if not giltiga:
        raise RiskanalysFel('Genomförandets datum får inte vara före utvärderingens datum.')
    h=max(giltiga,key=lambda h:h.datum)
    kontrollera_text(h.beskrivning)
    g=Plangenomforande(datum=datum,ansvarig=ansvarig,utvarderad=h.datum,utvardering=h.beskrivning,
        plansumma=summa,planinnehallssumma=planinnehallssumma(plan),fore_revision=fore_revision)
    return profil.model_copy(update={'tjansteplaner':tuple(p.model_copy(update={'genomforande':g}) if p.id==plan.id else p for p in profil.tjansteplaner)})
