from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json, os, io, base64, hashlib

from .models import Member, Workout, Schedule, Nutrition, WorkoutLog, BodyStat, Notification, WaterLog, ProgressPhoto
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MemberSerializer, WorkoutSerializer, WorkoutLogSerializer

import requests as req_lib
from datetime import date, timedelta
import json
from collections import Counter

# ── HELPERS ───────────────────────────────────────────────────────────────────

def create_notification(user, message, notif_type='info'):
    Notification.objects.create(user=user, message=message, notif_type=notif_type)

def get_streak(user):
    from datetime import date, timedelta
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

# ── AUTH ──────────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(request,
            username=request.POST['username'],
            password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid username or password!'})
    return render(request, 'login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name  = request.POST['last_name']
        username   = request.POST['username']
        email      = request.POST['email']
        password1  = request.POST['password1']
        password2  = request.POST['password2']
        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match!'})
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken!'})
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered!'})
        user = User.objects.create_user(
            username=username, email=email,
            password=password1, first_name=first_name, last_name=last_name)
        user.save()
        Member.objects.create(user=user)
        return render(request, 'signup.html', {'success': 'Account created! You can now login.'})
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

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
        create_notification(request.user, "Welcome to MyGym! Complete your profile in Settings.", 'success')
    if streak == 7:
        if not Notification.objects.filter(user=request.user, message__contains="7-day streak").exists():
            create_notification(request.user, "🔥 You hit a 7-day workout streak! Keep it up!", 'success')
    if monthly_count == 10:
        if not Notification.objects.filter(user=request.user, message__contains="10 workouts").exists():
            create_notification(request.user, "💪 Amazing! 10 workouts this month milestone reached!", 'success')

    unread_notifs = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'dashboard.html', {
        'member': member,
        'monthly_count': monthly_count,
        'streak': streak,
        'unread_notifs': unread_notifs,
    })

# ── SERVICES ──────────────────────────────────────────────────────────────────

SERVICES_DATA = {
    'strength-training': {
        'title': 'Strength Training', 'icon': '💪',
        'desc': 'Build muscle with state-of-the-art equipment and expert coaching tailored to your goals.',
        'full_info': 'Our strength facility includes advanced free weights, selectorized machines, and specialized lifting platforms.',
        'benefits': ['Increased muscle mass', 'Enhanced metabolic rate', 'Improved bone density', 'Better joint stability'],
        'schedule': 'Mon - Fri: 6:00 AM, 11:00 AM, 6:00 PM'
    },
    'cardio-hiit': {
        'title': 'Cardio & HIIT', 'icon': '🔥',
        'desc': 'Burn fat fast with high-intensity sessions led by certified fitness professionals.',
        'full_info': 'HIIT is designed to keep your heart rate up and burn more calories in less time.',
        'benefits': ['Rapid calorie burning', 'Improved cardiovascular health', 'Post-workout caloric burn', 'Short, efficient workouts'],
        'schedule': 'Tue - Thu: 7:00 AM, 5:30 PM'
    },
    'personal-training': {
        'title': 'Personal Training', 'icon': '🏋️',
        'desc': 'One-on-one sessions with dedicated trainers who customize every workout for you.',
        'full_info': 'Get matched with a certified personal trainer who builds an evolving roadmap for you.',
        'benefits': ['100% customized programming', 'Form correction', 'Accountability coaching', 'Accelerated milestones'],
        'schedule': 'By Appointment (Flexible booking)'
    },
    'yoga-wellness': {
        'title': 'Yoga & Wellness', 'icon': '🧘',
        'desc': 'Restore balance and mental clarity through guided yoga and wellness programs.',
        'full_info': 'Our wellness studio hosts Vinyasa flows, power yoga, and restorative meditation classes.',
        'benefits': ['Enhanced flexibility', 'Stress reduction', 'Improved breathing', 'Accelerated recovery'],
        'schedule': 'Mon - Wed - Sat: 8:00 AM, 4:00 PM'
    },
    'nutrition-plans': {
        'title': 'Nutrition Plans', 'icon': '🥗',
        'desc': 'Fuel your training with personalized diet plans crafted by our in-house dietitians.',
        'full_info': 'Our sports nutritionists break down your macronutrient thresholds and map out meal preps.',
        'benefits': ['Customized macro allocations', 'Sustainable adaptations', 'Weekly reviews', 'Optimized energy'],
        'schedule': 'Consultations bookable daily'
    },
    '24-7-access': {
        'title': '24/7 Access', 'icon': '⏰',
        'desc': 'Train on your schedule with round-the-clock access to all gym facilities.',
        'full_info': 'Members get an encrypted digital keypass providing safe, fully monitored access at any hour.',
        'benefits': ['Zero scheduling conflicts', 'Safe 24/7 surveillance', 'Full facility access', 'Quiet off-peak hours'],
        'schedule': 'Always Open (24 Hours / 365 Days)'
    },
}

