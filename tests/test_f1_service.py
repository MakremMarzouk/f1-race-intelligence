from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd
import pytest
from app.services.f1_service import F1DataService


class FakeSession:
    event = {
        "EventName": "Example Grand Prix",
        "Location": "Example Circuit",
        "Country": "Example Country",
    }

    results = pd.DataFrame(
        [
            {
                "FullName": "Test Driver",
                "Abbreviation": "TST",
                "TeamName": "Test Team",
                "GridPosition": 3,
                "Position": 1,
                "Status": "Finished",
                "Points": 25,
            }
        ]
    )

    laps = pd.DataFrame(
        [
            {
                "Driver": "TST",
                "LapTime": pd.Timedelta(92608, unit="ms"),
                "Deleted": False,
                "FastF1Generated": False,
            }
        ]
    )

    def load(self, **kwargs):
        self.load_arguments = kwargs


def test_get_race_results_normalizes_fastf1_data(tmp_path):
    session = FakeSession()

    with (
        patch("app.services.f1_service.fastf1.Cache.enable_cache"),
        patch(
            "app.services.f1_service.fastf1.get_session",
            return_value=session,
        ) as get_session,
    ):
        service = F1DataService(cache_dir=str(tmp_path))
        race = service.get_race_results(2024, 1)

    get_session.assert_called_once_with(2024, 1, "R")
    assert session.load_arguments == {
        "laps": True,
        "telemetry": False,
        "weather": False,
        "messages": False,
    }
    assert race == {
        "race": {
            "year": 2024,
            "round": 1,
            "name": "Example Grand Prix",
            "location": "Example Circuit",
            "country": "Example Country",
        },
        "results": [
            {
                "driver": "Test Driver",
                "abbreviation": "TST",
                "team": "Test Team",
                "grid_position": 3,
                "finish_position": 1,
                "status": "Finished",
                "points": 25.0,
                "fastest_lap_ms": 92608,
            }
        ],
    }


def test_get_latest_completed_race_returns_most_recent_past_race(tmp_path):
    schedule = pd.DataFrame(
        [
            {
                "RoundNumber": 1,
                "EventName": "First Grand Prix",
                "Location": "First Circuit",
                "Country": "First Country",
                "Session5DateUtc": pd.Timestamp("2024-03-01 12:00:00"),
            },
            {
                "RoundNumber": 2,
                "EventName": "Second Grand Prix",
                "Location": "Second Circuit",
                "Country": "Second Country",
                "Session5DateUtc": pd.Timestamp("2024-03-10 12:00:00"),
            },
            {
                "RoundNumber": 3,
                "EventName": "Future Grand Prix",
                "Location": "Future Circuit",
                "Country": "Future Country",
                "Session5DateUtc": pd.Timestamp("2024-03-20 12:00:00"),
            },
        ]
    )

    with (
        patch("app.services.f1_service.fastf1.Cache.enable_cache"),
        patch(
            "app.services.f1_service.fastf1.get_event_schedule",
            return_value=schedule,
        ) as get_event_schedule,
        patch(
            "app.services.f1_service.fastf1.get_session",
            return_value=FakeSession(),
        ) as get_session,
    ):
        service = F1DataService(cache_dir=str(tmp_path))
        race = service.get_latest_completed_race(
            year=2024,
            now=datetime(2024, 3, 15, tzinfo=timezone.utc),
        )

    get_event_schedule.assert_called_once_with(2024, include_testing=False)
    get_session.assert_called_once_with(2024, 2, "R")
    assert race == {
        "year": 2024,
        "round": 2,
        "name": "Second Grand Prix",
        "location": "Second Circuit",
        "country": "Second Country",
        "race_start_utc": "2024-03-10T12:00:00",
    }


def test_latest_completed_race_skips_past_event_without_classification(tmp_path):
    schedule = pd.DataFrame(
        [
            {
                "RoundNumber": 1,
                "EventName": "Completed Grand Prix",
                "Location": "Completed Circuit",
                "Country": "Completed Country",
                "Session5DateUtc": pd.Timestamp("2024-03-01 12:00:00"),
            },
            {
                "RoundNumber": 2,
                "EventName": "Unfinished Grand Prix",
                "Location": "Unfinished Circuit",
                "Country": "Unfinished Country",
                "Session5DateUtc": pd.Timestamp("2024-03-10 12:00:00"),
            },
        ]
    )

    class UnclassifiedSession(FakeSession):
        results = pd.DataFrame(
            [
                {
                    "FullName": "Driver One",
                    "Abbreviation": "ONE",
                    "Position": float("nan"),
                }
            ]
        )

    completed_session = FakeSession()
    with (
        patch("app.services.f1_service.fastf1.Cache.enable_cache"),
        patch(
            "app.services.f1_service.fastf1.get_event_schedule",
            return_value=schedule,
        ),
        patch(
            "app.services.f1_service.fastf1.get_session",
            side_effect=[UnclassifiedSession(), completed_session],
        ) as get_session,
    ):
        service = F1DataService(cache_dir=str(tmp_path))
        race = service.get_latest_completed_race(
            year=2024,
            now=datetime(2024, 3, 15, tzinfo=timezone.utc),
        )

    assert race["round"] == 1
    assert get_session.call_args_list[0].args == (2024, 2, "R")
    assert get_session.call_args_list[1].args == (2024, 1, "R")
    assert completed_session.load_arguments == {
        "laps": False,
        "telemetry": False,
        "weather": False,
        "messages": False,
    }


def test_get_race_results_continues_when_lap_data_is_unavailable(tmp_path):
    from fastf1.exceptions import DataNotLoadedError

    class FakeSessionWithoutLaps(FakeSession):
        @property
        def laps(self):
            raise DataNotLoadedError("Lap timing data is unavailable.")

    session = FakeSessionWithoutLaps()

    with (
        patch("app.services.f1_service.fastf1.Cache.enable_cache"),
        patch(
            "app.services.f1_service.fastf1.get_session",
            return_value=session,
        ),
    ):
        service = F1DataService(cache_dir=str(tmp_path))
        race = service.get_race_results(2026, 16)

    assert race["race"]["year"] == 2026
    assert race["results"][0]["fastest_lap_ms"] is None


def test_get_race_results_rejects_nonempty_unclassified_entry_list(tmp_path):
    class UnclassifiedSession(FakeSession):
        results = pd.DataFrame(
            [
                {
                    "FullName": "Test Driver",
                    "Abbreviation": "TST",
                    "TeamName": "Test Team",
                    "GridPosition": 3,
                    "Position": float("nan"),
                    "Status": "NotStarted",
                    "Points": 0,
                }
            ]
        )

    with (
        patch("app.services.f1_service.fastf1.Cache.enable_cache"),
        patch(
            "app.services.f1_service.fastf1.get_session",
            return_value=UnclassifiedSession(),
        ),
    ):
        service = F1DataService(cache_dir=str(tmp_path))

        with pytest.raises(
            ValueError,
            match="Classified race results are not available",
        ):
            service.get_race_results(2026, 16)
