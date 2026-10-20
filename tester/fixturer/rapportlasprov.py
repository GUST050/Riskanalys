"""H7.1:s frysta, uttryckligen påhittade verksamhet; inga live-AI-svar.

JSON-resursen är den slutliga provexportens bundna syntetiska profil och
lokala ogranskade analys. Äldre fixturer och deras beteende lämnas orörda.
"""
from dataclasses import replace
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from riskanalys.analys.modeller import Analyspaket, Analysgap
from riskanalys.analys.utkast import forifyll_analys
from riskanalys.bedomning.motor import bedom
from riskanalys.profil.modeller import Profil, Uppgift, Period
from riskanalys.profil.lagring import profilrevision
from riskanalys.profil.omfattning import harled_andelar
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.urval import valj
from riskanalys.intag.fordelning import FAKTORER, underlagsbindning
from tester.fixturer.analys_hela_kedjan import skapa_fall, SyntetisktFall, TJANSTER

FALL = ('fyra_tjanster', 'utan_betalningsmandat', 'med_betalningsmandat',
        'okand_fordelning', 'olika_perioder', 'ingen_belagd_effekt',
        'motstridig_analys', 'liten_exponerad_tjanst',
        'tvingat_tjansteoverlapp', 'ej_tvingat_tjansteoverlapp')
BASFIL = Path(__file__).with_name('rapportlasprov_bas.json')


