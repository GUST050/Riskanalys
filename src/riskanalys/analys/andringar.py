"""Transportoberoende ändringskommandon; tjänsten prövar dem under analyslåset."""
from dataclasses import dataclass
from datetime import date
from typing import Literal
from pydantic import BaseModel
from riskanalys.analys import modeller as m, provning as p
from riskanalys.analys.provning import BLOCKFALT, ALLTID
from riskanalys.fel import RiskanalysFel

Radidentitet = str | tuple[str, str]
Blockvarde = str | BaseModel | tuple[str | BaseModel, ...]
RADFALT = frozenset({'delanalyser','leverantorer','scenarier','sarbarhetsprovningar','kontroller','gap','rutinatgarder'})



def radidentitet(namn: str, rad) -> Radidentitet:
    """Kontrollrader saknar eget id; deras redigerbara referenspar identifierar raden."""
    return (rad.scenario,rad.kontroll) if namn=='kontroller' else rad.id


@dataclass(frozen=True)
class Blockandring:
    tjanst: str
    nummer: int
    revision: str
    operation: Literal['spara','bekrafta']
    forfattare: str
    visad_summa: str
    block: m.Analysblock
    varden: tuple[tuple[str, Blockvarde], ...]
    nya_rader: tuple[tuple[str, Radidentitet], ...] = ()
    borttagna_rader: tuple[tuple[str, Radidentitet], ...] = ()


@dataclass(frozen=True)
class Scenarioval:
    tjanst: str
    scenario: str
    revision: str
    forfattare: str
    val: m.Scenariokoppling


@dataclass(frozen=True)
class Scenarioandring:
    scenario: str
    revision: str
    forfattare: str
    visad_summa: str
    varden: tuple[tuple[str, str | tuple[str, ...]], ...]


@dataclass(frozen=True)
class Modellriskandring:
    rutinbelagg: str
    modellansvarig: str
    utvarderad: date
    nasta_genomgang: date
    feluppfoljning: str
    godkand: bool
    beslutad_av: str
    beslutsdatum: date


@dataclass(frozen=True)
class Modellfelandring:
    id: str
    datum: date
    beskrivning: str
    allvar: Literal['vasentligt','ovrigt']
    status: Literal['oppet','atgardat']
    atgard_och_omprovning: str
    belagg: tuple[str, ...]


def hamta_tjanst(paket, tjanst):
    if paket is None:raise RiskanalysFel('Starta ett analysutkast först.')
    a = next((a for a in paket.tjanster if a.tjanst == tjanst), None)
    if a is None:
        raise RiskanalysFel('Välj en tjänst ur analysöversikten.')
    return a


def _referenser(paket, a, nummer, rb):
    """Kontrollera bara blockets referenser; gamla ofullständiga utkast får finnas."""
    belagg = {b.id for b in paket.belagg}
    scenarier = {s.id for s in a.scenarier} | {k.scenario for k in a.scenariokopplingar}
    delanalyser = {d.id for d in a.delanalyser}
    katalog = rb.tjanster.get(a.tjanst) if rb is not None else None
    if rb is not None and katalog is None:
        raise RiskanalysFel('Välj en tjänst ur den aktuella källkatalogen.')
    if rb is not None and paket.schemaversion == 2:
        from riskanalys.analys.engangssvar import visade_scenarioval
        # Ett visat standardförslag kan hänvisas till i utkast före genomgången.
        # Ingen koppling eller bekräftelse skapas av formulärsparningen.
        scenarier.update(k.scenario for k in visade_scenarioval(rb, paket, a.tjanst))

    def radnyckel(rad):
        if not isinstance(rad,dict):return None
        if 'id' in rad:return ('id',rad['id'])
        if 'scenario' in rad and 'kontroll' in rad:return ('kontroll',rad['scenario'],rad['kontroll'])
        return None

    def kontrollera(data,tidigare):
        if isinstance(data, dict):
            for namn, v in data.items():
                gammalt = tidigare.get(namn) if isinstance(tidigare,dict) else None
                tillatna = None
                if namn.endswith('belagg'):
                    tillatna = belagg
                elif namn in ('scenarier', 'scenario') and isinstance(v, (str, tuple, list)) and not any(isinstance(x, dict) for x in v):
                    tillatna = scenarier
                elif namn == 'delanalyser' and isinstance(v, (tuple, list)) and not any(isinstance(x, dict) for x in v):
                    tillatna = delanalyser
                elif rb is not None and namn in ('hot', 'sarbarheter', 'kontroll', 'rackvidd'):
                    tillatna = {
                        'hot': set(katalog.hot), 'sarbarheter': set(rb.sarbarheter),
                        'kontroll': set(katalog.kontroller),
                        'rackvidd': {r.id for k in katalog.kontroller for r in rb.kontroller[k].rackvidd if r.tjanst == a.tjanst},
                    }[namn]
                if tillatna is not None:
                    refs = (v,) if isinstance(v, str) else v or ()
                    # Äldre överföringar kan innehålla samma belägg flera gånger.
                    # Bevara orörda värden; en ändring får inte införa dubbletter.
                    if len(refs)!=len(set(refs)) and v!=gammalt:
                        raise RiskanalysFel('Välj unika registrerade belägg och referenser.')
                    if any(id not in tillatna for id in refs):
                        raise RiskanalysFel('Välj registrerade belägg och referenser som hör till tjänstens analys.')
                else:
                    kontrollera(v,gammalt)
        elif isinstance(data, (tuple, list)):
            gamla = tidigare if isinstance(tidigare,(tuple,list)) else ()
            index = {radnyckel(v):v for v in gamla if radnyckel(v) is not None}
            for i,v in enumerate(data):
                nyckel = radnyckel(v)
                gammalt = index.get(nyckel) if nyckel is not None else (gamla[i] if i<len(gamla) else None)
                kontrollera(v,gammalt)

    raw = a.model_dump(mode='json')
    tidigare = hamta_tjanst(paket,a.tjanst).model_dump(mode='json')
    kontrollera({k: raw[k] for k in BLOCKFALT[nummer] if k != 'scenariokopplingar'},tidigare)


