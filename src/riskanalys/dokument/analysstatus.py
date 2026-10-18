"""Beskriv registrerad analys och modellrapport utan att attestera eller läsa filer."""
from riskanalys.analys.provning import gallande_beslut
from riskanalys.dokument.tjanstavsnitt_v6 import lokaltext
from riskanalys.drift.modellrapport import Modellvalidering, valideringens_innehallssumma


def analysstatus(rb, bedomning, paket, brister, *, formatversion=None):
    if paket is None:
        return (lokaltext('Lokal analys och dess godkännande saknas. Dokumentet är ett ofullständigt utkast. [VERIFIERA]'),)
    poster = []
    for t in bedomning.tjanster:
        if t.erbjuds is False:
            continue
        beslut = gallande_beslut(paket, t.tjanst)
        text = rb.tjanster[t.tjanst].namn + ': '
        text += ('godkänt beslut registrerat' if beslut.godkand else 'senaste beslut är underkänt') if beslut else 'aktuellt godkännande saknas'
        if beslut:
            text += f' {beslut.datum}.'
            if beslut.egen_granskning:
                text += ' Författare och godkännare är samma person.'
        else:
            text += '. [VERIFIERA]'
        poster.append(lokaltext(text, [t.tjanst, 'D-ARB.B1']))
    if formatversion == 'D-ARB-tjanst-v7':
        grupper = {}
        for post in poster:
            namn, text = post.text.split(': ', 1)
            grupper.setdefault(text, []).append((namn, post))
        poster = [lokaltext(', '.join(namn for namn, _ in delar) + ': ' + text,
            tuple(dict.fromkeys(ref for _, post in delar for ref in post.referenser)))
            for text, delar in grupper.items()]
    if brister:
        poster.append(lokaltext(f'Lokal analys har {len(brister)} kompletteringspunkter eller bindningsbrister. Se B1; registrerat beslut undanröjer inte dessa. [VERIFIERA]', ['D-ARB.B1']))
    poster.append(lokaltext('Registrerade beslut är inte ett fastställt dokument. Filaktualitet och slutliga grindar prövas separat.', ['D-ARB.B1']))
    return tuple(poster)


def modellstatus(paket, rapport: Modellvalidering | None):
    mr = paket.modellrisk if paket else None
    refs = ['D-ARB.B1']
    if mr is None:
        return (lokaltext('Modellriskunderlag och lokalt användningsgodkännande saknas. M1 är inte styrkt i detta dokument. [VERIFIERA]', refs),)
    poster = [lokaltext(f'Modellbindning: {mr.modellbindning}. Byråns användningsbeslut: '+('godkänt' if mr.godkand else 'inte godkänt')
        + f', {mr.beslutsdatum}; nästa modellgenomgång {mr.nasta_genomgang}.', refs)]
    if any(f.allvar == 'vasentligt' and f.status == 'oppet' for f in mr.fel):
        poster.append(lokaltext('Öppet väsentligt modellfel kräver omprövning före slutligt godkännande. Felakten återges inte i Word. [VERIFIERA]', refs))
    if rapport is None:
        poster.append(lokaltext('Projektets rapportbeskrivning saknas i dokumentunderlaget; M1 och rapportens sakkunnigstatus är inte styrkta här. [VERIFIERA]', refs))
        return tuple(poster)
    stammer = (rapport.modellbindning == paket.bindning.modell == mr.modellbindning
        and rapport.rapport_kontrollsumma == mr.valideringsrapport.kontrollsumma
        and rapport.modellfiler_kontrollsumma == mr.modellfiler.kontrollsumma)
    giltig = (rapport.sakkunnig.galler(valideringens_innehallssumma(rapport))
        and bool(rapport.sakkunnig.av and rapport.sakkunnig.av.strip())
        and rapport.sakkunnig.datum is not None and rapport.datum <= rapport.sakkunnig.datum <= mr.utvarderad)
    sakkunnig = 'giltigt sakkunnigverifierad' if giltig else 'inte giltigt sakkunnigverifierad'
    m1 = {'ej_provat': 'ej prövat', 'godkant': 'godkänt', 'andring_kravs': 'ändring krävs'}[rapport.m1_beslut]
    poster.append(lokaltext(f'Projektets rapport {rapport.rapportversion}, {rapport.datum}: M1 {m1}; {sakkunnig}. '
        + ('Modell-/rapportkopplingen stämmer med det lämnade analysunderlaget.' if stammer else 'Modell-/rapportkopplingen avviker. [VERIFIERA]'), refs))
    poster.append(lokaltext('Rapportens begränsningar: '+rapport.begransningar, refs))
    if rapport.m1_beslut != 'godkant' or not giltig or not stammer:
        poster.append(lokaltext('Metodfrågan M1 är inte styrkt godkänd med giltig sakkunnigprövning. [VERIFIERA]', refs))
    # Modellfelakter, fritext om enskilda fel och deras filnamn infogas aldrig.
    return tuple(poster)
