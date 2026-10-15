"""Lokal projektion av HVD v1. Okända fält och råa feltexter lämnas utanför."""
from riskanalys.fel import RiskanalysFel

KOD = {'kod': str, 'klartext': str}
NAMN = {'namn': str, 'organisationsnamntyp': KOD, 'registreringsdatum': (str, int)}
FALT = {
    'organisationsnamn': {'organisationsnamnLista': [NAMN]},
    'organisationsform': KOD,
    'juridiskForm': KOD,
    'verksamOrganisation': {'kod': str},
    'verksamhetsbeskrivning': {'beskrivning': str},
    'organisationsdatum': {'registreringsdatum': (str, int), 'infortHosScb': (str, int)},
    'avregistreradOrganisation': {'avregistreringsdatum': (str, int)},
    'avregistreringsorsak': KOD,
    'pagaendeAvvecklingsEllerOmstruktureringsforfarande': {
        'pagaendeAvvecklingsEllerOmstruktureringsforfarandeLista': [{**KOD, 'fromDatum': (str, int)}]},
    'naringsgrenOrganisation': {'sni': [KOD]},
    'postadressOrganisation': {'postadress': {k: str for k in
        ('utdelningsadress', 'postnummer', 'land', 'coAdress', 'postort')}},
}
DOKUMENT = {'dokumentId': str, 'filformat': str, 'rapporteringsperiodTom': (str, int),
            'registreringstidpunkt': (str, int)}


def _projicera(varde, schema):
    if isinstance(schema, dict):
        if not isinstance(varde, dict):
            raise ValueError('objekt')
        return {k: _projicera(varde[k], typ) for k, typ in schema.items()
                if k in varde and varde[k] is not None}
    if isinstance(schema, list):
        if not isinstance(varde, list) or len(varde) > 1000:
            raise ValueError('lista')
        return [_projicera(v, schema[0]) for v in varde]
    typer = schema if isinstance(schema, tuple) else (schema,)
    if type(varde) not in typer:
        raise ValueError('värde')
    return varde


def tolka_organisationer(data, orgnr: str) -> list[dict]:
    try:
        rader = data['organisationer']
        if not isinstance(rader, list) or not rader or len(rader) > 100:
            raise ValueError('organisationer')
        resultat = []
        for rad in rader:
            if rad['organisationsidentitet']['identitetsbeteckning'] != orgnr:
                raise ValueError('identitet')
            post = {}
            for namn, schema in FALT.items():
                falt = rad.get(namn)
                if falt is None:
                    post[namn] = {'status': 'saknas_i_svaret'}
                elif not isinstance(falt, dict):
                    raise ValueError('fält')
                elif falt.get('fel') is not None:
                    post[namn] = {'status': 'uppgiftsfel'}
                else:
                    post[namn] = _projicera(falt, schema)
                    if falt.get('dataproducent') in ('SCB', 'Bolagsverket'):
                        post[namn]['dataproducent'] = falt['dataproducent']
            if 'sni' in post.get('naringsgrenOrganisation', {}):
                post['naringsgrenOrganisation']['sni'] = [
                    rad for rad in post['naringsgrenOrganisation']['sni'] if rad.get('kod', '').strip()]
            resultat.append(post)
        return resultat
    except (KeyError, TypeError, ValueError):
        raise RiskanalysFel('Bolagsverket gav ingen entydig registerbild för valt organisationsnummer. Kontrollera numret och svarskontraktet.') from None


def tolka_dokument(data) -> list[dict]:
    try:
        dokument = _projicera(data['dokument'], [DOKUMENT])
        if any(not d.get('dokumentId', '').strip() for d in dokument):
            raise ValueError('dokumentidentitet')
        return dokument
    except (KeyError, TypeError, ValueError):
        raise RiskanalysFel('Bolagsverket gav en oläsbar dokumentlista. Saknade uppgifter får inte tolkas som att årsredovisningar saknas.') from None
