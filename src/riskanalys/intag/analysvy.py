"""Guidad lokal analys i vanliga HTML-formulär utan egna lagringsvägar."""
from datetime import date
from html import escape as e
from typing import Literal, get_args, get_origin
from urllib.parse import urlencode

from riskanalys.analys.guide import arbetsborda, guideblock
from riskanalys.analys.modeller import Tjansteanalys
from riskanalys.analys.provning import BLOCKFALT, blocksumma, gallande_beslut
from riskanalys.intag.analysformular import RADER, faltlista, grundtyp, hamta_tjanst, referensval
from riskanalys.intag.vyer import dold, falt, val

NAMN = {
    'id': 'Lokalt ID för spårbara hänvisningar',
    'betalningsinsyn': 'Faktisk betalningsinsyn',
    'uppdragsprovning': 'Prövning av uppdragets hanterbarhet', 'leverantorer': 'Leverantörsprövningar',
    'scenarier': 'Scenarioanalyser', 'scenariokopplingar': 'Tjänstens val av delade scenarier',
    'sarbarhetsprovningar': 'Sårbarhetsprövningar', 'kontroller': 'Faktisk kontroll och effekt',
    'gap': 'Kunskapsluckor, brister och konflikter', 'rutinatgarder': 'Rutinåtgärder',
    'hot': 'Kataloghot', 'sarbarheter': 'Sårbarheter ur källkatalogen',
    'delanalyser': 'Arbetsmoment och delanalyser', 'omrade': 'Sårbarhetsområde',
    'relevans': 'Relevans för uppdraget', 'handelseforlopp': 'Konkret händelseförlopp',
    'arbetsmoment_och_befogenheter': 'Arbetsmoment och befogenheter',
    'egen_verifiering': 'Byråns egen verifiering', 'leverantorens_kontroller': 'Leverantörens faktiska kontroller',
    'brister_och_motstridigheter': 'Brister, motstridigheter och hantering',
    'tackning': 'Kontrollens bedömda scenariotäckning', 'rutin_id': 'Rutinens ID',
    'rutin_version': 'Rutinens version', 'atgard': 'Konkret åtgärd',
    'utlosare_eller_frekvens': 'Utlösare eller frekvens', 'uppfoljning': 'Datum för uppföljning',
    'klart_nar': 'När är åtgärden klar? (slutkriterium)', 'prioritet': 'Beslutad prioritet',
    'reduktionsprovning': 'Prövning av den faktiskt beräknade reduktionen',
    'sektorsjamforelse': 'Jämförelse med sektorsbilden', 'beslutsstatus': 'Förslag eller faktiskt beslut',
    'modellansvarig': 'Ansvarig för byråns modellriskhantering', 'utvarderad': 'Datum för byråns utvärdering',
    'nasta_genomgang': 'Nästa modellgenomgång', 'feluppfoljning': 'Hur verkliga fel följs upp',
    'beslutad_av': 'Vem fattade användningsbeslutet?', 'beslutsdatum': 'Datum för faktiskt användningsbeslut',
    'allvar': 'Felets allvar', 'atgard_och_omprovning': 'Dokumenterad rättning och omprövning',
    'exponering': 'Uppdrag, kunder, period och mandat',
    'delningsmotivering': 'Varför behövs eller behövs inte delanalyser?',
    'pt_motivering': 'Varför är motorns PT-utfall rimligt eller ifrågasatt?',
    'tf_motivering': 'Vilka TF-scenarier och osäkerheter behöver hanteras?',
    'samverkan': 'Hur förstärker eller begränsar faktorerna varandra?',
    'erfarenhetsprovning': 'Vad har rapportering, avböjanden och myndighetsbevakning lärt oss?',
    'leverantorsmotivering': 'Vilka leverantörsuppgifter och vilket eget ansvar har prövats?',
    'synliga_floden': 'Synliga flöden och underlag',
    'insynsluckor': 'Kända insynsluckor',
    'avsandare_och_mottagare': 'Kan verklig avsändare och mottagare identifieras?',
    'underlagens_tillforlitlighet': 'Underlagens tillförlitlighet',
    'kompetens_och_insyn': 'Kompetens, insyn och förmåga att hantera riskerna',
    'belagg': 'Registrerade beläggs-ID:n (kommaseparerade)',
    'exponeringsbelagg': 'Belägg för exponeringen (registrerade ID:n)',
    'erfarenhetsbelagg': 'Belägg för lärdomar och bevakning (registrerade ID:n)',
    'rackvidd': 'Källbeskriven räckvidd (ID:n)',
    'tillampning': 'Faktisk tillämpning i angivet scenario',
    'utfall': 'Belagt utfall och faktisk effekt',
    'kvarstar': 'Vad täcks inte eller förblir okänt?',
    'rutinbelagg': 'Registrerat dokumentbelägg för aktuell rutin',
    'handlingsalternativ': 'Mänskligt handlingsalternativ (utför ingen kundåtgärd)',
    'reduktionsmotivering': 'Stöds motorns faktiska reduktion av räckvidd och effekt?',
}


