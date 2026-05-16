from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, index=True)
    msn = Column(String, unique=True, index=True, nullable=False)
    registration = Column(String, nullable=False)
    type_variant = Column(String, nullable=False, default="A320-214")
    operator = Column(String, nullable=False)
    delivery_date = Column(String, nullable=True)
    current_fh = Column(Float, default=0.0)
    current_fc = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    components = relationship("Component", back_populates="aircraft", cascade="all, delete-orphan")
    modifications = relationship("Modification", back_populates="aircraft", cascade="all, delete-orphan")
    sb_records = relationship("SBRecord", back_populates="aircraft", cascade="all, delete-orphan")
    changelogs = relationship("ConfigChangelog", back_populates="aircraft", cascade="all, delete-orphan")


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    position = Column(String, nullable=False)
    part_number = Column(String, nullable=False)
    serial_number = Column(String, nullable=False)
    software_pn = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    aircraft = relationship("Aircraft", back_populates="components")


class Modification(Base):
    __tablename__ = "modifications"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    mod_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    embodied_date = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    aircraft = relationship("Aircraft", back_populates="modifications")


class ConfigChangelog(Base):
    __tablename__ = "config_changelogs"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    field_changed = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_at = Column(DateTime, server_default=func.now())

    aircraft = relationship("Aircraft", back_populates="changelogs")


class SBRecord(Base):
    __tablename__ = "sb_records"

    id = Column(Integer, primary_key=True, index=True)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    sb_number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    ata_chapter = Column(String, nullable=False)
    category = Column(String, nullable=False)       # mandatory | recommended | optional
    latest_revision = Column(String, nullable=False, default="Rev 01")
    status = Column(String, nullable=False, default="open")
    # Accomplished fields
    revision_accomplished = Column(String, nullable=True)
    accomplishment_date = Column(String, nullable=True)
    work_order_ref = Column(String, nullable=True)
    # Deferred fields
    deferred_expiry_date = Column(String, nullable=True)
    deferred_limit_fh = Column(Float, nullable=True)
    deferred_limit_fc = Column(Integer, nullable=True)
    # Recurrence fields
    interval_type = Column(String, default="one_time")  # one_time | recurring
    interval_fh = Column(Float, nullable=True)
    interval_fc = Column(Integer, nullable=True)
    interval_days = Column(Integer, nullable=True)
    next_due_date = Column(String, nullable=True)
    next_due_fh = Column(Float, nullable=True)
    next_due_fc = Column(Integer, nullable=True)
    # Flags
    ad_flag = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    aircraft = relationship("Aircraft", back_populates="sb_records")
