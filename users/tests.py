from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User

USERS_URL = '/api/v1/users/'
REGISTER_URL = '/api/v1/auth/register/'
ME_URL = '/api/v1/auth/me/'
TOKEN_URL = '/api/v1/auth/token/'
PASSWORD = 'ClaveDePrueba#2026'
ADMIN_PASSWORD = 'OtraClaveAdmin#2026'
VALID_DATA = {
    'username': 'nuevo',
    'email': 'nuevo@example.com',
    'password': PASSWORD,
}


class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(REGISTER_URL, VALID_DATA, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        user = User.objects.get(username='nuevo')
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_registered_user_can_get_token_with_email(self):
        self.client.post(REGISTER_URL, VALID_DATA, format='json')

        response = self.client.post(TOKEN_URL, {
            'email': VALID_DATA['email'],
            'password': PASSWORD,
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user('otro', 'NUEVO@example.com', PASSWORD)

        response = self.client.post(REGISTER_URL, VALID_DATA, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user('nuevo', 'otro@example.com', PASSWORD)

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


class TokenTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user('ana', 'ana@example.com', PASSWORD)

    def test_login_uses_email_not_username(self):
        response = self.client.post(TOKEN_URL, {
            'username': 'ana',
            'password': PASSWORD,
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_access_token_uses_configured_lifetime(self):
        access = self.client.post(TOKEN_URL, {
            'email': 'ana@example.com',
            'password': PASSWORD,
        }, format='json').data['access']

        token = AccessToken(access)
        lifetime = token['exp'] - token['iat']

        self.assertEqual(
            lifetime, settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
        )


class MeTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            'ana', 'ana@example.com', PASSWORD, telefono='6671234567'
        )

    def test_me_requires_authentication(self):
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 401)

    def test_me_returns_logged_user_with_jwt_and_no_password(self):
        token = self.client.post(TOKEN_URL, {
            'email': 'ana@example.com',
            'password': PASSWORD,
        }, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'ana@example.com')
        self.assertEqual(response.data['telefono'], '6671234567')
        self.assertNotIn('password', response.data)


class UserCrudTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            'admin', 'admin@example.com', ADMIN_PASSWORD
        )
        self.user = User.objects.create_user('ana', 'ana@example.com', PASSWORD)
        self.detail_url = f'{USERS_URL}{self.user.id}/'
        self.client.force_authenticate(self.admin)

    def assert_password_unchanged(self):
        previous_hash = self.user.password
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, previous_hash)
        self.assertTrue(self.user.check_password(PASSWORD))
        self.assertFalse(self.user.check_password(ADMIN_PASSWORD))

    def test_crud_requires_admin(self):
        self.client.force_authenticate(self.user)

        response = self.client.get(USERS_URL)

        self.assertEqual(response.status_code, 403)

    def test_list_and_detail_do_not_expose_password(self):
        list_response = self.client.get(USERS_URL)
        detail_response = self.client.get(self.detail_url)

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        for user in list_response.data:
            self.assertNotIn('password', user)
        self.assertNotIn('password', detail_response.data)

    def test_create_hashes_password_and_does_not_return_it(self):
        response = self.client.post(USERS_URL, {
            **VALID_DATA, 'telefono': '6671234567',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertEqual(response.data['telefono'], '6671234567')
        user = User.objects.get(email=VALID_DATA['email'])
        self.assertTrue(user.check_password(PASSWORD))

    def test_create_requires_password(self):
        data = {key: value for key, value in VALID_DATA.items() if key != 'password'}

        response = self.client.post(USERS_URL, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_patch_without_password_keeps_user_password(self):
        response = self.client.patch(
            self.detail_url, {'telefono': '6671234567'}, format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['telefono'], '6671234567')
        self.assertNotIn('password', response.data)
        self.assert_password_unchanged()

    def test_put_without_password_keeps_user_password(self):
        response = self.client.put(self.detail_url, {
            'username': 'ana',
            'email': 'ana@example.com',
            'first_name': 'Ana',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.data)
        self.assert_password_unchanged()

    def test_patch_with_password_changes_it_hashed(self):
        new_password = 'NuevaClave#2026'

        response = self.client.patch(
            self.detail_url, {'password': new_password}, format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.data)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, new_password)
        self.assertTrue(self.user.check_password(new_password))

    def test_put_with_password_changes_it_hashed(self):
        new_password = 'NuevaClave#2026'

        response = self.client.put(self.detail_url, {
            'username': 'ana',
            'email': 'ana@example.com',
            'password': new_password,
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, new_password)
        self.assertTrue(self.user.check_password(new_password))

    def test_blank_password_is_rejected(self):
        response = self.client.patch(self.detail_url, {'password': ''}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assert_password_unchanged()

    def test_invalid_phone_is_rejected(self):
        response = self.client.patch(
            self.detail_url, {'telefono': 'abc'}, format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('telefono', response.data)


class AdminTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            'admin', 'admin@example.com', ADMIN_PASSWORD
        )
        self.client.force_login(self.admin)

    def test_change_form_shows_telefono(self):
        response = self.client.get(f'/admin/users/user/{self.admin.id}/change/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="telefono"')

    def test_add_form_hashes_password(self):
        response = self.client.post('/admin/users/user/add/', {
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'telefono': '6671234567',
            'usable_password': 'true',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='nuevo')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(user.telefono, '6671234567')


class SwaggerTestCase(TestCase):
    def setUp(self):
        self.schema = self.client.get('/swagger/?format=openapi').json()

    def test_title_uses_project_name(self):
        self.assertEqual(self.schema['info']['title'], 'Tienda Online API')

    def test_telefono_is_documented(self):
        self.assertIn('telefono', self.schema['definitions']['User']['properties'])

    def test_no_response_documents_password(self):
        for path, operations in self.schema['paths'].items():
            for method, operation in operations.items():
                if method == 'parameters':
                    continue
                for status_code, response in operation['responses'].items():
                    schema = response.get('schema', {})
                    reference = schema.get('$ref') or schema.get('items', {}).get('$ref')
                    if reference:
                        definition = self.schema['definitions'][reference.split('/')[-1]]
                        self.assertNotIn(
                            'password', definition['properties'],
                            f'{method} {path} {status_code}',
                        )
