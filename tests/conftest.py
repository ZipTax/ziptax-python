"""Pytest configuration and fixtures."""

from unittest.mock import Mock

import pytest

from ziptax import ZipTaxClient
from ziptax.config import Config
from ziptax.utils.http import HTTPClient


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-1234567890"


@pytest.fixture
def mock_config(mock_api_key):
    """Mock configuration for testing."""
    return Config(
        api_key=mock_api_key,
        base_url="https://api.zip-tax.com",
        timeout=30,
        max_retries=3,
        retry_delay=1.0,
    )


@pytest.fixture
def mock_http_client(mock_api_key):
    """Mock HTTP client for testing."""
    client = Mock(spec=HTTPClient)
    client.api_key = mock_api_key
    client.base_url = "https://api.zip-tax.com"
    client.timeout = 30
    return client


@pytest.fixture
def mock_client(mock_config, mock_http_client, monkeypatch):
    """Mock ZipTaxClient for testing."""
    client = ZipTaxClient(mock_config)
    client._http_client = mock_http_client
    return client


@pytest.fixture
def sample_v60_response():
    """Sample V60Response data for testing (matches actual API format)."""
    return {
        "metadata": {
            "version": "v60",
            "response": {
                "code": 100,
                "name": "RESPONSE_CODE_SUCCESS",
                "message": "Successful API Request.",
                "definition": "http://api.zip-tax.com/request/v60/schema",
            },
        },
        "baseRates": [
            {
                "rate": 0.06,
                "jurType": "US_STATE_SALES_TAX",
                "jurName": "CA",
                "jurDescription": "US State Sales Tax",
                "jurTaxCode": "06",
            }
        ],
        "service": {
            "adjustmentType": "SERVICE_TAXABLE",
            "taxable": "N",
            "description": "Services non-taxable",
        },
        "shipping": {
            "adjustmentType": "FREIGHT_TAXABLE",
            "taxable": "N",
            "description": "Freight non-taxable",
        },
        "sourcingRules": {
            "adjustmentType": "ORIGIN_DESTINATION",
            "description": "Destination Based Taxation",
            "value": "D",
        },
        "taxSummaries": [
            {
                "rate": 0.0775,
                "taxType": "SALES_TAX",
                "summaryName": "Total Base Sales Tax",
                "displayRates": [{"name": "Total Rate", "rate": 0.0775}],
            }
        ],
        "addressDetail": {
            "normalizedAddress": (
                "200 Spectrum Center Dr, Irvine, CA 92618-5003, United States"
            ),
            "incorporated": "true",
            "geoLat": 33.65253,
            "geoLng": -117.74794,
        },
    }


@pytest.fixture
def sample_account_metrics():
    """Sample V60AccountMetrics data for testing."""
    return {
        "core_request_count": 15595,
        "core_request_limit": 1000000,
        "core_usage_percent": 1.5595,
        "geo_enabled": True,
        "geo_request_count": 43891,
        "geo_request_limit": 1000000,
        "geo_usage_percent": 4.3891,
        "is_active": True,
        "message": "Contact support@zip.tax to modify your account",
    }
