from pathlib import Path
from sqlalchemy.orm import Session

from app import models
from app.pdf_utils import generate_attestation_pdf


def check_attestation_readiness(department_id: int, cycle_id: int, db: Session):
    assets = db.query(models.Asset).filter(
        models.Asset.department_id == department_id
    ).all()

    asset_ids = {a.id for a in assets}

    validations = db.query(models.AssetValidation).filter(
        models.AssetValidation.department_id == department_id,
        models.AssetValidation.cycle_id == cycle_id
    ).all()

    validated_asset_ids = {
        v.asset_id for v in validations
        if v.asset_id is not None
    }

    missing_asset_ids = sorted(asset_ids - validated_asset_ids)

    pending_lead_validations = db.query(models.AssetValidation).filter(
        models.AssetValidation.department_id == department_id,
        models.AssetValidation.cycle_id == cycle_id,
        models.AssetValidation.approval_stage == "pending_lead_review"
    ).count()

    pending_lead_discoveries = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.department_id == department_id,
        models.NewAssetDiscovery.cycle_id == cycle_id,
        models.NewAssetDiscovery.status == "new_asset_pending_lead_review"
    ).count()

    return {
        "is_ready": (
            len(missing_asset_ids) == 0
            and pending_lead_validations == 0
            and pending_lead_discoveries == 0
        ),
        "missing_asset_ids": missing_asset_ids,
        "pending_lead_validations": pending_lead_validations,
        "pending_lead_discoveries": pending_lead_discoveries,
    }


def process_attestation(
    user_id: int,
    department_id: int,
    cycle_id: int,
    attestation_data: str,
    db: Session,
):
    lead_user = db.query(models.ADUser).filter(
        models.ADUser.id == user_id
    ).first()
    if not lead_user:
        raise Exception("Lead user not found")

    dept = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    if not dept:
        raise Exception("Department not found")

    cycle = db.query(models.ValidationCycle).filter(
        models.ValidationCycle.id == cycle_id
    ).first()
    if not cycle:
        raise Exception("Validation cycle not found")

    existing_attestation = db.query(models.TeamAttestation).filter(
        models.TeamAttestation.department_id == department_id,
        models.TeamAttestation.cycle_id == cycle_id
    ).first()

    if existing_attestation:
        raise Exception("An attestation has already been submitted for this department and cycle.")

    readiness = check_attestation_readiness(
        department_id=department_id,
        cycle_id=cycle_id,
        db=db
    )

    if not readiness["is_ready"]:
        reasons = []

        if readiness["missing_asset_ids"]:
            reasons.append(
                f"{len(readiness['missing_asset_ids'])} assets have not been validated by Team Members."
            )

        if readiness["pending_lead_validations"] > 0:
            reasons.append(
                f"{readiness['pending_lead_validations']} validations are still pending Team Lead approval."
            )

        if readiness["pending_lead_discoveries"] > 0:
            reasons.append(
                f"{readiness['pending_lead_discoveries']} new asset discoveries are still pending Team Lead review."
            )

        raise Exception("Attestation cannot be submitted yet. " + " ".join(reasons))

    attestation = models.TeamAttestation(
        lead_user_id=user_id,
        department_id=department_id,
        cycle_id=cycle_id,
        attestation_data=attestation_data,
        status="submitted",
        infosec_status="pending",
    )
    db.add(attestation)
    db.commit()
    db.refresh(attestation)

    pdf_dir = Path("generated_attestations")
    pdf_filename = f"attestation_{attestation.id}.pdf"
    pdf_path = pdf_dir / pdf_filename

    generate_attestation_pdf(
        output_path=str(pdf_path),
        department_name=dept.name,
        cycle_name=cycle.name,
        lead_name=lead_user.display_name or lead_user.username,
        attestation_data=attestation_data or "",
        attestation_id=attestation.id,
    )

    if not pdf_path.exists():
        raise Exception("PDF generation failed")

    attestation.file_path = str(pdf_path)

    validations = db.query(models.AssetValidation).filter(
        models.AssetValidation.department_id == department_id,
        models.AssetValidation.cycle_id == cycle_id,
        models.AssetValidation.approval_stage == "pending_attestation"
    ).all()

    for v in validations:
        if v.status == "reassign":
            v.approval_stage = "pending_it_compliance"
            v.reassignment_status = "pending_compliance"
        else:
            v.approval_stage = "awaiting_infosec_attestation"

    discoveries = db.query(models.NewAssetDiscovery).filter(
        models.NewAssetDiscovery.department_id == department_id,
        models.NewAssetDiscovery.cycle_id == cycle_id,
        models.NewAssetDiscovery.status == "new_asset_pending_attestation"
    ).all()

    for d in discoveries:
        d.status = "awaiting_infosec_attestation"

    audit = models.AuditLog(
        user_id=user_id,
        action="submit_attestation",
        entity_type="team_attestation",
        entity_id=attestation.id,
        details=f"department_id={department_id}; cycle_id={cycle_id}; pdf={pdf_path}"
    )
    db.add(audit)

    db.commit()
    db.refresh(attestation)

    return attestation