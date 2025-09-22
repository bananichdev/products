import json
from pathlib import Path

import sqlalchemy as sa
from alembic import op
from sqlalchemy import ColumnClause


def insert_json_data(directory: str, file_name: str, table_name: str, columns: list[ColumnClause]) -> None:
    """Вставка данных в БД из json."""
    with open(Path(__file__).parent / "seed" / directory / file_name, encoding="utf-8") as file:
        json_data = json.load(file)
    table = sa.table(table_name, *columns)
    op.bulk_insert(table, json_data)


def clear_table(table_name: str) -> None:
    op.execute(f"DELETE FROM {table_name}")  # noqa: S608
