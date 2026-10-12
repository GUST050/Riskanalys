from datetime import datetime, timezone

from riskanalys.dokument.leverantor import Anropsdata, Tokenanvandning
from riskanalys.dokument.matning import felklass, kostnad_usd, sammanfatta
from riskanalys.dokument.skrivning import Forsok, Skrivresultat


def _forsok(nummer, fel, indata=1000, utdata=500):
    anrop = Anropsdata(leverantor="test", begard_modell="m", svarsmodell="m", effort="high", prompt_kontrollsumma=None,
                       svar_id=None, stop_reason="end_turn", reservmodell_svarade=False,
                       anvandning=(Tokenanvandning(typ="message", modell=None, indata_token=indata, utdata_token=utdata),),
                       tidpunkt=datetime.now(timezone.utc))
    return Forsok(nummer=nummer, anrop=anrop, text="{}", svar=None, fel=tuple(fel))


def test_sammanfattning_raknar_forsta_forsok_och_felklasser(real_underlag):
    direkt = Skrivresultat(underlag=real_underlag, leverantor="test", modell="m", forsok=(_forsok(1, []),))
    andra = Skrivresultat(underlag=real_underlag, leverantor="test", modell="m",
                          forsok=(_forsok(1, ["Stycke 1 innehåller talet 000, som inte finns i underlaget."]), _forsok(2, [])))
    s = sammanfatta([direkt, andra])
    assert (s.avsnitt, s.godkanda_forsta_forsoket, s.anrop) == (2, 1, 3)
    assert s.felklasser == {"tal": 1}
    assert kostnad_usd(s, 2.0, 10.0) == round(3000 * 2 / 1e6 + 1500 * 10 / 1e6, 4)


def test_felklasser():
    assert felklass("Stycke 2 anger en nivå för risken.") == "niva"
    assert felklass("Oklarhet 1: saknad_uppgift måste vara ett tillåtet fält.") == "oklarhet"
    assert felklass("Stycke 1 hänvisar till X, som inte finns i underlaget.") == "referens"
    assert felklass("Svaret följde inte schemat för AI-utkast (2 fel).") == "schema"
    assert felklass("Något annat.") == "ovrigt"


def test_cachetoken_redovisas_och_raknas_i_kostnaden(real_underlag):
    f=_forsok(1,[])
    usage=f.anrop.anvandning[0].model_copy(update={'cache_lasning_token':2000,'cache_skrivning_token':3000})
    f=f.model_copy(update={'anrop':f.anrop.model_copy(update={'anvandning':(usage,)})})
    s=sammanfatta([Skrivresultat(underlag=real_underlag,leverantor='test',modell='m',forsok=(f,))])
    assert s.cache_lasning_token==2000 and s.cache_skrivning_token==3000
    assert kostnad_usd(s,2,10,cache_laspris=0.2,cache_skrivpris=2.5)==round((1000*2+500*10+2000*0.2+3000*2.5)/1e6,4)
