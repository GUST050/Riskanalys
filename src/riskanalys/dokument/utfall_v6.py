"""Lokala utfall för sårbarheter vars exakta underlag inte lämnar byrån."""
from collections.abc import Mapping
from typing import Literal

from riskanalys.bedomning.modeller import Tjanstbedomning
from riskanalys.dokument.klartext import faltnamn, gransmening, under_grans
from riskanalys.dokument.modeller import Textstycke
from riskanalys.dokument.tabeller import kort_varde
from riskanalys.dokument.underlag import AVSNITTSTYP, provas_lokalt
from riskanalys.profil.modeller import Profil, Uppgift
from riskanalys.profil.omfattning import kompatibilitetsvy
from riskanalys.regelverk.modeller import Regelbas
from riskanalys.regelverk.villkor import Sanning, falt_i, tolka_villkor, utvardera

Utfall = Literal['galler', 'ej_uppfyllt', 'under_grans', 'okant', 'inaktuellt']

OMRADEN = {
    'kund': 'Kunder',
    'kanal': 'Distributionskanaler',
    'geo': 'Geografi',
    'verk': 'Egen verksamhet',
    'tj': 'Tjänstespecifika förhållanden',
}
FRASER: dict[Utfall, str] = {
    'galler': 'gäller',
    'ej_uppfyllt': '– villkoret är inte uppfyllt',
    'under_grans': 'förekommer under metodens gräns',
    'okant': 'har okänt utfall. [VERIFIERA]',
    'inaktuellt': 'har inaktuellt underlag. [VERIFIERA]',
}
EJ_FRANVARO = 'Ett villkor som inte är uppfyllt visar inte att risken saknas.'


def sarbarhetsutfall(rb: Regelbas, profil: Profil, sarbarhet_id: str, *, gransindex) -> Utfall:
    """Beskriv det befintliga villkoret; inga egna riskbeslut eller ändrade gränser.

    En sann OR-gren eller falsk AND-gren avgör fortfarande villkoret när en annan
    gren är okänd. Luckorna redovisas separat i fälttexten. Undergränsstatus kräver
    ett falskt villkor utan okända delar, så en enskild jämförelse inte ersätter
    det sammansatta sanningsvärdet.
    """
    profil = kompatibilitetsvy(profil, rb)
    s = rb.sarbarheter[sarbarhet_id]
    villkor = tolka_villkor(s.villkor, rb.faltdefinitioner())
    utfall = utvardera(villkor, profil.faltvarden())
    if utfall.sanning is Sanning.SANT:
        return 'galler'
    if utfall.sanning is Sanning.FALSKT:
        if not utfall.okanda and under_grans(profil, s.villkor):
            return 'under_grans'
        return 'ej_uppfyllt'
    if any(profil.uppgifter.get(ref, Uppgift()).inaktuell for ref in falt_i(villkor)):
        return 'inaktuellt'
    return 'okant'


def _faltmetadata(rb, profil, ref):
    u = profil.uppgifter.get(ref, Uppgift())
    falt = rb.falt[ref]
    omfang = 'tjänstens underlag' if ref.startswith('P-TJ.') else 'byråövergripande'
    if u.period:
        period = f'period {u.period.fran}–{u.period.till}'
    elif falt.periodkrav:
        period = 'period saknas. [VERIFIERA]'
    elif u.datum:
        period = f'bekräftat {u.datum}'
    else:
        period = 'datum saknas. [VERIFIERA]'
    return omfang, period


def _falttext(rb, profil, ref, *, gransindex, fordelning, gemensam_metadata=None):
    u = profil.uppgifter.get(ref, Uppgift())
    falt = rb.falt[ref]
    # Inaktuella siffror återges aldrig som aktuella värden; perioden visar vilket
    # underlag som behöver ersättas. Källfritext hör fortsatt hemma i bilagan.
    varde = 'inaktuellt underlag. [VERIFIERA]' if u.inaktuell else kort_varde(
        rb, profil, ref, gransindex=gransindex)
    n = fordelning.get(ref, fordelning.get(falt.antalfalt)) if fordelning else None
    if n is not None and not u.inaktuell and profil.ar_bekraftad(ref):
        varde += f', varav {n} i tjänsten'
    omfang, period = _faltmetadata(rb, profil, ref)
    if (omfang, period) == gemensam_metadata:
        return varde
    return f'{omfang}, {varde}, {period}'


