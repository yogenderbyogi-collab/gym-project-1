from datetime import date, timedelta


def get_streak(user):
    from MyGym.models import WorkoutLog  # Local import to avoid circular
    logs = WorkoutLog.objects.filter(user=user).values_list(
        'completed_at__date', flat=True
    ).distinct().order_by('-completed_at__date')

    streak = 0
    today = date.today()
    for i, log_date in enumerate(logs):
        if log_date == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak