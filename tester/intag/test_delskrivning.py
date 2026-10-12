import pytest

from riskanalys.bedomning.korning import kor_bedomning, las_bedomning
from riskanalys.dokument.delskrivning import skriv_tjanst
from riskanalys.dokument.leverantor import LeverantorFel, Testleverantor
from riskanalys.dokument.modeller import AIStycke, AISvar
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.underlag import tjanster_med_avsnitt
from riskanalys.profil.lagring import spara_profil

from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov

def _skriv(lev, rb, profil, t, avsnitt_id, effort="high", design="B"):
    return skriv_tjanst(lev, rb, profil, t, avsnitt_id, design=design, effort=effort, personnamn=(), spara=lambda d, f: None)


def test_design_b_ett_anrop_per_del_och_kedjat_underlag(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    res = _skriv(lev, rb_intag, klar, t, avsnitt_id)
    assert [a.del_id for a in lev.delanrop] == list(DELAR)
    assert not any(d.mall for d in res.delar)
    motivering = next(a for a in lev.delanrop if a.del_id == "risknivaer")
    assert any(b["text"].startswith("<maskinellt_validerat>") for b in motivering.innehall)


def test_underkand_del_kors_om_hogst_tva_ganger_med_hojd_effort_och_blir_mall(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    dalig = AISvar(stycken=[AIStycke(typ="analys", referenser=[t.tjanst], text="Risken är hög.")], oklarheter=[])
    lev = Testleverantor([dalig, dalig, dalig] + [godkant_delsvar(d, t) for d in DELAR[1:]])
    hot = _skriv(lev, rb_intag, klar, t, avsnitt_id, effort="medium").del_("hot")
    assert hot.mall and len(hot.forsok) == 3
    assert [f.effort for f in hot.forsok] == ["medium", "medium", "high"]


def test_ogiltigt_svar_i_en_del_kraschar_inte_hela_tjansten(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor(["", "", ""] + [godkant_delsvar(d, t) for d in DELAR[1:]])
    res = _skriv(lev, rb_intag, klar, t, avsnitt_id)
    assert res.del_("hot").mall and not res.del_("slutsatser").mall


def test_design_a_ger_tydligt_fel_tills_den_byggts(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    with pytest.raises(LeverantorFel, match="Design A"):
        _skriv(Testleverantor([]), rb_intag, klar, t, avsnitt_id, design="A")


def test_hela_ai_anropet_skyddar_lokal_fritext_kalla_och_sma_grupper(tmp_path, rb_intag, klar):
    hemligt = 'Kim Testsson /Users/x/kunder.xlsx'
    upp = {id: u.model_copy(update={'kalla': hemligt, 'bekraftad_av': 'Kim Testsson',
        **({'varde': hemligt} if rb_intag.falt[id].typ == 'text' else {})}) for id,u in klar.uppgifter.items()}
    p = klar.model_copy(update={'uppgifter':upp})
    avsnitt_id,t = tjanst_for_prov(tmp_path,rb_intag,p)
    lev=Testleverantor([godkant_delsvar(d,t) for d in DELAR])
    _skriv(lev,rb_intag,p,t,avsnitt_id)
    payload='\n'.join(str(a.innehall) for a in lev.delanrop)
    assert 'Kim Testsson' not in payload and '/Users/' not in payload and 'kunder.xlsx' not in payload


def test_natverksfel_sparas_och_ger_mall_utan_att_andra_delar_stannar(tmp_path,rb_intag,klar):
    from riskanalys.dokument.delskrivning import skriv_tjanst
    avsnitt_id,t=tjanst_for_prov(tmp_path,rb_intag,klar)
    class Avbrottsleverantor(Testleverantor):
        def skriv_del(self,anrop):
            if anrop.del_id == 'hot':
                raise LeverantorFel('Syntetiskt nätverksfel', tillfalligt=True)
            return super().skriv_del(anrop)
    sparade=[]
    lev=Avbrottsleverantor([godkant_delsvar(d,t) for d in DELAR[1:]])
    res=skriv_tjanst(lev,rb_intag,klar,t,avsnitt_id,effort='high',personnamn=(),spara=lambda d,f:sparade.append((d,f)))
    assert res.del_('hot').mall and len(res.del_('hot').forsok)==3
    assert not res.del_('slutsatser').mall
    assert [d for d,f in sparade].count('hot') == 3


def test_skiftlage_i_id_normaliseras_aven_i_delkedjan(tmp_path,rb_intag,klar):
    avsnitt_id,t=tjanst_for_prov(tmp_path,rb_intag,klar)
    svar=godkant_delsvar('hot',t)
    svar=svar.model_copy(update={'stycken':[s.model_copy(update={'referenser':[r.lower() for r in s.referenser]}) for s in svar.stycken]})
    lev=Testleverantor([svar]+[godkant_delsvar(d,t) for d in DELAR[1:]])
    res=_skriv(lev,rb_intag,klar,t,avsnitt_id)
    assert len(lev.delanrop)==5 and not res.del_('hot').mall


@pytest.mark.parametrize('status,orsak', [(400, 'begäran'), (401, 'nyckel'), (403, '[Bb]ehörighet'), (404, '404')])
def test_permanent_api_fel_avbryter_vid_forsta_anropet(tmp_path, rb_intag, klar, status, orsak):
    import anthropic
    import httpx2
    from riskanalys.dokument.claude import ClaudeLeverantor
    from tester.enhet.test_claude import API_URL, FalskKlient
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    fel = anthropic.APIStatusError('Syntetiskt API-fel', response=httpx2.Response(
        status, request=httpx2.Request('POST', API_URL)), body=None)
    klient = FalskKlient(undantag=fel)
    with pytest.raises(LeverantorFel, match=orsak):
        _skriv(ClaudeLeverantor(klient=klient), rb_intag, klar, t, id)
    assert len(klient.anrop) == 1


@pytest.mark.parametrize('status', [429, 500, 503, None])
def test_tillfalligt_api_fel_far_ge_forsok_och_mall(tmp_path, rb_intag, klar, status):
    import anthropic
    import httpx2
    from riskanalys.dokument.claude import ClaudeLeverantor
    from tester.enhet.test_claude import API_URL, FalskKlient
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    fel = (anthropic.APIConnectionError(request=httpx2.Request('POST', API_URL)) if status is None
           else anthropic.APIStatusError('Syntetiskt API-fel', response=httpx2.Response(
               status, request=httpx2.Request('POST', API_URL)), body=None))
    klient = FalskKlient(undantag=fel)
    res = _skriv(ClaudeLeverantor(klient=klient), rb_intag, klar, t, id)
    assert all(d.mall and len(d.forsok) == 3 for d in res.delar)
    assert len(klient.anrop) == 15
    assert all('Syntetiskt API-fel' not in str(a['messages']) for a in klient.anrop)


def test_slut_pa_testsvar_avbryter_i_stallet_for_att_ge_mallar(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar('hot', t)])
    with pytest.raises(LeverantorFel, match='förberedda svar'):
        _skriv(lev, rb_intag, klar, t, id)
    assert len(lev.delanrop) == 2


def test_delanrop_far_utrymme_for_tankande_och_svar(tmp_path, rb_intag, klar):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    lev = Testleverantor([godkant_delsvar(d, t) for d in DELAR])
    _skriv(lev, rb_intag, klar, t, id)
    assert all(a.max_tokens == 64000 for a in lev.delanrop)


@pytest.mark.parametrize('stoppskal', [('max_tokens', 'max_tokens'), ('end_turn', 'max_tokens'), ('max_tokens', 'end_turn')])
@pytest.mark.parametrize('effort', ['medium', 'high'])
def test_tokenavbrott_ger_inte_hogre_effort_i_sista_omforsoket(tmp_path, rb_intag, klar, stoppskal, effort):
    id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    class KlipptLeverantor(Testleverantor):
        def skriv_del(self, anrop):
            svar = super().skriv_del(anrop)
            if anrop.del_id == 'hot' and len(self.delanrop) <= 2:
                stopp = stoppskal[len(self.delanrop) - 1]
                return svar.model_copy(update={
                    'anrop': svar.anrop.model_copy(update={'stop_reason': stopp}),
                    'avbrott': 'Syntetiskt tokenavbrott' if stopp == 'max_tokens' else None})
            return svar
    lev = KlipptLeverantor(['{}', '{}', godkant_delsvar('hot', t)] + [godkant_delsvar(d, t) for d in DELAR[1:]])
    res = _skriv(lev, rb_intag, klar, t, id, effort=effort)
    assert [f.effort for f in res.del_('hot').forsok] == [effort] * 3
    assert res.del_('hot').godkant_svar is not None
