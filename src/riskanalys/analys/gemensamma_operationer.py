"""Typade gemensamma handlingar. Varje skrivning går genom analysens lås och CAS."""
from riskanalys.analys import modeller as m, lagring as l
from riskanalys.analys.gemensam import postsumma, tackningssumma
from riskanalys.bedomning.korning import las_bedomning
from riskanalys.fel import RiskanalysFel


def byt_tjanst(paket,a):
    return paket.model_copy(update={'tjanster':tuple(a if x.tjanst==a.tjanst else x for x in paket.tjanster)})


def gemensamt(paket):
    if paket is None or paket.schemaversion!=2:
        raise RiskanalysFel('Starta eller överför uttryckligen analysen till schema 2 först.')
    return paket


def hamta_post(paket,referens):
    poster=paket.gemensamma_sarbarhetsprovningar if referens.slag=='sarbarhet' else paket.gemensamma_verksamhetsposter
    p=next((p for p in poster if p.id==referens.post),None)
    if p is None:raise RiskanalysFel('Välj en befintlig gemensam post.')
    if postsumma(p)!=referens.summa:
        raise RiskanalysFel('Den gemensamma posten har ändrats. Läs om innehållet före bekräftelse.')
    return p


def hamta_tjanst(paket,id):
    a=next((a for a in paket.tjanster if a.tjanst==id),None)
    if a is None:raise RiskanalysFel('Välj en tjänst ur analysöversikten.')
    return a


class GemensammaOperationer:
    def _spara_gemensam(self,post,revision,forfattare,modell,falt):
        with l.analyslas(self.mapp):
            paket,_,_,_=self._last(revision);gemensamt(paket)
            p=modell.model_validate(post.model_dump(mode='json')).model_copy(update={'forfattare':self._forfattare(forfattare)})
            gamla=getattr(paket,falt)
            poster=tuple(p if x.id==p.id else x for x in gamla)
            if p.id not in {x.id for x in gamla}:poster=(*poster,p)
            return self._spara(paket.model_copy(update={falt:poster}),forvantad_summa=revision)

    def spara_gemensam_sarbarhet(self,post,revision,forfattare):
        return self._spara_gemensam(post,revision,forfattare,m.GemensamSarbarhetsprovning,'gemensamma_sarbarhetsprovningar')

    def spara_gemensam_verksamhet(self,post,revision,forfattare):
        return self._spara_gemensam(post,revision,forfattare,m.GemensamVerksamhetspost,'gemensamma_verksamhetsposter')

    def spara_tillampning(self,tjanst,referens,tillampning,revision,forfattare):
        with l.analyslas(self.mapp):
            paket,_,_,_=self._last(revision);gemensamt(paket)
            p=hamta_post(paket,referens);a=hamta_tjanst(paket,tjanst)
            sarbarhet=referens.slag=='sarbarhet'
            if sarbarhet != isinstance(tillampning,m.Sarbarhetstillampning):
                raise RiskanalysFel('Använd rätt tillämpningstyp för den gemensamma posten.')
            modell=m.Sarbarhetstillampning if sarbarhet else m.GemensamTillampning
            app=modell.model_validate(tillampning.model_dump(mode='json'))
            if app.post!=p.id or app.postsumma!=postsumma(p):
                raise RiskanalysFel('Tillämpningen gäller inte den visade gemensamma posten.')
            if sarbarhet and app.riktningsval and app.riktningsval.riktning!='oklar':
                if not app.riktningsval.motivering or not app.riktningsval.belagg:
                    raise RiskanalysFel('Klargjord manuell riktning kräver motivering och belägg.')
            falt='sarbarhetstillampningar' if sarbarhet else 'verksamhetstillampningar'
            gamla=getattr(a,falt);app=app.model_copy(update={'bekraftad':True})
            appar=tuple(app if x.post==app.post else x for x in gamla)
            if app.post not in {x.post for x in gamla}:appar=(*appar,app)
            a=a.model_copy(update={falt:appar,'forfattare':self._forfattare(forfattare)})
            return self._spara(byt_tjanst(paket,a),forvantad_summa=revision)

    def bekrafta_tillampningar(self,tjanst,poster,revision,forfattare):
        with l.analyslas(self.mapp):
            paket,_,_,_=self._last(revision);gemensamt(paket)
            a=hamta_tjanst(paket,tjanst);namn=self._forfattare(forfattare)
            if not poster or len({(p.slag,p.post) for p in poster})!=len(poster):
                raise RiskanalysFel('Markera unika visade poster som gäller oförändrat.')
            andringar={}
            for ref in poster:
                p=hamta_post(paket,ref)
                falt='sarbarhetstillampningar' if ref.slag=='sarbarhet' else 'verksamhetstillampningar'
                appar=andringar.get(falt,getattr(a,falt))
                app=next((x for x in appar if x.post==ref.post),None)
                if app is not None and app.stallningstagande!='galler':
                    raise RiskanalysFel('Samlad bekräftelse får bara sätta gäller och aldrig skriva över en avvikelse.')
                modell=m.Sarbarhetstillampning if ref.slag=='sarbarhet' else m.GemensamTillampning
                ny=(app or modell(post=p.id,stallningstagande='galler',postsumma=postsumma(p))).model_copy(update={'postsumma':postsumma(p),'bekraftad':True})
                andringar[falt]=tuple(ny if x.post==p.id else x for x in appar) if app else (*appar,ny)
            a=a.model_copy(update={**andringar,'forfattare':namn})
            return self._spara(byt_tjanst(paket,a),forvantad_summa=revision)

    def spara_tackningsprovning(self,tjanst,provning,revision,forfattare):
        with l.analyslas(self.mapp):
            paket,bm,_,_=self._last(revision);gemensamt(paket)
            a=hamta_tjanst(paket,tjanst)
            p=m.Tackningsprovning.model_validate(provning.model_dump(mode='json')).model_copy(update={'forfattare':self._forfattare(forfattare)})
            bedomning=las_bedomning(bm);t=next(x for x in bedomning.tjanster if x.tjanst==tjanst)
            if not p.visad_summa or p.visad_summa!=tackningssumma(self.rb,paket,t,p):
                raise RiskanalysFel('Prövningen eller dess underlag har ändrats. Visa prövningen på nytt före bekräftelse.')
            key=lambda x:(x.ursprung,x.post,x.hot,x.dimension,x.riskled)
            prov=tuple(p if key(x)==key(p) else x for x in a.tackningsprovningar)
            if key(p) not in {key(x) for x in a.tackningsprovningar}:prov=(*prov,p)
            a=a.model_copy(update={'tackningsprovningar':prov,'forfattare':self._forfattare(forfattare)})
            return self._spara(byt_tjanst(paket,a),forvantad_summa=revision)

    def bekrafta_byraunderlag(self,tjanster,celler,revision,forfattare):
        from riskanalys.analys.engangssvar import bygg_gemensam_bekraftelse
        with l.analyslas(self.mapp):
            paket,bm,_,_=self._last(revision);gemensamt(paket)
            bedomning=las_bedomning(bm)
            erbjudna={t.tjanst for t in bedomning.tjanster if t.erbjuds is True}
            if set(tjanster)-erbjudna:
                raise RiskanalysFel('Välj endast erbjudna tjänster ur aktuell bedömning.')
            nytt=bygg_gemensam_bekraftelse(paket,tjanster,celler,self._forfattare(forfattare))
            return self._spara(nytt,forvantad_summa=revision)
