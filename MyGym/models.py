from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from MyGym.managers import BodyStatManager, WorkoutLogManager


class Member(models.Model):

    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user             = models.OneToOneField(User, on_delete=models.CASCADE)
    phone            = models.CharField(max_length=15, blank=True)
    fitness_goal     = models.CharField(max_length=50, blank=True, null=True)
    experience_level = models.CharField(max_length=20, blank=True, null=True)
    gender           = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth    = models.DateField(null=True, blank=True)
    address          = models.TextField(blank=True)
    membership_type  = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='basic')
    join_date        = models.DateField(auto_now_add=True)
    is_active        = models.BooleanField(default=True)
    membership_status = models.CharField(max_length=20, default='active')
    profile_picture  = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type}"


class Nutrition(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_name = models.CharField(max_length=100)
    calories  = models.IntegerField()
    protein   = models.IntegerField()
    date      = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.meal_name}"


class Workout(models.Model):
    CATEGORY_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('legs', 'Legs'),
        ('abs', 'Abs'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    title        = models.CharField(max_length=100)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='chest')
    exercises    = models.TextField(help_text="Enter variation details, sets, and reps.")
    image_url    = models.URLField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, db_index=True)
    completed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = WorkoutLogManager()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'completed_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workout.title}"


class BodyStat(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    weight   = models.FloatField()
    body_fat = models.FloatField(null=True, blank=True)
    bmi      = models.FloatField(null=True, blank=True)
    date     = models.DateField(auto_now_add=True)
    objects = BodyStatManager()

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Notification(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    message    = models.CharField(max_length=300)
    notif_type = models.CharField(max_length=20, default='info')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['user', 'is_read', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} - {self.message[:40]}"


class WorkoutSession(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    day          = models.CharField(max_length=20, default='')
    name         = models.CharField(max_length=100, default='')
    activity     = models.CharField(max_length=200, default='')
    muscle_group = models.CharField(max_length=50, default='Custom')
    exercises    = models.TextField(blank=True)
    duration     = models.IntegerField(null=True, blank=True)
    exercise_count = models.IntegerField(null=True, blank=True)
    notes        = models.TextField(blank=True)
    color        = models.CharField(max_length=20, default='#a0aec0')

    def __str__(self):
        return f"{self.user.username} - {self.day} - {self.name}"


class Schedule(models.Model):
    COLOR_CHOICES = [
        ('#e63329', 'Red'),
        ('#48bb78', 'Green'),
        ('#4299e1', 'Blue'),
        ('#ed8936', 'Orange'),
        ('#9f7aea', 'Purple'),
    ]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    day_of_week    = models.CharField(max_length=20, default='', db_index=True)
    name           = models.CharField(max_length=100, default='')
    activity       = models.CharField(max_length=200, default='')
    muscle_group   = models.CharField(max_length=50, default='Full Body')
    exercises      = models.TextField(blank=True, default='')
    duration       = models.PositiveIntegerField(null=True, blank=True)
    exercise_count = models.PositiveIntegerField(null=True, blank=True)
    notes          = models.TextField(blank=True, default='')
    color          = models.CharField(max_length=10, choices=COLOR_CHOICES, default='#e63329')
    created_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['user', 'day_of_week'])]

    def __str__(self):
        return f"{self.user.username} - {self.day_of_week} - {self.name}"


class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    glasses = models.IntegerField(default=0)
    goal    = models.IntegerField(default=8)
    date = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user', '-date']),
        ]


    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.glasses} glasses"


class ProgressPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    photo  = models.ImageField(upload_to='progress_photos/')
    weight = models.FloatField(null=True, blank=True)
    notes  = models.TextField(blank=True)
    date   = models.DateField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-date']),
        ]