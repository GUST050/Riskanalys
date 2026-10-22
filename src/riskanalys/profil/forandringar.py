"""Gemensam transaktionsgräns för CLI/webb: förändringslås → profil-CAS → historiklås.

Rättelsens revisionsbundna avsikt journalförs före profilens atomiska namnbyte.
Vid avbruten profilsparning visar historiken därför ett försök, aldrig ett oregistrerat
undantag från införandespärren. Eftervärdet i profilen visar om rättelsen genomfördes.
"""
from contextlib import contextmanager
from datetime import date
import fcntl
import os
from riskanalys.fel import RiskanalysFel
from riskanalys.drift.historik import Handelse, las_historik, registrera_handelse
from riskanalys.profil.lagring import las_profil, profilrevision, spara_profil
from riskanalys.profil.modeller import Profil
from riskanalys.profil.planering import forandringshinder, planbrister
from riskanalys.profil.kombinationer import kombinationsbrister


@contextmanager
def forandringslas(mapp):
    mapp.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(mapp/'.forandringslas', os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd,'w') as las:
        fcntl.flock(las, fcntl.LOCK_EX)
        yield


def aktuell_profil(mapp, revision):
    p = las_profil(mapp)
    if profilrevision(p) != revision:
        raise RiskanalysFel('Profilen har ändrats i en annan flik eller ett annat program. Läs om sidan.')
    return p


def _tidigare_nej(mapp, rb, fore, efter):
    """Ett mellanliggande okänt svar gör inte ett tidigare nej till första kartläggning."""
    from riskanalys.profil.omfattning import kompatibilitetsvy
    upp = dict(kompatibilitetsvy(fore,rb).uppgifter)
    for t in rb.tjanster.values():
        f = t.erbjuds_falt
        a, b = upp.get(f), efter.uppgifter.get(f)
        if not (b and b.status == 'bekräftad' and b.varde is True) or a and a.status == 'bekräftad' and a.varde in (True, False):
            continue
        import yaml
        for fil in (mapp/'profil'/'historik').glob('*.yaml'):
            gammal = Profil.model_validate(yaml.safe_load(fil.read_text()))
            u = kompatibilitetsvy(gammal,rb).uppgifter.get(f)
            if u and u.status == 'bekräftad' and u.varde is False:
                upp[f] = u
                break
    return fore.model_copy(update={'uppgifter':upp})


def spara_andring(mapp, rb, efter, revision, *, rattelse=None, lokalt_underlag=False):
    from riskanalys.profil.text import kontrollera_profiltext
    with forandringslas(mapp):
        fore = aktuell_profil(mapp, revision)
        kontrollera_profiltext(efter)
        hinder = [*planbrister(rb, efter), *kombinationsbrister(rb, efter)]
        if set(p.id for p in fore.tjansteplaner) - set(p.id for p in efter.tjansteplaner):
            hinder.append('Registrerade planer får inte raderas. Bevara förändringsspåret.')
        gamla={p.id:p for p in fore.tjansteplaner}
        if any(p.id in gamla and p.tjanst!=gamla[p.id].tjanst for p in efter.tjansteplaner):
            hinder.append('En registrerad plans tjänst får inte bytas. Skapa en ny plan och bevara den tidigare.')
        for p in efter.tjansteplaner:
            gammal=gamla.get(p.id)
            if gammal and gammal.genomforande is not None and gammal!=p:
                hinder.append(f'{p.id}: genomförd plan är historik och får inte skrivas om. Registrera en ny plan.')
            elif p.genomforande is not None and (gammal is None or gammal.genomforande!=p.genomforande):
                hinder.append('Genomförande ska registreras genom det särskilda flödet, inte importeras som planuppgift.')
        if not lokalt_underlag:
            historik = las_historik(mapp)
            # Fakta kan kompletteras före omprövning. Själva erbjudandeövergången prövas här,
            # kvarstående aktualitet för erbjudna tjänster dessutom vid fastställelse.
            overgar = {t.id for t in rb.tjanster.values() if efter.ar_bekraftad(t.erbjuds_falt)
                and efter.uppgifter[t.erbjuds_falt].varde is True
                and not (fore.ar_bekraftad(t.erbjuds_falt) and fore.uppgifter[t.erbjuds_falt].varde is True)}
            relevant = efter.model_copy(update={'tjansteplaner':tuple(p for p in efter.tjansteplaner if p.tjanst in overgar)})
            historisk = fore if rattelse else _tidigare_nej(mapp, rb, fore, efter)
            hinder.extend(forandringshinder(rb, historisk, relevant, historik, date.today(), rattelse=rattelse))
        if hinder:
            raise RiskanalysFel('\n'.join(dict.fromkeys(hinder)))
        if rattelse:
            registrera_handelse(mapp, Handelse(datum=rattelse.datum, typ='rättelse', beskrivning='Begärd rättelse: '+rattelse.motivering, rattelse=rattelse))
        if not lokalt_underlag and not rattelse:
            from riskanalys.profil.planlivslopp import med_genomforande
            for p in efter.tjansteplaner:
                if p.tjanst in overgar and p.typ=='ny_tjanst' and p.genomforande is None:
                    u=efter.uppgifter[rb.tjanster[p.tjanst].erbjuds_falt]
                    if u.datum is None:
                        raise RiskanalysFel('Bekräfta datum för det nya erbjudandet före införandet.')
                    efter=med_genomforande(rb,efter,p.id,historik,u.datum,u.bekraftad_av or '',revision)
        spara_profil(mapp, efter, revision=revision)
    return efter


def registrera_genomforande(mapp,rb,plan_id,datum,ansvarig,revision):
    """Uttrycklig registrering för en faktiskt genomförd ändring av erbjuden tjänst."""
    from riskanalys.profil.planlivslopp import med_genomforande
    from riskanalys.profil.omfattning import kompatibilitetsvy
    with forandringslas(mapp):
        p=aktuell_profil(mapp,revision)
        plan=next((t for t in p.tjansteplaner if t.id==plan_id),None)
        if plan is None or plan.genomforande is not None or planbrister(rb,p):
            raise RiskanalysFel('Välj en giltig registrerad plan.')
        vy=kompatibilitetsvy(p,rb);f=rb.tjanster[plan.tjanst].erbjuds_falt
        if not vy.ar_bekraftad(f) or vy.uppgifter[f].varde is not True:
            raise RiskanalysFel('Bekräfta först att tjänsten erbjuds; en planerad tjänst är inte genomförd.')
        nytt=med_genomforande(rb,p,plan_id,las_historik(mapp),datum,ansvarig,revision)
        spara_profil(mapp,nytt,revision=revision)
        return nytt
