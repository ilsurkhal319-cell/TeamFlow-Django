from django.test import TestCase
from django.urls import reverse
from users.models import CustomUser


class RegisterViewTests(TestCase):
    def test_user_can_register(self):
        response = self.client.post(reverse("users:register"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPassword123",
            "password2": "StrongPassword123",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())

class LoginViewTests(TestCase):
    def test_user_can_login(self):
        CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPassword123"
        )

        response = self.client.post(reverse("users:login"), {
            "username": "testuser",
            "password": "StrongPassword123",
        })

        self.assertEqual(response.status_code, 302)