def bygg_rapportlasprov(regelbas: Regelbas, rot: Path, fall: str) -> SyntetisktFall:
    if fall not in FALL:
        raise ValueError('Okänt rapportläsprov: '+fall)
    bas = skapa_fall(regelbas, rot)
    data = json.loads(BASFIL.read_text())
    profil = Profil.model_validate(data['profil'])
    paket = Analyspaket.model_validate(data['analys'])
    upp = dict(profil.uppgifter)

    def satt(id, varde, **extra):
        upp[id] = upp[id].model_copy(update={'varde': varde, **extra})

    if fall == 'med_betalningsmandat':
        satt('P-TJ.red04_betalningsmandat', 'verkstaller')
        satt('P-TJ.red04_bankinsyn', 'full')
        satt('P-TJ.red04_arbetssatt', 'Byrån verkställer betalningar enligt kundens attest och separat betalningsmandat samt beräknar löner och upprättar AGI.')
        satt('P-BESK.verksamhet', 'Syntetisk byrå med fyra tjänster. Kunden attesterar underlagen. Byrån verkställer betalningar inom löneuppdragets uttryckliga mandat; övriga betalningar utförs av kunden.')
    elif fall == 'okand_fordelning':
        upp['P-TJ.red04_antal_utland_transaktion'] = Uppgift()
    elif fall == 'olika_perioder':
        satt('P-TJ.red04_antal_utland_transaktion', 6,
             period=Period(fran=date(2025,1,1), till=date(2025,9,30)))
    elif fall == 'ingen_belagd_effekt':
        for id in upp:
            if id.startswith('P-KONTROLL.') and id.endswith('.effekt'):
                satt(id, 'ej_bedömd')
    elif fall == 'liten_exponerad_tjanst':
        satt('P-TJ.red04_antal_kunder', 6)
        for suffix, varde in zip(FAKTORER, (6,2,6,5)):
            satt('P-TJ.red04_'+suffix, varde)
    elif fall in ('tvingat_tjansteoverlapp', 'ej_tvingat_tjansteoverlapp'):
        antal = 24 if fall == 'tvingat_tjansteoverlapp' else 10
        satt('P-KUND.antal_aktiva', 60)
        # Anpassa alla kundräknare: inga omöjliga antal över sina nämnare.
        for id, u in tuple(upp.items()):
            if id.startswith(('P-KUND.antal_', 'P-GEO.antal_', 'P-KANAL.antal_')) and type(u.varde) is int:
                satt(id, min(u.varde,60))
        for i in range(1,5):
            satt(f'P-TJ.red0{i}_antal_kunder', antal)
            for suffix in FAKTORER:
                id=f'P-TJ.red0{i}_'+suffix
                satt(id, min(upp[id].varde,antal))
    profil = harled_andelar(profil.model_copy(update={'uppgifter':upp}), regelbas)
    # Nya svar binds uttryckligen till de faktiska baserna; inkompatibla perioder
    # fortsätter att vara ogiltiga även med en aktuell bindning.
    if fall != 'fyra_tjanster':
        upp = dict(profil.uppgifter)
        for i in range(1,5):
            for suffix in FAKTORER:
                id=f'P-TJ.red0{i}_'+suffix
                if profil.ar_bekraftad(id):
                    upp[id]=upp[id].model_copy(update={'underlagsbindning':underlagsbindning(regelbas,profil,id)})
        profil=profil.model_copy(update={'uppgifter':upp})
    b=bedom(regelbas,valj(regelbas,profil.byra.regelpaket,profil.byra.datum,profil.byra.lan),profil)
    bindning=paket.bindning.model_copy(update={'profilrevision':profilrevision(profil),
        'regelbas':regelbas.kontrollsumma,'bedomningsdatum':profil.byra.datum,
        'bedomningsmanifest':'syntetisk-H7.1-omraknad-motor',
        'utkastmanifest':'syntetisk-H7.1-offline-ogranskat'})
    nytt=forifyll_analys(regelbas,profil,b,bindning)
    fras={t.tjanst:t for t in nytt.tjanster}
    analyser=[]
    for t in paket.tjanster:
        update={'block':tuple(x.model_copy(update={'bekraftad_summa':None}) for x in t.block)}
        if fall != 'fyra_tjanster':
            update.update(exponering=fras[t.tjanst].exponering,
                          exponeringsbelagg=fras[t.tjanst].exponeringsbelagg,
                          pt_motivering=fras[t.tjanst].pt_motivering,
                          tf_motivering=fras[t.tjanst].tf_motivering,
                          reduktionsprovning=fras[t.tjanst].reduktionsprovning)
        if t.tjanst == 'T-RED-04' and fall == 'med_betalningsmandat':
            # Variantens fakta ändrar alla återanvända mandat-/insynspåståenden,
            # även i scenario, kontrolltillämpning, luckor och åtgärder. Utfört
            # stickprov, okänd täckning och dokumentationsbrister består.
            ersattningar = {
                'Kunden genomför löneutbetalningen.':
                    'Byrån verkställer löneutbetalningen enligt kundens attest och uttryckligt betalningsmandat.',
                'Faktisk utbetalning och slutmottagare syns inte i tjänsten.':
                    'Faktiska löneutbetalningar är synliga via full bankinsyn; bakomliggande affär och senare betalningsled är inte därmed verifierade.',
                'Byrån förfogar inte över kundmedel eller betalningsmandat.':
                    'Byrån har betalningsmandat för löner och full bankinsyn inom uppdraget; detta bevisar inte att underlagen är riktiga.',
                'Löneunderlag och föreslagen betalningsfil, men inga kontoutdrag eller bekräftelser om faktisk utbetalning.':
                    'Löneunderlag, betalningsfil och kontoutdrag för de löneutbetalningar som byrån verkställer är tillgängliga inom uppdragets fulla bankinsyn.',
                'även utan betalningsmandat': 'även med betalningsmandat',
            }
            def mandattext(varde):
                if isinstance(varde, str):
                    for gammal, ny in ersattningar.items():
                        varde = varde.replace(gammal, ny)
                    return varde
                if isinstance(varde, list):
                    return [mandattext(v) for v in varde]
                if isinstance(varde, dict):
                    return {k: mandattext(v) for k, v in varde.items()}
                return varde
            t = type(t).model_validate(mandattext(t.model_dump(mode='json')))
        if t.tjanst == 'T-RED-04' and fall in ('utan_betalningsmandat','med_betalningsmandat','motstridig_analys'):
            text=('Byrån verkställer betalningar från kundens konto enligt separat mandat.'
                  if fall != 'utan_betalningsmandat' else
                  'Kunden verkställer betalningarna; byrån beräknar löner och upprättar AGI utan betalningsmandat.')
            if fall == 'med_betalningsmandat':
                text += ' Mandat och tillgång till kontoutdrag bevisar inte genomförd kontroll, verksam effekt eller verifierat affärssyfte.'
            update['betalningsinsyn']=t.betalningsinsyn.model_copy(update={'motivering':text})
            if fall == 'motstridig_analys':
                update['gap']=(*t.gap,Analysgap(id='H7.1:mandatkonflikt',typ='motstridigt_underlag',
                    beskrivning='Profilen anger inget betalningsmandat medan analysen säger att byrån verkställer betalningar.',
                    motivering='Båda uppgifterna bevaras. Mandatet måste klarläggas före sakgodkännande.'))
        if fall == 'ingen_belagd_effekt':
            update['kontroller']=tuple(c.model_copy(update={'utfall':'Rutin och genomförande finns i provunderlaget; effekt är inte bedömd.'}) for c in t.kontroller)
            update['reduktionsmotivering']='Dokumenterad rutin är inte belägg för verksam effekt. Ingen reduktion har antagits.'
        analyser.append(t.model_copy(update=update))
    # Profilbelägg återskapas så frånvarande/ogiltiga fördelningar inte lever kvar.
    paket=paket.model_copy(update={'bindning':bindning,'belagg':nytt.belagg,
        'tjanster':tuple(analyser),'beslut':()})
    return replace(bas, profil=profil, bedomning=b, analys=paket)


