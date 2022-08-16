import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


@pytest.fixture(scope='package')
def app():
    test_app = create_app()
    return test_app


@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session_ = TestingSessionLocal(bind=connection)

    yield session_

    session_.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope='function')
def client(app, db_session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        yield client


def _simple_client():
    """This client is required to generate tokens"""
    test_app = create_app(with_logger=False)
    return TestClient(test_app)


superuser_token = get_superuser_token_headers(_simple_client())
confirmed_client_token = get_client1_token_headers(_simple_client())
unconfirmed_client_token = get_client2_token_headers(_simple_client())
