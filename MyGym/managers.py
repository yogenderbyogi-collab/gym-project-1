from django.db import models
from django.utils import timezone


class WorkoutLogManager(models.Manager):
    def this_month(self, user):
        now = timezone.now()
        return self.filter(
            user=user,
            completed_at__year=now.year,
            completed_at__month=now.month
        )

    def this_week(self, user):
        from datetime import timedelta
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())
        return self.filter(user=user, completed_at__gte=week_start)

    def total_for_user(self, user):
        return self.filter(user=user).count()


class BodyStatManager(models.Manager):
    def latest_for_user(self, user, limit=30):
        return self.filter(user=user).order_by('-date')[:limit]