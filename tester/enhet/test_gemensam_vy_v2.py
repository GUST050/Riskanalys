from html.parser import HTMLParser
from collections import Counter
import pytest
from tester.enhet.test_riktning_v2 import fall,med_post

class Identiteter(HTMLParser):
    def __init__(self):super().__init__();self.ids=[]
    def handle_starttag(self,tag,attrs):
        self.ids.extend(v for k,v in attrs if k=='id')

def test_tillampningar_ar_escapade_och_dom_id_ar_unika(fall):
    from riskanalys.intag.gemensamvy import tillampningar
    p,t=med_post(fall)
    g=p.gemensamma_sarbarhetsprovningar[0].model_copy(update={'beskrivning':'</textarea><script>PRIVAT</script>'})
    p=p.model_copy(update={'gemensamma_sarbarhetsprovningar':(g,)})
    html=tillampningar(fall.rb,fall.profil,fall.bedomning,p,t.tjanst,'/token/','csrf','revision')
    assert '<script>' not in html and '&lt;script&gt;' in html
    ids=Identiteter();ids.feed(html)
    assert not [id for id,n in Counter(ids.ids).items() if n>1]
    assert 'name="riktningsval.riktning"' not in html
    assert 'Samlad' in html or 'samlat' in html


def test_byraanalysen_visar_antagande_utan_att_bekrafta_nagot(fall):
    from riskanalys.intag.gemensamvy import byraanalys
    fore=fall.paket.model_dump_json()
    html=byraanalys(fall.paket,'/token/','csrf','revision',rb=fall.rb)
    assert 'antagande' in html and 'Gemensam byråanalys' in html
    assert fall.paket.model_dump_json()==fore


def test_tackningsval_borjar_oklart_och_visar_plus_ett_referensen(fall):
    from riskanalys.intag.gemensamvy import tackningsformular
    p,t=med_post(fall,None)
    html=tackningsformular(fall.rb,p,t,'/token/','csrf','revision',{'post':['prov'],'hot':['H-03'],'dimension':['pt']})
    assert 'Referens: samma scenario med ytterligare +1 – inte ett facit' in html
    assert 'referensmotivering' in html and 'jamforelseniva' in html
    assert 'value="oklar" selected' in html
    assert 'operation' in html and not p.tjanster[0].tackningsprovningar
