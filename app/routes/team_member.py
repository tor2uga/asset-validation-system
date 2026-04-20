from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core_templates import templates
from app import models
from app.database import get_db
from app.services.auth_service import get_user_with_role_check
from app.services.validation_service import get_active_cycle

router = APIRouter()


@router.get("/ui/team-member/{user_id}", response_class=HTMLResponse)
def team_member_dashboard(user_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user = get_user_with_role_check(user_id, ["team_member"], db)
    except Exception as e:
        return HTMLResponse(str(e), status_code=403)

    if not user.department_id:
        return HTMLResponse("No department assigned", status_code=400)

    active_cycle = get_active_cycle(db)

    notifications = db.query(models.Notification).filter(
        models.Notification.department_id == user.department_id,
        models.Notification.is_read == False
    ).all()

    assets = db.query(models.Asset).filter(
        models.Asset.department_id == user.department_id
    ).order_by(models.Asset.id.desc()).all()

    departments = db.query(models.Department).order_by(models.Department.name).all()

    validations = db.query(models.AssetValidation).filter(
        models.AssetValidation.user_id == user_id
    ).all()

    validated_asset_ids = {
        v.asset_id for v in validations
        if v.asset_id is not None
        and v.cycle_id == (active_cycle.id if active_cycle else None)
        and v.approval_stage not in ["returned_to_team"]
    }

    returned_validation_map = {
        v.asset_id: v for v in validations
        if v.asset_id is not None
        and v.cycle_id == (active_cycle.id if active_cycle else None)
        and v.approval_stage == "returned_to_team"
    }

    return templates.TemplateResponse(
        "team_member_dashboard.html",
        {
            "request": request,
            "user": user,
            "assets": assets,
            "departments": departments,
            "validated_asset_ids": validated_asset_ids,
            "returned_validation_map": returned_validation_map,
            "notifications": notifications,
            "active_cycle": active_cycle
        }
    )