VALTEXT = {
    'bedomd': 'Bedömd insyn', 'ej_tillamplig': 'Ej tillämpligt', 'okand': 'Okänt – behöver prövas',
    'hanterbart': 'Hanterbart', 'kraver_atgard': 'Kräver åtgärd', 'kan_inte_hanteras': 'Kan inte hanteras',
    'okant': 'Okänt – behöver prövas', 'fortsatt': 'Fortsätt uppdrag', 'forstark': 'Förstärk förmågan',
    'begransa': 'Begränsa uppdrag', 'avboj': 'Avböj uppdrag', 'avsluta': 'Avsluta uppdrag',
    'forslag': 'Förslag', 'beslutad': 'Beslutad', 'foreslagen': 'Föreslagen', 'genomford': 'Genomförd',
    'relevant': 'Relevant', 'ej_relevant': 'Ej relevant', 'kund': 'Kunder', 'kanal': 'Distributionskanaler',
    'geo': 'Geografi', 'verk': 'Egen verksamhet', 'tjanst': 'Tjänst',
    'bedomd_tillracklig': 'Bedömd som tillräcklig för detta scenario', 'delvis': 'Delvis täckning',
    'saknas': 'Täckning saknas', 'kunskapslucka': 'Kunskapslucka', 'kontrollbrist': 'Kontrollbrist',
    'motstridigt_underlag': 'Motstridigt underlag', 'metodkonflikt': 'Metodkonflikt',
    'oppet': 'Öppet', 'atgardat': 'Åtgärdat', 'accepterad_kvarstaende_risk': 'Accepterad kvarstående risk',
    'vasentligt': 'Väsentligt', 'ovrigt': 'Övrigt', 'atgardat': 'Åtgärdat',
    'ej_reduktion': 'Motorn har inte sänkt nivån', 'motiverad': 'Reduktionen har belagt stöd',
    'ej_beslutad': 'Ej beslutad',
}


def _etikett(namn):
    return NAMN.get(namn, namn.replace('_', ' ').capitalize())


def _kontroll(namn, typ, varde, data, kataloger=None):
    text = data.get(namn, ', '.join(varde) if isinstance(varde, (tuple, list)) else '' if varde is None else str(varde))
    label = _etikett(namn.rsplit('.', 1)[-1])
    if kataloger and get_origin(typ) is tuple and namn.rsplit('.', 1)[-1] in kataloger:
        html = '<fieldset><legend>' + e(label.replace(' (kommaseparerade)', '')) + '</legend>' + dold(namn + '.urval', 'ja')
        ids = set(varde or ()) if namn + '.urval' not in data else None
        for i, (id, etikett) in enumerate(kataloger[namn.rsplit('.', 1)[-1]]):
            key = namn + '.val.' + str(i)
            checked = id in ids if ids is not None else data.get(key) == id
            html += '<label class="check"><input type="checkbox" name="' + e(key, quote=True) + '" value="' + e(id, quote=True) + '" ' + ('checked' if checked else '') + '><span>' + e(etikett) + '</span></label>'
        return html + '</fieldset>'
    if kataloger and namn.rsplit('.', 1)[-1] in kataloger:
        return val(namn, label, kataloger[namn.rsplit('.', 1)[-1]], text)
    if get_origin(typ) is Literal:
        return val(namn, label, [(v, VALTEXT.get(v, v.replace('_', ' ').capitalize())) for v in get_args(typ)], text)
    if typ is date:
        return falt(namn, label, text, 'date')
    if get_origin(typ) is tuple or namn.rsplit('.', 1)[-1] in ('id', 'rutin_id', 'rutin_version', 'rutinbelagg', 'ansvar'):
        return falt(namn, label, text)
    return f'<label for="{e(namn)}">{e(label)}</label><textarea id="{e(namn)}" name="{e(namn)}">{e(text)}</textarea>'


