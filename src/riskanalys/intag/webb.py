"""Ett privat formulär på loopback; ingen publik webbserver eller filrouter."""
import argparse
import json
import secrets
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs
from pydantic import ValidationError
from riskanalys.fel import RiskanalysFel
from riskanalys.intag import vyer
from riskanalys.intag.modeller import IntagSvar
from riskanalys.intag.tjanst import profilrevision
from riskanalys.intag.dokument import skapa_utkast, kontrollera_utkast, uppdatera_export
from riskanalys.profil.modeller import Period
from riskanalys.kommandon.skriv_kommando import valj_leverantor
from riskanalys.dokument.claude import STANDARDMODELL, STANDARDEFFORT


class Intagsserver(HTTPServer):
    def __init__(self,tjanst,port=0,leverantor=None,foretagsleverantor=None):
        if not 0<=port<=65535:raise RiskanalysFel('Porten ska vara 0–65535; 0 väljer en ledig port.')
        super().__init__(('127.0.0.1',port),Hantera)
        self.tjanst=tjanst
        self.prefix='/'+secrets.token_urlsafe(32)+'/'
        self.csrf=secrets.token_urlsafe(32)
        self.origin=f'http://127.0.0.1:{self.server_port}'
        self.url=self.origin+self.prefix
        self.leverantor=leverantor
        self.foretagsleverantor=foretagsleverantor
        self.bolagsverksleverantor=None
        self.utkast=None
        self.utkastrevision=None
        self.kompletteringar=()
        self._skrivformular=None
        self.rollforslag=''

    def skrivtoken(self, revision):
        if self._skrivformular is None or self._skrivformular[0] != revision:
            self._skrivformular=(revision,secrets.token_urlsafe(32))
        return self._skrivformular[1]

    def forbruka_skrivtoken(self, revision, token):
        if self._skrivformular is None or self._skrivformular[0] != revision or not secrets.compare_digest(token.encode(), self._skrivformular[1].encode()):
            raise RiskanalysFel('Skrivformuläret har redan använts eller är inaktuellt. Läs om översikten före ett nytt skrivförsök.')
        self._skrivformular=None

    def get_request(self):
        sock,addr=super().get_request();sock.settimeout(10);return sock,addr


def skapa_server(tjanst,port=0,leverantor=None,foretagsleverantor=None):
    return Intagsserver(tjanst,port,leverantor,foretagsleverantor)