def services_view(request):
    return render(request, 'services.html', {'services': SERVICES_DATA})

def service_detail_view(request, service_slug):
    service = SERVICES_DATA.get(service_slug)
    if not service:
        raise Http404("Service not found")
    return render(request, 'service_detail.html', {'service': service})

def support_view(request):
    return render(request, 'support.html')

def contact_view(request):
    return render(request, 'contact.html')

# ── WORKOUTS ──────────────────────────────────────────────────────────────────

@login_required
def workouts_view(request):
    if request.method == 'POST':
        workout_id = request.POST.get('workout_id')
        if workout_id:
            workout = Workout.objects.get(id=workout_id)
            WorkoutLog.objects.create(user=request.user, workout=workout)
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

# ── SCHEDULE ──────────────────────────────────────────────────────────────────

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

    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    sessions = Schedule.objects.filter(user=request.user)

    # Group sessions by day for the template's get_item filter
    schedule_by_day = {}
    for day in days:
        schedule_by_day[day] = list(sessions.filter(day_of_week=day))

    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).strftime('%b %d, %Y')

    return render(request, 'schedule.html', {
        'days': days,
        'schedule_by_day': schedule_by_day,
        'week_start': week_start,
    })

# ── NUTRITION ─────────────────────────────────────────────────────────────────

@login_required
def nutrition_view(request):
    return render(request, 'nutrition.html', {
        'nutrition_logs': Nutrition.objects.filter(user=request.user)
    })

@login_required
def nutrition_ai(request):
    return render(request, 'nutrition_ai.html')

@csrf_exempt
@require_POST
def nutrition_ai_chat(request):
    try:
        data = json.loads(request.body)
        msgs = data.get('messages', [])
        if not msgs:
            return JsonResponse({'error': 'No messages provided'}, status=400)

        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            return JsonResponse({'error': 'GROQ_API_KEY is not set. Get free key at console.groq.com'}, status=500)

        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            messages=[{
                "role": "system",
                "content": "You are a certified sports nutritionist. Give practical, personalized, food-specific advice. Always respect the user's dietary preference and cuisine preference strictly."
            }, *msgs]
        )
        return JsonResponse({'reply': response.choices[0].message.content})

    except Exception as e:
        import traceback
        print("=== NUTRITION AI ERROR ===")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

# ── FOOD SEARCH ───────────────────────────────────────────────────────────────

def food_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'products': []})

    USDA_KEY = 'DEMO_KEY'  # get free key at fdc.nal.usda.gov/api-key-signup.html

    try:
        response = req_lib.get(
            'https://api.nal.usda.gov/fdc/v1/foods/search',
            params={
                'query': query,
                'api_key': USDA_KEY,
                'pageSize': 6,
                'dataType': 'SR Legacy,Foundation'
            },
            timeout=10
        )
        data = response.json()

        filtered = []
        for food in data.get('foods', []):
            name = food.get('description', '').strip()
            if not name:
                continue
            nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}
            cal  = round(nutrients.get('Energy', 0))
            prot = round(nutrients.get('Protein', 0), 1)
            carb = round(nutrients.get('Carbohydrate, by difference', 0), 1)
            fat  = round(nutrients.get('Total lipid (fat)', 0), 1)
            if not cal:
                continue
            filtered.append({
                'product_name': name.title(),
                'nutriments': {
                    'energy-kcal_100g': cal,
                    'proteins_100g': prot,
                    'carbohydrates_100g': carb,
                    'fat_100g': fat,
                }
            })

        return JsonResponse({'products': filtered})

    except Exception as e:
        import traceback
        print("FOOD SEARCH ERROR:", traceback.format_exc())
        return JsonResponse({'error': str(e), 'products': []}, status=500)

# ── BODY STATS ────────────────────────────────────────────────────────────────

@login_required
def body_stats_view(request):
    if request.method == 'POST':
        try:
            weight   = float(request.POST.get('weight', 0) or 0)
            body_fat = request.POST.get('body_fat', '').strip() or None
            height   = request.POST.get('height', '').strip()
            if weight <= 0:
                messages.error(request, 'Weight must be greater than zero.')
                return redirect('body_stats')
            bmi = None
            if height:
                h = float(height) / 100
                bmi = round(weight / (h * h), 1)
            BodyStat.objects.create(
                user=request.user, weight=weight,
                body_fat=float(body_fat) if body_fat else None, bmi=bmi)
            messages.success(request, 'Stats logged!')
        except ValueError:
            messages.error(request, 'Please enter valid numeric values.')
        return redirect('body_stats')

    stats = BodyStat.objects.filter(user=request.user).order_by('-date')[:30]
    return render(request, 'body_stats.html', {'stats': stats})

