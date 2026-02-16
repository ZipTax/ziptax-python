"""Main client for the ZipTax SDK."""

import logging
from typing import Optional

from .config import Config
from .resources.functions import Functions
from .utils.http import HTTPClient
from .utils.validation import validate_api_key

logger = logging.getLogger(__name__)


class ZipTaxClient:
    """Main client for interacting with the ZipTax API.

    Example:
        Basic usage:
        >>> client = ZipTaxClient.api_key('your-api-key')
        >>> client.config['format'] = 'json'
        >>> response = client.request.GetSalesTaxByAddress(
        ...     "200 Spectrum Center Drive, Irvine, CA 92618"
        ... )

        With custom configuration:
        >>> client = ZipTaxClient.api_key(
        ...     'your-api-key', timeout=60, max_retries=5
        ... )
        >>> response = client.request.GetSalesTaxByGeoLocation(
        ...     "33.6489", "-117.8386"
        ... )
    """

    def __init__(self, config: Config):
        """Initialize ZipTaxClient.

        Args:
            config: Configuration object

        Note:
            It's recommended to use ZipTaxClient.api_key() class method instead
            of instantiating directly.
        """
        self.config = config
        self._http_client = HTTPClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
        )

        # Create TaxCloud HTTP client if configured
        self._taxcloud_http_client = None
        if config.has_taxcloud_config:
            assert config.taxcloud_api_key is not None
            self._taxcloud_http_client = HTTPClient(
                api_key=config.taxcloud_api_key,
                base_url=config.taxcloud_base_url,
                timeout=config.timeout,
            )

        self.request = Functions(
            http_client=self._http_client,
            taxcloud_http_client=self._taxcloud_http_client,
            config=config,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay,
        )

    @classmethod
    def api_key(
        cls,
        api_key: str,
        base_url: str = "https://api.zip-tax.com",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        taxcloud_connection_id: Optional[str] = None,
        taxcloud_api_key: Optional[str] = None,
        taxcloud_base_url: str = "https://api.v3.taxcloud.com",
        **kwargs,
    ) -> "ZipTaxClient":
        """Create a ZipTaxClient instance with an API key.

        Args:
            api_key: ZipTax API key
            base_url: Base URL for the ZipTax API (default: https://api.zip-tax.com)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
            taxcloud_connection_id: Optional TaxCloud Connection ID for order management
            taxcloud_api_key: Optional TaxCloud API key for order management
            taxcloud_base_url: Base URL for the TaxCloud API (default: https://api.v3.taxcloud.com)
            **kwargs: Additional configuration options

        Returns:
            ZipTaxClient instance

        Raises:
            ZipTaxValidationError: If API key is invalid

        Example:
            Basic usage:
            >>> client = ZipTaxClient.api_key('your-api-key')

            With TaxCloud support:
            >>> client = ZipTaxClient.api_key(
            ...     'your-api-key',
            ...     taxcloud_connection_id='25eb9b97-5acb-492d-b720-c03e79cf715a',
            ...     taxcloud_api_key='your-taxcloud-key'
            ... )
        """
        validate_api_key(api_key)

        config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            taxcloud_connection_id=taxcloud_connection_id,
            taxcloud_api_key=taxcloud_api_key,
            taxcloud_base_url=taxcloud_base_url,
            **kwargs,
        )

        return cls(config)

    def close(self) -> None:
        """Close the HTTP client session.

        It's recommended to use the client as a context manager instead of
        calling this method directly.
        """
        self._http_client.close()
        if self._taxcloud_http_client:
            self._taxcloud_http_client.close()

    def __enter__(self) -> "ZipTaxClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ZipTaxClient(base_url={self.config.base_url})"
