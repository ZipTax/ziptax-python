"""Tests for API functions."""

import pytest
from pydantic import ValidationError

from ziptax.exceptions import ZipTaxCloudConfigError, ZipTaxValidationError
from ziptax.models import (
    CalculateCartRequest,
    CalculateCartResponse,
    CartAddress,
    CartCurrency,
    CartItem,
    CartLineItem,
    CreateOrderRequest,
    OrderResponse,
    RefundTransactionRequest,
    RefundTransactionResponse,
    UpdateOrderRequest,
    V60AccountMetrics,
    V60PostalCodeResponse,
    V60Response,
)
from ziptax.resources.functions import Functions


class TestGetSalesTaxByAddress:
    """Test cases for GetSalesTaxByAddress function."""

    def test_basic_request(self, mock_http_client, mock_config, sample_v60_response):
        """Test basic address request."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetSalesTaxByAddress(
            "200 Spectrum Center Drive, Irvine, CA 92618"
        )

        assert isinstance(response, V60Response)
        assert response.metadata.version == "v60"
        assert response.metadata.response.code == 100
        mock_http_client.get.assert_called_once()

    def test_with_optional_parameters(
        self, mock_http_client, mock_config, sample_v60_response
    ):
        """Test request with optional parameters."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetSalesTaxByAddress(
            address="200 Spectrum Center Drive, Irvine, CA 92618",
            taxability_code="12345",
            country_code="USA",
            historical="202401",
            format="json",
        )

        assert isinstance(response, V60Response)
        call_args = mock_http_client.get.call_args
        assert (
            call_args[1]["params"]["address"]
            == "200 Spectrum Center Drive, Irvine, CA 92618"
        )
        assert call_args[1]["params"]["taxabilityCode"] == "12345"
        assert call_args[1]["params"]["historical"] == "202401"

    def test_empty_address_validation(self, mock_http_client, mock_config):
        """Test validation of empty address."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Address cannot be empty"):
            functions.GetSalesTaxByAddress("")

    def test_address_too_long_validation(self, mock_http_client, mock_config):
        """Test validation of address length."""
        functions = Functions(mock_http_client, mock_config)
        long_address = "a" * 101

        with pytest.raises(ZipTaxValidationError, match="cannot exceed 100 characters"):
            functions.GetSalesTaxByAddress(long_address)

    def test_invalid_country_code(self, mock_http_client, mock_config):
        """Test validation of country code."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Country code must be one of"):
            functions.GetSalesTaxByAddress(
                "200 Spectrum Center Drive",
                country_code="INVALID",
            )

    def test_invalid_historical_format(self, mock_http_client, mock_config):
        """Test validation of historical date format."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="must be in YYYYMM format"):
            functions.GetSalesTaxByAddress(
                "200 Spectrum Center Drive",
                historical="2024-13-01",
            )


class TestGetSalesTaxByGeoLocation:
    """Test cases for GetSalesTaxByGeoLocation function."""

    def test_basic_request(self, mock_http_client, mock_config, sample_v60_response):
        """Test basic geolocation request."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetSalesTaxByGeoLocation(
            lat="33.6489",
            lng="-117.8386",
        )

        assert isinstance(response, V60Response)
        assert response.metadata.version == "v60"
        assert response.metadata.response.code == 100
        mock_http_client.get.assert_called_once()

    def test_with_optional_parameters(
        self, mock_http_client, mock_config, sample_v60_response
    ):
        """Test request with optional parameters."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetSalesTaxByGeoLocation(
            lat="33.6489",
            lng="-117.8386",
            country_code="USA",
            historical="202401",
            format="json",
        )

        assert isinstance(response, V60Response)
        call_args = mock_http_client.get.call_args
        assert call_args[1]["params"]["lat"] == "33.6489"
        assert call_args[1]["params"]["lng"] == "-117.8386"

    def test_empty_coordinates_validation(self, mock_http_client, mock_config):
        """Test validation of empty coordinates."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="cannot be empty"):
            functions.GetSalesTaxByGeoLocation(lat="", lng="")

    def test_invalid_latitude_range(self, mock_http_client, mock_config):
        """Test validation of latitude range."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Latitude must be between"):
            functions.GetSalesTaxByGeoLocation(lat="100.0", lng="-117.8386")

    def test_invalid_longitude_range(self, mock_http_client, mock_config):
        """Test validation of longitude range."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Longitude must be between"):
            functions.GetSalesTaxByGeoLocation(lat="33.6489", lng="200.0")

    def test_invalid_coordinate_format(self, mock_http_client, mock_config):
        """Test validation of coordinate format."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="must be valid numbers"):
            functions.GetSalesTaxByGeoLocation(lat="invalid", lng="-117.8386")


class TestGetAccountMetrics:
    """Test cases for GetAccountMetrics function."""

    def test_basic_request(self, mock_http_client, mock_config, sample_account_metrics):
        """Test basic account metrics request."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics()

        assert isinstance(response, V60AccountMetrics)
        assert response.request_count == 15595
        assert response.is_active is True
        mock_http_client.get.assert_called_once()

    def test_with_key_parameter(
        self, mock_http_client, mock_config, sample_account_metrics
    ):
        """Test request with key parameter."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics(key="test-key")

        assert isinstance(response, V60AccountMetrics)
        call_args = mock_http_client.get.call_args
        assert call_args[1]["params"]["key"] == "test-key"

    def test_response_fields(
        self, mock_http_client, mock_config, sample_account_metrics
    ):
        """Test all response fields are properly parsed."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics()

        assert response.request_count == 15595
        assert response.request_limit == 1000000
        assert response.usage_percent == 1.5595
        assert response.is_active is True
        assert "support@zip.tax" in response.message

    def test_core_prefixed_fields(self, mock_http_client, mock_config):
        """Test that core_* prefixed fields are accepted as aliases."""
        mock_http_client.get.return_value = {
            "core_request_count": 500,
            "core_request_limit": 10000,
            "core_usage_percent": 5.0,
            "is_active": True,
            "message": "OK",
        }
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics()

        assert isinstance(response, V60AccountMetrics)
        assert response.request_count == 500
        assert response.request_limit == 10000
        assert response.usage_percent == 5.0

    def test_geo_prefixed_fields(self, mock_http_client, mock_config):
        """Test that geo_* prefixed fields are accepted as aliases."""
        mock_http_client.get.return_value = {
            "geo_request_count": 200,
            "geo_request_limit": 5000,
            "geo_usage_percent": 4.0,
            "is_active": True,
            "message": "OK",
        }
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics()

        assert isinstance(response, V60AccountMetrics)
        assert response.request_count == 200
        assert response.request_limit == 5000
        assert response.usage_percent == 4.0

    def test_flat_fields_take_priority(self, mock_http_client, mock_config):
        """Test that flat fields are preferred when both flat and prefixed exist."""
        mock_http_client.get.return_value = {
            "request_count": 999,
            "core_request_count": 111,
            "request_limit": 50000,
            "core_request_limit": 11111,
            "usage_percent": 2.0,
            "core_usage_percent": 1.0,
            "is_active": True,
            "message": "OK",
        }
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetAccountMetrics()

        assert isinstance(response, V60AccountMetrics)
        assert response.request_count == 999
        assert response.request_limit == 50000
        assert response.usage_percent == 2.0


