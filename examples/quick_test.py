"""Quick test script to verify the SDK works with real API responses."""

from ziptax import ZipTaxClient

# Replace with your actual API key
API_KEY = "your-api-key-here"

def test_address_lookup():
    """Test basic address lookup."""
    print("=" * 60)
    print("Testing GetSalesTaxByAddress")
    print("=" * 60)

    client = ZipTaxClient.api_key(API_KEY)

    try:
        response = client.request.GetSalesTaxByAddress(
            "200 Spectrum Center Drive, Irvine, CA 92618"
        )

        print(f"✓ Success!")
        print(f"  Address: {response.address_detail.normalized_address}")
        print(f"  Latitude: {response.address_detail.geo_lat}")
        print(f"  Longitude: {response.address_detail.geo_lng}")

        if response.service:
            print(f"\n  Service Taxable: {response.service.taxable}")
        if response.shipping:
            print(f"  Shipping Taxable: {response.shipping.taxable}")

        if response.sourcing_rules:
            print(f"  Sourcing: {response.sourcing_rules.value} ({response.sourcing_rules.description})")

        if response.tax_summaries:
            print(f"\n  Tax Summaries:")
            for summary in response.tax_summaries:
                print(f"    - {summary.summary_name}: {summary.rate * 100:.3f}%")

        if response.base_rates:
            print(f"\n  Base Rates ({len(response.base_rates)} jurisdictions):")
            for i, rate in enumerate(response.base_rates[:3], 1):  # Show first 3
                print(f"    {i}. {rate.jur_name} ({rate.jur_type}): {rate.rate * 100:.3f}%")
                if rate.jur_description:
                    print(f"       Description: {rate.jur_description}")
            if len(response.base_rates) > 3:
                print(f"    ... and {len(response.base_rates) - 3} more")

        print(f"\n  Response Code: {response.metadata.response.code} ({response.metadata.response.name})")
        print(f"  Response Message: {response.metadata.response.message}")
        print(f"  API Version: {response.metadata.version}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


def test_geolocation_lookup():
    """Test geolocation lookup."""
    print("\n" + "=" * 60)
    print("Testing GetSalesTaxByGeoLocation")
    print("=" * 60)

    client = ZipTaxClient.api_key(API_KEY)

    try:
        response = client.request.GetSalesTaxByGeoLocation(
            lat="33.6489",
            lng="-117.8386"
        )

        print(f"✓ Success!")
        print(f"  Address: {response.address_detail.normalized_address}")

        if response.tax_summaries:
            for summary in response.tax_summaries:
                print(f"  {summary.summary_name}: {summary.rate * 100:.3f}%")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


def test_account_metrics():
    """Test account metrics."""
    print("\n" + "=" * 60)
    print("Testing GetAccountMetrics")
    print("=" * 60)

    client = ZipTaxClient.api_key(API_KEY)

    try:
        metrics = client.request.GetAccountMetrics()

        print(f"✓ Success!")
        print(f"  Requests: {metrics.request_count:,} / {metrics.request_limit:,}")
        print(f"  Usage: {metrics.usage_percent:.2f}%")
        print(f"  Account Active: {metrics.is_active}")
        print(f"  Message: {metrics.message}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


if __name__ == "__main__":
    if API_KEY == "your-api-key-here":
        print("⚠️  Please set your API key in the script before running!")
        print("   Edit this file and replace 'your-api-key-here' with your actual key.")
        exit(1)

    test_address_lookup()
    test_geolocation_lookup()
    test_account_metrics()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
