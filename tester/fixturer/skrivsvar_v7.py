"""Syntetiska V7-svar; äldre testsvar och deras ordalydelse lämnas orörda."""
from riskanalys.dokument.faktablad import bygg_faktablad
from riskanalys.dokument.modeller import AISvar, AIStycke, AIOklarhet
from riskanalys.dokument.skrivversion import V7


def godkant_svar_v7(rb, profil, t, avsnitt_id):
    fb = bygg_faktablad(rb, profil, t, avsnitt_id, formatversion=V7)
    text = (
        f'Uppdraget avser {fb.tjanst_namn.lower()} och behöver förstås utifrån kundens verksamhet och de handlingar '
        'som ingår i uppdraget. Kundens egna uppgifter behöver skiljas från oberoende underlag. '
        'Arbetets mandat och tillgången till betalningsinformation bestämmer vilka affärshändelser som kan följas. '
        'Förändrade instruktioner kan innebära att tidigare förståelse behöver omprövas inför fortsatt arbete. '
        'Dokumentationen behöver därför ange vilka delar av flödet uppdraget faktiskt omfattar.'
    )
    refs = [fb.tjanst_id]
    oklarheter = []
    val = [u for u in fb.poster if u.id.endswith(('_attest', '_betalningsmandat', '_bankinsyn'))]
    for u in val:
        refs.append(u.id)
        if u.status == 'okänd':
            oklarheter.append(AIOklarhet(uppgift_id=u.id, fraga='Hur ser mandatet och insynen ut i tjänsten?'))
    if oklarheter:
        text += ' Mandat och insyn behöver kompletteras. [VERIFIERA]'
    uppdrag = AIStycke(typ='analys', referenser=refs, text=text)
    scenario = AIStycke(typ='scenario', referenser=[h.id for h in fb.hot] + ['P-KUND.antal_aktiva'], text=(
        'En kund kan använda fabricerade handlingar för att ge brottsvinster ett legitimt utseende i uppdraget. '
        'Ett annat möjligt upplägg är att dölja den verkliga mottagaren bakom skenbara affärshändelser och mellanled. '
        'Vid finansiering av terrorism kan till synes lagliga medel föras vidare genom betalningar vars syfte är oklart. '
        'Detta är möjliga scenarier och visar inte att sådana händelser har observerats hos byrån.'
    ))
    exponering = AIStycke(typ='analys', referenser=['P-KUND.antal_aktiva'] + [s.id for s in fb.sarbarheter if s.galler != 'prövas lokalt'], text=(
        'Byråövergripande uppgifter beskriver kundbasen och belägger ingen fördelning på tjänstens kunder. '
        'Kund-, kanal- och geografiförhållanden behöver förstås med denna avgränsning. '
        'Ett eventuellt överlapp behöver undersökas innan gemensam exponering kan påstås. '
        'Generella kontrollbeskrivningar bekräftar varken utfört arbete eller lokal effekt; dokumenterade insynsluckor '
        'och underlagens tillförlitlighet behöver bedömas i det enskilda uppdraget.'
    ))
    return AISvar(stycken=[uppdrag, scenario, exponering], oklarheter=oklarheter)


def med_verksamhetsval(rb, profil):
    """Uttryckligt syntetiskt uppdrag: kunden attesterar, byrån har inget betalningsmandat och läser utdrag."""
    from tester.fixturer.m2 import DAG
    from riskanalys.profil.modeller import Uppgift
    upp = dict(profil.uppgifter)
    for id, f in rb.falt.items():
        if id.endswith(('_attest', '_betalningsmandat', '_bankinsyn')):
            upp[id] = Uppgift(varde=f.val[0], status='bekräftad', kalla='Syntetiskt uppdragsbrev',
                datum=DAG, bekraftad_av='Syntetisk uppdragsansvarig')
    return profil.model_copy(update={'uppgifter': upp})


def tjanstspecifikt_svar_v7(rb, profil, t, avsnitt_id):
    """Full V7-analys plus verkliga särskiljande arbetsmoment ur det historiska syntetiska tjänstefallet."""
    from tester.fixturer.m2 import godkant_delsvar
    svar = godkant_svar_v7(rb, profil, t, avsnitt_id)
    arbetsmoment = godkant_delsvar('hot', t).stycken[0]
    return svar.model_copy(update={'stycken': [arbetsmoment, *svar.stycken]})
