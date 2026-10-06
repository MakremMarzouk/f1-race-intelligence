from app.database import models  # noqa: F401
from app.database.db import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)