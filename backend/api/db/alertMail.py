from psycopg2.extensions import QueryCanceledError
from psycopg2 import OperationalError
from psycopg2 import extras
import psycopg2

from common.logging_setup import setup_logger, log_event, DurationTimer
from .connection import get_db_connection

logger = setup_logger(service="api", module="db.alertMail")

def get_alert_email():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email FROM alert_emails LIMIT 1")
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None
    except psycopg2.Error as e:
        log_event(logger, "ERROR", "db.error.get_email", error=str(e))
        return None
    finally:
        if conn:
            conn.close()

def set_alert_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM alert_emails")
    cur.execute("INSERT INTO alert_emails (email) VALUES (%s)", (email,))
    conn.commit()
    cur.close()
    conn.close()
    
