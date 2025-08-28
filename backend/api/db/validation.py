from common.logging_setup import setup_logger, log_event
from .time_ranges import get_all_device_time_ranges_from_db


logger = setup_logger(service="api", module="db.validation")


def validate_timestamps_and_range(device_id1, device_id2, start, end):
    log_event(logger, "DEBUG", "db.validate_range.start", device_id1=device_id1, device_id2=device_id2, start=start, end=end)

    if start is None or end is None:
        return False, "Start and end timestamps must be provided."
    if start >= end:
        return False, "Start timestamp must be less than end timestamp."

    time_ranges = get_all_device_time_ranges_from_db()
    if not time_ranges:
        return False, "No time ranges available for the devices."

    errors = []
    valid = False
    if device_id1:
        range1 = next((tr for tr in time_ranges if tr['device_id'] == device_id1), None)
        if not range1 or range1['end'] < start:
            errors.append(f"No overlapping data available for device ID {device_id1} in the specified time range.")
        else:
            valid = True
    if device_id2:
        range2 = next((tr for tr in time_ranges if tr['device_id'] == device_id2), None)
        if not range2 or range2['end'] < start:
            errors.append(f"No overlapping data available for device ID {device_id2} in the specified time range.")
        else:
            valid = True

    if not valid:
        return False, " ".join(errors)

    log_event(logger, "DEBUG", "db.validate_range.ok", device_id1=device_id1, device_id2=device_id2)
    return True, None

__all__ = ["validate_timestamps_and_range"]


