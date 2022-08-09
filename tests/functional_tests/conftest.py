from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.db.db_sqlalchemy import BaseModel
from src.db.tools.db_operations import PsqlDatabaseConnection, DatabaseOperation
from src.api.factory_app import create_app
from src.config import get_settings
from src.api.dependencies.db import get_db
from src.utils.db_populating.inserting_data_into_db import insert_data_to_db

from tests.functional_tests.test_data import users_json, tables_json, schedules_json, order_json
from tests.functional_tests.utils import (get_superuser_token_headers,
                                          get_client1_token_headers,
                                          get_client2_token_headers)

setting = get_settings()

db_config = setting.TEST_DATABASE
URL = setting.get_test_database_url()
engine = create_engine(URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    connection = engine.connect()

    # begin a non-ORM transaction
    connection.begin()

    # bind an individual Session to the connection
    db = Session(bind=connection)

    yield db

    db.rollback()
    connection.close()


@pytest.fixture(scope="package", autouse=True)
def create_test_db():
    with PsqlDatabaseConnection() as conn:
        database = DatabaseOperation(connection=conn,
                                     db_name=db_config['db_name'],
                                     user_name=db_config['username'],
                                     user_password=db_config['user_password'])
        database.drop_all()
        database.create_all()
        BaseModel.metadata.create_all(bind=engine)
        insert_data_to_db(users_json, tables_json, schedules_json, order_json, TestingSessionLocal)


@pytest.fixture(scope='session')
def client():
    test_app = create_app(with_logger=False)
    test_app.dependency_overrides[get_db] = override_get_db
    return TestClient(test_app)


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def confirmed_client_token_headers(client: TestClient) -> Dict[str, str]:
    return get_client1_token_headers(client)


@pytest.fixture(scope="module")
def unconfirmed_client_token_headers(client: TestClient) -> Dict[str, str]:
    return get_client2_token_headers(client)
