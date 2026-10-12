"""En samlad granskning av källbundna förslag, skild från registerbakgrunden."""
from datetime import date
from html import escape as e
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.lagring import las_bild
from riskanalys.intag.vyer import sida, dold, falt, val, foreslagen_roll
from riskanalys.profil.lagring import profilrevision

# SCB:s variabelbeskrivning 2026-10-09, s. 15 och 21–22. Bakgrund, inga profilvärden.
ANST = ['Uppgift saknas','0 anställda','1–4 anställda','5–9 anställda','10–19 anställda','20–49 anställda','50–99 anställda','100–199 anställda','200–499 anställda','500–999 anställda','1 000–1 499 anställda','1 500–1 999 anställda','2 000–2 999 anställda','3 000–3 999 anställda','4 000–4 999 anställda','5 000–9 999 anställda','10 000 eller fler anställda']
OMS = ['under 1','1–499','500–999','1 000–4 999','5 000–9 999','10 000–19 999','20 000–49 999','50 000–99 999','100 000–499 999','500 000–999 999','1 000 000–4 999 999','5 000 000–9 999 999','över 9 999 999']
ETIKETTER={'P-ORG.namn':'Byråns namn','P-ORG.sateslan':'Säteslän','P-ORG.verksamhetsstallen':'Verksamhetsställen','P-ORG.koncernmoder':'Är byrån yttersta moderföretag i en koncern?'}
SKATT={'0':'Aldrig registrerad','1':'Registrerad','9':'Avregistrerad'}
MOMS={**SKATT,'3':'Registrerad via representant'}
ARBGIV={**SKATT,'1':'Registrerad som vanlig arbetsgivare','2':'Registrerad som privatarbetsgivare','3':'Registrerad via representant','4':'Registrerad som ambassad eller konsulat'}
AGARKONTROLL={'10':'Statligt','20':'Kommunalt','30':'Regioner','41':'Privat svenskt utan koncern','42':'Privat svenskt med koncern','50':'Utländska'}


def visat(v):
    return ('Ja' if v else 'Nej') if isinstance(v,bool) else str(v)


def koncernforklaring():
    return '<p class="hint">SCB klassar företaget som Privat svenskt utan koncern. Därför föreslås nej. Kontrollera att klassningen fortfarande stämmer; uppgiftens senaste ändringsdatum saknas.</p>'


def klass(kod,tabell,enhet=''):
    if kod is None:return 'Saknas'
    try:return tabell[int(kod)] + enhet
    except (ValueError,IndexError):return f'Okänd klasskod {kod} – kontrollera hos SCB'


def skattestatus(kod,tabell):
    return 'Saknas' if kod is None else tabell.get(kod,f'Okänd kod {kod} – kontrollera hos SCB')


def hamtform(s,data=None,profil=None,bild=None):
    d=data or {}
    p=profil if profil is not None else s.tjanst.profil() if s.tjanst.finns() else None
    if p and p.byra.datum < date.today():
        return '<p>Bedömningsdatumet är före idag. Nya registerbilder kan inte styrka den historiska bedömningen. Befintligt registerunderlag och dina svar behålls; börja ett separat intag för en ny bedömning.</p>'
    html='<h2>Hämta företagsuppgifter</h2><p>Ange organisationsnumret. Granska sedan förslagen och godkänn de uppgifter du vill använda.</p>'
    html+=f'<form method="post" action="{s.prefix}registerhamta" autocomplete="off">'+dold('csrf',s.csrf)
    html+=falt('orgnr','Organisationsnummer för juridisk person',d.get('orgnr',bild.orgnr if bild else ''),required=True)
    html+='<details><summary>Ange eller byt SCB-nyckel</summary><p>Nyckeln används endast i denna lokala session. Den visas inte igen och sparas inte på disk. En nyckel som redan är satt i RISKANALYS_SCB_API_KEY används också.</p>'
    html+=falt('nyckel','Din personliga SCB-nyckel','','password')+'</details>'
    html+='<button>'+('Uppdatera från SCB' if bild else 'Hämta från SCB')+'</button></form>'
    html+='<p class="hint">Ingen nyckel ännu? <a href="https://registreraafr.scb.se/" rel="noreferrer" target="_blank">Registrera dig kostnadsfritt hos SCB</a>. Enskild firma kan fortsätta manuellt utan personnummer.</p>'
    html+='<details><summary>Importera en redan hämtad SCB-JSON-fil</summary><p>Klistra in SCB:s juridiska enhet, full. Ursprunget kan inte verifieras vid filimport. Inga nycklar eller lösenord ska ingå.</p>'
    html+=f'<form method="post" action="{s.prefix}registerimport" autocomplete="off">'+dold('csrf',s.csrf)
    html+=falt('orgnr','Filens organisationsnummer',d.get('orgnr',''),required=True,html_id='import-orgnr')
    html+='<label for="jsontext">SCB-JSON</label><textarea id="jsontext" name="jsontext" maxlength="50000" required></textarea><button>Importera som förslag</button></form></details>'
    return html