def overlappsunderlag(fall: SyntetisktFall) -> dict:
    """Lokal härledning, aldrig AI-fakta eller exakt kund-/faktoröverlapp."""
    antal=[fall.profil.uppgifter[fall.regelbas.tjanster[id].erbjuds_falt.removesuffix('_erbjuds')+'_antal_kunder'].varde for id in TJANSTER]
    bas=fall.profil.uppgifter['P-KUND.antal_aktiva'].varde
    extra=max(0,sum(antal)-bas)
    grans=(extra+len(antal)-2)//(len(antal)-1)
    return {'aktiva_kunder':bas,'tjansteantal':antal,'tjanstekopplingar':sum(antal),
        'minst_flera_tjanster':grans,'exakt_antal':None,'kundidentiteter':None,
        'specifika_tjanstepar':None,'riskkategori_overlapp':None,
        'antaganden':'Samma period och kundbas; varje kund kan ha högst en koppling till vardera av fyra tjänster. Aktiva kunder behöver inte använda alla tjänster.',
        'berakning':f'Överskjutande kopplingar max(0, {sum(antal)} − {bas}) = {extra}; varje flertjänstkund kan bidra med högst 3 extra. Avrunda {extra}/3 uppåt = {grans}. Nedre gräns, inte exakt antal.'}


