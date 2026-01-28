"""Response models for the ZipTax API."""

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    rate_id: Optional[str] = Field(
        None, alias="rateId", description="Rate identifier from tax table"
    )
    jur_type: str = Field(..., alias="jurType", description="Jurisdiction type")
    jur_name: str = Field(..., alias="jurName", description="Jurisdiction name")
    jur_description: Optional[str] = Field(
        None, alias="jurDescription", description="Jurisdiction description"
    )
    jur_tax_code: Optional[str] = Field(
        None, alias="jurTaxCode", description="Tax code for jurisdiction"
    )


class V60Service(BaseModel):
    """Service taxability information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(
        ..., alias="adjustmentType", description="Service adjustment type"
    )
    taxable: Literal["Y", "N"] = Field(..., description="Taxability indicator")
    description: str = Field(..., description="Service description")


class V60Shipping(BaseModel):
    """Shipping taxability information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(
        ..., alias="adjustmentType", description="Shipping adjustment type"
    )
    taxable: Literal["Y", "N"] = Field(..., description="Taxability indicator")
    description: str = Field(..., description="Shipping description")


class V60SourcingRules(BaseModel):
    """Sourcing rules (origin/destination) taxation information."""

    model_config = ConfigDict(populate_by_name=True)

    adjustment_type: str = Field(
        ..., alias="adjustmentType", description="Sourcing rule type"
    )
    description: str = Field(..., description="Sourcing rule description")
    value: Literal["O", "D"] = Field(
        ..., description="Origin (O) or Destination (D) based"
    )


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
    summary_name: str = Field(
        ..., alias="summaryName", description="Summary description"
    )
    display_rates: List["V60DisplayRate"] = Field(
        ..., alias="displayRates", description="Display rates breakdown"
    )


class V60AddressDetail(BaseModel):
    """Address detail information for v6.0."""

    model_config = ConfigDict(populate_by_name=True)

    normalizedAddress: str = Field(..., description="Normalized address")
    incorporated: Literal["true", "false"] = Field(
        ..., description="Incorporation status"
    )
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
        None,
        alias="sourcingRules",
        description="Sourcing rules (origin/destination) taxation info",
    )
    tax_summaries: Optional[List[V60TaxSummary]] = Field(
        None, alias="taxSummaries", description="Tax rate summaries"
    )
    addressDetail: V60AddressDetail = Field(..., description="Address details")


class V60AccountMetrics(BaseModel):
    """Account metrics by API key."""

    model_config = ConfigDict(populate_by_name=True)

    core_request_count: int = Field(..., description="Number of core API requests made")
    core_request_limit: int = Field(
        ..., description="Maximum allowed core API requests"
    )
    core_usage_percent: float = Field(
        ..., description="Percentage of core request limit used"
    )
    geo_enabled: bool = Field(
        ..., description="Whether geolocation features are enabled"
    )
    geo_request_count: int = Field(
        ..., description="Number of geolocation requests made"
    )
    geo_request_limit: int = Field(
        ..., description="Maximum allowed geolocation requests"
    )
    geo_usage_percent: float = Field(
        ..., description="Percentage of geolocation request limit used"
    )
    is_active: bool = Field(..., description="Whether the account is currently active")
    message: str = Field(..., description="Account status or informational message")


