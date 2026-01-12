from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.family import FamilyProfile, FamilyMember
from app.models.user import User
from app.middleware.auth import get_current_user
from app import database as db

router = APIRouter()


@router.get("/profile", response_model=FamilyProfile)
async def get_profile(current_user: Optional[User] = Depends(get_current_user)):
    """Get the family profile with all members"""
    user_id = current_user.id if current_user else None
    members = await db.get_all_members(user_id=user_id)
    return FamilyProfile(members=members)


@router.post("/profile", response_model=FamilyProfile)
async def create_profile(
    profile: FamilyProfile,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create or replace the entire family profile"""
    # This would typically clear and recreate, but for simplicity
    # we'll just return the existing profile structure
    return profile


@router.post("/member", response_model=FamilyMember)
async def add_member(
    member: FamilyMember,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Add a family member"""
    user_id = current_user.id if current_user else None
    return await db.add_member(member, user_id=user_id)


@router.put("/member/{member_id}", response_model=FamilyMember)
async def update_member(member_id: str, member: FamilyMember):
    """Update a family member"""
    updated = await db.update_member(member_id, member)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    return updated


@router.delete("/member/{member_id}")
async def delete_member(member_id: str):
    """Delete a family member"""
    deleted = await db.delete_member(member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member deleted successfully"}
