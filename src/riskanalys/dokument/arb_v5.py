"""Kortare D-ARB med lokala tabeller; ändrar inga motorutfall eller AI-data."""
from riskanalys.bedomning.erfarenheter import ERFARENHETSFALT
from riskanalys.dokument.modeller import Avsnitt, AvsnittsUtkast, Dokument, Textstycke, Underrubrik
from riskanalys.dokument.tabeller import (cell, rad, tabell, kort_varde, bygg_riskoversikt,
    bygg_kontrolloversikt, bygg_tjansteoversikt, bygg_atgardsoversikt, bygg_metodmatris)
from riskanalys.dokument.underlag import tjanster_med_avsnitt, sarbarhet_status
from riskanalys.regelverk.granser import metodgransindex
from riskanalys.regelverk.villkor import falt_i, tolka_villkor


def stycke(text, refs=(), typ='beskrivning'):
    return Textstycke(typ=typ,text=text,referenser=list(dict.fromkeys(refs)))


def avsnitt(id,rubrik,stycken=(),tabeller=(),kalla='regelbas'):
    return Avsnitt(id=id,rubrik=rubrik,kalla=kalla,stycken=tuple(stycken),tabeller=tuple(tabeller),formatversion='D-ARB-tjanst-v5')


def geografitabell(rb,p,t,index):
    """En rad per geografiskt villkor; beskrivande geografi återges bara en gång."""
    from riskanalys.dokument.klartext import villkorstext
    rows=[]
    for id in rb.tjanster[t.tjanst].sarbarheter:
        s=rb.sarbarheter[id]
        if s.omrade!='geo':
            continue
        refs=sorted(falt_i(tolka_villkor(s.villkor,rb.faltdefinitioner())))
        status=sarbarhet_status(rb,p,id)
        text={'ja':'Villkoret är uppfyllt','nej':'Villkoret är inte uppfyllt','okänt':'Villkoret är okänt. [VERIFIERA]'}[status]
        values='; '.join(kort_varde(rb,p,x,period=True,gransindex=index) for x in refs)
        rows.append(rad(cell(s.namn,(id,)),cell(villkorstext(s.villkor,rb),refs),cell(text+'. Underlag: '+values,refs)))
    return tabell(t.tjanst+'-geografi','Geografiska villkor i metoden',('Faktor','Villkor','Utfall och underlag'),rows)


def egen_erfarenhet_kort(rb,p,t,index):
    slug=rb.tjanster[t.tjanst].erbjuds_falt.removesuffix('_erbjuds'); id=slug+'_ovriga_risker'
    text='Egen erfarenhet i hotanalysen: gemensamma rapporteringsuppgifter finns i avsnittet Myndighetsunderlag och egna erfarenheter. '
    e=t.egen_erfarenhet
    if e is None or not e.belagd:
        text+='Rapporteringsunderlaget är ofullständigt. [VERIFIERA] '
    if e and e.rapporter=='inga':
        text+='Noll rapporter visar inte frånvaro av hot. '
    text+='Byråns uppgift om tjänsten: '+kort_varde(rb,p,id,gransindex=index)
    return stycke(text,[t.tjanst,*ERFARENHETSFALT,id],typ='analys')


def bygg_tjanstavsnitt_v5(rb,p,t,resultat,avsnitt_id,*,gransindex=None):
    from riskanalys.dokument.delskrivning import kontrollera_resultat, ANSVARSMENING
    from riskanalys.dokument.tjanstavsnitt import _ai_stycken
    from riskanalys.dokument.nivatext import utfallsforklaring
    index=gransindex if gransindex is not None else metodgransindex(rb)
    kontrollera_resultat(rb,p,t,resultat,avsnitt_id,gransindex=index,formatversion="D-ARB-tjanst-v5")
    fb=resultat.faktablad; tj=rb.tjanster[t.tjanst]; slug=tj.erbjuds_falt.removesuffix('_erbjuds')
    def ai(id):
        svar=resultat.del_(id).godkant_svar
        if svar:
            return _ai_stycken(svar,fb.numeriska(),fb.perioder())
        markering=(stycke('Analysen behöver kompletteras. [VERIFIERA]',[t.tjanst],typ='motivering'),)
        if id=='hot':
            return (*markering,*(stycke(f'{rb.hot[x].namn}: {rb.hot[x].beskrivning}',[t.tjanst,x,*rb.hot[x].kallor]) for x in t.hot))
        if id=='sarbarheter':
            from riskanalys.dokument.analysunderlag import sarbarhetsstycke
            return (*markering,*(sarbarhetsstycke(rb,p,t.tjanst,x,gransindex=index) for x in tj.sarbarheter))
        return markering
    arbete=slug+'_arbetssatt'; geo=slug+'_geografi'
    delar=[
        ('Beskrivning och omfattning',(stycke(kort_varde(rb,p,arbete,gransindex=index),[t.tjanst,arbete]),)),
        ('Hot och egna erfarenheter',(*ai('hot'),egen_erfarenhet_kort(rb,p,t,index))),
        ('Sårbarheter och motivering',(*ai('sarbarheter'),stycke('Tjänstens geografi enligt byrån: '+kort_varde(rb,p,geo,gransindex=index)+'. Enskilda villkor utesluter inte andra geografiska risker, även inom Sverige.',[t.tjanst,geo,'P-BESK.geografi'],typ='analys'))),
        ('Kontroller och effekt',(*ai('kontroller'),stycke('Kontrollernas status, belägg och begränsningar redovisas i den gemensamma kontrolltabellen.',[t.tjanst,*[k.id for k in t.kontroller]]))),
        ('Scenarier och osäkerheter',(*ai('risknivaer'), stycke('Byråns prövning mot sektorsbilden: '+kort_varde(rb,p,slug+'_sektorsmotivering',gransindex=index),[t.tjanst,slug+'_sektorsmotivering'],typ='motivering'))),
        ('Slutsatser',(*ai('slutsatser'),stycke(ANSVARSMENING,[t.tjanst]))),
    ]
    texter=[]; rubriker=[]; tabeller=[]
    for i,(rubrik,poster) in enumerate(delar):
        pos=len(texter); rubriker.append(Underrubrik(fore_stycke=pos,rubrik=rubrik)); texter.extend(poster)
        if i==2:
            tabeller.append(geografitabell(rb,p,t,index).model_copy(update={'fore_stycke':pos}))
        if i==4:
            tabeller.append(utfallsforklaring(t,rb).model_copy(update={'fore_stycke':pos}))
    return Avsnitt(id=avsnitt_id,rubrik='Analys av '+tj.namn.lower(),kalla='ai',stycken=tuple(texter),
                   underrubriker=tuple(rubriker),tabeller=tuple(tabeller),formatversion='D-ARB-tjanst-v5')


