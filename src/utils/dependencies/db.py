from typing import Generator

from src.db.db_sqlalchemy import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        # print('Opening db connection...')
        yield db
        # db.commit()
    # except Exception:
    #     db.rollback()
    finally:
        # print('Closing db connection...')
        db.close()
