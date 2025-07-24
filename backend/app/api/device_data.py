from flask_restful import Resource
from flask import request, jsonify
from app.mock_data import get_mock_data

MOCK_DATA = get_mock_data()

class DeviceData(Resource):
    def get(self, device_id):
        start = request.args.get("start", type=int)
        end = request.args.get("end", type=int)

        device_data = MOCK_DATA.get(device_id)
        if device_data is None:
            return {"error": f"Device {device_id} not found"}, 404

        # print(f"\n Fetching data for device {device_id}")
        # print(f"Start = {start}, End = {end}")

        result = []

        for entry in device_data:
            ts = entry.get("timestamp")
            if ts is None:
                continue

            # if time range (start/end) is given，return filtered results, otherwise return all results.
            if (start is None or ts >= start) and (end is None or ts <= end):
                result.append(entry)

        return jsonify(result)
