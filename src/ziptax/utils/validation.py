"""Validation utilities for the ZipTax SDK."""

import re
from typing import Dict

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


def validate_address_autocomplete(address_autocomplete: str) -> None:
    """Validate address_autocomplete parameter for TaxCloud orders.

    Args:
        address_autocomplete: Address autocomplete option to validate

    Raises:
        ZipTaxValidationError: If address_autocomplete value is invalid
    """
    valid_options = ["none", "origin", "destination", "all"]

    if address_autocomplete not in valid_options:
        raise ZipTaxValidationError(
            f"address_autocomplete must be one of {valid_options}, "
            f"got: {address_autocomplete!r}"
        )


def validate_postal_code(postal_code: str) -> None:
    """Validate US postal code parameter.

    Args:
        postal_code: Postal code string to validate (5-digit format only)

    Raises:
        ZipTaxValidationError: If postal code is invalid
    """
    if not postal_code:
        raise ZipTaxValidationError("Postal code cannot be empty")

    if not isinstance(postal_code, str):
        raise ZipTaxValidationError("Postal code must be a string")

    # Pattern for 5-digit format only (API does not accept 9-digit codes)
    pattern = r"^[0-9]{5}$"

    if not re.match(pattern, postal_code):
        raise ZipTaxValidationError(
            f"Postal code must be in 5-digit format (e.g., 92694), "
            f"got: {postal_code}"
        )


def parse_address_string(address: str) -> Dict[str, str]:
    """Parse a single address string into structured TaxCloud address components.

    Parses addresses in the format:
        "line1, city, state zip" or "line1, city, state zip-plus4"

    Examples:
        "200 Spectrum Center Dr, Irvine, CA 92618"
        "323 Washington Ave N, Minneapolis, MN 55401-2427"

    Args:
        address: Full address string to parse

    Returns:
        Dictionary with keys: line1, city, state, zip, countryCode

    Raises:
        ZipTaxValidationError: If the address cannot be parsed into
            the required components. The address must contain at least
            3 comma-separated segments, and the last segment must contain
            a valid state abbreviation and ZIP code.
    """
    if not address or not address.strip():
        raise ZipTaxValidationError(
            "Address string cannot be empty. "
            "Expected format: 'street, city, state zip'"
        )

    # Split by comma and strip whitespace
    parts = [p.strip() for p in address.split(",")]

    if len(parts) < 3:
        raise ZipTaxValidationError(
            f"Cannot parse address into structured components. "
            f"Expected at least 3 comma-separated parts "
            f"(street, city, state zip), got {len(parts)}: {address!r}"
        )

    # line1 is everything before the last two segments
    # city is the second-to-last segment
    # state + zip is the last segment
    line1 = ", ".join(parts[:-2])
    city = parts[-2]
    state_zip = parts[-1]

    # Parse state and zip from the last segment (e.g., "CA 92618" or "CA 92618-1905")
    state_zip_match = re.match(r"^([A-Za-z]{2})\s+(\d{5}(?:-\d{4})?)$", state_zip)
    if not state_zip_match:
        raise ZipTaxValidationError(
            f"Cannot parse state and ZIP from address segment: {state_zip!r}. "
            f"Expected format: 'ST 12345' or 'ST 12345-6789'"
        )

    state = state_zip_match.group(1).upper()
    zip_code = state_zip_match.group(2)

    return {
        "line1": line1,
        "city": city,
        "state": state,
        "zip": zip_code,
        "countryCode": "US",
    }
