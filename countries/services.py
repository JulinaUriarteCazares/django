from functools import lru_cache

from requests.exceptions import RequestException
from zeep import Client
from zeep.exceptions import Error as ZeepError
from zeep.helpers import serialize_object
from zeep.transports import Transport

WSDL_URL = 'http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL'
TIMEOUT_SECONDS = 10


class SoapServiceError(Exception):
    """El servicio SOAP no respondió o devolvió una respuesta inválida."""


@lru_cache(maxsize=1)
def get_client():
    # El WSDL se descarga una sola vez; los fallos no se guardan en caché.
    transport = Transport(timeout=TIMEOUT_SECONDS, operation_timeout=TIMEOUT_SECONDS)
    return Client(WSDL_URL, transport=transport)


def obtener_pais(iso_code):
    """Consulta la operación SOAP FullCountryInfo. Devuelve None si el país no existe."""
    try:
        # El servicio solo reconoce el código ISO en mayúsculas.
        respuesta = get_client().service.FullCountryInfo(sCountryISOCode=iso_code.upper())
    except (ZeepError, RequestException) as exc:
        raise SoapServiceError(str(exc)) from exc

    pais = serialize_object(respuesta, dict)

    # Un país inexistente no es un Fault: llega con sISOCode vacío.
    if not pais['sISOCode']:
        return None

    idiomas = (pais['Languages'] or {}).get('tLanguage') or []
    return {
        'codigo_iso': pais['sISOCode'],
        'nombre': pais['sName'],
        'capital': pais['sCapitalCity'],
        'codigo_telefonico': pais['sPhoneCode'],
        'continente': pais['sContinentCode'],
        'moneda': pais['sCurrencyISOCode'],
        'bandera': pais['sCountryFlag'],
        'idiomas': [idioma['sName'] for idioma in idiomas],
    }
