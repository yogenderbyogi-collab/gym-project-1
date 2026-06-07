"""
Tests for your database models.
Tests make sure your code works correctly.
Think of them like a safety net for your website!
"""
from django.test import TestCase
from django.contrib.auth.models import User
from MyGym.models import Member, Workout, WorkoutLog


class MemberModelTest(TestCase):
    """Test the Member model."""
    
    def setUp(self):
        """This runs before each test. Creates a test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='test@test.com'
        )
    
    def test_member_creation(self):
        """Test that a member profile is created correctly."""
        member = Member.objects.create(user=self.user, membership_type='premium')
        self.assertEqual(str(member), 'testuser - premium')
        self.assertTrue(member.is_active)
    
    def test_default_membership(self):
        """Test that default membership is 'basic'."""
        member = Member.objects.create(user=self.user)
        self.assertEqual(member.membership_type, 'basic')


class WorkoutModelTest(TestCase):
    """Test the Workout model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_workout_creation(self):
        """Test that a workout is created correctly."""
        workout = Workout.objects.create(
            user=self.user,
            title='Bench Press',
            category='chest',
            exercises='4 sets x 8 reps'
        )
        self.assertEqual(str(workout), 'Bench Press (Chest)')


class WorkoutLogModelTest(TestCase):
    """Test the WorkoutLog model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            title='Squats',
            category='legs',
            exercises='4 sets x 8 reps'
        )
    
    def test_log_creation(self):
        """Test that a workout log is created correctly."""
        log = WorkoutLog.objects.create(user=self.user, workout=self.workout)
        self.assertEqual(log.user.username, 'testuser')
        self.assertEqual(log.workout.title, 'Squats')