from psycopg2.extensions import QueryCanceledError
from psycopg2 import OperationalError
from psycopg2 import extras
import psycopg2
from datetime import datetime

from common.logging_setup import setup_logger, log_event, DurationTimer
from .connection import get_db_connection

logger = setup_logger(service="api", module="db.sendAlertMail")

def is_alert_active(device, metric, mail_type):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM alert_cooldowns WHERE device=%s AND metric=%s AND mail_type=%s",
        (device, metric, mail_type)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row)

def set_alert_active(device, metric, mail_type):
    now = datetime.utcnow()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO alert_cooldowns (device, metric, mail_type, last_sent) VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (device, metric, mail_type) DO UPDATE SET last_sent = EXCLUDED.last_sent",
        (device, metric, mail_type, now)
    )
    conn.commit()
    cur.close()
    conn.close()

def reset_alert(device, metric, mail_type):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM alert_cooldowns WHERE device=%s AND metric=%s AND mail_type=%s",
        (device, metric, mail_type)
    )
    conn.commit()
    cur.close()
    conn.close()