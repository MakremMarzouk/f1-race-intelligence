from app.services.analysis_service import RaceAnalysisService


def test_analyze_calculates_race_facts():
    race_data = {
        "race": {
            "year": 2024,
            "round": 1,
            "name": "Example Grand Prix",
        },
        "results": [
            {
                "driver": "Driver One",
                "team": "Team Alpha",
                "grid_position": 1,
                "finish_position": 1,
                "status": "Finished",
                "points": 25.0,
                "fastest_lap_ms": 90000,
            },
            {
                "driver": "Driver Two",
                "team": "Team Beta",
                "grid_position": 10,
                "finish_position": 2,
                "status": "Finished",
                "points": 18.0,
                "fastest_lap_ms": 91000,
            },
            {
                "driver": "Driver Three",
                "team": "Team Alpha",
                "grid_position": 4,
                "finish_position": 3,
                "status": "Finished",
                "points": 15.0,
                "fastest_lap_ms": 90500,
            },
            {
                "driver": "Driver Four",
                "team": "Team Beta",
                "grid_position": 2,
                "finish_position": 4,
                "status": "+1 Lap",
                "points": 12.0,
                "fastest_lap_ms": 93000,
            },
            {
                "driver": "Driver Five",
                "team": "Team Gamma",
                "grid_position": 5,
                "finish_position": 5,
                "status": "Engine",
                "points": 0.0,
                "fastest_lap_ms": None,
            },
        ],
    }

    analysis = RaceAnalysisService().analyze(race_data)

    assert analysis["winner"] == "Driver One"
    assert analysis["podium"] == [
        "Driver One",
        "Driver Two",
        "Driver Three",
    ]
    assert analysis["biggest_mover"] == {
        "driver": "Driver Two",
        "start_position": 10,
        "finish_position": 2,
        "positions_gained": 8,
    }
    assert analysis["fastest_lap"] == {
        "driver": "Driver One",
        "time": "1:30.000",
    }
    assert analysis["dnfs"] == [
        {
            "driver": "Driver Five",
            "status": "Engine",
        }
    ]
    assert analysis["driver_points"]["Driver Three"] == 15.0
    assert analysis["constructor_points"] == {
        "Team Alpha": 40.0,
        "Team Beta": 30.0,
        "Team Gamma": 0.0,
    }


def test_lapped_drivers_are_not_dnfs():
    service = RaceAnalysisService()

    assert service._is_classified("Finished") is True
    assert service._is_classified("+1 Lap") is True
    assert service._is_classified("+2 Laps") is True
    assert service._is_classified("Engine") is False
    assert service._is_classified("Lapped") is True