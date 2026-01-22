# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Technical Details

The SDK correctly handles the ZipTax API v6.0 response format:
- API returns camelCase field names (e.g., `responseCode`, `adjustmentType`, `baseRates`)
- SDK exposes snake_case Python properties (e.g., `response_code`, `adjustment_type`, `base_rates`)
- Pydantic aliases ensure seamless mapping between formats
- All models support both naming conventions for flexibility

### Response Model Changes

#### V60Metadata
- `rCode` → `response_code` (alias: `rCode`) - API returns `rCode`, exposed as `response_code` in Python

#### V60BaseRate
- `rate` (required) - Tax rate as float
- `rate_id` (optional) → alias: `rateId` - May not be present in all responses
- `jur_type` (required) → alias: `jurType` - String (e.g., "US_STATE_SALES_TAX")
- `jur_name` (required) → alias: `jurName` - String with actual name (e.g., "CA", "ORANGE", "IRVINE")
- `jur_description` (optional) → alias: `jurDescription` - Human-readable description
- `jur_tax_code` (optional) → alias: `jurTaxCode` - Tax code, can be null

#### V60Service & V60Shipping
- `adjustment_type` → alias: `adjustmentType`

#### V60TaxSummary
- `rate` (required) - Summary tax rate as float
- `tax_type` (required) → alias: `taxType` - String (e.g., "SALES_TAX", "USE_TAX")
- `summary_name` (required) → alias: `summaryName` - Description of the summary

#### V60Response
- `base_rates` → alias: `baseRates`
- `tax_summaries` → alias: `taxSummaries`
- `origin_destination` → alias: `originDestination` (now Optional)

## Future Enhancements

Potential improvements for future releases:
- Native async/await support with aiohttp
- Response caching
- Batch operations
- Additional validation options
- Webhook support
- More comprehensive examples
