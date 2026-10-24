"""Strikt, sidoeffektsfri adapter från guidade fält till analysmodeller."""
from dataclasses import dataclass
from datetime import date
from types import UnionType
from typing import Literal, get_args, get_origin

from pydantic import BaseModel, ValidationError

from riskanalys.analys import modeller as m
from riskanalys.analys.provning import ALLTID, BLOCKFALT
from riskanalys.fel import RiskanalysFel
from riskanalys.analys.andringar import hamta_tjanst, hamta_scenario, _referenser, Blockandring, Scenarioval, Scenarioandring, Modellriskandring, Modellfelandring, radidentitet

RADER = {
    'delanalyser': m.Delanalys, 'leverantorer': m.Leverantorsprovning,
    'scenarier': m.Scenarioanalys, 'sarbarhetsprovningar': m.Sarbarhetsprovning,
    'kontroller': m.Kontrollprovning, 'gap': m.Analysgap,
    'rutinatgarder': m.Rutinatgard,
}
METADATA = frozenset({'csrf', 'revision', 'tjanst', 'nummer', 'operation',
    'forfattare', 'aktivering', 'aktiveringsmotivering', 'visad_summa'})


@dataclass(frozen=True)
class Formularblock:
    tjanst: m.Tjansteanalys
    operation: str
    forfattare: str
    visad_summa: str




def grundtyp(annotation):
    if get_origin(annotation) is UnionType:
        return next(a for a in get_args(annotation) if a is not type(None))
    return annotation


def faltlista(modell, prefix=''):
    """Endast blockets förvalda modell får definiera dess fältnamn."""
    for namn, field in modell.model_fields.items():
        typ = grundtyp(field.annotation)
        nyckel = prefix + namn
        if isinstance(typ, type) and issubclass(typ, BaseModel):
            yield from faltlista(typ, nyckel + '.')
        else:
            yield nyckel, typ, field.annotation


def _varde(text, typ, annotation):
    if not text.strip() and type(None) in get_args(annotation):
        return None
    if get_origin(typ) is tuple:
        ids = tuple(x.strip() for x in text.split(',') if x.strip())
        if len(ids) != len(set(ids)):
            raise ValueError('Dubbla referenser')
        return ids
    if typ is date:
        return date.fromisoformat(text)
    return text


def _objekt(modell, tidigare, prefix, data, tillatna):
    raw = tidigare.model_dump(mode='json') if tidigare else {}
    if tidigare and 'id' in raw and data.get(prefix + 'id', raw['id']).strip() != raw['id']:
        raise RiskanalysFel('Befintliga rad-ID:n kan inte ändras. Lägg till en ny rad vid behov.')
    for key, typ, annotation in faltlista(modell, prefix):
        tillatna.add(key)
        if key not in data:
            continue
        stig = key.removeprefix(prefix).split('.')
        pos = raw
        for steg in stig[:-1]:
            pos = pos.setdefault(steg, {})
        pos[stig[-1]] = _varde(data[key], typ, annotation)
    return modell.model_validate(raw)


