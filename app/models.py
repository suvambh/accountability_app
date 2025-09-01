from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# Enums
class ResourceType(str, enum.Enum):
    video = "video"
    book = "book"
    notebook = "notebook"
    kaggle = "kaggle"
    code = "code"
    project = "project"

class Mode(str, enum.Enum):
    watch = "watch"
    read = "read"
    code = "code"

class Status(str, enum.Enum):
    in_progress = "in-progress"
    completed = "completed"
    stopped = "stopped"

class Outcome(str, enum.Enum):
    clear = "clear"
    confused = "confused"
    needs_review = "needs_review"
    breakthrough = "breakthrough"
    other = "other"

# Users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)

    logs = relationship("ActivityLog", back_populates="user")

# Resources
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ResourceType), nullable=False)
    link = Column(String, nullable=False)
    chapter_number = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    details = Column(String, nullable=True)    # ✅ renamed from metadata

    logs = relationship("ActivityLog", back_populates="resource")


# Activity Logs
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    chapter_number = Column(Integer, nullable=True)
    mode = Column(Enum(Mode), nullable=False)
    goal = Column(String, nullable=True)
    time_allocated = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    date = Column(Date, nullable=True)
    status = Column(Enum(Status), nullable=True)
    completion_percent = Column(Float, nullable=True)
    outcome = Column(Enum(Outcome), nullable=True)
    notes = Column(Text, nullable=True)
    xp_earned = Column(Integer, default=0)
    notes_file = Column(String, nullable=True)  # path to uploaded .md file
    
    user = relationship("User", back_populates="logs")
    resource = relationship("Resource", back_populates="logs")

# Badges
class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    condition = Column(String)  # stored as text/JSON for now
    icon = Column(String, nullable=True)

# User Badges
class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_date = Column(Date, nullable=True)
