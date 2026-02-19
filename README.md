# Ziptax Python SDK

Official Python SDK for the [Ziptax API](https://zip-tax.com) - Get accurate sales and use tax rates for any US or Canadian address, with optional TaxCloud order management support.

[![Python Version](https://img.shields.io/pypi/pyversions/ziptax-sdk)](https://pypi.org/project/ziptax-sdk/)
[![License](https://img.shields.io/github/license/ziptax/ziptax-python)](LICENSE)

## Features

### Core Features (ZipTax API)
- 🚀 Simple and intuitive API
- 🛒 Cart tax calculation with automatic origin/destination sourcing
- 🔄 Automatic retry logic with exponential backoff
- ✅ Input validation
- 🔍 Type hints for better IDE support
- 📦 Pydantic models for response validation
- 🔒 Comprehensive error handling
- ⚡ Support for concurrent operations
- 🧪 Well-tested with high code coverage

### TaxCloud Integration (Optional)
- 📋 **Order Management**: Create, retrieve, and update orders
- 💰 **Refund Processing**: Full and partial refund support
- 🔗 **Dual API Support**: Seamlessly integrate both ZipTax and TaxCloud
- 🔐 **Optional Configuration**: TaxCloud features only enabled when credentials provided

## Installation

```bash
pip install ziptax-sdk
```

## Quick Start

```python
from ziptax import ZipTaxClient

# Initialize the client with your API key
client = ZipTaxClient.api_key("your-api-key-here")

# Get sales tax by address
response = client.request.GetSalesTaxByAddress(
    "200 Spectrum Center Drive, Irvine, CA 92618"
)

print(f"Address: {response.address_detail.normalized_address}")
if response.tax_summaries:
    for summary in response.tax_summaries:
        print(f"{summary.summary_name}: {summary.rate * 100:.2f}%")

# Always close the client when done
client.close()
```

## Usage

### Initialize the Client

```python
from ziptax import ZipTaxClient

# Basic initialization
client = ZipTaxClient.api_key("your-api-key-here")

# With custom configuration
client = ZipTaxClient.api_key(
    "your-api-key-here",
    timeout=60,           # Request timeout in seconds
    max_retries=5,        # Maximum retry attempts
    retry_delay=2.0,      # Base delay between retries
)

# Using as a context manager (recommended)
with ZipTaxClient.api_key("your-api-key-here") as client:
    response = client.request.GetSalesTaxByAddress("123 Main St")
```

### Get Sales Tax by Address

```python
response = client.request.GetSalesTaxByAddress(
    address="200 Spectrum Center Drive, Irvine, CA 92618",
    country_code="USA",      # Optional: "USA" or "CAN" (default: "USA")
    historical="202401",     # Optional: Historical date (YYYYMM format)
    format="json",           # Optional: Response format (default: "json")
)

# Access response data
print(response.address_detail.normalized_address)
print(response.address_detail.geo_lat)
print(response.address_detail.geo_lng)

# Response code
print(f"Response: {response.metadata.response.code} - {response.metadata.response.message}")

# Tax summaries with display rates
if response.tax_summaries:
    for summary in response.tax_summaries:
        print(f"{summary.summary_name}: {summary.rate}")
        for display_rate in summary.display_rates:
            print(f"  {display_rate.name}: {display_rate.rate}")

# Base rates by jurisdiction
if response.base_rates:
    for rate in response.base_rates:
        print(f"{rate.jur_name} ({rate.jur_type}): {rate.rate}")

# Sourcing rules
if response.sourcing_rules:
    print(f"Sourcing: {response.sourcing_rules.value}")
```

### Get Sales Tax by Geolocation

```python
response = client.request.GetSalesTaxByGeoLocation(
    lat="33.6489",
    lng="-117.8386",
    country_code="USA",
    format="json",
)

print(response.address_detail.normalized_address)
```

### Get Rates by Postal Code

```python
response = client.request.GetRatesByPostalCode(
    postal_code="92694",
    format="json",
)

# Response includes all tax jurisdictions for the postal code
for result in response.results:
    print(f"{result.geo_city}, {result.geo_state}")
    print(f"Sales Tax: {result.tax_sales * 100:.2f}%")
    print(f"Use Tax: {result.tax_use * 100:.2f}%")
```

### Get Account Metrics

```python
metrics = client.request.GetAccountMetrics()

print(f"Requests: {metrics.request_count:,} / {metrics.request_limit:,}")
print(f"Usage: {metrics.usage_percent:.2f}%")
print(f"Account Active: {metrics.is_active}")
print(f"Message: {metrics.message}")
```

### Calculate Cart Tax

Calculate sales tax for a shopping cart with multiple line items. The SDK automatically resolves origin/destination sourcing rules before sending the request to the API.

```python
from ziptax.models import (
    CalculateCartRequest,
    CartItem,
    CartAddress,
    CartCurrency,
    CartLineItem,
)

# Build the cart request
request = CalculateCartRequest(
    items=[
        CartItem(
            customer_id="customer-453",
            currency=CartCurrency(currency_code="USD"),
            destination=CartAddress(
                address="200 Spectrum Center Dr, Irvine, CA 92618"
            ),
            origin=CartAddress(
                address="323 Washington Ave N, Minneapolis, MN 55401"
            ),
            line_items=[
                CartLineItem(
                    item_id="item-1",
                    price=10.75,
                    quantity=1.5,
                ),
                CartLineItem(
                    item_id="item-2",
                    price=25.00,
                    quantity=2.0,
                    taxability_code=0,
                ),
            ],
        )
    ]
)

# Calculate tax
result = client.request.CalculateCart(request)

# Access results
cart = result.items[0]
print(f"Cart ID: {cart.cart_id}")
for item in cart.line_items:
    print(f"  {item.item_id}: rate={item.tax.rate}, amount=${item.tax.amount:.2f}")
```

#### Origin/Destination Sourcing

The SDK automatically determines whether to use origin-based or destination-based tax rates:

- **Interstate** (different states): Uses the destination address
- **Intrastate, destination-based** (e.g., CA, NY): Uses the destination address
- **Intrastate, origin-based** (e.g., TX, OH): Uses the origin address

This is handled transparently -- the SDK looks up both addresses via `GetSalesTaxByAddress`, checks the `sourcingRules.value` field, and sends the correct address to the cart API.

#### Validation

The cart models enforce constraints at construction time via Pydantic:

- `items` must contain exactly 1 cart
- `line_items` must contain 1-250 items
- `price` and `quantity` must be greater than 0
- `currency_code` must be `"USD"`

```python
from pydantic import ValidationError

try:
    CartLineItem(item_id="item-1", price=-5.00, quantity=1.0)
except ValidationError as e:
    print(e)  # price must be greater than 0
```

## TaxCloud Order Management

The SDK includes optional support for TaxCloud order management features. To use these features, you need both a ZipTax API key and TaxCloud credentials (Connection ID and API Key).

### Initialize Client with TaxCloud Support

```python
from ziptax import ZipTaxClient

# Initialize with TaxCloud credentials
client = ZipTaxClient.api_key(
    api_key="your-ziptax-api-key",
    taxcloud_connection_id="25eb9b97-5acb-492d-b720-c03e79cf715a",
    taxcloud_api_key="your-taxcloud-api-key",
)

# TaxCloud features are now available via client.request
```

### Create an Order

```python
from ziptax.models import (
    CreateOrderRequest,
    TaxCloudAddress,
    CartItemWithTax,
    Tax,
    Currency,
)

# Prepare order request
order_request = CreateOrderRequest(
    order_id="my-order-1",
    customer_id="customer-453",
    transaction_date="2024-01-15T09:30:00Z",
    completed_date="2024-01-15T09:30:00Z",
    origin=TaxCloudAddress(
        line1="323 Washington Ave N",
        city="Minneapolis",
        state="MN",
        zip="55401-2427",
    ),
    destination=TaxCloudAddress(
        line1="323 Washington Ave N",
        city="Minneapolis",
        state="MN",
        zip="55401-2427",
    ),
    line_items=[
        CartItemWithTax(
            index=0,
            item_id="item-1",
            price=10.8,
            quantity=1.5,
            tax=Tax(amount=1.31, rate=0.0813),
        )
    ],
    currency=Currency(currency_code="USD"),
)

# Create the order
order = client.request.CreateOrder(order_request)
print(f"Created order: {order.order_id}")
print(f"Tax amount: ${order.line_items[0].tax.amount}")
```

### Retrieve an Order

```python
# Get an existing order by ID
order = client.request.GetOrder("my-order-1")

print(f"Order ID: {order.order_id}")
print(f"Customer ID: {order.customer_id}")
print(f"Completed Date: {order.completed_date}")
print(f"Total Tax: ${sum(item.tax.amount for item in order.line_items)}")
```

### Update an Order

```python
from ziptax.models import UpdateOrderRequest

# Update the order's completed date
update_request = UpdateOrderRequest(
    completed_date="2024-01-16T10:00:00Z"
)

updated_order = client.request.UpdateOrder("my-order-1", update_request)
print(f"Updated completed date: {updated_order.completed_date}")
```

### Create a Refund

```python
from ziptax.models import (
    RefundTransactionRequest,
    CartItemRefundWithTaxRequest,
)

# Partial refund - specify items and quantities
refund_request = RefundTransactionRequest(
    items=[
        CartItemRefundWithTaxRequest(
            item_id="item-1",
            quantity=1.0,
        )
    ]
)
refunds = client.request.RefundOrder("my-order-1", refund_request)
print(f"Refunded tax: ${refunds[0].items[0].tax.amount}")

# Full refund - omit items parameter
full_refunds = client.request.RefundOrder("my-order-2")
print("Full refund created")
```

### TaxCloud Error Handling

```python
from ziptax import ZipTaxCloudConfigError

try:
    # Attempt to use TaxCloud feature without credentials
    order = client.request.GetOrder("my-order-1")

except ZipTaxCloudConfigError as e:
    # TaxCloud credentials not configured
    print(f"TaxCloud error: {e.message}")
    print("Please provide taxcloud_connection_id and taxcloud_api_key")

except ZipTaxNotFoundError as e:
    # Order not found
    print(f"Order not found: {e.message}")
```

### Configuration

You can configure the client using dict-style access:

```python
client = ZipTaxClient.api_key("your-api-key-here")

# Set configuration options
client.config["format"] = "json"
client.config["timeout"] = 60

# Get configuration options
timeout = client.config["timeout"]
```

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

```python
from ziptax import (
    ZipTaxClient,
    ZipTaxValidationError,
    ZipTaxAuthenticationError,
    ZipTaxRateLimitError,
    ZipTaxServerError,
    ZipTaxError,
)

client = ZipTaxClient.api_key("your-api-key-here")

try:
    response = client.request.GetSalesTaxByAddress("123 Main St")

except ZipTaxValidationError as e:
    # Input validation errors
    print(f"Validation error: {e.message}")

except ZipTaxAuthenticationError as e:
    # Authentication failures (401)
    print(f"Authentication error: {e.message}")

except ZipTaxRateLimitError as e:
    # Rate limit exceeded (429)
    print(f"Rate limit error: {e.message}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")

except ZipTaxServerError as e:
    # Server errors (5xx)
    print(f"Server error: {e.message}")

except ZipTaxError as e:
    # General Ziptax errors
    print(f"Ziptax error: {e.message}")
```

### Exception Hierarchy

```
ZipTaxError
├── ZipTaxAPIError
│   ├── ZipTaxAuthenticationError (401)
│   ├── ZipTaxAuthorizationError (403)
│   ├── ZipTaxNotFoundError (404)
│   ├── ZipTaxRateLimitError (429)
│   └── ZipTaxServerError (5xx)
├── ZipTaxValidationError
├── ZipTaxConnectionError
├── ZipTaxTimeoutError
├── ZipTaxRetryError
└── ZipTaxCloudConfigError (TaxCloud credentials not configured)
```

## Async Operations

For concurrent operations, you can use asyncio with the SDK:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ziptax import ZipTaxClient

async def get_tax_rates_async(client, addresses):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                client.request.GetSalesTaxByAddress,
                address
            )
            for address in addresses
        ]
        return await asyncio.gather(*tasks)

# Usage
client = ZipTaxClient.api_key("your-api-key-here")
addresses = ["123 Main St, CA", "456 Oak Ave, NY"]
responses = asyncio.run(get_tax_rates_async(client, addresses))
```

See [examples/async_usage.py](examples/async_usage.py) for more examples.

## Response Models

All API responses are validated using Pydantic models:

### V60Response

```python
class V60Response:
    metadata: V60Metadata                           # Response metadata with code/message
    base_rates: Optional[List[V60BaseRate]]        # Tax rates by jurisdiction
    service: Optional[V60Service]                   # Service taxability (None for some regions)
    shipping: Optional[V60Shipping]                 # Shipping taxability (None for some regions)
    sourcing_rules: Optional[V60SourcingRules]     # Origin/Destination rules
    tax_summaries: Optional[List[V60TaxSummary]]   # Tax summaries with display rates
    address_detail: V60AddressDetail                # Address details
```

### V60Metadata

```python
class V60Metadata:
    version: str                    # API version (e.g., "v60")
    response: V60ResponseInfo       # Response info object

class V60ResponseInfo:
    code: int                       # Response code (100 = success)
    name: str                       # Response code name
    message: str                    # Response message
    definition: str                 # Schema definition URL
```

### V60TaxSummary

```python
class V60TaxSummary:
    rate: float                                    # Summary tax rate
    tax_type: str                                  # Tax type (e.g., "SALES_TAX")
    summary_name: str                              # Summary description
    display_rates: List[V60DisplayRate]           # Display rates breakdown

class V60DisplayRate:
    name: str                                      # Display rate name
    rate: float                                    # Display rate value
```

### V60AccountMetrics

```python
class V60AccountMetrics:
    request_count: int       # Number of API requests made
    request_limit: int       # Maximum allowed API requests
    usage_percent: float     # Percentage of request limit used
    is_active: bool          # Whether the account is currently active
    message: str             # Account status or informational message
```

**Note:** Uses `extra="allow"` to accept any additional fields the API may return.

See the [models documentation](src/ziptax/models/responses.py) for complete model definitions.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ziptax/ziptax-python.git
cd ziptax-python

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ziptax --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking
mypy src/
```

## Examples

See the [examples/](examples/) directory for complete examples:

- [basic_usage.py](examples/basic_usage.py) - Basic SDK usage
- [async_usage.py](examples/async_usage.py) - Concurrent operations
- [error_handling.py](examples/error_handling.py) - Error handling patterns
- [taxcloud_orders.py](examples/taxcloud_orders.py) - TaxCloud order management

## API Reference

### ZipTaxClient

Main client for interacting with the Ziptax API.

#### Methods

- `api_key(api_key, **kwargs)` - Create a client instance with an API key
- `close()` - Close the HTTP client session

#### Properties

- `config` - Configuration object (dict-like access)
- `request` - Functions object for making API requests

### Functions

API endpoint functions accessible via `client.request`.

#### ZipTax API Methods

- `GetSalesTaxByAddress(address, **kwargs)` - Get tax rates by address
- `GetSalesTaxByGeoLocation(lat, lng, **kwargs)` - Get tax rates by coordinates
- `GetRatesByPostalCode(postal_code, **kwargs)` - Get tax rates by US postal code
- `GetAccountMetrics(**kwargs)` - Get account usage metrics
- `CalculateCart(request)` - Calculate sales tax for a shopping cart with origin/destination sourcing

#### TaxCloud API Methods (Optional)

Requires `taxcloud_connection_id` and `taxcloud_api_key` in client initialization.

- `CreateOrder(request, **kwargs)` - Create an order in TaxCloud
- `GetOrder(order_id)` - Retrieve an order by ID
- `UpdateOrder(order_id, request)` - Update an order's completed date
- `RefundOrder(order_id, request)` - Create a full or partial refund

## Requirements

- Python 3.8+
- requests >= 2.28.0
- pydantic >= 2.0.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://github.com/ziptax/ziptax-python#readme](https://github.com/ziptax/ziptax-python#readme)
- Issues: [https://github.com/ziptax/ziptax-python/issues](https://github.com/ziptax/ziptax-python/issues)
- Email: support@zip.tax

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and write tests
4. **Bump the version** using `python scripts/bump_version.py patch` (or `minor`/`major`)
5. Update CHANGELOG.md with your changes
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

**Note**: All PRs require a version bump. See [docs/VERSIONING.md](docs/VERSIONING.md) for details on our versioning strategy.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

---

Made with ❤️ by the Ziptax Team
