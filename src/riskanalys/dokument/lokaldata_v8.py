"""Lokala profilfakta med egna perioder; inga tal eller råsvar går till AI."""
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.intag.fordelning import kan_ateranvandas
from riskanalys.dokument.analystabeller import lokalcell
from riskanalys.dokument.tabeller import rad, tabell
from riskanalys.profil.omfattning import kompatibilitetsvy


def inaktiv_frivillig_fordelning(rb, profil, id):
    """Returnerar orsaken när en frivillig fördelningsfråga inte ska ställas."""
    from riskanalys.intag.fordelning import faltkoppling
    koppling=faltkoppling(rb,id)
    if koppling is None:
        return None
    t,byrafalt,_=koppling
    p=kompatibilitetsvy(profil,rb)
    def aktuell_bas(falt_id):
        u=p.uppgifter.get(falt_id)
        return bool(u and p.ar_bekraftad(falt_id) and not u.inaktuell and u.status=='bekräftad'
            and type(u.varde) is int and u.varde>=0 and u.period is not None and u.kalla and u.kalla.strip()
            and u.bekraftad_av and u.bekraftad_av.strip() and u.datum is not None
            and u.datum<=p.byra.datum and u.period.till<=p.byra.datum)
    if not aktuell_bas(byrafalt):
        return None
    bas=p.uppgifter[byrafalt]
    if bas.varde==0:
        return 'byråns bekräftade faktorbas är 0'
    erbjuds=p.uppgifter.get(t.erbjuds_falt)
    if not (erbjuds and p.ar_bekraftad(t.erbjuds_falt) and erbjuds.varde is True):
        return None
    andra=[x for x in rb.tjanster.values() if x.id!=t.id]
    if any((u:=p.uppgifter.get(x.erbjuds_falt)) and p.ar_bekraftad(x.erbjuds_falt) and u.varde is True for x in andra):
        return None
    kund_id=t.erbjuds_falt.removesuffix('_erbjuds')+'_antal_kunder'
    if not aktuell_bas(kund_id) or p.uppgifter[kund_id].period!=bas.period:
        return None
    return 'endast en tjänst är bekräftat erbjuden'


def _giltigt_lokalt_fordelningssvar(rb, profil, id, u):
    from riskanalys.intag.fordelning import faltkoppling, underlagsbindning
    if not (u and profil.ar_bekraftad(id) and not u.inaktuell and u.status=='bekräftad'
            and type(u.varde) is int and u.varde>=0 and u.period is not None and u.kalla and u.kalla.strip()
            and u.bekraftad_av and u.bekraftad_av.strip() and u.datum is not None
            and u.datum<=profil.byra.datum and u.period.till<=profil.byra.datum):
        return False
    koppling=faltkoppling(rb,id)
    if koppling is None:
        return False
    t,byrafalt,_=koppling
    kund_id=t.erbjuds_falt.removesuffix('_erbjuds')+'_antal_kunder'
    bas=profil.uppgifter.get(byrafalt)
    kunder=profil.uppgifter.get(kund_id)
    return (u.underlagsbindning==underlagsbindning(rb,profil,id) and bas is not None and kunder is not None
        and u.period==bas.period==kunder.period and type(bas.varde) is int and type(kunder.varde) is int
        and u.varde<=min(bas.varde,kunder.varde))

TJANSTEFALT = ('arbetssatt', 'attest', 'betalningsmandat', 'bankinsyn', 'antal_kunder',
    'antal_riskbransch', 'antal_kontant', 'antal_utland_transaktion', 'antal_utland_agare',
    'kundtyper', 'kanaler', 'geografi', 'ovriga_risker', 'sektorsmotivering')


