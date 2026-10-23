"""De faktiska sänkningarna måste följas även från ursprungsbaslinjen."""
def test_jamfor_sankning_bade_mot_forra_och_ursprunglig_baslinje():
    from docs.research.verktyg.metodkontraster import jamforelser
    def fall(risk):
        return {'ideell':{'profil_summa':'identiska-bytes','utfall':{'tjanster':[{'tjanst':'T-RED-01','erbjuds':True,
            'scenarier':[{'hot':'H-03','dimension':'pt','risk':risk,'kvarstaende':risk}]}]}}}
    steg,samlat=jamforelser(fall('hög'),fall('måttlig'),fall('mycket hög'))
    assert {x['fore'] for x in steg['ideell']['sankta_led']}=={'hög'}
    assert {x['fore'] for x in samlat['ideell']['sankta_led']}=={'mycket hög'}
    assert {x['efter'] for x in samlat['ideell']['sankta_led']}=={'måttlig'}
