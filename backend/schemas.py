from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


def _fmt_dt(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


# ── Component ─────────────────────────────────────────────────────────────────

class ComponentUpdate(BaseModel):
    position: str
    part_number: str
    serial_number: str
    software_pn: Optional[str] = None


class ComponentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: str
    part_number: str
    serial_number: str
    software_pn: Optional[str] = None
    updated_at: Optional[str] = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def fmt_updated(cls, v): return _fmt_dt(v)


# ── Modification ──────────────────────────────────────────────────────────────

class ModificationCreate(BaseModel):
    mod_number: str
    description: str
    embodied_date: str


class ModificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mod_number: str
    description: str
    embodied_date: str
    created_at: Optional[str] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def fmt_created(cls, v): return _fmt_dt(v)


# ── SB Record ─────────────────────────────────────────────────────────────────

class SBRecordCreate(BaseModel):
    sb_number: str
    title: str
    ata_chapter: str
    category: str
    latest_revision: str = "Rev 01"
    status: str = "open"
    revision_accomplished: Optional[str] = None
    accomplishment_date: Optional[str] = None
    work_order_ref: Optional[str] = None
    deferred_expiry_date: Optional[str] = None
    deferred_limit_fh: Optional[float] = None
    deferred_limit_fc: Optional[int] = None
    interval_type: str = "one_time"
    interval_fh: Optional[float] = None
    interval_fc: Optional[int] = None
    interval_days: Optional[int] = None
    next_due_date: Optional[str] = None
    next_due_fh: Optional[float] = None
    next_due_fc: Optional[int] = None
    ad_flag: bool = False
    notes: Optional[str] = None


class SBRecordUpdate(SBRecordCreate):
    pass


class SBRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sb_number: str
    title: str
    ata_chapter: str
    category: str
    latest_revision: str
    status: str
    revision_accomplished: Optional[str] = None
    accomplishment_date: Optional[str] = None
    work_order_ref: Optional[str] = None
    deferred_expiry_date: Optional[str] = None
    deferred_limit_fh: Optional[float] = None
    deferred_limit_fc: Optional[int] = None
    interval_type: str = "one_time"
    interval_fh: Optional[float] = None
    interval_fc: Optional[int] = None
    interval_days: Optional[int] = None
    next_due_date: Optional[str] = None
    next_due_fh: Optional[float] = None
    next_due_fc: Optional[int] = None
    ad_flag: bool = False
    notes: Optional[str] = None
    due_soon: bool = False
    updated_at: Optional[str] = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def fmt_updated(cls, v): return _fmt_dt(v)


# ── Aircraft ──────────────────────────────────────────────────────────────────

class AircraftUpdate(BaseModel):
    current_fh: Optional[float] = None
    current_fc: Optional[int] = None
    registration: Optional[str] = None
    operator: Optional[str] = None


class AircraftListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    msn: str
    registration: str
    type_variant: str
    operator: str
    delivery_date: Optional[str] = None
    current_fh: float
    current_fc: int
    open_sbs: int = 0
    ad_open: int = 0
    due_soon_count: int = 0
    updated_at: Optional[str] = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def fmt_updated(cls, v): return _fmt_dt(v)


class AircraftDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    msn: str
    registration: str
    type_variant: str
    operator: str
    delivery_date: Optional[str] = None
    current_fh: float
    current_fc: int
    components: List[ComponentOut] = []
    modifications: List[ModificationOut] = []
    sb_records: List[SBRecordOut] = []
    updated_at: Optional[str] = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def fmt_updated(cls, v): return _fmt_dt(v)
