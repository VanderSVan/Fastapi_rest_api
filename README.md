```commandline
alembic init migrations
```

```commandline
alembic revision --autogenerate -m "first_migration"
```

```commandline
alembic upgrade head
```

```commandline
py -m src -h
```

```commandline
uvicorn src.app:app --reload
```

