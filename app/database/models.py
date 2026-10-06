from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (
        UniqueConstraint("year", "round_number", name="uq_race_year_round"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer)
    round_number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    results: Mapped[list["RaceResult"]] = relationship(
        back_populates="race",
        cascade="all, delete-orphan",
    )


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    abbreviation: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255))

    results: Mapped[list["RaceResult"]] = relationship(
        back_populates="driver",
    )


class RaceResult(Base):
    __tablename__ = "race_results"
    __table_args__ = (
        UniqueConstraint(
            "race_id",
            "driver_id",
            name="uq_race_result_race_driver",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(
        ForeignKey("races.id", ondelete="CASCADE"),
    )
    driver_id: Mapped[int] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"),
    )
    team_name: Mapped[str] = mapped_column(String(255))
    grid_position: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    finish_position: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(255))
    points: Mapped[float] = mapped_column()
    fastest_lap_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    race: Mapped["Race"] = relationship(back_populates="results")
    driver: Mapped["Driver"] = relationship(back_populates="results")


class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_name: Mapped[str] = mapped_column(String(255))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )