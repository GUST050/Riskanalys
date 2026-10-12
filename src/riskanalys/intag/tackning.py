"""Underlaget kontrolleras separat från juridiska attester och dokumentgranskning."""
from riskanalys.fel import RiskanalysFel
from riskanalys.intag.modeller import Tackning
from riskanalys.profil.hantering import kontrollera_profil, saknade_kritiska
from riskanalys.profil.modeller import Profil
from riskanalys.profil.omfattning import aktivt, kompatibilitetsvy
from riskanalys.regelverk.intagskontrakt import intagskontraktsfel
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.tillsyn import rattlig_omfattning
from riskanalys.regelverk.urval import valj


def tackning(rb: Regelbas, profil: Profil) -> Tackning:
    p = kompatibilitetsvy(profil, rb)
    aktiva = [f for f in rb.falt.values() if f.intag and f.intag.obligatorisk and not f.alias_for and not f.basfalt and aktivt(f,p,rb)]
    saknade = {f.id for f in aktiva if not p.ar_bekraftad(f.id)}
    from riskanalys.intag.kvalitet import kvalitetsbrister
    hinder = [*intagskontraktsfel(rb), *kvalitetsbrister(rb,p)]
    for f in aktiva:
        if p.ar_bekraftad(f.id) and f.typ == 'text' and not str(p.uppgifter[f.id].varde or '').strip():
            saknade.add(f.id)
    try:
        kontrollera_profil(p, rb)
        u = valj(rb, p.byra.regelpaket, p.byra.datum, p.byra.lan)
        saknade.update(saknade_kritiska(p, rb, u))
    except RiskanalysFel as exc:
        hinder.append(str(exc))
    if rb.utokade_krav:
        hinder.extend(rattlig_omfattning(rb,p).hinder)
    if p.ar_bekraftad('P-BESK.ovriga_forhallanden') and p.uppgifter['P-BESK.ovriga_forhallanden'].varde is True:
        hinder.append('Ytterligare riskförhållanden finns. Komplettera riskmodellen och granska den innan ett helt utkast skapas.')
    return Tackning(len(aktiva), sum(p.ar_bekraftad(f.id) and f.id not in saknade for f in aktiva),
                    tuple(sorted(saknade)), tuple(dict.fromkeys(hinder)))
