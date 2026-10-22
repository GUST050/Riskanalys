"""Sex lokala analysfrågor, med skyddad AI-text och fulltextfallback för fria svar."""
from riskanalys.analys.modeller import Analyspaket, Tjansteanalys
from riskanalys.analys.provning import gallande_beslut
from riskanalys.dokument.analysreferenser import bygg_analysreferenser
from riskanalys.dokument.analystabeller import bygg_scenariotabell, bygg_rutinatgarder, lokalcell, scenarioetikett, status
from riskanalys.dokument.delskrivning import kontrollera_resultat
from riskanalys.dokument.gemensamt_v8 import tjanstens_erfarenhetsstycke, tjanstens_geografistycke
from riskanalys.dokument.lokaldata_v8 import tjanstefakta
from riskanalys.dokument.lokalblock_v8 import lokala_block
from riskanalys.dokument.modeller import Avsnitt, Underrubrik
from riskanalys.dokument.nivamotivering_v8 import ej_godtagna_sankningar, nivarad, nivaskal
from riskanalys.dokument.skrivversion import V8
from riskanalys.dokument.tabeller import rad, tabell
from riskanalys.dokument.tjanstavsnitt import _ai_stycken
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.dokument.tjanstavsnitt_v7 import kategorioversikt

RUBRIKER = ('Vad levererar tjänsten?', 'Hur kan tjänsten utnyttjas?', 'Vad betyder sårbarheterna lokalt?',
            'Vilken risknivå och vilka avgörande skäl?', 'Vad visar kontrollerna?', 'Vad behöver göras?')


def kontrollobservationer(a, paket):
    """Gruppera exakt samma observation, inklusive belägg/period/täckning/begränsning."""
    belagg = {b.id: b for b in paket.belagg} if paket else {}
    grupper = {}
    for n,k in enumerate(a.kontroller):
        perioder = tuple((id, belagg[id].period.model_dump_json() if id in belagg and belagg[id].period else None) for id in k.belagg)
        # Minst ett faktiskt daterat belägg krävs. Hela beläggs-/periodvektorn
        # ingår; odaterad utformning blandas inte ihop med observationens period.
        okand = not any(p is not None for _,p in perioder)
        nyckel = (a.tjanst, k.model_dump_json(exclude={'scenario'}), perioder, n if okand else None)
        grupper.setdefault(nyckel, []).append((n,k))
    return tuple(tuple(g) for g in grupper.values())


def kontrolltabell(a, paket, rb, index):
    rader = []
    belagg = {b.id:b for b in paket.belagg} if paket else {}
    for grupp in kontrollobservationer(a, paket):
        n,k = grupp[0]
        ids = tuple(x.scenario for _,x in grupp)
        refs = (k.kontroll,*k.rackvidd,*index.refs('scenario',ids),*index.refs('belagg',k.belagg),'D-ARB.B1')
        perioder = '; '.join(f'{id}: {belagg[id].period.fran}–{belagg[id].period.till}'
            if id in belagg and belagg[id].period else f'{id}: period okänd' for id in k.belagg) or 'Period och belägg saknas'
        namn = rb.kontroller[k.kontroll].namn if k.kontroll in rb.kontroller else k.kontroll
        rader.append(rad(*(lokalcell(x,refs) for x in (
            f'Observation {a.tjanst}-{n+1}. {namn}. {scenarioetikett(index,ids)}',
            f'Tillämpning: {k.tillampning}\nUtfall: {k.utfall}',
            f'Täckning: {status(k.tackning)}. Kvarstår: {k.kvarstar}',
            f'{perioder}. {index.lista("belagg",k.belagg)}'))))
    return tabell(a.tjanst+'-kontrollprovning', 'Faktisk kontroll, period och begränsning',
        ('Observation och scenario', 'Tillämpning och utfall', 'Täckning och begränsning', 'Period och belägg'),rader) if rader else None


