# FairShare

A shared expense splitter: create groups, split bills equally or by custom amounts, see who owes what, and track payments.

**Status:** work in progress. The backend foundations are in place; the frontend is next.

## Tech stack

- **Backend:** Django 5.2 LTS on Python 3.14, with Django REST Framework
- **Database:** MySQL 8.4 LTS
- **Local environment:** Docker Compose
- **Checks:** GitHub Actions runs ruff (lint and format), pytest and pip-audit on every pull request
- **Frontend (planned):** Next.js with TypeScript

## Getting started

You need **Git** and **Docker Desktop** (open and running).

1. Clone the repository and move into it:

   ```
   git clone https://github.com/PjnSai/fairshare.git
   cd fairshare
   ```

2. Create your private settings file from the template:

   ```
   Copy-Item .env.example .env
   ```

   (On Mac or Linux: `cp .env.example .env`.) Open `.env` and replace every `change-me` with a different long random string. This command prints one in PowerShell:

   ```
   -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 50 | % {[char]$_})
   ```

   `.env` is ignored by Git and must never be committed.

3. Start the app:

   ```
   docker compose up -d
   ```

   The first start takes around 40 seconds while MySQL sets itself up. The backend waits until the database reports healthy.

4. Create the database tables:

   ```
   docker compose exec backend python manage.py migrate
   ```

5. Check it works by opening http://localhost:8000/api/health. You should see `{"status": "ok"}`.

## Everyday commands

| Task | Command |
|---|---|
| Run the tests | `docker compose exec backend pytest` |
| Lint | `docker compose exec backend ruff check .` |
| Check formatting | `docker compose exec backend ruff format --check .` |
| Apply formatting | `docker compose exec backend ruff format .` |
| View backend logs | `docker compose logs backend --tail 50` |
| Stop everything | `docker compose down` |
| Reset the local database | `docker compose down -v` (this deletes all local data) |

If you change the passwords in `.env` after the database was first created, run `docker compose down -v` so the database is recreated with the new values.

## Project layout

```
backend/    Django project (config/ holds settings, URLs and the health endpoint)
docker/     Scripts MySQL runs the first time it creates a database
.github/    GitHub Actions workflow
```

## How changes are made

`main` is protected. Every change goes through a pull request, and the `backend` check (lint, format, tests, dependency audit) must pass before it can be merged.