def _modellfalt(modell, prefix, objekt, data, kataloger=None):
    raw = objekt.model_dump(mode='json') if objekt else {}
    html = ''
    for namn, typ, _ in faltlista(modell, prefix):
        value = raw
        for key in namn.removeprefix(prefix).split('.'):
            value = value.get(key, '') if isinstance(value, dict) else ''
        html += _kontroll(namn, typ, value, data, kataloger)
    return html


def blockformular(paket, tjanst, nummer, *, prefix, csrf, revision, data=None, fel='', rb=None):
    """HTML-fragment. HTTP-routern äger sidram, Origin/CSRF och CAS-transaktionen."""
    a = hamta_tjanst(paket, tjanst)
    block = next((b for b in guideblock(a) if b.nummer == nummer), None)
    if block is None:
        from riskanalys.fel import RiskanalysFel
        raise RiskanalysFel('Välj ett av guidens sexton block.')
    d = data or {}
    kataloger = {**referensval(paket, a, rb), 'scenario': [(s.id, s.rubrik or s.id) for s in (*paket.gemensamma_scenarier, *a.scenarier)], 'rutinbelagg': [(b.id, (b.dokument or ', '.join(b.profilfalt)) + ' (' + b.id + ')') for b in paket.belagg]}
    if rb is not None and tjanst in rb.tjanster:
        kataloger['kontroll'] = [(id, rb.kontroller[id].namn + ' (' + id + ')') for id in rb.tjanster[tjanst].kontroller]
    html = f'<h1>{nummer}. {e(block.rubrik)}</h1><p>Tjänst: {e(tjanst)}. Förifyllnad är ett redigerbart ogranskat utkast.</p>'
    if nummer in (1, 3, 6, 9, 16):
        html += '<p class="hint">Beskriv förhållanden på byrå- och tjänstenivå för riskrapporten. Kundspecifika ärenden, rapportidentifierare och kontonummer hör till kundakten. Privata dokumentkopior används som belägg; deras innehåll infogas inte i Word-rapporten.</p>'
    if fel:
        html += f'<p class="error" role="alert">{e(str(fel))}</p>'
    html += f'<form method="post" action="{e(prefix, quote=True)}analysblock">'
    for n, v in [('csrf', csrf), ('revision', revision), ('tjanst', tjanst), ('nummer', nummer), ('visad_summa', d.get('visad_summa', blocksumma(paket, tjanst, nummer)))]:
        html += dold(n, v)
    if block.obligatorisk:
        html += '<p>Alltid obligatoriskt för erbjuden tjänst.</p>' + dold('aktivering', 'aktiv')
    else:
        html += val('aktivering', 'Varför ska blocket fördjupas eller avgränsas?', [('aktiv', 'Aktiverat'), ('ej_tillamplig', 'Ej tillämpligt – motivera'), ('okand', 'Okänt – komplettering behövs')], d.get('aktivering', block.aktivering))
    html += _kontroll('aktiveringsmotivering', str, block.motivering, d)
    for namn in BLOCKFALT[nummer]:
        if namn == 'scenariokopplingar':
            html += '<p>Gemensamma scenarier kräver ett separat uttryckligt samma/avviker-val per tjänst. Inget val bekräftas genom att spara detta block.</p>'
            continue
        html += f'<fieldset><legend>{e(_etikett(namn))}</legend>'
        if namn in RADER:
            poster = getattr(a, namn)
            for i in range(len(poster) + 1):
                ny = i == len(poster)
                radprefix = f'{namn}.{i}.'
                html += f'<details {"" if ny else "open"}><summary>{"Lägg till ny rad" if ny else "Rad " + str(i + 1)}</summary>'
                if ny:
                    html += val(radprefix + 'anvand', 'Lägg till denna rad vid sparning?', [('ja', 'Ja, lägg till')], d.get(radprefix + 'anvand', ''))
                else:
                    html += dold(radprefix + 'anvand', 'ja')
                    html += val(radprefix + 'ta_bort', 'Ta bort denna rad?', [('ja', 'Ja, ta bort')], d.get(radprefix + 'ta_bort', ''))
                html += _modellfalt(RADER[namn], radprefix, None if ny else poster[i], d, kataloger) + '</details>'
        else:
            typ = grundtyp(Tjansteanalys.model_fields[namn].annotation)
            value = getattr(a, namn)
            if hasattr(type(value), 'model_fields'):
                html += _modellfalt(type(value), namn + '.', value, d, kataloger)
            else:
                html += _kontroll(namn, typ, value, d, kataloger)
        if namn == 'kontroller' and rb is not None and tjanst in rb.tjanster:
            html += '<details><summary>Källbeskriven räckvidd och begränsningar</summary><p>Källbeskrivning är inte belägg för faktisk tillämpning eller effekt.</p>'
            for id in rb.tjanster[tjanst].kontroller:
                k = rb.kontroller[id]
                html += '<h3>' + e(k.namn) + '</h3>'
                for r in k.rackvidd:
                    if r.tjanst == tjanst:
                        html += '<p>' + e(r.id) + ': ' + e(r.kan_belagga) + '</p><p>Begränsningar: ' + e(r.begransningar) + '</p><p>Förutsättningar: ' + e(r.forutsattningar) + '</p>'
            html += '</details>'
        html += '</fieldset>'
    html += '<h2>Återanvänd registrerade belägg</h2><ul>'
    for b in paket.belagg:
        html += f'<li>{e(b.id)} · {e(str(b.datum))} · {e(str(b.period or "period saknas"))} · {e(", ".join(b.profilfalt) or b.dokument or "")}</li>'
    html += '</ul><p>Fakta rättas i intaget. Belägg kan återanvändas i flera block; ny uppladdning behövs inte.</p>'
    html += falt('forfattare', 'Ditt namn eller lokala person-ID', d.get('forfattare', a.forfattare or ''), required=True)
    html += '<button name="operation" value="spara">Spara utkast</button> <button name="operation" value="bekrafta">Spara och bekräfta visade svar</button></form><p>Blockbekräftelse är inte godkännande av tjänsteanalysen eller dokumentet.</p>'
    return html


