from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import csv
import io

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/aircraft", tags=["aircraft"])


def compute_due_soon(sb: models.SBRecord, aircraft: models.Aircraft) -> bool:
    """Returns True if this SB is due within 30 days / 50 FH / 50 FC."""
    if sb.status not in ("open", "accomplished", "deferred"):
        return False
    today = date.today()

    if sb.next_due_date:
        try:
            nd = date.fromisoformat(sb.next_due_date)
            if (nd - today).days <= 30:
                return True
        except ValueError:
            pass

    if sb.next_due_fh is not None and aircraft.current_fh:
        if (sb.next_due_fh - aircraft.current_fh) <= 50:
            return True

    if sb.next_due_fc is not None and aircraft.current_fc:
        if (sb.next_due_fc - aircraft.current_fc) <= 50:
            return True

    return False


def enrich_sb(sb: models.SBRecord, aircraft: models.Aircraft) -> schemas.SBRecordOut:
    out = schemas.SBRecordOut.model_validate(sb)
    out.due_soon = compute_due_soon(sb, aircraft)
    return out


# ── List all aircraft ─────────────────────────────────────────────────────────

@router.get("", response_model=List[schemas.AircraftListItem])
def list_aircraft(db: Session = Depends(get_db)):
    aircraft_list = db.query(models.Aircraft).order_by(models.Aircraft.msn).all()
    results = []
    for a in aircraft_list:
        item = schemas.AircraftListItem.model_validate(a)
        item.open_sbs = sum(1 for sb in a.sb_records if sb.status == "open")
        item.ad_open = sum(1 for sb in a.sb_records if sb.status == "open" and sb.ad_flag)
        item.due_soon_count = sum(1 for sb in a.sb_records if compute_due_soon(sb, a))
        results.append(item)
    return results


# ── Aircraft detail ───────────────────────────────────────────────────────────

@router.get("/{msn}", response_model=schemas.AircraftDetail)
def get_aircraft(msn: str, db: Session = Depends(get_db)):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    out = schemas.AircraftDetail.model_validate(a)
    out.sb_records = [enrich_sb(sb, a) for sb in a.sb_records]
    return out


# ── Update aircraft FH/FC/registration ───────────────────────────────────────

@router.patch("/{msn}")
def update_aircraft(msn: str, data: schemas.AircraftUpdate, db: Session = Depends(get_db)):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    for field, val in data.model_dump(exclude_none=True).items():
        setattr(a, field, val)

    db.commit()
    db.refresh(a)
    return {"msn": a.msn, "current_fh": a.current_fh, "current_fc": a.current_fc}


# ── Update a component ────────────────────────────────────────────────────────

@router.put("/{msn}/component/{component_id}", response_model=schemas.ComponentOut)
def update_component(
    msn: str, component_id: int, data: schemas.ComponentUpdate, db: Session = Depends(get_db)
):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    comp = db.query(models.Component).filter(
        models.Component.id == component_id,
        models.Component.aircraft_id == a.id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")

    # Log the changes
    for field, new_val in data.model_dump().items():
        old_val = getattr(comp, field)
        if str(old_val) != str(new_val):
            db.add(models.ConfigChangelog(
                aircraft_id=a.id,
                field_changed=f"{comp.position} — {field}",
                old_value=str(old_val),
                new_value=str(new_val)
            ))

    for field, val in data.model_dump().items():
        setattr(comp, field, val)

    db.commit()
    db.refresh(comp)
    return schemas.ComponentOut.model_validate(comp)


# ── Add a modification ────────────────────────────────────────────────────────

@router.post("/{msn}/modification", response_model=schemas.ModificationOut)
def add_modification(msn: str, data: schemas.ModificationCreate, db: Session = Depends(get_db)):
    if not data.mod_number.strip():
        raise HTTPException(status_code=422, detail="Mod number cannot be empty")
    if not data.embodied_date:
        raise HTTPException(status_code=422, detail="Embodied date is required")

    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    mod = models.Modification(aircraft_id=a.id, **data.model_dump())
    db.add(mod)
    db.commit()
    db.refresh(mod)
    return schemas.ModificationOut.model_validate(mod)


# ── Delete a modification ─────────────────────────────────────────────────────

@router.delete("/{msn}/modification/{mod_id}")
def delete_modification(msn: str, mod_id: int, db: Session = Depends(get_db)):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    mod = db.query(models.Modification).filter(
        models.Modification.id == mod_id,
        models.Modification.aircraft_id == a.id
    ).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Modification not found")

    db.delete(mod)
    db.commit()
    return {"deleted": mod_id}


# ── Export SB list as CSV ─────────────────────────────────────────────────────

@router.get("/{msn}/export-csv")
def export_csv(msn: str, db: Session = Depends(get_db)):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "SB Number", "Title", "ATA Chapter", "Category", "Status",
        "AD Mandated", "Latest Revision", "Revision Accomplished",
        "Accomplishment Date", "Work Order Ref", "Deferred Expiry",
        "Next Due Date", "Next Due FH", "Next Due FC", "Interval Type",
        "Interval FH", "Interval FC", "Interval Days", "Notes"
    ])
    for sb in a.sb_records:
        w.writerow([
            sb.sb_number, sb.title, sb.ata_chapter, sb.category, sb.status,
            "Yes" if sb.ad_flag else "No",
            sb.latest_revision, sb.revision_accomplished or "",
            sb.accomplishment_date or "", sb.work_order_ref or "",
            sb.deferred_expiry_date or "", sb.next_due_date or "",
            sb.next_due_fh or "", sb.next_due_fc or "",
            sb.interval_type, sb.interval_fh or "", sb.interval_fc or "",
            sb.interval_days or "", sb.notes or ""
        ])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=SB_Status_{msn}.csv"}
    )
