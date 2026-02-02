from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class courses(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)

    subject: Mapped[str] = mapped_column(String, index = True) # "COMP"
    catalog_number: Mapped[str] = mapped_column(String, index = True) # "210"

    course_key: Mapped[str] = mapped_column(String, unique = True, index = True) # "COMP 210" 
    normalized_course_key: Mapped[str] = mapped_column(String, unique = True, index = True) # "comp210"

    sections = relationship("Sections", back_populates="course")


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

    course = relationship("Course", back_populates="sections")