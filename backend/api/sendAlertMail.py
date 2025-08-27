import os
import datetime
from flask_restful import Resource
from flask import request
from .db_operations import get_db_connection
import smtplib
import psycopg2
from email.mime.text import MIMEText
from common.logging_setup import setup_logger, log_event

logger = setup_logger(service="api", module="sendAlertMail")

SMTP_HOST = os.getenv("GF_SMTP_HOST")
SMTP_USER = os.getenv("GF_SMTP_USER")
SMTP_PASSWORD = os.getenv("GF_SMTP_PASSWORD")
SMTP_FROM = os.getenv("GF_SMTP_FROM")
SMTP_PORT = os.getenv("GF_SMTP_PORT")
SMTP_FROM_NAME = os.getenv("GF_SMTP_FROM_NAME")


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
        # Hier wird der Datenbankfehler abgefangen
        log_event(logger, "ERROR", "db.error.get_email", error=str(e))
        return None
    finally:
        if conn:
            conn.close()

def send_mail(email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    if SMTP_FROM is None:
        raise ValueError("SMTP_FROM environment variable is not set")
    if SMTP_HOST is None:
        raise ValueError("SMTP_HOST environment variable is not set")
    msg["From"] = SMTP_FROM
    msg["To"] = email
    if SMTP_USER is None:
        raise ValueError("SMTP_USER environment variable is not set")
    if SMTP_PASSWORD is None:
        raise ValueError("SMTP_PASSWORD environment variable is not set")
    # Host and port separation
    if ":" in SMTP_HOST:
        host, port = SMTP_HOST.split(":")
        port = int(port)
    else:
        host = SMTP_HOST
        port = 465
    with smtplib.SMTP_SSL(host, port) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

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
    now = datetime.datetime.utcnow()
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

class SendAlertMail(Resource):
    def post(self):
        data = request.get_json(force=True)
        metric = data.get("metric")
        value = data.get("value")
        thresholds = data.get("thresholds")
        device = data.get("device")
        metric_units = {
            "Temperatur": "°C",
            "Luftfeuchtigkeit": "%",
            "Pollen": "µg/m³",
            "Feinstaub": "µg/m³"
        }
        unit = metric_units.get(metric, "")
        
        if not (metric and value is not None and thresholds and device):
            log_event(logger, "WARNING", "alert_mail.missing_parameters", data=data)
            return {"status": "error", "message": "Missing parameters"}, 400

        t = thresholds.get(metric)
        if not t:
            log_event(logger, "WARNING", "alert_mail.unknown_metric", data=data)
            return {"status": "error", "message": "Unknown metric"}, 400

        try:
            mail_type = None
            threshold_low = None
            threshold_high = None
            
            # Schwellenlogik
            if value < t.get("redLow", float("-inf")) or value > t.get("redHigh", float("inf")):
                mail_type = "hart"
                threshold_low = t.get("redLow", float("-inf"))
                threshold_high = t.get("redHigh", float("inf"))
            elif value < t.get("yellowLow", float("-inf")) or value > t.get("yellowHigh", float("inf")):
                mail_type = "soft"
                threshold_low = t.get("yellowLow", float("-inf"))
                threshold_high = t.get("yellowHigh", float("inf"))
            
            in_normal_range = (
                t.get("redLow", float("-inf")) < value < t.get("redHigh", float("inf")) and
                t.get("yellowLow", float("-inf")) < value < t.get("yellowHigh", float("inf"))
            )

            if mail_type:
                # Check if an alert is already active
                if not is_alert_active(device, metric, mail_type):
                    email = get_alert_email()
                    subject = f"[{mail_type.upper()}] Alert: Arduino {device} - {metric}"
                    body = (
                        f"ALERT ({mail_type.upper()})\n"
                        f"\n"
                        f"Betroffener Arduino: {device}\n"
                        f"Sensor/Messgröße: {metric}\n"
                        f"\n"
                        f"Aktueller Wert: {value} {unit}\n"
                        f"\n"
                        f"Schwellenwerte:\n"
                        f"  Rot niedrig: {t.get('redLow', '-')}{unit}\n"
                        f"  Gelb niedrig: {t.get('yellowLow', '-')}{unit}\n"
                        f"  Gelb hoch: {t.get('yellowHigh', '-')}{unit}\n"
                        f"  Rot hoch: {t.get('redHigh', '-')}{unit}\n"
                        f"\n"
                        f"Der aktuelle Wert für {metric} hat den {mail_type.upper()}-Schwellenwert "
                        f"{'überschritten' if value > threshold_high else 'unterschritten'}.\n"
                        f"Bitte prüfen Sie die Luftqualität und lüften Sie ggf. die Räume oder ergreifen Sie weitere Maßnahmen."
                    )
                    send_mail(email, subject, body)
                    set_alert_active(device, metric, mail_type)
                    log_event(
                        logger, "INFO", "alert_mail.sent",
                        mail_type=mail_type, device=device, metric=metric, value=value, unit=unit
                    )
                    return {"status": "success", "message": f"{mail_type}-Mail sent"}, 200
                else:
                    log_event(
                        logger, "INFO", "alert_mail.cooldown_active",
                        mail_type=mail_type, device=device, metric=metric, value=value, unit=unit
                    )
                    return {"status": "success", "message": f"{mail_type}-Mail already active"}, 200
            elif in_normal_range:
                reset_alert(device, metric, "hart")
                reset_alert(device, metric, "soft")
                log_event(
                    logger, "INFO", "alert_mail.reset",
                    device=device, metric=metric, value=value, unit=unit
                )
                return {"status": "success", "message": "No Threshold Exceeded"}, 200
            else:
                # Value back in normal range -> reset alert
                reset_alert(device, metric, "hart")
                reset_alert(device, metric, "soft")
                log_event(
                    logger, "INFO", "alert_mail.reset",
                    device=device, metric=metric, value=value, unit=unit
                )
                return {"status": "success", "message": "No Threshold Exceeded"}, 200
        
        except (psycopg2.Error, smtplib.SMTPException) as e:
            error_message = f"An error occurred: {str(e)}"
            log_event(logger, "ERROR", "alert_mail.process_error", error=error_message)
            return {"status": "error", "message": error_message}, 500