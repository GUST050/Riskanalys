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
from riskanalys.lagring.yamlfil import las_yaml_text
from riskanalys.profil.lagring import las_profil, profilrevision, spara_profil
from riskanalys.profil.modeller import Profil
from riskanalys.profil.planering import forandringshinder, planbrister
from riskanalys.profil.kombinationer import kombinationsbrister
from riskanalys.profil.planlivslopp import aktiv_plan


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
    sokta = [f for f in (t.erbjuds_falt for t in rb.tjanster.values()) if _blir_ja_utan_tidigare_svar(upp.get(f), efter.uppgifter.get(f))]
    if not sokta:
        return fore.model_copy(update={'uppgifter':upp})
    # Historiken växer med varje sparat svar; tolka varje snapshot en gång per kontroll.
    historik = [kompatibilitetsvy(Profil.model_validate(las_yaml_text(fil.read_text())), rb).uppgifter
                for fil in (mapp/'profil'/'historik').glob('*.yaml')]
    for f in sokta:
        nej = next((u for g in historik if (u := g.get(f)) and u.status == 'bekräftad' and u.varde is False), None)
        if nej:
            upp[f] = nej
    return fore.model_copy(update={'uppgifter':upp})


def _blir_ja_utan_tidigare_svar(fore, efter):
    return bool(efter and efter.status == 'bekräftad' and efter.varde is True) and not (
        fore and fore.status == 'bekräftad' and fore.varde in (True, False))


def inforandebehov_for_andring(mapp, rb, efter, revision):
    from riskanalys.profil.planval import inforandebehov
    with forandringslas(mapp):
        fore = aktuell_profil(mapp, revision)
        return inforandebehov(rb, _tidigare_nej(mapp, rb, fore, efter), efter)


def spara_andring(mapp, rb, efter, revision, *, rattelse=None, lokalt_underlag=False, planval=()):
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
            if gammal and not aktiv_plan(gammal) and gammal!=p:
                hinder.append(f'{p.id}: genomförd eller återkallad plan är historik och får inte skrivas om. Registrera en ny plan.')
            elif not aktiv_plan(p) and (gammal is None or gammal.genomforande!=p.genomforande or gammal.aterkallelse!=p.aterkallelse):
                hinder.append('Genomförande och återkallelse ska registreras genom det särskilda flödet, inte importeras som planuppgift.')
        if not lokalt_underlag:
            from riskanalys.profil.planval import erbjudandeovergangar, validera_planval
            historik = las_historik(mapp)
            # Fakta kan kompletteras före omprövning. Själva erbjudandeövergången prövas här,
            # kvarstående aktualitet för erbjudna tjänster dessutom vid fastställelse.
            overgar = erbjudandeovergangar(rb, fore, efter)
            historisk = fore if rattelse else _tidigare_nej(mapp, rb, fore, efter)
            valfore = historisk
            if rattelse:
                if any(v.tjanst == rattelse.tjanst for v in planval):
                    raise RiskanalysFel('Rättelse och verkligt införandeval får inte kombineras för samma tjänst.')
                if rattelse.tjanst in rb.tjanster:
                    falt = rb.tjanster[rattelse.tjanst].erbjuds_falt
                    from riskanalys.profil.modeller import Uppgift
                    valfore = historisk.model_copy(update={'uppgifter': {**historisk.uppgifter, falt: efter.uppgifter.get(falt, Uppgift())}})
            valda = validera_planval(rb, valfore, efter, planval)
            valda_id = {p.id for p in valda.values()}
            relevant = efter.model_copy(update={'tjansteplaner':tuple(p for p in efter.tjansteplaner
                if p.tjanst in overgar and (p.typ != 'ny_tjanst' or not aktiv_plan(p) or p.id in valda_id))})
            hinder.extend(forandringshinder(rb, historisk, relevant, historik, date.today(), rattelse=rattelse))
        elif planval:
            raise RiskanalysFel('Planval hör till erbjudandeövergången, inte till sparning av lokalt underlag.')
        if hinder:
            raise RiskanalysFel('\n'.join(dict.fromkeys(hinder)))
        if rattelse:
            registrera_handelse(mapp, Handelse(datum=rattelse.datum, typ='rättelse', beskrivning='Begärd rättelse: '+rattelse.motivering, rattelse=rattelse))
        if not lokalt_underlag:
            from riskanalys.profil.planlivslopp import med_genomforande
            from riskanalys.profil.omfattning import kompatibilitetsvy
            for p in valda.values():
                u=kompatibilitetsvy(efter,rb).uppgifter[rb.tjanster[p.tjanst].erbjuds_falt]
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
        if plan is None or not aktiv_plan(plan) or planbrister(rb,p):
            raise RiskanalysFel('Välj en giltig registrerad plan.')
        vy=kompatibilitetsvy(p,rb);f=rb.tjanster[plan.tjanst].erbjuds_falt
        if not vy.ar_bekraftad(f) or vy.uppgifter[f].varde is not True:
            raise RiskanalysFel('Bekräfta först att tjänsten erbjuds; en planerad tjänst är inte genomförd.')
        nytt=med_genomforande(rb,p,plan_id,las_historik(mapp),datum,ansvarig,revision)
        spara_profil(mapp,nytt,revision=revision)
        return nytt


def aterkalla_plan(mapp, rb, plan_id, datum, ansvarig, motivering, revision):
    """Registrera återkallelsen i samma atomiska profilskrivning som dess innehåll."""
    from riskanalys.profil.planlivslopp import med_aterkallelse
    from riskanalys.profil.text import kontrollera_profiltext
    with forandringslas(mapp):
        p = aktuell_profil(mapp, revision)
        nytt = med_aterkallelse(p, plan_id, datum, ansvarig, motivering, revision)
        kontrollera_profiltext(nytt)
        spara_profil(mapp, nytt, revision=revision)
        return nytt
