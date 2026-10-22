"""Registrera bara en uttryckligen bekräftad, faktiskt genomförd utvärdering."""
from datetime import date
from riskanalys.drift.historik import Handelse, registrera_handelse
from riskanalys.fel import RiskanalysFel
from riskanalys.profil.lagring import profilrevision


def registrera_utvardering(tjanst, datum: date, beskrivning: str, revision: str, *, plan_id: str | None = None):
    if datum > date.today() or not beskrivning.strip() or len(beskrivning)>12000:
        raise RiskanalysFel('Ange datum senast idag och vad den genomförda utvärderingen omfattade. Registrera inte en planerad utvärdering som genomförd.')
    from riskanalys.profil.forandringar import forandringslas, aktuell_profil
    from riskanalys.profil.planering import plansumma, planbrister
    from riskanalys.profil.text import kontrollera_text
    kontrollera_text(beskrivning)
    with forandringslas(tjanst.mapp):
        p=aktuell_profil(tjanst.mapp,revision)
        summa = None
        if plan_id is not None:
            if planbrister(tjanst.rb,p) or plan_id not in {t.id for t in p.tjansteplaner}:
                raise RiskanalysFel('Välj en giltig registrerad plan före utvärderingen.')
            summa=plansumma(tjanst.rb,p,plan_id)
            from riskanalys.profil.planering import tillatna_planfalt
            plan=next(t for t in p.tjansteplaner if t.id==plan_id)
            erbjuds=tjanst.rb.tjanster[plan.tjanst].erbjuds_falt
            faktiska=[u for id,u in p.uppgifter.items() if id in tillatna_planfalt(tjanst.rb,plan.tjanst) and id!=erbjuds]
            faktiska.extend(u for g in p.kombinationsgrupper if g.tjanst==plan.tjanst for u in (g.antal,g.bas))
            if (any(u.datum and u.datum>datum for u in (*plan.uppgifter.values(),*faktiska))
                    or any(u.period and u.period.till>datum for u in faktiska)):
                raise RiskanalysFel('Utvärderingens datum får inte vara före planens underlag.')
        return registrera_handelse(tjanst.mapp, Handelse(datum=datum, typ='utvärdering', beskrivning=beskrivning.strip(),plan_id=plan_id,plansumma=summa))