# ── MEMBERSHIP QR ─────────────────────────────────────────────────────────────

@login_required
def membership_qr_view(request):
    import qrcode
    member = Member.objects.get(user=request.user)
    member_id = hashlib.md5(f"{request.user.username}{request.user.id}".encode()).hexdigest()[:10].upper()
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"MYGYM|{request.user.username}|{member_id}|{member.membership_type}|{member.membership_status}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return render(request, 'membership_qr.html', {
        'qr_code': base64.b64encode(buffer.getvalue()).decode(),
        'member_id': member_id,
        'membership_type': member.membership_type,
        'status': member.membership_status,
    })

@login_required
def download_qr_view(request):
    import qrcode
    member = Member.objects.get(user=request.user)
    member_id = hashlib.md5(f"{request.user.username}{request.user.id}".encode()).hexdigest()[:10].upper()
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"MYGYM|{request.user.username}|{member_id}|{member.membership_type}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="mygym_membership_qr.png"'
    return response

# ── SETTINGS ──────────────────────────────────────────────────────────────────

@login_required
def settings_view(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    active_tab = 'profile'

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_profile':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name  = request.POST.get('last_name', '').strip()
            user.email      = request.POST.get('email', '').strip()
            if request.FILES.get('profile_picture') and member:
                member.profile_picture = request.FILES['profile_picture']
                member.save()
            new_username = request.POST.get('username', '').strip()
            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                    messages.error(request, 'That username is already taken.')
                    return render(request, 'settings.html', {'member': member, 'active_tab': active_tab})
            user.username = new_username or user.username
            user.save()
            if member:
                member.phone            = request.POST.get('phone', '').strip()
                member.fitness_goal     = request.POST.get('fitness_goal', '')
                member.experience_level = request.POST.get('experience_level', '')
                member.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('settings')

        elif action == 'change_password':
            active_tab = 'password'
            current_pw = request.POST.get('current_password', '')
            new_pw     = request.POST.get('new_password', '')
            confirm_pw = request.POST.get('confirm_password', '')
            if not request.user.check_password(current_pw):
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'settings.html', {'member': member, 'active_tab': active_tab})
            if new_pw != confirm_pw:
                messages.error(request, 'New passwords do not match.')
                return render(request, 'settings.html', {'member': member, 'active_tab': active_tab})
            if len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
                return render(request, 'settings.html', {'member': member, 'active_tab': active_tab})
            request.user.set_password(new_pw)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('settings')

        elif action == 'change_plan':
            plan = request.POST.get('plan', '')
            if member and plan in ('basic', 'premium'):
                member.membership_type = plan
                member.save()
                messages.success(request, f'Plan changed to {plan.capitalize()} successfully.')
            return redirect('settings')

        elif action == 'freeze_membership':
            if member:
                member.membership_status = 'frozen'
                member.save()
            messages.success(request, 'Your membership has been frozen.')
            return redirect('settings')

        elif action == 'cancel_membership':
            if member:
                member.membership_status = 'cancelled'
                member.save()
            messages.success(request, 'Membership cancellation requested.')
            return redirect('settings')

        elif action == 'delete_account':
            from django.contrib.auth import logout as auth_logout
            user = request.user
            auth_logout(request)
            user.delete()
            return redirect('home')

    next_billing = billing_end = None
    if member:
        next_billing = (request.user.date_joined + timedelta(days=30)).strftime('%B %d, %Y')
        billing_end  = next_billing

    return render(request, 'settings.html', {
        'member': member,
        'next_billing': next_billing,
        'billing_end': billing_end,
        'active_tab': active_tab,
    })

# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

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
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

