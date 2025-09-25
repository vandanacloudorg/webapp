import pytest
from rest_framework.test import APIClient
from api.models import User

@pytest.mark.django_db
class TestUserAPI:

    def setup_method(self):
        self.client = APIClient()

    def test_create_user_success(self):
        data = {
            "email": "new@example.com",
            "password": "test123",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post("/v1/user/", data, format="json")
        assert response.status_code == 201
        user = User.objects.get(email="new@example.com")
        assert user.check_password("test123")  # password hashed

    def test_create_user_duplicate_email(self):
        User.objects.create_user(
            email="dup@example.com",
            password="abc123",
            first_name="Dup",
            last_name="User"
        )
        data = {
            "email": "dup@example.com",
            "password": "newpass",
            "first_name": "Dup",
            "last_name": "User"
        }
        response = self.client.post("/v1/user/", data, format="json")
        assert response.status_code == 400
        assert "already exists" in response.data.get("email", [])[0]

    def test_get_user_requires_auth(self):
        response = self.client.get("/v1/user/self/")
        assert response.status_code == 401

    def test_get_user_authenticated(self):
        user = User.objects.create_user(
            email="auth@example.com",
            password="auth123",
            first_name="Auth",
            last_name="User"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/v1/user/self/")
        assert response.status_code == 200
        assert response.data["email"] == "auth@example.com"

    def test_update_user_fields(self):
        user = User.objects.create_user(
            email="update@example.com",
            password="oldpass",
            first_name="Old",
            last_name="Name"
        )
        self.client.force_authenticate(user=user)
        data = {"first_name": "New", "password": "newpass"}
        response = self.client.patch("/v1/user/self/", data, format="json")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "New"
        assert user.check_password("newpass")

    def test_user_cannot_update_email(self):
        user = User.objects.create_user(
            email="emailchange@example.com",
            password="testpass",
            first_name="Email",
            last_name="Change"
        )
        self.client.force_authenticate(user=user)
        data = {"email": "hacker@example.com"}
        response = self.client.patch("/v1/user/self/", data, format="json")
        assert response.status_code == 400
        assert "You can only update" in response.data["error"]

    def test_user_password_not_exposed(self):
        user = User.objects.create_user(
            email="hidden@example.com",
            password="hiddenpass",
            first_name="Hidden",
            last_name="User"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/v1/user/self/")
        assert "password" not in response.data

    def test_put_requires_email_field(self):
        user = User.objects.create_user(
            email="puttest@example.com",
            password="putpass",
            first_name="Put",
            last_name="User"
        )
        self.client.force_authenticate(user=user)
        data = {"first_name": "NoEmail"}
        response = self.client.put("/v1/user/self/", data, format="json")
        assert response.status_code == 400
        assert "email" in response.data

    def test_user_can_update_all_allowed_fields(self):
        user = User.objects.create_user(
            email="allowed@example.com",
            password="oldpass",
            first_name="First",
            last_name="Last"
        )
        self.client.force_authenticate(user=user)
        data = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "password": "newallowedpass"
        }
        response = self.client.patch("/v1/user/self/", data, format="json")
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "UpdatedFirst"
        assert user.last_name == "UpdatedLast"
        assert user.check_password("newallowedpass")
