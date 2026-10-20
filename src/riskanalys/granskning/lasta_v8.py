"""V8:s uttryckliga kravtäckning för geografiskt underlag och egen rapportering.

V8 bevarar just dessa låsta stycken i tjänstens tredje analysdel. Gemensam
beskrivning i en bilaga ersätter aldrig den lokala täckningen. Äldre v6/v7
kontroller och bytekontrakt ändras inte.
"""
from riskanalys.granskning.lasta_v6 import lasta_fynd_v6

KRAVTACKNING_V8 = {'B-09': 'tjanst/lokal-sarbarhet', 'B-10': 'tjanst/lokal-sarbarhet',
                   'B-15': 'tjanst/lokal-sarbarhet'}


def lasta_fynd_v8(rb,p,b,d,forvantat,*,gransindex):
    return lasta_fynd_v6(rb,p,b,d,forvantat,gransindex=gransindex,bevara_original=True)
