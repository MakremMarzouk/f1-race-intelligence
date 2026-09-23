import logging
from fastapi import APIRouter, HTTPException, Path
from app.services.f1_service import F1DataService
from app.services.analysis_service import RaceAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/races", tags=["races"])


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