"""Central validation routine matching the TrackPoint data dictionary."""

import re

from settings import (
    EVENT_TYPES,
    HOUSES,
    MAX_AGE_GROUP_LENGTH,
    MAX_COMPETITOR_NAME_LENGTH,
    MAX_EVENT_NAME_LENGTH,
    MAX_ID_DIGITS,
    MAX_PASSWORD_LENGTH,
    MAX_RESULT_VALUE_LENGTH,
    MAX_SEARCH_LENGTH,
    MAX_USERNAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_USERNAME_LENGTH,
    RESULT_UNITS,
    ROLES,
    YEAR_GROUPS,
)


class ValidationError(ValueError):
    """Raised when data does not satisfy the documented validation rules."""


def validate_value(field, value, event_type=None):
    """Validate and normalise one TrackPoint field using its dictionary rules."""
    if field == "username":
        value = str(value).strip()
        if not MIN_USERNAME_LENGTH <= len(value) <= MAX_USERNAME_LENGTH:
            raise ValidationError(
                f"Username must be {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters."
            )
        if re.fullmatch(r"[A-Za-z0-9_]+", value) is None:
            raise ValidationError("Username can only contain letters, numbers and underscores.")
        return value

    if field == "password":
        value = str(value)
        if not MIN_PASSWORD_LENGTH <= len(value) <= MAX_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters."
            )
        return value

    if field == "role":
        if value not in ROLES:
            raise ValidationError("Role must be Admin, Staff or Student.")
        return value

    if field in ("user_id", "competitor_id", "event_id", "result_id"):
        labels = {
            "user_id": "User ID",
            "competitor_id": "Competitor ID",
            "event_id": "Event ID",
            "result_id": "Result ID",
        }
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValidationError(labels[field] + " must be a whole number.")
        if number < 1 or len(str(number)) > MAX_ID_DIGITS:
            raise ValidationError(
                labels[field] + f" must contain 1-{MAX_ID_DIGITS} digits."
            )
        return number

    if field == "competitor_name":
        value = " ".join(str(value).strip().split())
        if not 1 <= len(value) <= MAX_COMPETITOR_NAME_LENGTH:
            raise ValidationError(
                f"Student name must be 1-{MAX_COMPETITOR_NAME_LENGTH} characters."
            )
        if not all(character.isalpha() or character == " " for character in value):
            raise ValidationError("Student name can only contain letters and spaces.")
        return value

    if field == "year_group":
        value = str(value).strip()
        if value not in YEAR_GROUPS:
            raise ValidationError("Year group must be between 7 and 12.")
        return value

    if field == "house":
        if value not in HOUSES:
            raise ValidationError("House must be Midson, Darvall, Harris or Terry.")
        return value

    if field == "event_name":
        value = " ".join(str(value).strip().split())
        if not 1 <= len(value) <= MAX_EVENT_NAME_LENGTH:
            raise ValidationError(
                f"Event name must be 1-{MAX_EVENT_NAME_LENGTH} characters."
            )
        return value

    if field == "event_type":
        if value not in EVENT_TYPES:
            raise ValidationError("Event type must be Track or Field.")
        return value

    if field == "age_group":
        value = " ".join(str(value).strip().split())
        if not 1 <= len(value) <= MAX_AGE_GROUP_LENGTH:
            raise ValidationError(
                f"Age group must be 1-{MAX_AGE_GROUP_LENGTH} characters."
            )
        if re.fullmatch(r"[A-Za-z0-9 ]+", value) is None:
            raise ValidationError("Age group can only contain letters, numbers and spaces.")
        return value

    if field == "placing":
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Placing must be a whole number.")
        if number < 1 or number > 8:
            raise ValidationError("Placing must be between 1 and 8.")
        return number

    if field == "result_value":
        value = " ".join(str(value).strip().split())
        if not 1 <= len(value) <= MAX_RESULT_VALUE_LENGTH:
            raise ValidationError(
                f"Result value must be 1-{MAX_RESULT_VALUE_LENGTH} characters."
            )
        match = re.fullmatch(r"(\d{1,4}(?:\.\d{1,2})?)\s*([sm])", value.lower())
        if match is None:
            raise ValidationError(
                "Result must contain a number followed by s or m, for example 12.42 s."
            )
        if float(match.group(1)) <= 0:
            raise ValidationError("Result value must be greater than zero.")
        unit = match.group(2)
        if event_type in RESULT_UNITS and unit != RESULT_UNITS[event_type]:
            raise ValidationError(
                f"{event_type} results must use the unit '{RESULT_UNITS[event_type]}'."
            )
        return f"{match.group(1)} {unit}"

    if field == "search_text":
        value = str(value).strip()
        if len(value) > MAX_SEARCH_LENGTH:
            raise ValidationError(
                f"Search text cannot exceed {MAX_SEARCH_LENGTH} characters."
            )
        return value

    raise ValidationError("Unknown validation field: " + str(field))
