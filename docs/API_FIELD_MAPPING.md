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
| `service`           | `service`             | V60Service              | No       |
| `shipping`          | `shipping`            | V60Shipping             | No       |
| `sourcingRules`     | `sourcing_rules`      | V60SourcingRules        | No       |
| `taxSummaries`      | `tax_summaries`       | List[V60TaxSummary]     | No       |
| `addressDetail`     | `address_detail`      | V60AddressDetail        | Yes      |

**Note:** `service` and `shipping` are Optional because some jurisdictions (e.g., Canada) may not include them.

## V60Metadata

| API Field      | Python Property   | Type            | Required |
|----------------|-------------------|-----------------|----------|
| `version`      | `version`         | str             | Yes      |
| `response`     | `response`        | V60ResponseInfo | Yes      |

## V60ResponseInfo

| API Field      | Python Property   | Type | Required |
|----------------|-------------------|------|----------|
| `code`         | `code`            | int  | Yes      |
| `name`         | `name`            | str  | Yes      |
| `message`      | `message`         | str  | Yes      |
| `definition`   | `definition`      | str  | Yes      |

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

## V60SourcingRules

| API Field        | Python Property    | Type              | Required |
|------------------|--------------------|-------------------|----------|
| `adjustmentType` | `adjustment_type`  | str               | Yes      |
| `description`    | `description`      | str               | Yes      |
| `value`          | `value`            | str               | Yes      |

**Note:** This entire object may not be present in all responses. `value` is typically "O" (origin) or "D" (destination).

## V60TaxSummary

| API Field     | Python Property  | Type   | Required | Notes                              |
|---------------|------------------|--------|----------|------------------------------------|
| `rate`        | `rate`           | float  | Yes      | Summary tax rate                   |
| `taxType`     | `tax_type`       | str    | Yes      | e.g., "SALES_TAX", "USE_TAX"      |
| `summaryName` | `summary_name`   | str    | Yes      | Description of the summary         |

## V60AddressDetail

| API Field           | Python Property       | Type              | Required |
|---------------------|-----------------------|-------------------|----------|
| `normalizedAddress` | `normalized_address`  | str               | Yes      |
| `incorporated`      | `incorporated`        | str               | Yes      |
| `geoLat`            | `geo_lat`             | float             | Yes      |
| `geoLng`            | `geo_lng`             | float             | Yes      |

**Note:** `incorporated` is typically "true" or "false" but typed as `str` for flexibility.

## V60AccountMetrics

| API Field             | Python Property         | Type  | Required |
|-----------------------|-------------------------|-------|----------|
| `request_count`       | `request_count`         | int   | Yes      |
| `request_limit`       | `request_limit`         | int   | Yes      |
| `usage_percent`       | `usage_percent`         | float | Yes      |
| `is_active`           | `is_active`             | bool  | Yes      |
| `message`             | `message`               | str   | Yes      |

**Note:** Account metrics API uses snake_case directly. The model uses `extra="allow"` to accept any additional fields the API may return.

## Example Usage

```python
from ziptax import ZipTaxClient

client = ZipTaxClient.api_key('your-api-key')
response = client.request.GetSalesTaxByAddress("200 Spectrum Center Drive, Irvine, CA 92618")

# Response metadata
print(response.metadata.response.code)     # 100
print(response.metadata.response.message)  # "Successful API Request."

# Address details use snake_case
print(response.address_detail.normalized_address)
print(response.address_detail.geo_lat)
print(response.address_detail.geo_lng)

# Iterate through base rates
if response.base_rates:
    for rate in response.base_rates:
        print(f"{rate.jur_name}: {rate.rate * 100:.3f}%")
```

## Backward Compatibility

The SDK accepts both naming conventions thanks to `populate_by_name=True`:

```python
# Both work:
response.base_rates              # Pythonic (recommended)
response.baseRates               # API format (also works)

# Both work:
response.address_detail          # Pythonic (recommended)
response.addressDetail           # API format (also works)
```

This flexibility ensures compatibility while encouraging Pythonic naming.
