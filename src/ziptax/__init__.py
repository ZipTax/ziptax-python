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
    ZipTaxCloudConfigError,
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
    CalculateCartRequest,
    CalculateCartResponse,
    CartAddress,
    CartCurrency,
    CartItem,
    CartItemRefundWithTaxRequest,
    CartItemRefundWithTaxResponse,
    CartItemResponse,
    CartItemWithTax,
    CartItemWithTaxResponse,
    CartLineItem,
    CartLineItemResponse,
    CartTax,
    CreateOrderRequest,
    Currency,
    CurrencyResponse,
    Exemption,
    JurisdictionName,
    JurisdictionType,
    OrderResponse,
    RefundTax,
    RefundTransactionRequest,
    RefundTransactionResponse,
    Tax,
    TaxCloudAddress,
    TaxCloudAddressResponse,
    TaxCloudCalculateCartResponse,
    TaxCloudCartItemResponse,
    TaxCloudCartLineItemResponse,
    TaxType,
    UpdateOrderRequest,
    V60AccountMetrics,
    V60AddressDetail,
    V60BaseRate,
    V60DisplayRate,
    V60Metadata,
    V60PostalCodeAddressDetail,
    V60PostalCodeResponse,
    V60PostalCodeResult,
    V60Response,
    V60ResponseInfo,
    V60Service,
    V60Shipping,
    V60SourcingRules,
    V60TaxSummary,
)

__version__ = "0.2.3-beta"

__all__ = [
    "ZipTaxClient",
    "Config",
    # Exceptions
    "ZipTaxError",
    "ZipTaxAPIError",
    "ZipTaxAuthenticationError",
    "ZipTaxAuthorizationError",
    "ZipTaxCloudConfigError",
    "ZipTaxNotFoundError",
    "ZipTaxRateLimitError",
    "ZipTaxServerError",
    "ZipTaxValidationError",
    "ZipTaxConnectionError",
    "ZipTaxTimeoutError",
    "ZipTaxRetryError",
    # V60 Models
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
    "V60PostalCodeResponse",
    "V60PostalCodeResult",
    "V60PostalCodeAddressDetail",
    "JurisdictionType",
    "JurisdictionName",
    "TaxType",
    # Cart Tax Calculation Models
    "CalculateCartRequest",
    "CalculateCartResponse",
    "CartAddress",
    "CartCurrency",
    "CartItem",
    "CartItemResponse",
    "CartLineItem",
    "CartLineItemResponse",
    "CartTax",
    # TaxCloud Cart Models
    "TaxCloudCalculateCartResponse",
    "TaxCloudCartItemResponse",
    "TaxCloudCartLineItemResponse",
    # TaxCloud Models
    "TaxCloudAddress",
    "TaxCloudAddressResponse",
    "Tax",
    "RefundTax",
    "Currency",
    "CurrencyResponse",
    "Exemption",
    "CartItemWithTax",
    "CartItemWithTaxResponse",
    "CreateOrderRequest",
    "OrderResponse",
    "UpdateOrderRequest",
    "CartItemRefundWithTaxRequest",
    "CartItemRefundWithTaxResponse",
    "RefundTransactionRequest",
    "RefundTransactionResponse",
]
