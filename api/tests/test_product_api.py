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

    def test_product_public_access(self):
        product = Product.objects.create(
            name="Camera",
            description="DSLR Camera",
            sku="CAM2025",
            manufacturer="Canon",
            quantity=5,
            owner=self.user
        )
        self.client.logout()  # no authentication
        response = self.client.get(f"/v1/product/{product.id}/")
        assert response.status_code == 200
        assert response.data["name"] == "Camera"
        assert response.data["manufacturer"] == "Canon"

    def test_update_product_non_owner(self):
        product = Product.objects.create(
            name="Speaker",
            description="Bluetooth Speaker",
            sku="SPK100",
            manufacturer="JBL",
            quantity=4,
            owner=self.user,
        )
        other_user = User.objects.create_user(
            email="notowner@example.com",
            password="nopass"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(
            f"/v1/product/{product.id}/", {"quantity": 10}, format="json"
        )
        assert response.status_code == 403
        product.refresh_from_db()
        assert product.quantity == 4

    def test_delete_product_non_owner(self):
        product = Product.objects.create(
            name="Keyboard",
            description="Mechanical Keyboard",
            sku="KEY500",
            manufacturer="Logitech",
            quantity=2,
            owner=self.user,
        )
        other_user = User.objects.create_user(
            email="hacker@example.com",
            password="hackpass"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(f"/v1/product/{product.id}/")
        assert response.status_code == 403
        assert Product.objects.filter(id=product.id).exists()
