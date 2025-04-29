from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database.database import Base

class LicenseType(str, enum.Enum):
    TRIAL = "trial"
    MONTHLY = "monthly"
    LIFETIME = "lifetime"

class LicenseStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    licenses = relationship("License", back_populates="user")

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    type = Column(String, default=LicenseType.TRIAL)
    status = Column(String, default=LicenseStatus.ACTIVE)
    hwid = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="licenses")

    def is_expired(self) -> bool:
        if self.type == LicenseType.LIFETIME:
            return False
        if not self.expires_at:
            return True
        return datetime.utcnow() > self.expires_at

    def is_valid(self, hwid: str = None) -> bool:
        if self.status != LicenseStatus.ACTIVE:
            return False
        if self.is_expired():
            return False
        if hwid and self.hwid and self.hwid != hwid:
            return False
        return True