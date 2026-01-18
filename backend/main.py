from fastapi import FastAPI
from fastapi import Query
import pandas as pd
from datetime import datetime


app = FastAPI()

def parse_schedule(sched: str | None):
    if not sched:
        return None, None, None
    
    sched = str(sched).strip()

    if not sched:
        return None, None, None
    
    parts = sched.split(" ", 1)
    if len(parts) != 2:
        return None, None, None
    
    days = parts[0].strip()
    time_part = parts[1].strip()

    times = time_part.split("-", 1)
    if len(times) != 2:
        return None, None, None

    start_time = times[0].strip()
    end_time = times[1].strip()

    try:
        s = datetime.strptime(start_time, "%I:%M %p")
        e = datetime.strptime(end_time, "%I:%M %p")

        start_min = s.hour * 60 + s.minute
        end_min = e.hour * 60 + e.minute

        return days, start_min, end_min
    except ValueError:
        return days, None, None


DATA_PATH = "data/unc_all_sections_spring.csv"

df = pd.read_csv(DATA_PATH)

df["Subject"] = df["Subject"].astype(str)
df["Catalog Number"] = df["Catalog Number"].astype(str)

df["CourseKey"] = df["Subject"] + " " + df["Catalog Number"]
df["NormalizedCourseKey"] = df["CourseKey"].str.lower().str.replace(" ", "")

@app.get("/courses")
def courses(q: str = Query("", description="Search like 'comp' or '210'")):
    unique_courses = df[["CourseKey", "NormalizedCourseKey"]].drop_duplicates()
    
    q_normalized = q.strip().lower().replace(" ", "")

    if q_normalized:
        unique_courses = unique_courses[unique_courses["NormalizedCourseKey"].str.contains(q_normalized, na=False)]
    
    result = unique_courses["CourseKey"].tolist()
    result.sort()
    return {"courses": result[:50]}

@app.get("/sections")
def sections(course: str = Query(..., description="Course key like 'COMP 210'")):
    course_normalized = course.strip().lower().replace(" ", "")

    sub = df[df["NormalizedCourseKey"] == course_normalized].copy() # sub is a new dataframe consisting of all sections of inputted course

    sub = sub.where(pd.notna(sub), None) # converted NaN to None so converting to JSON is easier

    out = []

    for _,r in sub.iterrows():
        days, start_min, end_min = parse_schedule(r.get("Schedule"))

        out.append({
            "course": r.get("CourseKey"),
            "section": str(r.get("Class Section") or ""),
            "schedule": r.get("Schedule"),
            "days": days,
            "start_min": start_min,
            "end_min": end_min,
            "instructor": r.get("Instructor_Name")
        })

    return {"sections": out}

