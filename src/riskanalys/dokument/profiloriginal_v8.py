"""Typade originalspann för profiloperationer i den aktuella V8-producenten."""

from riskanalys.bedomning.erfarenheter import belagd_uppgift


def _aktuell(uppgift):
    return bool(uppgift and uppgift.status == 'bekräftad' and not uppgift.inaktuell)


def _textbelagd(uppgift):
    return bool(_aktuell(uppgift) and uppgift.kalla and uppgift.kalla.strip()
        and uppgift.bekraftad_av and uppgift.bekraftad_av.strip() and uppgift.datum
        and uppgift.varde is not None
        and (not isinstance(uppgift.varde,str) or uppgift.varde.strip()))


def spann_for_original(text: str, original: str, *, krav: bool = False) -> tuple[tuple[int, int], ...]:
    if not original:
        return ()
    start=text.find(original)
    if start < 0:
        if krav:
            raise ValueError('V8:s aktuella profiloriginal saknas i producentens text.')
        return ()
    return ((start,start+len(original)),)


def ansvarsmotiveringsspann(text: str, roll: str, original: str) -> tuple[tuple[int, int], ...]:
    """Skydda råmotiveringens infogningsposition, inte lika programtoken-träffar."""
    if not original:
        return ()
    prefix = f'Dokumenterad ansvarsfunktion: {roll}. Ansvarsfördelning: '
    if not text.startswith(prefix):
        raise ValueError('V8:s syftesoperation saknar ansvarsmotiveringens infogningsposition.')
    start = len(prefix)
    if not text.startswith(original, start):
        raise ValueError('V8:s ansvarsmotivering saknas på sin infogningsposition.')
    return ((start, start + len(original)),)


def _alla_spann(text: str, original: str) -> tuple[tuple[int, int], ...]:
    if not original:
        return ()
    spann=[]
    start=0
    while (plats:=text.find(original,start)) >= 0:
        spann.append((plats,plats+len(original)))
        start=plats+len(original)
    return tuple(spann)


def spann_for_profiltext(regelbas, profil, falt_id: str, text: str, *, krav_varde: bool = False,
                         krav_kalla: bool = False) -> tuple[tuple[int, int], ...]:
    """Skydda profilvärde och källa separat i en avgränsad producenttext."""
    uppgift = profil.uppgifter.get(falt_id)
    if not belagd_uppgift(regelbas, profil, falt_id):
        return ()
    spann=[]
    if isinstance(uppgift.varde,str) and uppgift.varde:
        value_spans=_alla_spann(text,uppgift.varde)
        if krav_varde and not value_spans:
            raise ValueError('V8:s aktuella profiloriginal saknas i producentens text.')
        spann.extend(value_spans)
    elif krav_varde and uppgift.varde not in (None, ''):
        raise ValueError('V8:s aktuella profiloriginal har ingen bokstavlig strängoperation.')
    if uppgift.kalla:
        markor='källa: '
        kallspann=tuple((start+len(markor),start+len(markor)+len(uppgift.kalla))
            for start,_ in _alla_spann(text,markor+uppgift.kalla))
        if kallspann:
            spann.extend(kallspann)
        elif krav_kalla:
            raise ValueError('V8:s aktuella källoriginal saknas i producentens text.')
    return tuple(spann)


def _rollspann(regelbas, profil, falt_id, text) -> tuple[tuple[int, int], ...]:
    """Förväntade spann för faktiska profilsträngar med rollsyntax."""
    uppgift = profil.uppgifter.get(falt_id)
    if not belagd_uppgift(regelbas, profil, falt_id):
        return ()
    spann=[]
    if isinstance(uppgift.varde,str) and '{roll:' in uppgift.varde:
        found=_alla_spann(text,uppgift.varde)
        if not found:
            raise ValueError('V8:s aktuella profilvärde med rollsyntax saknas i producenttexten.')
        spann.extend(found)
    if uppgift.kalla and '{roll:' in uppgift.kalla:
        found=tuple((a+len('källa: '),a+len('källa: ')+len(uppgift.kalla))
            for a,_ in _alla_spann(text,'källa: '+uppgift.kalla))
        if not found:
            raise ValueError('V8:s aktuella källtext med rollsyntax saknas i producenttexten.')
        spann.extend(found)
    return tuple(spann)


