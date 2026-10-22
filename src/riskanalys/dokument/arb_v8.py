"""Det kanoniska V8-dokumentet: fullständigt granskningsunderlag för två leveransdelar."""
from riskanalys.analys.provning import analysbrister
from riskanalys.dokument.analysreferenser import bygg_analysreferenser
from riskanalys.dokument.analysstatus import analysstatus, modellstatus
from riskanalys.dokument.analystabeller import scenariorad, lokalcell, status
from riskanalys.dokument.arb_v5 import stycke
from riskanalys.dokument.arb_v5_1 import METODFRAGOR, _sakkunnigstatus
from riskanalys.dokument.arb_v6 import bilaga_b1_v6, med_kallregisterrubrik, utvarderingsavsnitt_v6, _oppna_metodfragor
from riskanalys.dokument.delskrivning import Tjanstresultat
from riskanalys.dokument.kallhanvisningar import med_kallhanvisningar, bygg_kallregister
from riskanalys.dokument.gemensamt_v8 import (GEMENSAMT_ID, GEMENSAMT_RUBRIK, gemensamma_geografistycken,
                                             gemensamt_erfarenhetsstycke)
from riskanalys.dokument.lokaldata_v8 import kundoverlapp
from riskanalys.dokument.modeller import Avsnitt, Dokument
from riskanalys.dokument.radata_v8 import komplettera_radata
from riskanalys.dokument.rackvidd_v6 import rackviddsoversikt
from riskanalys.dokument.skrivversion import V8
from riskanalys.dokument.tabeller import bygg_riskoversikt, bygg_metodmatris, bygg_tjansteoversikt, tabell, rad
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.dokument.tjanstavsnitt_v7 import reservkatalog_i_b1
from riskanalys.dokument.tjanstavsnitt_v8 import bygg_tjanstavsnitt_v8
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.granser import metodgransindex

HELHET = ('Läsrapport och kompletterande underlagsbilaga B1 utgör tillsammans fullständig dokumentation. '
          'Granskaren ska läsa båda delarna; ingen del utgör ensam hela riskbedömningen.')


def avsnitt(id, rubrik, stycken=(), tabeller=(), *, leveransdel='lasrapport', kalla='regelbas'):
    return Avsnitt(id=id,rubrik=rubrik,stycken=tuple(stycken),tabeller=tuple(tabeller),kalla=kalla,
                  formatversion=V8,leveransdel=leveransdel)


def atgardsposter(bedomning, analys):
    """D9:s synliga radordning med index till exakt vald analys och åtgärd."""
    analyser = {a.tjanst:(ti,a) for ti,a in enumerate(analys.tjanster)} if analys else {}
    for id,t in tjanster_med_avsnitt(bedomning):
        vald = analyser.get(t.tjanst)
        if vald is not None:
            ti,a = vald
            for ri,r in enumerate(a.rutinatgarder):
                yield id,t,ti,ri,r


def atgardsoversikt(rb,bedomning,analys):
    rader=[]
    for id,t,ti,ri,r in atgardsposter(bedomning,analys):
        rader.append(rad(*(lokalcell(x,(id,'D-ARB.B1')) for x in (rb.tjanster[t.tjanst].namn,
            r.id,status(r.status),r.ansvar or 'Inte beslutat',str(r.uppfoljning or 'Inte beslutad'),
            f'Se {id}, Vad behöver göras?, åtgärd {r.id}.'))))
    return avsnitt('D-ARB.9','Åtgärdsöversikt',(
        lokaltext('Alla registrerade åtgärder visas var för sig. Full åtgärdstext, rutinbindning och utlösare står i tjänstens följdspunkt.'),
    ),(tabell('v8-atgardsoversikt','Tjänsternas åtgärder',('Tjänst','Åtgärds-ID','Status','Ansvar','Uppföljning','Fulltext'),rader),))


