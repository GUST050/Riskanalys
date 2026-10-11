"""NRA:s originalskala bevaras; jämförbarhet är ett eget metodval."""
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas, Strikt, _summa

class Sektorsavvikelse(Strikt):
    tjanst: str
    referens: str
    dimension: str = "inneboende_penningtvatt"
    metod_id: str
    motiverad: bool
    orsak: str

def sektorsavvikelser(regelbas: Regelbas, bedomning: Bedomning, profil: Profil) -> tuple[Sektorsavvikelse, ...]:
    poster=[]
    metod=regelbas.skalmappning
    for b in bedomning.tjanster:
        if b.erbjuds is False or b.inneboende is None:
            continue
        t=regelbas.tjanster[b.tjanst]
        ref=regelbas.sektorsreferenser.get(t.sektorreferens)
        if ref is None:
            continue
        giltig=bool(metod and metod.sakkunnig.galler(_summa(metod.model_dump(mode="json",exclude={"sakkunnig"}))))
        jamforbar=metod.mappning.get(ref.niva) if giltig else None
        if jamforbar==b.inneboende.risk:
            continue
        slug=t.erbjuds_falt.removesuffix("_erbjuds")
        u=profil.uppgifter.get(slug+"_sektorsmotivering")
        # Innehållets kvalitet granskas av människa; ensamt nivåord är inte en motivering.
        motiverad=bool(u and profil.ar_bekraftad(slug+"_sektorsmotivering") and u.kalla and u.kalla.strip() and u.datum and u.bekraftad_av
                      and isinstance(u.varde,str) and len(u.varde.split())>=5)
        poster.append(Sektorsavvikelse(tjanst=t.id,referens=ref.id,metod_id=metod.id if metod else "BT-SEKTOR-01",
            motiverad=motiverad,orsak="Avvikande inneboende risk." if giltig else "Skalornas jämförbarhet är ännu inte sakkunniggranskad."))
    return tuple(poster)