def _roll_vardespann(text, uppgift) -> tuple[tuple[int, int], ...]:
    if not _aktuell(uppgift) or not isinstance(uppgift.varde,str) or '{roll:' not in uppgift.varde:
        return ()
    found=_alla_spann(text,uppgift.varde)
    if not found:
        raise ValueError('V8:s aktuella profilvärde med rollsyntax saknas i producenttexten.')
    return found


def b1_spann(regelbas, profil, falt_id: str, text: str) -> tuple[tuple[int, int], ...]:
    """B1:s råfältsrad återger ordagrant profilvärde och källmetadata."""
    uppgift = profil.uppgifter.get(falt_id)
    if not belagd_uppgift(regelbas, profil, falt_id):
        return ()
    markor = f'({falt_id}): '
    rad = text.find(markor)
    if rad < 0:
        return ()
    spann = []
    start = rad + len(markor)
    if text.startswith('personuppgift hanteras lokalt i ansvarsfördelningen;', start):
        # Producentens uttryckliga dataminimeringsgren; personnamn upprepas inte i B1.
        return ()
    if isinstance(uppgift.varde,str) and uppgift.varde:
        if not text.startswith(uppgift.varde, start):
            raise ValueError(f'B1:s aktuella profiloriginal saknas för {falt_id}.')
        spann.append((start, start + len(uppgift.varde)))
        efter_varde = start + len(uppgift.varde)
    else:
        efter_varde = start
    if uppgift.kalla:
        markor_kalla = 'källa: '
        plats = text.find(markor_kalla, efter_varde)
        if plats < 0 or not text.startswith(uppgift.kalla, plats + len(markor_kalla)):
            raise ValueError(f'B1:s aktuella källoriginal saknas för {falt_id}.')
        kallstart = plats + len(markor_kalla)
        spann.append((kallstart, kallstart + len(uppgift.kalla)))
    return tuple(spann)


def omfattningsspann(regelbas, profil, falt_id: str, text: str, *, krav: bool = False) -> tuple[tuple[int, int], ...]:
    """D-ARB.2:s uttryckliga motiveringsoperation, skild från andra profilreferenser."""
    uppgift = profil.uppgifter.get(falt_id)
    if not belagd_uppgift(regelbas, profil, falt_id) or not isinstance(uppgift.varde,str) or not uppgift.varde:
        return ()
    markor = 'Byråns motivering: '
    plats = text.find(markor)
    if plats < 0:
        if krav:
            raise ValueError('V8:s omfattningsoperation för profiloriginal saknas.')
        return ()
    start = plats + len(markor)
    if not text.startswith(uppgift.varde, start):
        raise ValueError('V8:s aktuella omfattningsoriginal saknas i dokumentkroppen.')
    return ((start, start + len(uppgift.varde)),)