def hamta_scenario(paket, scenario):
    if paket is None:raise RiskanalysFel('Starta analysen först.')
    s = next((s for s in paket.gemensamma_scenarier if s.id == scenario), None)
    if s is None:
        raise RiskanalysFel('Välj ett registrerat gemensamt scenario.')
    return s



def tillampa_block(paket: m.Analyspaket, c: Blockandring, *, rb=None) -> m.Analyspaket:
    """Pröva blockgräns, referenser och visad summa mot låsets aktuella paket."""
    if c.nummer not in BLOCKFALT or c.operation not in ('spara','bekrafta'):
        raise RiskanalysFel('Välj ett av guidens sexton block och en giltig operation.')
    tillatna = set(BLOCKFALT[c.nummer]) - {'scenariokopplingar'}
    data = dict(c.varden)
    if len(data) != len(c.varden) or set(data) != tillatna:
        raise RiskanalysFel('Ändringen måste omfatta enbart det namngivna analysblocket.')
    a = hamta_tjanst(paket, c.tjanst)
    block = m.Analysblock.model_validate(c.block.model_dump(mode='json'))
    if block.nummer != c.nummer or block.bekraftad_summa is not None:
        raise RiskanalysFel('Kommandot får inte flytta block eller skapa en attest.')
    if c.nummer in ALLTID and block.aktivering != 'aktiv':
        raise RiskanalysFel('Detta block krävs för varje erbjuden tjänst.')
    if c.operation == 'bekrafta' and c.visad_summa != p.blocksumma(paket,c.tjanst,c.nummer):
        raise RiskanalysFel('Blocket har ändrats. Läs om sidan före bekräftelse.')
    raw = a.model_dump(mode='python')
    for namn in tillatna & RADFALT:
        gamla = {radidentitet(namn,x) for x in getattr(a,namn)}
        nya = {id for f,id in c.nya_rader if f==namn}
        bort = {id for f,id in c.borttagna_rader if f==namn}
        faktiska = {radidentitet(namn,x) for x in data[namn]}
        if not bort<=gamla or nya & gamla or faktiska != (gamla-bort)|nya:
            raise RiskanalysFel('Befintliga rad-ID:n kan inte ändras. Lägg till en ny rad vid behov.')
    raw.update(data)
    raw['block'] = tuple(sorted((*[b for b in a.block if b.nummer != c.nummer],block),key=lambda b:b.nummer))
    raw['forfattare'] = c.forfattare
    a = m.Tjansteanalys.model_validate(raw)
    _referenser(paket,a,c.nummer,rb)
    nytt = paket.model_copy(update={'tjanster':tuple(a if t.tjanst==c.tjanst else t for t in paket.tjanster)})
    if c.operation == 'bekrafta':
        summa = p.blocksumma(nytt,c.tjanst,c.nummer)
        a = a.model_copy(update={'block':tuple(b.model_copy(update={'bekraftad_summa':summa}) if b.nummer==c.nummer else b for b in a.block)})
        nytt = nytt.model_copy(update={'tjanster':tuple(a if t.tjanst==c.tjanst else t for t in nytt.tjanster)})
    return nytt
