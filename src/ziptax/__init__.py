"""ZipTax Python SDK.

Official Python SDK for the ZipTax API.

Example:
    Basic usage:
    >>> from ziptax import ZipTaxClient
    >>> client = ZipTaxClient.api_key('your-api-key')
    >>> response = client.request.GetSalesTaxByAddress("200 Spectrum Center Drive, Irvine, CA 92618")
    >>> print(response.tax_summaries[0].rate)
"""

from .client import ZipTaxClient
from .config import Config
from .exceptions import (
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
from .models import (
    V60Response,
    V60ResponseInfo,
    V60Metadata,
    V60BaseRate,
    V60Service,
    V60Shipping,
    V60SourcingRules,
    V60TaxSummary,
    V60DisplayRate,
    V60AddressDetail,
    V60AccountMetrics,
    JurisdictionType,
    JurisdictionName,
    TaxType,
)

__version__ = "1.0.0"

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