def analysoversikt(paket, *, prefix):
    b = arbetsborda(paket)
    html = f'<h1>Lokal verksamhetsanalys</h1><p>{b.alltid} alltid obligatoriska block · {b.villkorade} aktiverade fördjupningar · {b.unika_scenarier} unika scenarier · {b.bekraftade_block} aktuellt bekräftade block.</p><p>{b.ateranvanda_belaggsreferenser} återanvända beläggsreferenser. Faktiskt nyskrivna kompletteringar är inte uppmätta.</p>'
    html += '<p>Modellriskunderlag och rapporter registreras en gång för hela analyspaketet.</p>'
    for t in paket.tjanster:
        html += f'<h2>{e(t.tjanst)}</h2>'
        html += '<p>Författare till aktuell svarsrevision: ' + e(t.forfattare or 'Saknas – programutkast') + '.</p>'
        beslut = gallande_beslut(paket, t.tjanst)
        if beslut:
            html += '<p>Senaste gällande lokala beslut: ' + ('Godkänd' if beslut.godkand else 'Underkänd') + '. Granskare: ' + e(beslut.namn) + ', ' + e(beslut.roll) + ', ' + e(str(beslut.datum)) + '. Granskad författare: ' + e(beslut.forfattare) + '.</p>'
        if beslut and beslut.godkand and beslut.egen_granskning:
            html += '<p class="tag">Samma person har skrivit och godkänt den lokala analysen</p>'
        html += '<ol>'
        for block in guideblock(t):
            href = prefix + 'analys?' + urlencode({'tjanst': t.tjanst, 'block': block.nummer})
            status = 'Aktuellt bekräftat' if block.bekraftad_summa == blocksumma(paket, t.tjanst, block.nummer) else 'Ogranskat eller inaktuellt'
            html += f'<li><a href="{e(href, quote=True)}">{e(block.rubrik)}</a>: {e(block.aktivering)} · {e(block.motivering)} · {status}</li>'
        html += '</ol>'
    return html


