"""Tests for API functions."""

import pytest

from ziptax.exceptions import ZipTaxValidationError
from ziptax.models import V60AccountMetrics, V60Response
from ziptax.resources.functions import Functions


class TestGetSalesTaxByAddress:
    """Test cases for GetSalesTaxByAddress function."""

    def test_basic_request(self, mock_http_client, sample_v60_response):
        """Test basic address request."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client)

        response = functions.GetSalesTaxByAddress(
            "200 Spectrum Center Drive, Irvine, CA 92618"
        )

        assert isinstance(response, V60Response)
        assert response.metadata.version == "v60"
        assert response.metadata.response.code == 100
        mock_http_client.get.assert_called_once()

    def test_with_optional_parameters(self, mock_http_client, sample_v60_response):
        """Test request with optional parameters."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client)

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

    def test_empty_address_validation(self, mock_http_client):
        """Test validation of empty address."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="Address cannot be empty"):
            functions.GetSalesTaxByAddress("")

    def test_address_too_long_validation(self, mock_http_client):
        """Test validation of address length."""
        functions = Functions(mock_http_client)
        long_address = "a" * 101

        with pytest.raises(ZipTaxValidationError, match="cannot exceed 100 characters"):
            functions.GetSalesTaxByAddress(long_address)

    def test_invalid_country_code(self, mock_http_client):
        """Test validation of country code."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="Country code must be one of"):
            functions.GetSalesTaxByAddress(
                "200 Spectrum Center Drive",
                country_code="INVALID",
            )

    def test_invalid_historical_format(self, mock_http_client):
        """Test validation of historical date format."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="must be in YYYY-MM format"):
            functions.GetSalesTaxByAddress(
                "200 Spectrum Center Drive",
                historical="2024-13-01",
            )


class TestGetSalesTaxByGeoLocation:
    """Test cases for GetSalesTaxByGeoLocation function."""

    def test_basic_request(self, mock_http_client, sample_v60_response):
        """Test basic geolocation request."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client)

        response = functions.GetSalesTaxByGeoLocation(
            lat="33.6489",
            lng="-117.8386",
        )

        assert isinstance(response, V60Response)
        assert response.metadata.version == "v60"
        assert response.metadata.response.code == 100
        mock_http_client.get.assert_called_once()

    def test_with_optional_parameters(self, mock_http_client, sample_v60_response):
        """Test request with optional parameters."""
        mock_http_client.get.return_value = sample_v60_response
        functions = Functions(mock_http_client)

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

    def test_empty_coordinates_validation(self, mock_http_client):
        """Test validation of empty coordinates."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="cannot be empty"):
            functions.GetSalesTaxByGeoLocation(lat="", lng="")

    def test_invalid_latitude_range(self, mock_http_client):
        """Test validation of latitude range."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="Latitude must be between"):
            functions.GetSalesTaxByGeoLocation(lat="100.0", lng="-117.8386")

    def test_invalid_longitude_range(self, mock_http_client):
        """Test validation of longitude range."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="Longitude must be between"):
            functions.GetSalesTaxByGeoLocation(lat="33.6489", lng="200.0")

    def test_invalid_coordinate_format(self, mock_http_client):
        """Test validation of coordinate format."""
        functions = Functions(mock_http_client)

        with pytest.raises(ZipTaxValidationError, match="must be valid numbers"):
            functions.GetSalesTaxByGeoLocation(lat="invalid", lng="-117.8386")


class TestGetAccountMetrics:
    """Test cases for GetAccountMetrics function."""

    def test_basic_request(self, mock_http_client, sample_account_metrics):
        """Test basic account metrics request."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client)

        response = functions.GetAccountMetrics()

        assert isinstance(response, V60AccountMetrics)
        assert response.core_request_count == 15595
        assert response.geo_enabled is True
        assert response.is_active is True
        mock_http_client.get.assert_called_once()

    def test_with_key_parameter(self, mock_http_client, sample_account_metrics):
        """Test request with key parameter."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client)

        response = functions.GetAccountMetrics(key="test-key")

        assert isinstance(response, V60AccountMetrics)
        call_args = mock_http_client.get.call_args
        assert call_args[1]["params"]["key"] == "test-key"

    def test_response_fields(self, mock_http_client, sample_account_metrics):
        """Test all response fields are properly parsed."""
        mock_http_client.get.return_value = sample_account_metrics
        functions = Functions(mock_http_client)

        response = functions.GetAccountMetrics()

        assert response.core_request_count == 15595
        assert response.core_request_limit == 1000000
        assert response.core_usage_percent == 1.5595
        assert response.geo_enabled is True
        assert response.geo_request_count == 43891
        assert response.geo_request_limit == 1000000
        assert response.geo_usage_percent == 4.3891
        assert response.is_active is True
        assert "support@zip.tax" in response.message
