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
def mock_taxcloud_config(mock_api_key):
    """Mock configuration with TaxCloud credentials for testing."""
    return Config(
        api_key=mock_api_key,
        base_url="https://api.zip-tax.com",
        timeout=30,
        max_retries=3,
        retry_delay=1.0,
        taxcloud_connection_id="test-connection-id-uuid",
        taxcloud_api_key="test-taxcloud-api-key-1234567890",
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
def mock_taxcloud_http_client():
    """Mock HTTP client for TaxCloud API testing."""
    client = Mock(spec=HTTPClient)
    client.api_key = "test-taxcloud-api-key-1234567890"
    client.base_url = "https://api.v3.taxcloud.com"
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
    """Sample V60AccountMetrics data for testing (matches live API format)."""
    return {
        "request_count": 15595,
        "request_limit": 1000000,
        "usage_percent": 1.5595,
        "is_active": True,
        "message": "Contact support@zip.tax to modify your account",
    }


@pytest.fixture
def sample_postal_code_response():
    """Sample V60PostalCodeResponse data for testing."""
    return {
        "version": "v60",
        "rCode": 100,
        "results": [
            {
                "geoPostalCode": "92694",
                "geoCity": "LADERA RANCH",
                "geoCounty": "ORANGE",
                "geoState": "CA",
                "taxSales": 0.0775,
                "taxUse": 0.0775,
                "txbService": "N",
                "txbFreight": "N",
                "stateSalesTax": 0.06,
                "stateUseTax": 0.06,
                "citySalesTax": 0.0,
                "cityUseTax": 0.0,
                "cityTaxCode": "",
                "countySalesTax": 0.0025,
                "countyUseTax": 0.0025,
                "countyTaxCode": "30",
                "districtSalesTax": 0.015,
                "districtUseTax": 0.015,
                "district1Code": "26",
                "district1SalesTax": 0.005,
                "district1UseTax": 0.005,
                "district2Code": "38",
                "district2SalesTax": 0.01,
                "district2UseTax": 0.01,
                "district3Code": "",
                "district3SalesTax": 0.0,
                "district3UseTax": 0.0,
                "district4Code": "",
                "district4SalesTax": 0.0,
                "district4UseTax": 0.0,
                "district5Code": "",
                "district5SalesTax": 0.0,
                "district5UseTax": 0.0,
                "originDestination": "D",
            }
        ],
        "addressDetail": {
            "normalizedAddress": "",
            "incorporated": "",
            "geoLat": 0.0,
            "geoLng": 0.0,
        },
    }


@pytest.fixture
def sample_calculate_cart_response():
    """Sample CalculateCartResponse data for testing (matches actual API format)."""
    return {
        "items": [
            {
                "cartId": "ce4a1234-5678-90ab-cdef-1234567890ab",
                "customerId": "customer-453",
                "destination": {
                    "address": "200 Spectrum Center Dr, Irvine, CA 92618-1905"
                },
                "origin": {
                    "address": "323 Washington Ave N, Minneapolis, MN 55401-2427"
                },
                "lineItems": [
                    {
                        "itemId": "item-1",
                        "price": 10.75,
                        "quantity": 1.5,
                        "tax": {"rate": 0.09025, "amount": 1.45528},
                    },
                    {
                        "itemId": "item-2",
                        "price": 25.00,
                        "quantity": 2.0,
                        "tax": {"rate": 0.09025, "amount": 4.5125},
                    },
                ],
            }
        ]
    }


@pytest.fixture
def sample_order_response():
    """Sample TaxCloud OrderResponse data for testing."""
    return {
        "orderId": "test-order-1",
        "customerId": "customer-1",
        "connectionId": "test-connection-id-uuid",
        "transactionDate": "2024-01-15T09:30:00Z",
        "completedDate": "2024-01-15T09:30:00Z",
        "origin": {
            "line1": "323 Washington Ave N",
            "city": "Minneapolis",
            "state": "MN",
            "zip": "55401",
            "countryCode": "US",
        },
        "destination": {
            "line1": "323 Washington Ave N",
            "city": "Minneapolis",
            "state": "MN",
            "zip": "55401",
            "countryCode": "US",
        },
        "lineItems": [
            {
                "index": 0,
                "itemId": "item-1",
                "price": 10.80,
                "quantity": 1.5,
                "tax": {"amount": 1.31, "rate": 0.0813},
                "tic": 0,
            }
        ],
        "currency": {"currencyCode": "USD"},
        "deliveredBySeller": False,
        "excludeFromFiling": False,
    }


@pytest.fixture
def sample_refund_response():
    """Sample TaxCloud RefundTransactionResponse data for testing."""
    return {
        "connectionId": "test-connection-id-uuid",
        "createdDate": "2024-01-16T10:00:00Z",
        "items": [
            {
                "index": 0,
                "itemId": "item-1",
                "price": 10.80,
                "quantity": 1.0,
                "tax": {"amount": 0.88},
                "tic": 0,
            }
        ],
    }
