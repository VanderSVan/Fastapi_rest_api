from datetime import date, datetime as dt

from sqlalchemy.orm import Session

from src.api.models.table import TableModel
from src.api.crud_operations.table import TableOperation


def convert_ids_to_table_objs(table_ids: list[int], db: Session) -> list[TableModel]:
    """Converts integers to TableModel objects for nested model."""
    table_operation = TableOperation(db=db, user=None)
    return [table_operation.find_by_id_or_404(table_id) for table_id in table_ids]


def collect_new_tables_excluding_existing_ones(new_table_ids: list[int],
                                               existing_tables: list[TableModel],
                                               db: Session
                                               ) -> list[TableModel]:
    """Creates a list with new tables excluding existing ones."""
    table_operation = TableOperation(db=db, user=None)
    existing_table_ids: list[int] = [table_obj.id for table_obj in existing_tables]
    return [
        table_operation.find_by_id_or_404(table_id)
        for table_id in new_table_ids
        if table_id not in existing_table_ids
    ]


def get_table_ids_by_booking_time(start: dt | date,
                                  end: dt | date,
                                  db: Session
                                  ) -> list[int]:
    """Gets table ids by booking time."""
    table_operation = TableOperation(db=db, user=None)
    tables: list[TableModel] = table_operation.find_all_by_params(start_datetime=start,
                                                                  end_datetime=end)
    return [table.id for table in tables]
