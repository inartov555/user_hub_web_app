# Testing Guide

## Note:

The unit tests are embedded to GitHub actions and are run automatically on every commit

## Backend (Django + DRF)

Uses Django's test runner.

```bash
cd backend
export DJANGO_SETTINGS_MODULE=core.settings
python manage.py migrate
python manage.py test
```

## Frontend (Vite + React + Vitest)

```bash
cd frontend
npm i
npm run test
```

The test environment is jsdom and uses React Testing Library.
