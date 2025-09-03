import os
import psycopg2
from dotenv import load_dotenv

from common.logging_setup import setup_logger, log_event, DurationTimer
from common.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationalError,
)


logger = setup_logger(service="api", module="db.connection")

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432"),
}


def check_db_config():
    missing = [k for k in ["host", "database", "user", "password"] if not DB_CONFIG[k]]
    if missing:
        log_event(logger, "ERROR", "db.config_missing", missing=",".join(missing))
        raise ValueError(
            f"Missing DB config values: {', '.join(missing)}. Please check your .env file or environment variables."
        )


def get_db_connection():
    check_db_config()
    t = DurationTimer().start()
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=int(DB_CONFIG["port"]),
        )
        log_event(
            logger, "INFO", "db.conn_ok", duration_ms=t.stop_ms(), host=DB_CONFIG["host"], db=DB_CONFIG["database"]
        )
        return conn
    except psycopg2.OperationalError as e:
        log_event(
            logger, "ERROR", "db.conn_operational_error", duration_ms=t.stop_ms(), host=DB_CONFIG["host"], db=DB_CONFIG["database"], error_type=e.__class__.__name__
        )
        raise DatabaseOperationalError("database operational error", details={"op": "connect"}) from e
    except psycopg2.Error as e:
        log_event(
            logger, "ERROR", "db.conn_fail", duration_ms=t.stop_ms(), host=DB_CONFIG["host"], db=DB_CONFIG["database"], error_type=e.__class__.__name__
        )
        raise DatabaseConnectionError("database connection failed", details={"op": "connect"}) from e


