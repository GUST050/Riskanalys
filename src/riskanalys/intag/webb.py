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
from riskanalys.intag.dokument import skapa_utkast, las_utkast, uppdatera_export
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
        self.omfattningsfil=None
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
            query=parse_qs(u.query, max_num_fields=8 if u.path==self.server.prefix+'analys' else 4)
        except ValueError:
            self.svara(400,'Ogiltig förfrågan.');return None
        tillatna = {'plan','tjanst'} if u.path == self.server.prefix+'planering' else {'grupp'} if u.path == self.server.prefix+'samlat' else {'tjanst','block','scenario','granska','gemensamt','modellrisk','forslag','overfor','byraanalys','post','slag','tillampningar','genomgang','tackning','ursprung','hot','dimension','riskled'} if u.path == self.server.prefix+'analys' else {'oversikt','falt'}
        if any(len(v)!=1 for v in query.values()) or set(query)-tillatna:
            self.svara(400,'Ogiltig förfrågan.');return None
        if ('dimension' in query and query['dimension'][0] not in ('pt','tf')
                or 'ursprung' in query and query['ursprung'][0] not in ('gemensam','lokal')
                or 'riskled' in query and query['riskled'][0] not in ('inneboende','kvarstaende')
                or 'slag' in query and query['slag'][0] not in ('sarbarhet','verksamhet')):
            self.svara(400,'Välj giltigt område och dimension ur analysvyn.');return None
        return u.path.removeprefix(self.server.prefix),query

    def do_GET(self):
        vag=self.vag()
        if vag is None:return
        path,query=vag;s=self.server
        try:
            if path=='planering' and s.tjanst.finns():
                from riskanalys.intag.planeringsvy import planeringssida
                self.svara(200,planeringssida(s,query));return
            if path=='samlat' and s.tjanst.finns():
                from riskanalys.intag.samladvy import samladsida
                self.svara(200,samladsida(s,query.get('grupp',[None])[0]));return
            if path=='analys' and s.tjanst.finns():
                from riskanalys.intag.analysvy import analyssida
                self.svara(200,analyssida(s,query));return
            if path=='register' and not query:
                from riskanalys.intag.registervy import registersida
                self.svara(200,registersida(s));return
            if path=='tjanster' and not query and s.tjanst.finns():
                from riskanalys.intag.tjanstvy import tjanstesida
                self.svara(200,tjanstesida(s));return
            if path=='omfattningsword' and not query:
                if not s.omfattningsfil:self.svara(404,'Skapa ett ofullständigt omfattningsunderlag först.');return
                from riskanalys.dokument.omfattningsutkast import las_omfattningsunderlag
                body=las_omfattningsunderlag(s.tjanst.mapp,s.tjanst.rb,s.omfattningsfil)
                self.svara(200,body,'application/vnd.openxmlformats-officedocument.wordprocessingml.document',extra={'Content-Disposition':'attachment; filename="'+s.omfattningsfil.name+'"'});return
            if path in ('word','underlag'):
                self.word(underlag=path=='underlag');return
            if path:
                self.svara(404,'Sidan finns inte.');return
            if not s.tjanst.finns():html=vyer.grund(s)
            elif 'oversikt' in query:html=vyer.oversikt(s)
            else:html=vyer.fragesida(s,query.get('falt',[None])[0])
            self.svara(200,html)
        except RiskanalysFel as exc:self.svara(400,vyer.sida(s,'',exc))

    def formulardata(self,maxfalt=16,maxbytes=65536):
        if self.headers.get_all('Origin') != [self.server.origin]:
            self.svara(403,'Otillåtet ursprung.');return None
        if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:
            self.svara(400,'Ogiltig formulärlängd.');return None
        try:n=int(self.headers['Content-Length'])
        except ValueError:self.svara(400,'Ogiltig formulärlängd.');return None
        if not 0<=n<=maxbytes:self.svara(413,'Formuläret är för stort.');return None
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
        hanterare={k:getattr(self,'post_'+k) for k in ('omfattningsunderlag','plan','planutvardera','plangenomforande','planaterkalla','kombinationsgrupp','erbjudanderattelse','skapa','svar','samlat','skriv','uppdaterautkast','utvardera','registerhamta','registerimport','registerbekrafta','registersamlat','tjanster','analysgemensampost','analystillampning','analysbekraftatillampningar','analysbekraftabyraunderlag','analysbekraftatjansteunderlag','analystackning','analysstart','analysoverfor','analysfornya','analysblock','analysscenario','analysgemensamt','analysbeslut','analysmodellrisk','analysmodellfel')}
        if path not in hanterare or query:
            self.svara(404,'Sidan finns inte.');return
        from riskanalys.intag.flervalsvy import flervalsgrans
        maxfalt=512 if path.startswith('analys') or path=='plan' else 128 if path=='samlat' else 64 if path=='tjanster' else 32 if path in ('skapa','registersamlat') else 17+flervalsgrans(self.server.tjanst.rb) if path=='svar' else 16
        data=self.formulardata(maxfalt,maxbytes=1024*1024 if path=='samlat' else 65536)
        if data is None:return
        try:
            if hanterare[path](data) is False:return
            if path in ('skapa','svar','samlat','registerbekrafta','registersamlat','tjanster') and data.get('status','bekräftad')=='bekräftad' and data.get('roll','').strip():
                self.server.rollforslag=data['roll'].strip()
            if path.startswith('analys'):
                from urllib.parse import urlencode
                destination='analys'
                if path=='analysblock':destination+='?'+urlencode({'tjanst':data.get('tjanst',''),'block':data.get('nummer','')})
                elif path=='analysbekraftatjansteunderlag':destination+='?'+urlencode({'tjanst':data.get('tjanst',''),'genomgang':'ja'})
                elif path=='analysbekraftabyraunderlag':destination+='?byraanalys=ja'
                elif path=='analysgemensampost':destination+='?'+urlencode({'byraanalys':'ja','post':data.get('id',''),'slag':data.get('typ','')})
                elif path in ('analystillampning','analysbekraftatillampningar','analysbekraftabyraunderlag','analysbekraftatjansteunderlag','analystackning'):destination+='?'+urlencode({'tjanst':data.get('tjanst',''),'tillampningar':'ja'})
                elif path in ('analysscenario','analysbeslut'):destination+='?'+urlencode({'tjanst':data.get('tjanst',''),'granska':'ja'})
            else:
                destination='' if path=='registersamlat' and data.get('fortsatt')=='ja' else 'register' if path.startswith('register') else '?oversikt=1' if path in ('omfattningsunderlag','skriv','uppdaterautkast','utvardera') else ''
                if path in ('plan','planutvardera','plangenomforande','planaterkalla','kombinationsgrupp','erbjudanderattelse'):
                    destination='planering'
            self.svara(303,'',extra={'Location':self.server.prefix+destination})
        except RiskanalysFel as exc:
            self.formularfel(path,data,str(exc))
        except ValidationError as exc:
            falt=', '.join('.'.join(str(x) for x in e['loc']) for e in exc.errors())
            self.formularfel(path,data,'Kontrollera värde och längd i fälten: '+falt+'.')
        except ValueError:
            fel='Word-utkastet kunde inte skapas. Kontrollera underlaget och sparade skrivförsök före ett nytt försök.' if path in ('skriv','uppdaterautkast','utvardera') else 'Formuläret innehåller ett ogiltigt värde. Kontrollera de angivna uppgifterna.'
            self.formularfel(path,data,fel)

    def formularfel(self,path,data,fel):
        s=self.server
        status=409 if 'annan flik' in fel or 'Profilen har ändrats' in fel or 'redan använts' in fel or path.startswith('analys') and 'har ändrats' in fel else 400
        if path in ('plan','planutvardera','plangenomforande','planaterkalla','kombinationsgrupp','erbjudanderattelse'):
            from riskanalys.intag.planeringsvy import planeringssida
            html=planeringssida(s,data=data,fel=fel)
        elif path.startswith('analys'):
            from riskanalys.intag.analysvy import analyssida
            query={}
            if path=='analysoverfor':query={'overfor':['ja']}
            elif path=='analysblock':query={'tjanst':[data.get('tjanst','')],'block':[data.get('nummer','')]}
            elif path=='analysscenario':query={'tjanst':[data.get('tjanst','')],'scenario':[data.get('scenario','')]}
            elif path=='analysgemensamt':query={'gemensamt':[data.get('scenario','')]}
            elif path=='analysbekraftatjansteunderlag':query={'tjanst':[data.get('tjanst','')],'genomgang':['ja']}
            elif path=='analysbekraftabyraunderlag':query={'byraanalys':['ja']}
            elif path=='analysgemensampost':query={'byraanalys':['ja'],'post':[data.get('id','ny')],'slag':[data.get('typ','sarbarhet')]}
            elif path in ('analystillampning','analysbekraftatillampningar'):query={'tjanst':[data.get('tjanst','')],'tillampningar':['ja']}
            elif path=='analystackning':query={'tjanst':[data.get('tjanst','')],'tackning':['ja'],**{k:[data.get(k,'')] for k in ('ursprung','post','hot','dimension')},'riskled':[data.get('riskled') if data.get('riskled') in ('inneboende','kvarstaende') else 'inneboende']}
            elif path=='analysbeslut':query={'tjanst':[data.get('tjanst','')],'granska':['ja']}
            elif path in ('analysmodellrisk','analysmodellfel'):query={'modellrisk':['ja']}
            try:html=analyssida(s,query,data,fel)
            except RiskanalysFel:html=vyer.sida(s,'<h1>Lokal verksamhetsanalys</h1>',fel)
        elif path.startswith('register') or (path=='skapa' and data.get('bildsumma')):
            from riskanalys.intag.registervy import registersida
            html=registersida(s,data,fel)
        elif path=='tjanster':
            from riskanalys.intag.tjanstvy import tjanstesida
            html=tjanstesida(s,data,fel)
        elif path=='samlat':
            from riskanalys.intag.samladvy import samladsida
            try:html=samladsida(s,data.get('grupp'),data,fel)
            except RiskanalysFel:html=vyer.sida(s,'<h1>Samlade frågor</h1>',fel)
        elif path=='skapa':html=vyer.grund(s,data,fel)
        elif path=='svar':html=vyer.fragesida(s,data.get('falt'),data,fel)
        else:html=vyer.oversikt(s,fel)
        self.svara(status,html)

    def analystjanst(self):
        from riskanalys.analys.tjanst import Analystjanst
        return Analystjanst(self.server.tjanst.mapp, self.server.tjanst.rb)

    def post_plan(self,data):
        from riskanalys.intag.planeringsvy import spara_plan
        spara_plan(self.server.tjanst,data)
        self.server.utkast=None

    def post_kombinationsgrupp(self,data):
        from riskanalys.intag.planeringsvy import spara_kombinationsgrupp
        spara_kombinationsgrupp(self.server.tjanst,data)
        self.server.utkast=None

    def post_planutvardera(self,data):
        from riskanalys.intag.utvardering import registrera_utvardering
        delar=('underlag','hot_sarbarheter','risk_rutiner','beslut')
        if set(data)-{'csrf','revision','plan_id','datum',*delar} or not all(data.get(k,'').strip() for k in delar):
            raise RiskanalysFel('Beskriv underlag, hot och sårbarheter, påverkan på risk och rutiner samt beslut med skäl.')
        registrera_utvardering(self.server.tjanst,formulardatum(data,'datum'),'\n'.join(k+': '+data[k] for k in delar),data.get('revision',''),plan_id=data.get('plan_id',''))
        self.server.utkast=None

    def post_plangenomforande(self,data):
        from riskanalys.profil.forandringar import registrera_genomforande
        if set(data)-{'csrf','revision','plan_id','datum','ansvarig','genomford'} or data.get('genomford')!='ja':
            raise RiskanalysFel('Bekräfta uttryckligen att förändringen faktiskt är genomförd.')
        t=self.server.tjanst
        registrera_genomforande(t.mapp,t.rb,data.get('plan_id',''),formulardatum(data,'datum'),data.get('ansvarig',''),data.get('revision',''))
        self.server.utkast=None

    def post_planaterkalla(self,data):
        from riskanalys.profil.forandringar import aterkalla_plan
        if set(data)-{'csrf','revision','plan_id','datum','ansvarig','motivering'}:
            raise RiskanalysFel('Återkallelseformuläret innehåller okända uppgifter.')
        t=self.server.tjanst
        aterkalla_plan(t.mapp,t.rb,data.get('plan_id',''),formulardatum(data,'datum'),
                      data.get('ansvarig',''),data.get('motivering',''),data.get('revision',''))
        self.server.utkast=None

    def post_erbjudanderattelse(self,data):
        from riskanalys.drift.historik import Erbjudanderattelse
        from riskanalys.intag.svar import besvara
        if set(data)-{'csrf','revision','tjanst','motivering','kalla','roll','datum'}:
            raise RiskanalysFel('Rättelseformuläret innehåller okända fält.')
        s=self.server; p=s.tjanst.profil(); t=s.tjanst.rb.tjanster.get(data.get('tjanst',''))
        if t is None:
            raise RiskanalysFel('Välj en tjänst att rätta.')
        svar=IntagSvar(falt=t.erbjuds_falt,text='ja',kalla=data.get('kalla',''),roll=data.get('roll',''),datum=formulardatum(data,'datum'))
        efter=besvara(s.tjanst.rb,p,svar)
        from riskanalys.profil.omfattning import kompatibilitetsvy
        r=Erbjudanderattelse(tjanst=t.id,fore=kompatibilitetsvy(p,s.tjanst.rb).uppgifter[t.erbjuds_falt],efter=efter.uppgifter[t.erbjuds_falt],motivering=data.get('motivering',''),
            kalla=data.get('kalla',''),ansvarig=data.get('roll',''),datum=svar.datum,profilrevision=data.get('revision',''))
        s.tjanst.spara(svar,data.get('revision',''),rattelse=r)
        s.utkast=None

    def post_omfattningsunderlag(self,data):
        if set(data)-{'csrf','revision'}:raise RiskanalysFel('Omfattningsformuläret innehåller okända fält.')
        from riskanalys.dokument.omfattningsutkast import exportera_omfattningsutkast
        self.server.omfattningsfil=exportera_omfattningsutkast(self.server.tjanst.mapp,self.server.tjanst.rb,forvantad_revision=data.get('revision',''))

    def post_analysgemensampost(self,data):
        from riskanalys.intag.gemensamformular import las_post
        t=self.analystjanst();p=t.status().paket
        from riskanalys.analys.gemensamma_operationer import gemensamt
        gemensamt(p)
        post=las_post(data,p,self.server.tjanst.rb)
        if data['typ']=='sarbarhet':t.spara_gemensam_sarbarhet(post,data.get('revision',''),data.get('forfattare',''))
        else:t.spara_gemensam_verksamhet(post,data.get('revision',''),data.get('forfattare',''))

    def post_analystillampning(self,data):
        from riskanalys.intag.gemensamformular import las_tillampning
        t=self.analystjanst();status=t.status();p=status.paket
        operation=data.get('operation','spara')
        if operation not in ('visa','spara'):raise RiskanalysFel('Visa eller spara tillämpningen uttryckligen.')
        ref,app=las_tillampning(data,self.server.tjanst.rb,p)
        if operation=='visa':
            if data.get('revision')!=status.revision:raise RiskanalysFel('Analysen har ändrats i annan flik. Läs om underlaget.')
            from riskanalys.intag.gemensamvy import tillampningar
            from riskanalys.intag.vyer import sida
            html=tillampningar(self.server.tjanst.rb,status.profil,status.bedomning,p,data.get('tjanst',''),self.server.prefix,self.server.csrf,status.revision,data)
            self.svara(200,sida(self.server,html));return False
        t.spara_tillampning(data.get('tjanst',''),ref,app,data.get('revision',''),data.get('forfattare',''))

    def post_analysbekraftatillampningar(self,data):
        from riskanalys.intag.gemensamformular import las_samlad
        from riskanalys.analys.gemensamma_operationer import gemensamt
        t=self.analystjanst();p=gemensamt(t.status().paket)
        t.bekrafta_tillampningar(data.get('tjanst',''),las_samlad(data,p),data.get('revision',''),data.get('forfattare',''))

    def post_analysbekraftabyraunderlag(self,data):
        from riskanalys.intag.gemensamformular import las_helhet
        ids,celler=las_helhet(data)
        self.analystjanst().bekrafta_byraunderlag(ids,celler,data.get('revision',''),data.get('forfattare',''))

    def post_analysbekraftatjansteunderlag(self,data):
        if set(data)-{'csrf','revision','tjanst','forfattare','bekrafta'} or data.get('bekrafta')!='ja':
            raise RiskanalysFel('Bekräfta uttryckligen det visade tjänsteunderlaget utan extra fält.')
        self.analystjanst().bekrafta_tjansteunderlag(data.get('tjanst',''),data.get('revision',''),data.get('forfattare',''))

    def post_analystackning(self,data):
        from riskanalys.intag.gemensamformular import las_tackning
        from riskanalys.analys.gemensamma_operationer import gemensamt
        t=self.analystjanst();status=t.status();p=gemensamt(status.paket)
        prov=las_tackning(data,self.server.tjanst.rb,p).model_copy(update={'forfattare':t._forfattare(data.get('forfattare',''))})
        if data['operation']=='visa':
            if data.get('revision')!=status.revision:raise RiskanalysFel('Analysen har ändrats i annan flik. Läs om underlaget.')
            from riskanalys.intag.gemensamvy import tackningsformular
            from riskanalys.intag.vyer import sida
            b=next((b for b in status.bedomning.tjanster if b.tjanst==data.get('tjanst')),None)
            if b is None:raise RiskanalysFel('Välj en tjänst ur analysöversikten.')
            html=tackningsformular(self.server.tjanst.rb,p,b,self.server.prefix,self.server.csrf,status.revision,provning=prov)
            self.svara(200,sida(self.server,html));return False
        t.spara_tackningsprovning(data.get('tjanst',''),prov,data.get('revision',''),data.get('forfattare',''))

    def post_analysstart(self,data):
        if set(data)-{'csrf','revision','schema'} or data.get('schema','2') not in ('1','2'):raise RiskanalysFel('Startformuläret innehåller okända fält eller ogiltigt schema.')
        self.analystjanst().starta(data.get('revision',''),schema=int(data.get('schema','2')))

    def post_analysoverfor(self,data):
        if set(data)-{'csrf','revision','jamfort'} or data.get('jamfort')!='ja':
            raise RiskanalysFel('Jämför schemaförslaget med originalet och bekräfta jämförelsen först.')
        self.analystjanst().overfor(data.get('revision',''),True)

    def post_analysfornya(self,data):
        if set(data)-{'csrf','revision','jamfort'} or data.get('jamfort')!='ja':raise RiskanalysFel('Jämför de sparade svaren med aktuellt underlag först.')
        self.analystjanst().fornya(data.get('revision',''))

    def post_analysblock(self,data):
        try:nummer=int(data.get('nummer',''))
        except ValueError:raise RiskanalysFel('Välj ett av guidens sexton block.') from None
        self.analystjanst().spara_block(data.get('tjanst',''),nummer,data,data.get('revision',''))

    def post_analysscenario(self,data):
        self.analystjanst().spara_scenarioval(data.get('tjanst',''),data.get('scenario',''),data,data.get('revision',''))

    def post_analysgemensamt(self,data):
        self.analystjanst().spara_gemensamt(data.get('scenario',''),data,data.get('revision',''))

    def post_analysbeslut(self,data):
        if set(data)-{'csrf','revision','tjanst','beslut','namn','roll','datum','kommentar'} or data.get('beslut') not in ('godkann','underkann'):
            raise RiskanalysFel('Välj uttryckligen godkänn eller underkänn på granskningssidan.')
        self.analystjanst().beslut(data.get('tjanst',''),data['beslut']=='godkann',data.get('namn',''),data.get('roll',''),formulardatum(data,'datum'),data.get('kommentar',''),data.get('revision',''))

    def post_analysmodellfel(self,data):
        self.analystjanst().spara_modellfel(data,data.get('revision',''))

    def post_analysmodellrisk(self,data):
        self.analystjanst().spara_modellrisk(data,data.get('revision',''))

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
        planfalt={'plan_'+t.id for t in s.tjanst.rb.tjanster.values()}
        if set(data)-{'csrf','revision','hela_listan','underlag','kalla','roll','datum','urvalsformat'}-{'tjanst_'+id for id in ids}-planfalt:
            raise RiskanalysFel('Tjänstelistan innehåller okända uppgifter eller planval.')
        markers={k.removeprefix('tjanst_'):v for k,v in data.items() if k.startswith('tjanst_')}
        nytt_format=data.get('urvalsformat')=='2'
        if data.get('urvalsformat') not in (None,'2') or set(markers)-set(ids) or (nytt_format and (set(markers)!=set(ids) or any(v not in ('ja','nej','okant','bevara') for v in markers.values()))) or (not nytt_format and any(v!='ja' for v in markers.values())):
            raise RiskanalysFel('Välj bara tjänster ur den visade listan. Läs om sidan.')
        from riskanalys.intag.underlag import vald_kalla
        p=s.tjanst.profil()
        kalla=vald_kalla(s.tjanst.rb,p,s.tjanst.rb.falt[ids[0]],data)
        dag=formulardatum(data,'datum')
        if not kalla.strip() or not data.get('roll','').strip() or dag>date.today():
            raise RiskanalysFel('Ange gemensamt underlag, ansvarig funktion och datum senast idag för tjänsteurvalet.')
        svar=tuple(IntagSvar(falt=id,text='' if markers.get(id)=='okant' else markers[id] if nytt_format else 'ja' if id in markers else 'nej',
            status='okänt' if nytt_format and markers[id]=='okant' else 'bekräftad',
            motivering='Osäker vid genomgång av tjänsteutbudet; behöver kontrolleras.' if nytt_format and markers[id]=='okant' else '',
            kalla=kalla,roll=data['roll'],datum=dag) for id in ids if not nytt_format or markers[id]!='bevara')
        from riskanalys.profil.modeller import Planval
        val=tuple(Planval(tjanst=t.id,plan_id=data['plan_'+t.id]) for t in s.tjanst.rb.tjanster.values() if data.get('plan_'+t.id))
        s.tjanst.spara_flera(svar,data.get('revision',''),planval=val)
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
        if f.typ=='flerval':
            from riskanalys.intag.flervalsvy import formulartext
            text=formulartext(f,data)
        else:text=data.get('text','')
        svar=IntagSvar(falt=f.id,text=text,kalla=kalla,roll=data.get('roll',''),datum=formulardatum(data,'datum'),status=data.get('status','bekräftad'),motivering=data.get('motivering',''),period=period)
        from riskanalys.profil.modeller import Planval
        val=()
        if data.get('plan_id'):
            t=next((t for t in s.tjanst.rb.tjanster.values() if t.erbjuds_falt==f.id),None)
            if t is None:
                raise RiskanalysFel('Planval får bara följa med ett tjänsteerbjudande.')
            from riskanalys.intag.planvalsvy import bekraftat_ja
            if bekraftat_ja(f,text,svar.status):
                val=(Planval(tjanst=t.id,plan_id=data['plan_id']),)
        self.server.tjanst.spara(svar,data.get('revision',''),planval=val)
        self.server.utkast=None;self.server.kompletteringar=()

    def post_samlat(self,data):
        from riskanalys.intag.samlade import spara_grupp
        spara_grupp(self.server.tjanst,data)
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

    def post_uppdaterautkast(self,data):
        s=self.server
        if set(data)-{'csrf','revision'}:
            raise RiskanalysFel('Uppdateringsformuläret innehåller okända fält.')
        revision=profilrevision(s.tjanst.profil())
        if data.get('revision')!=revision or s.utkastrevision!=revision:
            raise RiskanalysFel('Profilen har ändrats eller formuläret hör till en annan flik. Läs om sidan och skapa ett nytt utkast vid ändrade fakta.')
        if not s.utkast:
            raise RiskanalysFel('Skapa ett Word-utkast före uppdatering.')
        s.utkast=uppdatera_export(s.tjanst.mapp,s.tjanst.rb,s.utkast)

    def word(self, *, underlag=False):
        s=self.server
        if not s.utkast:
            self.svara(404,'Skapa ett Word-utkast först.');return
        if s.utkastrevision != profilrevision(s.tjanst.profil()):
            raise RiskanalysFel('Utkastet bygger på äldre svar. Skapa ett nytt utkast.')
        fil=s.utkast.parent/'underlagsbilaga-UTKAST.docx' if underlag else s.utkast
        if underlag and not fil.is_file():
            raise RiskanalysFel('Underlagsbilagan saknas. Uppdatera båda delarna av Word-utkastet.')
        innehall=las_utkast(s.tjanst.mapp, s.tjanst.rb, fil)
        self.svara(200,innehall,'application/vnd.openxmlformats-officedocument.wordprocessingml.document',extra={'Content-Disposition':f'attachment; filename="{fil.name}"'})


def formulardatum(data,falt):
    try:return date.fromisoformat(data.get(falt,''))
    except ValueError:raise RiskanalysFel(f'Kontrollera datumfältet {falt}. Skriv datum som ÅÅÅÅ-MM-DD.') from None
