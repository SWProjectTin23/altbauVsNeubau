from flask_restful import Resource
from flask import jsonify
from app.mock_data import get_mock_data

MOCK_DATA = get_mock_data()

class DeviceLatest(Resource):
    def get(self, device_id):
        data = MOCK_DATA.get(device_id, [])

        if not data:
            return jsonify({"error": "No data found for this device"}), 404

        latest = max(data, key=lambda d: d["timestamp"])
        return jsonify(latest)