def frys_b_offline(fall: SyntetisktFall, rot: Path) -> Path:
    """Frys ett märkt V7-utkast; skapa aldrig om en befintlig baslinje."""
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.arb import bygg_arb
    from riskanalys.dokument.rendering import rendera_docx
    from riskanalys.dokument.matning import dokumentord
    from riskanalys.drift.historik import Historik
    from tester.fixturer.skrivsvar_v7 import tjanstspecifikt_svar_v7
    rot.mkdir(parents=True,exist_ok=False)
    par=list(tjanster_med_avsnitt(fall.bedomning))
    skript=[tjanstspecifikt_svar_v7(fall.regelbas,fall.profil,t,id) for id,t in par]
    leverantor=Testleverantor(skript)
    resultat={id:skriv_tjanst(leverantor,fall.regelbas,fall.profil,t,id,effort='medium',
        personnamn=(),spara=lambda *args:None,formatversion='D-ARB-tjanst-v7') for id,t in par}
    if any(d.mall or d.godkant_svar is None for r in resultat.values() for d in r.delar):
        raise ValueError('Baslinjens syntetiska skript gav inte godkända V7-svar.')
    dokument=bygg_arb(fall.regelbas,fall.profil,fall.bedomning,resultat,Historik(),analys=fall.analys,formatversion='D-ARB-tjanst-v7')
    _spara_granskning(fall,rot,resultat,dokument)
    poster={'profil':fall.profil,'bedomning':fall.bedomning,'analys':fall.analys,
        'testleverantor-skript':[s.model_dump(mode='json') for s in skript],
        'forvantade-anropsbytes':[a.model_dump(mode='json',by_alias=True) for a in leverantor.delanrop],
        'dokument':dokument,'regelbas':fall.regelbas}
    for namn,data in poster.items():
        if hasattr(data,'model_dump'):data=data.model_dump(mode='json')
        (rot/(namn+'.json')).write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    rendera_docx(dokument,fall.profil,'UTKAST – syntetiskt B-offline, inte sakkunniggranskat',rot/'V7-UTKAST.docx')
    manifest={'baslinje':'B-offline','format':'D-ARB-tjanst-v7','regelbas':fall.regelbas.kontrollsumma,
        'ai_text':'Testleverantor; inte B-live:s verkliga AI-text','programmets_ordmatt':dokumentord(dokument,fall.profil),
        'filer':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(rot.iterdir()) if p.is_file()}}
    (rot/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return rot


def _spara_granskning(fall, rot, resultat, dokument):
    from riskanalys.granskning.kontroller import granska
    from riskanalys.granskning.korning import oppna_fragor
    from riskanalys.dokument.rendering import atgardslista, rendera_docx, gruppera_fynd
    from riskanalys.drift.historik import Historik
    p=fall.profil
    fragor=oppna_fragor(resultat)
    fynd=granska(fall.regelbas,valj(fall.regelbas,p.byra.regelpaket,p.byra.datum,p.byra.lan),
        p,fall.bedomning,dokument,Historik(),p.byra.datum,fragor,skrivresultat=resultat,analys=fall.analys)
    presentation=atgardslista(fynd,fragor,formatversion='D-ARB-tjanst-v7')
    poster={'fynd':[f.model_dump(mode='json') for f in fynd],
        'fyndpresentation':presentation,
        'granskning':{'datum':str(p.byra.datum),'metod':'Produktens rena granska; ingen filkedjeattest eller fastställelse',
            'blockerande':sum(f.allvar=='blockerande' for f in fynd),'fyndposter':len(fynd),
            'exakta_fyndgrupper':len(gruppera_fynd(fynd)),
            'tjanstevisa_atgardsposter':sum(len(t.rutinatgarder) for t in fall.analys.tjanster),
            'historik':Historik().model_dump(mode='json')}}
    for namn,data in poster.items():
        (rot/(namn+'.json')).write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    rendera_docx(dokument,p,'UTKAST – syntetiskt B-offline med öppna granskningsfynd',rot/'V7-UTKAST-med-fynd.docx',presentation)


def komplettera_b_offline(fall: SyntetisktFall, bas: Path, rot: Path) -> Path:
    """Bind tillägg till en tidigare fryst bas utan att skriva i den."""
    from riskanalys.dokument.delskrivning import skriv_tjanst
    from riskanalys.dokument.leverantor import Testleverantor
    from riskanalys.dokument.underlag import tjanster_med_avsnitt
    from riskanalys.dokument.modeller import Dokument, AISvar
    ursprung=(bas/'manifest.json').read_bytes()
    manifest=json.loads(ursprung)
    for fil,h in manifest['filer'].items():
        if sha256((bas/fil).read_bytes()).hexdigest()!=h:
            raise ValueError('Baslinjefilen har ändrats: '+fil)
    rot.mkdir(parents=True,exist_ok=False)
    leverantor=Testleverantor([AISvar.model_validate(s) for s in json.loads((bas/'testleverantor-skript.json').read_text())])
    resultat={id:skriv_tjanst(leverantor,fall.regelbas,fall.profil,t,id,effort='medium',
        personnamn=(),spara=lambda *args:None,formatversion='D-ARB-tjanst-v7') for id,t in tjanster_med_avsnitt(fall.bedomning)}
    if [a.model_dump(mode='json',by_alias=True) for a in leverantor.delanrop]!=json.loads((bas/'forvantade-anropsbytes.json').read_text()):
        raise ValueError('De rekonstruerade begärandena skiljer sig från den frysta baslinjen.')
    # Skydda exakt profil/motor/analys, inte bara den offentliga AI-begäran.
    for namn,objekt in (('profil',fall.profil),('bedomning',fall.bedomning),('analys',fall.analys)):
        if objekt.model_dump(mode='json')!=json.loads((bas/(namn+'.json')).read_text()):
            raise ValueError('Kompletteringen kräver exakt samma '+namn+'.')
    _spara_granskning(fall,rot,resultat,Dokument.model_validate_json((bas/'dokument.json').read_text()))
    data={'baslinje':'B-offline-komplement','ursprungsmanifest_sha256':sha256(ursprung).hexdigest(),
        'oforandrade_basfiler':manifest['filer'],'filer':{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(rot.iterdir()) if p.is_file()}}
    (rot/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return rot
