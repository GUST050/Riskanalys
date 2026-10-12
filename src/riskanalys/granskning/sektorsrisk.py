"""B-13 hittar avsaknad av belagd lokal motivering, inte dess juridiska kvalitet."""
from riskanalys.bedomning.sektorsrisk import sektorsavvikelser
from riskanalys.dokument.underlag import tjanster_med_avsnitt

def sektorsfynd(regelbas, bedomning, profil):
    avsnitt={t.tjanst:id for id,t in tjanster_med_avsnitt(bedomning)}
    post=regelbas.bristmonster['B-13']
    return [dict(typ="bristmonster",regel="B-13",allvar=post.allvar,grund=post.grund,avsnitt=avsnitt[a.tjanst],
        beskrivning=f"{a.tjanst}: {a.orsak} Belagd motivering mot {a.referens} saknas.",
        atgard="Bekräfta tjänstens sektorsmotivering med källa, datum och ansvarig. Kvaliteten prövas i sakgranskningen.")
        for a in sektorsavvikelser(regelbas,bedomning,profil) if not a.motiverad]
