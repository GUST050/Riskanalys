import pytest

from riskanalys.dokument.delskrivning import FORMATVERSION, skriv_tjanst
from riskanalys.dokument.leverantor import Testleverantor
from riskanalys.dokument.modeller import AIStycke
from riskanalys.dokument.promptar import DELAR
from riskanalys.dokument.tjanstavsnitt import bygg_tjanstavsnitt_v3
from riskanalys.fel import RiskanalysFel
from riskanalys.granskning.analys import mallfynd
from tester.fixturer.m2 import godkant_delsvar, tjanst_for_prov


@pytest.fixture
def v3(tmp_path, rb_intag, klar):
    avsnitt_id, t = tjanst_for_prov(tmp_path, rb_intag, klar)
    res = skriv_tjanst(Testleverantor([godkant_delsvar(d, t) for d in DELAR]), rb_intag, klar, t, avsnitt_id,
                       design="B", effort="high", personnamn=(), spara=lambda d, f: None)
    return rb_intag, klar, t, res, avsnitt_id


def _med_hottext(res, t, text):
    def byt(d):
        if d.del_id != "hot":
            return d
        sista = d.forsok[-1]
        svar = sista.svar.model_copy(update={"stycken": [AIStycke(typ="analys", referenser=[t.tjanst], text=text)]})
        return d.model_copy(update={"forsok": (*d.forsok[:-1], sista.model_copy(update={"svar": svar}))})
    return res.model_copy(update={"delar": tuple(byt(d) for d in res.delar)})


def test_v3_har_sex_delar_och_lasta_stycken_pa_plats(v3):
    rb, p, t, res, avsnitt_id = v3
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id)
    assert [u.rubrik for u in a.underrubriker] == ["Beskrivning och omfattning", "Hot och egna erfarenheter",
        "Sårbarheter och motivering", "Kontroller och effekt", "Risknivåer och motivering", "Slutsatser"]
    texter = [s.text for s in a.stycken]
    assert any(x.startswith("Egen erfarenhet i hotanalysen") for x in texter)
    assert texter[-1].startswith("Byrån beslutar ansvariga")


def test_samma_underlag_ger_samma_summa_och_andrad_ai_text_avviker(v3):
    rb, p, t, res, avsnitt_id = v3
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id)
    assert a.kontrollsumma() == bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id).kontrollsumma()
    with pytest.raises(RiskanalysFel, match="råsvar"):
        bygg_tjanstavsnitt_v3(rb, p, t, _med_hottext(res, t, "Ändrad."), avsnitt_id)


def test_olost_platshallare_stoppar_sammanstallningen(v3):
    rb, p, t, res, avsnitt_id = v3
    with pytest.raises(RiskanalysFel):
        bygg_tjanstavsnitt_v3(rb, p, t, _med_hottext(res, t, "{tal:P-SAKNAS.x} kunder."), avsnitt_id)


def test_ny_profil_efter_skrivning_stoppar_sammanstallningen(v3):
    rb, p, t, res, avsnitt_id = v3
    id = next(iter(res.faktablad.numeriska()))
    andrad = p.model_copy(update={"uppgifter": {**p.uppgifter, id: p.uppgifter[id].model_copy(update={"varde": 999})}})
    with pytest.raises(RiskanalysFel, match="faktablad"):
        bygg_tjanstavsnitt_v3(rb, andrad, t, res, avsnitt_id)


def test_aktuellt_format_sparas_och_skild_fran_v2(v3):
    from riskanalys.dokument.modeller import Avsnitt, Dokument
    rb, p, t, res, avsnitt_id = v3
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, avsnitt_id)
    assert Dokument(id="D-ARB", titel="Prov", avsnitt=(a,)).formatversion == FORMATVERSION
    assert Avsnitt.model_validate_json(a.model_dump_json()).formatversion == FORMATVERSION


def test_felmarkering_far_inte_ersatta_omvalidering(v3):
    rb,p,t,res,id = v3
    d=res.del_("hot")
    svar=d.godkant_svar.model_copy(update={"stycken":[AIStycke(typ="analys",referenser=[t.tjanst],text="Risken är hög.")]})
    f=d.forsok[-1].model_copy(update={"svar":svar,"text":svar.model_dump_json(),"fel":()})
    andrad=res.model_copy(update={"delar":tuple(x.model_copy(update={"forsok":(f,)}) if x.del_id=="hot" else x for x in res.delar)})
    with pytest.raises(RiskanalysFel,match="valider"):
        bygg_tjanstavsnitt_v3(rb,p,t,andrad,id)


