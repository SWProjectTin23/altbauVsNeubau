from flask_restful import Resource
from flask import request
from api.db_operations import get_alert_email, set_alert_email

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

            set_alert_email(alert_email)
            return {"status": "success", "message": "Alert email saved."}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500