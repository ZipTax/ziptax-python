"""Tests for retry utilities."""

from unittest.mock import Mock, patch

import pytest

from ziptax.exceptions import (
    ZipTaxConnectionError,
    ZipTaxRateLimitError,
    ZipTaxRetryError,
    ZipTaxServerError,
    ZipTaxTimeoutError,
    ZipTaxValidationError,
)
from ziptax.utils.retry import (
    async_retry_with_backoff,
    retry_with_backoff,
    should_retry,
)


def test_should_retry_server_error():
    """Test should_retry returns True for server errors."""
    assert should_retry(ZipTaxServerError("Server error", 500, None))


def test_should_retry_rate_limit_error():
    """Test should_retry returns True for rate limit errors."""
    assert should_retry(ZipTaxRateLimitError("Rate limit", None, 429, None))


def test_should_retry_connection_error():
    """Test should_retry returns True for connection errors."""
    assert should_retry(ZipTaxConnectionError("Connection error"))


def test_should_retry_timeout_error():
    """Test should_retry returns True for timeout errors."""
    assert should_retry(ZipTaxTimeoutError("Timeout"))


def test_should_retry_validation_error():
    """Test should_retry returns False for validation errors."""
    assert not should_retry(ZipTaxValidationError("Validation error"))


def test_should_retry_generic_exception():
    """Test should_retry returns False for generic exceptions."""
    assert not should_retry(ValueError("Generic error"))


def test_retry_with_backoff_success():
    """Test retry_with_backoff decorator with successful call."""
    mock_func = Mock(return_value="success")
    decorated = retry_with_backoff()(mock_func)

    result = decorated()

    assert result == "success"
    mock_func.assert_called_once()


def test_retry_with_backoff_success_after_retry():
    """Test retry_with_backoff succeeds after one retry."""
    mock_func = Mock(
        side_effect=[
            ZipTaxServerError("Server error", 500, None),
            "success",
        ]
    )
    decorated = retry_with_backoff(max_retries=2, base_delay=0.01)(mock_func)

    with patch("time.sleep"):
        result = decorated()

    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_with_backoff_max_retries_exceeded():
    """Test retry_with_backoff raises ZipTaxRetryError when max retries exceeded."""
    mock_func = Mock(side_effect=ZipTaxServerError("Server error", 500, None))
    decorated = retry_with_backoff(max_retries=2, base_delay=0.01)(mock_func)

    with patch("time.sleep"):
        with pytest.raises(ZipTaxRetryError) as exc_info:
            decorated()

    assert exc_info.value.attempts == 3
    assert "Max retries (2) exceeded" in str(exc_info.value)
    assert mock_func.call_count == 3


def test_retry_with_backoff_non_retryable_error():
    """Test retry_with_backoff doesn't retry non-retryable errors."""
    mock_func = Mock(side_effect=ZipTaxValidationError("Validation error"))
    decorated = retry_with_backoff(max_retries=3)(mock_func)

    with pytest.raises(ZipTaxValidationError):
        decorated()

    mock_func.assert_called_once()


def test_retry_with_backoff_exponential_delay():
    """Test retry_with_backoff uses exponential backoff delays."""
    mock_func = Mock(side_effect=ZipTaxServerError("Server error", 500, None))
    decorated = retry_with_backoff(
        max_retries=3, base_delay=1.0, exponential_base=2.0, max_delay=60.0
    )(mock_func)

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(ZipTaxRetryError):
            decorated()

    # Check that sleep was called with exponential delays: 1, 2, 4
    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
    assert sleep_calls == [1.0, 2.0, 4.0]


def test_retry_with_backoff_max_delay():
    """Test retry_with_backoff respects max_delay."""
    mock_func = Mock(side_effect=ZipTaxServerError("Server error", 500, None))
    decorated = retry_with_backoff(
        max_retries=5, base_delay=10.0, exponential_base=2.0, max_delay=30.0
    )(mock_func)

    with patch("time.sleep") as mock_sleep:
        with pytest.raises(ZipTaxRetryError):
            decorated()

    # Check that delays are capped at max_delay (30.0)
    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
    # 10, 20, 30 (capped), 30 (capped), 30 (capped)
    assert sleep_calls == [10.0, 20.0, 30.0, 30.0, 30.0]


