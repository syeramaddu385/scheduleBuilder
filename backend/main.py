from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import SessionLocal
from app.models import courses, sections, professor_ratings


def make_name_key(full_name: str | None) -> str | None:
    """Reduce 'First Middle Last' to 'first last' for fuzzy joining."""
    if not full_name:
        return None
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name.strip().lower()
    return f"{parts[0]} {parts[-1]}".lower()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Yield a database session and close it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/courses")
def get_courses(q: str = Query("", description="Search like 'comp' or '210'"), db: Session = Depends(get_db)):
    q_normalized = q.strip().lower().replace(" ", "")

    query = db.query(courses.course_key)

    if q_normalized:
        query = query.filter(courses.normalized_course_key.contains(q_normalized))

    results = query.order_by(courses.course_key).limit(50).all()
    return {"courses": [row.course_key for row in results]}


@app.get("/sections")
def get_sections(course: str = Query(..., description="Course key like 'COMP 210'"), db: Session = Depends(get_db)):
    course_normalized = course.strip().lower().replace(" ", "")

    course_row = db.query(courses).filter(courses.normalized_course_key == course_normalized).first()
    if not course_row:
        raise HTTPException(status_code=404, detail=f"Course '{course}' not found")

    rows = (
        db.query(sections, professor_ratings)
        .outerjoin(
            professor_ratings,
            (func.lower(sections.instructor_name) == func.lower(professor_ratings.instructor_name))
            & (professor_ratings.subject == course_row.subject)
            & (professor_ratings.catalog_number == course_row.catalog_number),
        )
        .filter(sections.course_id == course_row.id)
        .all()
    )

    out = []
    for section, rating in rows:
        out.append({
            "course": course_row.course_key,
            "section": section.class_section,
            "schedule": section.schedule_raw,
            "days": section.days,
            "start_min": section.start_min,
            "end_min": section.end_min,
            "instructor": section.instructor_name,
            "avg_quality": rating.avg_quality if rating else None,
            "avg_difficulty": rating.avg_difficulty if rating else None,
            "would_take_again_pct": rating.would_take_again_pct if rating else None,
        })

    return {"sections": out}


@app.get("/professors/{instructor_name}")
def get_professor(instructor_name: str, db: Session = Depends(get_db)):
    rows = (
        db.query(professor_ratings)
        .filter(func.lower(professor_ratings.instructor_name) == instructor_name.strip().lower())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"Professor '{instructor_name}' not found")

    # Average across all courses they teach
    avg_quality = sum(r.avg_quality for r in rows if r.avg_quality) / len(rows)
    avg_difficulty = sum(r.avg_difficulty for r in rows if r.avg_difficulty) / len(rows)

    return {
        "instructor_name": rows[0].instructor_name,
        "courses_taught": [f"{r.subject} {r.catalog_number}" for r in rows],
        "avg_quality": round(avg_quality, 2),
        "avg_difficulty": round(avg_difficulty, 2),
        "num_ratings": rows[0].num_ratings,
        "would_take_again_pct": rows[0].would_take_again_pct,
    }
