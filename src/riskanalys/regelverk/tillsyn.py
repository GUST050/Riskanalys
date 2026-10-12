"""PTF 16 §: tillsyn efter säte/folkbokföring; PTL 1:2 skiljer yrkesroller."""

from riskanalys.fel import RiskanalysFel
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas, Strikt
from riskanalys.regelverk.urval import lydelse_galler
from riskanalys.regelverk.villkor import Kunskap, Sanning, tolka_villkor, utvardera
from typing import Literal

LAN_PER_OMRADE = {
    "RP-RED-VG": ("Dalarna", "Gävleborg", "Halland", "Värmland", "Västra Götaland", "Örebro"),
    "RP-RED-SKANE": ("Skåne", "Blekinge", "Kronoberg", "Jönköping", "Kalmar", "Östergötland"),
    "RP-RED-STHLM": ("Stockholm", "Södermanland", "Gotland", "Västmanland", "Uppsala", "Jämtland", "Västernorrland", "Västerbotten", "Norrbotten"),
}


class Omfattningsbeslut(Strikt):
    paket_id: str | None
    punkter: tuple[int, ...]
    status: Literal["preliminär", "slutlig"]
    regelspar: tuple[str, ...]
    hinder: tuple[str, ...]


def tillsynsomrade(lan: str, utlandsk_filial: bool) -> str:
    omrade = next((paket for paket, lanlista in LAN_PER_OMRADE.items() if lan in lanlista), None)
    if omrade is None:
        raise RiskanalysFel(f"Okänt län {lan!r}. Ange sätes- eller folkbokföringslän enligt PTF 16 §.")
    return "RP-RED-STHLM" if utlandsk_filial else omrade


def rattlig_omfattning(regelbas: Regelbas, profil: Profil) -> Omfattningsbeslut:
    from riskanalys.profil.omfattning import kompatibilitetsvy
    profil = kompatibilitetsvy(profil, regelbas)
    varden = profil.faltvarden()
    hinder: list[str] = []

    def kant(falt_id: str):
        falt = varden.get(falt_id)
        if falt is None or falt.kunskap is not Kunskap.KAND:
            hinder.append(f"Bekräfta {falt_id}; rättslig omfattning kan inte avgöras från okänd eller ej tillämplig uppgift.")
            return None
        return falt.varde

    lan = kant("P-ORG.sateslan")
    filial = kant("P-ORG.utlandsk_filial")
    paket = None
    if isinstance(lan, str) and type(filial) is bool:
        try:
            paket = tillsynsomrade(lan, filial)
        except RiskanalysFel as exc:
            hinder.append(str(exc))
        if profil.byra.lan != lan and not filial:
            hinder.append(f"Profilens säteslän {lan} stämmer inte med profilens län {profil.byra.lan}. Rätta grundsvaret via intaget eller bekrafta så att län och regelpaket uppdateras tillsammans; berörda underlag behöver bekräftas igen.")
        if paket and profil.byra.regelpaket != paket:
            hinder.append(f"Manuellt regelpaket {profil.byra.regelpaket} stämmer inte med tillsynsområdet {paket}. Välj rätt paket.")
    if lan is not None and not isinstance(lan, str):
        hinder.append("P-ORG.sateslan har fel typ. Bekräfta ett län.")
    if filial is not None and type(filial) is not bool:
        hinder.append("P-ORG.utlandsk_filial har fel typ. Bekräfta ja eller nej.")
    for service, roller in (("T-RED-01", ("P-VERK.bokforing", "P-VERK.auktoriserad_revision")),
                            ("T-RED-02", ("P-VERK.bokforing", "P-VERK.auktoriserad_revision")),
                            ("T-SKATT-01", ("P-VERK.skatteradgivning",)),
                            *[(i,("P-VERK.bolagstjanster",)) for i in ("T-BOLAG-01", "T-BOLAG-02", "T-BOLAG-03")]):
        t = regelbas.tjanster.get(service)
        if t and profil.ar_bekraftad(t.erbjuds_falt) and profil.uppgifter[t.erbjuds_falt].varde is True:
            if not any(profil.ar_bekraftad(r) and profil.uppgifter[r].varde is True for r in roller):
                hinder.append(f"{service}: faktiskt erbjuden tjänst kräver bekräftad verksamhetsroll {', '.join(roller)}.")
    for falt_id in ("P-VERK.trust", "P-VERK.nominell_aktieagare"):
        if kant(falt_id) is True:
            hinder.append(f"{falt_id}: tjänsten ligger utanför paketets avgränsning och kräver sakkunnig granskning.")
    punkter: set[int] = set()
    spar = []
    if not regelbas.tillamplighet:
        hinder.append("Beslutstabellen för rättslig tillämplighet saknas. Komplettera regelbasen före användning.")
    for rad in regelbas.tillamplighet.values():
        giltiga = [regelbas.lydelser[i] for i in rad.lydelser if i in regelbas.lydelser and lydelse_galler(regelbas.lydelser[i], profil.byra.datum)]
        if len(giltiga) != 1:
            hinder.append(f"{rad.id}: saknar entydig rättslig lydelse på profilens datum.")
            continue
        utfall = utvardera(tolka_villkor(rad.villkor, regelbas.faltdefinitioner()), varden)
        if utfall.sanning is Sanning.OKANT:
            hinder += [f"Bekräfta {falt_id} för tillämplighetsprövningen {rad.id}." for falt_id in sorted(utfall.okanda)]
        if utfall.sanning is Sanning.SANT:
            punkter.add(rad.punkt)
            spar.append(rad.id)
    if punkter & {18, 21, 22}:
        hinder.append("Yrkesroll enligt punkt 18, 21 eller 22 behöver ett särskilt avgränsat och sakkunniggranskat paket; detta paket täcker 19, 20 och 23.")
    if not punkter:
        hinder.append("Ingen rättslig verksamhetskategori är bekräftad. Beskriv faktiskt utfört arbete innan bedömningen används.")
    return Omfattningsbeslut(paket_id=paket, punkter=tuple(sorted(punkter)),
                            status="preliminär" if hinder else "slutlig", regelspar=tuple(spar), hinder=tuple(dict.fromkeys(hinder)))
