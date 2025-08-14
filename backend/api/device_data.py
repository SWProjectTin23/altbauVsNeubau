import logging
from flask_restful import Resource
from flask import request
from exceptions import ValidationError, NotFoundError
from .db_operations import get_device_data_from_db, device_exists

logger = logging.getLogger(__name__)

class DeviceData(Resource):
    def get(self, device_id):
        # Query-Parameter
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        # Validierung
        if start is not None and end is not None and start >= end:
            raise ValidationError("Parameter 'start' must be less than 'end'.")

        # Gerät vorhanden?
        if not device_exists(device_id):
            raise NotFoundError(f"Device with ID {device_id} does not exist.")

        # Daten laden (kann DatabaseError raisen -> zentraler Handler)
        data = get_device_data_from_db(device_id, start=start, end=end)

        if not data:
            logger.info("No data for device_id=%s in range start=%s end=%s", device_id, start, end)

        return {
            "device_id": device_id,
            "start": start,
            "end": end,
            "status": "success",
            "data": data,
            "message": None if data else f"No data available for device {device_id} in the specified range."
        }, 200