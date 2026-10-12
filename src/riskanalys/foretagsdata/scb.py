"""SCB AFR v1. Kontrakt: officiell OpenAPI och variabelbeskrivning, 2026-10-10."""
from datetime import datetime, timezone
from http.client import HTTPException
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener
from pydantic import ValidationError
from riskanalys.fel import RiskanalysFel
from riskanalys.foretagsdata.modeller import Registerbild

MAX_BYTES = 131072
LAN = dict(zip(['01','03','04','05','06','07','08','09','10','12','13','14','17','18','19','20','21','22','23','24','25'],
               ['Stockholm','Uppsala','Södermanland','Östergötland','Jönköping','Kronoberg','Kalmar','Gotland','Blekinge','Skåne','Halland','Västra Götaland','Värmland','Örebro','Västmanland','Dalarna','Gävleborg','Västernorrland','Jämtland','Västerbotten','Norrbotten']))


def organisationsnummer(text: str) -> str:
    """Juridiska personer: 10 siffror eller SCB:s 16-prefix, aldrig personnummer."""
    if not isinstance(text, str):
        raise RiskanalysFel('Ange ett juridiskt organisationsnummer med tio siffror.')
    n = text.strip()
    if re.fullmatch(r'[0-9]{6}-[0-9]{4}', n):
        n = n.replace('-', '')
    elif re.fullmatch(r'16[0-9]{10}', n):
        n = n[2:]
    if not re.fullmatch(r'[0-9]{10}', n) or int(n[2]) < 2:
        raise RiskanalysFel('Ange juridisk persons organisationsnummer med tio siffror. Enskild firma kan fortsätta intaget manuellt; ange inget personnummer här.')
    tal = [int(c) * (2 if i % 2 == 0 else 1) for i,c in enumerate(n)]
    if sum(t // 10 + t % 10 for t in tal) % 10:
        raise RiskanalysFel('Organisationsnumrets kontrollsiffra stämmer inte. Kontrollera numret.')
    return n


def _kod(data, key, langd=2):
    value = data.get(key)
    if value is None or value == '':
        return None
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,'+str(langd)+'}', value):
        raise ValueError(key)
    return value


def tolka_scb(data: dict, orgnr: str, ursprung: str) -> Registerbild:
    """Validera vald identitet och projicera endast den avsedda bakgrunden."""
    n = organisationsnummer(orgnr)
    try:
        if not isinstance(data, dict) or data.get('orgNr') != n or data.get('peOrgNr') != '16'+n:
            raise ValueError('identitet')
        namn = data.get('namn')
        if not isinstance(namn, str) or not namn.strip() or any(ord(c)<32 or 0xD800<=ord(c)<=0xDFFF or ord(c) in (0xFFFE,0xFFFF) for c in namn):
            raise ValueError('namn')
        lankod = _kod(data,'lanSate')
        if lankod is not None and lankod not in LAN:
            raise ValueError('län')
        grenar = data.get('naringsgrenar') or []
        if not isinstance(grenar,list) or len(grenar)>5:
            raise ValueError('SNI')
        sni = []
        for g in grenar:
            if not isinstance(g,dict) or not isinstance(g.get('naringsgren'),str) or not re.fullmatch(r'[0-9]{5}',g['naringsgren']):
                raise ValueError('SNI')
            sni.append(g['naringsgren'])
        ar = data.get('omsAr')
        return Registerbild(schema_version=3,orgnr=n,namn=namn.strip(),lan=LAN.get(lankod),
                            arbetsstallen=data.get('aeAnt'),anstalldaklass=_kod(data,'anstKl'),
                            omsattningsklass=_kod(data,'omsKl'),omsattningsar=None if ar==0 else ar,
                            juridisk_form=_kod(data,'jurform'),foretagsstatus=_kod(data,'ftgStat'),
                            sni=tuple(sni),ursprung=ursprung,hamtad=datetime.now(timezone.utc),
                            fskatt_status=_kod(data,'fSkattStat',1),moms_status=_kod(data,'momsStat',1),
                            arbetsgivar_status=_kod(data,'arbGivStat',1),agarkontroll=_kod(data,'agKat'))
    except (ValueError, TypeError, ValidationError) as exc:
        raise RiskanalysFel('Registersvaret har saknad/felaktig identitet eller oväntade uppgifter. Kontrollera numret och SCB-formatet; tidigare svar har inte ändrats.') from exc


class _IngaOmdirigeringar(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _transport(req, timeout):
    return build_opener(_IngaOmdirigeringar()).open(req, timeout=timeout)


class SCBLeverantor:
    def __init__(self, nyckel=None, transport=None):
        self._nyckel = nyckel if nyckel is not None else os.environ.get('RISKANALYS_SCB_API_KEY','')
        self._transport = transport or _transport

    def hamta(self, orgnr: str) -> Registerbild:
        n = organisationsnummer(orgnr)
        if not self._nyckel.strip():
            raise RiskanalysFel('Registrera dig kostnadsfritt hos SCB och lägg din personliga nyckel lokalt i RISKANALYS_SCB_API_KEY. Du kan också importera SCB-JSON eller fortsätta intaget manuellt.')
        if len(self._nyckel)>4096 or '\n' in self._nyckel or '\r' in self._nyckel:
            raise RiskanalysFel('SCB-nyckelns format är ogiltigt. Rätta den lokala konfigurationen.')
        req = Request(f'https://apiafr.scb.se/v1/juridiskaenheter/16{n}/full',headers={'X-API-Key':self._nyckel,'Accept':'application/json'})
        try:
            with self._transport(req,timeout=15) as svar:
                raw = svar.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES:
                raise RiskanalysFel('SCB-svaret är för stort. Inga profiluppgifter har ändrats.')
            return tolka_scb(json.loads(raw),n,'scb_api')
        except HTTPError as exc:
            texter = {401:'SCB nekade nyckeln. Kontrollera din lokala API-nyckel.',403:'SCB nekade åtkomst. Kontrollera din behörighet hos SCB.',
                      404:'SCB hittade inte företaget. Kontrollera organisationsnumret.',429:'SCB begränsar antalet anrop. Vänta innan du försöker igen.'}
            raise RiskanalysFel(texter.get(exc.code,'SCB kunde inte lämna uppgifter. Försök senare eller fortsätt manuellt.')) from None
        except (URLError, OSError, TimeoutError, HTTPException):
            raise RiskanalysFel('SCB kunde inte nås. Kontrollera internetanslutningen eller försök senare.') from None
        except (ValueError, UnicodeError, RecursionError):
            raise RiskanalysFel('SCB lämnade inte ett läsbart JSON-svar. Försök senare.') from None
