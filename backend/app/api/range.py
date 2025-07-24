from flask_restful import Resource
from flask import jsonify

# query: MIN(timestamp), MAX(timestamp)
MOCK_RANGE = {
    1: {
        "start": 1721736000,  # 2025-07-23 12:00:00 UTC
        "end":   1721745000   # 2025-07-23 14:30:00 UTC
    },
    2: {
        "start": 1721736300,  # 2025-07-23 12:05:00 UTC
        "end":   1721744700   # 2025-07-23 14:25:00 UTC
    }
}

class TimeRange(Resource):
    def get(self):
        # later can use altbau, neubau to replace device_1, device_2
        return jsonify({
            f"device_{device_id}": time_range
            for device_id, time_range in MOCK_RANGE.items()
        })
