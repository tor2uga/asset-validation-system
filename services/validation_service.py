from sqlalchemy.orm import Session
from app import models


def get_active_cycle(db: Session):
    return db.query(models.ValidationCycle).filter(
        models.ValidationCycle.status == "active"
    ).order_by(models.ValidationCycle.start_date.desc()).first()


def submit_team_member_validation(
    user_id: int,
    asset_id: int,
    status: str,
    comment: str,
    new_department_id: str | None,
    db: Session,
):
    user = db.query(models.ADUser).filter(models.ADUser.id == user_id).first()
    if not user:
        raise Exception("User not found")

    if user.role != "team_member":
        raise Exception("Access denied")

    if not user.department_id:
        raise Exception("No department assigned")

    active_cycle = get_active_cycle(db)
    if not active_cycle:
        raise Exception("No active validation cycle found")

    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise Exception("Asset not found")

    if asset.department_id != user.department_id:
        raise Exception("You can only validate assets in your department")

    target_department = int(new_department_id) if new_department_id else None

    if status == "reassign" and not target_department:
        raise Exception("Please choose a department to reassign to.")

    existing = db.query(models.AssetValidation).filter(
        models.AssetValidation.user_id == user_id,
        models.AssetValidation.asset_id == asset_id,
        models.AssetValidation.cycle_id == active_cycle.id
    ).first()

    # 🔁 Handle returned validation (resubmission)
    if existing and existing.approval_stage == "returned_to_team":
        existing.status = status
        existing.comment = comment
        existing.department_id = user.department_id
        existing.new_department_id = target_department
        existing.approval_stage = "pending_lead_review"
        existing.reassignment_status = "pending_lead" if status == "reassign" else None
        db.commit()
        return existing

    # ⛔ Already submitted
    if existing:
        return existing

    # ✅ Create new validation
    validation = models.AssetValidation(
        cycle_id=active_cycle.id,
        asset_id=asset_id,
        user_id=user_id,
        department_id=user.department_id,
        status=status,
        comment=comment,
        new_department_id=target_department,
        approval_stage="pending_lead_review",
        reassignment_status="pending_lead" if status == "reassign" else None
    )

    db.add(validation)
    db.commit()
    db.refresh(validation)

    return validation