from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

def get_test_image():
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")

class ProductAPITests(APITestCase):
    def setUp(self):
        # Create a sample product with a real image
        self.product = Product.objects.create(
            name="Test Product",
            price=10.99,
            description="A test product description",
            image=get_test_image()
        )
        self.list_url = '/products/'
        self.detail_url = f'/products/{self.product.id}/'

    def test_get_product_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF might return more if other tests ran, but in a clean test db it should be 1
        self.assertTrue(len(response.data) >= 1)

    def test_get_product_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_create_product(self):
        data = {
            "name": "New Product",
            "price": "20.50",
            "description": "New product description",
            "image": get_test_image()
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="New Product").exists())

    def test_update_product(self):
        data = {"name": "Updated Product Name", "price": "15.00", "description": "Updated"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product Name")

    def test_delete_product(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
