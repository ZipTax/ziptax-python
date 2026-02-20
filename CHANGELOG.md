# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3-beta] - 2025-02-20

### Added
- **TaxCloud Cart Routing**: `CalculateCart()` now automatically routes to TaxCloud's `POST /tax/connections/{connectionId}/carts` when TaxCloud credentials are configured
  - Same input contract (`CalculateCartRequest`) regardless of backend
  - SDK transforms request internally: parses single-string addresses into structured components, maps `taxabilityCode` to `tic`, adds 0-based `index` to line items
  - Returns `TaxCloudCalculateCartResponse` (with `connectionId`, `transactionDate`, structured addresses, `deliveredBySeller`, `exemption`) when routed to TaxCloud
  - Returns `CalculateCartResponse` (existing behavior) when TaxCloud is not configured
  - Return type: `Union[CalculateCartResponse, TaxCloudCalculateCartResponse]`
- **Address Parsing Utility**: `parse_address_string()` in `utils/validation.py`
  - Parses `"street, city, ST zip"` format into structured `{line1, city, state, zip}` dict
  - Supports 5-digit and 9-digit ZIP codes (e.g., `92618` or `92618-1905`)
  - Raises `ZipTaxValidationError` with descriptive messages on parse failure
- **3 New Pydantic Models** for TaxCloud cart responses:
  - `TaxCloudCalculateCartResponse`: top-level response with `connection_id`, `items`, `transaction_date`
  - `TaxCloudCartItemResponse`: per-cart result with structured addresses, `currency`, `delivered_by_seller`, `exemption`
  - `TaxCloudCartLineItemResponse`: per-item result with `index`, `item_id`, `price`, `quantity`, `tax`, `tic`
- **17 New Tests** in `TestCalculateCartTaxCloudRouting`:
  - Routing logic (ZipTax vs TaxCloud based on config)
  - Request transformation (address parsing, index, tic mapping, field passthrough)
  - Response parsing (top-level, cart fields, addresses, line items)
  - Error handling (unparseable addresses, invalid state/zip)

### Changed
- Version bumped from `0.2.1-beta` to `0.2.3-beta`
- `CalculateCart()` return type changed from `CalculateCartResponse` to `Union[CalculateCartResponse, TaxCloudCalculateCartResponse]`
- `CalculateCart()` implementation refactored into routing method with two private helpers: `_calculate_cart_ziptax()` and `_calculate_cart_taxcloud()`

### Technical Details
- Request transformation handled by static method `_transform_cart_for_taxcloud()` in `Functions`
- TaxCloud cart uses `taxcloud_http_client` (separate auth) with path `/tax/connections/{connectionId}/carts`
- Retry logic with exponential backoff applies to both ZipTax and TaxCloud routes
- All quality checks pass: black, ruff, mypy, pytest (125 tests, 96% coverage)

## [0.2.1-beta] - 2025-02-19

### Added
- **Cart Tax Calculation**: `CalculateCart()` function for calculating sales tax on shopping carts
  - Accepts a `CalculateCartRequest` with customer info, addresses, currency, and line items
  - Sends cart to `POST /calculate/cart` on the ZipTax API
  - Returns per-item tax rate and amount via `CalculateCartResponse`
  - Origin/destination sourcing is handled by the API internally
- **9 New Pydantic Models** for cart tax calculation:
  - Request models: `CalculateCartRequest`, `CartItem`, `CartAddress`, `CartCurrency`, `CartLineItem`
  - Response models: `CalculateCartResponse`, `CartItemResponse`, `CartLineItemResponse`, `CartTax`
- **Pydantic Validation** on cart models:
  - `CartLineItem.price` and `quantity`: must be greater than 0 (`gt=0`)
  - `CalculateCartRequest.items`: exactly 1 element (`min_length=1, max_length=1`)
  - `CartItem.line_items`: 1-250 elements (`min_length=1, max_length=250`)
  - `CartCurrency.currency_code`: must be `"USD"` (`Literal["USD"]`)
- **Documentation**:
  - CalculateCart usage guide with code examples in README.md
  - Cart endpoint specification in `docs/spec.yaml`
  - Actual API request/response examples in spec

### Changed
- Version bumped from `0.2.0-beta` to `0.2.1-beta`

### Technical Details
- Cart calculation uses the ZipTax HTTP client (not TaxCloud) with `X-API-Key` authentication
- Request bodies serialized with `model_dump(by_alias=True, exclude_none=True)` for camelCase API fields
- `taxabilityCode` is optional and excluded from the payload when not set
- All quality checks pass: black, ruff, mypy, pytest

## [0.2.0-beta] - 2025-02-16

### Added
- **TaxCloud Integration**: Optional support for TaxCloud order management API
  - `CreateOrder()` - Create orders in TaxCloud with line items and tax calculations
  - `GetOrder()` - Retrieve existing orders by ID
  - `UpdateOrder()` - Update order completed dates
  - `RefundOrder()` - Create full or partial refunds against orders
- **Postal Code Lookup**: `GetRatesByPostalCode()` function for US postal code tax rate lookups
- **18 New Pydantic Models** for TaxCloud data structures:
  - Address models: `TaxCloudAddress`, `TaxCloudAddressResponse`
  - Order models: `CreateOrderRequest`, `OrderResponse`, `UpdateOrderRequest`
  - Line item models: `CartItemWithTax`, `CartItemWithTaxResponse`
  - Refund models: `RefundTransactionRequest`, `RefundTransactionResponse`, `CartItemRefundWithTaxRequest`, `CartItemRefundWithTaxResponse`
  - Supporting models: `Tax`, `RefundTax`, `Currency`, `CurrencyResponse`, `Exemption`
  - Postal code models: `V60PostalCodeResponse`, `V60PostalCodeResult`
