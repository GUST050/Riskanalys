"""Källor och bokslutsbakgrund, utan att bakgrund blir bekräftade svar."""
from html import escape as e


def bokslutsperiod(b):
    p = b.bolagsverket.bokslut.period
    return f'{p.fran}–{p.till}'


def extra_forslag(b, id, data):
    if id == 'P-ORG.utlandsk_filial':
        return '<p class="hint">Bolagsverkets organisationsform: '+e(b.bolagsverket.organisationsform)+'. Kontrollera att detta är den juridiska person som bedömningen avser.</p>'
    if id == 'P-BESK.verksamhet':
        value = data.get('verksamhetstext', b.bolagsverket.verksamhet)
        return '<label for="verksamhetstext">Komplettera med dagens organisation, uppdrag och arbetssätt</label><textarea id="verksamhetstext" name="verksamhetstext" maxlength="12000">'+e(value)+'</textarea><p class="hint">Registrerad verksamhet är ett utkast. Texten stannar lokalt; ange inga kundnamn eller personnummer.</p>'
    if id == 'P-VERK.omsattning':
        return '<p>Nettoomsättning i SEK för '+e(bokslutsperiod(b))+'.</p><label class="check"><input type="checkbox" name="bokslutsperiod" value="ja" '+('checked' if data.get('bokslutsperiod') == 'ja' else '')+'> Jag använder denna period för intagets kund- och tjänstestatistik.</label>'
    return ''


def personalbakgrund(b):
    if not b.bolagsverket or not b.bolagsverket.bokslut or b.bolagsverket.bokslut.medelantal is None:
        return ''
    return '<p>Medelantal anställda i årsredovisningen: '+e(str(b.bolagsverket.bokslut.medelantal))+' under '+e(bokslutsperiod(b))+'. Detta är inte dagens antal personer inklusive ägare; besvara personantalet utifrån dagens verksamhet.</p>'


def bolagsverksbakgrund(b, p=None):
    if not b.bolagsverket:
        return ''
    bv = b.bolagsverket
    html='<section><h2>Bolagsverket och årsredovisning</h2>'
    if bv.namn and bv.namn != b.namn:
        html+='<p>Namnen skiljer sig: SCB '+e(b.namn)+'; Bolagsverket '+e(bv.namn)+'. Kontrollera rätt byrå och aktuellt namn före godkännande.</p>'
    html+='<p>Organisationsform: '+e(bv.organisationsform or 'Saknas')+'</p>'
    if bv.bokslutsnotis:
        html+='<p role="status">'+e(bv.bokslutsnotis)+'</p>'
    if bv.bokslut:
        from riskanalys.intag.register import tillgangliga_forslag
        html+='<p>Årsredovisning: '+e(str(bv.bokslut.omsattning))+' SEK nettoomsättning, '+e(bokslutsperiod(b))+'.</p>'
        if 'P-VERK.omsattning' not in tillgangliga_forslag(b,p):
            html+='<p>Omsättningen kan inte godkännas för intagets nuvarande period eller bedömningsdatum. Använd ett underlag för rätt period.</p>'
        html+=personalbakgrund(b)
        html+='<details><summary>Sparat årsredovisningsunderlag</summary><p>Originalpaketet är sparat privat. SHA256: '+e(bv.bokslut.sha256)+'</p></details>'
    html+='<details><summary>Bolagsverkets registerbakgrund</summary><dl>'
    html+=''.join('<dt>'+e(k)+'</dt><dd>'+e(v)+'</dd>' for k,v in bv.bakgrund)
    return html+'</dl><p>Uppgifterna bekräftar inga utförda kontroller eller risknivåer.</p></details></section>'
