from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import ListingStatus, Material, Role, ScrapListing, User
from app.schemas.main import QuantityIn, ScrapCreate, ScrapOut
from app.services.scrap import create_listing, get_owned, identify, save_images, set_quantity
from app.services.serializers import scrap_out

router = APIRouter(prefix="/api/scrap", tags=["scrap"])


@router.post("", response_model=ScrapOut)
def create_scrap(body: ScrapCreate, user: User = Depends(require_roles(Role.CONSUMER, Role.BUSINESS)), db: Session = Depends(get_db)):
    listing = create_listing(db, user.id, body)
    db.commit()
    db.refresh(listing)
    return scrap_out(listing)


@router.get("", response_model=list[ScrapOut])
def list_scrap(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(ScrapListing).filter(ScrapListing.user_id == user.id).order_by(ScrapListing.created_at.desc()).all()
    return [scrap_out(r) for r in rows]


@router.get("/marketplace")
def marketplace_requests(user: User = Depends(require_roles(Role.COLLECTOR, Role.ADMIN)), db: Session = Depends(get_db)):
    rows = (
        db.query(ScrapListing)
        .filter(ScrapListing.status.in_((ListingStatus.ACTIVE, ListingStatus.DRAFT, ListingStatus.MATCHED)))
        .order_by(ScrapListing.created_at.desc())
        .all()
    )
    payload = []
    for listing in rows:
        seller = db.get(User, listing.user_id)
        if not seller:
            continue
        material = db.get(Material, listing.material_id) if listing.material_id else None
        payload.append(
            {
                "id": str(listing.id),
                "seller_name": seller.full_name,
                "seller_type": "Business seller" if seller.role == Role.BUSINESS else "Individual seller",
                "area": listing.area or listing.location or "Satara",
                "location": listing.location,
                "quantity": listing.quantity,
                "unit": listing.unit,
                "material_name": material.name if material else "Scrap mix",
                "status": listing.status.value,
                "description": listing.description or "Seller is requesting a pickup.",
                "estimated_low": listing.estimated_low,
                "estimated_high": listing.estimated_high,
                "created_at": listing.created_at.isoformat() if listing.created_at else None,
                "photo_count": len(listing.images),
            }
        )
    return payload


@router.get("/{listing_id}", response_model=ScrapOut)
def get_scrap(listing_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return scrap_out(get_owned(db, listing_id, user.id))


@router.post("/{listing_id}/images")
def upload_images(
    listing_id: UUID,
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = get_owned(db, listing_id, user.id)
    saved = save_images(db, listing, files, user.id)
    db.commit()
    return {"uploaded": len(saved)}


@router.post("/{listing_id}/identify", response_model=ScrapOut)
def identify_material(listing_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned(db, listing_id, user.id)
    result = identify(db, listing, user.id)
    db.commit()
    db.refresh(listing)
    payload = scrap_out(listing)
    payload["identification_available"] = result.available
    payload["identification_message"] = result.message
    return payload


@router.post("/{listing_id}/quantity", response_model=ScrapOut)
def quantity(listing_id: UUID, body: QuantityIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = get_owned(db, listing_id, user.id)
    set_quantity(db, listing, body.quantity, body.unit, body.material_slug, user.id)
    db.commit()
    db.refresh(listing)
    return scrap_out(listing)
