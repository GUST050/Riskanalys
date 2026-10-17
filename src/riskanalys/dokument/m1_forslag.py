"""M1-förslaget i B1: ett metodförslag till sakkunnig som inte påverkar något beräknat utfall."""
from riskanalys.dokument.arb_v5 import stycke
from riskanalys.dokument.modeller import Textstycke

M1_FORSLAG_RUBRIK = 'Förslag till sakkunnig, M1'
_TEXT = (f'{M1_FORSLAG_RUBRIK} (inte beslutat): kvarstående risk sänks först när relevant räckvidd för tjänstens '
         'scenarier och kontrollens faktiska effekt under perioden är belagda lokalt. Länsstyrelsens vägledning anger att '
         'åtgärdernas effektivitet ska bedömas innan riskerna vägs samman. Dokumentets nivåer beräknas fortfarande med '
         'nuvarande regel tills sakkunnig har prövat metoden.')
_REFERENSER = ['SRC-LST-GOR-ARB', 'BT-KVAR-01', 'BT-KVAR-02', 'D-ARB.B1']


def m1_forslag() -> Textstycke:
    """Beslutsunderlag för sakkunnig. Huvudrapporten visar aldrig förslaget och motorns regel är oförändrad."""
    return stycke(_TEXT, _REFERENSER)


def ar_m1_forslag(text: str) -> bool:
    return text.startswith(M1_FORSLAG_RUBRIK)