def med_berakningstabeller(rb,bedomning,bilaga):
    """Tjänsternas motortabeller placeras i B1 direkt efter respektive tjänsts utfallstabell."""
    from riskanalys.dokument.nivamotivering_v8 import BERAKNINGSUNDERLAG, berakningstabeller
    start=next((u.fore_stycke for u in bilaga.underrubriker if u.rubrik==BERAKNINGSUNDERLAG),len(bilaga.stycken))
    flyttas={t.tjanst:berakningstabeller(rb,t) for _,t in tjanster_med_avsnitt(bedomning)}
    tabeller=[]
    for tab in bilaga.tabeller:
        tabeller.append(tab)
        tj=tab.id.removesuffix('-utfall') if tab.id.endswith('-utfall') else None
        tabeller.extend(x.model_copy(update={'fore_stycke':tab.fore_stycke}) for x in flyttas.pop(tj,()))
    tabeller.extend(x.model_copy(update={'fore_stycke':start}) for rest in flyttas.values() for x in rest)
    return bilaga.model_copy(update={'tabeller':tuple(tabeller)})


def bygg_arb_v8(rb,profil,bedomning,resultat,historik,*,analys,gransindex=None,modellrapport=None) -> Dokument:
    from riskanalys.dokument.gemensamt_v8 import gemensamma_faktormekanismer
    from riskanalys.dokument.forandringar_v8 import planunderlag
    from riskanalys.dokument.arb import _syfte,_metod
    from riskanalys.dokument.uppfoljning import bevakningsavsnitt,kort_omfattningsstycke,uppfoljningsstycken
    if any(not isinstance(r,Tjanstresultat) or r.formatversion != V8 for r in resultat.values()):
        raise RiskanalysFel('V8 kräver nya versionsbundna V8-skrivresultat. Skriv och granska på nytt; äldre utkast får inte märkas om.')
    index = gransindex if gransindex is not None else metodgransindex(rb)
    refindex=bygg_analysreferenser(analys)
    brister=analysbrister(rb,profil,bedomning,analys) if analys else ()
    metodposter=(*rb.metod.regler(),*rb.metod.riskmatris)
    syfte=_syfte(rb,profil,bedomning,bevara_original=True)
    syfte=syfte.model_copy(update={'stycken':(*syfte.stycken,stycke(HELHET,['D-ARB.B1']))})
    oversikt=avsnitt('D-ARB.8','Kort bedömning och tjänstevis risk',(
        stycke('Risknivåerna är motorns utfall, med alla avgörande skäl vid varje tjänst. Ingen sammanvägd byrånivå beräknas.'),
        stycke(f'Metodstatus: {sum(_sakkunnigstatus(r)=="verifierad" for r in metodposter)} av {len(metodposter)} regelobjekt har giltig sakkunnigverifiering.'),
        *analysstatus(rb,bedomning,analys,brister,formatversion=V8),*modellstatus(analys,modellrapport),
    ),(bygg_riskoversikt(bedomning,rb),))
    metod=avsnitt('D-ARB.2','Metod och begränsningar',(
        _metod(rb,bedomning).stycken[0],
        stycke('PT avser penningtvätt och TF finansiering av terrorism. Sanktioner prövas separat.'),
        kort_omfattningsstycke(rb,profil,bedomning,gransindex=index,bevara_original=True),stycke(_oppna_metodfragor(METODFRAGOR))),
        (bygg_metodmatris(rb),))
    tjanster=avsnitt('D-ARB.3','Byråns tjänster',(kundoverlapp(rb,profil,bedomning),),
        (bygg_tjansteoversikt(rb,profil,bedomning,gransindex=index),))
    gemensamt=avsnitt('D-ARB.4','Gemensamma scenarier',(
        stycke('Gemensamma händelseförlopp. Tjänstens egen relevans, avvikelser och begränsningar prövas i varje tjänsteavsnitt.'),),
        (tabell('gemensamma-scenarier','Gemensamma händelseförlopp',('Scenario','Händelseförlopp','Betydelse','Hot','Belägg'),
            (scenariorad(s,rb,refindex) for s in analys.gemensamma_scenarier)),) if analys and analys.gemensamma_scenarier else ())
    lokal=avsnitt(GEMENSAMT_ID,GEMENSAMT_RUBRIK,(
        lokaltext('Byråövergripande underlag redovisas här en gång. Varje tjänsteavsnitt anger tjänstens egen exponering, '
                  'lokala betydelse och avvikelser. Fullständiga ursprungliga lokala svar med fältsökvägar finns i den '
                  'kompletterande underlagsbilagan B1.',('D-ARB.B1',)),
        *gemensamt_erfarenhetsstycke(rb,profil,bedomning,gransindex=index),
        *gemensamma_geografistycken(rb,profil,bedomning,gransindex=index),
        *gemensamma_faktormekanismer(rb,bedomning)))
    kontroller=avsnitt('D-ARB.7','Källbunden kontrollräckvidd',rackviddsoversikt(rb,bedomning,formatversion=V8))
    risk=tuple(bygg_tjanstavsnitt_v8(rb,profil,t,resultat.get(id),id,gransindex=index,analys=analys)
               for id,t in tjanster_med_avsnitt(bedomning))
    bilaga=bilaga_b1_v6(rb,profil,bedomning,analys,refindex=refindex,brister=brister,tillampningskarta=(),
        metodposter=metodposter,gransindex=index,reservkatalog=reservkatalog_i_b1(rb,profil,bedomning,resultat,gransindex=index),
        bevara_original=True)
    bilaga=bilaga.model_copy(update={'formatversion':V8,'leveransdel':'underlagsbilaga','visningsnummer':'B1'})
    bilaga=med_berakningstabeller(rb,bedomning,bilaga)
    planstycken=planunderlag(profil,historik)
    if planstycken:
        from riskanalys.dokument.modeller import Underrubrik
        bilaga=bilaga.model_copy(update={'stycken':(*bilaga.stycken,*planstycken),
            'underrubriker':(*bilaga.underrubriker,Underrubrik(fore_stycke=len(bilaga.stycken),rubrik='Förändringsplaner och utvärderingar'))})
    uppfoljning=utvarderingsavsnitt_v6(historik)
    uppfoljning=uppfoljning.model_copy(update={'stycken':(*uppfoljning.stycken,*uppfoljningsstycken(rb,profil,gransindex=index,formatversion=V8))})
    if profil.tjansteplaner:
        uppfoljning=uppfoljning.model_copy(update={'stycken':(*uppfoljning.stycken,stycke(
            f'{len(profil.tjansteplaner)} registrerade förändringsplaner. Planantaganden och genomförda planutvärderingar redovisas i B1. '
            'Avgränsade planutvärderingar flyttar inte fristen för hela riskbedömningens årsgenomgång. De kräver förnyad analys och sakprövning.', ['D-ARB.B1']))})
    poster=(oversikt,syfte,metod,tjanster,gemensamt,lokal,kontroller,*risk,atgardsoversikt(rb,bedomning,analys),uppfoljning,
        bevakningsavsnitt(rb,profil,gransindex=index,kort=True,formatversion=V8),bilaga)
    poster=tuple(a.model_copy(update={'formatversion':V8,'leveransdel':a.leveransdel or 'lasrapport',
        'visningsnummer':'B1' if a.id=='D-ARB.B1' else str(n)}) for n,a in enumerate(poster,1))
    namn=profil.uppgifter.get('P-ORG.namn')
    titel='Allmän riskbedömning'+(' – '+str(namn.varde) if namn and namn.varde else '')
    d=med_kallhanvisningar(Dokument(id='D-ARB',titel=titel,avsnitt=poster),rb)
    d=med_kallregisterrubrik(d,bilaga)
    b1=komplettera_radata(d.avsnitt_med_id()['D-ARB.B1'],analys,refindex)
    register=bygg_kallregister(d,rb)
    kort=avsnitt('D-ARB.B2','Kort källbilaga',(
        stycke(HELHET,['D-ARB.B1']),
        *(stycke(f'[{nr}] {rb.kallor[id].titel}. {rb.kallor[id].utgivare}. Full källversion i underlagsbilaga B1.',[id,'D-ARB.B1']) for id,nr in register.items()),
    )).model_copy(update={'visningsnummer':'B2'})
    d=d.model_copy(update={'avsnitt':(*tuple(b1 if a.id=='D-ARB.B1' else a for a in d.avsnitt),kort)})
    from riskanalys.dokument.matning import med_langdvarning
    return med_langdvarning(Dokument.model_validate(d.model_dump()), profil)
