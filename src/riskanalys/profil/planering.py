"""Ren prövning av registrerade förändringar. Ingen beräkning av planens risk.

Plansumma v1: sorterad JSON av regelbasens kontrollsumma, byråidentitet, planen
och aktuella icke-personliga sakuppgifter i mål-P-TJ, P-GEO, P-KUND, P-KANAL
och P-RISK samt tjänstens kombinationsgrupper. Hela måltjänstens erbjudandeuppgift
undantas. Erbjudandets automatiska inaktualisering av följdsvar normaliseras till
inaktuell=True i båda lägena; värden, källor, status, datum och belägg bevaras.
Historik ingår inte. Detta påverkar inte profilrevision eller analysbindning.
"""
import hashlib
import json
from riskanalys.profil.hantering import belaggsbrister
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.regelverk.villkor import kontrollera_varde, VillkorsFel
from riskanalys.profil.planlivslopp import aktiv_plan


def tillatna_planfalt(rb, tjanst):
    if tjanst not in rb.tjanster:
        return ()
    prefix = rb.tjanster[tjanst].erbjuds_falt.removesuffix('_erbjuds') + '_'
    return tuple(id for id, f in rb.falt.items() if not f.personuppgift
        and not f.antalfalt and not f.basfalt and not f.alias_for
        and (id.startswith(prefix) or id.startswith(('P-GEO.', 'P-KUND.', 'P-KANAL.', 'P-RISK.'))))


def planbrister(rb, profil):
    fel, sett = [], set()
    for plan in profil.tjansteplaner:
        if plan.id in sett:
            fel.append(f'Plan-ID {plan.id} förekommer flera gånger.')
        sett.add(plan.id)
        if not aktiv_plan(plan):
            from riskanalys.profil.planlivslopp import genomforandebrist
            if brist:=genomforandebrist(plan):
                fel.append(brist)
            continue
        if plan.tjanst not in rb.tjanster:
            fel.append(f'{plan.id}: välj en tjänst ur regelpaketet.')
            continue
        from riskanalys.regelverk.urval import valj
        if plan.tjanst not in valj(rb, profil.byra.regelpaket, profil.byra.datum, profil.byra.lan).tjanster:
            fel.append(f'{plan.id}: tjänsten ingår inte i byråns regelpaket.')
        if not plan.beskrivning.strip():
            fel.append(f'{plan.id}: beskriv förändringen.')
        tillatna = tillatna_planfalt(rb, plan.tjanst)
        for id, u in plan.uppgifter.items():
            if id not in tillatna or u.harledd:
                fel.append(f'{plan.id}: {id} är inte ett tillåtet planantagande.')
                continue
            if u.varde is not None:
                try:
                    kontrollera_varde(rb.faltdefinitioner()[id], u.varde)
                except VillkorsFel:
                    fel.append(f'{plan.id}: kontrollera typen för {id}.')
        fel.extend(belaggsbrister(Profil(byra=profil.byra, uppgifter=plan.uppgifter)))
    return tuple(fel)


def plansumma(rb, profil, plan_id):
    from riskanalys.profil.omfattning import kompatibilitetsvy
    profil=kompatibilitetsvy(profil,rb)
    plan = next(p for p in profil.tjansteplaner if p.id == plan_id)
    erbjuds = rb.tjanster[plan.tjanst].erbjuds_falt
    ids = tillatna_planfalt(rb, plan.tjanst)
    beroende={erbjuds}
    while True:
        nya={id for id,f in rb.falt.items() if f.intag and set(f.intag.beroenden)&beroende}-beroende
        if not nya:
            break
        beroende |= nya
    sakuppgifter={}
    for id,u in profil.uppgifter.items():
        if id in ids and id!=erbjuds:
            data=u.model_dump(mode='json')
            if id in beroende and u.status in ('bekräftad','föreslagen','ej_tillämplig'):
                data['inaktuell']=True
            sakuppgifter[id]=data
    data = {'version': 1, 'regelbas': rb.kontrollsumma, 'byra': profil.byra.model_dump(mode='json'),
            'plan': plan.model_dump(mode='json',exclude={'genomforande', 'aterkallelse'}), 'sakuppgifter': sakuppgifter,
            'kombinationsgrupper': [g.model_dump(mode='json') for g in profil.kombinationsgrupper if g.tjanst==plan.tjanst]}
    return 'sha256:' + hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def aktuell_planutvardering(rb, profil, plan, historik, datum):
    return aktiv_plan(plan) and any(h.typ == 'utvärdering' and h.plan_id == plan.id and h.plansumma == plansumma(rb, profil, plan.id)
               and h.datum <= datum and h.beskrivning.strip() for h in historik.handelser)


def forandringshinder(rb, fore, efter, historik, datum, *, rattelse=None):
    from riskanalys.profil.omfattning import kompatibilitetsvy
    forevy=kompatibilitetsvy(fore,rb)
    eftervy=kompatibilitetsvy(efter,rb)
    hinder = list(planbrister(rb, efter))
    hinder.extend(f'{p.id}: beslutsdatum är före planens registrerade genomförande {p.genomforande.datum}.'
                  for p in efter.tjansteplaner if p.genomforande and p.genomforande.datum>datum)
    for id,t in rb.tjanster.items():
        f = t.erbjuds_falt
        a, b = forevy.uppgifter.get(f, Uppgift()), eftervy.uppgifter.get(f, Uppgift())
        if b.status != 'bekräftad' or b.varde is not True or b.inaktuell:
            continue
        planer = [p for p in efter.tjansteplaner if p.tjanst == id and aktiv_plan(p)]
        nytt = a.varde is False and a.status == 'bekräftad'
        if rattelse and rattelse.tjanst == id:
            giltig = (a.status == 'bekräftad' and a.varde is False and not planer and rattelse.fore == a and rattelse.efter == b
                      and rattelse.profilrevision == profilrevision(fore) and rattelse.datum <= datum)
            if not giltig:
                hinder.append(f'{id}: rättelsen stämmer inte med transaktionen eller kringgår en registrerad plan.')
            else:
                continue
        if nytt and not planer:
            hinder.append(f'{id}: registrera en plan och utvärdera riskbedömningen före införandet, eller dokumentera en felregistrering som rättelse.')
        for plan in planer:
            if not aktuell_planutvardering(rb, efter, plan, historik, datum):
                hinder.append(f'{plan.id}: genomför och bind en utvärdering till den aktuella planen före förändringen. Förnya därefter analysen och sakpröva igen.')
    if rattelse and rattelse.tjanst not in rb.tjanster:
        hinder.append('Rättelsen måste avse en registrerad tjänst.')
    elif rattelse:
        f=rb.tjanster[rattelse.tjanst].erbjuds_falt
        b=efter.uppgifter.get(f,Uppgift())
        if b.varde is not True or b.status != 'bekräftad' or b.inaktuell:
            hinder.append('Rättelsen måste ändra det felregistrerade nejet till ett bekräftat ja.')
    return tuple(hinder)
