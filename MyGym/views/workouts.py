from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from ..models import Workout, WorkoutLog, Schedule


@login_required
def workouts_view(request):
    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        if workout_id:
            try:
                workout = Workout.objects.get(id=int(workout_id))
                WorkoutLog.objects.create(user=request.user, workout=workout)
                messages.success(request, f'Logged: {workout.title}')
            except (Workout.DoesNotExist, ValueError):
                messages.error(request, 'Workout not found.')
        return redirect('workouts')

    now = timezone.now()
    user_workouts = Workout.objects.all()
    monthly_count = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__year=now.year,
        completed_at__month=now.month
    ).count()
    logged_ids = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__year=now.year,
        completed_at__month=now.month
    ).values_list('workout_id', flat=True)

    return render(request, 'workouts.html', {
        'workouts': user_workouts,
        'monthly_count': monthly_count,
        'logged_ids': list(logged_ids),
    })


@login_required
def schedule_view(request):
    from datetime import date

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            Schedule.objects.create(
                user=request.user,
                day_of_week=request.POST.get('day'),
                name=request.POST.get('name'),
                muscle_group=request.POST.get('muscle_group'),
                exercises=request.POST.get('exercises', ''),
                duration=request.POST.get('duration') or None,
                exercise_count=request.POST.get('exercise_count') or None,
                notes=request.POST.get('notes', ''),
            )
        elif action == 'delete':
            Schedule.objects.filter(
                id=request.POST.get('session_id'),
                user=request.user
            ).delete()
        return redirect('schedule')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sessions = Schedule.objects.filter(user=request.user)
    schedule_by_day = {day: list(sessions.filter(day_of_week=day)) for day in days}
    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).strftime('%b %d, %Y')

    return render(request, 'schedule.html', {
        'days': days,
        'schedule_by_day': schedule_by_day,
        'week_start': week_start,
    })


@login_required
def timer_view(request):
    return render(request, 'timer.html')