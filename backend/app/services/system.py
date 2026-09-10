from uuid import UUID

from sqlalchemy.orm import Session

from app.models.entities import AuditLog, Notification


def audit(db: Session, action: str, entity: str, entity_id: str | None, actor_id: UUID | None, meta: dict | None = None):
    db.add(AuditLog(actor_id=actor_id, action=action, entity=entity, entity_id=entity_id, metadata_json=meta))


def notify(db: Session, user_id: UUID, title: str, body: str):
    db.add(Notification(user_id=user_id, title=title, body=body))
