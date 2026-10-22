"""Gemensam analys en gång; tjänstens explicita tillämpning utan nya motorbeslut."""
import json
from riskanalys.analys.gemensam import tillampning_aktuell,tackningssumma
from riskanalys.analys.riktning import harled_riktningar
from riskanalys.analys.referens import referensniva
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext


ETIKETTER={
    'kund':'kunder','kanal':'distributionskanaler','geo':'geografi','verk':'egen verksamhet',
    'bekraftad':'bekräftat faktaunderlag','antagande':'antagande','kunskapslucka':'kunskapslucka',
    'relevant':'relevant','ej_relevant':'ej relevant','okant':'okänd relevans',
    'galler':'gäller oförändrat','galler_annorlunda':'gäller annorlunda','beror_inte':'berör inte tjänsten','otillrackligt':'otillräckligt underlag',
    'i_linje':'i linje med motorn','lagre':'lägre bedömning, motorn är försiktigare','under_troskel':'under tröskeln',
    'villkor_ej_uppfyllt':'villkoret är inte uppfyllt','ersatt_av_faktor':'ersatt av annan faktor','tackt_av_scenario':'täcks av befintligt scenario',
    'mojlig_underskattning':'möjlig underskattning','oklar':'oklar riktning','harledd':'härledd av programmet','manuell':'byråns motiverade val',
    'leverantorer':'leverantörer och eget ansvar','erfarenhet':'egna lärdomar','sanktionsanknytning':'sanktionsanknytning',
    'inneboende':'inneboende risk','kvarstaende':'kvarstående risk',
    'tacks_av_scenario':'täcks av befintligt scenario','tacks_inte':'täcks inte',
}

def etikett(varde):return ETIKETTER.get(varde,varde)


def originalstycke(inledning,varden,refs=()):
    text=inledning;spann=[]
    for etikett,original in varden:
        if not original:continue
        text+='\n'+etikett
        start=len(text);text+=original;spann.append((start,len(text)))
    return lokaltext(text,refs).model_copy(update={'literala_spann':tuple(spann)})


def gemensamma_provningsstycken(rb,paket):
    if paket is None or paket.schemaversion!=2:return ()
    stycken=[];sedda=set()
    for p in paket.gemensamma_sarbarhetsprovningar:
        refs=('ANALYS:gemensam_sarbarhet:'+p.id,*('ANALYS:belagg:'+b for b in p.belagg),'D-ARB.B1')
        for id in p.sarbarheter if p.relevans=='relevant' else ():
            if id in sedda or id not in rb.sarbarheter:continue
            sedda.add(id);s=rb.sarbarheter[id]
            text=f'Katalogens mekanism – {s.namn} ({id}): '+(s.metodmotivering or s.beskrivning or 'Mekanism saknas. [VERIFIERA]')
            stycken.append(lokaltext(text,(id,*s.kallor),typ='motivering').model_copy(update={'proveniens':'regelbas'}))
        stycken.append(originalstycke(f'Byråns gemensamma prövning {p.id}: {etikett(p.omrade)}; {etikett(p.relevans)}; status {etikett(p.status)}. ',
            (('Författare: ',p.forfattare or 'inte registrerad'),('Beskrivning: ',p.beskrivning),('Motivering: ',p.motivering)),refs))
    for p in paket.gemensamma_verksamhetsposter:
        refs=('ANALYS:gemensam_verksamhet:'+p.id,*('ANALYS:belagg:'+b for b in p.belagg),'D-ARB.B1')
        stycken.append(originalstycke(f'Gemensamt verksamhetsunderlag {p.id}: {etikett(p.slag)}; status {etikett(p.status)}. ',(('Författare: ',p.forfattare or 'inte registrerad'),('Analys: ',p.text)),refs))
        for l in p.leverantorer:
            stycken.append(originalstycke('Leverantör '+l.id+':',tuple((n.replace('_',' ')+': ',getattr(l,n)) for n in
                ('omfattning','leverantorens_kontroller','egen_verifiering','brister_och_motstridigheter','ansvar')),(*refs,*('ANALYS:belagg:'+b for b in l.belagg))))
    return tuple(stycken)


