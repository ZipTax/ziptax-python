"""Tests for HTTP client utilities."""

from unittest.mock import Mock, patch

import pytest
import requests

from ziptax.exceptions import (
    ZipTaxAPIError,
    ZipTaxAuthenticationError,
    ZipTaxAuthorizationError,
    ZipTaxConnectionError,
    ZipTaxNotFoundError,
    ZipTaxRateLimitError,
    ZipTaxServerError,
    ZipTaxTimeoutError,
)
from ziptax.utils.http import HTTPClient


@pytest.fixture
def http_client():
    """Create an HTTPClient instance for testing."""
    return HTTPClient(
        api_key="test-key-123",
        base_url="https://api.zip-tax.com",
        timeout=30,
    )


def test_http_client_initialization(http_client):
    """Test HTTPClient initialization."""
    assert http_client.api_key == "test-key-123"
    assert http_client.base_url == "https://api.zip-tax.com"
    assert http_client.timeout == 30
    assert "X-API-Key" in http_client.session.headers
    assert http_client.session.headers["X-API-Key"] == "test-key-123"


def test_http_client_context_manager():
    """Test HTTPClient as context manager."""
    with HTTPClient("test-key", "https://api.zip-tax.com", 30) as client:
        assert client.api_key == "test-key"
    # Session should be closed after exiting context


def test_get_success(http_client):
    """Test successful GET request."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        result = http_client.get("/test", params={"key": "value"})

    assert result == {"data": "test"}


def test_get_with_headers(http_client):
    """Test GET request with custom headers."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch.object(
        http_client.session, "get", return_value=mock_response
    ) as mock_get:
        result = http_client.get("/test", headers={"Custom": "header"})

    assert result == {"data": "test"}
    mock_get.assert_called_once()