def scenarioformular(paket, tjanst, scenario, *, prefix, csrf, revision, data=None, fel=''):
    from riskanalys.analys.provning import scenariosumma
    from riskanalys.intag.analysformular import hamta_scenario
    a = hamta_tjanst(paket, tjanst)
    s = hamta_scenario(paket, scenario)
    d = data or {}
    html = f'<h2>Pröva gemensamt scenario för {e(tjanst)}</h2>'
    if fel:
        html += f'<p class="error" role="alert">{e(str(fel))}</p>'
    html += f'<h3>{e(s.rubrik)}</h3><p>{e(s.handelseforlopp)}</p><p>Relevans: {e(s.relevans)}. {e(s.motivering)}</p><p>Belägg: {e(", ".join(s.belagg))}</p>'
    html += f'<h3>Tjänstens förhållanden</h3><p>{e(a.exponering)}</p><p>Arbetsmoment: {e(a.delningsmotivering)}</p><p>{e("; ".join(d.arbetsmoment_och_befogenheter for d in a.delanalyser))}</p>'
    html += f'<form method="post" action="{e(prefix, quote=True)}analysscenario">'
    for n, v in [('csrf', csrf), ('revision', revision), ('tjanst', tjanst), ('scenario', scenario), ('visad_summa', d.get('visad_summa', scenariosumma(s)))]:
        html += dold(n, v)
    html += val('tillampning', 'Gäller samma analys eller behövs en lokal avvikelse?', [('samma', 'Samma – jag har prövat tjänstens förhållanden'), ('avviker', 'Avviker – använd lokal variant')], d.get('tillampning', ''))
    html += val('lokal_scenario', 'Lokal variant vid avvikelse', [(s.id, s.rubrik or s.id) for s in a.scenarier], d.get('lokal_scenario', ''))
    html += _kontroll('motivering', str, '', d)
    html += falt('forfattare', 'Ditt namn eller lokala person-ID', d.get('forfattare', a.forfattare or ''), required=True)
    return html + '<button>Bekräfta detta visade scenario för tjänsten</button></form><p>Valet godkänner inte hela analysen.</p>'


