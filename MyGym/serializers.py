from rest_framework import serializers
from .models import Member, Workout, WorkoutLog
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Member
        fields = ['user', 'membership_type', 'membership_status', 'phone', 'fitness_goal', 'experience_level']

class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'title', 'category', 'exercises', 'image_url', 'date_created']

class WorkoutLogSerializer(serializers.ModelSerializer):
    workout_title = serializers.CharField(source='workout.title', read_only=True)
    category      = serializers.CharField(source='workout.category', read_only=True)
    class Meta:
        model = WorkoutLog
        fields = ['id', 'workout_title', 'category', 'completed_at']

class ProfileSerializer(serializers.ModelSerializer):
    membership_type   = serializers.CharField(source='member.membership_type')
    membership_status = serializers.CharField(source='member.membership_status')
    join_date         = serializers.DateField(source='member.join_date')
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'membership_type', 'membership_status', 'join_date']