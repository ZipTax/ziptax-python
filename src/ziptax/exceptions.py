"""Exception classes for the ZipTax SDK."""

from typing import Optional, Any


class ZipTaxError(Exception):
    """Base exception for all ZipTax SDK errors."""

    def __init__(self, message: str, response: Optional[Any] = None):
        """Initialize ZipTaxError.

        Args:
            message: Error message
            response: Optional HTTP response object
        """
        super().__init__(message)
        self.message = message
        self.response = response


class ZipTaxAPIError(ZipTaxError):
    """Exception raised for API-level errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
    ):
        """Initialize ZipTaxAPIError.

        Args:
            message: Error message
            status_code: HTTP status code
            response: Optional HTTP response object
        """
        super().__init__(message, response)
        self.status_code = status_code


class ZipTaxAuthenticationError(ZipTaxAPIError):
    """Exception raised for authentication failures (401)."""

    pass


class ZipTaxAuthorizationError(ZipTaxAPIError):
    """Exception raised for authorization failures (403)."""

    pass


class ZipTaxNotFoundError(ZipTaxAPIError):
    """Exception raised when a resource is not found (404)."""

    pass


class ZipTaxRateLimitError(ZipTaxAPIError):
    """Exception raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response: Optional[Any] = None,
    ):
        """Initialize ZipTaxRateLimitError.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
            status_code: HTTP status code
            response: Optional HTTP response object
        """
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class ZipTaxServerError(ZipTaxAPIError):
    """Exception raised for server errors (5xx)."""

    pass


class ZipTaxValidationError(ZipTaxError):
    """Exception raised for input validation errors."""

    pass


class ZipTaxConnectionError(ZipTaxError):
    """Exception raised for connection-related errors."""

    pass


class ZipTaxTimeoutError(ZipTaxError):
    """Exception raised when a request times out."""

    pass


class ZipTaxRetryError(ZipTaxError):
    """Exception raised when max retries are exceeded."""

    def __init__(self, message: str, attempts: int, last_exception: Optional[Exception] = None):
        """Initialize ZipTaxRetryError.

        Args:
            message: Error message
            attempts: Number of retry attempts made
            last_exception: The last exception that occurred
        """
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception
