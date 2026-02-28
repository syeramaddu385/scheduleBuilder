# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ScheduleBuilder is a FastAPI backend that serves UNC course and section search endpoints. It currently reads directly from CSV files (not the database) at runtime. SQLAlchemy models and Alembic migrations exist but the database integration into the API endpoints is not yet complete.

## Commands

All backend commands must be run from `backend/` (the server uses a relative path `data/unc_all_sections_spring.csv`).

**Setup:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Alembic and SQLAlchemy/psycopg are not in requirements.txt yet — install separately if needed:
# pip install alembic sqlalchemy psycopg
```

**Start PostgreSQL:**
```bash
# From the repo root
docker compose up -d
```

**Run the API server:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

**Database migrations (Alembic):**
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic history
```

**Re-scrape UNC course data:**
```bash
cd backend
python data/scrapeuncsections.py        # generates unc_all_sections_spring.csv
python data/cleanup_prof_class.py       # generates prof_class_aggregates_cleaned.csv
```

## Architecture

**Current data flow (CSV-based):**
- `main.py` loads `data/unc_all_sections_spring.csv` into a Pandas DataFrame at startup
- `GET /courses?q=<query>` searches the DataFrame for matching `CourseKey` values (returns up to 50)
- `GET /sections?course=COMP+210` returns all sections for a course with parsed schedule fields
- Schedule strings like `"MWF 10:10 AM-11:00 AM"` are parsed into `days`, `start_min`, `end_min` (minutes from midnight)

**Database layer (defined but not yet wired to endpoints):**
- `app/db.py` — SQLAlchemy engine + `SessionLocal` + `Base` (DeclarativeBase), reads `DATABASE_URL` from `.env`
- `app/models.py` — `courses` and `sections` ORM models with indexes on searchable fields
- `alembic/` — migration tooling; `env.py` imports `Base` and `app.models` but `target_metadata` is still `None` (must be set to `Base.metadata` to enable autogenerate)

**Database credentials (docker-compose):**
- Host: `localhost:5432`, DB: `schedulebuilder`, user/pass: `schedule/schedule`
- `DATABASE_URL=postgresql+psycopg://schedule:schedule@localhost:5432/schedulebuilder`

## Key Known Issues

- `alembic/env.py` line 33: `target_metadata = None` must be changed to `target_metadata = Base.metadata` before `alembic revision --autogenerate` will detect model changes.
- SQLAlchemy and Alembic are missing from `requirements.txt`.
- `app/models.py` has a broken back-reference: `sections.course` references `"Course"` (capitalized) but the class is named `courses` (lowercase) — this will cause a relationship error when the ORM is used.
