from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base

JSONType = JSON().with_variant(JSONB, "postgresql")


class Role(str, enum.Enum):
    CONSUMER = "CONSUMER"
    COLLECTOR = "COLLECTOR"
    RECYCLER = "RECYCLER"
    BUSINESS = "BUSINESS"
    ADMIN = "ADMIN"


class DataType(str, enum.Enum):
    DEMO = "DEMO"
    LIVE = "LIVE"
    HISTORICAL = "HISTORICAL"


class ListingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    MATCHED = "MATCHED"
    PICKUP_SCHEDULED = "PICKUP_SCHEDULED"
    COLLECTED = "COLLECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUSPENDED = "SUSPENDED"


class PickupStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    CONFIRMED = "CONFIRMED"
    ON_THE_WAY = "ON_THE_WAY"
    ARRIVED = "ARRIVED"
    COLLECTED = "COLLECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class OfferStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False), default=Role.CONSUMER, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    consumer_profile = relationship("ConsumerProfile", back_populates="user", uselist=False)
    collector_profile = relationship("CollectorProfile", back_populates="user", uselist=False)
    recycler_profile = relationship("RecyclerProfile", back_populates="user", uselist=False)
    business_profile = relationship("BusinessProfile", back_populates="user", uselist=False)


class ConsumerProfile(Base):
    __tablename__ = "consumer_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    area: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user = relationship("User", back_populates="consumer_profile")


class CollectorProfile(Base, TimestampMixin):
    __tablename__ = "collector_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    service_areas: Mapped[list] = mapped_column(JSONType, default=list)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accepted_materials: Mapped[list] = mapped_column(JSONType, default=list)
    payout_rate: Mapped[float] = mapped_column(Float, default=0.92)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completed_pickups: Mapped[int] = mapped_column(Integer, default=0)
    user = relationship("User", back_populates="collector_profile")
    verification = relationship("VerificationRecord", back_populates="collector", uselist=False)


class RecyclerProfile(Base, TimestampMixin):
    __tablename__ = "recycler_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    organization_name: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(200))
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pickup_lead_days: Mapped[int] = mapped_column(Integer, default=1)
    pickup_available: Mapped[bool] = mapped_column(Boolean, default=True)
    authority_name: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    verification_source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    user = relationship("User", back_populates="recycler_profile")
    verification = relationship("VerificationRecord", back_populates="recycler", uselist=False)
    materials = relationship("RecyclerMaterial", back_populates="recycler")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    organization_name: Mapped[str] = mapped_column(String(200))
    organization_type: Mapped[str] = mapped_column(String(80))
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user = relationship("User", back_populates="business_profile")


class VerificationRecord(Base, TimestampMixin):
    __tablename__ = "verification_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("collector_profiles.id"), nullable=True)
    recycler_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("recycler_profiles.id"), nullable=True)
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, native_enum=False), default=VerificationStatus.PENDING
    )
    authority_name: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    verification_source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    verification_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collector = relationship("CollectorProfile", back_populates="verification")
    recycler = relationship("RecyclerProfile", back_populates="verification")


class Material(Base):
    __tablename__ = "materials"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    category: Mapped[str] = mapped_column(String(40))


class PriceSource(Base):
    __tablename__ = "price_sources"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    provider_key: Mapped[str] = mapped_column(String(80))
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False)


class MaterialPrice(Base, TimestampMixin):
    __tablename__ = "material_prices"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id"), index=True)
    location: Mapped[str] = mapped_column(String(80), default="Satara")
    neighborhood: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    low: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    average: Mapped[float] = mapped_column(Float)
    recommended: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    source: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_type: Mapped[DataType] = mapped_column(Enum(DataType, native_enum=False), default=DataType.DEMO)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chart_points: Mapped[list] = mapped_column(JSONType, default=list)
    material = relationship("Material")


class ScrapListing(Base, TimestampMixin):
    __tablename__ = "scrap_listings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("materials.id"), nullable=True)
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    location: Mapped[str] = mapped_column(String(80), default="Satara")
    area: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, native_enum=False), default=ListingStatus.DRAFT, index=True
    )
    estimated_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    images = relationship("ScrapImage", back_populates="listing", cascade="all, delete-orphan")
    identification = relationship("MaterialIdentification", back_populates="listing", uselist=False)
    offers = relationship("Offer", back_populates="listing")


