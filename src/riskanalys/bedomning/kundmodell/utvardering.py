"""Ingen låg/normal fallback: C måste träffa en explicit granskad metodrad."""

from datetime import date

from riskanalys.bedomning.kundmodell.modeller import Kundutfall
from riskanalys.bedomning.kundmodell.pep import pep_varde
from riskanalys.bedomning.kundmodell.tabeller import radutfall
from riskanalys.fel import RiskanalysFel
from riskanalys.regelverk.modeller import Kundmall, Kundrad
from riskanalys.regelverk.villkor import Faltdef, Faltvarde, Kunskap, Sanning, kontrollera_varde


def utvardera_kundmall(mall: Kundmall, varden: dict[str, Faltvarde], datum: date) -> Kundutfall:
    """Pröva C först och därefter A/B/D med deras egna rättsliga förutsättningar."""
    for id, varde in varden.items():
        if id not in mall.falt:
            raise RiskanalysFel(f'Okänt kundfält {id}. Rätta mot kundfältregistret.')
        if varde.kunskap is Kunskap.KAND:
            falt = mall.falt[id]
            kontrollera_varde(Faltdef(id, falt.typ, falt.val), varde.varde)

    varden = dict(varden)
    okanda: set[str] = set()
    spar: list[str] = []
    forklaringar: list[str] = []
    if 'K-PEP.atgarder_kravs' in mall.falt:
        varden['K-PEP.atgarder_kravs'] = pep_varde(varden, datum)
        if varden['K-PEP.atgarder_kravs'].kunskap is Kunskap.OKAND:
            okanda.update(
                id for id in mall.falt
                if id.startswith('K-PEP.') and id != 'K-PEP.atgarder_kravs'
                and (id not in varden or varden[id].kunskap is Kunskap.OKAND)
            )

    def prova(spar_id: str) -> tuple[list[Kundrad], bool]:
        """Spara träffar och okända förutsättningar separat för varje spår."""
        traffar: list[Kundrad] = []
        osakert = False
        for rad in mall.rader:
            if rad.spar != spar_id:
                continue
            utfall = radutfall(mall, rad, varden, datum)
            if utfall.sanning is Sanning.OKANT:
                osakert = True
                okanda.update(utfall.okanda)
            elif utfall.sanning is Sanning.SANT:
                traffar.append(rad)
                spar.append(rad.id)
        return traffar, osakert

    c, c_okant = prova('C')
    nivaer = {rad.utfall['risk'] for rad in c}
    granskad = mall.c_granskning.galler(mall.c_innehallssumma())
    c_niva = next(iter(nivaer)) if len(nivaer) == 1 and not c_okant and granskad else 'preliminär'
    if c_niva == 'preliminär':
        forklaringar.append('C saknar entydig träff eller verifierad metod. Mänsklig riskbedömning krävs.')
    for id, niva in (('K-C.hog', 'hög'), ('K-C.lag', 'låg'), ('K-C.ej_hog', 'normal')):
        if id in mall.falt:
            varden[id] = (
                Faltvarde(Kunskap.OKAND) if c_niva == 'preliminär'
                else Faltvarde(Kunskap.KAND, c_niva != 'hög' if id == 'K-C.ej_hog' else c_niva == niva)
            )

    a, a_okant = prova('A')
    b, b_okant = prova('B')
    d, d_okant = prova('D')

    def beslut(rader: list[Kundrad], okant: bool) -> str:
        """Ett självständigt stopp kvarstår; olösta undantag ger preliminärt beslut."""
        utfall = {rad.utfall['beslut'] for rad in rader}
        if 'stopp' in utfall:
            return 'stopp'
        if len(utfall) != 1 or okant:
            return 'preliminart'
        return next(iter(utfall))

    a_beslut = beslut(a, a_okant)
    d_beslut = beslut(d, d_okant)
    b_atgarder = tuple(sorted({id for rad in b for id in rad.utfall['atgarder']}))
    preliminar = (a_okant or b_okant or d_okant or c_niva == 'preliminär'
                  or a_beslut == 'preliminart' or d_beslut == 'preliminart')
    if preliminar:
        forklaringar.append(
            'Pröva okända förutsättningar och undantag manuellt; mallen får inte avgöra eller skicka ett ärende.'
        )
    return Kundutfall(
        A=a_beslut, B=b_atgarder, C=c_niva, D=d_beslut, status='preliminär' if preliminar else 'slutlig',
        okanda_uppgifter=tuple(sorted(okanda)), regelspar=tuple(spar), forklaringar=tuple(forklaringar),
    )