def analyssida(s, query=None, data=None, fel=''):
    """En tjänst i taget, med samma status/brister som CLI."""
    from riskanalys.analys.tjanst import Analystjanst
    from riskanalys.fel import RiskanalysFel
    from riskanalys.intag.vyer import sida
    q = query or {}
    d = data or {}
    t = Analystjanst(s.tjanst.mapp, s.tjanst.rb)
    try:
        status = t.status()
    except RiskanalysFel as exc:
        return sida(s, '<h1>Lokal verksamhetsanalys</h1><p>' + e(str(exc)) + '</p><p>Komplettera intaget och skapa ett skrivutkast före lokal analys. Härifrån görs inga AI-anrop.</p>', fel)
    paket = status.paket
    html = '<nav><a href="' + e(s.prefix, quote=True) + 'analys">Analysöversikt</a><a href="' + e(s.prefix, quote=True) + 'analys?forslag=ja">Jämför ny förifyllnad</a><a href="' + e(s.prefix, quote=True) + 'analys?modellrisk=ja">Gemensamt modellriskunderlag</a></nav>'
    if paket is None:
        html += '<h1>Starta lokal verksamhetsanalys</h1><p>Programmet förifyller redigerbara ogranskade svar från bekräftad profil och motorutfall. Inga belägg för faktisk effekt eller mänskliga godkännanden hittas på.</p>'
        html += f'<form method="post" action="{e(s.prefix, quote=True)}analysstart">' + dold('csrf', s.csrf) + dold('revision', '') + '<button>Starta ogranskat analysutkast</button></form>'
        return sida(s, html, fel)
    if 'forslag' in q:
        nytt = t.forslag()
        html += '<h1>Jämför ny förifyllnad</h1><p>Manuella svar bevaras; aktuella profilbelägg uppdateras med källa, datum och period och nya tjänster får ogranskade utkast. En förnyad bindning upphäver tidigare block- och scenariobekräftelser; läs och pröva dem mot aktuella fakta igen.</p>'
        for a in nytt.tjanster:
            gammal = next((x for x in paket.tjanster if x.tjanst == a.tjanst), None)
            html += '<h2>' + e(a.tjanst) + '</h2><h3>Sparad exponering</h3><p>' + e(gammal.exponering if gammal else 'Saknas') + '</p><h3>Aktuellt förslag</h3><p>' + e(a.exponering) + '</p>'
        html += f'<form method="post" action="{e(s.prefix, quote=True)}analysfornya">' + dold('csrf', s.csrf) + dold('revision', d.get('revision', status.revision)) + '<label class="check"><input type="checkbox" name="jamfort" value="ja" required> Jag har jämfört sparade svar och aktuellt underlag</label><button>Förnya bindning och profilbelägg, bevara manuella svar</button></form>'
    elif 'modellrisk' in q:
        html += modellriskformular(paket, prefix=s.prefix, csrf=s.csrf, revision=status.revision, data=data)
    elif 'gemensamt' in q:
        html += gemensamtformular(paket, q['gemensamt'][0], prefix=s.prefix, csrf=s.csrf, revision=status.revision, data=data, rb=s.tjanst.rb)
    elif 'tjanst' in q:
        tid = q['tjanst'][0]
        a = hamta_tjanst(paket, tid)
        tb = next((b for b in status.bedomning.tjanster if b.tjanst == tid), None)
        html += '<h2>' + e(s.tjanst.rb.tjanster[tid].namn) + '</h2>'
        if tb:
            html += '<p>Motorns utfall (rättas inte här): Inneboende PT ' + e(tb.inneboende.risk if tb.inneboende else 'okänt') + ', kvarstående ' + e(tb.kvarstaende or 'okänt') + ', TF ' + e(tb.terrorfinansiering.risk if tb.terrorfinansiering else 'okänt') + '.</p>'
        html += '<p>Bekräftade fakta och perioder visas i <a href="' + e(s.prefix, quote=True) + '?oversikt=1">intagets svar</a>. Ändra sakuppgifter där.</p><nav>'
        for b in guideblock(a):
            html += '<a href="' + e(s.prefix + 'analys?' + urlencode({'tjanst': tid, 'block': b.nummer}), quote=True) + '">' + str(b.nummer) + '</a> '
        html += '<a href="' + e(s.prefix + 'analys?' + urlencode({'tjanst': tid, 'granska': 'ja'}), quote=True) + '">Granska tjänsteanalysen</a></nav>'
        if 'scenario' in q:
            html += scenarioformular(paket, tid, q['scenario'][0], prefix=s.prefix, csrf=s.csrf, revision=status.revision, data=data)
        elif 'granska' in q:
            html += granskningsformular(paket, tid, prefix=s.prefix, csrf=s.csrf, revision=status.revision, data=data)
        else:
            try:
                n = int(q.get('block', ['1'])[0])
            except ValueError:
                raise RiskanalysFel('Välj ett av guidens sexton block.') from None
            html += blockformular(paket, tid, n, prefix=s.prefix, csrf=s.csrf, revision=status.revision, data=data, rb=s.tjanst.rb)
            if n == 6:
                html += '<h2>Gemensamma scenarier att pröva</h2><ul>'
                for scenario in paket.gemensamma_scenarier:
                    if set(scenario.hot) <= set(s.tjanst.rb.tjanster[tid].hot):
                        href = s.prefix + 'analys?' + urlencode({'tjanst': tid, 'scenario': scenario.id})
                        html += '<li><a href="' + e(href, quote=True) + '">' + e(scenario.rubrik or scenario.id) + '</a> – välj samma eller avviker</li>'
                html += '</ul>'
    else:
        html += analysoversikt(paket, prefix=s.prefix)
        html += '<h2>Redigera delade scenarier en gång</h2><ul>'
        for scenario in paket.gemensamma_scenarier:
            href = s.prefix + 'analys?' + urlencode({'gemensamt': scenario.id})
            html += '<li><a href="' + e(href, quote=True) + '">' + e(scenario.rubrik or scenario.id) + '</a></li>'
        html += '</ul><p>Gemensam ändring gör beroende tjänsteval inaktuella.</p>'
    html += '<h2>Aktuella hinder för analysgodkännande</h2><p>Godkännande av en tjänst prövar också paketets gemensamma brister. Sidan visar hela prövningen; en partiell paketattest utlovas inte.</p><ul>'
    html += ''.join('<li>' + e(h) + '</li>' for h in status.brister) + '</ul>'
    if not status.brister:
        html += '<p>Inga strukturella brister upptäckta. Riktigheten behöver fortfarande granskas av en människa.</p>'
    return sida(s, html, fel)


