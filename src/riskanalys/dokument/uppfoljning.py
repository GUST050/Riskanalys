"""Lokal omfattning, utförd bevakning och uppföljning med tydliga belägg."""

from riskanalys.regelverk.granser import metodgransindex
from riskanalys.dokument.modeller import Avsnitt, Textstycke
from riskanalys.bedomning.modeller import Bedomning
from riskanalys.profil.modeller import Profil
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.dokument.analysunderlag import _belagg
from riskanalys.dokument.klartext import faltnamn, kod_till_namn, uppgiftstext
from riskanalys.dokument.tabeller import kort_varde
from riskanalys.dokument.tjanstavsnitt import stycke
import re

def omfattningsstycke(rb: Regelbas, p: Profil, b: Bedomning, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> Textstycke:
    if gransindex is None:
        gransindex = metodgransindex(rb)
    prop = b.proportionalitet
    text = 'Storlek: ' + _belagg(rb, p, 'P-ORG.antal_anstallda', gransindex=gransindex) + ' ' + _belagg(rb, p, 'P-ORG.verksamhetsstallen', gransindex=gransindex) + ' ' + _belagg(rb, p, 'P-VERK.omsattning', gransindex=gransindex)
    text += ' Art: ' + ', '.join((rb.tjanster[t.tjanst].namn for t in b.tjanster if t.inneboende)) + '. '
    text += f'Vald omfattning (vald omfattning enligt metod): {prop.niva}; {prop.status}. ' + rb.metod.omfattning.forklaring + ' '
    if prop.okanda_uppgifter:
        text += 'Uppgifter saknas: ' + ', '.join(faltnamn(rb, id) for id in prop.okanda_uppgifter) + '. [VERIFIERA] '
    text += uppgiftstext(rb, p, 'P-OMFATTNING.motivering', namn='Byråns motivering', gransindex=gransindex)
    return stycke(text, [*prop.regelspar, 'P-ORG.antal_anstallda', 'P-ORG.verksamhetsstallen', 'P-VERK.omsattning', 'P-OMFATTNING.motivering', *rb.metod.omfattning.kallor], typ='motivering')


STORLEKSFALT = ('P-ORG.antal_anstallda', 'P-ORG.verksamhetsstallen', 'P-VERK.omsattning')


def kort_omfattningsstycke(rb: Regelbas, p: Profil, b: Bedomning, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> Textstycke:
    """V6: samma motivering efter storlek och art som omfattningsstycke; belägg och trösklar står i B1."""
    index = gransindex if gransindex is not None else metodgransindex(rb)
    prop = b.proportionalitet
    regel = rb.metod.omfattning
    text = 'Vald omfattning enligt metod: ' + (f'{prop.niva}; {prop.status}. ' if prop else 'ej bedömd. [VERIFIERA] ')
    text += 'Storlek: ' + '; '.join(f'{faltnamn(rb, id)}: {kort_varde(rb, p, id, period=True, gransindex=index).rstrip(".")}'
                                    for id in STORLEKSFALT) + '. '
    art = ', '.join(rb.tjanster[t.tjanst].namn for t in b.tjanster if t.inneboende)
    text += 'Art: ' + (art + '. ' if art else 'ingen bedömd tjänst. [VERIFIERA] ')
    okanda = prop.okanda_uppgifter if prop else ()
    if okanda:
        text += 'Uppgifter saknas: ' + ', '.join(faltnamn(rb, id) for id in okanda) + '. [VERIFIERA] '
    if regel:
        text += 'Trösklar och metodregel: bilaga B1. '
    text += 'Byråns motivering: ' + kort_varde(rb, p, 'P-OMFATTNING.motivering', gransindex=index)
    regelspar = prop.regelspar if prop else ((regel.id,) if regel else ())
    refs = [*regelspar, *STORLEKSFALT, *okanda, 'P-OMFATTNING.motivering', *((regel.id, 'D-ARB.B1') if regel else ())]
    return stycke(text, list(dict.fromkeys(refs)), typ='motivering')


def omfattningsregel_i_bilaga(rb: Regelbas) -> tuple[Textstycke, ...]:
    """Metodens förklaring av omfattningen; huvudtexten hänvisar hit."""
    regel = rb.metod.omfattning
    return (stycke(f'Omfattningsregel {regel.id}: {regel.forklaring}', [regel.id], typ='beskrivning'),) if regel else ()


def bevakningsavsnitt(rb: Regelbas, p: Profil, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> Avsnitt:
    if gransindex is None:
        gransindex = metodgransindex(rb)
    refs = ['P-BEVAKNING.' + s for s in ['kallor', 'datum', 'ansvarig', 'relevans']]
    text = 'Byråns dokumenterade omvärldsbevakning: ' + ' '.join((_belagg(rb, p, id, gransindex=gransindex) for id in refs))
    uppgift = p.uppgifter.get('P-BEVAKNING.kallor')
    idn = tuple(re.split('[,;\\s]+', str(uppgift.varde).strip())) if uppgift else ()
    kanda = [id for id in idn if id in rb.kallor and rb.kallor[id].kontrollsumma]
    if not idn or len(kanda) != len(idn):
        text += ' [VERIFIERA] Ange enbart registrerade käll-ID:n med kontrollerad version, separerade med komma. '
    else:
        refs.extend(kanda)
        text += ' Lästa källor: ' + '; '.join(rb.kallor[id].titel for id in kanda) + '. Version och kontrollsumma för varje källa redovisas i bilaga B1. '
    text += ' En hämtning eller registrering i programmets källregister visar inte att byrån läst och bedömt relevansen. Lästa källor ska knytas till varje tjänsts hot, sårbarheter och åtgärder, även när slutsatsen är att inget behöver ändras.'
    text = kod_till_namn(rb, text)
    return Avsnitt(id='D-ARB.11', rubrik='Omvärldsbevakning', kalla='regelbas', stycken=(stycke(text, list(dict.fromkeys([*refs, 'SRC-TS-2026-14']))),))

def uppfoljningsstycken(rb: Regelbas, p: Profil, *, gransindex: dict[str, tuple[float, ...]] | None = None) -> tuple[Textstycke, ...]:
    if gransindex is None:
        gransindex = metodgransindex(rb)
    refs = ['P-VERK.spridning', 'P-VERK.goaml', 'P-VERK.tidigare_tillsyn']
    text = 'Uppdateringsgrunder: pröva behovet efter hot eller hämnd mot personal, förändrade tjänster, kunder, leveranssätt eller geografi, ny nationell riskbedömning, ändrad EU-lista över högrisktredjeländer och nya tillsynsbeslut. Uppdatera vid behov; omvärldshändelsen ger inte automatiskt en bestämd risknivå. Dokumentera spridning till berörda roller, utbildning utifrån riskbedömningen, goAML-förmåga och uppföljning av tillsyn. '
    text += ' '.join((_belagg(rb, p, id, gransindex=gransindex) for id in refs))
    return (stycke(text, [*refs, 'SRC-14FS-2024-11', 'SRC-PTL', 'SRC-VAGL-2025-03', 'SRC-FIPO-AR-2025']),)
