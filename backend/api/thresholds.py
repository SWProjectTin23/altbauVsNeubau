import logging
from flask_restful import Resource
from flask import request
from exceptions import ValidationError
from .db_operations import get_thresholds_from_db, update_thresholds_in_db

logger = logging.getLogger(__name__)

# Import database operation functions
from .db_operations import get_thresholds_from_db, update_thresholds_in_db


class Thresholds(Resource):
    def get(self):
        thresholds = get_thresholds_from_db()  # kann DatabaseError raisen -> zentraler Handler
        if not thresholds:
            logger.info("No thresholds available.")
            return {
                "status": "success",
                "data": [],
                "message": "No thresholds available."
            }, 200

        return {
            "status": "success",
            "data": thresholds,
            "message": None
        }, 200
        

    def post(self):
        # JSON laden
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise ValidationError("Invalid input data. Expecting a Dictionary.")

        # Erwartete Keys + Zieltypen
        expected = {
            "temperature_min_soft": float, "temperature_max_soft": float,
            "temperature_min_hard": float, "temperature_max_hard": float,
            "humidity_min_soft": float, "humidity_max_soft": float,
            "humidity_min_hard": float, "humidity_max_hard": float,
            "pollen_min_soft": int, "pollen_max_soft": int,
            "pollen_min_hard": int, "pollen_max_hard": int,
            "particulate_matter_min_soft": int, "particulate_matter_max_soft": int,
            "particulate_matter_min_hard": int, "particulate_matter_max_hard": int
        }

        validated = {}
        for key, typ in expected.items():
            if key not in payload:
                raise ValidationError(f"Missing required key: '{key}'.")
            value = payload[key]
            if value is None:
                raise ValidationError(f"Value for '{key}' cannot be None.")
            try:
                validated[key] = float(value) if typ is float else int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid value for '{key}': {value}. Expected type {typ.__name__}.")

        # Relations-Validierung
        # min_hard < max_hard
        for a, b in [
            ("temperature_min_hard", "temperature_max_hard"),
            ("humidity_min_hard", "humidity_max_hard"),
            ("pollen_min_hard", "pollen_max_hard"),
            ("particulate_matter_min_hard", "particulate_matter_max_hard"),
        ]:
            if validated[a] >= validated[b]:
                raise ValidationError(f"'{a}' must be less than '{b}'.")

        # min_soft < max_hard
        for a, b in [
            ("temperature_min_soft", "temperature_max_hard"),
            ("humidity_min_soft", "humidity_max_hard"),
            ("pollen_min_soft", "pollen_max_hard"),
            ("particulate_matter_min_soft", "particulate_matter_max_hard"),
        ]:
            if validated[a] >= validated[b]:
                raise ValidationError(f"'{a}' must be less than '{b}'.")

        # min_soft < max_soft
        for a, b in [
            ("temperature_min_soft", "temperature_max_soft"),
            ("humidity_min_soft", "humidity_max_soft"),
            ("pollen_min_soft", "pollen_max_soft"),
            ("particulate_matter_min_soft", "particulate_matter_max_soft"),
        ]:
            if validated[a] >= validated[b]:
                raise ValidationError(f"'{a}' must be less than '{b}'.")

        # min_hard < min_soft
        for a, b in [
            ("temperature_min_hard", "temperature_min_soft"),
            ("humidity_min_hard", "humidity_min_soft"),
            ("pollen_min_hard", "pollen_min_soft"),
            ("particulate_matter_min_hard", "particulate_matter_min_soft"),
        ]:
            if validated[a] >= validated[b]:
                raise ValidationError(f"'{a}' must be less than '{b}'.")

        # max_hard > max_soft
        for a, b in [
            ("temperature_max_hard", "temperature_max_soft"),
            ("humidity_max_hard", "humidity_max_soft"),
            ("pollen_max_hard", "pollen_max_soft"),
            ("particulate_matter_max_hard", "particulate_matter_max_soft"),
        ]:
            if validated[a] <= validated[b]:
                raise ValidationError(f"'{a}' must be greater than '{b}'.")

        # Persistieren (kann DatabaseError raisen -> zentraler Handler)
        update_thresholds_in_db(validated)
        logger.info("Thresholds updated.")

        return {
            "status": "success",
            "message": "Thresholds updated successfully."
        }, 200


            