def las_blockformular(paket, tjanst, nummer, data, *, rb=None) -> Formularblock:
    """Bygg kandidat. Kärntjänsten äger identitet, CAS och bekräftelse/attest."""
    if nummer not in BLOCKFALT:
        raise RiskanalysFel('Välj ett av guidens sexton block.')
    a = hamta_tjanst(paket, tjanst)
    data = normalisera_urval(data, _blockfalt(a, nummer), referensval(paket, a, rb))
    operation = data.get('operation', 'spara')
    if operation not in ('spara', 'bekrafta'):
        raise RiskanalysFel('Välj spara utkast eller bekräfta visat block.')
    tillatna = set(METADATA)
    raw = a.model_dump(mode='json')
    try:
        for namn in BLOCKFALT[nummer]:
            if namn == 'scenariokopplingar':
                # Gemensamma val har en separat, hashbunden kommandoväg.
                continue
            if namn in RADER:
                poster = []
                tidigare = getattr(a, namn)
                for i in range(len(tidigare) + 1):
                    prefix = f'{namn}.{i}.'
                    tillatna.update({prefix + 'anvand', prefix + 'ta_bort'})
                    finns = i < len(tidigare)
                    anvand = data.get(prefix + 'anvand', 'ja' if finns else '')
                    bort = data.get(prefix + 'ta_bort', '')
                    if anvand not in ('', 'ja') or bort not in ('', 'ja'):
                        raise ValueError('Ogiltigt radval')
                    # Validera nycklar även för en orörd tom extrarad.
                    tillatna.update(k for k, _, _ in faltlista(RADER[namn], prefix))
                    if bort == 'ja' or anvand != 'ja':
                        continue
                    post = _objekt(RADER[namn], tidigare[i] if finns else None, prefix, data, tillatna)
                    poster.append(post.model_dump(mode='json'))
                raw[namn] = poster
            else:
                typ = grundtyp(m.Tjansteanalys.model_fields[namn].annotation)
                if isinstance(typ, type) and issubclass(typ, BaseModel):
                    raw[namn] = _objekt(typ, getattr(a, namn), namn + '.', data, tillatna).model_dump(mode='json')
                else:
                    tillatna.add(namn)
                    if namn in data:
                        raw[namn] = _varde(data[namn], typ, m.Tjansteanalys.model_fields[namn].annotation)
        if set(data) - tillatna:
            raise RiskanalysFel('Formuläret innehåller fält utanför det visade analysblocket. Läs om sidan.')
        aktivering = data.get('aktivering', next((b.aktivering for b in a.block if b.nummer == nummer), 'aktiv' if nummer in ALLTID else 'okand'))
        if nummer in ALLTID and aktivering != 'aktiv':
            raise RiskanalysFel('Detta block krävs för varje erbjuden tjänst.')
        block = m.Analysblock(nummer=nummer, aktivering=aktivering,
            motivering=data.get('aktiveringsmotivering', next((b.motivering for b in a.block if b.nummer == nummer), '')))
        raw['block'] = [b.model_dump(mode='json') for b in a.block if b.nummer != nummer] + [block.model_dump(mode='json')]
        raw['block'].sort(key=lambda b: b['nummer'])
        kandidat = m.Tjansteanalys.model_validate(raw)
    except (ValueError, ValidationError) as exc:
        raise RiskanalysFel('Kontrollera status, datum och referenser i analysblocket.') from exc
    _referenser(paket, kandidat, nummer, rb)
    if operation == 'bekrafta':
        from riskanalys.analys.provning import blocksumma
        visad = blocksumma(paket, tjanst, nummer)
        if data.get('visad_summa') != visad:
            raise RiskanalysFel('Blocket har ändrats. Läs om sidan före bekräftelse.')
    return Formularblock(kandidat, operation, data.get('forfattare', '').strip(), data.get('visad_summa', ''))






def las_scenarioval(paket, tjanst, scenario, data) -> m.Scenariokoppling:
    """Validerad ogranskad kandidat; kärntjänsten bekräftar under sitt lås."""
    from riskanalys.analys.provning import scenariosumma
    a = hamta_tjanst(paket, tjanst)
    s = hamta_scenario(paket, scenario)
    tillatna = {'csrf', 'revision', 'tjanst', 'scenario', 'visad_summa', 'tillampning', 'lokal_scenario', 'motivering', 'forfattare'}
    if set(data) - tillatna or data.get('visad_summa') != scenariosumma(s):
        raise RiskanalysFel('Det gemensamma scenariot har ändrats eller formuläret är ogiltigt. Läs om jämförelsen.')
    val = data.get('tillampning', '')
    lokal = data.get('lokal_scenario', '').strip() or None
    motivering = data.get('motivering', '').strip() or None
    if val == 'avviker' and (lokal not in {s.id for s in a.scenarier} or not motivering):
        raise RiskanalysFel('Välj en lokal scenarioanalys för denna tjänst och motivera avvikelsen.')
    if val == 'samma' and lokal:
        raise RiskanalysFel('En lokal avvikelse kräver valet avviker.')
    if val not in ('samma', 'avviker'):
        raise RiskanalysFel('Välj uttryckligen samma eller avviker efter genomgången.')
    return m.Scenariokoppling(scenario=scenario, tillampning=val,
        lokal_scenario=lokal, motivering=motivering,
        scenariosumma=scenariosumma(s), bekraftad=False)


