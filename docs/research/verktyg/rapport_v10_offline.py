"""V10:s två fulla syntetiska referenspaket utan produktintegration eller attester."""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def main(argv=None):
    from docs.research.verktyg.analyslagen import bygg
    from riskanalys.regelverk.laddning import ladda_regelbas
    from riskanalys.regelverk.urval import valj
    from riskanalys.dokument.arb_v10 import bygg_resultatpaket_v10
    from riskanalys.dokument.presentation_v10 import bygg_presentation_v10
    from riskanalys.dokument.rapportvyer_v10 import bygg_rapportvyer_v10
    from riskanalys.dokument.rendering_v10 import rendera_rapportvyer_v10
    from riskanalys.dokument.leverans_v10 import LeveransV10
    from riskanalys.dokument.resultatmodell_v9 import kallartefakter
    from riskanalys.drift.historik import Historik, las_historik
    from riskanalys.granskning.kontroller import granska
    from riskanalys.granskning.dokument_v10 import resultatfynd_v10, kravkarta_v10
    from riskanalys.granskning.modeller import Fynd
    from riskanalys.lagring.manifest import skriv_manifest
    from riskanalys.granskning.korning import godkanda_utkast, oppna_fragor
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ut', type=Path, required=True)
    p.add_argument('--fran', type=Path, help='Återanvänd exakt sparade syntetiska källor från en tidigare offlinekörning.')
    a = p.parse_args(argv)
    a.ut = a.ut.resolve()
    a.ut.mkdir(parents=True, exist_ok=False)
    rb = ladda_regelbas()
    dag = date(2026, 10, 23)
    for namn in ('fyra_tjanster', 'med_betalningsmandat'):
        rot = a.ut / namn
        rot.mkdir(parents=True, exist_ok=False)
        if a.fran:
            from types import SimpleNamespace
            from riskanalys.profil.modeller import Profil
            from riskanalys.bedomning.modeller import Bedomning
            from riskanalys.analys.modeller import Analyspaket
            from riskanalys.regelverk.modeller import Regelbas
            from riskanalys.dokument.delskrivning import Tjanstresultat
            data = json.loads((a.fran / namn / 'kallor.json').read_text())
            sparad = Regelbas.model_validate(data['regelbas'])
            if sparad != rb:
                raise ValueError('Sparad regelbas avviker. Bygg nya referensfall för den nya versionen.')
            f = SimpleNamespace(regelbas=rb, profil=Profil.model_validate(data['profil']),
                bedomning=Bedomning.model_validate(data['bedomning']), analys=Analyspaket.model_validate(data['analys']))
            # JSON bevarar ISO-värdet men inte datumtypen i Uppgifts värdeunion.
            f.profil=f.profil.model_copy(update={'uppgifter':{id:u.model_copy(update={'varde':date.fromisoformat(u.varde)})
                if id in rb.falt and rb.falt[id].typ=='datum' and isinstance(u.varde,str) else u
                for id,u in f.profil.uppgifter.items()}})
            r = {id: Tjanstresultat.model_validate(v) for id, v in data['skrivresultat'].items()}
            h = Historik.model_validate(data['historik'])
            kontext = json.loads((a.fran / namn / 'granskningskontext.json').read_text())
            from riskanalys.drift.modellrisk import Modellvalidering
            rapport = Modellvalidering.model_validate(kontext['modellrapport']) if kontext['modellrapport'] else None
            brister = tuple(kontext['analysbrister_filer'])
        else:
            f = bygg(rb, rot / 'arbetsdata', namn, 'direkt2')
            from types import SimpleNamespace
            from riskanalys.lagring.korningar import senaste_korning
            from riskanalys.bedomning.korning import BEDOMNINGAR, las_bedomning, las_bedomningsprofil
            from riskanalys.analys.lagring import las_analyssnapshot_last
            from riskanalys.granskning.analysunderlag import fryst_modellrapport
            byra = rot / 'arbetsdata/byra'
            bm = senaste_korning(byra, BEDOMNINGAR, 'syntetisk referens')
            r, um = godkanda_utkast(byra, bm)
            snapshot = las_analyssnapshot_last(byra, rb, dag, bedomningsmapp=bm, utkastmapp=um)
            if snapshot.paket is None:
                raise ValueError('Referensfallet saknar sparad analys.')
            f = SimpleNamespace(regelbas=rb, profil=las_bedomningsprofil(bm),
                                bedomning=las_bedomning(bm), analys=snapshot.paket)
            h, rapport, brister = las_historik(byra), fryst_modellrapport(snapshot), snapshot.brister
            kontext = {'modellrapport': rapport.model_dump(mode='json') if rapport else None,
                       'analysbrister_filer': list(brister), 'bedomning': bm.name, 'skrivutkast': um.name}
        b = bygg_resultatpaket_v10(rb, f.profil, f.bedomning, r, h, analys=f.analys, modellrapport=rapport)
        u = valj(rb, f.bedomning.regelpaket, f.bedomning.datum, f.bedomning.lan)
        fynd = granska(rb, u, f.profil, f.bedomning, b.analysdokument, h, dag, oppna_fragor(r),
                       skrivresultat=r, analys=f.analys, modellrapport=rapport, analysbrister_filer=brister)
        extra = resultatfynd_v10(rb, f.profil, f.bedomning, r, h, analys=f.analys, bygge=b, dokument=b.dokument,
                                 modellrapport=rapport)
        fynd = (*fynd, *(Fynd(id=f'F-{dag}-{i:03d}', **x) for i, x in enumerate(extra, len(fynd) + 1)))
        pr = bygg_presentation_v10(b, analys=f.analys, fynd=fynd, bedomning=f.bedomning, profil=f.profil)
        lev = LeveransV10(datum=dag, bedomning='offline-referens', granskning='offline-referens')
        rendera_rapportvyer_v10(bygg_rapportvyer_v10(b.dokument), f.profil, rot / 'word', presentation=pr, leverans=lev)
        def spara(namn, data):
            (rot / namn).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        spara('kallor.json', kallartefakter(rb, f.profil, f.bedomning, r, h, f.analys, b.analysdokument))
        spara('bygge.json', b.model_dump(mode='json'))
        spara('presentation.json', pr.model_dump(mode='json'))
        spara('kravkarta.json', kravkarta_v10(rb, f.profil, f.bedomning, b))
        spara('granskningskontext.json', kontext)
        spara('fynd.json', [x.model_dump(mode='json') for x in fynd])
        spara('matning.json', {'format': b.dokument.formatversion, 'maskinfynd': len(fynd),
            'presentationsfynd': len(extra), 'pdf_granskad': False, 'pdf_sidor': None,
            'nya_intagsfragor': 0, 'verkliga_ai_anrop': 0})
        skriv_manifest(rot, {'typ': 'offline-forhandsvisning-v10', 'regelbas': rb.kontrollsumma})
        print(namn, f'{len(fynd)} ofiltrerade maskinfynd; {len(extra)} presentationsfynd', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
