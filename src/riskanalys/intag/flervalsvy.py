"""Flervalsfält i webbintaget: en kryssruta per alternativ, tillbaka som kommaseparerad svarstext."""
from html import escape as e
from riskanalys.fel import RiskanalysFel

PREFIX = 'flerval:'
KRYSSAT = 'ja'


def formularval(data) -> frozenset[str]:
    """Alternativen som kryssats i ett inskickat formulär."""
    return frozenset(k.removeprefix(PREFIX) for k in data if k.startswith(PREFIX))


def formulartext(falt, data) -> str:
    """Kryssrutorna som svarstext; ett okänt alternativ eller värde avvisas i stället för att ignoreras."""
    valda = formularval(data)
    if valda - set(falt.val) or any(v != KRYSSAT for k, v in data.items() if k.startswith(PREFIX)):
        raise RiskanalysFel('Välj bara alternativ ur listan. Läs om sidan och försök igen.')
    return ','.join(sorted(valda))


def flervalsgrans(rb) -> int:
    """Det största antalet kryssrutor som ett formulär kan skicka."""
    return max((len(f.val) for f in rb.falt.values() if f.typ == 'flerval'), default=0)


def sparade_val(varde) -> frozenset[str]:
    return frozenset(varde) if isinstance(varde, (tuple, list)) else frozenset()


def flervalsrutor(rb, falt, valda) -> str:
    def text(v):
        return f'{v} – {rb.hot[v].namn}' if v in rb.hot else v.replace('_', ' ')
    rutor = ''.join(
        f'<label class="check" for="{e(PREFIX + v, quote=True)}"><input id="{e(PREFIX + v, quote=True)}" '
        f'name="{e(PREFIX + v, quote=True)}" type="checkbox" value="{KRYSSAT}"{" checked" if v in valda else ""}>'
        f'{e(text(v))}</label>'
        for v in falt.val)
    return ('<fieldset><legend>Ditt svar – kryssa i alla som stämmer. '
            'Lämna alla tomma om inget av alternativen gäller.</legend>' + rutor + '</fieldset>')
