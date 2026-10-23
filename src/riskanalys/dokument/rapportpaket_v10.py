"""Tre obligatoriska V10-delar; aktuell återbyggnad och historisk bytekontroll."""
import json
from pathlib import Path
from riskanalys.dokument.resultatmodell_v10 import ResultatbyggeV10
from riskanalys.dokument.resultatmodell_v9 import summa,los_referens
from riskanalys.dokument.presentation_v10 import PresentationV10,bygg_presentation_v10
from riskanalys.dokument.leverans_v10 import LeveransV10
from riskanalys.fel import RiskanalysFel


def las_presentation_v10(granskningsmapp:Path,bedomning,profil,*,aktuell=True,regelbas=None):
    from riskanalys.granskning.korning import las_granskning
    from riskanalys.granskning.analysunderlag import las_fryst_analys,fryst_modellrapport
    try:
        g=granskningsmapp
        p=PresentationV10.model_validate_json((g/'presentation.json').read_text())
        b=ResultatbyggeV10.model_validate_json((g/'resultatbygge-v10.json').read_text())
        kallor=json.loads((g/'kallor-v10.json').read_text())
        d,fynd=las_granskning(g);snap=las_fryst_analys(g)
        if (d!=b.dokument or p.bygge!=summa(b.model_dump(mode='json'))
            or p.dokument!=summa(d.model_dump(mode='json'))
            or p.profil!=summa(profil.model_dump(mode='json'))
            or p.bedomning!=summa(bedomning.model_dump(mode='json'))
            or p.analys!=summa(snap.paket.model_dump(mode='json') if snap.paket else None)
            or p.fyndkalla!=fynd or p.fynd!=summa([f.model_dump(mode='json') for f in fynd])
            or p.underlag!=b.underlag or p.transformationer!=b.transformationer or p.konstruktioner!=b.konstruktioner
            or dict(b.underlag.kallsummor)!={k:summa(v) for k,v in kallor.items()}
            or kallor['analysdokument']!=json.loads((g/'analysdokument-v8.json').read_text())
            or kallor['analysdokument']!=b.analysdokument.model_dump(mode='json')
            or b.underlag.model_dump(mode='json')!=json.loads((g/'resultatunderlag-v10.json').read_text())
            or [t.model_dump(mode='json') for t in b.transformationer]!=json.loads((g/'transformationer-v10.json').read_text())):
            raise ValueError('Fryst presentationskälla avviker')
        if p!=bygg_presentation_v10(b,analys=snap.paket,fynd=fynd,bedomning=bedomning,profil=profil):
            raise ValueError('Den frysta presentationen avviker från sina egna källor')
        for post in (*b.underlag.poster,*b.underlag.brister,*b.konstruktioner):
            for r in post.kallor:los_referens(kallor,r)
        if aktuell:
            from riskanalys.dokument.rapportpaket_v8 import _regelbas_for_aktuell_presentation
            from riskanalys.dokument.arb_v10 import bygg_resultatpaket_v10
            from riskanalys.dokument.delskrivning import Tjanstresultat
            from riskanalys.drift.historik import Historik
            rb=_regelbas_for_aktuell_presentation(bedomning,regelbas)
            r={id:Tjanstresultat.model_validate(v) for id,v in kallor['skrivresultat'].items()}
            ny=bygg_resultatpaket_v10(rb,profil,bedomning,r,Historik.model_validate(kallor['historik']),
                analys=snap.paket,modellrapport=fryst_modellrapport(snap))
            from riskanalys.granskning.dokument_v10 import kravkarta_v10
            if json.loads((g/'kravkarta-v10.json').read_text())!=kravkarta_v10(rb,profil,bedomning,ny):
                raise ValueError('Kravkartan avviker från aktuellt underlag')
            if b!=ny or p!=bygg_presentation_v10(ny,analys=snap.paket,fynd=fynd,bedomning=bedomning,profil=profil):
                raise ValueError('Ny presentationspolicy eller ändrat innehåll')
        return p
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise RiskanalysFel('V10-presentationen är ändrad eller saknas. Granska resultatrapport och båda bilagorna på nytt.') from exc


def ar_v10_paket(mapp,manifest):
    """Yttre hint kan inte dölja det frysta dokumentets verkliga format."""
    if manifest.metadata.get('dokumentformat')=='D-ARB-resultat-v10':return True
    try:
        if json.loads((mapp/'leverans.json').read_text()).get('format')=='D-ARB-v10-leverans-1':return True
    except (OSError,ValueError,AttributeError):pass
    try:
        d=json.loads((mapp/'granskning/dokument.json').read_text())
        return any(a.get('formatversion')=='D-ARB-resultat-v10' for a in d.get('avsnitt',[]))
    except (OSError,ValueError,AttributeError,TypeError):return False


def verifiera_rapportpaket_v10(mapp:Path,manifest):
    from riskanalys.lagring.manifest import verifiera_manifest
    from riskanalys.bedomning.korning import las_bedomning,las_bedomningsprofil
    if manifest.metadata.get('typ')=='granskning':return []
    try:
        fel=[f'Fryst källa {n}: {x}' for n in ('granskning','bedomning') for x in verifiera_manifest(mapp/n)]
        if fel:return fel
        bm=mapp/'bedomning';p=las_presentation_v10(mapp/'granskning',las_bedomning(bm),las_bedomningsprofil(bm),aktuell=False)
        l=LeveransV10.model_validate_json((mapp/'leverans.json').read_text())
        for namn in p.leveransmall.filnamn_for(l):
            if namn not in manifest.filer or not (mapp/namn).is_file():fel.append('Obligatorisk V10-del saknas: '+namn)
        return fel
    except (OSError,ValueError,RiskanalysFel) as exc:
        return [f'V10-paketets frysta källa eller leveransbindning är skadad: {exc}']