def bygg_tjanstavsnitt_v8(rb, profil, t, resultat, avsnitt_id, *, gransindex, analys=None, _operationer=None):
    """Analys är det frysta paketet; en ensam tjänsteanalys stöds utan påhittad beläggsperiod."""
    paket = analys if isinstance(analys,Analyspaket) else None
    a = next((x for x in paket.tjanster if x.tjanst == t.tjanst),None) if paket else analys
    if a is not None and not isinstance(a,Tjansteanalys):
        raise TypeError('Analys ska vara ett fryst analyspaket eller en tjänsteanalys.')
    index = bygg_analysreferenser(paket)
    if resultat is not None:
        kontrollera_resultat(rb,profil,t,resultat,avsnitt_id,gransindex=gransindex,formatversion=V8)
    operationer = {}
    def bind(stycke, falt, *, kalla='analys'):
        operationer[id(stycke)] = tuple((kalla,f) for f in falt)
        return stycke
    ai = {}
    delar = [[] for _ in RUBRIKER]
    tabeller = [[] for _ in RUBRIKER]
    fakta, faktatabell = tjanstefakta(rb,profil,t)
    delar[0].extend(fakta)
    tabeller[0].append(faktatabell)
    svar = resultat.del_('analys').godkant_svar if resultat else None
    if svar:
        for n,s in enumerate(_ai_stycken(svar,resultat.faktablad.numeriska(),resultat.faktablad.perioder())):
            s=s.model_copy(update={'proveniens':'ai'})
            ai[id(s)]=n
            delar[1].append(s)
    else:
        delar[1].append(lokaltext('Validerad AI-text saknas. Komplettera och granska analysen. Fullständigt katalogunderlag finns i underlagsbilaga B1. [VERIFIERA]',(t.tjanst,'D-ARB.B1')))
    # Byråns gemensamma underlag står i avsnittet Gemensamt faktaunderlag; tjänstens egen prövning står här.
    delar[2].extend((*tjanstens_erfarenhetsstycke(rb,profil,t,gransindex=gransindex),
                     *tjanstens_geografistycke(rb,profil,t.tjanst,gransindex=gransindex)))
    from riskanalys.dokument.nivamotivering_v8 import lokala_faktorskal
    from riskanalys.dokument.forandringar_v8 import gruppstycken
    faktorstycken=lokala_faktorskal(rb,profil,paket,t)
    delar[2].extend(bind(s,('sarbarhetsprovningar',)) if a is not None else s for s in faktorstycken)
    delar[2].extend(gruppstycken(rb,profil,t.tjanst))
    if a is not None:
        beslut = gallande_beslut(paket,t.tjanst) if paket else None
        status_text = ('Registrerat analysgodkännande saknas. [VERIFIERA]' if beslut is None else
            f'Senaste registrerade analysbeslut: {"godkänt" if beslut.godkand else "underkänt"}, {beslut.datum}, av {beslut.namn}.')
        forfattarstycke=lokaltext(f'Registrerade lokala svar. Analysförfattare: {a.forfattare or "inte registrerad"}. '
            + status_text + ' Dokumenttexten utgör ingen ny attest.', (t.tjanst,'D-ARB.B1'))
        delar[0].append(bind(forfattarstycke,('forfattare',)))
        # Befintliga fullständiga fältmallar: inga nya fria svar tolkas eller kapas.
        lokala = lokala_block(a,paket or Analyspaket.model_construct(tjanster=(a,),gemensamma_scenarier=(),belagg=()),rb,index,profil=profil)
        for block in lokala:
            delar[block.fraga].append(bind(block.stycke,block.falt))
        if paket:
            tabeller[1].append(bygg_scenariotabell(a,paket,rb,index))
        tabeller[4].append(kontrolltabell(a,paket,rb,index))
        tabeller[5].append(bygg_rutinatgarder(a,index))
    niva = nivaskal(rb,t,a)
    if t.scenarier:
        delar[3].append(nivarad(t))
    if a is not None:
        # Byråns PT- och TF-bedömning är nivåskälets två sista stycken; positionen registreras här.
        bind(niva[-2],('pt_motivering','reduktionsmotivering','reduktionsprovning'))
        bind(niva[-1],('tf_motivering',))
    delar[3].extend(niva)
    if paket and a is not None:
        delar[3].extend(bind(s,('kontroller','scenarier','scenariokopplingar'))
                        for s in ej_godtagna_sankningar(rb,profil,paket,a,t))
    # Fullständiga motorutfall, faktorer och register står i B1 (berakningstabeller); här står nivå och avgörande skäl.
    if not t.scenarier:
        tabeller[3].append(kategorioversikt(rb,profil,t,a,gransindex=gransindex,position=0))
    # Varje fråga får synlig osäkerhet om dess uppgifter saknas, aldrig ett positivt standardpåstående.
    reserv = ('Lokal uppdragsanalys saknas.', 'Lokal modusanalys saknas.', 'Lokal sårbarhetsprövning saknas.',
              'Lokal nivåmotivering saknas.', 'Faktisk kontrollprövning saknas.', 'Åtgärdsprövning saknas.')
    stycken, rubriker, tab = [], [], []
    for n,rubrik in enumerate(RUBRIKER):
        start = len(stycken)
        rubriker.append(Underrubrik(fore_stycke=start,rubrik=rubrik))
        stycken.extend(delar[n] or (lokaltext(('Underlag i tabellen nedan.' if any(tabeller[n]) else reserv[n]+' [VERIFIERA]'),(t.tjanst,)),))
        tab.extend(x.model_copy(update={'fore_stycke':start}) for x in tabeller[n] if x is not None)
    if _operationer is not None:
        for n,s in enumerate(stycken):
            if id(s) in operationer:
                _operationer[f'stycken/{n}']=operationer[id(s)]
            if id(s) in ai:
                _operationer[f'stycken/{n}']=(('ai',str(ai[id(s)])),)
        if a is not None:
            _operationer['beslutsstycke']=next(n for n,s in enumerate(stycken) if s is forfattarstycke)
    return Avsnitt(id=avsnitt_id,rubrik='Analys av '+rb.tjanster[t.tjanst].namn.lower(),kalla='lokal',
        stycken=tuple(stycken),tabeller=tuple(tab),underrubriker=tuple(rubriker),formatversion=V8,leveransdel='lasrapport')
