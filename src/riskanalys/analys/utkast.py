"""Förifyll redigerbara ogranskade svar från bekräftad profil och motor."""
from collections import Counter
from riskanalys.intag.fordelning import kan_ateranvandas
from riskanalys.analys.modeller import (
    Analysbelagg, Analysblock, Analyspaket, Scenarioanalys, Sarbarhetsprovning, Tjansteanalys,
)
from riskanalys.analys.provning import ALLTID, faktisk_reduktion
from riskanalys.analys.exponering import forifylld_exponering


def forifyll_analys(rb,profil,bedomning,bindning,*,schema=1) -> Analyspaket:
    belagg=tuple(Analysbelagg(id='profil:'+f,profilfalt=(f,),datum=u.datum,period=u.period)
                 for f,u in sorted(profil.uppgifter.items())
                 if f in rb.falt and profil.ar_bekraftad(f) and u.datum and u.kalla and u.bekraftad_av
                 and kan_ateranvandas(rb, profil, f))
    erbjudna=[t for t in bedomning.tjanster if t.erbjuds is not False]
    antal=Counter(h for t in erbjudna for h in rb.tjanster[t.tjanst].hot)
    def scenario(id,hot):
        h=rb.hot[hot]
        return Scenarioanalys(id=id,hot=(hot,),rubrik=h.namn,handelseforlopp=h.beskrivning)
    gemensamma=tuple(scenario('gem:'+h,h) for h,n in sorted(antal.items()) if n>1)
    tjanster=[]
    giltiga={f for b in belagg for f in b.profilfalt}
    for t in erbjudna:
        kat=rb.tjanster[t.tjanst]
        exponering,exponeringsbelagg=forifylld_exponering(rb,profil,t.tjanst,giltiga)
        block=[]
        for n in range(1,17):
            aktiv='aktiv' if n in ALLTID else 'okand'
            skal='Alltid obligatorisk lokal prövning.' if n in ALLTID else 'Ta ställning till relevansen utifrån uppdraget.'
            if n==12:
                aktiv='aktiv' if faktisk_reduktion(t) else 'ej_tillamplig'
                skal='Motorn redovisar reduktion.' if faktisk_reduktion(t) else 'Motorn redovisar ingen riskreduktion.'
            if n==5:
                f=[f for f in ('P-RISK.extern_kyc','P-RISK.utkontraktering') if f in rb.falt]
                if f and all(profil.ar_bekraftad(id) for id in f):
                    finns=any(profil.uppgifter[id].varde is True for id in f)
                    aktiv='aktiv' if finns else 'ej_tillamplig'
                    skal='Bekräftad extern KYC/utkontraktering.' if finns else 'Bekräftat att extern KYC/utkontraktering inte används.'
            block.append(Analysblock(nummer=n,aktivering=aktiv,motivering=skal))
        sarbarheter=[]
        for omrade in ('kund','kanal','geo','verk','tjanst'):
            if omrade == 'tjanst' and not any(rb.sarbarheter[s].omrade == 'tj' for s in kat.sarbarheter):
                continue
            ids=tuple(s for s in kat.sarbarheter if rb.sarbarheter[s].omrade==('tj' if omrade == 'tjanst' else omrade))
            sarbarheter.append(Sarbarhetsprovning(id=t.tjanst+':'+omrade,omrade=omrade,sarbarheter=ids))
        tjanster.append(Tjansteanalys(tjanst=t.tjanst,block=tuple(block),exponering=exponering,
            exponeringsbelagg=exponeringsbelagg,
            scenarier=tuple(scenario(t.tjanst+':'+h,h) for h in kat.hot if antal[h]==1),
            sarbarhetsprovningar=tuple(sarbarheter),
            reduktionsprovning='okand' if faktisk_reduktion(t) else 'ej_reduktion',
            pt_motivering=f'Motorns PT-utfall: {t.inneboende.risk if t.inneboende else "okänt"}; kvarstående {t.kvarstaende or "okänd"}. Lokal rimlighetsprövning återstår.',
            tf_motivering=f'Motorns TF-utfall: {t.terrorfinansiering.risk if t.terrorfinansiering else "okänt"}. Separat lokal prövning återstår.'))
    paket=Analyspaket(bindning=bindning,belagg=belagg,gemensamma_scenarier=gemensamma,tjanster=tuple(tjanster))
    if schema==1:
        return paket
    if schema!=2:
        raise ValueError('Välj analysschema 1 eller 2.')
    from riskanalys.analys.gemensam import forifyll_gemensamt
    return forifyll_gemensamt(rb,paket)