def kontrollera_aktuella_originaloperationer(dokument, profil, regelbas, bedomning) -> None:
    """Kräv spann för de faktiska V8-profiloperationerna före aktuell användning.

    B1-fältoperationen identifieras av dess egna fält-ID-radmarkör. Andra
    stycken som bara hänvisar till samma profilfält saknar den markören och
    skapar därför inget krav på att de ska upprepa råvärdet. Programbyggda
    syftes-, geografi- och uppföljningsstycken kontrolleras bara för sina
    uttryckliga profiloperationer.
    """
    from riskanalys.dokument.skrivversion import V8
    from riskanalys.regelverk.granser import metodgransindex
    from riskanalys.dokument.klartext import uppgiftstext
    from riskanalys.dokument.tabeller import kort_varde

    if dokument.formatversion != V8:
        return
    for avsnitt in dokument.avsnitt:
        if avsnitt.id == 'D-ARB.B1':
            for stycke in avsnitt.stycken:
                for falt_id in stycke.referenser:
                    if falt_id not in profil.uppgifter or f'({falt_id}): ' not in stycke.text:
                        continue
                    falt = regelbas.falt.get(falt_id)
                    if falt is None:
                        raise ValueError(f'V8:s B1 hänvisar till okänt fält {falt_id}.')
                    from riskanalys.dokument.intagsunderlag import _b1_falt_inkluderas, _b1_falttext
                    if not _b1_falt_inkluderas(regelbas, profil, falt):
                        raise ValueError(f'V8:s B1 visar ett fält som producenten inte tar med: {falt_id}.')
                    if not belagd_uppgift(regelbas, profil, falt_id):
                        expected = _b1_falttext(regelbas, profil, falt, metodgransindex(regelbas),
                                                bevara_original=True)
                        if stycke.text != expected:
                            raise ValueError(f'V8:s B1 saknar aktuell bristtext för {falt_id}.')
                        continue
                    spann = b1_spann(regelbas, profil, falt_id, stycke.text)
                    if any(x not in stycke.literala_spann for x in spann):
                        raise ValueError(f'V8:s B1-originaloperation saknar spannskydd för {falt_id}.')
        elif avsnitt.id == 'D-ARB.1':
            for stycke in avsnitt.stycken:
                for falt_id in stycke.referenser:
                    if falt_id == 'P-ROLL.ffr_namn':
                        # Syftesstycket använder roll-tokenen som programtext;
                        # fältets namn återges inte som ett direkt profilvärde.
                        continue
                    if falt_id not in profil.uppgifter:
                        continue
                    u=profil.uppgifter[falt_id]
                    try:
                        spann=_roll_vardespann(stycke.text,u)
                    except ValueError as exc:
                        raise ValueError(f'V8:s syftesoperation saknar aktuellt original för {falt_id}.') from exc
                    if any(x not in stycke.literala_spann for x in spann):
                        raise ValueError(f'V8:s syftesoperation saknar spannskydd för {falt_id}.')
                if 'P-ROLL.ffr_namn' in stycke.referenser:
                    u=profil.uppgifter.get('P-ROLL.ffr_namn')
                    original=getattr(u,'motivering',None) if u and u.status=='ej_tillämplig' else None
                    if isinstance(original,str) and original:
                        roll = ('{roll:Ansvarsfunktion}' if profil.ar_bekraftad('P-ROLL.ansvarsfunktion')
                                else '[VERIFIERA]')
                        spann = ansvarsmotiveringsspann(stycke.text, roll, original)
                        if not spann or any(x not in stycke.literala_spann for x in spann):
                            raise ValueError('V8:s syftesoperation saknar spannskydd för ansvarsmotiveringen.')
        elif avsnitt.id.startswith('D-ARB.6'):
            for stycke in avsnitt.stycken:
                for falt_id in stycke.referenser:
                    if falt_id != 'P-BESK.geografi' and not falt_id.endswith('_geografi'):
                        continue
                    operation='Byråns geografibeskrivning: ' if falt_id=='P-BESK.geografi' else 'Tjänstens geografi: '
                    if operation not in stycke.text:
                        continue
                    u=profil.uppgifter.get(falt_id)
                    if not belagd_uppgift(regelbas, profil, falt_id):
                        from riskanalys.profil.omfattning import kompatibilitetsvy
                        from riskanalys.dokument.lasta_v6 import GEOGRAFIBESKRIVNINGAR
                        slug = (regelbas.tjanster[stycke.referenser[0]].erbjuds_falt
                                .removesuffix('_erbjuds')) if stycke.referenser and stycke.referenser[0] in regelbas.tjanster else ''
                        namn = next((namn for mall,namn in GEOGRAFIBESKRIVNINGAR
                                     if mall.format(slug=slug) == falt_id), None)
                        expected = uppgiftstext(regelbas, kompatibilitetsvy(profil, regelbas), falt_id,
                                                namn=namn or 'geografibeskrivning')
                        if expected not in stycke.text:
                            raise ValueError(f'V8:s geografiska profiloperation saknar aktuell bristtext för {falt_id}.')
                        continue
                    spann=_rollspann(regelbas,profil,falt_id,stycke.text)
                    if any(x not in stycke.literala_spann for x in spann):
                        raise ValueError(f'V8:s geografiska profiloperation saknar spannskydd för {falt_id}.')
        elif avsnitt.id in ('D-ARB.10','D-ARB.11'):
            for stycke in avsnitt.stycken:
                for falt_id in stycke.referenser:
                    u=profil.uppgifter.get(falt_id)
                    if not u:
                        continue
                    if not belagd_uppgift(regelbas, profil, falt_id):
                        expected = uppgiftstext(regelbas, profil, falt_id)
                        if expected not in stycke.text:
                            raise ValueError(f'V8:s uppföljningsoperation saknar aktuell bristtext för {falt_id}.')
                        continue
                    spann=_rollspann(regelbas,profil,falt_id,stycke.text)
                    if any(x not in stycke.literala_spann for x in spann):
                        raise ValueError(f'V8:s uppföljningsoperation saknar spannskydd för {falt_id}.')
        elif avsnitt.id == 'D-ARB.2' and len(avsnitt.stycken) > 2:
            stycke = avsnitt.stycken[2]
            falt_id = 'P-OMFATTNING.motivering'
            if falt_id in stycke.referenser and falt_id in profil.uppgifter:
                if not belagd_uppgift(regelbas, profil, falt_id):
                    from riskanalys.dokument.arb import _metod
                    from riskanalys.dokument.arb_v5 import stycke as bygg_stycke
                    from riskanalys.dokument.arb_v5_1 import METODFRAGOR
                    from riskanalys.dokument.arb_v6 import _oppna_metodfragor
                    from riskanalys.dokument.kallhanvisningar import med_kallhanvisningar
                    from riskanalys.dokument.modeller import Avsnitt
                    from riskanalys.dokument.uppfoljning import kort_omfattningsstycke
                    from riskanalys.dokument.skrivversion import V8
                    kanonisk = Avsnitt(id='D-ARB.2', rubrik='Metod och begränsningar', kalla='regelbas',
                        stycken=(_metod(regelbas, bedomning).stycken[0],
                            bygg_stycke('PT avser penningtvätt och TF finansiering av terrorism. Sanktioner prövas separat.'),
                            kort_omfattningsstycke(regelbas, profil, bedomning,
                                gransindex=metodgransindex(regelbas), bevara_original=True),
                            bygg_stycke(_oppna_metodfragor(METODFRAGOR))),
                        formatversion=V8, visningsnummer='2', leveransdel='lasrapport')
                    # Hänvisningsnumren beror på hela dokumentets källregister.
                    # Bara D2 byggs om och kontrolleras; övriga avsnitt bidrar endast
                    # med samma referensmängd som i den kanoniska dekoreringen.
                    med_forvantat = dokument.model_copy(update={'avsnitt': tuple(
                        kanonisk if x.id == 'D-ARB.2' else x for x in dokument.avsnitt)})
                    forvantad = med_kallhanvisningar(med_forvantat, regelbas).avsnitt_med_id()['D-ARB.2'].stycken[2]
                    if stycke != forvantad:
                        raise ValueError('V8:s omfattningsoperation saknar aktuell bristtext.')
                    continue
                spann = omfattningsspann(regelbas, profil, falt_id, stycke.text, krav=True)
                if any(x not in stycke.literala_spann for x in spann):
                    raise ValueError('V8:s omfattningsoriginal saknar spannskydd.')
