from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from requests.exceptions import ConnectTimeout
from rest_framework.test import APIClient
from zeep.exceptions import Fault

MEXICO = {
    'sISOCode': 'MX',
    'sName': 'Mexico',
    'sCapitalCity': 'Mexico City',
    'sPhoneCode': '52',
    'sContinentCode': 'AM',
    'sCurrencyISOCode': 'MXN',
    'sCountryFlag': 'http://example.com/Mexico.jpg',
    'Languages': {'tLanguage': [{'sISOCode': 'es', 'sName': 'Spanish'}]},
}
NOT_FOUND = {
    'sISOCode': None,
    'sName': 'Country not found in the database',
    'sCapitalCity': None,
    'sPhoneCode': None,
    'sContinentCode': None,
    'sCurrencyISOCode': None,
    'sCountryFlag': None,
    'Languages': None,
}


@patch('countries.services.get_client')
class PaisSoapTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(User.objects.create_user('ana', password='x'))

    def test_returns_country_and_sends_iso_in_uppercase(self, get_client):
        operation = get_client.return_value.service.FullCountryInfo
        operation.return_value = MEXICO

        response = self.client.get('/api/soap/countries/mx/')

        self.assertEqual(response.status_code, 200)
        operation.assert_called_once_with(sCountryISOCode='MX')
        self.assertEqual(response.data['pais']['capital'], 'Mexico City')
        self.assertEqual(response.data['pais']['idiomas'], ['Spanish'])

    def test_country_without_languages(self, get_client):
        get_client.return_value.service.FullCountryInfo.return_value = {
            **MEXICO,
            'Languages': None,
        }

        response = self.client.get('/api/soap/countries/MX/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['pais']['idiomas'], [])

    def test_unknown_country_returns_404(self, get_client):
        get_client.return_value.service.FullCountryInfo.return_value = NOT_FOUND

        response = self.client.get('/api/soap/countries/ZZ/')

        self.assertEqual(response.status_code, 404)

    def test_soap_fault_returns_502(self, get_client):
        get_client.return_value.service.FullCountryInfo.side_effect = Fault('fallo')

        response = self.client.get('/api/soap/countries/MX/')

        self.assertEqual(response.status_code, 502)

    def test_network_error_returns_502(self, get_client):
        get_client.side_effect = ConnectTimeout('sin red')

        response = self.client.get('/api/soap/countries/MX/')

        self.assertEqual(response.status_code, 502)

    def test_requires_authentication(self, get_client):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/soap/countries/MX/')

        self.assertEqual(response.status_code, 401)
        get_client.assert_not_called()
