from django.test import TestCase
from django.contrib.auth.models import User
from MyGym.models import Workout, WorkoutLog
from MyGym.services.streak_service import get_streak
from datetime import date, timedelta
from django.utils import timezone

class StreakServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!'
        )
        self.workout = Workout.objects.create(
            user=self.user, title='Test', category='chest',
            exercises='Test'
        )

    def test_no_workouts_zero_streak(self):
        self.assertEqual(get_streak(self.user), 0)

    def test_single_day_streak(self):
        WorkoutLog.objects.create(user=self.user, workout=self.workout)
        self.assertEqual(get_streak(self.user), 1)

    def test_multiple_day_streak(self):
        today = date.today()
        for i in range(3):
            log = WorkoutLog.objects.create(user=self.user, workout=self.workout)
            log.completed_at = timezone.make_aware(
                timezone.datetime.combine(today - timedelta(days=i), timezone.datetime.min.time())
            )
            log.save()
        self.assertEqual(get_streak(self.user), 3)