def granskningsformular(paket, tjanst, *, prefix, csrf, revision, data=None):
    a = hamta_tjanst(paket, tjanst)
    d = data or {}
    html = '<h1>Granska tjänsteanalysen</h1><p>Författare: ' + e(a.forfattare or 'Saknas') + '. Beslutet gäller exakt aktuell revision, svar och underlag.</p>'
    for b in guideblock(a):
        html += '<details open><summary>' + str(b.nummer) + '. ' + e(b.rubrik) + '</summary>'
        for namn in BLOCKFALT[b.nummer]:
            html += '<p><strong>' + e(_etikett(namn)) + '</strong>: ' + e(_lasbar(getattr(a, namn))) + '</p>'
        html += '</details>'
    html += f'<form method="post" action="{e(prefix, quote=True)}analysbeslut">' + dold('csrf', csrf) + dold('revision', d.get('revision', revision)) + dold('tjanst', tjanst)
    html += falt('namn', 'Granskarens namn eller lokala person-ID', d.get('namn', ''), required=True)
    html += falt('roll', 'Granskarens roll', d.get('roll', ''), required=True)
    html += falt('datum', 'Faktiskt beslutsdatum', d.get('datum', ''), 'date', True)
    html += _kontroll('kommentar', str, '', d)
    return html + '<button name="beslut" value="godkann">Godkänn denna tjänsteanalys</button><button name="beslut" value="underkann">Underkänn och ange kommentar</button></form><p>Beslutet fastställer inte dokumentet och utför inga kundåtgärder.</p>'