def uppgiftsrad(rb, profil, id):
    u = profil.uppgifter.get(id)
    f = rb.falt.get(id)
    namn = (f.etikett or f.fraga) if f else id
    inaktiv= inaktiv_frivillig_fordelning(rb,profil,id)
    if (f and f.intag and not f.intag.obligatorisk
            and (u is None or u.varde is None) and not (u and u.inaktuell)
            and not profil.ar_bekraftad(id)):
        from riskanalys.intag.fordelning import aktiverad
        if aktiverad(rb,profil,id):
            return rad(*(lokalcell(x, (id,)) for x in (namn,
                'Frivillig fördelning har inte lämnats; aktuellt antal är okänt.',
                'Ej lämnat', 'Frivillig fråga; inget svar registrerat')))
    if u is None:
        if inaktiv:
            return rad(*(lokalcell(x, (id,)) for x in (namn, 'Frivillig fördelning efterfrågas inte; '+inaktiv+'.', 'Ej efterfrågad', 'Frivillig fråga inaktiv')))
        return rad(*(lokalcell(x, (id,)) for x in (namn, 'Okänt. [VERIFIERA]', 'Period okänd', 'Källa saknas')))
    if inaktiv and u.varde is None and not u.inaktuell:
        return rad(*(lokalcell(x, (id,)) for x in (namn, 'Frivillig fördelning efterfrågas inte; '+inaktiv+'.', 'Ej efterfrågad', 'Frivillig fråga inaktiv')))
    varde = 'ja' if u.varde is True else 'nej' if u.varde is False else str(u.varde) if u.varde is not None else 'Okänt. [VERIFIERA]'
    giltigt_inaktivt=inaktiv and _giltigt_lokalt_fordelningssvar(rb,profil,id,u)
    if inaktiv and not giltigt_inaktivt:
        varde = ('Registrerat värde ' + varde + '; frivillig fördelning är inaktiv, men värdet saknar aktuell '
            'underlagsbindning eller annan bekräftelse. Det är inte verifierat som aktuell fördelning.')
    elif u.inaktuell or (not kan_ateranvandas(rb, profil, id) and not giltigt_inaktivt):
        varde = 'Registrerat värde ' + varde + '; inaktuellt eller oförenligt underlag. Aktuellt antal okänt. [VERIFIERA]'
    elif giltigt_inaktivt:
        varde += '; frivillig fördelning är inaktiv.'
    if u.status != 'bekräftad':
        varde += ' (status: ' + u.status + ')'
    period = f'{u.period.fran}–{u.period.till}' if u.period else 'Period okänd'
    kalla = f'Källa: {u.kalla or "saknas"}; registrerat/bekräftat {u.datum or "okänt"}. Status: {u.status}.'
    return rad(*(lokalcell(x, (id,)) for x in (namn, varde, period, kalla)))


def tjanstefakta(rb, profil, t):
    slug = rb.tjanster[t.tjanst].erbjuds_falt.removesuffix('_erbjuds')
    ids = tuple(slug+'_'+s for s in TJANSTEFALT if slug+'_'+s in rb.falt)
    perioder = {profil.uppgifter[id].period for id in ids if '_antal_' in id and id in profil.uppgifter}
    text = 'Antalen avser tjänstens egna kunder; fördelningarna är separata och styrker inget specifikt faktoröverlapp.'
    if len(perioder) > 1:
        text += ' Uppgifterna har olika perioder eller saknar period; ingen procent eller jämförbar fördelning härleds.'
    return (lokaltext(text, ids),), tabell(t.tjanst+'-lokala-fakta', 'Uppdrag, mandat, insyn och lokal fördelning',
        ('Uppgift', 'Värde', 'Period', 'Källa och status'), (uppgiftsrad(rb, profil, id) for id in ids))


def kundoverlapp(rb, profil, bedomning):
    """Ingen exakt överlappsuppgift kan härledas ur enbart tjänsternas marginaltal."""
    return lokaltext('Exakt kundöverlapp är okänt. Kundantalen får inte summeras till unika kunder; '
        'separata tjänste- och faktorantal visar inte vilka kunder som sammanfaller.', ('P-KUND.antal_aktiva',))
