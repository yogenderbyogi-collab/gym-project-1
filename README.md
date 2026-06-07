# MyGym

A comprehensive Django-based fitness management platform with workout tracking, AI nutrition coaching, body stats, QR membership cards, and more.

## Features

- User authentication (login/signup) with strong password validation
- Workout tracking and logging
- AI-powered nutrition coaching (Groq API)
- Weekly schedule builder
- Body stats & BMI tracking
- Progress photo uploads
- QR code membership cards
- Workout streak tracking
- PDF export & email reports
- 1RM calculator
- Water intake tracker
- Notification system

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for caching)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yogenderbyogi-collab/gym-project-1.git
cd gym-project-1
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Seed workout data:
```bash
python manage.py seed_workouts
```

8. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000

### Running Tests

```bash
python manage.py test MyGym.tests --verbosity=2
```

### Docker Deployment

```bash
docker-compose up --build
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Enable debug mode | No (default: False) |
| ALLOWED_HOSTS | Comma-separated allowed hosts | Yes |
| DATABASE_URL | PostgreSQL connection URL | For production |
| GROQ_API_KEY | Groq API key for AI features | Yes |
| EMAIL_HOST_USER | SMTP email address | For email features |
| EMAIL_HOST_PASSWORD | SMTP app password | For email features |
| CSRF_TRUSTED_ORIGINS | HTTPS origins for CSRF | For production |

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **AI**: Groq API (Llama 3.3 70B)
- **Styling**: Custom CSS (dark theme)
- **PDF**: ReportLab
- **QR Codes**: qrcode library
- **Cache**: Redis

## License

[Your License]