def test_mall_del_ger_blockerande_fynd(v3):
    rb, p, t, res, avsnitt_id = v3
    mall = res.model_copy(update={"delar": tuple(d.model_copy(update={"mall": d.del_id == "hot"}) for d in res.delar)})
    fynd = mallfynd(mall)
    assert len(fynd) == 1 and fynd[0]["allvar"] == "blockerande" and "hot" in fynd[0]["beskrivning"]


def test_nivaer_och_sektorskala_ar_kodskrivna_och_tillgangliga_for_ai(v3):
    rb,p,t,res,id=v3
    ref=rb.sektorsreferenser[rb.tjanster[t.tjanst].sektorreferens]
    assert res.faktablad.nivaer['inneboende_risk']==t.inneboende.risk
    assert res.faktablad.sektorsreferens.skala==ref.skala
    a=bygg_tjanstavsnitt_v3(rb,p,t,res,id)
    start,slut=[u.fore_stycke for u in a.underrubriker[4:]]
    assert any('Källans skala är separat' in s.text and ref.kalla in s.referenser for s in a.stycken[start:slut])


def test_flyttad_last_mening_ger_blockerande_fynd(v3,tmp_path):
    from riskanalys.bedomning.korning import kor_bedomning,las_bedomning
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.granskning.analys import analysfynd
    from riskanalys.dokument.modeller import Dokument
    rb,p,t,res,id=v3
    spara_profil(tmp_path,p)
    b=las_bedomning(kor_bedomning(tmp_path,rb))
    a=bygg_tjanstavsnitt_v3(rb,p,t,res,id)
    egna=next(i for i,s in enumerate(a.stycken) if s.text.startswith('Egen erfarenhet i hotanalysen'))
    stycken=list(a.stycken);stycken[egna],stycken[egna+1]=stycken[egna+1],stycken[egna]
    a=a.model_copy(update={'stycken':tuple(stycken)})
    doc=Dokument(id='D-ARB',titel='Prov',avsnitt=(a,))
    assert any(f['allvar']=='blockerande' and 'analysdelar avviker' in f['beskrivning'] for f in analysfynd(rb,b,p,doc,{id:res}))


def test_likhet_markeras_som_b04_nar_regelposten_finns(v3,tmp_path):
    from riskanalys.bedomning.korning import kor_bedomning,las_bedomning
    from riskanalys.profil.lagring import spara_profil
    from riskanalys.granskning.analys import analysfynd
    from riskanalys.dokument.modeller import Dokument
    rb,p,t,res,id=v3
    spara_profil(tmp_path,p)
    b=las_bedomning(kor_bedomning(tmp_path,rb))
    annat=res.model_copy(update={'avsnitt':'D-ARB.6.2','tjanst':'T-SKATT-01'})
    a=bygg_tjanstavsnitt_v3(rb,p,t,res,id)
    doc=Dokument(id='D-ARB',titel='Prov',avsnitt=(a,))
    fynd=analysfynd(rb,b,p,doc,{id:res,'D-ARB.6.2':annat})
    lika=[f for f in fynd if 'nästan likadan' in f['beskrivning']]
    assert lika and all(f['typ']=='bristmonster' and f['regel']=='B-04' for f in lika)


def test_period_ersatts_fore_sakgranskning_och_foljande_bygge(v3):
    rb, p, t, res, id = v3
    d = res.del_('hot')
    sista = d.forsok[-1]
    s = sista.svar.stycken[0]
    s = s.model_copy(update={'text': s.text + ' Byrån stämmer av under {period:P-KUND.antal_aktiva}, det vill säga under statistikperioden.',
        'referenser': list(dict.fromkeys([*s.referenser, 'P-KUND.antal_aktiva']))})
    svar = sista.svar.model_copy(update={'stycken': [s, *sista.svar.stycken[1:]]})
    forsok = sista.model_copy(update={'svar': svar, 'text': svar.model_dump_json()})
    res = res.model_copy(update={'delar': tuple(x.model_copy(update={'forsok': (forsok,)}) if x.del_id == 'hot' else x for x in res.delar)})
    a = bygg_tjanstavsnitt_v3(rb, p, t, res, id)
    text = next(s.text for s in a.stycken if 'det vill säga under statistikperioden' in s.text)
    assert '2026-01-01–2026-09-30' in text and '{period:' not in text
    assert a.kontrollsumma() == bygg_tjanstavsnitt_v3(rb, p, t, res, id).kontrollsumma()
