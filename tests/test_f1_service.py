from unittest.mock import patch

import pandas as pd

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