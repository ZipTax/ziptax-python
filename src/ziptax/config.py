"""Configuration module for the ZipTax SDK."""

from typing import Any, Dict, Optional


class Config:
    """Configuration class for ZipTax client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.zip-tax.com",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        taxcloud_connection_id: Optional[str] = None,
        taxcloud_api_key: Optional[str] = None,
        taxcloud_base_url: str = "https://api.v3.taxcloud.com",
        **kwargs: Any,
    ):
        """Initialize Config.

        Args:
            api_key: ZipTax API key
            base_url: Base URL for the ZipTax API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            taxcloud_connection_id: Optional TaxCloud Connection ID (UUID format)
            taxcloud_api_key: Optional TaxCloud API key for order management
            taxcloud_base_url: Base URL for the TaxCloud API
            **kwargs: Additional configuration options
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._taxcloud_connection_id = taxcloud_connection_id
        self._taxcloud_api_key = taxcloud_api_key
        self._taxcloud_base_url = taxcloud_base_url.rstrip("/")
        self._extra: Dict[str, Any] = kwargs

    @property
    def api_key(self) -> str:
        """Get API key."""
        return self._api_key

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    @property
    def timeout(self) -> int:
        """Get timeout."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: int) -> None:
        """Set timeout."""
        self._timeout = value

    @property
    def max_retries(self) -> int:
        """Get max retries."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        """Set max retries."""
        self._max_retries = value

    @property
    def retry_delay(self) -> float:
        """Get retry delay."""
        return self._retry_delay

    @retry_delay.setter
    def retry_delay(self, value: float) -> None:
        """Set retry delay."""
        self._retry_delay = value

    @property
    def taxcloud_connection_id(self) -> Optional[str]:
        """Get TaxCloud connection ID."""
        return self._taxcloud_connection_id

    @property
    def taxcloud_api_key(self) -> Optional[str]:
        """Get TaxCloud API key."""
        return self._taxcloud_api_key

    @property
    def taxcloud_base_url(self) -> str:
        """Get TaxCloud base URL."""
        return self._taxcloud_base_url

    @property
    def has_taxcloud_config(self) -> bool:
        """Check if TaxCloud credentials are configured."""
        return bool(self._taxcloud_connection_id and self._taxcloud_api_key)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key

        Returns:
            Configuration value
        """
        if hasattr(self, f"_{key}"):
            return getattr(self, f"_{key}")
        return self._extra.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value by key.

        Args:
            key: Configuration key
            value: Configuration value
        """
        if hasattr(self, f"_{key}"):
            setattr(self, f"_{key}", value)
        else:
            self._extra[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value with default.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config
        """
        result: Dict[str, Any] = {
            "api_key": "***",  # Mask API key
            "base_url": self._base_url,
            "timeout": self._timeout,
            "max_retries": self._max_retries,
            "retry_delay": self._retry_delay,
        }

        if self._taxcloud_connection_id:
            result["taxcloud_connection_id"] = self._taxcloud_connection_id
        if self._taxcloud_api_key:
            result["taxcloud_api_key"] = "***"  # Mask TaxCloud API key
        if self._taxcloud_base_url != "https://api.v3.taxcloud.com":
            result["taxcloud_base_url"] = self._taxcloud_base_url

        result.update(self._extra)
        return result
