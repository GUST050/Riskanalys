"""Två verkliga syntetiska exportkedjor, samma V8/V9-källor och ofiltrerade fynd."""
import argparse,json,sys
from pathlib import Path
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))


def main(argv=None):
    from docs.research.verktyg.analyslagen import bygg,ord_och_upprepning
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.dokument.export import kor_export_utkast
    from riskanalys.lagring.manifest import verifiera_manifest
    from riskanalys.dokument.resultatmodell_v9 import summa
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ut',type=Path,required=True);a=p.parse_args(argv)
    a.ut=a.ut.resolve();a.ut.mkdir(parents=True,exist_ok=False);rb=ladda_regelbas();dag=date(2026,10,23)
    for namn in ('fyra_tjanster','med_betalningsmandat'):
        rot=a.ut/namn;f=bygg(rb,rot,namn,'direkt2');byra=rot/'byra';m={'arbetsbord':f.arbetsbord,'format':{}}
        for v in ('v8','v9'):
            gm=kor_granskning(byra,rb,dag,rapportformat=v)
            d,fynd=las_granskning(gm)
            e=kor_export_utkast(byra,dag,granskningsmapp=gm,regelbas=rb)
            assert not verifiera_manifest(e)
            m['format'][v]={'granskning':str(gm),'export':str(e),'fynd':len(fynd),
                'matning':ord_och_upprepning(d,f.profil)}
        # Sparade granskningar delar exakt bedömning, skrivresultat, historik och analys.
        from riskanalys.lagring.manifest import las_manifest
        mg=[las_manifest(Path(m['format'][v]['granskning'])).metadata for v in ('v8','v9')]
        assert all(mg[0][x]==mg[1][x] for x in ('bedomning','utkast','utkastmanifest','historik','analysbindning'))
        m['samma_kallor']={x:mg[0][x] for x in ('bedomning','utkast','utkastmanifest','historik','analysbindning')}
        (rot/'matning.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
        print(namn,json.dumps(m['format'],ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
