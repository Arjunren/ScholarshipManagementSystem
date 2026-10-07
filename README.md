# Scholarship Management System

A secure Django REST API for scholarship programs, applicant profiles, application review, and capacity-controlled awards.

## Features

- Admin, reviewer, and applicant roles with rotating token authentication
- Applicant registration with student profile and GPA validation
- Scholarship program windows, funding amounts, and award-slot limits
- One application per applicant per program
- Submitted, under-review, approved, rejected, and withdrawn workflow
- Transactional approval with race-safe slot enforcement and automatic awards
- Applicant-owned data isolation and reviewer dashboard
- PostgreSQL 18, Docker Compose, migrations, seed data, tests, and CI

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

SQLite is used by default. Configure `.env.example` for PostgreSQL or run `docker compose up --build`. Seed users are `admin`, `reviewer`, and `applicant`, all with local-only password `ChangeMe123!`.

## API

Use `Authorization: Token <token>`.

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/auth/register/` | Public applicant registration |
| POST | `/api/auth/login/` | Public |
| GET | `/api/programs/` | Authenticated |
| POST/PATCH | `/api/programs/` | Admin |
| GET | `/api/applications/` | Reviewers all; applicants own |
| POST | `/api/applications/` | Applicant |
| PATCH | `/api/applications/{id}/review/` | Reviewer/admin |
| PATCH | `/api/applications/{id}/withdraw/` | Owning applicant |
| GET | `/api/dashboard/` | Reviewer/admin |

Collections support pagination, search, and ordering. Applications accept a `status` query filter.

## Verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
pip check
```

Tests cover registration role enforcement, duplicate applications, applicant isolation, award capacity, and terminal-state protection. GitHub Actions runs migrations, seeding, checks, tests, and dependency validation against PostgreSQL.

## Security

Public registration can only create applicants. Password validation, login throttling, token rotation, role permissions, and object-scoped querysets are enabled. Application windows and unique submissions are validated on the server and backed by database constraints. Program rows are locked during approvals to prevent capacity races. Configure production secrets, HTTPS, allowed hosts, and restrictive CORS before deployment.

## License

MIT