def referensval(paket, a, rb=None):
    """Stabila indexval med läsbara etiketter; samma lista för vy och adapter."""
    belagg = []
    for b in paket.belagg:
        kalla = ', '.join((rb.falt[f].etikett or rb.falt[f].fraga) if rb and f in rb.falt else f for f in b.profilfalt) or 'Privat dokumentkopia'
        period = f' · period {b.period.fran}–{b.period.till}' if b.period else ''
        belagg.append((b.id, kalla + f' · {b.datum}' + period))
    v = {key: tuple(belagg) for key in ('belagg', 'exponeringsbelagg', 'erfarenhetsbelagg')}
    v['scenarier'] = tuple((s.id, s.rubrik or s.id) for s in (*a.scenarier, *paket.gemensamma_scenarier))
    v['delanalyser'] = tuple((d.id, d.rubrik or d.id) for d in a.delanalyser)
    if rb and a.tjanst in rb.tjanster:
        kat = rb.tjanster[a.tjanst]
        v['hot'] = tuple((id, rb.hot[id].namn) for id in kat.hot)
        v['sarbarheter'] = tuple((id, s.namn) for id, s in rb.sarbarheter.items())
        v['rackvidd'] = tuple((r.id, rb.kontroller[k].namn + ': ' + r.kan_belagga) for k in kat.kontroller for r in rb.kontroller[k].rackvidd if r.tjanst == a.tjanst)
    return v


def normalisera_urval(data, falt, val):
    """Checkboxfält har unika namn; dubblettnyckelskyddet förblir intakt."""
    nytt = dict(data)
    for key, typ, _ in falt:
        blad = key.rsplit('.', 1)[-1]
        marker = key + '.urval'
        if get_origin(typ) is not tuple or blad not in val or marker not in data:
            continue
        if data[marker] != 'ja' or key in data:
            raise RiskanalysFel('Referensurvalet är ogiltigt. Välj bara bland de visade alternativen.')
        options = val[blad]
        tillatna = {f'{key}.val.{i}': id for i, (id, _) in enumerate(options)}
        inskickat = {k: v for k, v in data.items() if k.startswith(key + '.val.')}
        if any(k not in tillatna or v != tillatna[k] for k, v in inskickat.items()):
            raise RiskanalysFel('Referensurvalet innehåller ett ogiltigt eller okänt alternativ. Läs om sidan.')
        nytt[key] = ','.join(id for k, id in tillatna.items() if k in inskickat)
        del nytt[marker]
        for k in inskickat:
            del nytt[k]
    return nytt


def _blockfalt(a, nummer):
    for namn in BLOCKFALT[nummer]:
        if namn == 'scenariokopplingar':
            continue
        if namn in RADER:
            for i in range(len(getattr(a, namn)) + 1):
                yield from faltlista(RADER[namn], f'{namn}.{i}.')
        else:
            field = m.Tjansteanalys.model_fields[namn]
            typ = grundtyp(field.annotation)
            if isinstance(typ, type) and issubclass(typ, BaseModel):
                yield from faltlista(typ, namn + '.')
            else:
                yield namn, typ, field.annotation



