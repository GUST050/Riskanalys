"""Syntetisk V8-export med frysta fakta och skrivsvar, utan nätverk eller verkliga attester."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from docs.research.verktyg.matkontrakt import frysta_skrivsvar


def hasha(v):
    return 'sha256:'+sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ut',required=True,type=Path)
    p.add_argument('--fall',required=True,choices=('fyra_tjanster','med_betalningsmandat'))
    p.add_argument('--analyslage',choices=('schema1','direkt2','overforing2'),default='overforing2')
    args=p.parse_args(argv)
    from docs.research.verktyg.analyslagen import bygg,ord_och_upprepning
    from tester.fixturer.gemensam_analys import bygg_gemensamt_fall
    from tester.enhet.test_arb_v8 import skriv
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.dokument.arb_v8 import bygg_arb_v8
    from riskanalys.drift.historik import Historik
    from riskanalys.dokument.rapportvyer import bygg_rapportvyer
    from riskanalys.dokument.presentation_v8 import bygg_presentation
    from riskanalys.dokument.rendering import rendera_rapportvyer
    from riskanalys.dokument.matning import dokumentord
    rb=ladda_regelbas();ut=args.ut.resolve()
    if ut.exists():p.error('Välj en ny utdatamapp; tidigare provresultat skrivs inte över.')
    with tempfile.TemporaryDirectory() as tmp:
        f=bygg(rb,Path(tmp).resolve(),args.fall,args.analyslage)
        from types import SimpleNamespace
        svar=skriv(SimpleNamespace(regelbas=rb,profil=f.profil,bedomning=f.bedomning))
        d=bygg_arb_v8(rb,f.profil,f.bedomning,svar,Historik(),analys=f.analys)
        pres=bygg_presentation(d,analys=f.analys,fynd=(),bedomning=f.bedomning,profil=f.profil)
        ut.mkdir(parents=True)
        filer=rendera_rapportvyer(bygg_rapportvyer(d),f.profil,'UTKAST – SYNTETISKT SLUTPROV, EJ FASTSTÄLLT',ut,
            analys=f.analys,fynd=(),bedomning=f.bedomning,presentation=pres)
        data={'fall':args.fall,'format':d.formatversion,'analysschema':f.analys.schemaversion,'analyslage':args.analyslage,'arbetsbord':f.arbetsbord,'syntetiskt':True,
            'tillstand':'syntetiska ogranskade svar; överföringsoriginal bevaras enbart i overforing2','profil':hasha(f.profil.model_dump(mode='json')),
            'motor':hasha(f.bedomning.model_dump(mode='json')),'skrivsvar':hasha(frysta_skrivsvar(svar)),
            'regelbas':rb.kontrollsumma,'ord':dokumentord(d,f.profil),'matning':ord_och_upprepning(d,f.profil),
            'filer':{x.name:'sha256:'+sha256(x.read_bytes()).hexdigest() for x in ut.glob('*.docx')}}
        (ut/'slutprov.json').write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(data,ensure_ascii=False,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
