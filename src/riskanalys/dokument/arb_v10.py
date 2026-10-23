"""Offlinebyggare för V10 från oförändrade analys- och skrivkällor."""
from riskanalys.dokument.arb_v9 import bygg_resultatpaket_v9
from riskanalys.dokument.modeller import Dokument
from riskanalys.dokument.rapportversion import V10
from riskanalys.dokument.resultatmodell_v9 import kallartefakter, referens
from riskanalys.dokument.resultatmodell_v10 import ResultatbyggeV10, KonstruktionV10
from riskanalys.dokument.resultatrapport_v10 import bygg_resultatavsnitt_v10


def bygg_resultatpaket_v10(rb, profil, bedomning, resultat, historik, *, analys,
                          gransindex=None, modellrapport=None):
    bas = bygg_resultatpaket_v9(rb, profil, bedomning, resultat, historik, analys=analys,
                               gransindex=gransindex, modellrapport=modellrapport)
    huvud = bygg_resultatavsnitt_v10(rb, profil, bedomning, resultat, historik,
                                    analys=analys, underlag=bas.underlag)
    bilagor = tuple(a.model_copy(update={'formatversion': V10}) for a in bas.dokument.avsnitt
                    if a.leveransdel != 'resultatrapport')
    dokument = Dokument.model_validate({'id': bas.dokument.id, 'titel': bas.dokument.titel,
                                        'avsnitt': [a.model_dump(mode='json') for a in (*huvud, *bilagor)]})
    transformationer = tuple(t.model_copy(update={'efter': V10}) if t.orsak == 'format' else t
                             for t in bas.transformationer)
    kallor = kallartefakter(rb, profil, bedomning, resultat, historik, analys, bas.analysdokument)
    konstruktioner = []
    for a in huvud:
        positioner = [(f'{a.id}/stycken/{n}', s) for n, s in enumerate(a.stycken)]
        positioner += [(f'{a.id}/tabeller/{t.id}/rader/{ri}/celler/{ci}', c)
                       for t in a.tabeller for ri, r in enumerate(t.rader) for ci, c in enumerate(r.celler)]
        for pos, post in positioner:
            refs = []
            for kod in post.referenser:
                if kod.startswith('kalla:'):
                    art, ptr = kod.removeprefix('kalla:').split('#', 1)
                    refs.append(referens(kallor, art, ptr))
            slag = 'lokalt_original' if post.proveniens == 'lokal' else (
                'regelbas' if refs and all(r.artefakt == 'regelbas' for r in refs) else 'programmall')
            konstruktioner.append(KonstruktionV10(placering=pos, produktionsslag=slag, kallor=tuple(refs)))
    return ResultatbyggeV10(dokument=dokument, analysdokument=bas.analysdokument, underlag=bas.underlag,
        transformationer=transformationer, konstruktioner=tuple(konstruktioner))