def test_retry_with_backoff_rate_limit_retry_after():
    """Test retry_with_backoff uses retry-after header for rate limit errors."""
    mock_func = Mock(
        side_effect=[
            ZipTaxRateLimitError(
                "Rate limit", retry_after=5, status_code=429, response=None
            ),
            "success",
        ]
    )
    decorated = retry_with_backoff(max_retries=2, base_delay=1.0)(mock_func)

    with patch("time.sleep") as mock_sleep:
        result = decorated()

    assert result == "success"
    # Should use retry_after value (5) instead of exponential delay (1)
    mock_sleep.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_async_retry_with_backoff_success():
    """Test async_retry_with_backoff decorator with successful call."""
    mock_func = Mock(return_value="success")

    async def async_mock():
        return mock_func()

    decorator = await async_retry_with_backoff()
    decorated = decorator(async_mock)

    result = await decorated()

    assert result == "success"
    mock_func.assert_called_once()


@pytest.mark.asyncio
async def test_async_retry_with_backoff_success_after_retry():
    """Test async_retry_with_backoff succeeds after one retry."""
    call_count = 0

    async def async_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ZipTaxServerError("Server error", 500, None)
        return "success"

    decorator = await async_retry_with_backoff(max_retries=2, base_delay=0.01)
    decorated = decorator(async_func)

    with patch("asyncio.sleep"):
        result = await decorated()

    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_async_retry_with_backoff_max_retries_exceeded():
    """Test async_retry_with_backoff raises error when max retries exceeded."""

    async def async_func():
        raise ZipTaxServerError("Server error", 500, None)

    decorator = await async_retry_with_backoff(max_retries=2, base_delay=0.01)
    decorated = decorator(async_func)

    with patch("asyncio.sleep"):
        with pytest.raises(ZipTaxRetryError) as exc_info:
            await decorated()

    assert exc_info.value.attempts == 3
    assert "Max retries (2) exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_retry_with_backoff_non_retryable_error():
    """Test async_retry_with_backoff doesn't retry non-retryable errors."""

    async def async_func():
        raise ZipTaxValidationError("Validation error")

    decorator = await async_retry_with_backoff(max_retries=3)
    decorated = decorator(async_func)

    with pytest.raises(ZipTaxValidationError):
        await decorated()


@pytest.mark.asyncio
async def test_async_retry_with_backoff_exponential_delay():
    """Test async_retry_with_backoff uses exponential backoff delays."""

    async def async_func():
        raise ZipTaxServerError("Server error", 500, None)

    decorator = await async_retry_with_backoff(
        max_retries=3, base_delay=1.0, exponential_base=2.0, max_delay=60.0
    )
    decorated = decorator(async_func)

    with patch("asyncio.sleep") as mock_sleep:
        with pytest.raises(ZipTaxRetryError):
            await decorated()

    # Check that sleep was called with exponential delays: 1, 2, 4
    sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
    assert sleep_calls == [1.0, 2.0, 4.0]


@pytest.mark.asyncio
async def test_async_retry_with_backoff_rate_limit_retry_after():
    """Test async_retry_with_backoff uses retry-after header for rate limit errors."""
    call_count = 0

    async def async_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ZipTaxRateLimitError(
                "Rate limit", retry_after=5, status_code=429, response=None
            )
        return "success"

    decorator = await async_retry_with_backoff(max_retries=2, base_delay=1.0)
    decorated = decorator(async_func)

    with patch("asyncio.sleep") as mock_sleep:
        result = await decorated()

    assert result == "success"
    # Should use retry_after value (5) instead of exponential delay (1)
    mock_sleep.assert_called_once_with(5)
