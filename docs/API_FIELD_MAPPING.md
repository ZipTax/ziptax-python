# ZipTax API Field Mapping

This document shows how the ZipTax API's JSON fields map to Python SDK properties.

## Overview

The ZipTax API returns fields in different naming conventions:
- Some use **camelCase** (e.g., `baseRates`, `taxSummaries`)
- Some use **PascalCase** (e.g., `adjustmentType`)
- Some use mixed case (e.g., `rCode`)

The Python SDK normalizes these to **snake_case** for Pythonic code while maintaining compatibility with the API's actual format.

## V60Response

| API Field           | Python Property       | Type                    | Required |
|---------------------|-----------------------|-------------------------|----------|
| `metadata`          | `metadata`            | V60Metadata             | Yes      |
| `baseRates`         | `base_rates`          | List[V60BaseRate]       | No       |
| `service`           | `service`             | V60Service              | Yes      |
| `shipping`          | `shipping`            | V60Shipping             | Yes      |
| `originDestination` | `origin_destination`  | V60OriginDestination    | No       |
| `taxSummaries`      | `tax_summaries`       | List[V60TaxSummary]     | No       |
| `addressDetail`     | `addressDetail`       | V60AddressDetail        | Yes      |

## V60Metadata

| API Field      | Python Property   | Type | Required |
|----------------|-------------------|------|----------|
| `version`      | `version`         | str  | Yes      |
| `rCode`        | `response_code`   | int  | Yes      |

**Note:** The API returns `rCode` (not `responseCode`).

## V60BaseRate

| API Field         | Python Property     | Type   | Required | Notes                                    |
|-------------------|---------------------|--------|----------|------------------------------------------|
| `rate`            | `rate`              | float  | Yes      | Tax rate (e.g., 0.0725 = 7.25%)         |
| `rateId`          | `rate_id`           | str    | No       | May not be present in all responses      |
| `jurType`         | `jur_type`          | str    | Yes      | e.g., "US_STATE_SALES_TAX"              |
| `jurName`         | `jur_name`          | str    | Yes      | Actual name: "CA", "ORANGE", "IRVINE"   |
| `jurDescription`  | `jur_description`   | str    | No       | Human-readable description               |
| `jurTaxCode`      | `jur_tax_code`      | str    | No       | Tax code, can be null                    |

**Important:** `jurName` contains the actual jurisdiction name (e.g., "CA", "ORANGE"), not an enum value.

## V60Service

| API Field        | Python Property    | Type              | Required |
|------------------|--------------------|-------------------|----------|
| `adjustmentType` | `adjustment_type`  | str               | Yes      |
| `taxable`        | `taxable`          | "Y" or "N"        | Yes      |
| `description`    | `description`      | str               | Yes      |

## V60Shipping

| API Field        | Python Property    | Type              | Required |
|------------------|--------------------|-------------------|----------|
| `adjustmentType` | `adjustment_type`  | str               | Yes      |
| `taxable`        | `taxable`          | "Y" or "N"        | Yes      |
| `description`    | `description`      | str               | Yes      |

## V60OriginDestination

| API Field        | Python Property    | Type              | Required |
|------------------|--------------------|-------------------|----------|
| `adjustmentType` | `adjustment_type`  | str               | Yes      |
| `description`    | `description`      | str               | Yes      |
| `value`          | `value`            | "O" or "D"        | Yes      |

**Note:** This entire object may not be present in all responses.

## V60TaxSummary

| API Field     | Python Property  | Type   | Required | Notes                              |
|---------------|------------------|--------|----------|------------------------------------|
| `rate`        | `rate`           | float  | Yes      | Summary tax rate                   |
| `taxType`     | `tax_type`       | str    | Yes      | e.g., "SALES_TAX", "USE_TAX"      |
| `summaryName` | `summary_name`   | str    | Yes      | Description of the summary         |

## V60AddressDetail

| API Field           | Python Property       | Type              | Required |
|---------------------|-----------------------|-------------------|----------|
| `normalizedAddress` | `normalizedAddress`   | str               | Yes      |
| `incorporated`      | `incorporated`        | "true" or "false" | Yes      |
| `geoLat`            | `geoLat`              | float             | Yes      |
| `geoLng`            | `geoLng`              | float             | Yes      |

**Note:** These fields keep their camelCase names in Python for consistency with the API.

## V60AccountMetrics

| API Field             | Python Property         | Type  | Required |
|-----------------------|-------------------------|-------|----------|
| `core_request_count`  | `core_request_count`    | int   | Yes      |
| `core_request_limit`  | `core_request_limit`    | int   | Yes      |
| `core_usage_percent`  | `core_usage_percent`    | float | Yes      |
| `geo_enabled`         | `geo_enabled`           | bool  | Yes      |
| `geo_request_count`   | `geo_request_count`     | int   | Yes      |
| `geo_request_limit`   | `geo_request_limit`     | int   | Yes      |
| `geo_usage_percent`   | `geo_usage_percent`     | float | Yes      |
| `is_active`           | `is_active`             | bool  | Yes      |
| `message`             | `message`               | str   | Yes      |

**Note:** Account metrics API uses snake_case directly.

## Example Usage

```python
from ziptax import ZipTaxClient

client = ZipTaxClient.api_key('your-api-key')
response = client.request.GetSalesTaxByAddress("200 Spectrum Center Drive, Irvine, CA 92618")

# Python uses snake_case properties
print(response.metadata.response_code)  # Accessing rCode from API

# Some fields keep their original names
print(response.addressDetail.normalizedAddress)

# Iterate through base rates
if response.base_rates:
    for rate in response.base_rates:
        print(f"{rate.jur_name}: {rate.rate * 100:.3f}%")
```

## Backward Compatibility

The SDK accepts both naming conventions thanks to `populate_by_name=True`:

```python
# Both work:
response.metadata.response_code  # Pythonic (recommended)
response.metadata.rCode          # API format (also works)

# Both work:
response.base_rates              # Pythonic (recommended)
response.baseRates               # API format (also works)
```

This flexibility ensures compatibility while encouraging Pythonic naming.
