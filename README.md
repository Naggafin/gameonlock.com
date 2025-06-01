# Game On Lock

A Django-based real-money sports betting platform.

## Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Testing](#testing)
- [Deployment](#deployment)
- [Celery & Background Jobs](#celery--background-jobs)
- [Payment Integration](#payment-integration)
- [Wagtail CMS](#wagtail-cms)
- [API Endpoints](#api-endpoints)
- [CI/CD](#cicd)
- [Documentation](#documentation)

---

## Project Overview
Game On Lock enables users to place real-money sports bets through a mobile-first web interface. Plays (bet slips) consist of at least 4 picks. Admins define betting lines via spreadsheet upload, fed by external APIs. Users pay via PayPal at play submission.

## Tech Stack
- Django 5.x
- Wagtail (CMS)
- Celery (background jobs)
- PayPal (payment)
- Bootstrap 5.3, AlpineJS, HTMX (frontend)
- PostgreSQL, Redis
- Django REST Framework (API)

## Setup
1. **Clone the repo:**
   ```bash
   git clone https://github.com/Naggafin/gameonlock.com.git
   cd gameonlock.com
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and update settings (DB, Redis, PayPal, etc).
4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Testing
- **Run all tests:**
  ```bash
  python manage.py test
  ```
- **Test Celery tasks:**
  ```bash
  celery -A gameonlock worker -l info
  # In another terminal:
  python manage.py test betting.tests.test_tasks
  ```
- **Test payment integration:**
  - Configure PayPal sandbox credentials in `.env`.
  - Run payment-related tests:
    ```bash
    python manage.py test payments.tests
    ```
- **Test Wagtail CMS:**
  ```bash
  python manage.py test wagtail.tests
  ```

## Deployment
- **Production checklist:**
  - Set `DEBUG=False` in `.env`.
  - Configure allowed hosts, SSL, and secure settings.
  - Use Gunicorn/Uvicorn, Nginx, and Docker as needed.
  - Set up Redis and Celery for background jobs.
  - Run `python manage.py collectstatic`.

## Celery & Background Jobs
- **Start Celery worker:**
  ```bash
  celery -A gameonlock worker -l info
  ```
- **Start Celery beat (scheduled tasks):**
  ```bash
  celery -A gameonlock beat -l info
  ```
- **Configure Redis in `.env` for Celery broker and backend.**

## Payment Integration
- **PayPal:**
  - Configure PayPal sandbox/production credentials in `.env`.
  - Payment is required at play submission (no wallet system).

## Wagtail CMS
- **Activate Wagtail:**
  - Run migrations and create initial page models.
  - Access Wagtail admin at `/cms/`.

## API Endpoints
- **Implemented with Django REST Framework.**
- Example endpoints:
  - `/api/betting-lines/`
  - `/api/plays/`
  - `/api/results/`
- All endpoints require authentication.

## CI/CD
- **GitHub Actions:**
  - Linting, formatting, and tests run on every push.
  - See `.github/workflows/` for pipeline config.

## Documentation
- See `specifications.md` and `TODO.md` for roadmap and requirements.
- Update documentation as features evolve.

---

For questions, see the project documentation or contact the maintainers.
