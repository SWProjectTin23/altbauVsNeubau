import datetime
from decimal import Decimal


def serialize_row(row: dict) -> dict:
    """Converts Decimal and datetime for JSON compatibility."""
    result = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, (datetime.datetime, datetime.date)):
            result[k] = v.isoformat()
        else:
            result[k] = v
    return result

__all__ = ["serialize_row"]


