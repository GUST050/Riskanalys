"""Verksamhetsfakta från uttryckliga källor, med synliga dataluckor."""
from riskanalys.dokument.rapportdelar_v10 import (
    avsnitt, tabell, rad, stycke, med_falttext, kallkod, faltref, uppgift, period_kalla, fakta, register, tjanstalias,
)


def faktaruta(rb, profil, b, historik):
    paket = b.omfattning.paket_id if b.omfattning else None
    myndighet = {'RP-RED-VG': 'Länsstyrelsen Västra Götaland', 'RP-RED-SKANE': 'Länsstyrelsen Skåne',
                 'RP-RED-STHLM': 'Länsstyrelsen Stockholm'}.get(paket, 'Okänt')
    rows = [rad(('Verksamhetsutövare', uppgift(rb, profil, 'P-ORG.namn')), (faltref(profil, 'P-ORG.namn'),)),
            rad(('Organisationsnummer / registrering', 'Okänt; strukturerat underlag saknas'), (kallkod('profil'),)),
            rad(('Tillsynsmyndighet', myndighet), (kallkod('bedomning', '/omfattning'),)),
            rad(('Avser / regelversion', f'{b.datum}; {b.regelbas_version}'), (kallkod('bedomning'),)),
            rad(('Dokumentansvarig / fastställd av', 'Dokumentansvarig: okänt. Fastställelse framgår av statusraden. Rollfördelningen finns i bilaga A.'), (kallkod('profil'),)),
            rad(('Senaste / nästa samlade utvärdering', f'{historik.senaste_utvardering() or "Okänt"} / {historik.nasta_genomgang() or "Okänt"}'), (kallkod('historik'),))]
    return avsnitt('F', 'Fakta och läsanvisning', (stycke(
        '0 sammanfattar tjänsternas risk; 1 beskriver verksamheten; 2 hoten; 3 faktorerna; '
        '4 risknivåer, scenarier och kontroller; 5 åtgärder och uppföljning. '
        'Bilaga A är fullständig analys och B1 är fullständigt underlag. Alla tre delarna granskas och fastställs tillsammans.',
        (kallkod('analysdokument'),)),), (tabell('faktaruta', 'Dokumentfakta', ('Uppgift', 'Underlag'), rows),))


def verksamhet(rb, profil):
    ids = ('P-ORG.namn', 'P-ORG.antal_anstallda', 'P-ORG.verksamhetsstallen', 'P-ORG.sateslan',
           'P-VERK.omsattning', 'P-KUND.antal_aktiva', 'P-KUND.antal_nya', 'P-KUND.antal_juridisk',
           'P-VERK.juniora_konsulter', 'P-VERK.tidigare_tillsyn', 'P-KUND.andel_nya',
           'P-KUND.andel_juridisk', 'P-ROLL.ffr_namn', 'P-ROLL.ansvarsfunktion')
    rows = [rad((rb.falt[id].etikett or rb.falt[id].fraga, uppgift(rb, profil, id), *period_kalla(profil, id)), (faltref(profil, id),))
            for id in ids if id in rb.falt]
    stycken = [stycke('Gemensamt period- och källregister för faktatabellerna (K anger lokal källa, P observationsperiod):\n'
        + register(profil), (kallkod('profil'),), lokal=True)]
    for id in ('P-BESK.verksamhet', 'P-BESK.kundtyper'):
        if id in profil.uppgifter:
            stycken.append(stycke(fakta(rb, profil, id), (faltref(profil, id),), lokal=True))
    return avsnitt('1.1', 'Verksamhetens fakta', stycken,
        (tabell('verksamhet', 'Bekräftade verksamhetsuppgifter', ('Uppgift', 'Värde', 'Period', 'Källa'), rows),))


def tjanster(rb, profil, b):
    rows, nej, okanda = [], [], []
    for id in rb.regelpaket[profil.byra.regelpaket].tjanster:
        t = rb.tjanster[id]
        erbjuds = uppgift(rb, profil, t.erbjuds_falt)
        if erbjuds == 'Nej':
            nej.append(id + ' ' + t.namn)
            continue
        if erbjuds != 'Ja':
            okanda.append(id + ' ' + t.namn)
            continue
        slug = t.erbjuds_falt.removesuffix('_erbjuds')
        refs = (kallkod('regelbas', '/tjanster/' + id), kallkod('profil'))
        arbets = t.beskrivning + '\n' + fakta(rb, profil, slug + '_arbetssatt')
        rows.append(rad((tjanstalias(rb, profil, id) + ' ' + id + ' ' + t.namn, arbets, fakta(rb, profil, slug + '_antal_kunder'),
            'Mandat: ' + fakta(rb, profil, slug + '_betalningsmandat') + '\nAttest: ' + fakta(rb, profil, slug + '_attest'),
            fakta(rb, profil, slug + '_bankinsyn'), fakta(rb, profil, slug + '_kanaler')), refs))
    return avsnitt('1.2', 'Produkter och tjänster', (
        stycke('Bekräftat ej erbjudna: ' + ('; '.join(nej) or 'inga') + '.', (kallkod('profil'), kallkod('regelbas', '/tjanster'))),
        stycke('Okänd omfattning: ' + ('; '.join(okanda) or 'inga') + '. Mandat, insyn och utförd kontroll är skilda uppgifter. '
               'Fulla arbetsmoment och lokal uppdragsprövning finns i bilaga A. Tjänstealias i tabellerna: '
               + ', '.join(tjanstalias(rb, profil, id) + '=' + id for id in rb.regelpaket[profil.byra.regelpaket].tjanster) + '.',
               (kallkod('profil'), kallkod('analys'), kallkod('regelbas', '/tjanster')))),
        (tabell('tjanster', 'Tjänsternas innehåll och arbetssätt',
            ('Tjänst', 'Innehåll / arbetssätt', 'Kunder', 'Mandat / attest', 'Insyn', 'Leverans'), rows),))


