import re
from collections import defaultdict
from typing import Any


class RaceAnalysisService:
    """Calculates deterministic race facts from normalized race results."""

    def analyze(self, race_data: dict[str, Any]) -> dict[str, Any]:
        results = race_data.get("results", [])

        if not results:
            raise ValueError("Race data has no results.")

        classified_results = sorted(
            (
                result
                for result in results
                if result.get("finish_position") is not None
            ),
            key=lambda result: result["finish_position"],
        )

        winner = self._find_winner(classified_results)
        position_changes = self._calculate_position_changes(
            classified_results
        )

        return {
            "race": race_data["race"],
            "winner": winner["driver"],
            "podium": [
                result["driver"] for result in classified_results[:3]
            ],
            "position_changes": position_changes,
            "biggest_mover": self._find_biggest_mover(position_changes),
            "fastest_lap": self._find_fastest_lap(results),
            "dnfs": self._find_dnfs(results),
            "driver_points": {
                result["driver"]: result["points"] for result in results
            },
            "constructor_points": self._calculate_constructor_points(
                results
            ),
        }

    @staticmethod
    def _find_winner(
        classified_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        for result in classified_results:
            if result["finish_position"] == 1:
                return result

        raise ValueError("Race data has no winner.")

    @staticmethod
    def _calculate_position_changes(
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        changes = []

        for result in results:
            start_position = result.get("grid_position")
            finish_position = result.get("finish_position")

            if not start_position or not finish_position:
                continue

            changes.append(
                {
                    "driver": result["driver"],
                    "start_position": start_position,
                    "finish_position": finish_position,
                    "positions_gained": (
                        start_position - finish_position
                    ),
                }
            )

        return changes

    @staticmethod
    def _find_biggest_mover(
        position_changes: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not position_changes:
            return None

        return sorted(
            position_changes,
            key=lambda change: (
                -change["positions_gained"],
                change["finish_position"],
                change["driver"],
            ),
        )[0]

    @staticmethod
    def _find_fastest_lap(
        results: list[dict[str, Any]],
    ) -> dict[str, str] | None:
        drivers_with_lap_times = [
            result
            for result in results
            if result.get("fastest_lap_ms") is not None
        ]

        if not drivers_with_lap_times:
            return None

        fastest = min(
            drivers_with_lap_times,
            key=lambda result: (
                result["fastest_lap_ms"],
                result["driver"],
            ),
        )

        return {
            "driver": fastest["driver"],
            "time": RaceAnalysisService._format_lap_time(
                fastest["fastest_lap_ms"]
            ),
        }

    @staticmethod
    def _find_dnfs(
        results: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        return [
            {
                "driver": result["driver"],
                "status": result["status"],
            }
            for result in results
            if not RaceAnalysisService._is_classified(result["status"])
        ]

    @staticmethod
    def _is_classified(status: str) -> bool:
        normalized_status = status.strip().casefold()

        return normalized_status in {"finished", "lapped"} or bool(
            re.fullmatch(r"\+\d+ laps?", normalized_status)
        )

    @staticmethod
    def _calculate_constructor_points(
        results: list[dict[str, Any]],
    ) -> dict[str, float]:
        constructor_points: defaultdict[str, float] = defaultdict(float)

        for result in results:
            constructor_points[result["team"]] += result["points"]

        return dict(constructor_points)

    @staticmethod
    def _format_lap_time(lap_time_ms: int) -> str:
        minutes, remaining_ms = divmod(lap_time_ms, 60_000)
        seconds, milliseconds = divmod(remaining_ms, 1_000)

        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"