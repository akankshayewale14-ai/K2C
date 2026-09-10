from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.entities import DataType, ListingStatus, OfferStatus, PickupStatus, Role, VerificationStatus


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=160)
    phone: Optional[str] = None
    role: Role = Role.CONSUMER
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("email is required")
        return normalized.lower()


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("email is required")
        return normalized.lower()


class RefreshIn(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: Role
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class MaterialOut(BaseModel):
    id: UUID
    slug: str
    name: str
    unit: str
    category: str

    class Config:
        from_attributes = True


class NeighborhoodPriceOut(BaseModel):
    area: str
    price: float
    data_type: DataType


class PriceOut(BaseModel):
    material: str
    material_name: str
    location: str
    unit: str
    low: float
    high: float
    average: float
    recommended: float
    currency: str
    source: str
    source_url: Optional[str]
    retrieved_at: datetime
    data_type: DataType
    is_live: bool
    confidence: Optional[float]
    chart_points: list[float]
    neighborhoods: list[NeighborhoodPriceOut]


class ScrapCreate(BaseModel):
    location: str = "Bengaluru"
    area: Optional[str] = "Whitefield"
    description: Optional[str] = None
    lat: Optional[float] = 12.9698
    lng: Optional[float] = 77.7500


class QuantityIn(BaseModel):
    quantity: float = Field(gt=0)
    unit: str = "kg"
    material_slug: Optional[str] = None


class ScrapOut(BaseModel):
    id: UUID
    status: ListingStatus
    material_id: Optional[UUID]
    quantity: Optional[float]
    unit: str
    location: str
    area: Optional[str]
    estimated_low: Optional[float]
    estimated_high: Optional[float]
    identification_available: Optional[bool] = None
    identification_message: Optional[str] = None

    class Config:
        from_attributes = True


class OfferOut(BaseModel):
    id: UUID
    listing_id: UUID
    buyer_type: str
    name: str
    verification: str
    distance_km: Optional[float]
    eta_label: str
    price_per_unit: float
    score: float
    status: OfferStatus
    data_type: DataType


class PickupCreate(BaseModel):
    listing_id: UUID
    scheduled_at: Optional[datetime] = None
    address: Optional[str] = None
    area: Optional[str] = None


class PickupStatusIn(BaseModel):
    status: PickupStatus


class PickupOut(BaseModel):
    id: UUID
    listing_id: UUID
    status: PickupStatus
    collector_name: Optional[str]
    vehicle_type: Optional[str]
    eta_minutes: Optional[int]
    area: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    route: Optional[list[list[float]]] = None
    data_note: str


class BulkCreate(BaseModel):
    organization_type: str
    materials: list[dict]
    pickup_location: str
    preferred_schedule: Optional[str] = None
    description: Optional[str] = None


class BulkOut(BaseModel):
    id: UUID
    status: str
    pickup_location: str
    materials: list
    estimated_low: Optional[float]
    estimated_high: Optional[float]
    data_type: DataType

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: UUID
    title: str
    body: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordResetIn(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("email is required")
        return normalized.lower()


class CollectorOut(BaseModel):
    id: UUID
    name: str
    vehicle_type: Optional[str]
    service_areas: list
    rating: Optional[float]
    completed_pickups: int
    verification: str
    lat: Optional[float]
    lng: Optional[float]


class RecyclerOut(BaseModel):
    id: UUID
    organization_name: str
    location: str
    pickup_available: bool
    materials: list[str]
    verification: str
    authority_name: Optional[str]
    verification_source: Optional[str]


class RecyclerCreate(BaseModel):
    organization_name: str
    location: str = "Bengaluru"
    lat: Optional[float] = None
    lng: Optional[float] = None
    pickup_lead_days: int = 1


class VerificationSubmit(BaseModel):
    authority_name: Optional[str] = None
    registration_number: Optional[str] = None
    verification_source: Optional[str] = None
    notes: Optional[str] = None


class BidCreate(BaseModel):
    amount: float = Field(gt=0)
    notes: Optional[str] = None
    listing_id: Optional[UUID] = None
    bulk_request_id: Optional[UUID] = None


class TraceEventOut(BaseModel):
    event_type: str
    timestamp: datetime
    location: Optional[str]
    weight: Optional[float]
    notes: Optional[str]


class TraceabilityOut(BaseModel):
    lot_id: str
    current_status: str
    initial_weight: Optional[float]
    current_weight: Optional[float]
    events: list[TraceEventOut]
    data_type: DataType = DataType.DEMO


class MapConfigOut(BaseModel):
    tile_url: str
    attribution: str
    provider_configured: bool
    note: str
    center: list[float] = [12.9716, 77.5946]
    zoom: int = 12


class AdminReviewIn(BaseModel):
    status: VerificationStatus
    notes: Optional[str] = None


class LotStatusIn(BaseModel):
    status: str
    location: Optional[str] = None
    weight: Optional[float] = None
    notes: Optional[str] = None
