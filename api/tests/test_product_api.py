import pytest
from rest_framework.test import APIClient
from api.models import User, Product


@pytest.mark.django_db
class TestProductAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="prod@example.com",
            password="prodpass",
            first_name="Prod",
            last_name="Owner"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_product_success(self):
        data = {
            "name": "Laptop",
            "description": "MacBook Pro",
            "sku": "MBP123",
            "manufacturer": "Apple",
            "quantity": 3
        }
        response = self.client.post("/v1/product/", data, format="json")
        assert response.status_code == 201
        product = Product.objects.get(sku="MBP123")
        assert product.owner == self.user

    def test_create_product_invalid_quantity(self):
        data = {
            "name": "Phone",
            "description": "iPhone",
            "sku": "IPH999",
            "manufacturer": "Apple",
            "quantity": -1  # invalid
        }
        response = self.client.post("/v1/product/", data, format="json")
        assert response.status_code == 400

    def test_update_product_owner_only(self):
        product = Product.objects.create(
            name="Tablet",
            description="iPad",
            sku="IPAD123",
            manufacturer="Apple",
            quantity=2,
            owner=self.user,
        )
        # another user
        other_user = User.objects.create_user(
            email="other@example.com",
            password="otherpass",
            first_name="Other",
            last_name="User"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(f"/v1/product/{product.id}/", {"quantity": 5}, format="json")
        assert response.status_code == 403

    def test_delete_product_owner_only(self):
        product = Product.objects.create(
            name="Headphones",
            description="Sony WH-1000XM5",
            sku="SONY1000",
            manufacturer="Sony",
            quantity=1,
            owner=self.user,
        )
        response = self.client.delete(f"/v1/product/{product.id}/")
        assert response.status_code == 204
        assert not Product.objects.filter(id=product.id).exists()
