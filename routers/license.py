from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from models.models import User, License, LicenseType, LicenseStatus
from database.database import get_db
from core.security import get_hwid
from routers.auth import get_current_user

router = APIRouter()

@router.post("/activate")
async def activate_license(
    license_key: str,
    hwid: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the license
    license = db.query(License).filter(License.key == license_key).first()
    if not license:
        raise HTTPException(status_code=404, detail="License key not found")
    
    # Check if license is already activated
    if license.user_id and license.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="License key is already activated by another user")
    
    # Check license status
    if license.status != LicenseStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="License key is not active")
    
    # Check expiration
    if license.is_expired():
        license.status = LicenseStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="License key has expired")
    
    # Bind HWID if provided
    if hwid:
        if license.hwid and license.hwid != hwid:
            raise HTTPException(status_code=400, detail="License key is bound to a different hardware ID")
        license.hwid = hwid
    
    # Bind license to user if not already bound
    if not license.user_id:
        license.user_id = current_user.id
    
    db.commit()
    db.refresh(license)
    
    return {
        "message": "License key activated successfully",
        "type": license.type,
        "expires_at": license.expires_at
    }

@router.post("/validate")
async def validate_license(
    license_key: str,
    hwid: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the license
    license = db.query(License).filter(License.key == license_key).first()
    if not license:
        raise HTTPException(status_code=404, detail="License key not found")
    
    # Check if license belongs to user
    if license.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="License key does not belong to this user")
    
    # Validate HWID if provided and bound
    if hwid and license.hwid and license.hwid != hwid:
        raise HTTPException(status_code=403, detail="Hardware ID mismatch")
    
    # Check license validity
    if not license.is_valid(hwid):
        return {
            "valid": False,
            "message": "License key is not valid",
            "reason": "expired" if license.is_expired() else "invalid"
        }
    
    return {
        "valid": True,
        "type": license.type,
        "expires_at": license.expires_at,
        "message": "License key is valid"
    }

@router.get("/status")
async def get_license_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all licenses for the current user
    licenses = db.query(License).filter(License.user_id == current_user.id).all()
    
    return {
        "licenses": [
            {
                "key": license.key,
                "type": license.type,
                "status": license.status,
                "expires_at": license.expires_at,
                "is_valid": license.is_valid()
            }
            for license in licenses
        ]
    }