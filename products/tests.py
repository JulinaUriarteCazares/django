from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Product


class CategoryTestCase(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			username='test-user',
			password='test-password',
		)
		self.client.force_authenticate(user=self.user)
		self.category = Category.objects.create(name='Electronica')

	# PRUEBA 1: Verifica que se pueda crear una categoria mediante POST.
	def test_create_category(self):
		response = self.client.post('/api/categories/', {'name': 'Ropa'})

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Category.objects.count(), 2)
		self.assertTrue(Category.objects.filter(name='Ropa').exists())

	# PRUEBA 2: Verifica que se puedan listar las categorias existentes.
	def test_list_categories(self):
		response = self.client.get('/api/categories/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], 'Electronica')


class ProductTestCase(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			username='test-user',
			password='test-password',
		)
		self.client.force_authenticate(user=self.user)
		self.category = Category.objects.create(name='Electronica')
		self.product = Product.objects.create(
			name='Laptop',
			category=self.category,
			description='Laptop HP',
			price=15000.00,
		)

	# PRUEBA 3: Verifica que se pueda crear un producto mediante POST.
	def test_create_product(self):
		response = self.client.post('/api/products/', {
			'name': 'Mouse',
			'description': 'Mouse inalambrico',
			'price': 500.00,
		})

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Product.objects.count(), 2)
		self.assertTrue(Product.objects.filter(name='Mouse').exists())

	# PRUEBA 4: Verifica que se puedan listar los productos existentes.
	def test_list_products(self):
		response = self.client.get('/api/products/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], 'Laptop')

	# PRUEBA 5: Verifica que se pueda actualizar un producto mediante PUT.
	def test_update_product(self):
		response = self.client.put(
			f'/api/products/{self.product.id}/',
			{
				'name': 'Laptop Pro',
				'description': 'Laptop HP actualizada',
				'price': 18000.00,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.product.refresh_from_db()
		self.assertEqual(self.product.name, 'Laptop Pro')
		self.assertEqual(self.product.price, 18000.00)

	# PRUEBA 6: Verifica que se pueda eliminar un producto mediante DELETE.
	def test_delete_product(self):
		response = self.client.delete(
			f'/api/products/{self.product.id}/',
		)

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Product.objects.filter(id=self.product.id).exists())

	def test_precio_final_autenticado(self):
		ropa = Category.objects.create(name='Ropa')
		producto_ropa = Product.objects.create(
			name='Sudadera',
			category=ropa,
			description='Sudadera de algodon',
			price=1000.00,
		)
		response_electronica = self.client.get(
			f'/api/products/{self.product.id}/precio-final/'
		)
		response_ropa = self.client.get(
			f'/api/products/{producto_ropa.id}/precio-final/'
		)

		self.assertEqual(response_electronica.status_code, 200)
		self.assertEqual(response_ropa.status_code, 200)
		self.assertEqual(response_electronica.data['precio_final'], 13500.0)
		self.assertEqual(response_ropa.data['precio_final'], 800.0)

	def test_precio_final_sin_autenticar(self):
		self.client.force_authenticate(user=None)
		response = self.client.get(
			f'/api/products/{self.product.id}/precio-final/'
		)

		self.assertEqual(response.status_code, 401)