class Hantera(BaseHTTPRequestHandler):
    server: Intagsserver
    def log_message(self,*args):pass

    def svara(self,status,innehall,typ='text/html; charset=utf-8',extra=None):
        body=innehall.encode() if isinstance(innehall,str) else innehall
        self.send_response(status)
        for k,v in {'Content-Type':typ,'Content-Length':str(len(body)), 'Cache-Control':'no-store',
                    'Referrer-Policy':'same-origin','X-Content-Type-Options':'nosniff',
                    'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'", **(extra or {})}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)

    def vag(self):
        if self.headers.get_all('Host') != [self.server.origin.removeprefix('http://')]:
            self.svara(403,'Otillåten värd.');return None
        u=urlsplit(self.path)
        if u.scheme or u.netloc or not u.path.startswith(self.server.prefix):
            self.svara(404,'Sidan finns inte.');return None
        try:
            query=parse_qs(u.query, max_num_fields=3)
        except ValueError:
            self.svara(400,'Ogiltig förfrågan.');return None
        if any(len(v)!=1 for v in query.values()) or set(query)-{'oversikt','falt'}:
            self.svara(400,'Ogiltig förfrågan.');return None
        return u.path.removeprefix(self.server.prefix),query

    def do_GET(self):
        vag=self.vag()
        if vag is None:return
        path,query=vag;s=self.server
        try:
            if path=='register' and not query:
                from riskanalys.intag.registervy import registersida
                self.svara(200,registersida(s));return
            if path=='tjanster' and not query and s.tjanst.finns():
                from riskanalys.intag.tjanstvy import tjanstesida
                self.svara(200,tjanstesida(s));return
            if path=='word':
                self.word();return
            if path:
                self.svara(404,'Sidan finns inte.');return
            if not s.tjanst.finns():html=vyer.grund(s)
            elif 'oversikt' in query:html=vyer.oversikt(s)
            else:html=vyer.fragesida(s,query.get('falt',[None])[0])
            self.svara(200,html)
        except RiskanalysFel as exc:self.svara(400,vyer.sida(s,'',exc))

    def formulardata(self,maxfalt=16):
        if self.headers.get_all('Origin') != [self.server.origin]:
            self.svara(403,'Otillåtet ursprung.');return None
        if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:
            self.svara(400,'Ogiltig formulärlängd.');return None
        try:n=int(self.headers['Content-Length'])
        except ValueError:self.svara(400,'Ogiltig formulärlängd.');return None
        if not 0<=n<=65536:self.svara(413,'Formuläret är för stort.');return None
        if self.headers.get_content_type()!='application/x-www-form-urlencoded':
            self.svara(400,'Skicka ett vanligt formulär.');return None
        try:
            raw=self.rfile.read(n)
            if len(raw)!=n:raise ValueError('Avbruten kropp')
            values=parse_qs(raw.decode('utf-8'),keep_blank_values=True,max_num_fields=maxfalt,strict_parsing=True)
            if any(len(v)!=1 for v in values.values()):raise ValueError('Dubbletter')
            data={k:v[0] for k,v in values.items()}
        except (ValueError,UnicodeError):self.svara(400,'Ogiltigt formulär.');return None
        if not secrets.compare_digest(data.get('csrf','').encode('utf-8'),self.server.csrf.encode('utf-8')):
            self.svara(403,'Formuläret hör inte till denna session. Läs om sidan.');return None
        return data

    def do_POST(self):
        vag=self.vag()
        if vag is None:return
        path,query=vag
        hanterare={k:getattr(self,'post_'+k) for k in ('skapa','svar','skriv','utvardera','registerhamta','registerimport','registerbekrafta','registersamlat','tjanster')}
        if path not in hanterare or query:
            self.svara(404,'Sidan finns inte.');return
        data=self.formulardata(32 if path in ('tjanster','skapa','registersamlat') else 16)
        if data is None:return
        try:
            hanterare[path](data)
            if path in ('skapa','svar','registerbekrafta','registersamlat','tjanster') and data.get('status','bekräftad')=='bekräftad' and data.get('roll','').strip():
                self.server.rollforslag=data['roll'].strip()
            destination='' if path=='registersamlat' and data.get('fortsatt')=='ja' else 'register' if path.startswith('register') else '?oversikt=1' if path in ('skriv','utvardera') else ''
            self.svara(303,'',extra={'Location':self.server.prefix+destination})
        except RiskanalysFel as exc:
            self.formularfel(path,data,str(exc))
        except ValidationError as exc:
            falt=', '.join('.'.join(str(x) for x in e['loc']) for e in exc.errors())
            self.formularfel(path,data,'Kontrollera värde och längd i fälten: '+falt+'.')
        except ValueError:
            fel='Word-utkastet kunde inte skapas. Kontrollera underlaget och sparade skrivförsök före ett nytt försök.' if path in ('skriv','utvardera') else 'Formuläret innehåller ett ogiltigt värde. Kontrollera de angivna uppgifterna.'
            self.formularfel(path,data,fel)

    def formularfel(self,path,data,fel):
        s=self.server
        status=409 if 'annan flik' in fel or 'Profilen har ändrats' in fel or 'redan använts' in fel else 400
        if path.startswith('register') or (path=='skapa' and data.get('bildsumma')):
            from riskanalys.intag.registervy import registersida
            html=registersida(s,data,fel)
        elif path=='tjanster':
            from riskanalys.intag.tjanstvy import tjanstesida
            html=tjanstesida(s,data,fel)
        elif path=='skapa':html=vyer.grund(s,data,fel)
        elif path=='svar':html=vyer.fragesida(s,data.get('falt'),data,fel)
        else:html=vyer.oversikt(s,fel)
        self.svara(status,html)

    def kontrollera_hamtningsdatum(self):
        if self.server.tjanst.finns() and self.server.tjanst.profil().byra.datum < date.today():
            raise RiskanalysFel('Nya registeruppgifter hämtas efter bedömningsdatumet. Befintligt underlag behålls; börja ett separat intag för en ny bedömning.')

    def post_registerhamta(self,data):
        from riskanalys.foretagsdata.scb import SCBLeverantor
        from riskanalys.foretagsdata.lagring import spara_bild
        self.kontrollera_hamtningsdatum()
        s=self.server
        nyckel=data.get('nyckel','').strip()
        provider=SCBLeverantor(nyckel=nyckel) if nyckel else (s.foretagsleverantor or SCBLeverantor())
        bild=provider.hamta(data.get('orgnr',''))
        if data.get('bolagsverket') == 'ja':
            from riskanalys.foretagsdata.bolagsverket import BolagsverketLeverantor
            from riskanalys.foretagsdata.samlad import komplettera_bolagsverket
            bild=komplettera_bolagsverket(bild,s.bolagsverksleverantor or BolagsverketLeverantor(),s.tjanst.mapp)
        spara_bild(s.tjanst.mapp,bild)
        if nyckel:s.foretagsleverantor=provider

    def post_registerimport(self,data):
        from riskanalys.foretagsdata.scb import tolka_scb
        from riskanalys.foretagsdata.lagring import spara_bild
        self.kontrollera_hamtningsdatum()
        try:raw=json.loads(data.get('jsontext',''))
        except (ValueError,RecursionError):raise RiskanalysFel('JSON-filen kunde inte läsas. Klistra in hela SCB-JSON-innehållet utan nycklar.') from None
        bild=tolka_scb(raw,data.get('orgnr',''),'lokal_json')
        spara_bild(self.server.tjanst.mapp,bild)

    def post_registerbekrafta(self,data):
        if data.get('ratt_byra')!='ja':raise RiskanalysFel('Kontrollera och bekräfta att uppgiften gäller rätt byrå och gäller nu.')
        from riskanalys.intag.register import bekrafta_register
        s=self.server
        bekrafta_register(s.tjanst,data.get('bildsumma',''),data.get('falt',''),data.get('roll',''),formulardatum(data,'datum'),data.get('revision',''))
        s.utkast=None;s.kompletteringar=()

    def post_registersamlat(self,data):
        if data.get('ratt_byra')!='ja':raise RiskanalysFel('Kontrollera och bekräfta att detta är rätt byrå och uppgifterna gäller nu.')
        from riskanalys.intag.register import bekrafta_samlat
        s=self.server
        bekrafta_samlat(s.tjanst,data,formulardatum(data,'datum'))
        s.utkast=None;s.kompletteringar=()

    def post_skapa(self,data):
        s=self.server
        dag=formulardatum(data,'datum')
        if not data.get('bildsumma'):
            if data.get('filial') not in ('ja','nej'):raise RiskanalysFel('Välj ja eller nej för utländsk filial.')
            s.tjanst.skapa(data.get('lan',''),data['filial']=='ja',dag,data.get('kalla',''),data.get('roll',''))
            return
        from riskanalys.foretagsdata.lagring import registerlas,las_bild
        with registerlas(s.tjanst.mapp):
            bild=las_bild(s.tjanst.mapp)
            if not bild or bild.summa!=data['bildsumma']:raise RiskanalysFel('Registerunderlaget har ändrats i en annan flik. Läs om sidan.')
            if data.get('ratt_byra')!='ja':raise RiskanalysFel('Kontrollera och bekräfta att detta är rätt byrå och uppgifterna gäller nu.')
            if dag<bild.hamtningsdag:raise RiskanalysFel('En aktuell registerbild kan inte styrka historisk bedömning. Börja manuellt med historiskt underlag.')
            if not bild.lan:raise RiskanalysFel('Säteslän saknas i registret. Börja intaget manuellt.')
            from riskanalys.intag.register import valda_falt,registersvar
            ids=valda_falt(data,bild)
            if 'P-ORG.sateslan' not in ids:
                raise RiskanalysFel('Godkänn säteslänet för att starta med registeruppgifter, eller börja manuellt.')
            if 'P-ORG.utlandsk_filial' in ids:
                filial=bild.forslag()['P-ORG.utlandsk_filial']
                filialkalla=bild.faltkalla('P-ORG.utlandsk_filial')
            else:
                if data.get('filial') not in ('ja','nej'):raise RiskanalysFel('Välj ja eller nej för utländsk filial, eller godkänn registerförslaget.')
                if not data.get('filialkalla','').strip():raise RiskanalysFel('Ange eget underlag för filialsvaret. SCB-bilden styrker inte detta.')
                filial=data['filial']=='ja'
                filialkalla=data['filialkalla']
            svar=registersvar(bild,tuple(id for id in ids if id not in ('P-ORG.sateslan','P-ORG.utlandsk_filial')),data.get('roll',''),date.today(),data)
            s.tjanst.skapa(bild.lan,filial,dag,bild.hanvisning(),data.get('roll',''),filialkalla=filialkalla,svar=svar)

    def post_tjanster(self,data):
        if data.get('hela_listan')!='ja':
            raise RiskanalysFel('Bekräfta hela tjänstelistan, eller besvara tjänsterna en i taget när du är osäker.')
        s=self.server
        ids=tuple(t.erbjuds_falt for t in s.tjanst.rb.tjanster.values())
        markers={k.removeprefix('tjanst_'):v for k,v in data.items() if k.startswith('tjanst_')}
        if set(markers)-set(ids) or any(v!='ja' for v in markers.values()):
            raise RiskanalysFel('Välj bara tjänster ur den visade listan. Läs om sidan.')
        from riskanalys.intag.underlag import vald_kalla
        p=s.tjanst.profil()
        kalla=vald_kalla(s.tjanst.rb,p,s.tjanst.rb.falt[ids[0]],data)
        svar=tuple(IntagSvar(falt=id,text='ja' if id in markers else 'nej',kalla=kalla,roll=data.get('roll',''),datum=formulardatum(data,'datum')) for id in ids)
        s.tjanst.spara_flera(svar,data.get('revision',''))
        s.utkast=None;s.kompletteringar=()

    def post_svar(self,data):
        a,b=data.get('period_fran',''),data.get('period_till','')
        if bool(a)!=bool(b):raise RiskanalysFel('Ange både periodens start och slut.')
        from riskanalys.intag.underlag import vald_kalla
        s=self.server;p=s.tjanst.profil()
        if data.get('revision')!=profilrevision(p):
            raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan.')
        f=s.tjanst.rb.falt.get(data.get('falt',''))
        if not f or not f.intag or f.alias_for or f.basfalt:
            raise RiskanalysFel('Välj en registrerad intagsfråga.')
        period=Period(fran=formulardatum(data,'period_fran'),till=formulardatum(data,'period_till')) if a else None
        kalla=vald_kalla(s.tjanst.rb,p,f,data,period) if data.get('status','bekräftad')=='bekräftad' else data.get('kalla','')
        svar=IntagSvar(falt=f.id,text=data.get('text',''),kalla=kalla,roll=data.get('roll',''),datum=formulardatum(data,'datum'),status=data.get('status','bekräftad'),motivering=data.get('motivering',''),period=period)
        self.server.tjanst.spara(svar,data.get('revision',''))
        self.server.utkast=None;self.server.kompletteringar=()

    def post_utvardera(self,data):
        from riskanalys.intag.utvardering import registrera_utvardering
        s=self.server
        registrera_utvardering(s.tjanst,formulardatum(data,'datum'),data.get('beskrivning',''),data.get('revision',''))
        tidigare=s.utkast
        s.utkast=None
        if tidigare and s.utkastrevision==profilrevision(s.tjanst.profil()):
            s.utkast=uppdatera_export(s.tjanst.mapp,s.tjanst.rb,tidigare)

    def post_skriv(self,data):
        s=self.server
        revision=profilrevision(s.tjanst.profil())
        if data.get('revision')!=revision:raise RiskanalysFel('Profilen har ändrats i en annan flik. Läs om sidan.')
        s.forbruka_skrivtoken(revision,data.get('skrivtoken',''))
        provider=s.leverantor or valj_leverantor(argparse.Namespace(leverantor='claude',modell=STANDARDMODELL,effort=STANDARDEFFORT))
        fil=skapa_utkast(s.tjanst.mapp,s.tjanst.rb,provider)
        if profilrevision(s.tjanst.profil())!=revision:raise RiskanalysFel('Profilen har ändrats under skrivningen. Skapa ett nytt utkast.')
        s.utkast=fil;s.utkastrevision=revision
        from riskanalys.dokument.export import utkastens_oklarheter
        from riskanalys.granskning.korning import GRANSKNING,granskningens_metadata
        from riskanalys.lagring.korningar import senaste_korning
        m=senaste_korning(s.tjanst.mapp,GRANSKNING,'granska')
        s.kompletteringar=utkastens_oklarheter(s.tjanst.mapp,granskningens_metadata(m)['utkast'])

    def word(self):
        s=self.server
        if not s.utkast:
            self.svara(404,'Skapa ett Word-utkast först.');return
        if s.utkastrevision != profilrevision(s.tjanst.profil()):
            raise RiskanalysFel('Utkastet bygger på äldre svar. Skapa ett nytt utkast.')
        kontrollera_utkast(s.tjanst.mapp, s.tjanst.rb, s.utkast)
        self.svara(200,s.utkast.read_bytes(),'application/vnd.openxmlformats-officedocument.wordprocessingml.document',extra={'Content-Disposition':'attachment; filename="allman-riskbedomning-UTKAST.docx"'})


def formulardatum(data,falt):
    try:return date.fromisoformat(data.get(falt,''))
    except ValueError:raise RiskanalysFel(f'Kontrollera datumfältet {falt}. Skriv datum som ÅÅÅÅ-MM-DD.') from None
