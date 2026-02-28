"""
load_data.py — Bulk-inserts CSV data into PostgreSQL.

Run from backend/:
    python data/load_data.py
"""

import sys
import os

# Make sure `app/` is on the path when running as a script from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from app.db import SessionLocal
from app.models import courses, sections, professor_ratings


def make_name_key(full_name: str) -> str:
    """Reduce 'First Middle Last' to 'first last' for fuzzy joining."""
    parts = full_name.strip().split()
    if len(parts) < 2:
        return full_name.strip().lower()
    return f"{parts[0]} {parts[-1]}".lower()


def parse_schedule(sched):
    """Parse 'MWF 10:10 AM-11:00 AM' into (days, start_min, end_min)."""
    if not sched or str(sched).strip() in ("", "nan"):
        return None, None, None

    parts = str(sched).strip().split(" ", 1)
    if len(parts) != 2:
        return None, None, None

    days = parts[0].strip()
    time_part = parts[1].strip()

    times = time_part.split("-", 1)
    if len(times) != 2:
        return days, None, None

    try:
        s = datetime.strptime(times[0].strip(), "%I:%M %p")
        e = datetime.strptime(times[1].strip(), "%I:%M %p")
        return days, s.hour * 60 + s.minute, e.hour * 60 + e.minute
    except ValueError:
        return days, None, None


def load_courses_and_sections(db):
    courses_exist = db.query(courses).first() is not None
    sections_exist = db.query(sections).first() is not None

    if courses_exist and sections_exist:
        print("Courses and sections tables already have data — skipping.")
        return

    df = pd.read_csv("data/unc_all_sections_spring.csv")
    df["Subject"] = df["Subject"].astype(str)
    df["Catalog Number"] = df["Catalog Number"].astype(str)
    df["CourseKey"] = df["Subject"] + " " + df["Catalog Number"]
    df["NormalizedCourseKey"] = df["CourseKey"].str.lower().str.replace(" ", "", regex=False)

    # Build course_map from existing rows or insert new ones
    course_map = {}
    if not courses_exist:
        unique = df[["Subject", "Catalog Number", "CourseKey", "NormalizedCourseKey"]].drop_duplicates("NormalizedCourseKey")
        print(f"Inserting {len(unique)} courses...")
        for _, row in unique.iterrows():
            c = courses(
                subject=row["Subject"],
                catalog_number=row["Catalog Number"],
                course_key=row["CourseKey"],
                normalized_course_key=row["NormalizedCourseKey"],
            )
            db.add(c)
            course_map[row["NormalizedCourseKey"]] = c
        db.flush()
    else:
        print("Courses already loaded — building map from DB...")
        for c in db.query(courses).all():
            course_map[c.normalized_course_key] = c

    if not sections_exist:
        print(f"Inserting {len(df)} sections...")
        for _, row in df.iterrows():
            nck = row["NormalizedCourseKey"]
            parent = course_map.get(nck)
            if parent is None:
                continue

            sched = row.get("Schedule")
            days, start_min, end_min = parse_schedule(sched)

            s = sections(
                course_id=parent.id,
                class_section=str(row.get("Class Section") or ""),
                schedule_raw=str(sched) if pd.notna(sched) else None,
                instructor_name=str(row.get("Instructor_Normalized") or "") or None,
                days=days,
                start_min=start_min,
                end_min=end_min,
            )
            db.add(s)

    db.commit()
    print("Courses and sections committed.")


def load_professor_ratings(db):
    if db.query(professor_ratings).first():
        print("Professor ratings table already has data — skipping.")
        return

    df = pd.read_csv("data/prof_class_aggregates_cleaned.csv")

    def to_bool(val):
        if pd.isna(val):
            return None
        return str(val).strip().lower() in ("true", "1", "yes")

    print(f"Inserting {len(df)} professor rating rows...")
    for _, row in df.iterrows():
        raw_name = str(row.get("Instructor_Name") or "")
        r = professor_ratings(
            instructor_name=raw_name,
            name_key=make_name_key(raw_name) if raw_name else None,
            subject=str(row.get("Subject") or ""),
            catalog_number=str(row.get("Catalog Number") or ""),
            num_ratings=int(row["num_ratings"]) if pd.notna(row.get("num_ratings")) else None,
            avg_quality=float(row["avg_quality"]) if pd.notna(row.get("avg_quality")) else None,
            avg_difficulty=float(row["avg_difficulty"]) if pd.notna(row.get("avg_difficulty")) else None,
            would_take_again_pct=float(row["would_take_again_pct"]) if pd.notna(row.get("would_take_again_pct")) else None,
            attendance_mandatory=to_bool(row.get("attendance_mandatory")),
            is_online=to_bool(row.get("is_online")),
        )
        db.add(r)

    db.commit()
    print("Professor ratings committed.")


def main():
    db = SessionLocal()
    try:
        load_courses_and_sections(db)
        load_professor_ratings(db)
    finally:
        db.close()
    print("Done!")


if __name__ == "__main__":
    main()
