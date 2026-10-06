import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.services.analysis_service import RaceAnalysisService
from app.database.db import get_db
from app.services.f1_service import F1DataService
from app.services.persistence_service import RacePersistenceService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/races", tags=["races"])


@router.get("/latest-completed")
def get_latest_completed_race(
    year: int | None = Query(default=None, ge=2018),
):
    try:
        return F1DataService().get_latest_completed_race(year)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception:
        logger.exception("Could not determine the latest completed race")
        raise HTTPException(
            status_code=502,
            detail="Race data provider is unavailable.",
        )


@router.get("/{year}/{round_number}/results")
def get_race_results(
    year: int = Path(ge=2018),
    round_number: int = Path(ge=1),
):
    try:
        return F1DataService().get_race_results(year, round_number)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception:
        logger.exception(
            "Could not retrieve race results for year=%s round=%s",
            year,
            round_number,
        )
        raise HTTPException(
            status_code=502,
            detail="Race data provider is unavailable.",
        )


@router.get("/{year}/{round_number}/analysis")
def get_race_analysis(
    year: int = Path(ge=2018),
    round_number: int = Path(ge=1),
):
    try:
        race_data = F1DataService().get_race_results(
            year,
            round_number,
        )
        return RaceAnalysisService().analyze(race_data)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception:
        logger.exception(
            "Could not analyze race for year=%s round=%s",
            year,
            round_number,
        )
        raise HTTPException(
            status_code=502,
            detail="Race analysis could not be completed.",
        )


@router.post("/{year}/{round_number}/ingest")
def ingest_race(
    year: int = Path(ge=2018),
    round_number: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    try:
        race_data = F1DataService().get_race_results(
            year,
            round_number,
        )
        race, created = RacePersistenceService().save_race(
            race_data,
            db,
        )

        return {
            "race_id": race.id,
            "created": created,
            "race": {
                "year": race.year,
                "round": race.round_number,
                "name": race.name,
            },
        }
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception:
        logger.exception(
            "Could not ingest race for year=%s round=%s",
            year,
            round_number,
        )
        raise HTTPException(
            status_code=502,
            detail="Race ingestion could not be completed.",
        )
