from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models

from ..models import Member, WorkoutLog, Notification
from ..services.streak_service import get_streak


@login_required(login_url='login')
def dashboard(request):
    member, created = Member.objects.get_or_create(user=request.user)
    now = timezone.now()
    monthly_count = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__year=now.year,
        completed_at__month=now.month
    ).count()
    streak = get_streak(request.user)

    if created:
        Notification.objects.create(
            user=request.user,
            message="Welcome to MyGym! Complete your profile in Settings.",
            notif_type='success'
        )
    if streak == 7:
        if not Notification.objects.filter(user=request.user, message__contains="7-day streak").exists():
            Notification.objects.create(
                user=request.user,
                message="You hit a 7-day workout streak! Keep it up!",
                notif_type='success'
            )
    if monthly_count == 10:
        if not Notification.objects.filter(user=request.user, message__contains="10 workouts").exists():
            Notification.objects.create(
                user=request.user,
                message="Amazing! 10 workouts this month milestone reached!",
                notif_type='success'
            )

    unread_notifs = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'dashboard.html', {
        'member': member,
        'monthly_count': monthly_count,
        'streak': streak,
        'unread_notifs': unread_notifs,
    })


@login_required
def streak_view(request):
    from datetime import date, timedelta
    from collections import Counter

    logs = WorkoutLog.objects.filter(user=request.user)
    date_counts = Counter(log.completed_at.date().isoformat() for log in logs)
    streak = get_streak(request.user)
    total = WorkoutLog.objects.filter(user=request.user).count()

    best = cur = 0
    today = date.today()
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if d in date_counts:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0

    import json
    return render(request, 'streak.html', {
        'date_counts_json': json.dumps(dict(date_counts)),
        'streak': streak,
        'best_streak': best,
        'total_workouts': total,
    })


@login_required
def notifications_view(request):
    if request.method == 'POST':
        notif_id = request.POST.get('mark_read')
        if notif_id == 'all':
            Notification.objects.filter(user=request.user).update(is_read=True)
        else:
            Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
        return redirect('notifications')

    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread = notifs.filter(is_read=False).count()
    return render(request, 'notifications.html', {'notifs': notifs, 'unread': unread})


@login_required
def notifications_count(request):
    from django.http import JsonResponse
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})