import enum

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from app.core.enums import TaskPriority, TaskStatus
from app.db.database import Base


# USER MODEL -> 'users'
# User model representing the users table in the database
class User(Base):
    __tablename__ = "users"  # Table name

    # User attributes: id, fullname, email, password, is_active
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship: One user has many tasks
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Property: Count of tasks for the user
    @property
    def tasks_count(self):
        return len(self.tasks)

    # Property: Get user's first name from full name
    @property
    def first_name(self) -> str:
        return self.fullname.split(" ")[0]

    # String representation for debugging
    def __repr__(self):
        return f"<User(id={self.id}, fullname='{self.fullname}', email='{self.email}', is_active={self.is_active}, tasks_count={self.tasks_count})>"


# TASK MODEL -> 'tasks'
# Task model representing the tasks table in the database
class Task(Base):
    __tablename__ = "tasks"  # Table name

    # Task attributes: id, title, description, priority, status, created_at, due_date
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[enum.Enum] = mapped_column(Enum(TaskPriority), nullable=False)
    status: Mapped[enum.Enum] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Foreign key to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship: Task belongs to a user
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    # String representation for debugging
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status}, created_at={self.created_at}, due_date={self.due_date})>"
