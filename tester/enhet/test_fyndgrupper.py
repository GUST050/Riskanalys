from collections import Counter
import pytest
from riskanalys.granskning.modeller import Fynd
from riskanalys.granskning.fyndgrupper import Fyndgrupp, gruppera_fynd


def fynd(**kw):
    return Fynd(id='F1', typ='tackning', allvar='blockerande', grund='metodval', beskrivning='Syntetisk brist', atgard='Pröva', **kw)


def test_fyndgrupper_bevarar_alla_id_och_sparrar():
    a=fynd()
    poster=(a,a,a.model_copy(update={'id':'F2'}),a.model_copy(update={'id':'F3','status':'åtgärdad'}))
    grupper=gruppera_fynd(poster)
    assert tuple(len(g.medlemmar) for g in grupper)==(3,1)
    assert Counter(x.model_dump_json() for x in poster)==Counter(x.model_dump_json() for g in grupper for x in g.medlemmar)
    assert poster[0].status=='öppen'
    with pytest.raises(ValueError): Fyndgrupp(())


@pytest.mark.parametrize('falt,varde',[('regel','R2'),('avsnitt','D-ARB.6.2'),('status','sakkunnigbedömd'),('motivering','Annat'),('hanterad_av','Annan')])
def test_samma_text_med_olika_sakfalt_forblir_separat(falt,varde):
    a=fynd()
    assert len(gruppera_fynd((a,a.model_copy(update={falt:varde}))))==2


def test_gruppering_forandrar_inte_faststallelsehinder():
    from riskanalys.faststallelse.grindar import fyndhinder
    a=fynd()
    poster=(a,a.model_copy(update={'id':'F2','allvar':'viktig','status':'åtgärdad'}),a.model_copy(update={'id':'F3','status':'sakkunnigbedömd','motivering':'Syntetisk prövning'}))
    before=tuple((p.id,fyndhinder(p)) for p in poster)
    after=tuple((p.id,fyndhinder(p)) for g in gruppera_fynd(poster) for p in g.medlemmar)
    assert before==after
    assert before[0][1] and not before[1][1] and before[2][1]
