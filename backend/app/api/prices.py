from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.db.session import get_db
from app.models.entities import Material
from app.providers.maps.factory import get_map_provider
from app.schemas.main import MapConfigOut, MaterialOut, PriceOut
from app.services.pricing import price_payload

router = APIRouter(prefix="/api", tags=["prices"])


@router.get("/materials", response_model=list[MaterialOut])
def materials(db: Session = Depends(get_db)):
    return db.query(Material).order_by(Material.name).all()


@router.get("/prices", response_model=list[PriceOut])
def prices(
    material: str | None = Query(default=None),
    location: str = Query(default="Bengaluru"),
    date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    slugs = [material] if material else [m.slug for m in db.query(Material).all()]
    out = []
    for slug in slugs:
        payload = price_payload(db, slug, location, date)
        if payload:
            out.append(payload)
    return out


@router.get("/prices/{material}", response_model=PriceOut)
def price_one(
    material: str,
    location: str = Query(default="Bengaluru"),
    date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    payload = price_payload(db, material, location, date)
    if not payload:
        raise not_found("Price data currently unavailable for this material and location.")
    return payload


@router.get("/map/config", response_model=MapConfigOut)
def map_config():
    cfg = get_map_provider().public_config()
    return MapConfigOut(
        tile_url=cfg.tile_url,
        attribution=cfg.attribution,
        provider_configured=cfg.provider_configured,
        note=cfg.note,
    )
