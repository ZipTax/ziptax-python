"""Basic usage example for the ZipTax SDK."""

from ziptax import ZipTaxClient

# Initialize the client with your API key
client = ZipTaxClient.api_key("your-api-key-here")

# Optional: Configure additional settings
client.config["format"] = "json"
client.config["timeout"] = 30

# Example 1: Get sales tax by address
print("=" * 60)
print("Example 1: Get Sales Tax by Address")
print("=" * 60)

response = client.request.GetSalesTaxByAddress(
    "200 Spectrum Center Drive, Irvine, CA 92618"
)

print(f"Address: {response.addressDetail.normalizedAddress}")
print(f"Latitude: {response.addressDetail.geoLat}")
print(f"Longitude: {response.addressDetail.geoLng}")
print(f"Incorporated: {response.addressDetail.incorporated}")
print(f"\nService Taxable: {response.service.taxable}")
print(f"Shipping Taxable: {response.shipping.taxable}")
if response.sourcing_rules:
    print(
        f"Sourcing: {response.sourcing_rules.value} ({response.sourcing_rules.description})"
    )

if response.tax_summaries:
    print(f"\nTax Summaries:")
    for summary in response.tax_summaries:
        print(f"  - {summary.summary_name}: {summary.rate * 100:.3f}%")

if response.base_rates:
    print(f"\nBase Rates:")
    for rate in response.base_rates:
        print(f"  - {rate.jur_description} ({rate.jur_type}): {rate.rate * 100:.2f}%")

# Example 2: Get sales tax by geolocation
print("\n" + "=" * 60)
print("Example 2: Get Sales Tax by Geolocation")
print("=" * 60)

response = client.request.GetSalesTaxByGeoLocation(
    lat="33.6489",
    lng="-117.8386",
)

print(f"Address: {response.addressDetail.normalizedAddress}")

if response.tax_summaries:
    for summary in response.tax_summaries:
        print(f"{summary.summary_name}: {summary.rate * 100:.2f}%")

# Example 3: Get sales tax with historical date
print("\n" + "=" * 60)
print("Example 3: Get Sales Tax with Historical Date")
print("=" * 60)

response = client.request.GetSalesTaxByAddress(
    address="1 Apple Park Way, Cupertino, CA 95014",
    historical="2024-01",
)

print(f"Address: {response.addressDetail.normalizedAddress}")
if response.tax_summaries:
    for summary in response.tax_summaries:
        print(f"{summary.summary_name}: {summary.rate * 100:.2f}%")

# Example 4: Get sales tax by postal code
print("\n" + "=" * 60)
print("Example 4: Get Sales Tax by Postal Code")
print("=" * 60)

response = client.request.GetRatesByPostalCode("92694")

print(f"Postal Code: {response.results[0].geo_postal_code}")
print(f"API Version: {response.version}")
print(f"Response Code: {response.r_code}")
print(f"\nFound {len(response.results)} location(s) for this postal code:\n")

for result in response.results:
    print(f"Location: {result.geo_city}, {result.geo_state} {result.geo_postal_code}")
    print(f"  County: {result.geo_county}")
    print(f"  Total Sales Tax: {result.tax_sales * 100:.2f}%")
    print(f"  Total Use Tax: {result.tax_use * 100:.2f}%")
    print(f"  Service Taxable: {result.txb_service}")
    print(f"  Freight Taxable: {result.txb_freight}")
    print(f"  Sourcing: {result.origin_destination}")
    print(f"  State Sales Tax: {result.state_sales_tax * 100:.2f}%")
    print(f"  County Sales Tax: {result.county_sales_tax * 100:.2f}%")
    print(f"  City Sales Tax: {result.city_sales_tax * 100:.2f}%")
    print(f"  District Sales Tax: {result.district_sales_tax * 100:.2f}%")
    print()

# Example 5: Get account metrics
print("=" * 60)
print("Example 5: Get Account Metrics")
print("=" * 60)

metrics = client.request.GetAccountMetrics()

print(f"Core Request Count: {metrics.core_request_count:,}")
print(f"Core Request Limit: {metrics.core_request_limit:,}")
print(f"Core Usage: {metrics.core_usage_percent:.2f}%")
print(f"\nGeo Enabled: {metrics.geo_enabled}")
print(f"Geo Request Count: {metrics.geo_request_count:,}")
print(f"Geo Request Limit: {metrics.geo_request_limit:,}")
print(f"Geo Usage: {metrics.geo_usage_percent:.2f}%")
print(f"\nAccount Active: {metrics.is_active}")
print(f"Message: {metrics.message}")

# Always close the client when done (or use context manager)
client.close()

# Alternatively, use as a context manager
print("\n" + "=" * 60)
print("Example 6: Using Context Manager")
print("=" * 60)

with ZipTaxClient.api_key("your-api-key-here") as client:
    response = client.request.GetSalesTaxByAddress("123 Main St, Los Angeles, CA 90001")
    print(f"Address: {response.addressDetail.normalizedAddress}")
    if response.tax_summaries:
        for summary in response.tax_summaries:
            print(f"{summary.summary_name}: {summary.rate * 100:.2f}%")
