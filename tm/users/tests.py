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
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_user_returns_to_requested_page_after_login(self):
        CustomUser.objects.create_user(
            username="profileuser",
            email="profileuser@example.com",
            password="StrongPassword123"
        )

        response = self.client.post(reverse("users:login"), {
            "username": "profileuser",
            "password": "StrongPassword123",
            "next": reverse("flow:profile"),
        })

        self.assertRedirects(response, reverse("flow:profile"))

    def test_user_can_logout(self):
        user = CustomUser.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password="StrongPassword123",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("users:logout"))

        self.assertRedirects(response, reverse("users:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