def las_blockandring(paket, tjanst, nummer, data, *, revision, rb=None) -> Blockandring:
    r = las_blockformular(paket,tjanst,nummer,data,rb=rb)
    a = hamta_tjanst(paket,tjanst)
    varden = tuple((f,getattr(r.tjanst,f)) for f in BLOCKFALT[nummer] if f!='scenariokopplingar')
    nya, bort = [], []
    for f in RADER.keys() & set(BLOCKFALT[nummer]):
        fore = {radidentitet(f,x) for x in getattr(a,f)}
        efter = {radidentitet(f,x) for x in getattr(r.tjanst,f)}
        nya.extend((f,id) for id in sorted(efter-fore))
        bort.extend((f,id) for id in sorted(fore-efter))
    return Blockandring(tjanst,nummer,revision,r.operation,r.forfattare,r.visad_summa,
        next(b for b in r.tjanst.block if b.nummer==nummer),varden,tuple(nya),tuple(bort))


def las_scenariokommando(paket,tjanst,scenario,data,*,revision):
    return Scenarioval(tjanst,scenario,revision,data.get('forfattare',''),las_scenarioval(paket,tjanst,scenario,data))


def las_gemensamandring(paket,scenario,data,*,revision,rb):
    tidigare = hamta_scenario(paket,scenario)
    val = referensval(paket,m.Tjansteanalys(tjanst=''),rb)
    val['hot'] = tuple((id,rb.hot[id].namn) for id in tidigare.hot)
    data = normalisera_urval(data,faltlista(m.Scenarioanalys),val)
    tillatna = {'csrf','revision','scenario','visad_summa','forfattare','hot','rubrik','handelseforlopp','relevans','motivering','belagg'}
    if set(data)-tillatna:
        raise RiskanalysFel('Välj bara fält i det gemensamma scenarioformuläret.')
    varden = tuple((k,tuple(x.strip() for x in v.split(',') if x.strip()) if k in ('hot','belagg') else v)
        for k,v in data.items() if k in ('hot','rubrik','handelseforlopp','relevans','motivering','belagg'))
    return Scenarioandring(scenario,revision,data.get('forfattare',''),data.get('visad_summa',''),varden)


def las_modellfelandring(paket,data):
    if paket is None or paket.modellrisk is None:raise RiskanalysFel('Registrera paketets lokala modellriskunderlag före feluppföljning.')
    val = {'belagg':tuple((b.id,b.id) for b in paket.belagg if b.dokument)}
    data = normalisera_urval(data,[('belagg',tuple[str,...],tuple[str,...])],val)
    tillatna = {'csrf','revision','id','datum','beskrivning','allvar','status','atgard_och_omprovning','belagg'}
    if set(data)-tillatna:raise RiskanalysFel('Välj bara de visade lokala modellfälten.')
    return Modellfelandring(id=data.get('id',''),datum=date.fromisoformat(data.get('datum','')),
        beskrivning=data.get('beskrivning',''),allvar=data.get('allvar',''),status=data.get('status',''),
        atgard_och_omprovning=data.get('atgard_och_omprovning',''),belagg=tuple(x.strip() for x in data.get('belagg','').split(',') if x.strip()))


def las_modellriskandring(data):
    tillatna = {'csrf','revision','rutinbelagg','modellansvarig','utvarderad','nasta_genomgang','feluppfoljning','godkand','beslutad_av','beslutsdatum'}
    if set(data)-tillatna or data.get('godkand') not in ('ja','nej'):
        raise RiskanalysFel('Pröva modellens lokala användning och välj uttryckligen ja eller nej.')
    return Modellriskandring(data.get('rutinbelagg',''),data.get('modellansvarig',''),
        date.fromisoformat(data.get('utvarderad','')),date.fromisoformat(data.get('nasta_genomgang','')),
        data.get('feluppfoljning',''),data['godkand']=='ja',data.get('beslutad_av',''),date.fromisoformat(data.get('beslutsdatum','')))
