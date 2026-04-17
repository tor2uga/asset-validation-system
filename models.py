from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class ADUser(Base):
    __tablename__ = "ad_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=True)
    role = Column(String, nullable=True)  # team_member, team_lead, compliance, infosec
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    last_login = Column(DateTime, default=datetime.utcnow)


class ADGroupMapping(Base):
    __tablename__ = "ad_group_mappings"

    id = Column(Integer, primary_key=True, index=True)
    ad_group_name = Column(String, unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    role = Column(String, nullable=False)  # member, lead, infosec, compliance

    department = relationship("Department")


class ValidationCycle(Base):
    __tablename__ = "validation_cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g. 2026-Q3
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, active, paused, closed
    created_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(String, unique=True, nullable=False)  # import key
    asset_serial_no = Column(String, nullable=True)          # real Asset / Serial No
    asset_type = Column(String, nullable=True)
    host_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    privilege = Column(String, nullable=True)
    criticality = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    assigned_to_custodian_owner_business_line = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    department = relationship("Department")


class AssetValidation(Base):
    __tablename__ = "asset_validations"

    id = Column(Integer, primary_key=True, index=True)

    cycle_id = Column(Integer, ForeignKey("validation_cycles.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("ad_users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    status = Column(String, nullable=False)  # active, decommissioned, inactive, reassign
    comment = Column(Text, nullable=True)

    is_new_asset = Column(Boolean, default=False)
    new_asset_status = Column(String, nullable=True)  # pending_lead, pending_infosec, approved, rejected

    reassignment_status = Column(String, nullable=True)  # pending_lead, pending_compliance, approved, rejected
    new_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    approval_stage = Column(String, default="pending_lead_review")
    approved = Column(Boolean, default=False)

    lead_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    lead_approved_at = Column(DateTime, nullable=True)

    infosec_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    infosec_approved_at = Column(DateTime, nullable=True)

    compliance_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    compliance_approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", foreign_keys=[asset_id])
    user = relationship("ADUser", foreign_keys=[user_id])
    department = relationship("Department", foreign_keys=[department_id])
    new_department = relationship("Department", foreign_keys=[new_department_id])


class NewAssetDiscovery(Base):
    __tablename__ = "new_asset_discoveries"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("validation_cycles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("ad_users.id"), nullable=False)

    sn = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    asset_type = Column(String, nullable=True)
    asset_serial_no = Column(String, nullable=True)
    host_application_server_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    application_url_ip = Column(String, nullable=True)
    privilege = Column(String, nullable=True)
    criticality = Column(String, nullable=True)
    assigned_to_custodian_owner_business_line = Column(String, nullable=True)

    status = Column(String, nullable=False, default="new_asset_pending_lead_review")
    created_at = Column(DateTime, default=datetime.utcnow)

    infosec_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    infosec_approved_at = Column(DateTime, nullable=True)

    status = Column(String, default="new_asset_pending_lead_review")
    lead_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    lead_approved_at = Column(DateTime, nullable=True)
    infosec_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    infosec_approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class TeamAttestation(Base):
    __tablename__ = "team_attestations"

    __table_args__ = (
        UniqueConstraint("department_id", "cycle_id", name="unique_attestation_per_cycle"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("validation_cycles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    lead_user_id = Column(Integer, ForeignKey("ad_users.id"), nullable=False)
    attestation_data = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="submitted")
    submitted_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=True)
    
    infosec_status = Column(String, nullable=True, default="pending")
    infosec_approved_by = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    infosec_approved_at = Column(DateTime, nullable=True)
    infosec_comment = Column(Text, nullable=True)
    
    download_restricted_to = Column(String, default="compliance")
    


class TeamQueueItem(Base):
    __tablename__ = "team_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    source_validation_id = Column(Integer, ForeignKey("asset_validations.id"), nullable=True)

    queue_type = Column(String, default="reassigned_asset")
    status = Column(String, default="pending_new_team_validation")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("ad_users.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    

    