class V60PostalCodeResult(BaseModel):
    """Individual tax rate result for a postal code location."""

    model_config = ConfigDict(populate_by_name=True)

    geo_postal_code: str = Field(..., alias="geoPostalCode", description="Postal code")
    geo_city: str = Field(..., alias="geoCity", description="City name")
    geo_county: str = Field(..., alias="geoCounty", description="County name")
    geo_state: str = Field(..., alias="geoState", description="State code")
    tax_sales: float = Field(..., alias="taxSales", description="Total sales tax rate")
    tax_use: float = Field(..., alias="taxUse", description="Total use tax rate")
    txb_service: Literal["Y", "N"] = Field(
        ..., alias="txbService", description="Service taxability indicator"
    )
    txb_freight: Literal["Y", "N"] = Field(
        ..., alias="txbFreight", description="Freight taxability indicator"
    )
    state_sales_tax: float = Field(
        ..., alias="stateSalesTax", description="State sales tax rate"
    )
    state_use_tax: float = Field(
        ..., alias="stateUseTax", description="State use tax rate"
    )
    city_sales_tax: float = Field(
        ..., alias="citySalesTax", description="City sales tax rate"
    )
    city_use_tax: float = Field(
        ..., alias="cityUseTax", description="City use tax rate"
    )
    city_tax_code: str = Field(..., alias="cityTaxCode", description="City tax code")
    county_sales_tax: float = Field(
        ..., alias="countySalesTax", description="County sales tax rate"
    )
    county_use_tax: float = Field(
        ..., alias="countyUseTax", description="County use tax rate"
    )
    county_tax_code: str = Field(
        ..., alias="countyTaxCode", description="County tax code"
    )
    district_sales_tax: float = Field(
        ..., alias="districtSalesTax", description="Total district sales tax rate"
    )
    district_use_tax: float = Field(
        ..., alias="districtUseTax", description="Total district use tax rate"
    )
    district1_code: str = Field(
        ..., alias="district1Code", description="District 1 tax code"
    )
    district1_sales_tax: float = Field(
        ..., alias="district1SalesTax", description="District 1 sales tax rate"
    )
    district1_use_tax: float = Field(
        ..., alias="district1UseTax", description="District 1 use tax rate"
    )
    district2_code: str = Field(
        ..., alias="district2Code", description="District 2 tax code"
    )
    district2_sales_tax: float = Field(
        ..., alias="district2SalesTax", description="District 2 sales tax rate"
    )
    district2_use_tax: float = Field(
        ..., alias="district2UseTax", description="District 2 use tax rate"
    )
    district3_code: str = Field(
        ..., alias="district3Code", description="District 3 tax code"
    )
    district3_sales_tax: float = Field(
        ..., alias="district3SalesTax", description="District 3 sales tax rate"
    )
    district3_use_tax: float = Field(
        ..., alias="district3UseTax", description="District 3 use tax rate"
    )
    district4_code: str = Field(
        ..., alias="district4Code", description="District 4 tax code"
    )
    district4_sales_tax: float = Field(
        ..., alias="district4SalesTax", description="District 4 sales tax rate"
    )
    district4_use_tax: float = Field(
        ..., alias="district4UseTax", description="District 4 use tax rate"
    )
    district5_code: str = Field(
        ..., alias="district5Code", description="District 5 tax code"
    )
    district5_sales_tax: float = Field(
        ..., alias="district5SalesTax", description="District 5 sales tax rate"
    )
    district5_use_tax: float = Field(
        ..., alias="district5UseTax", description="District 5 use tax rate"
    )
    origin_destination: Literal["O", "D"] = Field(
        ..., alias="originDestination", description="Origin/destination indicator"
    )


class V60PostalCodeAddressDetail(BaseModel):
    """Address details for postal code lookup."""

    model_config = ConfigDict(populate_by_name=True)

    normalized_address: str = Field(
        ...,
        alias="normalizedAddress",
        description="Normalized address (not available for postal code lookups)",
    )
    incorporated: str = Field(
        ...,
        description="Incorporation status (not available for postal code lookups)",
    )
    geo_lat: float = Field(
        ..., alias="geoLat", description="Latitude (0 for postal code lookups)"
    )
    geo_lng: float = Field(
        ..., alias="geoLng", description="Longitude (0 for postal code lookups)"
    )


class V60PostalCodeResponse(BaseModel):
    """Response for postal code lookup.

    Returns flat structure with multiple results.
    """

    model_config = ConfigDict(populate_by_name=True)

    version: str = Field(..., description="API version")
    r_code: int = Field(..., alias="rCode", description="Response code (100=success)")
    results: List[V60PostalCodeResult] = Field(
        ..., description="Array of tax rate results for the postal code"
    )
    address_detail: V60PostalCodeAddressDetail = Field(
        ..., alias="addressDetail", description="Address details for postal code lookup"
    )