class TestGetRatesByPostalCode:
    """Test cases for GetRatesByPostalCode function."""

    def test_basic_request(
        self, mock_http_client, mock_config, sample_postal_code_response
    ):
        """Test basic postal code request."""
        mock_http_client.get.return_value = sample_postal_code_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetRatesByPostalCode("92694")

        assert isinstance(response, V60PostalCodeResponse)
        assert response.version == "v60"
        assert response.r_code == 100
        assert len(response.results) == 1
        assert response.results[0].geo_postal_code == "92694"
        mock_http_client.get.assert_called_once()

    def test_with_format_parameter(
        self, mock_http_client, mock_config, sample_postal_code_response
    ):
        """Test request with format parameter."""
        mock_http_client.get.return_value = sample_postal_code_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetRatesByPostalCode(postal_code="92694", format="json")

        assert isinstance(response, V60PostalCodeResponse)
        call_args = mock_http_client.get.call_args
        assert call_args[1]["params"]["postalcode"] == "92694"
        assert call_args[1]["params"]["format"] == "json"

    def test_invalid_postal_code(self, mock_http_client, mock_config):
        """Test validation of invalid postal code."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Postal code must be"):
            functions.GetRatesByPostalCode("invalid")

    def test_nine_digit_postal_code_rejected(self, mock_http_client, mock_config):
        """Test that 9-digit postal codes are rejected (API does not accept them)."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Postal code must be"):
            functions.GetRatesByPostalCode("92694-1234")

    def test_empty_postal_code(self, mock_http_client, mock_config):
        """Test validation of empty postal code."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxValidationError, match="Postal code cannot be empty"):
            functions.GetRatesByPostalCode("")

    def test_response_fields(
        self, mock_http_client, mock_config, sample_postal_code_response
    ):
        """Test all response fields are properly parsed."""
        mock_http_client.get.return_value = sample_postal_code_response
        functions = Functions(mock_http_client, mock_config)

        response = functions.GetRatesByPostalCode("92694")
        result = response.results[0]

        assert result.geo_city == "LADERA RANCH"
        assert result.geo_county == "ORANGE"
        assert result.geo_state == "CA"
        assert result.tax_sales == 0.0775
        assert result.tax_use == 0.0775


class TestCalculateCart:
    """Test cases for CalculateCart function."""

    def _build_request(self):
        """Build a sample CalculateCartRequest for testing."""
        return CalculateCartRequest(
            items=[
                CartItem(
                    customer_id="customer-453",
                    currency=CartCurrency(currency_code="USD"),
                    destination=CartAddress(
                        address="200 Spectrum Center Dr, Irvine, CA 92618-1905"
                    ),
                    origin=CartAddress(
                        address="323 Washington Ave N, Minneapolis, MN 55401-2427"
                    ),
                    line_items=[
                        CartLineItem(
                            item_id="item-1",
                            price=10.75,
                            quantity=1.5,
                        ),
                        CartLineItem(
                            item_id="item-2",
                            price=25.00,
                            quantity=2.0,
                            taxability_code=0,
                        ),
                    ],
                )
            ]
        )

    def test_basic_request(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test basic cart tax calculation request."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        response = functions.CalculateCart(request)

        assert isinstance(response, CalculateCartResponse)
        assert len(response.items) == 1
        assert response.items[0].cart_id == "ce4a1234-5678-90ab-cdef-1234567890ab"
        assert response.items[0].customer_id == "customer-453"
        mock_http_client.post.assert_called_once()

    def test_request_uses_correct_path(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that CalculateCart calls the correct API path."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        functions.CalculateCart(request)

        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == "/calculate/cart"

    def test_request_body_serialization(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that request body uses camelCase field names (by_alias)."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        functions.CalculateCart(request)

        call_args = mock_http_client.post.call_args
        json_body = call_args[1]["json"]

        # Verify top-level structure
        assert "items" in json_body
        assert len(json_body["items"]) == 1

        cart = json_body["items"][0]
        # Verify camelCase aliases are used
        assert "customerId" in cart
        assert cart["customerId"] == "customer-453"
        assert "lineItems" in cart
        assert len(cart["lineItems"]) == 2

        # Verify line item serialization
        line_item = cart["lineItems"][0]
        assert "itemId" in line_item
        assert line_item["itemId"] == "item-1"
        assert line_item["price"] == 10.75
        assert line_item["quantity"] == 1.5

    def test_optional_taxability_code_excluded_when_none(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that taxabilityCode is excluded from JSON when not set."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = CalculateCartRequest(
            items=[
                CartItem(
                    customer_id="cust-1",
                    currency=CartCurrency(currency_code="USD"),
                    destination=CartAddress(address="123 Main St"),
                    origin=CartAddress(address="456 Other St"),
                    line_items=[
                        CartLineItem(
                            item_id="item-1",
                            price=10.00,
                            quantity=1.0,
                        )
                    ],
                )
            ]
        )
        functions.CalculateCart(request)

        call_args = mock_http_client.post.call_args
        json_body = call_args[1]["json"]
        line_item = json_body["items"][0]["lineItems"][0]
        assert "taxabilityCode" not in line_item

    def test_optional_taxability_code_included_when_set(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that taxabilityCode is included in JSON when set."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        functions.CalculateCart(request)

        call_args = mock_http_client.post.call_args
        json_body = call_args[1]["json"]
        # Second line item has taxability_code=0
        line_item = json_body["items"][0]["lineItems"][1]
        assert "taxabilityCode" in line_item
        assert line_item["taxabilityCode"] == 0

    def test_response_line_items_parsed(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that response line items and tax details are properly parsed."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        response = functions.CalculateCart(request)

        cart = response.items[0]
        assert len(cart.line_items) == 2

        # First line item
        item1 = cart.line_items[0]
        assert item1.item_id == "item-1"
        assert item1.price == 10.75
        assert item1.quantity == 1.5
        assert item1.tax.rate == 0.09025
        assert item1.tax.amount == 1.45528

        # Second line item
        item2 = cart.line_items[1]
        assert item2.item_id == "item-2"
        assert item2.price == 25.00
        assert item2.quantity == 2.0
        assert item2.tax.rate == 0.09025
        assert item2.tax.amount == 4.5125

    def test_response_addresses_parsed(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that response addresses are properly parsed."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        response = functions.CalculateCart(request)

        cart = response.items[0]
        assert (
            cart.destination.address == "200 Spectrum Center Dr, Irvine, CA 92618-1905"
        )
        assert cart.origin.address == "323 Washington Ave N, Minneapolis, MN 55401-2427"

    def test_uses_ziptax_http_client(
        self, mock_http_client, mock_config, sample_calculate_cart_response
    ):
        """Test that CalculateCart uses the ZipTax HTTP client, not TaxCloud."""
        mock_http_client.post.return_value = sample_calculate_cart_response
        functions = Functions(mock_http_client, mock_config)

        request = self._build_request()
        functions.CalculateCart(request)

        # Should use the main ZipTax http_client, not taxcloud
        mock_http_client.post.assert_called_once()

    def test_price_must_be_greater_than_zero(self):
        """Test that CartLineItem rejects price <= 0."""
        with pytest.raises(ValidationError, match="greater than 0"):
            CartLineItem(item_id="item-1", price=0, quantity=1.0)

        with pytest.raises(ValidationError, match="greater than 0"):
            CartLineItem(item_id="item-1", price=-5.00, quantity=1.0)

    def test_quantity_must_be_greater_than_zero(self):
        """Test that CartLineItem rejects quantity <= 0."""
        with pytest.raises(ValidationError, match="greater than 0"):
            CartLineItem(item_id="item-1", price=10.00, quantity=0)

        with pytest.raises(ValidationError, match="greater than 0"):
            CartLineItem(item_id="item-1", price=10.00, quantity=-1.0)

    def test_items_must_contain_exactly_one_cart(self):
        """Test that CalculateCartRequest rejects empty or multi-cart arrays."""
        with pytest.raises(ValidationError, match="too_short"):
            CalculateCartRequest(items=[])

        cart = CartItem(
            customer_id="cust-1",
            currency=CartCurrency(currency_code="USD"),
            destination=CartAddress(address="123 Main St"),
            origin=CartAddress(address="456 Other St"),
            line_items=[CartLineItem(item_id="item-1", price=10.00, quantity=1.0)],
        )
        with pytest.raises(ValidationError, match="too_long"):
            CalculateCartRequest(items=[cart, cart])

    def test_line_items_must_have_at_least_one(self):
        """Test that CartItem rejects empty line_items."""
        with pytest.raises(ValidationError, match="too_short"):
            CartItem(
                customer_id="cust-1",
                currency=CartCurrency(currency_code="USD"),
                destination=CartAddress(address="123 Main St"),
                origin=CartAddress(address="456 Other St"),
                line_items=[],
            )

    def test_currency_code_must_be_usd(self):
        """Test that CartCurrency rejects non-USD currency codes."""
        with pytest.raises(ValidationError, match="literal_error"):
            CartCurrency(currency_code="EUR")


class TestTaxCloudFunctions:
    """Test cases for TaxCloud order management functions."""

    def test_check_taxcloud_config_raises_without_config(
        self, mock_http_client, mock_config
    ):
        """Test that TaxCloud functions raise without TaxCloud config."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(
            ZipTaxCloudConfigError,
            match="TaxCloud credentials not configured",
        ):
            functions._check_taxcloud_config()

    def test_create_order(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_order_response,
    ):
        """Test creating an order."""
        mock_taxcloud_http_client.post.return_value = sample_order_response
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = CreateOrderRequest(
            order_id="test-order-1",
            customer_id="customer-1",
            transaction_date="2024-01-15T09:30:00Z",
            completed_date="2024-01-15T09:30:00Z",
            origin={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            destination={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            line_items=[
                {
                    "index": 0,
                    "itemId": "item-1",
                    "price": 10.80,
                    "quantity": 1.5,
                    "tax": {"amount": 1.31, "rate": 0.0813},
                }
            ],
            currency={"currencyCode": "USD"},
        )

        response = functions.CreateOrder(request)

        assert isinstance(response, OrderResponse)
        assert response.order_id == "test-order-1"
        mock_taxcloud_http_client.post.assert_called_once()

    def test_get_order(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_order_response,
    ):
        """Test retrieving an order."""
        mock_taxcloud_http_client.get.return_value = sample_order_response
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        response = functions.GetOrder("test-order-1")

        assert isinstance(response, OrderResponse)
        assert response.order_id == "test-order-1"
        mock_taxcloud_http_client.get.assert_called_once()

    def test_update_order(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_order_response,
    ):
        """Test updating an order."""
        mock_taxcloud_http_client.patch.return_value = sample_order_response
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = UpdateOrderRequest(completed_date="2024-01-16T10:00:00Z")
        response = functions.UpdateOrder("test-order-1", request)

        assert isinstance(response, OrderResponse)
        assert response.order_id == "test-order-1"
        mock_taxcloud_http_client.patch.assert_called_once()

    def test_refund_order(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_refund_response,
    ):
        """Test refunding an order."""
        mock_taxcloud_http_client.post.return_value = [sample_refund_response]
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = RefundTransactionRequest(
            items=[{"itemId": "item-1", "quantity": 1.0}]
        )
        response = functions.RefundOrder("test-order-1", request)

        assert isinstance(response, list)
        assert len(response) == 1
        assert isinstance(response[0], RefundTransactionResponse)
        mock_taxcloud_http_client.post.assert_called_once()

    def test_refund_order_full(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_refund_response,
    ):
        """Test full refund (no request body)."""
        mock_taxcloud_http_client.post.return_value = [sample_refund_response]
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        response = functions.RefundOrder("test-order-1")

        assert isinstance(response, list)
        assert len(response) == 1
        mock_taxcloud_http_client.post.assert_called_once()

    def test_refund_order_single_dict_response(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_refund_response,
    ):
        """Test that RefundOrder handles API returning a single dict (not a list)."""
        # API sometimes returns a single dict for partial refunds
        mock_taxcloud_http_client.post.return_value = sample_refund_response
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = RefundTransactionRequest(
            items=[{"itemId": "item-1", "quantity": 1.0}]
        )
        response = functions.RefundOrder("test-order-1", request)

        assert isinstance(response, list)
        assert len(response) == 1
        assert isinstance(response[0], RefundTransactionResponse)
        assert response[0].connection_id == "test-connection-id-uuid"

    def test_create_order_without_taxcloud_config(self, mock_http_client, mock_config):
        """Test CreateOrder raises without TaxCloud config."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxCloudConfigError):
            functions.CreateOrder(
                CreateOrderRequest(
                    order_id="x",
                    customer_id="y",
                    transaction_date="2024-01-15T09:30:00Z",
                    completed_date="2024-01-15T09:30:00Z",
                    origin={
                        "line1": "123 Main",
                        "city": "City",
                        "state": "ST",
                        "zip": "12345",
                    },
                    destination={
                        "line1": "123 Main",
                        "city": "City",
                        "state": "ST",
                        "zip": "12345",
                    },
                    line_items=[
                        {
                            "index": 0,
                            "itemId": "i",
                            "price": 1.0,
                            "quantity": 1,
                            "tax": {"amount": 0.1, "rate": 0.1},
                        }
                    ],
                    currency={"currencyCode": "USD"},
                )
            )

    def test_create_order_with_valid_address_autocomplete(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
        sample_order_response,
    ):
        """Test CreateOrder accepts all valid address_autocomplete values."""
        mock_taxcloud_http_client.post.return_value = sample_order_response
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = CreateOrderRequest(
            order_id="test-order-1",
            customer_id="customer-1",
            transaction_date="2024-01-15T09:30:00Z",
            completed_date="2024-01-15T09:30:00Z",
            origin={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            destination={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            line_items=[
                {
                    "index": 0,
                    "itemId": "item-1",
                    "price": 10.80,
                    "quantity": 1.5,
                    "tax": {"amount": 1.31, "rate": 0.0813},
                }
            ],
            currency={"currencyCode": "USD"},
        )

        for value in ["none", "origin", "destination", "all"]:
            mock_taxcloud_http_client.post.reset_mock()
            response = functions.CreateOrder(request, address_autocomplete=value)
            assert isinstance(response, OrderResponse)

    def test_create_order_with_invalid_address_autocomplete(
        self,
        mock_http_client,
        mock_taxcloud_config,
        mock_taxcloud_http_client,
    ):
        """Test CreateOrder raises for invalid address_autocomplete."""
        functions = Functions(
            mock_http_client,
            mock_taxcloud_config,
            taxcloud_http_client=mock_taxcloud_http_client,
        )

        request = CreateOrderRequest(
            order_id="test-order-1",
            customer_id="customer-1",
            transaction_date="2024-01-15T09:30:00Z",
            completed_date="2024-01-15T09:30:00Z",
            origin={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            destination={
                "line1": "323 Washington Ave N",
                "city": "Minneapolis",
                "state": "MN",
                "zip": "55401",
            },
            line_items=[
                {
                    "index": 0,
                    "itemId": "item-1",
                    "price": 10.80,
                    "quantity": 1.5,
                    "tax": {"amount": 1.31, "rate": 0.0813},
                }
            ],
            currency={"currencyCode": "USD"},
        )

        with pytest.raises(
            ZipTaxValidationError,
            match="address_autocomplete must be one of",
        ):
            functions.CreateOrder(request, address_autocomplete="invalid")

    def test_get_order_without_taxcloud_config(self, mock_http_client, mock_config):
        """Test GetOrder raises without TaxCloud config."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxCloudConfigError):
            functions.GetOrder("test-order-1")