def hot(rb, profil, b, analys):
    ids = tuple(dict.fromkeys(h for id in rb.regelpaket[profil.byra.regelpaket].tjanster
        if uppgift(rb, profil, rb.tjanster[id].erbjuds_falt) != 'Nej' for h in rb.tjanster[id].hot))
    from riskanalys.regelverk.modeller import hot_dimensioner
    rows = []
    kallids = tuple(dict.fromkeys(k.kalla for id in ids for k in rb.hot[id].kallhanvisningar))
    for id in ids:
        h = rb.hot[id]
        refs = (kallkod('regelbas', '/hot/' + id),)
        locator = '; '.join('S' + str(kallids.index(k.kalla) + 1) + (f' s. {k.sida}' if k.sida else '') + (' ' + k.avsnitt if k.avsnitt else '')
                            for k in h.kallhanvisningar)
        rows.append(rad((id + ' ' + h.namn, '/'.join(hot_dimensioner(h)).upper(), h.beskrivning, locator), refs))
    pt = sum('pt' in hot_dimensioner(rb.hot[id]) for id in ids)
    tf = sum('tf' in hot_dimensioner(rb.hot[id]) for id in ids)
    return avsnitt('2', 'Hot', (stycke(f'{len(ids)} unika kataloghot för erbjudna eller ännu okända tjänster: {pt} med PT och {tf} med TF. '
        'Hot med både PT och TF räknas en gång. Katalogen beskriver möjliga tillvägagångssätt; lokal relevans och '
        'händelsekedjor prövas i 4.2–4.3 och bilaga A. Nivåmotivering och fulla källor finns i B1.',
        (kallkod('regelbas', '/hot'), kallkod('bedomning'))),
        stycke('Källnyckel: ' + '; '.join('S' + str(i) + '=' + id for i, id in enumerate(kallids, 1))
            + '. Fullständiga källposter finns i B1.', (kallkod('regelbas', '/kallor'),))),
        (tabell('hot', 'Hotbild', ('Hot', 'PT/TF', 'Beskrivning', 'Källor'), rows),))


def erfarenhet(rb, profil, analys):
    s = [med_falttext(id + ': ', fakta(rb, profil, id), '', (faltref(profil, id),))
         for id in ('P-VERK.antal_rapporter', 'P-VERK.antal_avbojanden', 'P-BESK.erfarenheter')]
    if analys:
        for i, p in enumerate(analys.gemensamma_verksamhetsposter):
            if p.slag == 'erfarenhet':
                s.append(stycke(f'{p.id}, {p.status}: {p.text}', (kallkod('analys', f'/gemensamma_verksamhetsposter/{i}'),), lokal=True))
    s.append(stycke('Noll rapporter eller avböjanden bevisar inte frånvaro av hot. Fulla tjänstevisa erfarenhetsprövningar finns i bilaga A.',
                    (kallkod('analys'), kallkod('bedomning'))))
    return avsnitt('2.1', 'Egen erfarenhet', s)


def rutiner(rb, profil, analys):
    rows = []
    if analys:
        for i, a in enumerate(analys.tjanster):
            for j, r in enumerate(a.rutinatgarder):
                rows.append(rad((a.tjanst + ' / ' + r.id, r.rutin_id or 'Saknas', r.rutin_version or 'Saknas',
                    r.rutinbelagg or 'Underlag saknas', r.ansvar or 'Saknas', r.utlosare_eller_frekvens or 'Saknas'),
                    (kallkod('analys', f'/tjanster/{i}/rutinatgarder/{j}'),)))
    return avsnitt('5.2', 'Koppling till rutinerna', (
        stycke(fakta(rb, profil, 'P-BESK.rutiner'), (faltref(profil, 'P-BESK.rutiner'),), lokal=True),),
        (tabell('rutiner', 'Faktiska rutinhänvisningar', ('Åtgärd', 'Rutindokument/ID', 'Version', 'Belägg', 'Ansvar', 'Utlösare/frekvens'), rows),))


def uppfoljning(rb, profil, historik):
    s = [stycke(id + ': ' + fakta(rb, profil, id), (faltref(profil, id),), lokal=True)
         for id in ('P-BEVAKNING.kallor', 'P-BEVAKNING.datum', 'P-BEVAKNING.ansvarig', 'P-BEVAKNING.relevans', 'P-BESK.uppdatering')]
    s.append(stycke('Registrerad källa är inte bevis för att den lästs. Senaste samlade utvärdering: '
        f'{historik.senaste_utvardering() or "Okänt"}; nästa genomgång: {historik.nasta_genomgang() or "Okänt"}. '
        'Avgränsad planutvärdering flyttar inte den samlade årsfristen.', (kallkod('historik'), kallkod('profil'))))
    return avsnitt('5.3', 'Utvärdering och omvärld', s)


def versionslogg(b, historik):
    rows = [rad((str(h.datum), h.typ, str(h.version) if h.version else 'Ej angiven', h.beskrivning),
        (kallkod('historik', f'/handelser/{i}'),)) for i, h in enumerate(historik.handelser)]
    return avsnitt('5.4', 'Versionslogg', (stycke(
        f'Analysens regelversion är {b.regelbas_version}. Leveransstatus framgår av statusraden. Historiken nedan återger bara registrerade händelser; '
        'dokumentets framställning är inte ett fastställelsebeslut. ' + ('Ingen historik registrerad.' if not rows else ''),
        (kallkod('historik'), kallkod('bedomning'))),),
        (tabell('historik', 'Registrerade händelser', ('Datum', 'Händelse', 'Version', 'Beskrivning'), rows),))
