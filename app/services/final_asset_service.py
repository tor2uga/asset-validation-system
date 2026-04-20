from sqlalchemy.orm import Session
from app import models


def get_final_assets_for_department_user(user, db: Session):
    if not user:
        raise Exception("User not found")

    if user.role not in ["team_member", "team_lead"]:
        raise Exception("Access denied")

    if not user.department_id:
        raise Exception("No department assigned")

    assets = db.query(models.Asset).filter(
        models.Asset.department_id == user.department_id
    ).order_by(models.Asset.id.desc()).all()

    approved_validations = db.query(models.AssetValidation).filter(
        models.AssetValidation.department_id == user.department_id,
        models.AssetValidation.approval_stage == "approved"
    ).all()

    approved_asset_ids = {
        v.asset_id for v in approved_validations
        if v.asset_id is not None
    }

    final_assets = [a for a in assets if a.id in approved_asset_ids]
    return final_assets


def get_final_assets_for_admin(role: str, department_id: int | None, db: Session):
    if role not in ["compliance", "infosec"]:
        raise Exception("Access denied")

    approved_validations_query = db.query(models.AssetValidation).filter(
        models.AssetValidation.approval_stage == "approved"
    )

    if department_id:
        approved_validations_query = approved_validations_query.filter(
            models.AssetValidation.department_id == department_id
        )

    approved_validations = approved_validations_query.all()
    approved_asset_ids = {
        v.asset_id for v in approved_validations
        if v.asset_id is not None
    }

    assets_query = db.query(models.Asset)
    if department_id:
        assets_query = assets_query.filter(
            models.Asset.department_id == department_id
        )

    assets = assets_query.order_by(models.Asset.id.desc()).all()
    final_assets = [a for a in assets if a.id in approved_asset_ids]

    return final_assets


def get_department_map(db: Session):
    return {
        d.id: d.name for d in db.query(models.Department).all()
    }


def get_department_by_id(department_id: int, db: Session):
    return db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()