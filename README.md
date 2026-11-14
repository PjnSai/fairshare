# FairShare

A shared expense splitter: create groups, split bills equally or by custom amounts, see who owes what, and track payments.

**Status:** work in progress. The backend and frontend foundations are in place; the splitting logic is next.

## Tech stack

- **Backend:** Django 5.2 LTS on Python 3.14, with Django REST Framework
- **Database:** MySQL 8.4 LTS
- **Frontend:** Next.js 16 with React 19, TypeScript and Tailwind CSS, on Node.js 26 LTS
- **Local environment:** Docker Compose runs the backend and database; the frontend runs directly with Node
- **Checks:** on every pull request, GitHub Actions runs ruff, pytest and pip-audit for the backend, and ESLint, a type check, a build and an npm audit for the frontend

## Getting started

You need **Git**, **Docker Desktop** (open and running) and **Node.js 26** (LTS).

### Backend and database

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

3. Start the backend and database:

   ```
   docker compose up -d
   ```

   The first start takes around 40 seconds while MySQL sets itself up. The backend waits until the database reports healthy.

4. Create the database tables:

   ```
   docker compose exec backend python manage.py migrate
   ```

5. Check it works by opening http://localhost:8420/api/health. You should see `{"status": "ok"}`.

### Frontend

1. Install the packages exactly as locked:

   ```
   cd frontend
   npm ci
   ```

2. Start the dev server:

   ```
   npm run dev
   ```

3. Open http://localhost:3420. The frontend is not connected to the backend yet.

## Ports

| Service                       | Port |
| ----------------------------- | ---- |
| Backend (Django)              | 8420 |
| Frontend (Next.js)            | 3420 |
| MySQL (from your own machine) | 3426 |

These are deliberately unusual so FairShare can run next to other projects. To change the backend or database port, set `BACKEND_PORT` or `DB_HOST_PORT` in `.env`.

## Everyday commands

| Task                                       | Command                                                |
| ------------------------------------------ | ------------------------------------------------------ |
| Backend tests                              | `docker compose exec backend pytest`                   |
| Backend lint                               | `docker compose exec backend ruff check .`             |
| Backend format check                       | `docker compose exec backend ruff format --check .`    |
| Backend format                             | `docker compose exec backend ruff format .`            |
| Backend logs                               | `docker compose logs backend --tail 50`                |
| Frontend lint (in `frontend/`)             | `npm run lint`                                         |
| Frontend type check (in `frontend/`)       | `npm run typecheck`                                    |
| Frontend production build (in `frontend/`) | `npm run build`                                        |
| Stop the backend and database              | `docker compose down`                                  |
| Reset the local database                   | `docker compose down -v` (this deletes all local data) |

If you change the passwords in `.env` after the database was first created, run `docker compose down -v` so the database is recreated with the new values.

## Project layout

```
backend/    Django project (config/ holds settings, URLs and the health endpoint)
frontend/   Next.js app (pages live in src/app)
docker/     Scripts MySQL runs the first time it creates a database
.github/    GitHub Actions workflow
```

## How changes are made

`main` is protected. Every change goes through a pull request, and both the `backend` and `frontend` checks must pass before it can be merged.