def _lasbar(value):
    if hasattr(value, 'model_dump'):
        return '; '.join(_etikett(k) + ': ' + _lasbar(v) for k, v in value.model_dump().items())
    if isinstance(value, dict):
        return '; '.join(_etikett(k) + ': ' + _lasbar(v) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return ' | '.join(_lasbar(v) for v in value) or 'Saknas / ej tillämpligt'
    return VALTEXT.get(value, str(value)) if isinstance(value, str) else str(value or '')


def gemensamtformular(paket, scenario, *, prefix, csrf, revision, data=None, rb=None):
    from riskanalys.analys.modeller import Scenarioanalys
    from riskanalys.analys.provning import scenariosumma
    from riskanalys.intag.analysformular import hamta_scenario
    a = hamta_scenario(paket, scenario)
    kataloger = referensval(paket, Tjansteanalys(tjanst=''), rb)
    if rb:kataloger['hot'] = tuple((id, rb.hot[id].namn) for id in a.hot)
    d = data or {}
    html = '<h1>Redigera gemensamt scenario</h1><p>En ändring upphäver beroende samma/avviker-bekräftelser. Tjänsternas faktiska kontrolltillämpning granskas separat.</p>'
    html += f'<form method="post" action="{e(prefix, quote=True)}analysgemensamt">'
    for n, v in [('csrf', csrf), ('revision', d.get('revision', revision)), ('scenario', scenario), ('visad_summa', d.get('visad_summa', scenariosumma(a)))]:
        html += dold(n, v)
    for namn, typ, _ in faltlista(Scenarioanalys):
        if namn in ('id', 'delanalyser'):
            continue
        html += _kontroll(namn, typ, getattr(a, namn), d, kataloger)
    html += falt('forfattare', 'Ditt namn eller lokala person-ID', d.get('forfattare', ''), required=True)
    return html + '<button>Spara gemensamt scenario som ogranskat utkast</button></form>'


def modellriskformular(paket, *, prefix, csrf, revision, data=None):
    d = data or {}
    u = paket.modellrisk
    html = '<h1>Gemensamt modellriskunderlag</h1><p>Projektet levererar versionsbunden modellrapport. Byrån prövar relevans, begränsningar och användning samt följer upp verkliga fel; byrån skriver inget nytt valideringsfacit.</p>'
    html += '<p>Importera rapporttrippeln en gång med <code>riskanalys analys BYRA --modellrapport MAPP --revision SUMMA --datum ÅÅÅÅ-MM-DD</code>. Registrera byråns rutin med <code>--belagg FIL --belagg-id ID --datum ÅÅÅÅ-MM-DD --revision SUMMA</code>. Aktuell registersumma: <code>' + e(revision) + '</code>. Webben öppnar inga godtyckliga lokala filer.</p>'
    html += f'<form method="post" action="{e(prefix, quote=True)}analysmodellrisk">' + dold('csrf', csrf) + dold('revision', d.get('revision', revision))
    for namn in ('modellansvarig', 'utvarderad', 'nasta_genomgang', 'feluppfoljning', 'beslutad_av', 'beslutsdatum'):
        v = getattr(u, namn) if u else ''
        html += _kontroll(namn, date if namn in ('utvarderad', 'nasta_genomgang', 'beslutsdatum') else str, v, d)
    rutin = next((b.id for b in paket.belagg if u and b.dokument == u.rutin.fil), '')
    html += val('rutinbelagg', 'Registrerat dokumentbelägg för byråns modellriskrutin', [(b.id, b.id + ': ' + (b.dokument or '')) for b in paket.belagg if b.dokument and not b.id.startswith('modell:')], d.get('rutinbelagg', rutin))
    html += val('godkand', 'Har byrån faktiskt beslutat om användningen?', [('ja', 'Ja – faktiskt användningsbeslut finns'), ('nej', 'Nej – användning är inte godkänd')], d.get('godkand', ''))
    html += '<button>Registrera lokalt modellriskunderlag</button></form>'
    if u:
        html += modellfelformular(paket, prefix=prefix, csrf=csrf, revision=revision, data=data)
    return html



def modellfelformular(paket, *, prefix, csrf, revision, data=None):
    from riskanalys.drift.modellrisk import Modellfel
    d = data or {}
    html = '<h2>Löpande modellfel och omprövning</h2><p>Registrera verkliga observationer, rättning och omprövning. Ett ändrat felregister kräver ett nytt lokalt användningsbeslut.</p>'
    options = {'belagg': [(b.id, 'Registrerad dokumentkopia · ' + str(b.datum) + ' (' + b.id + ')') for b in paket.belagg if b.dokument]}
    for fel in (*paket.modellrisk.fel, None):
        current = fel is not None
        postdata = d if (d.get('id', '') == fel.id if current else d.get('id', '') not in {f.id for f in paket.modellrisk.fel}) else {}
        html += '<details><summary>' + (e(fel.id + ': ' + fel.beskrivning) if current else 'Registrera nytt modellfel') + '</summary>'
        html += f'<form method="post" action="{e(prefix, quote=True)}analysmodellfel">' + dold('csrf', csrf) + dold('revision', postdata.get('revision', revision))
        if current:
            html += dold('id', fel.id)
        else:
            html += falt('id', 'Fel-ID', postdata.get('id', ''), required=True)
        for namn, typ, _ in faltlista(Modellfel):
            if namn == 'id' or namn.startswith('belagg.'):
                continue
            if namn == 'belagg':
                ids = tuple(b.id for b in paket.belagg if current and any(b.dokument == r.fil and b.kontrollsumma == r.kontrollsumma for r in fel.belagg))
                html += _kontroll(namn, tuple[str, ...], ids, postdata, options)
            else:
                html += _kontroll(namn, typ, getattr(fel, namn) if current else '', postdata)
        html += '<button>Registrera feluppföljning</button></form></details>'
    return html
