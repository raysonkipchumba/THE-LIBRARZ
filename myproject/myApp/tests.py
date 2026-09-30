from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_has_forgot_password_link(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, reverse('password_reset'))


class ChatFeatureTests(TestCase):
    def test_user_profile_is_online_when_recently_active(self):
        user = User.objects.create_user(username='alice', email='alice@example.com', password='pass123')
        profile = UserProfile.objects.create(user=user, last_seen=timezone.now() - timedelta(minutes=2))

        self.assertTrue(profile.is_online())

    def test_chat_page_requires_login(self):
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 302)


class RegistrationValidationTests(TestCase):
    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username='alice', email='alice@example.com', password='pass123')

        form = RegistrationForm(data={
            'username': 'alice',
            'email': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
            'role': 'student',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(username='alice', email='alice@example.com', password='pass123')

        form = RegistrationForm(data={
            'username': 'bob',
            'email': 'alice@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
            'role': 'student',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
