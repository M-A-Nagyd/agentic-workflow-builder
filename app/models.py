from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
from app.database import Base


# =================================================
# Workflow
# =================================================

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # 🔑 MUST match Step.workflow
    steps = relationship(
        "Step",
        back_populates="workflow",
        cascade="all, delete-orphan"
    )

    runs = relationship(
        "Run",
        back_populates="workflow",
        cascade="all, delete-orphan"
    )


# =================================================
# Step
# =================================================

class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)

    model = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    criteria_type = Column(String, nullable=False)

    # Stored as JSON string
    criteria_value = Column(Text, nullable=True)

    max_retries = Column(Integer, nullable=False, default=2)

    # 🔑 THIS WAS MISSING / MISMATCHED
    workflow = relationship(
        "Workflow",
        back_populates="steps"
    )


# =================================================
# Run
# =================================================

class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)

    status = Column(String, nullable=False)

    workflow = relationship(
        "Workflow",
        back_populates="runs"
    )

    logs = relationship(
        "RunLog",
        back_populates="run",
        cascade="all, delete-orphan"
    )


# =================================================
# RunLog
# =================================================

class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)

    step = Column(Integer, nullable=False)
    attempt = Column(Integer, nullable=False)

    passed = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)

    error_type = Column(String, nullable=True)
    error = Column(Text, nullable=True)

    run = relationship(
        "Run",
        back_populates="logs"
    )
