from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Optional
from app.database import get_db, engine

router = APIRouter()


@router.get("/tables")
def list_tables():
    """List all tables in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}


@router.get("/tables/{table_name}")
def get_table_data(
    table_name: str,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all rows from a specific table with pagination"""
    # Validate table exists
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    # Get data
    result = db.execute(
        text(f'SELECT * FROM "{table_name}" LIMIT :limit OFFSET :offset'),
        {"limit": limit, "offset": offset}
    )
    rows = [dict(row._mapping) for row in result]

    # Get total count
    count_result = db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
    total = count_result.scalar()

    return {
        "table": table_name,
        "data": rows,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total
        }
    }


@router.get("/tables/{table_name}/schema")
def get_table_schema(table_name: str):
    """Get the schema/columns of a specific table"""
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    columns = inspector.get_columns(table_name)
    return {
        "table": table_name,
        "columns": [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"]
            }
            for col in columns
        ]
    }


@router.get("/tables/{table_name}/{record_id}")
def get_record_by_id(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific record by ID"""
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    # Try common ID column names
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    id_column = None
    for possible_id in ["id", "ID", f"{table_name}_id", f"{table_name}Id"]:
        if possible_id in columns:
            id_column = possible_id
            break

    if not id_column:
        raise HTTPException(status_code=400, detail="Could not determine ID column for this table")

    result = db.execute(
        text(f'SELECT * FROM "{table_name}" WHERE "{id_column}" = :id'),
        {"id": record_id}
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"table": table_name, "data": dict(row._mapping)}
