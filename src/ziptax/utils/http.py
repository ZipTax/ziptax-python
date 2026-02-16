"""HTTP utilities for the ZipTax SDK."""

import logging
from typing import Any, Dict, Optional, cast

import requests

from ..exceptions import (
    ZipTaxAPIError,
    ZipTaxAuthenticationError,
    ZipTaxAuthorizationError,
    ZipTaxConnectionError,
    ZipTaxNotFoundError,
    ZipTaxRateLimitError,
    ZipTaxServerError,
    ZipTaxTimeoutError,
)

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for making requests to the ZipTax API."""

    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        """Initialize HTTPClient.

        Args:
            api_key: ZipTax API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response object

        Raises:
            ZipTaxAuthenticationError: For 401 errors
            ZipTaxAuthorizationError: For 403 errors
            ZipTaxNotFoundError: For 404 errors
            ZipTaxRateLimitError: For 429 errors
            ZipTaxServerError: For 5xx errors
            ZipTaxAPIError: For other errors
        """
        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
        except Exception:
            message = response.text or f"HTTP {status_code} error"

        if status_code == 401:
            raise ZipTaxAuthenticationError(
                message=f"Authentication failed: {message}",
                status_code=status_code,
                response=response,
            )
        elif status_code == 403:
            raise ZipTaxAuthorizationError(
                message=f"Authorization failed: {message}",
                status_code=status_code,
                response=response,
            )
        elif status_code == 404:
            raise ZipTaxNotFoundError(
                message=f"Resource not found: {message}",
                status_code=status_code,
                response=response,
            )
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise ZipTaxRateLimitError(
                message=f"Rate limit exceeded: {message}",
                retry_after=int(retry_after) if retry_after else None,
                status_code=status_code,
                response=response,
            )
        elif 500 <= status_code < 600:
            raise ZipTaxServerError(
                message=f"Server error: {message}",
                status_code=status_code,
                response=response,
            )
        else:
            raise ZipTaxAPIError(
                message=f"API error: {message}",
                status_code=status_code,
                response=response,
            )

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            ZipTaxConnectionError: For connection errors
            ZipTaxTimeoutError: For timeout errors
            ZipTaxAPIError: For API errors
        """
        url = f"{self.base_url}{path}"
        logger.debug(f"GET {url} with params: {params}")

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            logger.debug(f"Response status: {response.status_code}")

            if not response.ok:
                self._handle_error_response(response)

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.Timeout as e:
            raise ZipTaxTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ZipTaxConnectionError(f"Connection error: {e}")
        except (ZipTaxAPIError, ZipTaxTimeoutError, ZipTaxConnectionError):
            raise
        except Exception as e:
            raise ZipTaxAPIError(f"Unexpected error: {e}")

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make a POST request to the API.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data (dict or list)

        Raises:
            ZipTaxConnectionError: For connection errors
            ZipTaxTimeoutError: For timeout errors
            ZipTaxAPIError: For API errors
        """
        url = f"{self.base_url}{path}"
        logger.debug(f"POST {url} with json: {json}, params: {params}")

        try:
            response = self.session.post(
                url,
                json=json,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            logger.debug(f"Response status: {response.status_code}")

            if not response.ok:
                self._handle_error_response(response)

            return response.json()

        except requests.exceptions.Timeout as e:
            raise ZipTaxTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ZipTaxConnectionError(f"Connection error: {e}")
        except (ZipTaxAPIError, ZipTaxTimeoutError, ZipTaxConnectionError):
            raise
        except Exception as e:
            raise ZipTaxAPIError(f"Unexpected error: {e}")

    def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PATCH request to the API.

        Args:
            path: API endpoint path
            json: JSON request body
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            ZipTaxConnectionError: For connection errors
            ZipTaxTimeoutError: For timeout errors
            ZipTaxAPIError: For API errors
        """
        url = f"{self.base_url}{path}"
        logger.debug(f"PATCH {url} with json: {json}, params: {params}")

        try:
            response = self.session.patch(
                url,
                json=json,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            logger.debug(f"Response status: {response.status_code}")

            if not response.ok:
                self._handle_error_response(response)

            return cast(Dict[str, Any], response.json())

        except requests.exceptions.Timeout as e:
            raise ZipTaxTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ZipTaxConnectionError(f"Connection error: {e}")
        except (ZipTaxAPIError, ZipTaxTimeoutError, ZipTaxConnectionError):
            raise
        except Exception as e:
            raise ZipTaxAPIError(f"Unexpected error: {e}")

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
