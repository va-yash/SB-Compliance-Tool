#!/usr/bin/env python3
"""
Seed the SB Compliance Tool database with 10 A320-214 aircraft.
Run from the backend/ directory:  python seed.py
"""
import sys
import os
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

TODAY = date.today()


# ─────────────────────────────────────────────────────────────────────────────
# SB POOL  —  20 representative A320 Service Bulletins
# ─────────────────────────────────────────────────────────────────────────────
SB_POOL = [
    {
        "sb_number": "A320-27-1098",
        "title": "SFCC — Software Standard Update to Std 5.2",
        "ata_chapter": "27", "category": "recommended",
        "latest_revision": "Rev 03", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-53-2341",
        "title": "Fuselage — Frame 47 Area Fatigue Crack Inspection",
        "ata_chapter": "53", "category": "mandatory",
        "latest_revision": "Rev 01", "ad_flag": True,
        "interval_type": "recurring", "interval_fh": 5000,
    },
    {
        "sb_number": "A320-32-1456",
        "title": "MLG — Actuator Attachment Bracket Fatigue Inspection",
        "ata_chapter": "32", "category": "mandatory",
        "latest_revision": "Rev 02", "ad_flag": False,
        "interval_type": "recurring", "interval_fc": 3000,
    },
    {
        "sb_number": "A320-28-1203",
        "title": "Fuel System — EWIS Wiring Inspection (FAR 25.981)",
        "ata_chapter": "28", "category": "mandatory",
        "latest_revision": "Rev 04", "ad_flag": True, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-24-0891",
        "title": "Electrical — Generator Control Unit Software Upgrade v3.4",
        "ata_chapter": "24", "category": "recommended",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-34-1567",
        "title": "Navigation — ADIRU Software Update to Std P12/18",
        "ata_chapter": "34", "category": "recommended",
        "latest_revision": "Rev 05", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-21-0445",
        "title": "Air Conditioning — Pack Flow Control Valve Inspection",
        "ata_chapter": "21", "category": "optional",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-52-1123",
        "title": "Doors — Type A Door Seal Assembly Replacement",
        "ata_chapter": "52", "category": "optional",
        "latest_revision": "Rev 02", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-71-2234",
        "title": "Powerplant — CFM56 Nacelle Cowl Latch Pin Inspection",
        "ata_chapter": "71", "category": "mandatory",
        "latest_revision": "Rev 01", "ad_flag": False,
        "interval_type": "recurring", "interval_fh": 1000,
    },
    {
        "sb_number": "A320-57-0678",
        "title": "Wings — Lower Wing Spar Joint Fatigue Inspection",
        "ata_chapter": "57", "category": "mandatory",
        "latest_revision": "Rev 03", "ad_flag": True,
        "interval_type": "recurring", "interval_fh": 6000,
    },
    {
        "sb_number": "A320-29-0934",
        "title": "Hydraulic — Yellow System Pump Bracket Fatigue Check",
        "ata_chapter": "29", "category": "recommended",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-25-1045",
        "title": "Equipment — Passenger Seat Track Wear Inspection",
        "ata_chapter": "25", "category": "optional",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-05-0234",
        "title": "Time Limits — Structural Sampling Programme Update",
        "ata_chapter": "05", "category": "mandatory",
        "latest_revision": "Rev 02", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-27-1234",
        "title": "Flight Controls — ELAC Software Standard Update to P7/9",
        "ata_chapter": "27", "category": "recommended",
        "latest_revision": "Rev 04", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-34-1890",
        "title": "Navigation — GPS/MMR Software Update to Std 3.0.1",
        "ata_chapter": "34", "category": "optional",
        "latest_revision": "Rev 02", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-32-1678",
        "title": "Landing Gear — NLG Shimmy Damper Wear Inspection",
        "ata_chapter": "32", "category": "mandatory",
        "latest_revision": "Rev 01", "ad_flag": False,
        "interval_type": "recurring", "interval_fc": 2000,
    },
    {
        "sb_number": "A320-53-2567",
        "title": "Fuselage — Belly Fairing Rib Attachment Inspection",
        "ata_chapter": "53", "category": "recommended",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-24-1102",
        "title": "Electrical — Main Battery Charger Modification",
        "ata_chapter": "24", "category": "optional",
        "latest_revision": "Rev 01", "ad_flag": False, "interval_type": "one_time",
    },
    {
        "sb_number": "A320-71-2456",
        "title": "Powerplant — CFM56-5B Fan Blade FPI (EASA AD 2019/045)",
        "ata_chapter": "71", "category": "mandatory",
        "latest_revision": "Rev 02", "ad_flag": True,
        "interval_type": "recurring", "interval_fh": 2000,
    },
    {
        "sb_number": "A320-28-1389",
        "title": "Fuel System — FQMS Software and Wiring Harness Update",
        "ata_chapter": "28", "category": "recommended",
        "latest_revision": "Rev 03", "ad_flag": False, "interval_type": "one_time",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# AIRCRAFT MASTER DATA
# ─────────────────────────────────────────────────────────────────────────────
AIRCRAFT_LIST = [
    {"msn": "0834", "registration": "F-FAKE1", "operator": "Air Occitanie",
     "type_variant": "A320-214", "delivery_date": "2001-03-15",
     "current_fh": 46832.0, "current_fc": 33240},
    {"msn": "0921", "registration": "F-FAKE2", "operator": "Air Occitanie",
     "type_variant": "A320-214", "delivery_date": "2002-07-22",
     "current_fh": 43210.5, "current_fc": 30780},
    {"msn": "1205", "registration": "OE-LKA", "operator": "Alpine Express",
     "type_variant": "A320-214", "delivery_date": "2004-05-10",
     "current_fh": 38450.0, "current_fc": 27340},
    {"msn": "1312", "registration": "OE-LKB", "operator": "Alpine Express",
     "type_variant": "A320-214", "delivery_date": "2005-09-18",
     "current_fh": 35670.5, "current_fc": 25120},
    {"msn": "2341", "registration": "YU-APB", "operator": "Balkan Regional",
     "type_variant": "A320-214", "delivery_date": "2009-02-14",
     "current_fh": 27890.0, "current_fc": 19840},
    {"msn": "2456", "registration": "YU-APC", "operator": "Balkan Regional",
     "type_variant": "A320-214", "delivery_date": "2010-06-30",
     "current_fh": 25340.0, "current_fc": 18050},
    {"msn": "3102", "registration": "D-AXRA", "operator": "Rhein Air",
     "type_variant": "A320-214", "delivery_date": "2012-11-05",
     "current_fh": 20150.5, "current_fc": 14320},
    {"msn": "3215", "registration": "D-AXRB", "operator": "Rhein Air",
     "type_variant": "A320-214", "delivery_date": "2013-04-22",
     "current_fh": 18230.0, "current_fc": 12980},
    {"msn": "4401", "registration": "C-FAKE3", "operator": "Air Nordique",
     "type_variant": "A320-214", "delivery_date": "2017-08-15",
     "current_fh": 11890.0, "current_fc": 8450},
    {"msn": "4502", "registration": "C-FAKE4", "operator": "Air Nordique",
     "type_variant": "A320-214", "delivery_date": "2018-03-28",
     "current_fh": 9870.5, "current_fc": 7020},
]


# ─────────────────────────────────────────────────────────────────────────────
# DUE-SOON OVERRIDES  — force specific aircraft-SB pairs into the warning zone
# ─────────────────────────────────────────────────────────────────────────────
DUE_SOON_OVERRIDES = {
    ("0834", "A320-71-2456"): {"next_due_fh": 46832.0 + 35},        # fan blade FPI: 35 FH remaining
    ("0921", "A320-53-2341"): {"next_due_fh": 43210.5 + 22},        # fuselage frame: 22 FH remaining
    ("1205", "A320-32-1456"): {"next_due_fc": 27340 + 28},          # MLG bracket: 28 FC remaining
    ("2341", "A320-32-1678"): {"next_due_date": (TODAY + timedelta(days=18)).isoformat()},
    ("3102", "A320-57-0678"): {"next_due_fh": 20150.5 + 40},        # wing spar: 40 FH remaining
    ("4401", "A320-71-2234"): {"next_due_fh": 11890.0 + 45},        # cowl latch: 45 FH remaining
}


# ─────────────────────────────────────────────────────────────────────────────
# MOD POOL
# ─────────────────────────────────────────────────────────────────────────────
MOD_POOL = [
    ("SB A320-27-1098",  "SFCC Software Std 5.2 embodied"),
    ("SB A320-24-0891",  "GCU Software v3.4 upgrade"),
    ("SB A320-34-1567",  "ADIRU Software P12/18 update"),
    ("SB A320-27-1234",  "ELAC Software P7/9 embodied"),
    ("SB A320-34-1890",  "GPS/MMR Software v3.0.1"),
    ("SB A320-52-1123",  "Type A door seal replaced"),
    ("SB A320-29-0934",  "Yellow hyd pump bracket modified"),
    ("SB A320-25-1045",  "Seat track wear pads installed"),
    ("SB A320-05-0234",  "Structural sampling programme Std 2"),
    ("SB A320-24-1102",  "Battery charger modification kit installed"),
    ("SB A320-53-2567",  "Belly fairing rib strap installed"),
    ("SB A320-28-1389",  "FQMS software wiring update"),
    ("MOD 26345",        "Cabin connectivity pre-wire installation"),
    ("MOD 27891",        "Passenger emergency lighting update"),
    ("MOD 29012",        "SATCOM dome structural reinforcement"),
    ("MOD 31456",        "ACARS printer removal — EFB transition"),
    ("MOD 32001",        "BSCU v24 brake control software update"),
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def make_components(idx: int) -> list:
    """Generate 12 components per aircraft. idx is 1-based."""
    return [
        {"position": "Engine 1",     "part_number": "CFM56-5B4/P",   "serial_number": f"565B-{12300 + idx*17:05d}"},
        {"position": "Engine 2",     "part_number": "CFM56-5B4/P",   "serial_number": f"565B-{98700 + idx*23:05d}"},
        {"position": "APU",          "part_number": "GTCP131-9A",    "serial_number": f"P{45000 + idx*31:06d}"},
        {"position": "NLG (Nose)",   "part_number": "A32032-0010-00","serial_number": f"NLG-{8000 + idx*11:04d}"},
        {"position": "MLG Left",     "part_number": "A32032-0020-00","serial_number": f"MLG-{4000 + idx*13:04d}"},
        {"position": "MLG Right",    "part_number": "A32032-0020-00","serial_number": f"MLG-{6000 + idx*17:04d}"},
        {"position": "ADIRU 1",      "part_number": "HG2030AD01",    "serial_number": f"ADIRU-{1000 + idx*7:04d}",  "software_pn": f"SW-ADR-{34 + idx:02d}"},
        {"position": "ADIRU 2",      "part_number": "HG2030AD01",    "serial_number": f"ADIRU-{2000 + idx*7:04d}",  "software_pn": f"SW-ADR-{34 + idx:02d}"},
        {"position": "FMGC 1",       "part_number": "822-0883-114",  "serial_number": f"FMGC-{1100 + idx*9:04d}",  "software_pn": f"SW-FMS-H{5 + idx}"},
        {"position": "FMGC 2",       "part_number": "822-0883-114",  "serial_number": f"FMGC-{2200 + idx*9:04d}",  "software_pn": f"SW-FMS-H{5 + idx}"},
        {"position": "SFCC 1",       "part_number": "A28276028-00",  "serial_number": f"SFCC-{1000 + idx*11:04d}", "software_pn": f"SW-SFCC-{5 + idx}"},
        {"position": "GPWS/TAWS",    "part_number": "965-1676-003",  "serial_number": f"GPWS-{500  + idx*7:04d}",  "software_pn": f"SW-TAWS-{22 + idx}"},
    ]


def make_mods(msn: str, rng: random.Random) -> list:
    n = rng.randint(5, 12)
    selected = rng.sample(MOD_POOL, min(n, len(MOD_POOL)))
    result = []
    for mod_num, desc in selected:
        days_ago = rng.randint(180, 3200)
        emb_date = (TODAY - timedelta(days=days_ago)).isoformat()
        result.append({"mod_number": mod_num, "description": desc, "embodied_date": emb_date})
    return result


def pick_status(fh: float, sb: dict, rng: random.Random) -> str:
    ad = sb.get("ad_flag", False)
    cat = sb["category"]
    if fh > 35000:
        if ad:       opts = [("accomplished", 90), ("open", 7), ("amoc_applied", 3)]
        elif cat == "mandatory":   opts = [("accomplished", 80), ("open", 12), ("deferred", 5), ("amoc_applied", 3)]
        elif cat == "recommended": opts = [("accomplished", 72), ("open", 16), ("not_applicable", 9), ("superseded", 3)]
        else:        opts = [("accomplished", 48), ("not_applicable", 38), ("open", 14)]
    elif fh > 20000:
        if ad:       opts = [("accomplished", 74), ("open", 20), ("deferred", 6)]
        elif cat == "mandatory":   opts = [("accomplished", 64), ("open", 28), ("deferred", 8)]
        elif cat == "recommended": opts = [("accomplished", 50), ("open", 34), ("not_applicable", 16)]
        else:        opts = [("not_applicable", 44), ("accomplished", 30), ("open", 26)]
    else:
        if ad:       opts = [("accomplished", 55), ("open", 40), ("deferred", 5)]
        elif cat == "mandatory":   opts = [("accomplished", 44), ("open", 48), ("deferred", 8)]
        elif cat == "recommended": opts = [("open", 50), ("accomplished", 30), ("not_applicable", 20)]
        else:        opts = [("open", 38), ("not_applicable", 50), ("accomplished", 12)]

    statuses, weights = zip(*opts)
    return rng.choices(statuses, weights=weights)[0]


def make_sb_record(aircraft_id: int, fh: float, fc: int, sb: dict, rng: random.Random) -> dict:
    status = pick_status(fh, sb, rng)
    itype = sb.get("interval_type", "one_time")

    rec = {
        "aircraft_id": aircraft_id,
        "sb_number":   sb["sb_number"],
        "title":       sb["title"],
        "ata_chapter": sb["ata_chapter"],
        "category":    sb["category"],
        "latest_revision": sb["latest_revision"],
        "ad_flag":     sb.get("ad_flag", False),
        "interval_type": itype,
        "interval_fh":  sb.get("interval_fh"),
        "interval_fc":  sb.get("interval_fc"),
        "interval_days": sb.get("interval_days"),
        "status": status,
    }

    if status == "accomplished":
        years = max(1, int(fh / 9000))
        acc_date = (TODAY - timedelta(days=rng.randint(60, years * 365 + 180))).isoformat()
        rec["revision_accomplished"] = sb["latest_revision"]
        rec["accomplishment_date"] = acc_date
        rec["work_order_ref"] = f"WO-{rng.randint(10000, 99999)}"
        # Recurring: set a future next_due (not in due-soon zone yet)
        if itype == "recurring":
            if sb.get("interval_fh"):
                gap = rng.uniform(200, max(210, sb["interval_fh"] - 200))
                rec["next_due_fh"] = round(fh - gap + sb["interval_fh"], 1)
            if sb.get("interval_fc"):
                gap = rng.randint(200, max(210, sb["interval_fc"] - 200))
                rec["next_due_fc"] = fc - gap + sb["interval_fc"]

    elif status == "deferred":
        rec["deferred_expiry_date"] = (TODAY + timedelta(days=rng.randint(30, 180))).isoformat()

    return rec


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SEED FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def seed():
    db = SessionLocal()

    # Clear existing data
    for mdl in [models.SBRecord, models.Modification, models.Component,
                models.ConfigChangelog, models.Aircraft]:
        db.query(mdl).delete()
    db.commit()
    print("Database cleared.")

    total_sbs = 0

    for idx, ac_data in enumerate(AIRCRAFT_LIST, 1):
        aircraft = models.Aircraft(**ac_data)
        db.add(aircraft)
        db.flush()  # assigns aircraft.id

        # Components
        for comp_data in make_components(idx):
            db.add(models.Component(aircraft_id=aircraft.id, **comp_data))

        # Modifications
        rng_mod = random.Random(f"{ac_data['msn']}-mods")
        for mod_data in make_mods(ac_data["msn"], rng_mod):
            db.add(models.Modification(aircraft_id=aircraft.id, **mod_data))

        # SB records
        rng_sb = random.Random(f"{ac_data['msn']}-sbs")
        for sb_def in SB_POOL:
            rec = make_sb_record(
                aircraft.id,
                ac_data["current_fh"],
                ac_data["current_fc"],
                sb_def,
                rng_sb
            )

            # Apply due-soon override if this aircraft-SB pair is in the list
            key = (ac_data["msn"], sb_def["sb_number"])
            if key in DUE_SOON_OVERRIDES:
                # Make sure it's accomplished with a recurring next_due in the warning zone
                rec["status"] = "accomplished"
                if not rec.get("revision_accomplished"):
                    rec["revision_accomplished"] = sb_def["latest_revision"]
                    rec["accomplishment_date"] = (TODAY - timedelta(days=rng_sb.randint(30, 400))).isoformat()
                    rec["work_order_ref"] = f"WO-{rng_sb.randint(10000, 99999)}"
                rec.update(DUE_SOON_OVERRIDES[key])

            db.add(models.SBRecord(**rec))
            total_sbs += 1

        print(f"  ✓ MSN {ac_data['msn']}  {ac_data['registration']}  ({ac_data['operator']})")

    db.commit()
    db.close()

    print(f"\nSeed complete.")
    print(f"  Aircraft:  {len(AIRCRAFT_LIST)}")
    print(f"  SB records: {total_sbs}  ({total_sbs // len(AIRCRAFT_LIST)} per aircraft)")
    print(f"  Due-soon overrides: {len(DUE_SOON_OVERRIDES)}")


if __name__ == "__main__":
    seed()
