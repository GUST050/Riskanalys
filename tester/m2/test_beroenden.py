import pytest
from riskanalys.regelverk.validering import validera

@pytest.mark.parametrize('typ',['bas','alias','kundfalt','kundatgard','ersatter','metodgrund','inventarietext'])
def test_m2_broken_dependency_ar_valideringsfel(regelbas_v1,typ):
 rb=regelbas_v1
 if typ in {'bas','alias'}:
  k=next(k for k,f in rb.falt.items() if f.basfalt)
  f=rb.falt[k].model_copy(update={'basfalt' if typ=='bas' else 'alias_for':'P-SAKNAS'})
  rb=rb.model_copy(update={'falt':{**rb.falt,k:f}})
 elif typ in {'kundfalt','kundatgard'}:
  r=next(r for r in rb.kundmall.rader if r.spar=='B')
  r=r.model_copy(update={'villkor':{'falt':'K-SAKNAS','op':'==','varde':True}} if typ=='kundfalt' else {'utfall':{'atgarder':['KB-SAKNAS']}})
  rb=rb.model_copy(update={'kundmall':rb.kundmall.model_copy(update={'rader':tuple(r if x.id==r.id else x for x in rb.kundmall.rader)})})
 elif typ=='ersatter':
  k=next(iter(rb.sarbarheter));rb=rb.model_copy(update={'sarbarheter':{**rb.sarbarheter,k:rb.sarbarheter[k].model_copy(update={'ersatter':(k,)})}})
 elif typ=='metodgrund':
  k=next(iter(rb.tjanster));rb=rb.model_copy(update={'tjanster':{**rb.tjanster,k:rb.tjanster[k].model_copy(update={'grund':'ska_krav'})}})
 else:
  i=rb.inventarium[0];rb=rb.model_copy(update={'inventarium':(i.model_copy(update={'text':i.text+' fel'}),*rb.inventarium[1:])})
 assert validera(rb)
