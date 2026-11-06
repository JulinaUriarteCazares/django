from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

REGISTER_URL = '/api/auth/register/'
ME_URL = '/api/auth/me/'
TOKEN_URL = '/api/token/'
VALID_DATA = {
    'username': 'nuevo',
    'email': 'nuevo@example.com',
    'password': 'ClaveDePrueba#2026',
}


class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(REGISTER_URL, VALID_DATA, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='nuevo')
        self.assertNotEqual(user.password, VALID_DATA['password'])
        self.assertTrue(user.check_password(VALID_DATA['password']))

    def test_registered_user_can_get_token(self):
        self.client.post(REGISTER_URL, VALID_DATA, format='json')

        response = self.client.post(TOKEN_URL, {
            'username': VALID_DATA['username'],
            'password': VALID_DATA['password'],
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user('otro', 'NUEVO@example.com', 'ClaveDePrueba#2026')

        response = self.client.post(REGISTER_URL, VALID_DATA, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user('nuevo', 'otro@example.com', 'ClaveDePrueba#2026')

        response = self.client.post(REGISTER_URL, VALID_DATA, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            REGISTER_URL, {**VALID_DATA, 'password': '12345678'}, format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(username='nuevo').exists())

    def test_register_ignores_privilege_fields(self):
        self.client.post(
            REGISTER_URL,
            {**VALID_DATA, 'is_staff': True, 'is_superuser': True},
            format='json',
        )

        user = User.objects.get(username='nuevo')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class MeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('ana', 'ana@example.com', 'ClaveDePrueba#2026')

    def test_me_requires_authentication(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)

    def test_me_returns_logged_user_with_jwt(self):
        token = self.client.post(TOKEN_URL, {
            'username': 'ana',
            'password': 'ClaveDePrueba#2026',
        }, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'ana')
        self.assertNotIn('password', response.data)
