"""Error handling example for the ZipTax SDK."""

from ziptax import (
    ZipTaxClient,
    ZipTaxError,
    ZipTaxAPIError,
    ZipTaxAuthenticationError,
    ZipTaxAuthorizationError,
    ZipTaxNotFoundError,
    ZipTaxRateLimitError,
    ZipTaxServerError,
    ZipTaxValidationError,
    ZipTaxConnectionError,
    ZipTaxTimeoutError,
    ZipTaxRetryError,
)


def example_validation_errors():
    """Example of handling validation errors."""
    print("=" * 60)
    print("Example 1: Validation Errors")
    print("=" * 60)

    try:
        # This will fail due to invalid API key
        client = ZipTaxClient.api_key("short")
    except ZipTaxValidationError as e:
        print(f"Validation Error: {e.message}")
        print("Fix: Provide a valid API key")

    client = ZipTaxClient.api_key("valid-api-key-1234567890")

    try:
        # This will fail due to empty address
        response = client.request.GetSalesTaxByAddress("")
    except ZipTaxValidationError as e:
        print(f"\nValidation Error: {e.message}")
        print("Fix: Provide a non-empty address")

    try:
        # This will fail due to address being too long
        long_address = "a" * 101
        response = client.request.GetSalesTaxByAddress(long_address)
    except ZipTaxValidationError as e:
        print(f"\nValidation Error: {e.message}")
        print("Fix: Limit address to 100 characters")

    try:
        # This will fail due to invalid country code
        response = client.request.GetSalesTaxByAddress(
            "123 Main St",
            country_code="INVALID"
        )
    except ZipTaxValidationError as e:
        print(f"\nValidation Error: {e.message}")
        print("Fix: Use 'USA' or 'CAN' as country code")

    try:
        # This will fail due to invalid historical date format
        response = client.request.GetSalesTaxByAddress(
            "123 Main St",
            historical="2024-13-01"
        )
    except ZipTaxValidationError as e:
        print(f"\nValidation Error: {e.message}")
        print("Fix: Use YYYY-MM format (e.g., '2024-01')")

    try:
        # This will fail due to invalid coordinates
        response = client.request.GetSalesTaxByGeoLocation(
            lat="invalid",
            lng="-117.8386"
        )
    except ZipTaxValidationError as e:
        print(f"\nValidation Error: {e.message}")
        print("Fix: Provide valid numeric coordinates")

    client.close()


