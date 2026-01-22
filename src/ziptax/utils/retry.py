"""Retry utilities for the ZipTax SDK."""

import time
import logging
from typing import Callable, TypeVar, Any
from functools import wraps

from ..exceptions import (
    ZipTaxRetryError,
    ZipTaxServerError,
    ZipTaxRateLimitError,
    ZipTaxConnectionError,
    ZipTaxTimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def should_retry(exception: Exception) -> bool:
    """Determine if an exception should trigger a retry.

    Args:
        exception: The exception to check

    Returns:
        True if the exception should trigger a retry
    """
    return isinstance(
        exception,
        (
            ZipTaxServerError,
            ZipTaxRateLimitError,
            ZipTaxConnectionError,
            ZipTaxTimeoutError,
        ),
    )


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception = Exception("Unknown error")

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Don't retry if it's not a retryable exception
                    if not should_retry(e):
                        raise

                    # Don't retry if we've exhausted our attempts
                    if attempt >= max_retries:
                        raise ZipTaxRetryError(
                            message=f"Max retries ({max_retries}) exceeded",
                            attempts=attempt + 1,
                            last_exception=last_exception,
                        )

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # For rate limit errors, use the retry-after header if available
                    if isinstance(e, ZipTaxRateLimitError) and e.retry_after:
                        delay = e.retry_after

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)

            # This should never be reached, but just in case
            raise ZipTaxRetryError(
                message=f"Max retries ({max_retries}) exceeded",
                attempts=max_retries + 1,
                last_exception=last_exception,
            )

        return wrapper

    return decorator


async def async_retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry an async function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation

    Returns:
        Decorated async function with retry logic
    """
    import asyncio

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception = Exception("Unknown error")

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Don't retry if it's not a retryable exception
                    if not should_retry(e):
                        raise

                    # Don't retry if we've exhausted our attempts
                    if attempt >= max_retries:
                        raise ZipTaxRetryError(
                            message=f"Max retries ({max_retries}) exceeded",
                            attempts=attempt + 1,
                            last_exception=last_exception,
                        )

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # For rate limit errors, use the retry-after header if available
                    if isinstance(e, ZipTaxRateLimitError) and e.retry_after:
                        delay = e.retry_after

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )

                    await asyncio.sleep(delay)

            # This should never be reached, but just in case
            raise ZipTaxRetryError(
                message=f"Max retries ({max_retries}) exceeded",
                attempts=max_retries + 1,
                last_exception=last_exception,
            )

        return wrapper

    return decorator
