"""
Tests for your views (the pages users see).
These test that pages load correctly and forms work.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from MyGym.models import Member, Workout


class AuthViewTest(TestCase):
    """Test login, signup, and logout pages."""
    
    def setUp(self):
        """Create a test user and log them in."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        Member.objects.create(user=self.user)
    
    def test_login_page_loads(self):
        """Test that the login page loads."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        """Test that login works with correct credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_failure(self):
        """Test that login fails with wrong password."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')
    
    def test_signup_password_mismatch(self):
        """Test that signup fails when passwords don't match."""
        response = self.client.post(reverse('signup'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'newuser123',
            'email': 'new@test.com',
            'password1': 'password1',
            'password2': 'password2'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')
    
    def test_signup_weak_password(self):
        """Test that signup fails with weak password."""
        response = self.client.post(reverse('signup'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'newuser456',
            'email': 'new2@test.com',
            'password1': '123',
            'password2': '123'
        })
        self.assertEqual(response.status_code, 200)


class DashboardViewTest(TestCase):
    """Test the dashboard page."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        Member.objects.create(user=self.user)
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_dashboard_access(self):
        """Test that logged-in users can see the dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_requires_login(self):
        """Test that logged-out users are redirected."""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class WorkoutsViewTest(TestCase):
    """Test the workouts page."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            title='Test Workout',
            category='chest',
            exercises='Test exercises'
        )
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_workouts_page(self):
        """Test that workouts page loads."""
        response = self.client.get(reverse('workouts'))
        self.assertEqual(response.status_code, 200)
    
    def test_log_workout(self):
        """Test logging a workout."""
        response = self.client.post(reverse('workouts'), {
            'workout_id': self.workout.id
        })
        self.assertEqual(response.status_code, 302)
    
    def test_log_invalid_workout(self):
        """Test logging a non-existent workout."""
        response = self.client.post(reverse('workouts'), {
            'workout_id': 99999
        })
        self.assertEqual(response.status_code, 302)  # Should redirect, not crash