def bygg_arb_v5(rb,p,b,resultat,historik,*,gransindex=None):
    from riskanalys.dokument.arb import _syfte, _utvardering
    from riskanalys.dokument.intagsunderlag import bygg_underlagsbilaga
    from riskanalys.dokument.uppfoljning import bevakningsavsnitt, uppfoljningsstycken
    from riskanalys.dokument.kallhanvisningar import med_kallhanvisningar
    index=gransindex if gransindex is not None else metodgransindex(rb)
    erbjudna=[t for t in b.tjanster if t.inneboende]
    syfte=_syfte(rb,p,b)
    syfte=syfte.model_copy(update={'formatversion':'D-ARB-tjanst-v5','stycken':(*syfte.stycken,
        stycke('Metodstatus: riskvikter, tak och kontrollreduktion är ogranskade metodval. Nivåerna redovisar motorns beräkning, inte sakkunniggodkända slutsatser. Öppna frågor och kontrollbrister behöver hanteras före fastställelse.'))})
    metod=avsnitt('D-ARB.2','Metod och begränsningar',(
        stycke('PT avser penningtvätt, TF finansiering av terrorism. Riskmatrisen är kvalitativ. Faktorer höjer sannolikheten till ett tak; minst en belagd verksam kontroll sänker PT ett steg enligt dagens metod. TF sänks inte av den regeln. Kontrollernas täckning måste prövas separat.',
               [rb.metod.sannolikhet.id,rb.metod.konsekvens.id,rb.metod.terrorfinansiering.id,rb.metod.kvarstaende_sankning.id]),
        stycke('Omfattning enligt metoden: '+(b.proportionalitet.niva if b.proportionalitet else 'ej bedömd')+'. Byråns motivering: '+kort_varde(rb,p,'P-OMFATTNING.motivering',gransindex=index),['P-OMFATTNING.motivering']),
    ),(bygg_metodmatris(rb),))
    from riskanalys.dokument.nivatext import sektorsmening
    sektorer=sorted({rb.tjanster[t.tjanst].sektorreferens for t in erbjudna if rb.tjanster[t.tjanst].sektorreferens})
    metod=metod.model_copy(update={'stycken':(*metod.stycken,*(stycke(sektorsmening(rb,rb.sektorsreferenser[id]),[id,rb.sektorsreferenser[id].kalla]) for id in sektorer))})
    inte=[rb.tjanster[t.tjanst].namn for t in b.tjanster if t.erbjuds is False]
    tjanster=avsnitt('D-ARB.3','Byråns tjänster',(
        stycke('Kundantal överlappar mellan tjänster och summeras inte till unika kunder. Befogenheter framgår av respektive tjänsteanalys.'),
        stycke('Erbjuds inte: '+', '.join(inte)+'.') if inte else stycke('Alla katalogens tjänster behöver prövas individuellt.'),
    ),(bygg_tjansteoversikt(rb,p,b,gransindex=index),))
    refs=[*ERFARENHETSFALT,'P-BESK.erfarenheter']
    hot=avsnitt('D-ARB.4','Myndighetsunderlag och egna erfarenheter',(
        stycke('Myndigheternas riskscenarier analyseras per tjänst. Sektorsrisk är en separat referens och bestämmer inte automatiskt byråns nivå.',
               sorted({k for t in erbjudna for id in t.hot for k in rb.hot[id].kallor})),
        stycke('Byrågemensamt underlag: '+'; '.join(rb.falt[id].fraga.rstrip('?')+': '+kort_varde(rb,p,id,period=True,gransindex=index) for id in refs)+'. Antalen tillhör hela byrån. Noll rapporter är inte belägg för frånvaro av risk.',refs,typ='analys'),
    ))
    gem=['P-BESK.geografi','P-BESK.kunder']
    gem=[id for id in gem if id in rb.falt]
    sarb=avsnitt('D-ARB.5','Gemensamma riskförhållanden',(
        stycke('Byrågemensamma indikatorer tillämpas konservativt per tjänst. De visar inte att varje kund berörs; överlapp och tjänstefördelning behöver sakprövas.'),
        *(stycke(rb.falt[id].fraga.rstrip('?')+': '+kort_varde(rb,p,id,gransindex=index),[id],typ='analys') for id in gem),
    ))
    kontroller=avsnitt('D-ARB.7','Kontroller, utfall och bedömd effekt',(
        stycke('Noll avvikelser bevisar inte effektivitet. Scenariovis kontrolltäckning är inte fastställd av motorn. Tabellen visar dokumenterat underlag; lokala belägg finns i B1.'),
    ),(bygg_kontrolloversikt(b,rb,p,gransindex=index),))
    kontroll_ids=tuple(dict.fromkeys(k.id for t in erbjudna for k in (*t.kontroller,*((t.sanktionsrisk.kontroll,) if t.sanktionsrisk and t.sanktionsrisk.kontroll else ()))))
    kontroller=kontroller.model_copy(update={'stycken':(*kontroller.stycken,*(stycke(rb.kontroller[id].namn+': '+rb.kontroller[id].beskrivning,[id]) for id in kontroll_ids))})
    risk=tuple(bygg_tjanstavsnitt_v5(rb,p,t,resultat[id],id,gransindex=index) for id,t in tjanster_med_avsnitt(b) if id in resultat)
    # Samla exakt samma strukturerade geografi en gång; tjänstespecifik prosa kvarstår.
    gemensamma={}
    for a in risk:
        for tab in a.tabeller:
            if tab.id.endswith('-geografi'):
                gemensamma.setdefault((tab.kolumner,tab.rader),[]).append(a.id)
    for signatur, ids in gemensamma.items():
        if len(ids)<2:
            continue
        tab=next(t for a in risk if a.id==ids[0] for t in a.tabeller if t.id.endswith('-geografi'))
        namn=', '.join(a.rubrik.removeprefix('Analys av ') for a in risk if a.id in ids)
        tab=tab.model_copy(update={'id':'gemensam-geografi-'+str(len(sarb.tabeller)+1),
                                  'rubrik':'Geografiska villkor: '+namn, 'fore_stycke':0})
        sarb=sarb.model_copy(update={'tabeller':(*sarb.tabeller,tab)})
        risk=tuple(a.model_copy(update={'tabeller':tuple(t for t in a.tabeller if not t.id.endswith('-geografi')),
                   'stycken':(*a.stycken,stycke('Geografiska villkor och belägg: se Gemensamma riskförhållanden.'))})
                   if a.id in ids else a for a in risk)
    samman=avsnitt('D-ARB.8','Tjänstevis risksammanställning',(
        stycke('Nivåerna är oförändrade motorutfall. Beräkningsförklaringen finns i respektive tjänsteanalys. Ingen sammanvägd byrånivå beräknas. Sanktionsrisk är inte ett besked om listträff eller förbud.'),
    ),(bygg_riskoversikt(b,rb),))
    atgarder=avsnitt('D-ARB.9','Åtgärder och fortsatt arbete',(
        stycke('Förslagen är inte beslut eller genomförda åtgärder. Ansvar och tidsfrist saknar egna beslutade intagsfält. Komplettera även de öppna granskningsfynden i slutet av dokumentet. Prioritering beslutas av byrån.'),
    ),(bygg_atgardsoversikt(rb,b),))
    if b.status!='slutlig':
        atgarder=atgarder.model_copy(update={'stycken':(*atgarder.stycken,stycke('Bedömningen är preliminär; komplettera okända uppgifter före beslut. [VERIFIERA]'))})
    uppf=_utvardering(historik)
    uppf=uppf.model_copy(update={'stycken':(*uppf.stycken,*uppfoljningsstycken(rb,p,gransindex=index))})
    poster=(syfte,metod,tjanster,hot,sarb,kontroller,*risk,samman,atgarder,uppf,
            bevakningsavsnitt(rb,p,gransindex=index),bygg_underlagsbilaga(rb,p,gransindex=index))
    poster=tuple(a.model_copy(update={'formatversion':'D-ARB-tjanst-v5','visningsnummer':'B1' if a.id=='D-ARB.B1' else str(n)}) for n,a in enumerate(poster,1))
    from riskanalys.dokument.matning import med_langdvarning
    return med_langdvarning(med_kallhanvisningar(Dokument(id='D-ARB',titel='Allmän riskbedömning',avsnitt=poster),rb),p)
