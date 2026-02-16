"""Async usage example for the ZipTax SDK.

Note: This example demonstrates concurrent operations using asyncio with the
synchronous client. Full async HTTP support (using aiohttp) can be added as
a future enhancement for better performance.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from ziptax import ZipTaxClient


async def get_tax_by_address_async(client, address):
    """Async wrapper for GetSalesTaxByAddress.

    Args:
        client: ZipTaxClient instance
        address: Address to query

    Returns:
        V60Response object
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        response = await loop.run_in_executor(
            executor,
            client.request.GetSalesTaxByAddress,
            address,
        )
    return response


async def get_tax_by_location_async(client, lat, lng):
    """Async wrapper for GetSalesTaxByGeoLocation.

    Args:
        client: ZipTaxClient instance
        lat: Latitude
        lng: Longitude

    Returns:
        V60Response object
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        response = await loop.run_in_executor(
            executor,
            client.request.GetSalesTaxByGeoLocation,
            lat,
            lng,
        )
    return response


async def get_account_metrics_async(client):
    """Async wrapper for GetAccountMetrics.

    Args:
        client: ZipTaxClient instance

    Returns:
        V60AccountMetrics object
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        response = await loop.run_in_executor(
            executor,
            client.request.GetAccountMetrics,
        )
    return response


async def main():
    """Main async function demonstrating concurrent API calls."""

    # Initialize the client
    client = ZipTaxClient.api_key("your-api-key-here")

    try:
        # Example 1: Run multiple address lookups concurrently
        print("=" * 60)
        print("Example 1: Concurrent Address Lookups")
        print("=" * 60)

        addresses = [
            "200 Spectrum Center Drive, Irvine, CA 92618",
            "1 Apple Park Way, Cupertino, CA 95014",
            "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        ]

        # Create tasks for all addresses
        tasks = [get_tax_by_address_async(client, addr) for addr in addresses]

        # Run all tasks concurrently
        responses = await asyncio.gather(*tasks)

        # Process results
        for address, response in zip(addresses, responses):
            print(f"\nAddress: {response.address_detail.normalized_address}")
            if response.tax_summaries:
                for summary in response.tax_summaries:
                    print(f"  {summary.summary_name}: {summary.rate * 100:.2f}%")

        # Example 2: Mix different API calls concurrently
        print("\n" + "=" * 60)
        print("Example 2: Mixed Concurrent API Calls")
        print("=" * 60)

        # Create tasks for different API endpoints
        address_task = get_tax_by_address_async(
            client,
            "123 Main St, Los Angeles, CA 90001"
        )
        location_task = get_tax_by_location_async(
            client,
            "34.0522",
            "-118.2437"
        )
        metrics_task = get_account_metrics_async(client)

        # Run all tasks concurrently
        address_response, location_response, metrics = await asyncio.gather(
            address_task,
            location_task,
            metrics_task,
        )

        print(f"\nAddress lookup: {address_response.address_detail.normalized_address}")
        print(f"Location lookup: {location_response.address_detail.normalized_address}")
        print(f"Account metrics: {metrics.request_count:,} requests")

        # Example 3: Process results as they complete
        print("\n" + "=" * 60)
        print("Example 3: Process Results as They Complete")
        print("=" * 60)

        locations = [
            ("33.6489", "-117.8386"),
            ("34.0522", "-118.2437"),
            ("37.7749", "-122.4194"),
        ]

        tasks = [
            get_tax_by_location_async(client, lat, lng)
            for lat, lng in locations
        ]

        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            response = await coro
            print(f"Completed: {response.address_detail.normalized_address}")
            if response.tax_summaries:
                rate = response.tax_summaries[0].rate
                print(f"  Tax rate: {rate * 100:.2f}%")

    finally:
        # Always close the client
        client.close()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
