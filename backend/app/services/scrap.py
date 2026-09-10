from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload

from app.core.errors import bad_request, forbidden, not_found
from app.core.config import get_settings
from app.models.entities import (
    ListingStatus,
    Material,
    MaterialIdentification,
    ScrapImage,
    ScrapListing,
)
from app.providers.ai.factory import get_identification_provider
from app.providers.storage.factory import get_storage
from app.services.pricing import price_payload
from app.services.system import audit

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILES = 5


def create_listing(db: Session, user_id: UUID, data) -> ScrapListing:
    listing = ScrapListing(
        user_id=user_id,
        location=data.location,
        area=data.area,
        description=data.description,
        lat=data.lat,
        lng=data.lng,
        status=ListingStatus.DRAFT,
    )
    db.add(listing)
    db.flush()
    audit(db, "scrap.create", "scrap_listing", str(listing.id), user_id)
    return listing


def get_owned(db: Session, listing_id: UUID, user_id: UUID) -> ScrapListing:
    listing = (
        db.query(ScrapListing)
        .options(joinedload(ScrapListing.identification), joinedload(ScrapListing.images))
        .filter(ScrapListing.id == listing_id)
        .first()
    )
    if not listing:
        raise not_found("Listing not found")
    if listing.user_id != user_id:
        raise forbidden("You do not own this listing")
    return listing


def save_images(db: Session, listing: ScrapListing, files: list, user_id: UUID):
    settings = get_settings()
    if len(listing.images) + len(files) > MAX_FILES:
        raise bad_request(f"Maximum {MAX_FILES} images per listing")
    storage = get_storage()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    saved = []
    for upload in files:
        content_type = upload.content_type or ""
        name = (upload.filename or "upload").lower()
        ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
        if content_type not in ALLOWED_TYPES or ext not in ALLOWED_EXT:
            raise bad_request("Only JPEG, PNG, and WebP images are allowed")
        data = upload.file.read()
        if len(data) > max_bytes:
            raise bad_request(f"Each image must be under {settings.MAX_UPLOAD_MB} MB")
        key = f"{listing.id}/{uuid4()}{ext}"
        storage.save(key, data, content_type)
        image = ScrapImage(listing_id=listing.id, storage_key=key, content_type=content_type, size_bytes=len(data))
        db.add(image)
        saved.append(image)
    audit(db, "scrap.upload", "scrap_listing", str(listing.id), user_id, {"count": len(saved)})
    return saved


def identify(db: Session, listing: ScrapListing, user_id: UUID):
    provider = get_identification_provider()
    first = listing.images[0] if listing.images else None
    result = provider.identify(first.storage_key if first else "none", first.content_type if first else "application/octet-stream")
    material = None
    if result.material_slug:
        material = db.query(Material).filter(Material.slug == result.material_slug).first()
        if material:
            listing.material_id = material.id
    ident = listing.identification
    if not ident:
        ident = MaterialIdentification(listing_id=listing.id)
        db.add(ident)
        listing.identification = ident
    ident.material_id = material.id if material else None
    ident.provider = result.provider
    ident.confidence = result.confidence
    ident.condition = result.condition
    ident.raw_metadata = result.metadata
    ident.available = result.available
    audit(db, "scrap.identify", "scrap_listing", str(listing.id), user_id, {"available": result.available})
    return result


def set_quantity(db: Session, listing: ScrapListing, quantity: float, unit: str, material_slug: str | None, user_id: UUID):
    if material_slug:
        material = db.query(Material).filter(Material.slug == material_slug).first()
        if not material:
            raise bad_request("Unknown material")
        listing.material_id = material.id
    listing.quantity = quantity
    listing.unit = unit
    if listing.material_id:
        material = db.get(Material, listing.material_id)
        payload = price_payload(db, material.slug, listing.location) if material else None
        if payload:
            listing.estimated_low = round(payload["low"] * quantity, 2)
            listing.estimated_high = round(payload["high"] * quantity, 2)
        else:
            listing.estimated_low = None
            listing.estimated_high = None
    listing.status = ListingStatus.ACTIVE
    audit(db, "scrap.quantity", "scrap_listing", str(listing.id), user_id)
    return listing
