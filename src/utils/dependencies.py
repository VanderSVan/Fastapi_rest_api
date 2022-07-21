from typing import Generator

from src.db.db_sqlalchemy import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
        # db.commit()
    # except Exception:
    #     db.rollback()
    finally:
        db.close()
