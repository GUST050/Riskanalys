"""Lokal omfattning, utförd bevakning och uppföljning med tydliga belägg."""
from riskanalys.dokument.modeller import Avsnitt, Textstycke
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.dokument.analysunderlag import _belagg
from riskanalys.dokument.tjanstavsnitt import stycke
import re

def omfattningsstycke(rb: Regelbas, p: Profil, b: Bedomning) -> Textstycke:
    prop = b.proportionalitet
    text = 'Storlek: ' + _belagg(rb, p, 'P-ORG.antal_anstallda') + ' ' + _belagg(rb, p, 'P-ORG.verksamhetsstallen') + ' ' + _belagg(rb, p, 'P-VERK.omsattning')
    text += ' Art: ' + ', '.join((rb.tjanster[t.tjanst].namn for t in b.tjanster if t.inneboende)) + '. '
    text += f'Vald omfattning (vald omfattning enligt metod): {prop.niva}; {prop.status}. ' + rb.metod.omfattning.forklaring + ' '
    if prop.okanda_uppgifter:
        text += 'Uppgifter saknas: ' + ', '.join(prop.okanda_uppgifter) + '. [VERIFIERA] '
    text += 'Byråns motivering: ' + _belagg(rb, p, 'P-OMFATTNING.motivering')
    return stycke(text, [*prop.regelspar, 'P-ORG.antal_anstallda', 'P-ORG.verksamhetsstallen', 'P-VERK.omsattning', 'P-OMFATTNING.motivering', *rb.metod.omfattning.kallor], typ='motivering')

def bevakningsavsnitt(rb: Regelbas, p: Profil) -> Avsnitt:
    refs = ['P-BEVAKNING.' + s for s in ['kallor', 'datum', 'ansvarig', 'relevans']]
    text = 'Byråns dokumenterade omvärldsbevakning: ' + ' '.join((_belagg(rb, p, id) for id in refs))
    uppgift = p.uppgifter.get('P-BEVAKNING.kallor')
    idn = tuple(re.split('[,;\\s]+', str(uppgift.varde).strip())) if uppgift else ()
    kanda = [id for id in idn if id in rb.kallor and rb.kallor[id].kontrollsumma]
    if not idn or len(kanda) != len(idn):
        text += ' [VERIFIERA] Ange enbart registrerade käll-ID:n med kontrollerad version, separerade med komma. '
    else:
        refs.extend(kanda)
        text += ' Lästa versioner: ' + '; '.join((id + ' ' + rb.kallor[id].kontrollsumma for id in kanda)) + '. '
    text += ' En hämtning eller registrering i programmets källregister visar inte att byrån läst och bedömt relevansen. Lästa källor ska knytas till varje tjänsts hot, sårbarheter och åtgärder, även när slutsatsen är att inget behöver ändras.'
    return Avsnitt(id='D-ARB.11', rubrik='Omvärldsbevakning', kalla='regelbas', stycken=(stycke(text, [*refs, 'SRC-TS-2026-14']),))

def uppfoljningsstycken(rb: Regelbas, p: Profil) -> tuple[Textstycke, ...]:
    refs = ['P-VERK.spridning', 'P-VERK.goaml', 'P-VERK.tidigare_tillsyn']
    text = 'Uppdateringsgrunder: pröva behovet efter hot eller hämnd mot personal, förändrade tjänster, kunder, leveranssätt eller geografi, ny nationell riskbedömning, ändrad EU-lista över högrisktredjeländer och nya tillsynsbeslut. Uppdatera vid behov; omvärldshändelsen ger inte automatiskt en bestämd risknivå. Dokumentera spridning till berörda roller, utbildning utifrån riskbedömningen, goAML-förmåga och uppföljning av tillsyn. '
    text += ' '.join((_belagg(rb, p, id) for id in refs))
    return (stycke(text, [*refs, 'SRC-14FS-2024-11', 'SRC-PTL', 'SRC-VAGL-2025-03', 'SRC-FIPO-AR-2025']),)
