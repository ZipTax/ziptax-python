"""Validation utilities for the ZipTax SDK."""

import re

from ..exceptions import ZipTaxValidationError


def validate_address(address: str) -> None:
    """Validate address parameter.

    Args:
        address: Address string to validate

    Raises:
        ZipTaxValidationError: If address is invalid
    """
    if not isinstance(address, str):
        raise ZipTaxValidationError("Address must be a string")

    if not address:
        raise ZipTaxValidationError("Address cannot be empty")

    if len(address) > 100:
        raise ZipTaxValidationError("Address cannot exceed 100 characters")


def validate_coordinates(lat: str, lng: str) -> None:
    """Validate latitude and longitude parameters.

    Args:
        lat: Latitude string to validate
        lng: Longitude string to validate

    Raises:
        ZipTaxValidationError: If coordinates are invalid
    """
    if not lat or not lng:
        raise ZipTaxValidationError("Latitude and longitude cannot be empty")

    if not isinstance(lat, str) or not isinstance(lng, str):
        raise ZipTaxValidationError("Latitude and longitude must be strings")

    # Try to convert to float for validation
    try:
        lat_float = float(lat)
        lng_float = float(lng)
    except ValueError:
        raise ZipTaxValidationError("Latitude and longitude must be valid numbers")

    # Validate ranges
    if not -90 <= lat_float <= 90:
        raise ZipTaxValidationError("Latitude must be between -90 and 90")

    if not -180 <= lng_float <= 180:
        raise ZipTaxValidationError("Longitude must be between -180 and 180")


def validate_country_code(country_code: str) -> None:
    """Validate country code parameter.

    Args:
        country_code: Country code to validate

    Raises:
        ZipTaxValidationError: If country code is invalid
    """
    valid_codes = ["USA", "CAN"]

    if country_code not in valid_codes:
        raise ZipTaxValidationError(
            f"Country code must be one of {valid_codes}, got: {country_code}"
        )


def validate_historical_date(historical: str) -> None:
    """Validate historical date parameter.

    Args:
        historical: Historical date string to validate (YYYYMM format)

    Raises:
        ZipTaxValidationError: If historical date is invalid
    """
    pattern = r"^[0-9]{4}[0-9]{2}$"

    if not re.match(pattern, historical):
        raise ZipTaxValidationError(
            f"Historical date must be in YYYYMM format, got: {historical}"
        )

    # Validate year and month ranges
    try:
        year_int = int(historical[:4])
        month_int = int(historical[4:6])

        if year_int < 1900 or year_int > 2100:
            raise ZipTaxValidationError(f"Invalid year: {year_int}")

        if month_int < 1 or month_int > 12:
            raise ZipTaxValidationError(f"Invalid month: {month_int}")

    except (ValueError, IndexError):
        raise ZipTaxValidationError(
            f"Historical date must be in YYYYMM format, got: {historical}"
        )


def validate_format(format_str: str) -> None:
    """Validate format parameter.

    Args:
        format_str: Format string to validate

    Raises:
        ZipTaxValidationError: If format is invalid
    """
    valid_formats = ["json"]

    if format_str not in valid_formats:
        raise ZipTaxValidationError(
            f"Format must be one of {valid_formats}, got: {format_str}"
        )


def validate_api_key(api_key: str) -> None:
    """Validate API key.

    Args:
        api_key: API key to validate

    Raises:
        ZipTaxValidationError: If API key is invalid
    """
    if not api_key:
        raise ZipTaxValidationError("API key cannot be empty")

    if not isinstance(api_key, str):
        raise ZipTaxValidationError("API key must be a string")

    if len(api_key) < 10:
        raise ZipTaxValidationError("API key appears to be invalid (too short)")


def validate_postal_code(postal_code: str) -> None:
    """Validate US postal code parameter.

    Args:
        postal_code: Postal code string to validate (5-digit or 9-digit format)

    Raises:
        ZipTaxValidationError: If postal code is invalid
    """
    if not postal_code:
        raise ZipTaxValidationError("Postal code cannot be empty")

    if not isinstance(postal_code, str):
        raise ZipTaxValidationError("Postal code must be a string")

    # Pattern for 5-digit or 5+4 digit format
    pattern = r"^[0-9]{5}(-[0-9]{4})?$"

    if not re.match(pattern, postal_code):
        raise ZipTaxValidationError(
            f"Postal code must be in 5-digit (e.g., 92694) or "
            f"9-digit (e.g., 92694-1234) format, got: {postal_code}"
        )
