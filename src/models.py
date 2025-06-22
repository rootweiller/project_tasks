import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskList(Base):
    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tasks = relationship("Task", back_populates="task_list", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.LOW)
    task_list_id = Column(Integer, ForeignKey("task_lists.id"))
    task_list = relationship("TaskList", back_populates="tasks")