from flask_restful import Resource
from flask import request
from api.db import get_db_connection

class ConfirmEmail(Resource):
    def post(self):
        data = request.get_json(force=True)
        token = data.get("token")
        if not token:
            return {"status": "error", "message": "Token missing."}, 400
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE alert_emails SET confirmed=TRUE WHERE confirmation_token=%s RETURNING email",
            (token,)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if row:
            return {"status": "success", "message": "Email confirmed.", "email": row[0]}, 200
        else:
            return {"status": "error", "message": "Invalid token."}, 400