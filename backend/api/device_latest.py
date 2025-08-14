from flask_restful import Resource
from flask import jsonify
import logging
from exceptions import ValidationError, NotFoundError
# Import database operation functions
from .db_operations import get_latest_device_data_from_db, device_exists

logger = logging.getLogger(__name__)

class DeviceLatest(Resource):
    def get(self, device_id):
        if not device_exists(device_id):
            raise NotFoundError(f"Device with ID {device_id} does not exist.")

        data = get_latest_device_data_from_db(device_id)

        if not data:
            return {
                "status": "success",
                "data": [],
                "message": f"No data available for device {device_id}."
            }, 200

        return {
                "status": "success",
                "data": data,
                "message": None
        }, 200