def ratt_byra():
    return '<label class="check"><input type="checkbox" name="ratt_byra" value="ja" required> Jag har kontrollerat att organisationsnummer och namn gäller rätt byrå och att de valda uppgifterna gäller nu.</label>'


def gemensamt(s,b,formid='start',profil=None,data=None):
    d=data or {}
    return dold('csrf',s.csrf)+dold('bildsumma',b.summa)+falt('roll','Din funktion som bekräftar uppgifterna',d.get('roll',foreslagen_roll(profil,getattr(s,'rollforslag',''))),required=True,html_id=formid+'-roll')+ratt_byra()


def forslagsrader(s,b,p=None,data=None):
    d=data or {};html=''
    for id,v in b.forslag().items():
        u=p.uppgifter.get(id) if p else None
        avviker=bool(u and u.varde is not None and u.varde!=v)
        klar=bool(p and p.ar_bekraftad(id) and not avviker)
        checked=d.get('val_'+id)=='ja' if data is not None else not avviker and not klar
        required='required' if p is None and id=='P-ORG.sateslan' else ''
        html+=f'<section class="proposal"><label class="check"><input type="checkbox" name="val_{e(id)}" value="ja" {"checked" if checked else ""} {required}><span>{e(ETIKETTER[id])}<br><strong>{e(visat(v))}</strong></span></label>'
        if u and u.varde is not None:
            html+=f'<p class="hint">Sparat svar: {e(str(u.varde))} ({e(u.status)}). '+('Avviker från sparat svar.' if avviker else 'Redan godkänt.' if klar else 'Behöver bekräftas igen.')+'</p>'
        if avviker:
            html+=f'<label class="check"><input type="checkbox" name="ersatt_{e(id)}" value="ja" {"checked" if d.get("ersatt_"+id)=="ja" else ""}> Jag vill ersätta det sparade svaret med detta förslag.</label>'
        if id=='P-ORG.verksamhetsstallen':html+='<p class="hint">Kontrollera att SCB:s registrerade arbetsställeantal motsvarar era faktiska verksamhetsställen.</p>'
        if id=='P-ORG.koncernmoder':html+=koncernforklaring()
        html+='</section>'
    return html


def inlineforslag(s,b,p,id):
    if id not in b.forslag():return ''
    u=p.uppgifter.get(id);v=b.forslag()[id]
    html=f'<section class="proposal"><h2>Redan hämtat från SCB</h2><p><strong>{e(visat(v))}</strong> · orgnr {e(b.orgnr)} · hämtad/importerad {e(str(b.hamtningsdag))}.</p>'
    if b.ursprung=='lokal_json':html+='<p>Lokalt importerat SCB-format – ursprung ej verifierat.</p>'
    if id=='P-ORG.verksamhetsstallen':html+='<p>Kontrollera att registrerade arbetsställen motsvarar era faktiska verksamhetsställen.</p>'
    if id=='P-ORG.koncernmoder':html+=koncernforklaring()
    html+=f'<form method="post" action="{s.prefix}registersamlat">'+gemensamt(s,b,'forslag',p)+dold('revision',profilrevision(p))+dold('val_'+id,'ja')+dold('datum',date.today())+dold('fortsatt','ja')
    if u and u.varde is not None and u.varde!=v:
        html+=f'<p>Avviker från ditt sparade svar: {e(str(u.varde))}.</p><label class="check"><input type="checkbox" name="ersatt_{e(id)}" value="ja" required> Ersätt mitt sparade svar med förslaget.</label>'
    return html+'<p class="hint">SCB-källa och bekräftelsedatum sparas automatiskt när du godkänner.</p><button>Godkänn registerförslaget och fortsätt</button></form></section><p>Du kan också ange ett eget svar nedan.</p>'