- **HTTP Client Enhancements**:
  - Added `post()` method for POST requests
  - Added `patch()` method for PATCH requests
  - Both methods support JSON payloads, query parameters, and headers
- **Dual API Architecture**:
  - Seamlessly manage two separate HTTP clients (ZipTax + TaxCloud)
  - TaxCloud features are completely optional - enabled only when credentials provided
  - Automatic credential validation with helpful error messages
- **New Exception**: `ZipTaxCloudConfigError` for TaxCloud configuration issues
- **Configuration Enhancements**:
  - Added `taxcloud_connection_id` parameter for TaxCloud Connection ID
  - Added `taxcloud_api_key` parameter for TaxCloud API authentication
  - Added `taxcloud_base_url` parameter (default: `https://api.v3.taxcloud.com`)
  - Added `has_taxcloud_config` property to check TaxCloud configuration
  - TaxCloud fields now included in `Config.to_dict()` (API keys masked)
- **Canada Support**: Country code validation now accepts "CAN" in addition to "USA"
- **Documentation**:
  - Comprehensive TaxCloud usage examples in README.md
  - New example file: `examples/taxcloud_orders.py`
  - Created `CLAUDE.md` - AI development guide for the project
  - Created `docs/VERSIONING.md` - Versioning strategy and processes
  - Created `docs/API_FIELD_MAPPING.md` - API field to Python property mapping
  - Created `docs/ACTUAL_API_STRUCTURE.md` - Live API response structure reference
  - Updated API reference with all endpoints
  - Updated exception hierarchy documentation
- **Version Management**:
  - `scripts/bump_version.py` for consistent version bumping across all files
  - GitHub Actions `version-check.yml` workflow for PR version validation
- **Test Coverage**: 85 tests with 95% code coverage
  - Full test suite for TaxCloud CRUD operations
  - POST and PATCH HTTP method tests
  - Postal code function tests

### Changed
- **V60AccountMetrics**: Redesigned to match live API response format
  - Fields changed from `core_request_count`/`geo_request_count`/etc. to `request_count`/`request_limit`/`usage_percent`
  - Added `extra="allow"` to accept any additional fields the API may return
- **V60Response**: Made `service` and `shipping` fields Optional to support Canada responses
- **V60AddressDetail**: Renamed fields to snake_case with camelCase aliases
  - `normalizedAddress` -> `normalized_address` (alias: `normalizedAddress`)
  - `geoLat` -> `geo_lat` (alias: `geoLat`)
  - `geoLng` -> `geo_lng` (alias: `geoLng`)
  - `incorporated` changed from `Literal["true","false"]` to `str`
- **V60Response.address_detail**: Renamed from `addressDetail` to `address_detail` (alias: `addressDetail`)
- **Historical date format**: Changed from `YYYY-MM` to `YYYYMM` to match live API requirements
- **Format validation**: Removed "xml" from valid formats; only "json" is accepted
- **Literal types replaced with str**: `V60Service.taxable`, `V60Shipping.taxable`, `V60SourcingRules.value`, `V60PostalCodeResult.txb_service`, `txb_freight`, `origin_destination` all changed from `Literal` to `str` for flexibility
- **Validation order**: `validate_address()` now checks `isinstance` before `len()` to handle non-string inputs gracefully
- **async_retry_with_backoff**: Changed from `async def` to `def` (only inner wrapper is async)

### Fixed
- V60AccountMetrics model now matches live API response (was causing ValidationError on real API calls)
- Historical date validation now uses correct `YYYYMM` format accepted by the API
- All `__init__.py` exports updated: added `ZipTaxCloudConfigError` and all TaxCloud/postal code models
- Config `to_dict()` now includes TaxCloud configuration fields (masked)

### Technical Details
- TaxCloud API uses separate authentication with X-API-KEY header
- Connection ID is automatically injected into TaxCloud API paths
- All TaxCloud methods validate credentials before execution via `_check_taxcloud_config()`
- Type-safe implementation with assertions for optional HTTP clients
- Maintains backward compatibility for existing ZipTax functionality
- Passes all linting (ruff), formatting (black), and type checking (mypy) with no errors

## [0.1.2-beta] - 2025-02-15

### Changed
- Version bump for beta release

## [1.0.0] - 2024-01-21

### Added
- Initial release of the ZipTax Python SDK
- Support for all three v6.0 API endpoints:
  - `GetSalesTaxByAddress` - Get tax rates by street address
  - `GetSalesTaxByGeoLocation` - Get tax rates by latitude/longitude
  - `GetAccountMetrics` - Get account usage metrics
- Comprehensive Pydantic models for all API responses
- Automatic retry logic with exponential backoff
- Input validation for all parameters
- Comprehensive error handling with custom exception types
- Type hints throughout the codebase
- Full test suite with 77% code coverage
- Example files for basic usage, async operations, and error handling
- GitHub Actions CI/CD workflows

### Fixed
- Updated Pydantic models to use modern `ConfigDict` instead of deprecated `Config` class
- Added proper field aliases to map API's camelCase fields to Python's snake_case
- Made `origin_destination` field optional in `V60Response` (not always present in API responses)
- Configured models with `populate_by_name=True` to accept both camelCase and snake_case field names
- Made `V60BaseRate` fields more flexible to handle actual API responses:
  - `rate_id`: Changed from required to optional (not always present)
  - `jur_name`: Changed from enum to string (contains actual jurisdiction names like "CA", "ORANGE", "IRVINE")
  - `jur_type`: Changed from enum to string (for flexibility with API variations)
  - `jur_description`: Changed from required to optional
  - `jur_tax_code`: Changed from required to optional (can be null)
- Made `V60TaxSummary.tax_type` a string instead of enum for flexibility
