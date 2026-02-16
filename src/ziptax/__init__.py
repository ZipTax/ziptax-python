"""ZipTax Python SDK.

Official Python SDK for the ZipTax API.

Example:
    Basic usage:
    >>> from ziptax import ZipTaxClient
    >>> client = ZipTaxClient.api_key('your-api-key')
    >>> response = client.request.GetSalesTaxByAddress(
    ...     "200 Spectrum Center Drive, Irvine, CA 92618"
    ... )
    >>> print(response.tax_summaries[0].rate)
"""

from .client import ZipTaxClient
from .config import Config
from .exceptions import (
    ZipTaxAPIError,
    ZipTaxAuthenticationError,
    ZipTaxAuthorizationError,
    ZipTaxConnectionError,
    ZipTaxError,
    ZipTaxNotFoundError,
    ZipTaxRateLimitError,
    ZipTaxRetryError,
    ZipTaxServerError,
    ZipTaxTimeoutError,
    ZipTaxValidationError,
)
from .models import (
    JurisdictionName,
    JurisdictionType,
    TaxType,
    V60AccountMetrics,
    V60AddressDetail,
    V60BaseRate,
    V60DisplayRate,
    V60Metadata,
    V60Response,
    V60ResponseInfo,
    V60Service,
    V60Shipping,
    V60SourcingRules,
    V60TaxSummary,
)

__version__ = "0.2.0-beta"

__all__ = [
    "ZipTaxClient",
    "Config",
    # Exceptions
    "ZipTaxError",
    "ZipTaxAPIError",
    "ZipTaxAuthenticationError",
    "ZipTaxAuthorizationError",
    "ZipTaxNotFoundError",
    "ZipTaxRateLimitError",
    "ZipTaxServerError",
    "ZipTaxValidationError",
    "ZipTaxConnectionError",
    "ZipTaxTimeoutError",
    "ZipTaxRetryError",
    # Models
    "V60Response",
    "V60ResponseInfo",
    "V60Metadata",
    "V60BaseRate",
    "V60Service",
    "V60Shipping",
    "V60SourcingRules",
    "V60TaxSummary",
    "V60DisplayRate",
    "V60AddressDetail",
    "V60AccountMetrics",
    "JurisdictionType",
    "JurisdictionName",
    "TaxType",
]