def registersida(s,data=None,fel=''):
    try:b=las_bild(s.tjanst.mapp)
    except RiskanalysFel as exc:return sida(s,'<h1>Företagsuppgifter</h1><p>Återställ registerunderlaget innan nya registerförslag används. Dina profilsvar är fortfarande sparade.</p>',str(exc))
    p=s.tjanst.profil() if s.tjanst.finns() else None;d=data or {}
    html='<p class="eyebrow">1. Hämta · 2. Godkänn · 3. Komplettera</p><h1>Granska företagsuppgifterna</h1>'
    if b:
        html+=f'<section class="identity"><h2>{e(b.namn)}</h2><p>{e(b.orgnr)} · {"SCB AFR API" if b.ursprung=="scb_api" else "Lokalt importerat SCB-format – ursprung ej verifierat"} · hämtad/importerad {e(str(b.hamtningsdag))}</p></section>'
        html+='<p>Markera uppgifterna du har kontrollerat. Ett godkännande sparar alla valda förslag. Dina andra svar behålls.</p>'
        if p or b.lan:
            endpoint='registersamlat' if p else 'skapa'
            html+=f'<form method="post" action="{s.prefix}{endpoint}">'+dold('revision',profilrevision(p) if p else '')
            html+=forslagsrader(s,b,p,data)
            if not p:
                html+='<h2>Komplettera det registret inte styrker</h2>'
                html+=val('filial','Är detta en filial till ett utländskt företag?',[('ja','Ja'),('nej','Nej')],d.get('filial',''))
                html+=falt('filialkalla','Eget underlag för filialsvaret (SCB-bilden styrker inte detta)',d.get('filialkalla',''),required=True)
            html+=gemensamt(s,b,'samlat',p,data)
            html+=falt('datum','Bekräftelsedatum' if p else 'Bedömningsdatum',d.get('datum',date.today()),'date',True)
            if p:html+=dold('fortsatt','ja')
            html+=f'<p><a href="{s.prefix}">Fortsätt intaget utan att ändra sparade svar</a></p>'
            html+='<p class="hint">Källa och datum kopplas till varje godkänt registerförslag. Ett ändrat säteslän kan göra tidigare följdsvar inaktuella.</p><button>Godkänn valda uppgifter och fortsätt</button></form>'
        else:html+=f'<p>Säteslän saknas. <a href="{s.prefix}">Börja med egna grunduppgifter</a>.</p>'
        bakgrund=[('SNI-koder (registrerad bransch)',', '.join(b.sni) or 'Saknas'),('Anställdas storleksklass',klass(b.anstalldaklass,ANST)),('Omsättningsklass',klass(b.omsattningsklass,OMS,' tkr')+f'; år {b.omsattningsar or "saknas"}'),('Juridisk form','Övriga aktiebolag (49)' if b.juridisk_form=='49' else 'Kod '+(b.juridisk_form or 'saknas')),('Företagsstatus',{'0':'Aldrig verksam','1':'Verksam enligt SCB:s registerkriterier','9':'Ej verksam enligt SCB:s registerkriterier'}.get(b.foretagsstatus,'Kod '+(b.foretagsstatus or 'saknas'))),('F-skatt enligt SCB',skattestatus(b.fskatt_status,SKATT)),('Moms enligt SCB',skattestatus(b.moms_status,MOMS)),('Arbetsgivarregistrering enligt SCB',skattestatus(b.arbetsgivar_status,ARBGIV))]
        bakgrund.append(('Ägarkontroll enligt SCB',skattestatus(b.agarkontroll,AGARKONTROLL)))
        html+='<details><summary>Registerbakgrund: bransch, storlek och registreringar</summary><table><tbody>'+''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k,v in bakgrund)+'</tbody></table><p>Storleksklasser är inte exakta antal eller belopp. SNI anger inte vilka tjänster ni faktiskt erbjuder. Skattestatus är registerbakgrund, inget belägg för utförda kontroller. SCB uppdaterar dessa registreringsstatusar veckovis.</p></details>'
        html+=f'<details><summary>Källa och sparat underlag</summary><p>{e(b.hanvisning())}</p><p>Uppgifternas senaste ändringsdatum saknas. Hämtningstid är inte uppgiftens giltighetsdatum. Bilden styrker inte historiska förhållanden.</p></details>'
        html+='<details><summary>Uppdatera eller importera registerunderlag</summary>'+hamtform(s,data,p,b)+'</details>'
    else:html+=hamtform(s,data,p)
    html+='<details><summary>Vilka fler uppgifter kan hämtas?</summary><p>Bolagsverket kan ge registrerad verksamhetsbeskrivning, organisationsform och digitala årsredovisningar. Hämtning därifrån kräver separat åtkomst och finns ännu inte i programmet. <a href="https://bolagsverket.se/apierochoppnadata/hamtaforetagsinformation/vardefulladatamangder/apiforvardefulladatamangder.5513.html" rel="noreferrer" target="_blank">Läs om Bolagsverkets avgiftsfria data</a>.</p><p>Kundantal, tjänsteintäkter och genomförda kontroller behöver underlag från byråns egen verksamhet. Dina egna underlag och statistikperioder kan återanvändas i intaget.</p></details>'
    return sida(s,html,fel)