def utfallsstycken(rb: Regelbas, profil: Profil, t: Tjanstbedomning, *, gransindex,
                  fordelning: Mapping[str, int] | None = None) -> tuple[Textstycke, ...]:
    """Ett lokalt stycke per område efter AI-texten, med omfång och beläggsreferenser.

    Fördelningen är ett separat lokalt tillägg som anroparen validerar. Ett nolltal
    ändrar aldrig byråvillkoret. Denna funktion ingår inte i AI:s skrivkedja.
    """
    profil = kompatibilitetsvy(profil, rb)
    tillatna = rb.tillatelselistor[AVSNITTSTYP].falt
    grupper = {omrade: [] for omrade in OMRADEN}
    for id in rb.tjanster[t.tjanst].sarbarheter:
        falt = falt_i(tolka_villkor(rb.sarbarheter[id].villkor, rb.faltdefinitioner()))
        har_fordelning = bool(fordelning) and any(
            ref in fordelning or rb.falt[ref].antalfalt in fordelning for ref in falt)
        if har_fordelning or provas_lokalt(rb, profil, id, tillatna, gransindex=gransindex):
            grupper[rb.sarbarheter[id].omrade].append(id)
    stycken = []
    for omrade, ids in grupper.items():
        if not ids:
            continue
        poster = []
        granser = []
        refs = [t.tjanst]
        ej_uppfyllt = False
        falt_per_id = {id: sorted(falt_i(tolka_villkor(rb.sarbarheter[id].villkor, rb.faltdefinitioner()))) for id in ids}
        metadata = {_faltmetadata(rb, profil, ref) for falt in falt_per_id.values() for ref in falt}
        gemensam_metadata = next(iter(metadata)) if len(metadata) == 1 and len(ids) > 1 else None
        negativa = []
        for id in ids:
            s = rb.sarbarheter[id]
            falt = falt_per_id[id]
            utfall = sarbarhetsutfall(rb, profil, id, gransindex=gransindex)
            varden = [((faltnamn(rb, ref) + ': ') if len(falt) > 1 else '') + _falttext(
                rb, profil, ref, gransindex=gransindex, fordelning=fordelning,
                gemensam_metadata=gemensam_metadata) for ref in falt]
            if utfall == 'ej_uppfyllt' and len(ids) > 1:
                negativa.append(f'{s.namn} ({"; ".join(varden)})')
            else:
                poster.append(f'{s.namn} {FRASER[utfall]} ({"; ".join(varden)})')
            refs.extend((id, *falt, *s.kallor))
            ej_uppfyllt |= utfall == 'ej_uppfyllt'
            if utfall == 'under_grans':
                granser.extend(gransmening(rb, profil, g, gransindex=gransindex)
                    for g in under_grans(profil, s.villkor))
        if negativa:
            poster.append('För följande faktorer är villkoret inte uppfyllt: ' + '; '.join(negativa))
        metadata_text = f' ({", ".join(gemensam_metadata)})' if gemensam_metadata else ''
        text = f'{OMRADEN[omrade]} enligt byråns underlag{metadata_text}: ' + '; '.join(poster) + '.'
        tillagg = [*dict.fromkeys(granser), *([EJ_FRANVARO] if ej_uppfyllt else [])]
        if tillagg:
            text += ' ' + ' '.join(tillagg)
        stycken.append(Textstycke(typ='analys', text=text,
            referenser=list(dict.fromkeys(refs)), proveniens='lokal'))
    return tuple(stycken)
