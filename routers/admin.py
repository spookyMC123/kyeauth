from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from models.models import User, License, LicenseType, LicenseStatus
from database.database import get_db
from routers.auth import get_current_user

router = APIRouter()

def verify_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/users")
async def get_users(db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "license_count": len(user.licenses)
        }
        for user in users
    ]

@router.post("/generate-key")
async def generate_license(
    license_type: LicenseType,
    duration_days: int = None,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    # Generate a unique license key
    license_key = str(uuid.uuid4())
    
    # Calculate expiration date
    expires_at = None
    if license_type != LicenseType.LIFETIME:
        if not duration_days:
            duration_days = 30 if license_type == LicenseType.MONTHLY else 7
        expires_at = datetime.utcnow() + timedelta(days=duration_days)
    
    # Create new license
    license = License(
        key=license_key,
        type=license_type,
        status=LicenseStatus.ACTIVE,
        expires_at=expires_at
    )
    
    db.add(license)
    db.commit()
    db.refresh(license)
    
    return {
        "key": license.key,
        "type": license.type,
        "expires_at": license.expires_at
    }

@router.get("/licenses")
async def get_licenses(db: Session = Depends(get_db), admin: User = Depends(verify_admin)):
    licenses = db.query(License).all()
    return [
        {
            "id": license.id,
            "key": license.key,
            "type": license.type,
            "status": license.status,
            "hwid": license.hwid,
            "created_at": license.created_at,
            "expires_at": license.expires_at,
            "user_id": license.user_id,
            "is_valid": license.is_valid()
        }
        for license in licenses
    ]

@router.post("/revoke-license/{license_id}")
async def revoke_license(
    license_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    license = db.query(License).filter(License.id == license_id).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    license.status = LicenseStatus.REVOKED
    db.commit()
    
    return {"message": "License revoked successfully"}

@router.post("/extend-license/{license_id}")
async def extend_license(
    license_id: int,
    days: int,
    db: Session = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    license = db.query(License).filter(License.id == license_id).first()
    if not license:
        raise HTTPException(status_code=404, detail="License not found")
    
    if license.type == LicenseType.LIFETIME:
        raise HTTPException(status_code=400, detail="Cannot extend lifetime license")
    
    # Calculate new expiration date
    current_expiry = license.expires_at or datetime.utcnow()
    license.expires_at = current_expiry + timedelta(days=days)
    
    db.commit()
    
    return {
        "message": "License extended successfully",
        "new_expiry": license.expires_at
    }