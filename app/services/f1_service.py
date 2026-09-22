import os
from pathlib import Path
from typing import Any

import fastf1


class F1DataService:
    """Fetches and normalizes completed race results from FastF1."""

    def __init__(self, cache_dir: str | None = None):
        configured_cache_dir = cache_dir or os.getenv(
            "F1_CACHE_DIR",
            "f1_cache",
        )

        self.cache_dir = Path(configured_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        fastf1.Cache.enable_cache(str(self.cache_dir))

    def get_race_results(
        self,
        year: int,
        round_number: int,
    ) -> dict[str, Any]:
        """Load one race and return only normalized result fields."""

        session = fastf1.get_session(year, round_number, "R")
        session.load(
            laps=False,
            telemetry=False,
            weather=False,
            messages=False,
        )

        if session.results.empty:
            raise ValueError(
                f"No race results found for year={year}, round={round_number}."
            )

        return {
            "race": {
                "year": year,
                "round": round_number,
                "name": str(session.event["EventName"]),
                "location": str(session.event["Location"]),
                "country": str(session.event["Country"]),
            },
            "results": [
                {
                    "driver": str(result["FullName"]),
                    "abbreviation": str(result["Abbreviation"]),
                    "team": str(result["TeamName"]),
                    "grid_position": self._optional_int(
                        result["GridPosition"]
                    ),
                    "finish_position": self._optional_int(
                        result["Position"]
                    ),
                    "status": str(result["Status"]),
                    "points": float(result["Points"]),
                }
                for _, result in session.results.iterrows()
            ],
        }

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None:
            return None

        try:
            if value != value:  # Handles missing pandas values (NaN).
                return None

            return int(value)
        except (TypeError, ValueError):
            return None