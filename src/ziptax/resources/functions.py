"""API functions for the ZipTax SDK."""

import logging
import re
from typing import Any, Dict, List, Optional

from ..config import Config
from ..exceptions import ZipTaxCloudConfigError
from ..models import (
    CalculateCartRequest,
    CalculateCartResponse,
    CreateOrderRequest,
    OrderResponse,
    RefundTransactionRequest,
    RefundTransactionResponse,
    UpdateOrderRequest,
    V60AccountMetrics,
    V60PostalCodeResponse,
    V60Response,
)
from ..utils.http import HTTPClient
from ..utils.retry import retry_with_backoff
from ..utils.validation import (
    validate_address,
    validate_address_autocomplete,
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
        self,
        http_client: HTTPClient,
        config: Config,
        taxcloud_http_client: Optional[HTTPClient] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize Functions.

        Args:
            http_client: HTTP client for making ZipTax requests
            config: Configuration object
            taxcloud_http_client: Optional HTTP client for TaxCloud requests
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.http_client = http_client
        self.taxcloud_http_client = taxcloud_http_client
        self.config = config
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
            historical: Historical date for rates (YYYYMM format, e.g. "202401")
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
            historical: Historical date for rates (YYYYMM format, e.g. "202401")
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
            postal_code: US postal code (5-digit format, e.g., "92694")
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

    # =========================================================================
    # ZipTax Cart Tax Calculation
    # =========================================================================

    @staticmethod
    def _extract_state_from_normalized_address(normalized_address: str) -> str:
        """Extract the US state abbreviation from a V60 normalized address.

        The V60 API returns normalized addresses in the format:
        "200 Spectrum Center Dr, Irvine, CA 92618-5003, United States"

        This method extracts the two-letter state abbreviation (e.g., "CA")
        from that format.

        Args:
            normalized_address: Normalized address string from
                V60Response.addressDetail.normalizedAddress

        Returns:
            Two-letter uppercase state abbreviation (e.g., "CA", "TX")

        Raises:
            ValueError: If the state cannot be parsed from the address
        """
        # Match a two-letter state code followed by a ZIP code pattern
        # e.g., "Irvine, CA 92618-5003, United States"
        match = re.search(r",\s+([A-Z]{2})\s+\d{5}", normalized_address)
        if match:
            return match.group(1)

        raise ValueError(
            f"Could not extract state from normalized address: "
            f"'{normalized_address}'"
        )

    def _resolve_sourcing_address(
        self,
        origin_address: str,
        destination_address: str,
    ) -> str:
        """Resolve which address to use for tax calculation based on sourcing rules.

        Uses the V60 API to look up both addresses, extracts the state from
        each normalized address, and applies origin/destination sourcing logic:

        - Interstate (different states): use destination address (skip sourcing)
        - Intrastate (same state), destination-based ("D"): use destination address
        - Intrastate (same state), origin-based ("O"): use origin address

        Args:
            origin_address: The seller/shipper address string
            destination_address: The buyer/recipient address string

        Returns:
            The address string to use for tax calculation

        Raises:
            ZipTaxAPIError: If the V60 API returns an error
            ValueError: If state cannot be parsed from a normalized address
        """
        # Step 1: Look up both addresses via the V60 API
        destination_v60 = self.GetSalesTaxByAddress(destination_address)
        origin_v60 = self.GetSalesTaxByAddress(origin_address)

        # Step 2: Extract states from normalized addresses
        dest_state = self._extract_state_from_normalized_address(
            destination_v60.address_detail.normalized_address
        )
        origin_state = self._extract_state_from_normalized_address(
            origin_v60.address_detail.normalized_address
        )

        logger.debug(
            f"Sourcing resolution: origin_state={origin_state}, "
            f"dest_state={dest_state}"
        )

        # Step 3: Interstate — always use destination
        if dest_state != origin_state:
            logger.debug("Interstate transaction — using destination address for rates")
            return destination_address

        # Step 4: Intrastate — check sourcingRules.value from destination lookup
        sourcing_value = None
        if destination_v60.sourcing_rules:
            sourcing_value = destination_v60.sourcing_rules.value

        if sourcing_value == "O":
            logger.debug("Origin-based sourcing state — using origin address for rates")
            return origin_address

        # Default to destination (covers "D" and any unexpected value)
        logger.debug(
            "Destination-based sourcing state — using destination address for rates"
        )
        return destination_address

    def CalculateCart(
        self,
        request: CalculateCartRequest,
    ) -> CalculateCartResponse:
        """Calculate sales tax for a shopping cart with multiple line items.

        Resolves origin/destination sourcing rules automatically, then sends
        the cart to the API for tax calculation using the correct address.

        The sourcing resolution logic:
        1. Looks up both origin and destination addresses via GetSalesTaxByAddress
        2. Extracts and compares states from normalized addresses
        3. Interstate (different states): uses destination address
        4. Intrastate (same state): checks sourcingRules.value from the
           destination lookup — if "O", uses origin address; otherwise
           uses destination address
        5. Sends the resolved address to POST /calculate/cart

        Args:
            request: CalculateCartRequest object with cart details including
                customer ID, addresses, currency, and line items

        Returns:
            CalculateCartResponse object with per-item tax calculations

        Raises:
            ZipTaxAPIError: If the API returns an error
            ValueError: If state cannot be parsed from a normalized address

        Example:
            >>> from ziptax.models import (
            ...     CalculateCartRequest, CartItem, CartAddress,
            ...     CartCurrency, CartLineItem
            ... )
            >>> request = CalculateCartRequest(
            ...     items=[
            ...         CartItem(
            ...             customer_id="customer-453",
            ...             currency=CartCurrency(currency_code="USD"),
            ...             destination=CartAddress(
            ...                 address="200 Spectrum Center Dr, Irvine, CA 92618"
            ...             ),
            ...             origin=CartAddress(
            ...                 address="323 Washington Ave N, Minneapolis, MN 55401"
            ...             ),
            ...             line_items=[
            ...                 CartLineItem(
            ...                     item_id="item-1",
            ...                     price=10.75,
            ...                     quantity=1.5,
            ...                 )
            ...             ],
            ...         )
            ...     ]
            ... )
            >>> result = client.request.CalculateCart(request)
        """
        cart = request.items[0]

        # Resolve which address should be used for tax calculation
        resolved_address = self._resolve_sourcing_address(
            origin_address=cart.origin.address,
            destination_address=cart.destination.address,
        )

        # Build the request payload, overriding both addresses with the
        # resolved address so the API calculates using the correct rates
        request_data = request.model_dump(by_alias=True, exclude_none=True)
        request_data["items"][0]["destination"]["address"] = resolved_address
        request_data["items"][0]["origin"]["address"] = resolved_address

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            return self.http_client.post(
                "/calculate/cart",
                json=request_data,
            )

        response_data = _make_request()
        return CalculateCartResponse(**response_data)

    # =========================================================================
    # TaxCloud API - Order Management Functions
    # =========================================================================

    def _check_taxcloud_config(self) -> None:
        """Check if TaxCloud credentials are configured.

        Raises:
            ZipTaxCloudConfigError: If TaxCloud credentials are not configured
        """
        if not self.config.has_taxcloud_config or self.taxcloud_http_client is None:
            raise ZipTaxCloudConfigError(
                "TaxCloud credentials not configured. Please provide "
                "taxcloud_connection_id and taxcloud_api_key when creating the client."
            )

    def CreateOrder(
        self,
        request: CreateOrderRequest,
        address_autocomplete: str = "none",
    ) -> OrderResponse:
        """Create an order in TaxCloud.

        Args:
            request: CreateOrderRequest object with order details
            address_autocomplete: Address autocomplete option (default: "none")
                Options: "none", "origin", "destination", "all"

        Returns:
            OrderResponse object with created order details

        Raises:
            ZipTaxValidationError: If address_autocomplete value is invalid
            ZipTaxCloudConfigError: If TaxCloud credentials not configured
            ZipTaxAPIError: If the API returns an error

        Example:
            >>> from ziptax.models import (
            ...     CreateOrderRequest, TaxCloudAddress, CartItemWithTax,
            ...     Tax, Currency
            ... )
            >>> request = CreateOrderRequest(
            ...     order_id="my-order-1",
            ...     customer_id="customer-453",
            ...     transaction_date="2024-01-15T09:30:00Z",
            ...     completed_date="2024-01-15T09:30:00Z",
            ...     origin=TaxCloudAddress(
            ...         line1="323 Washington Ave N",
            ...         city="Minneapolis",
            ...         state="MN",
            ...         zip="55401-2427"
            ...     ),
            ...     destination=TaxCloudAddress(
            ...         line1="323 Washington Ave N",
            ...         city="Minneapolis",
            ...         state="MN",
            ...         zip="55401-2427"
            ...     ),
            ...     line_items=[
            ...         CartItemWithTax(
            ...             index=0,
            ...             item_id="item-1",
            ...             price=10.8,
            ...             quantity=1.5,
            ...             tax=Tax(amount=1.31, rate=0.0813)
            ...         )
            ...     ],
            ...     currency=Currency(currency_code="USD")
            ... )
            >>> order = client.request.CreateOrder(request)
        """
        self._check_taxcloud_config()

        # Validate inputs
        validate_address_autocomplete(address_autocomplete)

        # Build query parameters
        params: Dict[str, Any] = {}
        if address_autocomplete != "none":
            params["addressAutocomplete"] = address_autocomplete

        # Build path with connection ID
        path = f"/tax/connections/{self.config.taxcloud_connection_id}/orders"

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            assert self.taxcloud_http_client is not None
            return self.taxcloud_http_client.post(
                path,
                json=request.model_dump(by_alias=True, exclude_none=True),
                params=params,
            )

        response_data = _make_request()
        return OrderResponse(**response_data)

    def GetOrder(self, order_id: str) -> OrderResponse:
        """Retrieve an order from TaxCloud by ID.

        Args:
            order_id: The ID of the order to retrieve

        Returns:
            OrderResponse object with order details

        Raises:
            ZipTaxCloudConfigError: If TaxCloud credentials not configured
            ZipTaxAPIError: If the API returns an error

        Example:
            >>> order = client.request.GetOrder("my-order-1")
        """
        self._check_taxcloud_config()

        # Build path with connection ID and order ID
        path = (
            f"/tax/connections/{self.config.taxcloud_connection_id}/orders/{order_id}"
        )

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            assert self.taxcloud_http_client is not None
            return self.taxcloud_http_client.get(path)

        response_data = _make_request()
        return OrderResponse(**response_data)

    def UpdateOrder(
        self,
        order_id: str,
        request: UpdateOrderRequest,
    ) -> OrderResponse:
        """Update an existing order's completedDate in TaxCloud.

        Args:
            order_id: The ID of the order to update
            request: UpdateOrderRequest object with updated completedDate

        Returns:
            OrderResponse object with updated order details

        Raises:
            ZipTaxCloudConfigError: If TaxCloud credentials not configured
            ZipTaxAPIError: If the API returns an error

        Example:
            >>> from ziptax.models import UpdateOrderRequest
            >>> request = UpdateOrderRequest(
            ...     completed_date="2024-01-16T10:00:00Z"
            ... )
            >>> order = client.request.UpdateOrder("my-order-1", request)
        """
        self._check_taxcloud_config()

        # Build path with connection ID and order ID
        path = (
            f"/tax/connections/{self.config.taxcloud_connection_id}/orders/{order_id}"
        )

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> Dict[str, Any]:
            assert self.taxcloud_http_client is not None
            return self.taxcloud_http_client.patch(
                path, json=request.model_dump(by_alias=True, exclude_none=True)
            )

        response_data = _make_request()
        return OrderResponse(**response_data)

    def RefundOrder(
        self,
        order_id: str,
        request: Optional[RefundTransactionRequest] = None,
    ) -> List[RefundTransactionResponse]:
        """Create a refund against an order in TaxCloud.

        An order can only be refunded once, regardless of whether the order is
        partially or fully refunded.

        Args:
            order_id: The ID of the order to refund
            request: Optional RefundTransactionRequest with items to refund.
                If None or items is empty, entire order will be refunded.

        Returns:
            List of RefundTransactionResponse objects

        Raises:
            ZipTaxCloudConfigError: If TaxCloud credentials not configured
            ZipTaxAPIError: If the API returns an error

        Example:
            Full refund:
            >>> refunds = client.request.RefundOrder("my-order-1")

            Partial refund:
            >>> from ziptax.models import (
            ...     RefundTransactionRequest, CartItemRefundWithTaxRequest
            ... )
            >>> request = RefundTransactionRequest(
            ...     items=[
            ...         CartItemRefundWithTaxRequest(
            ...             item_id="item-1",
            ...             quantity=1.0
            ...         )
            ...     ]
            ... )
            >>> refunds = client.request.RefundOrder("my-order-1", request)
        """
        self._check_taxcloud_config()

        # Build path with connection ID and order ID
        conn_id = self.config.taxcloud_connection_id
        path = f"/tax/connections/{conn_id}/orders/refunds/{order_id}"

        # Prepare request body
        request_body = {}
        if request:
            request_body = request.model_dump(by_alias=True, exclude_none=True)

        # Make request with retry logic
        @retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.retry_delay,
        )
        def _make_request() -> List[Dict[str, Any]]:
            assert self.taxcloud_http_client is not None
            return self.taxcloud_http_client.post(path, json=request_body)

        response_data = _make_request()

        # API may return a single dict or a list of dicts
        if isinstance(response_data, dict):
            response_data = [response_data]

        return [RefundTransactionResponse(**item) for item in response_data]