# ── REST API ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    member = Member.objects.get(user=request.user)
    return Response(MemberSerializer(member).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_workouts(request):
    return Response(WorkoutSerializer(Workout.objects.all(), many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_logs(request):
    logs = WorkoutLog.objects.filter(user=request.user).order_by('-completed_at')[:20]
    return Response(WorkoutLogSerializer(logs, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    now = timezone.now()
    monthly = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__year=now.year,
        completed_at__month=now.month
    ).count()
    total  = WorkoutLog.objects.filter(user=request.user).count()
    member = Member.objects.get(user=request.user)
    return Response({
        'username': request.user.username,
        'membership': member.membership_type,
        'status': member.membership_status,
        'workouts_this_month': monthly,
        'total_workouts': total,
        'current_streak': get_streak(request.user),
    })

# ── EXPORT PDF ────────────────────────────────────────────────────────────────

@login_required
def export_workout_pdf(request):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from datetime import date

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFillColorRGB(0.9, 0.24, 0.24)
    p.rect(0, height-80, width, 80, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 28)
    p.drawString(40, height-52, "MyGym — Workout Report")
    p.setFont("Helvetica", 12)
    p.drawString(40, height-70, f"Member: {request.user.get_full_name() or request.user.username}")
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.setFont("Helvetica", 10)
    p.drawString(40, height-100, f"Generated: {date.today().strftime('%B %d, %Y')}")

    now = timezone.now()
    monthly = WorkoutLog.objects.filter(user=request.user, completed_at__year=now.year, completed_at__month=now.month).count()
    streak  = get_streak(request.user)
    total   = WorkoutLog.objects.filter(user=request.user).count()

    for i, (val, label, x) in enumerate([(monthly,'THIS MONTH',40),(streak,'DAY STREAK',210),(total,'TOTAL',380)]):
        p.setFillColorRGB(0.1, 0.1, 0.1)
        p.rect(x, height-160, 150, 50, fill=1, stroke=0)
        p.setFillColorRGB(0.9, 0.24, 0.24)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(x+50, height-135, str(val))
        p.setFillColorRGB(0.6, 0.6, 0.6)
        p.setFont("Helvetica", 9)
        p.drawString(x+15, height-153, label)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, height-195, "Recent Workout History")
    p.setFillColorRGB(0.9, 0.24, 0.24)
    p.rect(40, height-215, width-80, 20, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, height-208, "WORKOUT")
    p.drawString(460, height-208, "DATE")

    y = height - 230
    for i, log in enumerate(WorkoutLog.objects.filter(user=request.user).order_by('-completed_at')[:25]):
        bg = 0.97 if i % 2 == 0 else 1.0
        p.setFillColorRGB(bg, bg, bg)
        p.rect(40, y-5, width-80, 18, fill=1, stroke=0)
        p.setFillColorRGB(0.1, 0.1, 0.1)
        p.setFont("Helvetica", 9)
        p.drawString(50, y+2, str(log.workout)[:60])
        p.drawString(460, y+2, log.completed_at.strftime('%d %b %Y'))
        y -= 18
        if y < 60:
            p.showPage()
            y = height - 60

    p.setFillColorRGB(0.7, 0.7, 0.7)
    p.setFont("Helvetica", 8)
    p.drawString(40, 30, "MyGym — Live Your Best Life | Generated automatically")
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="MyGym_Workout_Report.pdf"'
    return response

# ── EMAIL REPORT ──────────────────────────────────────────────────────────────

@login_required
def send_email_report(request):
    from django.core.mail import send_mail
    now    = timezone.now()
    monthly = WorkoutLog.objects.filter(user=request.user, completed_at__year=now.year, completed_at__month=now.month).count()
    streak  = get_streak(request.user)
    total   = WorkoutLog.objects.filter(user=request.user).count()
    member  = Member.objects.get(user=request.user)
    name    = request.user.get_full_name() or request.user.username

    try:
        send_mail(
            f"💪 MyGym Weekly Report — {now.strftime('%B %Y')}",
            f"Hi {name}!\n\nWorkouts this month: {monthly}\nStreak: {streak} days 🔥\nTotal: {total}\nPlan: {member.membership_type.upper()}\n\n— MyGym Team",
            None,
            [request.user.email],
            fail_silently=False,
        )
        messages.success(request, f'Report sent to {request.user.email}!')
    except Exception as e:
        messages.error(request, f'Email failed: {str(e)}')
    return redirect('dashboard')

@login_required
def streak_view(request):
    from datetime import date
    from collections import Counter
    logs = WorkoutLog.objects.filter(user=request.user)
    date_counts = Counter(log.completed_at.date().isoformat() for log in logs)
    streak = get_streak(request.user)
    total  = WorkoutLog.objects.filter(user=request.user).count()
    best = cur = 0
    today = date.today()
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        if d in date_counts:
            cur += 1; best = max(best, cur)
        else:
            cur = 0
    return render(request, 'streak.html', {
        'date_counts_json': json.dumps(dict(date_counts)),
        'streak': streak,
        'best_streak': best,
        'total_workouts': total,
    })

@login_required
def orm_view(request):
    result = None
    if request.method == 'POST':
        try:
            weight = float(request.POST.get('weight', 0))
            reps   = int(request.POST.get('reps', 0))
            if weight > 0 and reps > 0:
                # Brzycki formula
                orm = weight / (1.0278 - 0.0278 * reps)
                result = {
                    'orm':    round(orm, 1),
                    'p90':    round(orm * 0.90, 1),
                    'p80':    round(orm * 0.80, 1),
                    'p70':    round(orm * 0.70, 1),
                    'p60':    round(orm * 0.60, 1),
                    'weight': weight,
                    'reps':   reps,
                    'zones': [
                        ('90% — Heavy',       round(orm * 0.90, 1), '#e63329', '3-5 reps'),
                        ('80% — Strength',    round(orm * 0.80, 1), '#f6ad55', '5-8 reps'),
                        ('70% — Hypertrophy', round(orm * 0.70, 1), '#68d391', '8-12 reps'),
                        ('60% — Endurance',   round(orm * 0.60, 1), '#4299e1', '12-15 reps'),
                    ]
                }
        except (ValueError, ZeroDivisionError):
            pass
    return render(request, 'orm.html', {'result': result})

# ── WATER LOG ─────────────────────────────────────────────────────────────────

@login_required
def water_view(request):
    from datetime import date
    today = date.today()
    log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    history = WaterLog.objects.filter(user=request.user).order_by('-date')[:7]
    return render(request, 'water.html', {'log': log, 'history': history})

@login_required
@require_POST
def water_update(request):
    from datetime import date
    data   = json.loads(request.body)
    action = data.get('action')
    today  = date.today()
    log, _ = WaterLog.objects.get_or_create(user=request.user, date=today)
    if action == 'add' and log.glasses < 20:
        log.glasses += 1
    elif action == 'remove' and log.glasses > 0:
        log.glasses -= 1
    elif action == 'set_goal':
        log.goal = int(data.get('goal', 8))
    log.save()
    return JsonResponse({'glasses': log.glasses, 'goal': log.goal})

@login_required
def progress_photos_view(request):
    if request.method == 'POST':
        photo  = request.FILES.get('photo')
        weight = request.POST.get('weight', '').strip() or None
        notes  = request.POST.get('notes', '').strip()
        if photo:
            ProgressPhoto.objects.create(
                user=request.user, photo=photo,
                weight=float(weight) if weight else None, notes=notes)
            messages.success(request, 'Progress photo saved!')
        return redirect('progress_photos')
    photos = ProgressPhoto.objects.filter(user=request.user).order_by('-date')
    return render(request, 'progress_photos.html', {'photos': photos})

@login_required
def delete_progress_photo(request, pk):
    ProgressPhoto.objects.filter(id=pk, user=request.user).delete()
    return redirect('progress_photos')

@login_required
def timer_view(request):
    return render(request, 'timer.html')

@login_required
def workout_card_view(request):
    from datetime import date
    today_logs = WorkoutLog.objects.filter(
        user=request.user,
        completed_at__date=date.today()
    ).select_related('workout')
    streak = get_streak(request.user)
    total  = WorkoutLog.objects.filter(user=request.user).count()
    return render(request, 'workout_card.html', {
        'today_logs': today_logs,
        'streak': streak,
        'total': total,
        'today': date.today().strftime('%B %d, %Y'),
    })

@login_required
def ai_workout_view(request):
    return render(request, 'ai_workout.html')

@csrf_exempt
@require_POST
def ai_workout_generate(request):
    try:
        data   = json.loads(request.body)
        goal   = data.get('goal', 'muscle gain')
        muscle = data.get('muscle', 'full body')
        level  = data.get('level', 'intermediate')
        days   = data.get('days', 4)
        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            return JsonResponse({'error': 'GROQ_API_KEY not set'}, status=500)
        from groq import Groq
        client = Groq(api_key=api_key)
        prompt = f"""You are an expert personal trainer. Generate a {days}-day workout plan.
Goal: {goal}, Focus: {muscle}, Level: {level}
Return ONLY a JSON object (no markdown):
{{"plan_name":"string","days":[{{"day":"Day 1 - Monday","focus":"Chest","exercises":[{{"name":"Bench Press","sets":4,"reps":"8-10","rest":"90s","tip":"Keep back flat"}}]}}],"tips":["tip1"]}}"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", max_tokens=2000,
            messages=[{"role": "user", "content": prompt}])
        raw  = response.choices[0].message.content.strip()
        raw  = raw.replace('```json','').replace('```','').strip()
        plan = json.loads(raw)
        return JsonResponse({'plan': plan})
    except Exception as e:
        import traceback; print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)