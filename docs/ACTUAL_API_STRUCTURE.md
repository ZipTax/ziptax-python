# Actual ZipTax API v6.0 Structure

This document shows the **actual** API response structure based on real API responses.

## Complete Response Example

```json
{
  "metadata": {
    "version": "v60",
    "response": {
      "code": 100,
      "name": "RESPONSE_CODE_SUCCESS",
      "message": "Successful API Request.",
      "definition": "http://api.zip-tax.com/request/v60/schema"
    }
  },
  "baseRates": [
    {
      "rate": 0.06,
      "jurType": "US_STATE_SALES_TAX",
      "jurName": "CA",
      "jurDescription": "US State Sales Tax",
      "jurTaxCode": "06"
    }
  ],
  "service": {
    "adjustmentType": "SERVICE_TAXABLE",
    "taxable": "N",
    "description": "Services non-taxable"
  },
  "shipping": {
    "adjustmentType": "FREIGHT_TAXABLE",
    "taxable": "N",
    "description": "Freight non-taxable"
  },
  "sourcingRules": {
    "adjustmentType": "ORIGIN_DESTINATION",
    "description": "Destination Based Taxation",
    "value": "D"
  },
  "taxSummaries": [
    {
      "rate": 0.0775,
      "taxType": "SALES_TAX",
      "summaryName": "Total Base Sales Tax",
      "displayRates": [
        {
          "name": "Total Rate",
          "rate": 0.0775
        }
      ]
    }
  ],
  "addressDetail": {
    "normalizedAddress": "200 Spectrum Center Dr, Irvine, CA 92618-5003, United States",
    "incorporated": "true",
    "geoLat": 33.65253,
    "geoLng": -117.74794
  }
}
```

## Key Structure Points

### 1. Nested Response Metadata

The API uses a **nested structure** for metadata:
```json
"metadata": {
  "version": "v60",
  "response": {
    "code": 100,
    "name": "RESPONSE_CODE_SUCCESS",
    "message": "Successful API Request.",
    "definition": "http://api.zip-tax.com/request/v60/schema"
  }
}
```

**Not** a flat structure like `"rCode": 100`

### 2. Sourcing Rules (not Origin/Destination)

The API field is named **`sourcingRules`**, not `originDestination`:
```json
"sourcingRules": {
  "adjustmentType": "ORIGIN_DESTINATION",
  "description": "Destination Based Taxation",
  "value": "D"
}
```

### 3. Tax Summaries with Display Rates

Tax summaries include a nested `displayRates` array:
```json
"taxSummaries": [
  {
    "rate": 0.0775,
    "taxType": "SALES_TAX",
    "summaryName": "Total Base Sales Tax",
    "displayRates": [
      {
        "name": "Total Rate",
        "rate": 0.0775
      }
    ]
  }
]
```

### 4. Base Rates Field Details

Base rates contain:
- `rate` (float, required)
- `jurType` (string, required) - e.g., "US_STATE_SALES_TAX"
- `jurName` (string, required) - actual name like "CA", "ORANGE", "IRVINE", "Local District: 37"
- `jurDescription` (string, optional) - human-readable description
- `jurTaxCode` (string, optional, can be null) - tax code

**Important:** `jurName` contains the **actual jurisdiction name**, not an enum!

## Python SDK Field Mapping

| API Field          | Python Property    | Type                    |
|--------------------|--------------------|-------------------------|
| `metadata`         | `metadata`         | V60Metadata             |
| `metadata.response`| `response`         | V60ResponseInfo         |
| `baseRates`        | `base_rates`       | List[V60BaseRate]       |
| `service`          | `service`          | V60Service              |
| `shipping`         | `shipping`         | V60Shipping             |
| `sourcingRules`    | `sourcing_rules`   | V60SourcingRules        |
| `taxSummaries`     | `tax_summaries`    | List[V60TaxSummary]     |
| `displayRates`     | `display_rates`    | List[V60DisplayRate]    |
| `addressDetail`    | `addressDetail`    | V60AddressDetail        |

## Usage Examples

### Accessing Response Code

```python
# Correct way to access response code:
response.metadata.response.code              # 100
response.metadata.response.name              # "RESPONSE_CODE_SUCCESS"
response.metadata.response.message           # "Successful API Request."
```

### Accessing Sourcing Rules

```python
# Correct way to access sourcing rules:
if response.sourcing_rules:
    print(response.sourcing_rules.value)         # "D" for Destination
    print(response.sourcing_rules.description)   # "Destination Based Taxation"
```

### Accessing Tax Summaries with Display Rates

```python
# Correct way to access tax summaries:
if response.tax_summaries:
    for summary in response.tax_summaries:
        print(f"{summary.summary_name}: {summary.rate}")

        # Access display rates
        for display_rate in summary.display_rates:
            print(f"  {display_rate.name}: {display_rate.rate}")
```

### Accessing Base Rates

```python
# Base rates with actual jurisdiction names:
if response.base_rates:
    for rate in response.base_rates:
        print(f"{rate.jur_name}: {rate.rate * 100:.3f}%")
        print(f"  Type: {rate.jur_type}")

        # Optional fields:
        if rate.jur_description:
            print(f"  Description: {rate.jur_description}")
        if rate.jur_tax_code:
            print(f"  Tax Code: {rate.jur_tax_code}")
```

## What Changed from Initial Implementation

### 1. Metadata Structure
- **Before:** `metadata.response_code` (flat)
- **After:** `metadata.response.code` (nested object)

### 2. Field Name
- **Before:** `origin_destination`
- **After:** `sourcing_rules` (matches API field name)

### 3. Tax Summaries
- **Before:** No `display_rates` field
- **After:** Added `display_rates: List[V60DisplayRate]`

### 4. Jurisdiction Fields
- **Before:** `jurName` was an enum (US_STATE, US_COUNTY, etc.)
- **After:** `jurName` is a string (actual names like "CA", "ORANGE", "IRVINE")

### 5. Optional Fields
- **Before:** Many fields were required
- **After:** Made appropriate fields optional (`rateId`, `jurDescription`, `jurTaxCode`)

## Testing with Real API

Use `examples/quick_test.py` to test with your actual API key:

```bash
# Edit the file to add your API key
python3 examples/quick_test.py
```

This will show you the actual response structure and verify all fields are correctly mapped.
