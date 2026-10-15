"""Bolagsverket HVD v1: lokalt uppslag, OAuth-token endast i minnet.

Kontrakt och anslutningsanvisning 1.01 verifierade i myndighetens portal
2026-10-14. Se research 10, avsnitt 14.5. Ingen profil eller AI används.
"""
from datetime import datetime, timezone
from http.client import HTTPException
import json
import math
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.scb import organisationsnummer
from riskanalys.foretagsdata.bolagsverket_svar import tolka_dokument, tolka_organisationer

TOKEN_URL = 'https://portal.api.bolagsverket.se/oauth2/token'
API_URL = 'https://gw.api.bolagsverket.se/vardefulla-datamangder/v1'
MAX_BYTES = 1048576


class IngaOmdirigeringar(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def transport(req, timeout):
    return build_opener(IngaOmdirigeringar()).open(req, timeout=timeout)


def _httpfel(kod: int) -> RiskanalysFel:
    text = {
        400: 'Bolagsverket avvisade begäran. Kontrollera anslutningsuppgifter och API-kontrakt.',
        401: 'Bolagsverket nekade autentiseringen. Kontrollera client_id och client_secret i den lokala nyckelfilen.',
        403: 'Bolagsverket nekade åtkomst. Kontrollera behörigheten för Värdefulla datamängder.',
        404: 'Bolagsverket hittade inte den begärda resursen.',
        429: 'Bolagsverket begränsar antalet anrop. Vänta innan du försöker igen.',
    }.get(kod, 'Bolagsverket kunde inte lämna uppgifter. Försök senare.')
    return RiskanalysFel(text)


class BolagsverketLeverantor:
    def __init__(self, client_id=None, client_secret=None, *, transport=None, klocka=None):
        self._client_id = client_id if client_id is not None else os.environ.get('BOLAGSVERKET_CLIENT_ID', '')
        self._client_secret = client_secret if client_secret is not None else os.environ.get('BOLAGSVERKET_CLIENT_SECRET', '')
        self._transport = transport or globals()['transport']
        self._klocka = klocka or time.monotonic
        self._token = ''
        self._giltig_till = 0.0

    def _json(self, req):
        try:
            with self._transport(req, timeout=20) as svar:
                raw = svar.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise RiskanalysFel('Bolagsverkets svar är för stort. Inga profiluppgifter har ändrats.')
            return json.loads(raw)
        except HTTPError:
            raise
        except (URLError, OSError, HTTPException):
            raise RiskanalysFel('Bolagsverket kunde inte nås. Kontrollera anslutningen eller försök senare.') from None
        except (ValueError, UnicodeError, RecursionError):
            raise RiskanalysFel('Bolagsverket gav ett oläsbart JSON-svar.') from None

    def _hamta_token(self):
        if self._token and self._klocka() < self._giltig_till:
            return self._token
        for value in (self._client_id, self._client_secret):
            if not isinstance(value, str) or not value.strip() or len(value) > 4096 or any(ord(c) < 32 for c in value):
                raise RiskanalysFel('Bolagsverket kräver BOLAGSVERKET_CLIENT_ID och BOLAGSVERKET_CLIENT_SECRET i den lokala nyckelfilen. Kontrollera värdena.')
        body = urlencode({'grant_type': 'client_credentials', 'client_id': self._client_id,
                          'client_secret': self._client_secret, 'scope': 'vardefulla-datamangder:read'}).encode()
        start = self._klocka()
        svar = self._json(Request(TOKEN_URL, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}))
        try:
            token, giltighet = svar['access_token'], svar['expires_in']
            if (not isinstance(token, str) or not token or len(token) > 16384
                    or any(ord(c) <= 32 or ord(c) >= 127 for c in token)
                    or svar['token_type'].lower() != 'bearer'
                    or type(giltighet) not in (int, float) or not math.isfinite(giltighet) or giltighet <= 0):
                raise ValueError('token')
        except (KeyError, TypeError, ValueError, AttributeError):
            raise RiskanalysFel('Bolagsverket gav en ogiltig token eller giltighetstid.') from None
        self._token = token
        self._giltig_till = start + max(0, giltighet - 30)
        return token

    def _data(self, path: str, orgnr: str):
        # En nekad cache-token kan förnyas en gång. Inga övriga automatiska omförsök.
        for forsok in range(2):
            token = self._hamta_token()
            req = Request(API_URL + path, data=json.dumps({'identitetsbeteckning': orgnr}).encode(),
                          headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'application/json'})
            try:
                return self._json(req)
            except HTTPError as exc:
                if exc.code != 401 or forsok:
                    raise
                self._token = ''

    def hamta(self, orgnr: str) -> dict:
        """Hämtar aktuell registerbild och dokumentmetadata. Sparar inga filer."""
        n = organisationsnummer(orgnr)
        try:
            organisationer = tolka_organisationer(self._data('/organisationer', n), n)
            dokument = tolka_dokument(self._data('/dokumentlista', n))
        except HTTPError as exc:
            raise _httpfel(exc.code) from None
        return {'orgnr': n, 'hamtad': datetime.now(timezone.utc).isoformat(), 'kalla': API_URL,
                'organisationer': organisationer, 'dokument': dokument}


    def hamta_dokument(self, dokument_id: str) -> bytes:
        """GET av ett dokument-id från listan; begränsad ZIP-respons."""
        from riskanalys.foretagsdata.arsredovisning import MAX_ZIP
        if not isinstance(dokument_id, str) or not dokument_id.strip() or len(dokument_id) > 500:
            raise RiskanalysFel('Dokumentets identitet är ogiltig. Hämta dokumentlistan igen.')
        try:
            for forsok in range(2):
                req = Request(API_URL + '/dokument/' + quote(dokument_id, safe=''),
                              headers={'Authorization': 'Bearer ' + self._hamta_token(), 'Accept': 'application/zip'})
                try:
                    with self._transport(req, timeout=20) as svar:
                        raw = svar.read(MAX_ZIP + 1)
                    if len(raw) > MAX_ZIP:
                        raise RiskanalysFel('Årsredovisningspaketet är för stort. Använd manuellt underlag.')
                    return raw
                except HTTPError as exc:
                    if exc.code != 401 or forsok:
                        raise
                    self._token = ''
        except HTTPError as exc:
            raise _httpfel(exc.code) from None
        except (URLError, OSError, HTTPException):
            raise RiskanalysFel('Bolagsverkets dokument kunde inte hämtas. Försök senare.') from None
