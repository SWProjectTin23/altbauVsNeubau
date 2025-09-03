import os
from flask_restful import Resource
from flask import request, url_for
from api.db import get_alert_email, set_alert_email
from common.logging_setup import setup_logger, log_event
from api.sendAlertMail import send_mail
logger = setup_logger(service="api", module="alertMail")

class AlertEmail(Resource):
    def get(self):
        try:
            email = get_alert_email()
            if email:
                return {"status": "success", "email": email}, 200
            else:
                return {"status": "error", "message": "No mail found."}, 404
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    def post(self):
        try:
            data = request.get_json(force=True)
            alert_email = data.get("alert_email")
            if not alert_email:
                return {"status": "error", "message": "Mail is missing."}, 400

            token = set_alert_email(alert_email)
            # Bestätigungslink generieren
            confirm_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/confirm-email?token={token}"
            subject = "Bitte bestätige deine Alert-Mail-Adresse"
            body = (
                f"Hallo,\n\n"
                f"Bitte bestätige deine E-Mail-Adresse für Alerts, indem du auf folgenden Link klickst:\n\n"
                f"{confirm_url}\n\n"
                f"Falls du diese Anfrage nicht gestellt hast, ignoriere diese E-Mail einfach."
            )
            send_mail(alert_email, subject, body)
            log_event(logger, "INFO", "alert_email.confirmation_sent", email=alert_email)
            return {"status": "success", "message": "Confirmation mail sent."}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500