def tjanstens_tillampningsstycken(rb,profil,paket,t):
    if paket is None or paket.schemaversion!=2:return ()
    a=next((a for a in paket.tjanster if a.tjanst==t.tjanst),None)
    if a is None:return ()
    stycken=[];samma=[]
    for slag,poster,appar in (('sarbarhet',paket.gemensamma_sarbarhetsprovningar,a.sarbarhetstillampningar),('verksamhet',paket.gemensamma_verksamhetsposter,a.verksamhetstillampningar)):
        for p in poster:
            app=next((x for x in appar if x.post==p.id),None)
            refs=(t.tjanst,'D-ARB.5','D-ARB.B1','ANALYS:gemensam_'+slag+':'+p.id)
            if app and tillampning_aktuell(p,app) and app.stallningstagande=='galler' and p.status=='bekraftad':
                samma.append(p.id);continue
            aktuell=app is not None and tillampning_aktuell(p,app)
            text=f'Gemensamt faktaunderlag {p.id}: '+(etikett(app.stallningstagande) if app else 'ställningstagande saknas')+f'. Sakstatus {etikett(p.status)}. '+('Aktuellt bekräftad tillämpning.' if aktuell else 'Tillämpningen är obekräftad eller inaktuell. [VERIFIERA]')
            if p.status!='bekraftad':text+=' Osäkerheten gäller även denna tjänst; antagandet är inte ett bekräftat faktum.'
            stycken.append(originalstycke(text,(('Lokal motivering: ',app.motivering if app else ''),),(*refs,*('ANALYS:belagg:'+b for b in (app.belagg if app else ())))))
    if samma:stycken.insert(0,lokaltext('Gemensamt faktaunderlag gäller oförändrat för tjänsten, enligt uttrycklig prövning: '+', '.join(samma)+'. Se gemensamma mekanismer och belägg i Gemensamt faktaunderlag.',(t.tjanst,'D-ARB.5','D-ARB.B1')))
    for r in harled_riktningar(rb,profil,paket,t):
        if r.riktning=='i_linje':continue
        fakta='; '.join(f'{f}={profil.uppgifter[f].varde}' if profil.ar_bekraftad(f) else f'{f}=okänt' for f in r.profilfalt)
        villkor=rb.sarbarheter.get(r.sarbarhet)
        regel=(' Villkor: '+json.dumps(villkor.villkor,ensure_ascii=False,sort_keys=True)+'.') if villkor and r.riktning in ('under_troskel','villkor_ej_uppfyllt') else ''
        text=f'{r.post} / {r.sarbarhet or "egen sårbarhet"} / {r.hot} / {r.dimension}: {etikett(r.riktning)} ({etikett(r.kalla)}). {r.motivering}'+(' Faktaunderlag: '+fakta+'.' if fakta else '')+regel
        if r.riktning in ('under_troskel','villkor_ej_uppfyllt'):text+=' Upplysning till D9 C, inget beslutat metodfel och ingen ändrad tröskel.'
        stycken.append(lokaltext(text,(t.tjanst,'D-ARB.5','D-ARB.B1',*(r.profilfalt),*(r.regelspar),*((r.sarbarhet,) if r.sarbarhet in rb.sarbarheter else ()))))
    for p in a.tackningsprovningar:
        ref=referensniva(rb,profil,t,p.hot,p.dimension,p.riskled)
        aktuell=p.visad_summa==tackningssumma(rb,paket,t,p)
        text=f'Egen sårbarhet {p.post}, {p.hot}/{p.dimension}, {etikett(p.riskled)}: {etikett(p.stallningstagande)}. Lokalt scenario: {p.lokalt_scenario or "saknas"}. Byråns jämförelsenivå: {p.jamforelseniva or "saknas"}. Referens: samma scenario med ytterligare +1 – inte ett facit: {ref or "underlag saknas"}. '+('Aktuellt visad prövning.' if aktuell else 'Inaktuell eller obekräftad täckningsprövning. [VERIFIERA]')
        if p.riskled=='kvarstaende':text+=' Referensen behåller samma kontrollantaganden; deras giltighet för den egna mekanismen måste sakprövas.'
        stycken.append(originalstycke(text,(('Mekanism och täckning: ',p.motivering),('Avvikelse från referens: ',p.referensmotivering)),(t.tjanst,'D-ARB.B1',*('ANALYS:belagg:'+b for b in p.belagg))))
    return tuple(stycken)


def delat_lokalblock(block,a,paket):
    """Visa aktuellt gemensamt arv i sin egen operation, aldrig genom falska lokala pointers."""
    if paket.schemaversion!=2:return False
    appar={x.post:x for x in a.verksamhetstillampningar}
    for p in paket.gemensamma_verksamhetsposter:
        app=appar.get(p.id)
        if not app or not tillampning_aktuell(p,app) or app.stallningstagande=='galler_annorlunda':continue
        namn={'leverantorer':('leverantorsmotivering','leverantorer'),'erfarenhet':('erfarenhetsprovning','erfarenhetsbelagg'),'sanktionsanknytning':('sanktioner',)}[p.slag]
        if any(f.split('/')[0] in namn for f in block.falt):return True
    return False


def d9_upplysningar(rb,profil,paket,bedomning):
    """Samla kända falska villkor per faktor, aldrig okända värden eller metodbeslut."""
    if paket is None or paket.schemaversion!=2:return ()
    grupper={}
    for t in bedomning.tjanster:
        if t.erbjuds is not True:continue
        for r in harled_riktningar(rb,profil,paket,t):
            if r.riktning not in ('under_troskel','villkor_ej_uppfyllt'):continue
            grupper.setdefault((r.sarbarhet,r.riktning),[]).append((t.tjanst,r))
    stycken=[]
    for (id,riktning),grupp in grupper.items():
        r=grupp[0][1];s=rb.sarbarheter[id]
        fakta='; '.join(f'{f}={profil.uppgifter[f].varde}' if profil.ar_bekraftad(f) else f'{f}=okänt' for f in r.profilfalt)
        berorda=', '.join(dict.fromkeys(t+'/'+rad.hot+'/'+rad.dimension for t,rad in grupp))
        refs=(id,*r.profilfalt,*r.regelspar,
            *('ANALYS:gemensam_sarbarhet:'+rad.post for _,rad in grupp),
            *('ANALYS:tillampning:sarbarhet:'+t+':'+rad.post for t,rad in grupp))
        text=f'D9 C – {id}, {etikett(riktning)}. Faktiskt underlag: {fakta}. Villkor: '+json.dumps(s.villkor,ensure_ascii=False,sort_keys=True)+f'. Berörda tjänster/hot/dimensioner: {berorda}. Upplysning för metoduppföljning, inget beslutat metodfel. Ingen tröskel eller risknivå ändras.'
        stycken.append(lokaltext(text,refs))
    return tuple(stycken)
