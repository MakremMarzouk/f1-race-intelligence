from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Driver, Race, RaceResult


class RacePersistenceService:
    """Persists normalized race data without duplicate race ingestion."""

    def save_race(
        self,
        race_data: dict[str, Any],
        db: Session,
    ) -> tuple[Race, bool]:
        race_info = race_data["race"]

        existing_race = db.scalar(
            select(Race).where(
                Race.year == race_info["year"],
                Race.round_number == race_info["round"],
            )
        )

        if existing_race:
            return existing_race, False

        race = Race(
            year=race_info["year"],
            round_number=race_info["round"],
            name=race_info["name"],
            location=race_info.get("location"),
            country=race_info.get("country"),
        )
        db.add(race)
        db.flush()

        for result in race_data["results"]:
            driver = db.scalar(
                select(Driver).where(
                    Driver.abbreviation == result["abbreviation"]
                )
            )

            if not driver:
                driver = Driver(
                    abbreviation=result["abbreviation"],
                    full_name=result["driver"],
                )
                db.add(driver)
                db.flush()

            db.add(
                RaceResult(
                    race_id=race.id,
                    driver_id=driver.id,
                    team_name=result["team"],
                    grid_position=result["grid_position"],
                    finish_position=result["finish_position"],
                    status=result["status"],
                    points=result["points"],
                    fastest_lap_ms=result.get("fastest_lap_ms"),
                )
            )

        db.commit()
        db.refresh(race)

        return race, True