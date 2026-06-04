import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gym_project.settings')
django.setup()

from django.contrib.auth.models import User
from MyGym.models import Workout

def seed_data():
    user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        print("❌ Error: No admin user found!")
        return

    Workout.objects.filter(user=user).delete()

    workouts_data = [
        # ================= CHEST =================
        {
            "title": "Barbell Bench Press",
            "category": "chest",
            "exercises": "• 4 sets x 8 reps\n• Lower the bar slowly to mid-chest level.\n• Keep shoulder blades squeezed tightly.",
            "image_url": "/static/gifs/bench-press.gif"
        },
        {
            "title": "Incline Dumbbell Press",
            "category": "chest",
            "exercises": "• 3 sets x 10 reps\n• Set bench to 30-degree incline.\n• Push weights up in arc over upper chest.",
            "image_url": "/static/gifs/incline-press.gif"
        },
        {
            "title": "Dumbbell Chest Flyes",
            "category": "chest",
            "exercises": "• 3 sets x 12 reps\n• Maintain slight bend in elbows.\n• Squeeze pectorals together at peak contraction.",
            "image_url": "/static/gifs/chest-fly.gif"
        },

        # ================= BACK =================
        {
            "title": "Bent Over Barbell Row",
            "category": "back",
            "exercises": "• 4 sets x 10 reps\n• Hinge at hips. Pull bar to lower stomach.\n• Squeeze upper back at the top.",
            "image_url": "/static/gifs/barbell-row.gif"
        },
        {
            "title": "Lat Pulldown",
            "category": "back",
            "exercises": "• 4 sets x 12 reps\n• Sit upright, pull to upper chest.\n• Let weight up slowly under control.",
            "image_url": "/static/gifs/lat-pulldown.gif"
        },
        {
            "title": "Seated Cable Rows",
            "category": "back",
            "exercises": "• 3 sets x 12 reps\n• Keep spine tall.\n• Pull handles into lower belly.",
            "image_url": "/static/gifs/cable-row.gif"
        },

        # ================= SHOULDERS =================
        {
            "title": "Seated Dumbbell Press",
            "category": "shoulders",
            "exercises": "• 3 sets x 12 reps\n• Keep back flat against seat.\n• Press weights straight up overhead.",
            "image_url": "/static/gifs/shoulder-press.gif"
        },
        {
            "title": "Dumbbell Lateral Raise",
            "category": "shoulders",
            "exercises": "• 4 sets x 15 reps\n• Raise weights out to sides until parallel to floor.",
            "image_url": "/static/gifs/lateral-raise.gif"
        },
        {
            "title": "Barbell Shrugs",
            "category": "shoulders",
            "exercises": "• 3 sets x 15 reps\n• Elevate shoulders toward ears, pause, and lower.",
            "image_url": "/static/gifs/shrugs.gif"
        },

        # ================= LEGS =================
        {
            "title": "Barbell Back Squat",
            "category": "legs",
            "exercises": "• 4 sets x 8 reps\n• Drop hips back and down below parallel.\n• Drive up forcefully through heels.",
            "image_url": "/static/gifs/squat.gif"
        },
        {
            "title": "Dumbbell Lunges",
            "category": "legs",
            "exercises": "• 3 sets x 12 reps per leg\n• Step forward into deep stance.\n• Push back off front foot.",
            "image_url": "/static/gifs/lunges.gif"
        },
        {
            "title": "Leg Extensions",
            "category": "legs",
            "exercises": "• 3 sets x 15 reps\n• Sit in machine.\n• Fully extend legs out straight.",
            "image_url": "/static/gifs/leg-extension.gif"
        },

        # ================= ABS =================
        {
            "title": "Hanging Leg Raise",
            "category": "abs",
            "exercises": "• 3 sets x 15 reps\n• Hang from bar.\n• Use core to bring knees toward chest.",
            "image_url": "/static/gifs/hanging-leg-raise.gif"
        },
        {
            "title": "Standard Crunches",
            "category": "abs",
            "exercises": "• 3 sets x 20 reps\n• Elevate shoulder blades off floor.\n• Squeeze core tight.",
            "image_url": "/static/gifs/crunches.gif"
        },
        {
            "title": "Plank Hold",
            "category": "abs",
            "exercises": "• 3 sets x 60 seconds\n• Keep body straight on forearms.\n• Do not sag hips.",
            "image_url": "/static/gifs/plank.gif"
        },
    ]

    for item in workouts_data:
        Workout.objects.create(
            user=user,
            title=item["title"],
            category=item["category"],
            exercises=item["exercises"],
            image_url=item["image_url"]
        )
    print("✅ Done! All 15 workouts seeded correctly.")

if __name__ == '__main__':
    seed_data()