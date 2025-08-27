from flask_restful import Resource, reqparse
from flask import request
import psycopg2
from .db_operations import get_db_connection 

class AlertEmail(Resource):
    def get(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT email FROM alert_emails LIMIT 1")
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return {"status": "success", "email": row[0]}, 200
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

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM alert_emails")
            cur.execute("INSERT INTO alert_emails (email) VALUES (%s)", (alert_email,))
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "message": "Alert email saved."}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500