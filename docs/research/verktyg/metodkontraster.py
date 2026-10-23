"""Frysta syntetiska kontraster för D utan experimentmutation av motorn."""
from pathlib import Path
import json
from riskanalys.regelverk.laddning import ladda_regelbas
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.profil.modeller import Kombinationsgrupp, Uppgift
from tester.fixturer.faktorer import faktorprofil
from tester.fixturer.arb_kedja import andrat,bedom_kedja
from riskanalys.lagring.kontrollsumma import for_fil
from docs.research.verktyg.metodsteg import jamfor


def jamforelser(fore,efter,baslinje):
    return jamfor(fore,efter),jamfor(baslinje,efter)


def main():
    rb=ladda_regelbas();rot=Path('.superpowers/evidens/2026-10-23-metodbeslut');ut=rot/'kontraster3';ut.mkdir(exist_ok=False)
    fall={}
    for namn,faktorer in [('inga',()),('ideell',('S-ARB-05',)),('pep',('S-KUND-02',)),
                         ('ideell_pep_okant_overlapp',('S-ARB-05','S-KUND-02')),
                         ('riskbransch',('S-KUND-01',)),('riskbransch_bankdata',('S-KUND-01',)),
                         ('flera_orsaker',('S-ARB-05','S-KUND-02','S-GEO-01','S-KUND-01'))]:
        fall[namn]=faktorprofil(rb,faktorer,alla_tjanster=True,med_bankdata=namn=='riskbransch_bankdata')
    # Varje indikator prövas ensam genom den riktiga motorn, inklusive trösklar/ersättning.
    for s in rb.sarbarheter.values():
        if s.omrade!='tj':fall['ensam_'+s.id]=faktorprofil(rb,(s.id,),alla_tjanster=True)
    bas=fall['ideell_pep_okant_overlapp'];mall=bas.uppgifter['P-KUND.antal_aktiva']
    grupp=Kombinationsgrupp(id='syntetiskt-overlapp',tjanst='T-RED-04',population='kunder',
        avgransning='Endast syntetiska lönekunder med både PEP och ideell anknytning.',
        beskrivning='Syntetisk verifierad korsning, inte härledd ur marginaltal.',sarbarheter=('S-ARB-05','S-KUND-02'),
        antal=mall.model_copy(update={'varde':1}),bas=mall)
    fall['ideell_pep_kant_overlapp']=bas.model_copy(update={'kombinationsgrupper':(grupp,)})
    for namn,varde in [('lokal_nolla',0),('lokal_positiv',1),('lokal_okand',None)]:
        p=fall['riskbransch']
        p=andrat(p,'P-TJ.red04_antal_riskbransch',varde=varde,status='saknas' if varde is None else 'bekräftad')
        fall[namn]=p
    for namn,p in fall.items():
        from riskanalys.profil.modeller import Profil
        Profil.model_validate_json(p.model_dump_json())
        (ut/(namn+'-profil.json')).write_text(p.model_dump_json(indent=2))
    def kor(rb):
        out={}
        for namn,p in fall.items():
            _,b=bedom_kedja(rb,p)
            out[namn]={'profil_summa':for_fil(ut/(namn+'-profil.json')),'utfall':b.model_dump(mode='json')}
        return out
    fore=kor(Regelbas.model_validate_json((rot/'D1/fore/regelbas.json').read_text()))
    baslinje=kor(Regelbas.model_validate_json((rot/'baslinje-2.0.0/regelbas.json').read_text()))
    (ut/'baslinje-2.0.0-utfall.json').write_text(json.dumps(baslinje,ensure_ascii=False,indent=2))
    for id in ('D1','D2','D3','D4','D5','D6','D7','D8','D9','D-LAGRE'):
        step=Regelbas.model_validate_json((rot/id/'efter/regelbas.json').read_text());efter=kor(step)
        diff,samlat=jamforelser(fore,efter,baslinje)
        (ut/(id+'-efter.json')).write_text(json.dumps(efter,ensure_ascii=False,indent=2))
        (ut/(id+'-samlat-mot-2.0.0.json')).write_text(json.dumps(samlat,ensure_ascii=False,indent=2))
        (ut/(id+'-jamforelse.json')).write_text(json.dumps(diff,ensure_ascii=False,indent=2))
        print(id,'sänkta led',sum(len(x['sankta_led']) for x in diff.values()),'borttagna scenarier',sum(len(x['borttagna_scenarier']) for x in diff.values()),flush=True)
        fore=efter
    # Två tillåtna kundfördelningar har samma 60 kunder och fyra marginaltal 24.
    a=[list(range(4)) for _ in range(24)]+[[] for _ in range(36)]
    b=[list(range(4)) for _ in range(12)]+[[t] for t in range(4) for _ in range(12)]
    marg=lambda x:[sum(t in kund for kund in x) for t in range(4)]
    assert marg(a)==marg(b)==[24]*4 and len(a)==len(b)==60
    (ut/'marginalkontrast.json').write_text(json.dumps({'a':a,'b':b,'marginaler':marg(a),
        'flertjanstkunder_a':sum(len(x)>1 for x in a),'flertjanstkunder_b':sum(len(x)>1 for x in b),
        'slutsats':'Marginaltal bestämmer inte faktiskt kundöverlapp eller vilka riskfaktorer som sammanfaller.'},ensure_ascii=False,indent=2))
    print(len(fall),'kontrastprofiler; identiska bytes i varje D-version')

if __name__=='__main__':main()
