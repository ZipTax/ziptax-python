"""Response models for the ZipTax API."""

from typing import List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class JurisdictionType(str, Enum):
    """Jurisdiction type enumeration."""

    US_STATE_SALES_TAX = "US_STATE_SALES_TAX"
    US_STATE_USE_TAX = "US_STATE_USE_TAX"
    US_COUNTY_SALES_TAX = "US_COUNTY_SALES_TAX"
    US_COUNTY_USE_TAX = "US_COUNTY_USE_TAX"
    US_CITY_SALES_TAX = "US_CITY_SALES_TAX"
    US_CITY_USE_TAX = "US_CITY_USE_TAX"
    US_DISTRICT_SALES_TAX = "US_DISTRICT_SALES_TAX"
    US_DISTRICT_USE_TAX = "US_DISTRICT_USE_TAX"


class JurisdictionName(str, Enum):
    """Jurisdiction name enumeration."""

    US_STATE = "US_STATE"
    US_COUNTY = "US_COUNTY"
    US_CITY = "US_CITY"
    US_DISTRICT = "US_DISTRICT"


class TaxType(str, Enum):
    """Tax type enumeration."""

    SALES_TAX = "SALES_TAX"
    USE_TAX = "USE_TAX"


class V60ResponseInfo(BaseModel):
    """Response information nested in metadata."""

    model_config = ConfigDict(populate_by_name=True)

    code: int = Field(..., description="Response code (100=success)")
    name: str = Field(..., description="Response code name")
    message: str = Field(..., description="Response message")
    definition: str = Field(..., description="Schema definition URL")


class V60Metadata(BaseModel):
    """Metadata for v6.0 response."""

    model_config = ConfigDict(populate_by_name=True)

    version: str = Field(..., description="API version")
    response: V60ResponseInfo = Field(..., description="Response information")


class V60BaseRate(BaseModel):
    """Base tax rate for a specific jurisdiction."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    rate: float = Field(..., description="Tax rate")
    rate_id: Optional[str] = Field(None, alias="rateId", description="Rate identifier from tax table")
    jur_type: str = Field(..., alias="jurType", description="Jurisdiction type")
    jur_name: str = Field(..., alias="jurName", description="Jurisdiction name")
    jur_description: Optional[str] = Field(None, alias="jurDescription", description="Jurisdiction description")
    jur_tax_code: Optional[str] = Field(None, alias="jurTaxCode", description="Tax code for jurisdiction")


class V60Service(BaseModel):
    """Service taxability information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(..., alias="adjustmentType", description="Service adjustment type")
    taxable: Literal["Y", "N"] = Field(..., description="Taxability indicator")
    description: str = Field(..., description="Service description")


class V60Shipping(BaseModel):
    """Shipping taxability information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(..., alias="adjustmentType", description="Shipping adjustment type")
    taxable: Literal["Y", "N"] = Field(..., description="Taxability indicator")
    description: str = Field(..., description="Shipping description")


class V60SourcingRules(BaseModel):
    """Sourcing rules (origin/destination) taxation information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(..., alias="adjustmentType", description="Sourcing rule type")
    description: str = Field(..., description="Sourcing rule description")
    value: Literal["O", "D"] = Field(..., description="Origin (O) or Destination (D) based")


class V60DisplayRate(BaseModel):
    """Display rate information."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="Display rate name")
    rate: float = Field(..., description="Display rate value")


class V60TaxSummary(BaseModel):
    """Tax rate summary."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    rate: float = Field(..., description="Summary tax rate")
    tax_type: str = Field(..., alias="taxType", description="Tax type")
    summary_name: str = Field(..., alias="summaryName", description="Summary description")
    display_rates: List["V60DisplayRate"] = Field(..., alias="displayRates", description="Display rates breakdown")


class V60AddressDetail(BaseModel):
    """Address detail information for v6.0."""

    model_config = ConfigDict(populate_by_name=True)

    normalizedAddress: str = Field(..., description="Normalized address")
    incorporated: Literal["true", "false"] = Field(..., description="Incorporation status")
    geoLat: float = Field(..., description="Geocoded latitude")
    geoLng: float = Field(..., description="Geocoded longitude")


class V60Response(BaseModel):
    """Response for v6.0 API - structured format with separate components."""

    model_config = ConfigDict(populate_by_name=True)

    metadata: V60Metadata = Field(..., description="Response metadata")
    base_rates: Optional[List[V60BaseRate]] = Field(
        None, alias="baseRates", description="Base tax rates by jurisdiction"
    )
    service: V60Service = Field(..., description="Service taxability information")
    shipping: V60Shipping = Field(..., description="Shipping taxability information")
    sourcing_rules: Optional[V60SourcingRules] = Field(
        None, alias="sourcingRules", description="Sourcing rules (origin/destination) taxation info"
    )
    tax_summaries: Optional[List[V60TaxSummary]] = Field(
        None, alias="taxSummaries", description="Tax rate summaries"
    )
    addressDetail: V60AddressDetail = Field(..., description="Address details")


class V60AccountMetrics(BaseModel):
    """Account metrics by API key."""

    model_config = ConfigDict(populate_by_name=True)

    core_request_count: int = Field(..., description="Number of core API requests made")
    core_request_limit: int = Field(..., description="Maximum allowed core API requests")
    core_usage_percent: float = Field(
        ..., description="Percentage of core request limit used"
    )
    geo_enabled: bool = Field(..., description="Whether geolocation features are enabled")
    geo_request_count: int = Field(..., description="Number of geolocation requests made")
    geo_request_limit: int = Field(..., description="Maximum allowed geolocation requests")
    geo_usage_percent: float = Field(
        ..., description="Percentage of geolocation request limit used"
    )
    is_active: bool = Field(..., description="Whether the account is currently active")
    message: str = Field(..., description="Account status or informational message")
