from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# -------------------------
# Department
# -------------------------
class DepartmentCreate(BaseModel):
    name: str


class DepartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# -------------------------
# AD User
# -------------------------
class ADUserCreate(BaseModel):
    username: str
    email: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None


class ADUserOut(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    last_login: datetime

    class Config:
        from_attributes = True

# -------------------------
# AD Group Mapping
# -------------------------
class ADGroupMappingCreate(BaseModel):
    ad_group_name: str
    department_id: Optional[int] = None
    role: str  # member, lead, infosec, compliance


class ADGroupMappingOut(BaseModel):
    id: int
    ad_group_name: str
    department_id: Optional[int] = None
    role: str

    class Config:
        from_attributes = True


# -------------------------
# Validation Cycle
# -------------------------
class ValidationCycleCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    status: str = "scheduled"


class ValidationCycleOut(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Asset
# -------------------------
class AssetCreate(BaseModel):
    serial_no: str
    asset_serial_no: Optional[str] = None
    asset_type: Optional[str] = None
    host_name: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    privilege: Optional[str] = None
    criticality: Optional[str] = None
    condition: Optional[str] = None
    assigned_to_custodian_owner_business_line: Optional[str] = None
    department_id: int


class AssetOut(BaseModel):
    id: int
    serial_no: str
    asset_serial_no: Optional[str] = None
    asset_type: Optional[str] = None
    host_name: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    privilege: Optional[str] = None
    criticality: Optional[str] = None
    condition: Optional[str] = None
    assigned_to_custodian_owner_business_line: Optional[str] = None
    department_id: int

    class Config:
        from_attributes = True

# -------------------------
# Asset Validation
# -------------------------
class AssetValidationCreate(BaseModel):
    cycle_id: Optional[int] = None
    asset_id: Optional[int] = None
    user_id: int
    department_id: int
    status: str
    comment: Optional[str] = None
    is_new_asset: bool = False
    new_asset_status: Optional[str] = None
    reassignment_status: Optional[str] = None
    new_department_id: Optional[int] = None
    approval_stage: str = "pending_lead_review"


class AssetValidationOut(BaseModel):
    id: int
    cycle_id: Optional[int] = None
    asset_id: Optional[int] = None
    user_id: int
    department_id: int
    status: str
    comment: Optional[str] = None
    is_new_asset: bool
    new_asset_status: Optional[str] = None
    reassignment_status: Optional[str] = None
    new_department_id: Optional[int] = None
    approval_stage: str
    approved: bool
    lead_approved_by: Optional[int] = None
    lead_approved_at: Optional[datetime] = None
    infosec_approved_by: Optional[int] = None
    infosec_approved_at: Optional[datetime] = None
    compliance_approved_by: Optional[int] = None
    compliance_approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# New Asset Discovery
# -------------------------
class NewAssetDiscoveryCreate(BaseModel):
    cycle_id: Optional[int] = None
    department_id: int
    submitted_by: int

    sn: Optional[str] = None
    condition: Optional[str] = None
    asset_type: Optional[str] = None
    asset_serial_no: Optional[str] = None
    host_application_server_name: Optional[str] = None
    description: Optional[str] = None
    application_url_ip: Optional[str] = None
    privilege: Optional[str] = None
    criticality: Optional[str] = None
    assigned_to_custodian_owner_business_line: Optional[str] = None


class NewAssetDiscoveryOut(BaseModel):
    id: int
    cycle_id: Optional[int] = None
    department_id: int
    submitted_by: int

    sn: Optional[str] = None
    condition: Optional[str] = None
    asset_type: Optional[str] = None
    asset_serial_no: Optional[str] = None
    host_application_server_name: Optional[str] = None
    description: Optional[str] = None
    application_url_ip: Optional[str] = None
    privilege: Optional[str] = None
    criticality: Optional[str] = None
    assigned_to_custodian_owner_business_line: Optional[str] = None

    status: str
    lead_approved_by: Optional[int] = None
    lead_approved_at: Optional[datetime] = None
    infosec_approved_by: Optional[int] = None
    infosec_approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Team Attestation
# -------------------------
class TeamAttestationCreate(BaseModel):
    cycle_id: Optional[int] = None
    department_id: int
    lead_user_id: int
    attestation_data: Optional[str] = None
    status: str = "submitted"
    file_path: Optional[str] = None


class TeamAttestationOut(BaseModel):
    id: int
    cycle_id: Optional[int] = None
    department_id: int
    lead_user_id: int
    attestation_data: Optional[str] = None
    status: str
    submitted_at: datetime
    file_path: Optional[str] = None
    download_restricted_to: str
    infosec_status: Optional[str] = None
    infosec_approved_by: Optional[int] = None
    infosec_approved_at: Optional[datetime] = None
    infosec_comment: Optional[str] = None
    class Config:
        from_attributes = True


# -------------------------
# Team Queue Item
# -------------------------
class TeamQueueItemCreate(BaseModel):
    asset_id: int
    department_id: int
    source_validation_id: Optional[int] = None
    queue_type: str = "reassigned_asset"
    status: str = "pending_new_team_validation"


class TeamQueueItemOut(BaseModel):
    id: int
    asset_id: int
    department_id: int
    source_validation_id: Optional[int] = None
    queue_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Audit Log
# -------------------------
class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
