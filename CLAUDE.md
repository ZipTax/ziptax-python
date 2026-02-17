# CLAUDE.md - AI Development Guide

This document provides comprehensive guidance for AI assistants (like Claude) working on the ZipTax Python SDK project. It covers the codebase architecture, development patterns, testing requirements, and contribution guidelines.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Development Environment](#development-environment)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Common Tasks](#common-tasks)
- [API Integration](#api-integration)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is This Project?

The ZipTax Python SDK is an official client library that provides programmatic access to:

1. **ZipTax API** (Primary) - Sales and use tax rate lookups for US and Canadian addresses
2. **TaxCloud API** (Optional) - Order management and refund processing capabilities

### Key Design Principles

- **Dual API Support**: The SDK seamlessly integrates two separate APIs with a unified interface
- **Optional Features**: TaxCloud functionality is completely optional - users can use ZipTax features without TaxCloud credentials
- **Type Safety**: Full type hints using Python type annotations and Pydantic models
- **Error Handling**: Comprehensive exception hierarchy for different error scenarios
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Backward Compatibility**: All existing ZipTax functionality remains unchanged

---

## Architecture

### Directory Structure

```
ziptax-python/
├── src/ziptax/              # Main source code
│   ├── __init__.py          # Package exports
│   ├── client.py            # Main ZipTaxClient class
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   ├── models/              # Pydantic data models
│   │   ├── __init__.py
│   │   └── responses.py     # API response models
│   ├── resources/           # API endpoint functions
│   │   ├── __init__.py
│   │   └── functions.py     # ZipTax and TaxCloud functions
│   └── utils/               # Utility modules
│       ├── __init__.py
│       ├── http.py          # HTTP client wrapper
│       ├── retry.py         # Retry logic
│       └── validation.py    # Input validation
├── tests/                   # Test suite
├── examples/                # Usage examples
├── docs/                    # Documentation
│   └── spec.yaml           # OpenAPI-style specification
├── pyproject.toml          # Project configuration
└── README.md               # User documentation
```

### Core Components

#### 1. **Client (`client.py`)**

- **Purpose**: Main entry point for SDK users
- **Key Features**:
  - Factory method `api_key()` for initialization
  - Manages two HTTP clients (ZipTax + optional TaxCloud)
  - Context manager support for resource cleanup
  - Passes configuration to Functions class

**Important Implementation Details**:
```python
# Client initialization pattern
client = ZipTaxClient.api_key(
    api_key="ziptax-key",                    # Required
    taxcloud_connection_id="uuid",           # Optional
    taxcloud_api_key="taxcloud-key",         # Optional
)

# Two separate HTTP clients are created:
# 1. self._http_client (ZipTax API)
# 2. self._taxcloud_http_client (TaxCloud API, if configured)
```

#### 2. **Configuration (`config.py`)**

- **Purpose**: Centralized configuration management
- **Key Properties**:
  - `api_key`: ZipTax API key (required)
  - `base_url`: ZipTax API base URL
  - `taxcloud_connection_id`: TaxCloud Connection ID (optional)
  - `taxcloud_api_key`: TaxCloud API key (optional)
  - `taxcloud_base_url`: TaxCloud API base URL
  - `has_taxcloud_config`: Boolean property to check if TaxCloud is configured

**Implementation Pattern**:
```python
# Config uses properties with private attributes
@property
def has_taxcloud_config(self) -> bool:
    return bool(self._taxcloud_connection_id and self._taxcloud_api_key)
```

#### 3. **Functions (`resources/functions.py`)**

- **Purpose**: Implements all API endpoint methods
- **Architecture**:
  - Takes both `http_client` and optional `taxcloud_http_client`
  - Uses decorator pattern for retry logic
  - TaxCloud methods check credentials before executing

**Critical Pattern**:
```python
def _check_taxcloud_config(self) -> None:
    """Check if TaxCloud credentials are configured."""
    if not self.config.has_taxcloud_config or self.taxcloud_http_client is None:
        raise ZipTaxCloudConfigError(
            "TaxCloud credentials not configured. Please provide "
            "taxcloud_connection_id and taxcloud_api_key when creating the client."
        )

# All TaxCloud methods call this first
def CreateOrder(self, request: CreateOrderRequest, ...) -> OrderResponse:
    self._check_taxcloud_config()  # Guards against missing credentials
    # ... implementation
```

#### 4. **HTTP Client (`utils/http.py`)**

- **Purpose**: Wraps `requests` library with error handling
- **Methods**: `get()`, `post()`, `patch()`
- **Features**:
  - Automatic error response handling
  - Status code to exception mapping
  - Timeout and retry support
  - Session management for connection pooling

**Key Implementation**:
```python
# HTTP client is API-agnostic
# Uses X-API-Key header for authentication
self.session.headers.update({"X-API-Key": api_key})
```

#### 5. **Models (`models/responses.py`)**

- **Purpose**: Pydantic models for request/response validation
- **Structure**:
  - V60 models for ZipTax API responses
  - TaxCloud models for order management
  - Uses `Field` with `alias` for camelCase ↔ snake_case mapping

**Pydantic Configuration**:
```python
# All models use this configuration
model_config = ConfigDict(populate_by_name=True)

# Field aliases map API fields to Python conventions
order_id: str = Field(..., alias="orderId", description="...")
```

---

## Development Environment

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/ziptax/ziptax-python.git
cd ziptax-python

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import ziptax; print(ziptax.__version__)"
```

### Development Dependencies

```python
# Defined in pyproject.toml [project.optional-dependencies]
dev = [
    "pytest>=7.0.0",           # Testing framework
    "pytest-cov>=4.0.0",       # Coverage reporting
    "black>=23.0.0",           # Code formatting
    "mypy>=1.0.0",             # Type checking
    "ruff>=0.1.0",             # Linting
]
```

---

## Code Standards

### Type Hints

**Required**: All functions must have complete type hints

```python
# Good ✅
def GetOrder(self, order_id: str) -> OrderResponse:
    pass

# Bad ❌
def GetOrder(self, order_id):
    pass
```

### Pydantic Models

**Pattern**: Use Pydantic v2 with `ConfigDict`

```python
# Good ✅
class OrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(..., alias="orderId", description="...")

# Bad ❌ (Pydantic v1 pattern)
class OrderResponse(BaseModel):
    class Config:
        allow_population_by_field_name = True
```

### Error Handling

**Pattern**: Always check for TaxCloud configuration before using TaxCloud features

```python
# Good ✅
def CreateOrder(self, request: CreateOrderRequest) -> OrderResponse:
    self._check_taxcloud_config()  # Raises ZipTaxCloudConfigError if not configured

    # Type checker needs assertion
    assert self.taxcloud_http_client is not None

    # ... implementation

# Bad ❌
def CreateOrder(self, request: CreateOrderRequest) -> OrderResponse:
    # Missing config check
    return self.taxcloud_http_client.post(...)  # Type error + runtime error
```

### Naming Conventions

- **Classes**: PascalCase (`ZipTaxClient`, `OrderResponse`)
- **Functions**: PascalCase for API methods (`GetSalesTaxByAddress`), snake_case for internal (`_check_taxcloud_config`)
- **Variables**: snake_case (`order_id`, `tax_amount`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)

### Documentation

**Required**: All public methods must have docstrings with:
- Purpose description
- Args section with types
- Returns section with type
- Raises section for exceptions
- Example usage (for complex methods)

```python
def CreateOrder(
    self,
    request: CreateOrderRequest,
    address_autocomplete: str = "none",
) -> OrderResponse:
    """Create an order in TaxCloud.

    Args:
        request: CreateOrderRequest object with order details
        address_autocomplete: Address autocomplete option (default: "none")
            Options: "none", "origin", "destination", "all"

    Returns:
        OrderResponse object with created order details

    Raises:
        ZipTaxCloudConfigError: If TaxCloud credentials not configured
        ZipTaxAPIError: If the API returns an error

    Example:
        >>> request = CreateOrderRequest(...)
        >>> order = client.request.CreateOrder(request)
    """
```

---

## Testing Requirements

### Code Coverage

**Minimum Requirement**: 80% code coverage

```bash
# Run tests with coverage
pytest --cov=src/ziptax --cov-report=term-missing

# Enforce minimum coverage
coverage report --fail-under=80
```

### Test Structure

```
tests/
├── test_client.py          # Client initialization and lifecycle
├── test_functions.py       # API endpoint functions
├── test_http.py           # HTTP client functionality
├── test_retry.py          # Retry logic
└── conftest.py            # Shared fixtures
```

### Testing Patterns

#### 1. **Mocking HTTP Requests**

```python
import pytest
from unittest.mock import Mock, patch

def test_create_order(mock_http_client):
    """Test order creation."""
    # Mock response
    mock_response = {
        "orderId": "test-order-1",
        "customerId": "customer-1",
        # ... full response
    }

    mock_http_client.post.return_value = mock_response

    # Test the function
    result = client.request.CreateOrder(request)

    assert result.order_id == "test-order-1"
```

#### 2. **Testing Error Handling**

```python
def test_taxcloud_without_credentials():
    """Test TaxCloud method without credentials raises error."""
    client = ZipTaxClient.api_key("test-key")  # No TaxCloud credentials

    with pytest.raises(ZipTaxCloudConfigError) as exc_info:
        client.request.GetOrder("order-1")

    assert "TaxCloud credentials not configured" in str(exc_info.value)
```

#### 3. **Testing Retry Logic**

```python
@patch('time.sleep')  # Mock sleep to speed up tests
def test_retry_on_server_error(mock_sleep, mock_http_client):
    """Test automatic retry on server errors."""
    # Fail twice, then succeed
    mock_http_client.get.side_effect = [
        ZipTaxServerError("Server error", 500),
        ZipTaxServerError("Server error", 500),
        {"data": "success"}
    ]

    result = client.request.GetOrder("order-1")

    assert result is not None
    assert mock_http_client.get.call_count == 3
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_functions.py

# Run specific test
pytest tests/test_functions.py::test_create_order

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/ziptax --cov-report=html
```

---

## Common Tasks

### Adding a New API Endpoint

**Step 1**: Add the data models to `models/responses.py`

```python
class NewFeatureRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field_name: str = Field(..., alias="fieldName", description="...")

class NewFeatureResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    result: str = Field(..., description="...")
```

**Step 2**: Export models in `models/__init__.py`

```python
from .responses import (
    # ... existing exports
    NewFeatureRequest,
    NewFeatureResponse,
)

__all__ = [
    # ... existing exports
    "NewFeatureRequest",
    "NewFeatureResponse",
]
```

**Step 3**: Add the function to `resources/functions.py`

```python
def NewFeature(self, request: NewFeatureRequest) -> NewFeatureResponse:
    """Description of the new feature.

    Args:
        request: NewFeatureRequest with input data

    Returns:
        NewFeatureResponse with results

    Raises:
        ZipTaxAPIError: If the API returns an error
    """
    # Validation
    # ...

    # Make request with retry logic
    @retry_with_backoff(
        max_retries=self.max_retries,
        base_delay=self.retry_delay,
    )
    def _make_request() -> Dict[str, Any]:
        return self.http_client.post("/new/endpoint", json=request.model_dump())

    response_data = _make_request()
    return NewFeatureResponse(**response_data)
```

**Step 4**: Add tests in `tests/test_functions.py`

**Step 5**: Update documentation in `README.md` and examples

**Step 6**: Run quality checks

```bash
black src/ tests/
ruff check src/ tests/
mypy src/ziptax/
pytest --cov=src/ziptax --cov-report=term
```

### Adding HTTP Methods

The HTTP client (`utils/http.py`) currently supports GET, POST, and PATCH. To add more:

```python
def delete(
    self,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Make a DELETE request to the API."""
    url = f"{self.base_url}{path}"
    logger.debug(f"DELETE {url}")

    try:
        response = self.session.delete(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

        if not response.ok:
            self._handle_error_response(response)

        return cast(Dict[str, Any], response.json())

    except requests.exceptions.Timeout as e:
        raise ZipTaxTimeoutError(f"Request timed out after {self.timeout}s: {e}")
    except requests.exceptions.ConnectionError as e:
        raise ZipTaxConnectionError(f"Connection error: {e}")
    except (ZipTaxAPIError, ZipTaxTimeoutError, ZipTaxConnectionError):
        raise
    except Exception as e:
        raise ZipTaxAPIError(f"Unexpected error: {e}")
```

### Updating the Spec File

The `docs/spec.yaml` file serves as the single source of truth for the SDK structure. When adding features:

1. Update the `api` section for new APIs or configuration
2. Update the `resources` section for new endpoints
3. Update the `models` section for new data structures
4. Update the `actual_api_responses` section with real API examples

This file is used as a reference for code generation and documentation.

---

## API Integration

### ZipTax API

**Base URL**: `https://api.zip-tax.com/`

**Authentication**: X-API-Key header

**Endpoints**:
- `GET /request/v60/` - Tax rate lookup by address or geolocation
- `GET /account/v60/metrics` - Account usage metrics

**Response Format**: JSON with nested structure

```json
{
  "metadata": {
    "version": "v60",
    "response": {"code": 100, "message": "..."}
  },
  "baseRates": [...],
  "taxSummaries": [...],
  "addressDetail": {...}   // Python: response.address_detail
}
```

### TaxCloud API

**Base URL**: `https://api.v3.taxcloud.com/`

**Authentication**: X-API-KEY header + Connection ID in path

**Endpoints**:
- `POST /tax/connections/{connectionId}/orders` - Create order
- `GET /tax/connections/{connectionId}/orders/{orderId}` - Get order
- `PATCH /tax/connections/{connectionId}/orders/{orderId}` - Update order
- `POST /tax/connections/{connectionId}/orders/refunds/{orderId}` - Create refund

**Response Format**: JSON with camelCase fields

```json
{
  "orderId": "my-order-1",
  "customerId": "customer-453",
  "connectionId": "25eb9b97-...",
  "lineItems": [...]
}
```

### Field Name Mapping

The SDK uses snake_case for Python conventions, but APIs use camelCase. Pydantic handles this:

```python
# API sends: {"orderId": "123", "customerId": "456"}
# Python receives:
order.order_id  # "123"
order.customer_id  # "456"

# Python sends:
request = CreateOrderRequest(order_id="123", customer_id="456")
# API receives: {"orderId": "123", "customerId": "456"}
```

---

## Troubleshooting

### Common Issues

#### 1. **Type Checking Errors with Optional HTTP Client**

**Problem**:
```python
# mypy error: Item "None" of "Optional[HTTPClient]" has no attribute "post"
return self.taxcloud_http_client.post(...)
```

**Solution**:
```python
# Add assertion after config check
self._check_taxcloud_config()  # Raises if not configured
assert self.taxcloud_http_client is not None  # Satisfies type checker
return self.taxcloud_http_client.post(...)
```

#### 2. **Pydantic Validation Errors**

**Problem**: API returns data that doesn't match model

**Debug Steps**:
1. Check `actual_api_responses` in `docs/spec.yaml` for real API response format
2. Verify field aliases match API field names
3. Check if fields should be Optional
4. Use `model_dump(by_alias=True)` when sending to API

#### 3. **Import Errors After Adding Models**

**Problem**: New models not accessible

**Solution**: Update `models/__init__.py` exports:
```python
from .responses import (
    NewModel,  # Add this
)

__all__ = [
    "NewModel",  # Add this
]
```

#### 4. **Line Length Violations (Ruff E501)**

**Problem**: Lines longer than 88 characters

**Solution**:
```python
# Use black formatter
black src/ziptax/file.py

# Or break long strings
description=(
    "This is a very long description that would exceed "
    "the 88 character limit if written on one line"
)
```

### Debugging Tips

1. **Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Inspect HTTP Requests**:
```python
# HTTP client logs all requests at DEBUG level
# Check logs for: "POST https://... with json: {...}"
```

3. **Validate Pydantic Models**:
```python
# Test model with sample data
from ziptax.models import OrderResponse
data = {...}  # Copy from API response
model = OrderResponse(**data)  # Will raise ValidationError if invalid
```

4. **Test TaxCloud Config**:
```python
client = ZipTaxClient.api_key(...)
print(f"Has TaxCloud: {client.config.has_taxcloud_config}")
print(f"Connection ID: {client.config.taxcloud_connection_id}")
```

---

## Development Workflow

### Before Committing

1. **Format Code**:
```bash
black src/ tests/
```

2. **Run Linter**:
```bash
ruff check src/ tests/
```

3. **Type Check**:
```bash
mypy src/ziptax/
```

4. **Run Tests**:
```bash
pytest --cov=src/ziptax --cov-report=term
```

5. **Check Coverage**:
```bash
coverage report --fail-under=80
```

### CI/CD Pipeline

The project uses GitHub Actions (when configured) to:
- Run tests on Python 3.8, 3.9, 3.10, 3.11
- Check code formatting (black)
- Run linter (ruff)
- Run type checker (mypy)
- Generate coverage report
- Fail if coverage < 80%

---

## Additional Resources

### Documentation Links

- **ZipTax API Docs**: https://zip-tax.com/api-documentation
- **TaxCloud API Docs**: https://docs.taxcloud.com/
- **Pydantic V2 Docs**: https://docs.pydantic.dev/latest/
- **Requests Library**: https://requests.readthedocs.io/

### Project Files

- `docs/spec.yaml` - Comprehensive API specification
- `pyproject.toml` - Project metadata and dependencies
- `README.md` - User-facing documentation
- `CHANGELOG.md` - Version history

### Code Examples

- `examples/basic_usage.py` - Basic ZipTax usage
- `examples/taxcloud_orders.py` - TaxCloud order management
- `examples/async_usage.py` - Concurrent operations
- `examples/error_handling.py` - Error handling patterns

---

## Questions & Support

For questions about the codebase or implementation details:

1. Check this CLAUDE.md file first
2. Review the `docs/spec.yaml` specification
3. Look at existing implementations for similar patterns
4. Check tests for usage examples

For API-specific questions:
- ZipTax API: support@zip.tax
- TaxCloud API: TaxCloud documentation

---

**Last Updated**: 2025-02-16
**SDK Version**: 0.2.0-beta
**Maintained By**: ZipTax Team
