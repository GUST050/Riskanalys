"""Få riktiga V9-kedjor; negativa mutationer görs på kopior av granskade källor."""
import pytest
from tester.fixturer.resultatkedja import resultatkedja_bas,resultatkedja,DAG


@pytest.mark.fullkedja
@pytest.mark.parametrize('format',['v8','v9'])
def test_befintligt_v8_och_v9_med_v8_skrivresultat_kan_faststallas_efter_standardbyte(resultatkedja,monkeypatch,format):
    from riskanalys.dokument import rapportversion
    from riskanalys.granskning.korning import kor_granskning,las_granskning
    from riskanalys.dokument.export import kor_export_utkast
    from riskanalys.faststallelse.faststall import faststall,verifiera_version,FaststallelseFel
    from riskanalys.faststallelse.modeller import Beslut
    from riskanalys.faststallelse.sakgranskning import registrera_sakgranskning,spara_sakgranskningar,struktur_summa,las_sakgranskningar
    from riskanalys.analys.provning import registersumma
    k=resultatkedja;f=k.fall
    # Ett redan sparat V8-utkast ska inte märkas om när standarden byts.
    monkeypatch.setattr(rapportversion,'AKTUELL_DOKUMENTVERSION',rapportversion.V9)
    gm=k.granskningsmapp if format=='v8' else kor_granskning(f.byramapp,f.regelbas,DAG,rapportformat='v9')
    d,fynd=las_granskning(gm);assert not fynd
    e=kor_export_utkast(f.byramapp,DAG,granskningsmapp=gm,regelbas=f.regelbas)
    beslut=Beslut(organ='Syntetisk styrelse',namn='Syntetisk',roll='FfR',datum=DAG)
    if format=='v9':
        from riskanalys.dokument.rapportpaket_v9 import las_presentation_v9
        from riskanalys.faststallelse.resultatgranskning import registrera_resultatgranskning
        p=las_presentation_v9(gm,f.bedomning,f.profil,regelbas=f.regelbas)
        with pytest.raises(FaststallelseFel):faststall(f.byramapp,k.regelrot,f.regelbas,beslut)
        poster=registrera_resultatgranskning((),d,f.profil,presentation=p,visad_struktursumma=struktur_summa(d,presentation=p),
            analysbindning=registersumma(f.analys),godkand=True,roll='FfR',namn='Syntetisk',datum=DAG)
        spara_sakgranskningar(f.byramapp,poster)
        with pytest.raises(FaststallelseFel):faststall(f.byramapp,k.regelrot,f.regelbas,beslut)
        for a in d.avsnitt:
            if a.leveransdel!='resultatrapport':
                poster=registrera_sakgranskning(poster,d,f.profil,a.id,True,'FfR','Syntetisk',DAG,analysbindning=registersumma(f.analys),presentation=p)
        spara_sakgranskningar(f.byramapp,poster)
        # Gamla R-poster har korrekta summor men styrker inte den samlade handlingen.
        from riskanalys.faststallelse.modeller import Sakgranskning
        aldre=tuple(Sakgranskning.model_validate(p.model_dump(mode='json',exclude={'granskningssatt'})) for p in poster)
        spara_sakgranskningar(f.byramapp,aldre)
        with pytest.raises(FaststallelseFel,match='--resultatrapport'):
            faststall(f.byramapp,k.regelrot,f.regelbas,beslut)
        assert not (f.byramapp/'faststallda/v1').exists()
        spara_sakgranskningar(f.byramapp,poster)
    final=faststall(f.byramapp,k.regelrot,f.regelbas,beslut)
    assert verifiera_version(f.byramapp,1)==[]
    assert len(list(final.glob('*.docx')))==(3 if format=='v9' else 2)
    # Historisk kontroll får inte läsa dagens regelbas eller rendera om filerna.
    import riskanalys.dokument.rendering_v9 as r9
    import riskanalys.dokument.rendering as r8
    from riskanalys.regelverk import laddning
    def forbjudet(*args,**kw):pytest.fail('Historisk verifiering försökte återbygga eller läsa aktuell regelbas')
    monkeypatch.setattr(r9,'rendera_rapportvyer_v9',forbjudet)
    monkeypatch.setattr(r8,'rendera_rapportvyer',forbjudet)
    monkeypatch.setattr(laddning,'ladda_regelbas',forbjudet)
    assert verifiera_version(f.byramapp,1)==[]
