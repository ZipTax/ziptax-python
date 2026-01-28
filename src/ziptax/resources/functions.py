"""API functions for the ZipTax SDK."""

import logging
from typing import Any, Dict, Optional

from ..models import V60AccountMetrics, V60PostalCodeResponse, V60Response
from ..utils.http import HTTPClient
from ..utils.retry import retry_with_backoff
from ..utils.validation import (
    validate_address,
    validate_coordinates,
    validate_country_code,
    validate_format,
    validate_historical_date,
    validate_postal_code,
)

logger = logging.getLogger(__name__)


class Functions:
    """Functions class for ZipTax API endpoints."""

    def __init__(
        self, http_client: HTTPClient, max_retries: int = 3, retry_delay: float = 1.0
    ):
        """Initialize Functions.

        Args:
            http_client: HTTP client for making requests
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.http_client = http_client
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def GetSalesTaxByAddress(
        self,
        address: str,
        taxability_code: Optional[str] = None,
        country_code: str = "USA",
        historical: Optional[str] = None,
        format: str = "json",
    ) -> V60Response:
        """Get sales tax rates by address.

        Args:
            address: Full or partial street address for geocoding
            taxability_code: Optional taxability code
            country_code: Country code (default: "USA")
            historical: Historical date for rates (YYYY-MM format)
            format: Response format (default: "json")

        Returns:
            V60Response object with tax rate information

        Raises:
            ZipTaxValidationError: If input parameters are invalid
            ZipTaxAPIError: If the API returns an error
        """
        # Validate inputs
        validate_address(address)
        validate_country_code(country_code)
        if historical:
            validate_historical_date(historical)
        validate_format(format)

        # Build query parameters
        params: Dict[str, Any] = {
            "address": address,
            "countryCode": country_code,
            "format": format,
        }

        if taxability_code:
            params["taxabilityCode"] = taxability_code

        if historical:
            params["historical"] = historical

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            return self.http_client.get("/request/v60/", params=params)

        response_data = _make_request()
        return V60Response(**response_data)

    def GetSalesTaxByGeoLocation(
        self,
        lat: str,
        lng: str,
        country_code: str = "USA",
        historical: Optional[str] = None,
        format: str = "json",
    ) -> V60Response:
        """Get sales tax rates by geolocation.

        Args:
            lat: Latitude for geolocation
            lng: Longitude for geolocation
            country_code: Country code (default: "USA")
            historical: Historical date for rates (YYYY-MM format)
            format: Response format (default: "json")

        Returns:
            V60Response object with tax rate information

        Raises:
            ZipTaxValidationError: If input parameters are invalid
            ZipTaxAPIError: If the API returns an error
        """
        # Validate inputs
        validate_coordinates(lat, lng)
        validate_country_code(country_code)
        if historical:
            validate_historical_date(historical)
        validate_format(format)

        # Build query parameters
        params: Dict[str, Any] = {
            "lat": lat,
            "lng": lng,
            "countryCode": country_code,
            "format": format,
        }

        if historical:
            params["historical"] = historical

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            return self.http_client.get("/request/v60/", params=params)

        response_data = _make_request()
        return V60Response(**response_data)

    def GetAccountMetrics(self, key: Optional[str] = None) -> V60AccountMetrics:
        """Get account metrics.

        Args:
            key: Optional API key parameter

        Returns:
            V60AccountMetrics object with account metrics

        Raises:
            ZipTaxAPIError: If the API returns an error
        """
        # Build query parameters
        params: Dict[str, Any] = {}
        if key:
            params["key"] = key

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            return self.http_client.get("/account/v60/metrics", params=params)

        response_data = _make_request()
        return V60AccountMetrics(**response_data)

    def GetRatesByPostalCode(
        self,
        postal_code: str,
        format: str = "json",
    ) -> V60PostalCodeResponse:
        """Get sales tax rates by US postal code.

        Args:
            postal_code: US postal code (5-digit or 9-digit format,
                e.g., "92694" or "92694-1234")
            format: Response format (default: "json")

        Returns:
            V60PostalCodeResponse object with tax rate information for all locations
            within the postal code

        Raises:
            ZipTaxValidationError: If input parameters are invalid
            ZipTaxAPIError: If the API returns an error
        """
        # Validate inputs
        validate_postal_code(postal_code)
        validate_format(format)

        # Build query parameters
        params: Dict[str, Any] = {
            "postalcode": postal_code,
            "format": format,
        }

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            return self.http_client.get("/request/v60/", params=params)

        response_data = _make_request()
        return V60PostalCodeResponse(**response_data)