class ScrapImage(Base, TimestampMixin):
    __tablename__ = "scrap_images"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"), index=True)
    storage_key: Mapped[str] = mapped_column(String(400))
    content_type: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer)
    listing = relationship("ScrapListing", back_populates="images")


class MaterialIdentification(Base, TimestampMixin):
    __tablename__ = "material_identifications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"), unique=True)
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("materials.id"), nullable=True)
    provider: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    condition: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, default=False)
    listing = relationship("ScrapListing", back_populates="identification")


class Offer(Base, TimestampMixin):
    __tablename__ = "offers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"), index=True)
    collector_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("collector_profiles.id"), nullable=True)
    recycler_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("recycler_profiles.id"), nullable=True)
    price_per_unit: Mapped[float] = mapped_column(Float)
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eta_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[OfferStatus] = mapped_column(Enum(OfferStatus, native_enum=False), default=OfferStatus.ACTIVE)
    data_type: Mapped[DataType] = mapped_column(Enum(DataType, native_enum=False), default=DataType.DEMO)
    listing = relationship("ScrapListing", back_populates="offers")
    collector = relationship("CollectorProfile")
    recycler = relationship("RecyclerProfile")


class PickupRequest(Base, TimestampMixin):
    __tablename__ = "pickup_requests"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"), index=True)
    consumer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PickupStatus] = mapped_column(
        Enum(PickupStatus, native_enum=False), default=PickupStatus.REQUESTED, index=True
    )
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    area: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assignment = relationship("PickupAssignment", back_populates="pickup", uselist=False)
    history = relationship("PickupStatusHistory", back_populates="pickup")


class PickupAssignment(Base, TimestampMixin):
    __tablename__ = "pickup_assignments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pickup_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pickup_requests.id"), unique=True)
    collector_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collector_profiles.id"))
    eta_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    pickup = relationship("PickupRequest", back_populates="assignment")
    collector = relationship("CollectorProfile")


class PickupRoute(Base, TimestampMixin):
    __tablename__ = "pickup_routes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collector_profiles.id"))
    pickup_ids: Mapped[list] = mapped_column(JSONType, default=list)
    coordinates: Mapped[list] = mapped_column(JSONType, default=list)
    total_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_earnings: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(40), default="haversine")
    data_type: Mapped[DataType] = mapped_column(Enum(DataType, native_enum=False), default=DataType.DEMO)


class PickupStatusHistory(Base):
    __tablename__ = "pickup_status_history"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pickup_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pickup_requests.id"), index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    to_status: Mapped[str] = mapped_column(String(40))
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    pickup = relationship("PickupRequest", back_populates="history")


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"))
    payer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    payee_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    status: Mapped[str] = mapped_column(String(40), default="RECORDED")


class RecyclingLot(Base, TimestampMixin):
    __tablename__ = "recycling_lots"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    scrap_listing_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrap_listings.id"))
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("materials.id"), nullable=True)
    initial_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_status: Mapped[str] = mapped_column(String(80), default="Listed")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    events = relationship("TraceabilityEvent", back_populates="lot", order_by="TraceabilityEvent.timestamp")


class TraceabilityEvent(Base):
    __tablename__ = "traceability_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recycling_lots.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lot = relationship("RecyclingLot", back_populates="events")


class RecyclerMaterial(Base):
    __tablename__ = "recycler_materials"
    __table_args__ = (UniqueConstraint("recycler_id", "material_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recycler_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recycler_profiles.id"))
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id"))
    price_per_unit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_quantity: Mapped[float] = mapped_column(Float, default=1)
    recycler = relationship("RecyclerProfile", back_populates="materials")
    material = relationship("Material")


class RecyclerBid(Base, TimestampMixin):
    __tablename__ = "recycler_bids"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recycler_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recycler_profiles.id"))
    bulk_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("business_bulk_requests.id"), nullable=True)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("scrap_listings.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class BusinessBulkRequest(Base, TimestampMixin):
    __tablename__ = "business_bulk_requests"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    organization_type: Mapped[str] = mapped_column(String(80))
    materials: Mapped[list] = mapped_column(JSONType, default=list)
    quantity_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pickup_location: Mapped[str] = mapped_column(String(200))
    preferred_schedule: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="OPEN")
    estimated_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    data_type: Mapped[DataType] = mapped_column(Enum(DataType, native_enum=False), default=DataType.DEMO)
    bids = relationship("RecyclerBid", backref="bulk_request")


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
