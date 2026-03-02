from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class courses(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)

    subject: Mapped[str] = mapped_column(String, index = True) # "COMP"
    catalog_number: Mapped[str] = mapped_column(String, index = True) # "210"

    course_key: Mapped[str] = mapped_column(String, unique = True, index = True) # "COMP 210" 
    normalized_course_key: Mapped[str] = mapped_column(String, unique = True, index = True) # "comp210"

    sections = relationship("sections", back_populates="course")


class sections(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index = True)

    class_section: Mapped[str] = mapped_column(String)
    schedule_raw: Mapped[str] = mapped_column(String, nullable = True)
    instructor_name: Mapped[str] = mapped_column(String, nullable = True)

    days: Mapped[str] = mapped_column(String, nullable = True, index = True) # e.g. "MWF"
    start_min: Mapped[int] = mapped_column(Integer, nullable = True, index = True) # minutes from midnight
    end_min: Mapped[int] = mapped_column(Integer, nullable = True, index = True)
    # "first last" (no middle), lower-cased — matches professor_ratings.name_key
    name_key: Mapped[str] = mapped_column(String, nullable = True, index = True)

    course = relationship("courses", back_populates="sections")


class professor_ratings(Base):
    __tablename__ = "professor_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    instructor_name: Mapped[str] = mapped_column(String, index=True)
    # "first last" (no middle name/initial), lower-cased — used to join against sections
    name_key: Mapped[str] = mapped_column(String, index=True, nullable=True)
    subject: Mapped[str] = mapped_column(String)
    catalog_number: Mapped[str] = mapped_column(String)

    num_ratings: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_quality: Mapped[float] = mapped_column(Float, nullable=True)
    avg_difficulty: Mapped[float] = mapped_column(Float, nullable=True)
    would_take_again_pct: Mapped[float] = mapped_column(Float, nullable=True)
    attendance_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=True)