def test_get_authentication_error(http_client):
    """Test GET request with 401 authentication error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.json.return_value = {"message": "Invalid API key"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxAuthenticationError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_get_authorization_error(http_client):
    """Test GET request with 403 authorization error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_response.json.return_value = {"message": "Access denied"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxAuthorizationError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 403
    assert "Authorization failed" in str(exc_info.value)


def test_get_not_found_error(http_client):
    """Test GET request with 404 not found error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.json.return_value = {"message": "Resource not found"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxNotFoundError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 404
    assert "Resource not found" in str(exc_info.value)


def test_get_rate_limit_error(http_client):
    """Test GET request with 429 rate limit error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"
    mock_response.headers = {"Retry-After": "60"}
    mock_response.json.return_value = {"message": "Rate limit exceeded"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxRateLimitError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 60
    assert "Rate limit exceeded" in str(exc_info.value)


def test_get_rate_limit_error_no_retry_after(http_client):
    """Test GET request with 429 rate limit error without Retry-After header."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"
    mock_response.headers = {}
    mock_response.json.return_value = {"message": "Rate limit exceeded"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxRateLimitError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.retry_after is None


def test_get_server_error(http_client):
    """Test GET request with 500 server error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.return_value = {"message": "Server error"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 500
    assert "Server error" in str(exc_info.value)


def test_get_server_error_503(http_client):
    """Test GET request with 503 service unavailable error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_response.text = "Service Unavailable"
    mock_response.json.return_value = {"message": "Service unavailable"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 503


def test_get_generic_error(http_client):
    """Test GET request with generic API error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.json.return_value = {"message": "Invalid request"}

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxAPIError) as exc_info:
            http_client.get("/test")

    assert exc_info.value.status_code == 400
    assert "API error" in str(exc_info.value)


def test_get_error_without_json(http_client):
    """Test GET request error when response is not JSON."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.get("/test")

    assert "Internal Server Error" in str(exc_info.value)


def test_get_error_empty_response(http_client):
    """Test GET request error with empty response text."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = ""
    mock_response.json.side_effect = ValueError("Not JSON")

    with patch.object(http_client.session, "get", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.get("/test")

    assert "HTTP 500 error" in str(exc_info.value)


def test_get_timeout_error(http_client):
    """Test GET request with timeout error."""
    with patch.object(
        http_client.session, "get", side_effect=requests.exceptions.Timeout("Timeout")
    ):
        with pytest.raises(ZipTaxTimeoutError) as exc_info:
            http_client.get("/test")

    assert "Request timed out after 30s" in str(exc_info.value)


def test_get_connection_error(http_client):
    """Test GET request with connection error."""
    with patch.object(
        http_client.session,
        "get",
        side_effect=requests.exceptions.ConnectionError("Connection failed"),
    ):
        with pytest.raises(ZipTaxConnectionError) as exc_info:
            http_client.get("/test")

    assert "Connection error" in str(exc_info.value)


def test_get_unexpected_error(http_client):
    """Test GET request with unexpected error."""
    with patch.object(
        http_client.session, "get", side_effect=RuntimeError("Unexpected error")
    ):
        with pytest.raises(ZipTaxAPIError) as exc_info:
            http_client.get("/test")

    assert "Unexpected error" in str(exc_info.value)


def test_close(http_client):
    """Test closing the HTTP client session."""
    with patch.object(http_client.session, "close") as mock_close:
        http_client.close()
        mock_close.assert_called_once()


# =============================================================================
# POST method tests
# =============================================================================


def test_post_success(http_client):
    """Test successful POST request."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"orderId": "test-1"}

    with patch.object(http_client.session, "post", return_value=mock_response):
        result = http_client.post("/test", json={"key": "value"})

    assert result == {"orderId": "test-1"}


def test_post_with_params(http_client):
    """Test POST request with query parameters."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch.object(
        http_client.session, "post", return_value=mock_response
    ) as mock_post:
        result = http_client.post(
            "/test", json={"body": "data"}, params={"param1": "value1"}
        )

    assert result == {"data": "test"}
    mock_post.assert_called_once()


def test_post_authentication_error(http_client):
    """Test POST request with 401 authentication error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_response.json.return_value = {"message": "Invalid API key"}

    with patch.object(http_client.session, "post", return_value=mock_response):
        with pytest.raises(ZipTaxAuthenticationError) as exc_info:
            http_client.post("/test", json={})

    assert exc_info.value.status_code == 401


def test_post_server_error(http_client):
    """Test POST request with 500 server error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.return_value = {"message": "Server error"}

    with patch.object(http_client.session, "post", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.post("/test", json={})

    assert exc_info.value.status_code == 500


def test_post_timeout_error(http_client):
    """Test POST request with timeout error."""
    with patch.object(
        http_client.session,
        "post",
        side_effect=requests.exceptions.Timeout("Timeout"),
    ):
        with pytest.raises(ZipTaxTimeoutError):
            http_client.post("/test", json={})


def test_post_connection_error(http_client):
    """Test POST request with connection error."""
    with patch.object(
        http_client.session,
        "post",
        side_effect=requests.exceptions.ConnectionError("Connection failed"),
    ):
        with pytest.raises(ZipTaxConnectionError):
            http_client.post("/test", json={})


# =============================================================================
# PATCH method tests
# =============================================================================


def test_patch_success(http_client):
    """Test successful PATCH request."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"orderId": "test-1", "updated": True}

    with patch.object(http_client.session, "patch", return_value=mock_response):
        result = http_client.patch("/test", json={"completedDate": "2024-01"})

    assert result == {"orderId": "test-1", "updated": True}


def test_patch_with_params(http_client):
    """Test PATCH request with query parameters."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch.object(
        http_client.session, "patch", return_value=mock_response
    ) as mock_patch:
        result = http_client.patch(
            "/test", json={"body": "data"}, params={"param1": "value1"}
        )

    assert result == {"data": "test"}
    mock_patch.assert_called_once()


def test_patch_not_found_error(http_client):
    """Test PATCH request with 404 not found error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.json.return_value = {"message": "Order not found"}

    with patch.object(http_client.session, "patch", return_value=mock_response):
        with pytest.raises(ZipTaxNotFoundError) as exc_info:
            http_client.patch("/test", json={})

    assert exc_info.value.status_code == 404


def test_patch_server_error(http_client):
    """Test PATCH request with 500 server error."""
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.return_value = {"message": "Server error"}

    with patch.object(http_client.session, "patch", return_value=mock_response):
        with pytest.raises(ZipTaxServerError) as exc_info:
            http_client.patch("/test", json={})

    assert exc_info.value.status_code == 500


def test_patch_timeout_error(http_client):
    """Test PATCH request with timeout error."""
    with patch.object(
        http_client.session,
        "patch",
        side_effect=requests.exceptions.Timeout("Timeout"),
    ):
        with pytest.raises(ZipTaxTimeoutError):
            http_client.patch("/test", json={})


def test_patch_connection_error(http_client):
    """Test PATCH request with connection error."""
    with patch.object(
        http_client.session,
        "patch",
        side_effect=requests.exceptions.ConnectionError("Connection failed"),
    ):
        with pytest.raises(ZipTaxConnectionError):
            http_client.patch("/test", json={})
