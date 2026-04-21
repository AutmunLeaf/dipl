import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    WORKER = "worker"
    VIEWER = "viewer"


class ActStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.WORKER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    acts_created = relationship("Act", foreign_keys="Act.created_by", back_populates="creator")
    approvals = relationship("Approval", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class ConstructionObject(Base):
    __tablename__ = "construction_objects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    works = relationship("WorkType", back_populates="construction_object")
    acts = relationship("Act", back_populates="construction_object")


class WorkType(Base):
    __tablename__ = "work_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    unit = Column(String(50))  # ед. измерения (м3, м2, шт и т.д.)
    construction_object_id = Column(Integer, ForeignKey("construction_objects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    construction_object = relationship("ConstructionObject", back_populates="works")
    acts = relationship("Act", back_populates="work_type")


class Act(Base):
    __tablename__ = "acts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50))
    date = Column(DateTime, default=datetime.utcnow)
    
    volume = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)  # volume * price
    
    status = Column(Enum(ActStatus), default=ActStatus.DRAFT)
    
    work_type_id = Column(Integer, ForeignKey("work_types.id"))
    construction_object_id = Column(Integer, ForeignKey("construction_objects.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    work_type = relationship("WorkType", back_populates="acts")
    construction_object = relationship("ConstructionObject", back_populates="acts")
    creator = relationship("User", foreign_keys=[created_by], back_populates="acts_created")
    approvals = relationship("Approval", back_populates="act")
    attachments = relationship("Attachment", back_populates="act")
    audit_logs = relationship("AuditLog", back_populates="act")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    act_id = Column(Integer, ForeignKey("acts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    is_approved = Column(Boolean, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    act = relationship("Act", back_populates="approvals")
    user = relationship("User", back_populates="approvals")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    act_id = Column(Integer, ForeignKey("acts.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # в байтах
    mime_type = Column(String(100))
    
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    act = relationship("Act", back_populates="attachments")
    uploader = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    act_id = Column(Integer, ForeignKey("acts.id"))
    
    action = Column(String(50), nullable=False)  # create, update, delete, approve, reject
    entity_type = Column(String(50))  # Act, User, etc.
    entity_id = Column(Integer)
    
    old_values = Column(Text)  # JSON строка со старыми значениями
    new_values = Column(Text)  # JSON строка с новыми значениями
    
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    act = relationship("Act", back_populates="audit_logs")