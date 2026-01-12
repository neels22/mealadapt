"""
Family profile and member management routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyProfile, FamilyMember, HealthCondition
from app.models.user import User
from app.middleware.auth import get_current_user
from app.database import get_session
from app import crud

router = APIRouter()


def member_to_response(member) -> FamilyMember:
    """Convert SQLModel FamilyMember to Pydantic response"""
    from app.models.tables import Role, ConditionType
    import json
    
    conditions = [
        HealthCondition(
            type=cond.condition_type,
            enabled=cond.enabled,
            notes=cond.notes
        )
        for cond in member.conditions
    ]
    
    custom_restrictions = []
    if member.custom_restrictions:
        custom_restrictions = json.loads(member.custom_restrictions)
    
    preferences = None
    if member.preferences:
        preferences = json.loads(member.preferences)
    
    return FamilyMember(
        id=member.id,
        name=member.name,
        avatar=member.avatar,
        role=member.role,
        conditions=conditions,
        custom_restrictions=custom_restrictions,
        preferences=preferences
    )


@router.get("/profile", response_model=FamilyProfile)
async def get_profile(
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get the family profile with all members"""
    user_id = current_user.id if current_user else None
    members = await crud.get_all_members(session, user_id=user_id)
    
    response_members = [member_to_response(m) for m in members]
    return FamilyProfile(members=response_members)


@router.post("/profile", response_model=FamilyProfile)
async def create_profile(
    profile: FamilyProfile,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create or replace the entire family profile"""
    # This would typically clear and recreate, but for simplicity
    # we'll just return the existing profile structure
    return profile


@router.post("/member", response_model=FamilyMember)
async def add_member(
    member: FamilyMember,
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Add a family member"""
    user_id = current_user.id if current_user else None
    
    # Convert conditions to dict format for crud
    conditions = [
        {
            "type": cond.type,
            "enabled": cond.enabled,
            "notes": cond.notes
        }
        for cond in member.conditions
    ]
    
    new_member = await crud.add_member(
        session,
        member_id=member.id,
        name=member.name,
        avatar=member.avatar,
        role=member.role,
        conditions=conditions,
        custom_restrictions=member.custom_restrictions,
        preferences=member.preferences,
        user_id=user_id
    )
    
    return member_to_response(new_member)


@router.put("/member/{member_id}", response_model=FamilyMember)
async def update_member(
    member_id: str,
    member: FamilyMember,
    session: AsyncSession = Depends(get_session)
):
    """Update a family member"""
    # Convert conditions to dict format for crud
    conditions = [
        {
            "type": cond.type,
            "enabled": cond.enabled,
            "notes": cond.notes
        }
        for cond in member.conditions
    ]
    
    updated = await crud.update_member(
        session,
        member_id=member_id,
        name=member.name,
        avatar=member.avatar,
        role=member.role,
        conditions=conditions,
        custom_restrictions=member.custom_restrictions,
        preferences=member.preferences
    )
    
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return member_to_response(updated)


@router.delete("/member/{member_id}")
async def delete_member(
    member_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a family member"""
    deleted = await crud.delete_member(session, member_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member deleted successfully"}
