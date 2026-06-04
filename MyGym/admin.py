from django.contrib import admin
from django.utils.html import format_html
from .models import Member, Workout, WorkoutLog, Schedule, Nutrition

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display  = ['user', 'phone', 'membership_type', 'membership_status', 'is_active', 'join_date']
    list_filter   = ['membership_type', 'membership_status', 'is_active']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display  = ['user', 'title', 'category', 'date_created']
    list_filter   = ['category']
    search_fields = ['title', 'user__username']

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display  = ['user', 'workout', 'completed_at']
    list_filter   = ['completed_at']
    search_fields = ['user__username']
    ordering      = ['-completed_at']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display  = ['user', 'day_of_week', 'name', 'muscle_group']
    list_filter   = ['day_of_week', 'muscle_group']
    search_fields = ['user__username', 'name', 'muscle_group']

@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'meal_name', 'calories', 'protein', 'date']
    list_filter   = ['date']

admin.site.site_header = '💪 MyGym Admin'
admin.site.site_title  = 'MyGym Admin'
admin.site.index_title = 'MyGym Management Panel'