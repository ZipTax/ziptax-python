"""Tests for the ZipTaxClient."""

import pytest

from ziptax import ZipTaxClient
from ziptax.exceptions import ZipTaxValidationError


class TestZipTaxClient:
    """Test cases for ZipTaxClient."""

    def test_api_key_method(self, mock_api_key):
        """Test creating client with api_key class method."""
        client = ZipTaxClient.api_key(mock_api_key)

        assert client is not None
        assert isinstance(client, ZipTaxClient)
        assert client.config.api_key == mock_api_key
        assert client.config.base_url == "https://api.zip-tax.com"
        assert client.config.timeout == 30
        assert client.config.max_retries == 3

    def test_api_key_with_custom_config(self, mock_api_key):
        """Test creating client with custom configuration."""
        client = ZipTaxClient.api_key(
            mock_api_key,
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
        )

        assert client.config.base_url == "https://custom.api.com"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
        assert client.config.retry_delay == 2.0

    def test_api_key_validation(self):
        """Test API key validation."""
        with pytest.raises(ZipTaxValidationError, match="API key cannot be empty"):
            ZipTaxClient.api_key("")

        with pytest.raises(ZipTaxValidationError, match="too short"):
            ZipTaxClient.api_key("short")

    def test_direct_initialization(self, mock_config):
        """Test direct initialization with Config object."""
        client = ZipTaxClient(mock_config)

        assert client is not None
        assert client.config == mock_config

    def test_config_dict_access(self, mock_api_key):
        """Test config dict-style access."""
        client = ZipTaxClient.api_key(mock_api_key)

        # Test getting values
        assert client.config["timeout"] == 30
        assert client.config["max_retries"] == 3

        # Test setting values
        client.config["timeout"] = 60
        assert client.config.timeout == 60

        # Test custom values
        client.config["format"] = "json"
        assert client.config["format"] == "json"

    def test_config_get_with_default(self, mock_api_key):
        """Test config.get() returns default for missing keys."""
        client = ZipTaxClient.api_key(mock_api_key)

        # Existing key returns its value, not the default
        assert client.config.get("timeout", 999) == 30

        # Missing key returns the provided default
        assert client.config.get("nonexistent", "fallback") == "fallback"
        assert client.config.get("nonexistent", 42) == 42

        # Missing key with no default returns None
        assert client.config.get("nonexistent") is None

    def test_config_getitem_raises_for_missing_key(self, mock_api_key):
        """Test config[key] raises KeyError for missing keys."""
        client = ZipTaxClient.api_key(mock_api_key)

        with pytest.raises(KeyError):
            _ = client.config["nonexistent"]

    def test_context_manager(self, mock_api_key):
        """Test using client as context manager."""
        with ZipTaxClient.api_key(mock_api_key) as client:
            assert client is not None
            assert isinstance(client, ZipTaxClient)

    def test_repr(self, mock_api_key):
        """Test string representation of client."""
        client = ZipTaxClient.api_key(mock_api_key)
        repr_str = repr(client)

        assert "ZipTaxClient" in repr_str
        assert "https://api.zip-tax.com" in repr_str

    def test_request_attribute(self, mock_api_key):
        """Test that client has request attribute."""
        client = ZipTaxClient.api_key(mock_api_key)

        assert hasattr(client, "request")
        assert hasattr(client.request, "GetSalesTaxByAddress")
        assert hasattr(client.request, "GetSalesTaxByGeoLocation")
        assert hasattr(client.request, "GetAccountMetrics")