def example_api_errors():
    """Example of handling API errors."""
    print("\n" + "=" * 60)
    print("Example 2: API Errors")
    print("=" * 60)

    # Authentication Error (401)
    try:
        client = ZipTaxClient.api_key("invalid-api-key-1234567890")
        response = client.request.GetSalesTaxByAddress("123 Main St")
    except ZipTaxAuthenticationError as e:
        print(f"Authentication Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        print("Fix: Check your API key is correct")
    except Exception as e:
        print(f"Note: This example requires a real API call to trigger: {type(e).__name__}")

    # Authorization Error (403)
    try:
        # This would happen if API key is valid but lacks permissions
        client = ZipTaxClient.api_key("valid-but-unauthorized-key")
        response = client.request.GetAccountMetrics()
    except ZipTaxAuthorizationError as e:
        print(f"\nAuthorization Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        print("Fix: Check your API key has the required permissions")
    except Exception as e:
        print(f"Note: This example requires a real API call to trigger: {type(e).__name__}")

    # Rate Limit Error (429)
    try:
        # This would happen if you exceed rate limits
        client = ZipTaxClient.api_key("your-api-key-here")
        # Make many rapid requests...
        for i in range(1000):
            response = client.request.GetSalesTaxByAddress(f"{i} Main St")
    except ZipTaxRateLimitError as e:
        print(f"\nRate Limit Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        if e.retry_after:
            print(f"Retry After: {e.retry_after} seconds")
        print("Fix: Implement rate limiting or wait before retrying")
    except Exception as e:
        print(f"Note: This example requires hitting rate limits: {type(e).__name__}")


def example_connection_errors():
    """Example of handling connection errors."""
    print("\n" + "=" * 60)
    print("Example 3: Connection Errors")
    print("=" * 60)

    # Timeout Error
    try:
        client = ZipTaxClient.api_key(
            "your-api-key-here",
            timeout=0.001  # Very short timeout to trigger error
        )
        response = client.request.GetSalesTaxByAddress("123 Main St")
    except ZipTaxTimeoutError as e:
        print(f"Timeout Error: {e.message}")
        print("Fix: Increase timeout or check network connection")
    except Exception as e:
        print(f"Note: This example requires a real API call: {type(e).__name__}")

    # Connection Error
    try:
        client = ZipTaxClient.api_key(
            "your-api-key-here",
            base_url="https://invalid-domain-that-does-not-exist.com"
        )
        response = client.request.GetSalesTaxByAddress("123 Main St")
    except ZipTaxConnectionError as e:
        print(f"\nConnection Error: {e.message}")
        print("Fix: Check base URL and network connection")
    except Exception as e:
        print(f"Note: This example requires a real API call: {type(e).__name__}")


def example_retry_errors():
    """Example of handling retry errors."""
    print("\n" + "=" * 60)
    print("Example 4: Retry Errors")
    print("=" * 60)

    try:
        # Configure client with limited retries
        client = ZipTaxClient.api_key(
            "your-api-key-here",
            max_retries=2,
            retry_delay=0.5
        )

        # This would fail after exhausting retries (if server errors occur)
        response = client.request.GetSalesTaxByAddress("123 Main St")

    except ZipTaxRetryError as e:
        print(f"Retry Error: {e.message}")
        print(f"Attempts: {e.attempts}")
        if e.last_exception:
            print(f"Last Exception: {type(e.last_exception).__name__}")
        print("Fix: Check server status or increase max_retries")
    except Exception as e:
        print(f"Note: This example requires server errors: {type(e).__name__}")


def example_comprehensive_error_handling():
    """Example of comprehensive error handling."""
    print("\n" + "=" * 60)
    print("Example 5: Comprehensive Error Handling")
    print("=" * 60)

    client = ZipTaxClient.api_key("your-api-key-here")

    try:
        response = client.request.GetSalesTaxByAddress(
            "200 Spectrum Center Drive, Irvine, CA 92618"
        )
        print(f"Success! Address: {response.addressDetail.normalizedAddress}")
        if response.tax_summaries:
            rate = response.tax_summaries[0].rate
            print(f"Tax rate: {rate * 100:.2f}%")

    except ZipTaxValidationError as e:
        print(f"Validation Error: {e.message}")
        print("Action: Fix input parameters")

    except ZipTaxAuthenticationError as e:
        print(f"Authentication Error: {e.message}")
        print("Action: Verify API key")

    except ZipTaxRateLimitError as e:
        print(f"Rate Limit Error: {e.message}")
        if e.retry_after:
            print(f"Action: Wait {e.retry_after} seconds before retrying")
        else:
            print("Action: Implement exponential backoff")

    except ZipTaxServerError as e:
        print(f"Server Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        print("Action: Retry later or contact support")

    except ZipTaxConnectionError as e:
        print(f"Connection Error: {e.message}")
        print("Action: Check network connection")

    except ZipTaxTimeoutError as e:
        print(f"Timeout Error: {e.message}")
        print("Action: Increase timeout or check network")

    except ZipTaxAPIError as e:
        print(f"API Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        print("Action: Review API documentation")

    except ZipTaxError as e:
        print(f"General ZipTax Error: {e.message}")
        print("Action: Review error details")

    except Exception as e:
        print(f"Unexpected Error: {e}")
        print("Action: Report to support")

    finally:
        client.close()
        print("\nClient closed successfully")


if __name__ == "__main__":
    # Run all examples
    example_validation_errors()
    example_api_errors()
    example_connection_errors()
    example_retry_errors()
    example_comprehensive_error_handling()

    print("\n" + "=" * 60)
    print("Error Handling Examples Complete")
    print("=" * 60)
