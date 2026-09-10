from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.errors import not_found
from app.db.session import get_db
from app.models.entities import AuditLog, Role, User, VerificationRecord
from app.schemas.main import AdminReviewIn
from app.services.system import audit

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def users(_: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.created_at.desc()).all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "is_active": u.is_active} for u in rows]


@router.get("/verifications")
def verifications(_: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(VerificationRecord).order_by(VerificationRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "status": r.status,
            "authority_name": r.authority_name,
            "registration_number": r.registration_number,
            "verification_source": r.verification_source,
            "collector_id": r.collector_id,
            "recycler_id": r.recycler_id,
        }
        for r in rows
    ]


@router.post("/verifications/{record_id}/review")
def review(
    record_id: UUID,
    body: AdminReviewIn,
    admin: User = Depends(require_roles(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    record = db.get(VerificationRecord, record_id)
    if not record:
        raise not_found("Verification record not found")
    record.status = body.status
    record.notes = body.notes
    audit(db, "verification.review", "verification_record", str(record.id), admin.id, {"status": body.status.value})
    db.commit()
    return {"id": record.id, "status": record.status}


@router.get("/audit")
def audit_logs(_: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
    return [
        {
            "id": r.id,
            "actor_id": r.actor_id,
            "action": r.action,
            "entity": r.entity,
            "entity_id": r.entity_id,
            "created_at": r.created_at,
        }
        for r in rows
    ]
