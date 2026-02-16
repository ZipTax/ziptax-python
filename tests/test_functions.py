"""Tests for API functions."""

import pytest

from ziptax.exceptions import ZipTaxCloudConfigError, ZipTaxValidationError
from ziptax.models import (
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
            historical="2024-01",
            format="json",
        )

        assert isinstance(response, V60Response)
        call_args = mock_http_client.get.call_args
        assert (
            call_args[1]["params"]["address"]
            == "200 Spectrum Center Drive, Irvine, CA 92618"
        )
        assert call_args[1]["params"]["taxabilityCode"] == "12345"
        assert call_args[1]["params"]["historical"] == "2024-01"

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

        with pytest.raises(ZipTaxValidationError, match="must be in YYYY-MM format"):
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
            historical="2024-01",
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

    def test_get_order_without_taxcloud_config(self, mock_http_client, mock_config):
        """Test GetOrder raises without TaxCloud config."""
        functions = Functions(mock_http_client, mock_config)

        with pytest.raises(ZipTaxCloudConfigError):
            functions.GetOrder("test-order-1")
