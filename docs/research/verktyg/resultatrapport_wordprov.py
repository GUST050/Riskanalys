"""R3:s tre Word-delar i två syntetiska provfall. Ingen produktgranskning eller fastställelse.

Kör med projektets Python 3.12 och ny --ut-mapp. Fyndlistan är en uttryckligen
tom provlista; verklig V9-granskning och paketexport tillkommer i R4–R5.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))


def main(argv=None):
    from docs.research.verktyg.analyslagen import bygg
    from docs.research.verktyg.resultatrapport_offline import FALL
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
    from riskanalys.dokument.rapportvyer_v9 import bygg_rapportvyer_v9
    from riskanalys.dokument.presentation_v9 import bygg_presentation_v9
    from riskanalys.dokument.leverans_v9 import LeveransV9,DELAR
    from riskanalys.dokument.rendering_v9 import rendera_rapportvyer_v9
    from riskanalys.dokument.resultatmodell_v9 import kallartefakter
    from riskanalys.drift.historik import Historik
    from tester.enhet.test_arb_v8 import skriv
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ut',type=Path,required=True)
    args=p.parse_args(argv);args.ut.mkdir(parents=True,exist_ok=False);rb=ladda_regelbas()
    def spara(path,obj):
        path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def ord(d):
        return len(d.titel.split())+sum(len(s.text.split()) for a in d.avsnitt for s in a.stycken)+sum(
            len(c.text.split()) for a in d.avsnitt for t in a.tabeller for r in t.rader for c in r.celler)
    for namn in FALL:
        with tempfile.TemporaryDirectory(prefix='v9-wordprov-') as tmp:
            f=bygg(rb,Path(tmp).resolve(),namn,'direkt2');r=skriv(f);h=Historik()
            b=bygg_resultatpaket_v9(rb,f.profil,f.bedomning,r,h,analys=f.analys)
            presentation=bygg_presentation_v9(b,analys=f.analys,fynd=(),bedomning=f.bedomning,profil=f.profil)
            l=LeveransV9(datum=date(2026,10,23),bedomning='syntetisk-R3-'+namn,granskning='R3-wordprov-ingen-produktgranskning')
            ut=args.ut/namn
            paths=rendera_rapportvyer_v9(bygg_rapportvyer_v9(b.dokument),f.profil,ut,presentation=presentation,leverans=l)
            for fil,obj in (('bygge.json',b),('presentation.json',presentation),('leverans.json',l)):
                (ut/fil).write_text(obj.model_dump_json(indent=2),encoding='utf-8')
            spara(ut/'kallor.json',kallartefakter(rb,f.profil,f.bedomning,r,h,f.analys,b.analysdokument))
            m={'ordkontrakt':'titel + stycken + dataceller i frysta renderade vyer; leveransdekor/hänvisningsrader mäts i faktisk DOCX/PDF',
                'ord':dict(zip(DELAR,(ord(d) for d in presentation.renderade),strict=True)),
                'v8_kanonisk_samma_kontrakt':ord(b.analysdokument),
                'fyndkalla':'Tom syntetisk provlista, inte körd V9-produktgranskning.',
                'filer':[p.name for p in paths],'pdf_granskad':False}
            spara(ut/'matning.json',m);print(namn,json.dumps(m,ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
