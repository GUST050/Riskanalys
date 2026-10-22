"""Privat plan- och gruppunderlag återges ordagrant, utan att tolkas till riskpoäng."""
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.profil.kombinationer import grupper_for_tjanst


def _original(text, refs):
    # Hela denna explicita underlagsåtergivning skyddas från platshållarsubstitution.
    return lokaltext(text, refs).model_copy(update={'literala_spann':((0,len(text)),)})


def _antal(u):
    if u.status != 'bekräftad' or u.inaktuell or type(u.varde) is not int:
        return 'okänt aktuellt antal'
    return str(u.varde)


def gruppstycken(rb, profil, tjanst):
    poster=[]
    for g in grupper_for_tjanst(rb,profil,tjanst):
        u=g.bas
        period=f'{u.period.fran}–{u.period.till}' if u.period else 'okänd period'
        text=(f'Kombinationsgrupp {g.id}: {g.beskrivning} Avgränsning: {g.avgransning}. '
              f'Population för både antal och bas: {g.population}. Antal {_antal(g.antal)}, bas {_antal(g.bas)}. '
              f'Period {period}. Källa: {u.kalla or g.antal.kalla or "saknas"}; bekräftat {u.datum or "okänt"}, av {u.bekraftad_av or "okänd"}. '
              f'Sårbarheter: {", ".join(g.sarbarheter)}. Grupper kan överlappa och får inte summeras till unika totaler. '
              'Bas 0 visar ingen låg risk. Gruppen är lokalt analysunderlag och ändrar inte motorutfallet före beslut om metod.')
        poster.append(_original(text,(tjanst,*g.sarbarheter,'LOKAL-GRUPP:'+g.id)))
    return tuple(poster)


def planunderlag(profil, historik):
    poster=[]
    for p in profil.tjansteplaner:
        g=p.genomforande
        status=(f'Genomförd {g.datum}, ansvarig {g.ansvarig}. Historisk plan; omprövas inte mot aktuella byråfakta. '
                f'Utvärderad {g.utvarderad}: {g.utvardering}. Historisk plansumma {g.plansumma}.' if g else
                'Planerad förändring; inget genomförande registrerat. Avsett datum avslutar inte planen.')
        text=(f'Plan {p.id}, tjänst {p.tjanst}, typ {p.typ}. {p.beskrivning} '
              f'Avsett införande: {p.avsett_inforande or "ej angivet"}. {status}')
        poster.append(_original(text,('LOKAL-PLAN:'+p.id,p.tjanst)))
        for id,u in p.uppgifter.items():
            poster.append(_original(f'Planantagande {p.id}, {id}: {u.varde}. Status {u.status}; källa {u.kalla or "saknas"}; '
                f'datum {u.datum or "okänt"}; ansvarig {u.bekraftad_av or "okänd"}; period {u.period or "ej angiven"}. '
                'Påverkar inte aktuell profils värden eller motorresultat.',('LOKAL-PLAN:'+p.id,id)))
    for h in historik.handelser:
        if h.plan_id or h.rattelse:
            text=f'{h.typ.capitalize()} {h.datum}: {h.beskrivning}.'
            if h.plan_id:
                text+=f' Plan-ID {h.plan_id}; bindning {h.plansumma}. Begränsad planutvärdering flyttar inte årsfristen.'
            if h.rattelse:
                r=h.rattelse
                text+=f' Tjänst {r.tjanst}; före {r.fore.varde}, efter {r.efter.varde}; källa {r.kalla}; ansvarig {r.ansvarig}; ursprunglig profilrevision {r.profilrevision}. Begärd rättelse; sparad profil visar om eftervärdet genomförts.'
            poster.append(_original(text,('KRV-LSF-006',)))
    return tuple(poster)
