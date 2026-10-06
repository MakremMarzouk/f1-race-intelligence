import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.database.db import Base
from app.database.models import Driver, Race, RaceResult
from app.services.persistence_service import RacePersistenceService


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_save_race_persists_results_and_prevents_duplicates(db):
    race_data = {
        "race": {
            "year": 2024,
            "round": 1,
            "name": "Example Grand Prix",
            "location": "Example Circuit",
            "country": "Example Country",
        },
        "results": [
            {
                "driver": "Driver One",
                "abbreviation": "ONE",
                "team": "Team Alpha",
                "grid_position": 1,
                "finish_position": 1,
                "status": "Finished",
                "points": 25.0,
                "fastest_lap_ms": 90000,
            },
            {
                "driver": "Driver Two",
                "abbreviation": "TWO",
                "team": "Team Beta",
                "grid_position": 2,
                "finish_position": 2,
                "status": "Finished",
                "points": 18.0,
                "fastest_lap_ms": 91000,
            },
        ],
    }

    service = RacePersistenceService()

    race, created = service.save_race(race_data, db)

    assert created is True
    assert race.id is not None
    assert db.scalar(select(func.count()).select_from(Race)) == 1
    assert db.scalar(select(func.count()).select_from(Driver)) == 2
    assert db.scalar(select(func.count()).select_from(RaceResult)) == 2

    same_race, created_again = service.save_race(race_data, db)

    assert created_again is False
    assert same_race.id == race.id
    assert db.scalar(select(func.count()).select_from(Race)) == 1
    assert db.scalar(select(func.count()).select_from(RaceResult)) == 2
