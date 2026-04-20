from datetime import datetime
from sqlalchemy.orm import Session

from app import models
from app.services.validation_service import get_active_cycle


def submit_new_asset_discovery(
    user_id: int,
    sn: str,
    condition: str,
    asset_type: str,
    asset_serial_no: str,
    host_application_server_name: str,
    description: str,
    application_url_ip: str,
    privilege: str,
    criticality: str,
    assigned_to_custodian_owner_business_line: str,
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

    discovery = models.NewAssetDiscovery(
        cycle_id=active_cycle.id,
        department_id=user.department_id,
        submitted_by=user_id,
        sn=sn or None,
        condition=condition or None,
        asset_type=asset_type or None,
        asset_serial_no=asset_serial_no or None,
        host_application_server_name=host_application_server_name or None,
        description=description or None,
        application_url_ip=application_url_ip or None,
        privilege=privilege or None,
        criticality=criticality or None,
        assigned_to_custodian_owner_business_line=assigned_to_custodian_owner_business_line or None,
        status="new_asset_pending_lead_review"
    )

    db.add(discovery)
    db.commit()
    db.refresh(discovery)

    audit = models.AuditLog(
        user_id=user_id,
        action="ui_create_new_asset_discovery",
        entity_type="new_asset_discovery",
        entity_id=discovery.id,
        details=f"department_id={user.department_id}; cycle_id={active_cycle.id}"
    )
    db.add(audit)
    db.commit()

    return discovery


def approve_discovery_by_team_lead(
    discovery_id: int,
    user_id: int,
    db: Session,
):
    discovery = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.id == discovery_id
    ).first()

    if not discovery:
        raise Exception("Discovery not found")

    if discovery.status != "new_asset_pending_lead_review":
        raise Exception("This discovery has already been processed.")

    discovery.status = "new_asset_pending_attestation"

    audit = models.AuditLog(
        user_id=user_id,
        action="ui_team_lead_approve_discovery",
        entity_type="new_asset_discovery",
        entity_id=discovery.id,
        details="Approved by Team Lead"
    )
    db.add(audit)
    db.commit()

    return discovery


def reject_discovery_by_team_lead(
    discovery_id: int,
    user_id: int,
    reason: str,
    db: Session,
):
    discovery = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.id == discovery_id
    ).first()

    if not discovery:
        raise Exception("Discovery not found")

    if discovery.status != "new_asset_pending_lead_review":
        raise Exception("This discovery has already been processed.")

    discovery.status = "returned_to_team"

    audit = models.AuditLog(
        user_id=user_id,
        action="ui_team_lead_reject_discovery",
        entity_type="new_asset_discovery",
        entity_id=discovery.id,
        details=reason or "No reason provided"
    )
    db.add(audit)
    db.commit()

    return discovery


def approve_discovery_by_infosec(
    discovery_id: int,
    user_id: int,
    db: Session,
):
    discovery = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.id == discovery_id
    ).first()

    if not discovery:
        raise Exception("Discovery not found")

    if discovery.status not in ["awaiting_infosec_attestation", "new_asset_pending_infosec"]:
        raise Exception("Discovery is not awaiting Infosec approval.")

    new_asset = models.Asset(
        serial_no=discovery.sn or discovery.asset_serial_no or f"new-{discovery.id}",
        asset_serial_no=discovery.asset_serial_no,
        asset_type=discovery.asset_type,
        host_name=discovery.host_application_server_name,
        description=discovery.description,
        ip_address=discovery.application_url_ip,
        privilege=discovery.privilege,
        criticality=discovery.criticality,
        condition=discovery.condition,
        assigned_to_custodian_owner_business_line=discovery.assigned_to_custodian_owner_business_line,
        department_id=discovery.department_id
    )
    db.add(new_asset)

    discovery.status = "approved"
    discovery.infosec_approved_by = user_id
    discovery.infosec_approved_at = datetime.utcnow()

    audit = models.AuditLog(
        user_id=user_id,
        action="ui_infosec_approve_new_asset",
        entity_type="new_asset_discovery",
        entity_id=discovery.id,
        details="New asset approved by Infosec"
    )
    db.add(audit)
    db.commit()

    return discovery


def reject_discovery_by_infosec(
    discovery_id: int,
    user_id: int,
    reason: str,
    db: Session,
):
    discovery = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.id == discovery_id
    ).first()

    if not discovery:
        raise Exception("Discovery not found")

    if discovery.status not in ["awaiting_infosec_attestation", "new_asset_pending_infosec"]:
        raise Exception("Discovery is not awaiting Infosec approval.")

    discovery.status = "returned_to_lead"

    audit = models.AuditLog(
        user_id=user_id,
        action="ui_infosec_reject_new_asset",
        entity_type="new_asset_discovery",
        entity_id=discovery.id,
        details=reason or "No reason provided"
    )
    db.add(audit)
    db.commit()

    return discovery