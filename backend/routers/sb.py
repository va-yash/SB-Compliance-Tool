from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import json
import os
import io

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api", tags=["sb"])

SYSTEM_PROMPT = """You are an aviation technical document parser specialising in Airbus Service Bulletin applicability. \
Extract the applicability rules from the effectivity section provided. Return only valid JSON with this structure:
{
  "msn_range": {"from": null, "to": null},
  "excluded_msns": [],
  "required_mod_numbers": [],
  "excluded_mod_numbers": [],
  "required_pns": [],
  "notes": "",
  "confidence": "high",
  "confidence_reason": ""
}
If any field is not mentioned in the text, set it to null or empty array. Return ONLY the JSON object, no other text."""


# ── Add SB record ─────────────────────────────────────────────────────────────

@router.post("/aircraft/{msn}/sb", response_model=schemas.SBRecordOut)
def add_sb(msn: str, data: schemas.SBRecordCreate, db: Session = Depends(get_db)):
    if not data.sb_number.strip():
        raise HTTPException(status_code=422, detail="SB number cannot be empty")
    if data.status == "accomplished" and data.accomplishment_date:
        from datetime import date
        try:
            d = date.fromisoformat(data.accomplishment_date)
            if d > date.today():
                raise HTTPException(status_code=422, detail="Accomplishment date cannot be in the future")
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid accomplishment date format")

    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    sb = models.SBRecord(aircraft_id=a.id, **data.model_dump())
    db.add(sb)
    db.commit()
    db.refresh(sb)
    return schemas.SBRecordOut.model_validate(sb)


# ── Update SB record ──────────────────────────────────────────────────────────

@router.put("/aircraft/{msn}/sb/{sb_id}", response_model=schemas.SBRecordOut)
def update_sb(msn: str, sb_id: int, data: schemas.SBRecordUpdate, db: Session = Depends(get_db)):
    if data.status == "accomplished" and data.accomplishment_date:
        from datetime import date
        try:
            d = date.fromisoformat(data.accomplishment_date)
            if d > date.today():
                raise HTTPException(status_code=422, detail="Accomplishment date cannot be in the future")
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid accomplishment date format")

    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    sb = db.query(models.SBRecord).filter(
        models.SBRecord.id == sb_id,
        models.SBRecord.aircraft_id == a.id
    ).first()
    if not sb:
        raise HTTPException(status_code=404, detail="SB record not found")

    for field, val in data.model_dump().items():
        setattr(sb, field, val)

    db.commit()
    db.refresh(sb)
    return schemas.SBRecordOut.model_validate(sb)


# ── Delete SB record ──────────────────────────────────────────────────────────

@router.delete("/aircraft/{msn}/sb/{sb_id}")
def delete_sb(msn: str, sb_id: int, db: Session = Depends(get_db)):
    a = db.query(models.Aircraft).filter(models.Aircraft.msn == msn).first()
    if not a:
        raise HTTPException(status_code=404, detail="Aircraft not found")

    sb = db.query(models.SBRecord).filter(
        models.SBRecord.id == sb_id,
        models.SBRecord.aircraft_id == a.id
    ).first()
    if not sb:
        raise HTTPException(status_code=404, detail="SB record not found")

    db.delete(sb)
    db.commit()
    return {"deleted": sb_id}


# ── Parse SB applicability ────────────────────────────────────────────────────

@router.post("/sb/parse-applicability")
async def parse_applicability(
    pdf_file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Extract text
    if pdf_file is not None and pdf_file.filename:
        if not pdf_file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")
        contents = await pdf_file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large — maximum 10 MB")
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {e}")
        if not extracted.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF — it may be a scanned image")
        source = "pdf"
        input_text = extracted
    elif text and text.strip():
        input_text = text
        source = "text"
    else:
        raise HTTPException(status_code=400, detail="Provide either a PDF file or paste text")

    # 2. Call Claude
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set in environment")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": input_text[:8000]}]
        )
        raw = message.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Claude returned malformed JSON — try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {e}")

    # 3. Compare against registered MSNs
    all_aircraft = db.query(models.Aircraft).order_by(models.Aircraft.msn).all()
    msn_from = (parsed.get("msn_range") or {}).get("from")
    msn_to = (parsed.get("msn_range") or {}).get("to")
    excluded_msns = parsed.get("excluded_msns") or []
    required_mods = parsed.get("required_mod_numbers") or []
    excluded_mods = parsed.get("excluded_mod_numbers") or []

    results = []
    for a in all_aircraft:
        applicability = "likely_applicable"
        reasons = []

        # MSN range check
        if msn_from or msn_to:
            try:
                msn_int = int(a.msn)
                if msn_from and int(msn_from) > msn_int:
                    applicability = "likely_not_applicable"
                    reasons.append(f"MSN below range start ({msn_from})")
                if msn_to and int(msn_to) < msn_int:
                    applicability = "likely_not_applicable"
                    reasons.append(f"MSN above range end ({msn_to})")
            except (ValueError, TypeError):
                applicability = "uncertain"
                reasons.append("MSN range format could not be parsed numerically")

        # Explicit exclusion
        if a.msn in excluded_msns:
            applicability = "likely_not_applicable"
            reasons.append("MSN explicitly excluded in effectivity")

        # Required mods
        aircraft_mods = {m.mod_number for m in a.modifications}
        for req in required_mods:
            if req not in aircraft_mods:
                applicability = "uncertain"
                reasons.append(f"Required mod '{req}' not in aircraft config")

        # Excluded mods
        for excl in excluded_mods:
            if excl in aircraft_mods:
                applicability = "likely_not_applicable"
                reasons.append(f"Aircraft has excluded mod '{excl}'")

        if not reasons:
            reasons.append("Within effectivity range — no conflicts found")

        results.append({
            "msn": a.msn,
            "registration": a.registration,
            "operator": a.operator,
            "applicability": applicability,
            "reason": "; ".join(reasons)
        })

    return {
        "parsed": parsed,
        "results": results,
        "source": source,
        "chars_analysed": len(input_text)
    }
