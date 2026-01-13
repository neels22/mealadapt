"""
Image scanning and ingredient label analysis routes.
"""
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app import crud
from app.models.family import FamilyProfile
from app.models.user import User
from app.middleware.rate_limit import check_ai_rate_limit
from app.database import get_session

router = APIRouter()


def member_to_dict(member) -> dict:
    """Convert SQLModel FamilyMember to dict for AI service"""
    conditions = [
        {
            "type": cond.condition_type.value,
            "enabled": cond.enabled,
            "notes": cond.notes
        }
        for cond in member.conditions
    ]
    
    custom_restrictions = []
    if member.custom_restrictions:
        custom_restrictions = json.loads(member.custom_restrictions)
    
    preferences = None
    if member.preferences:
        preferences = json.loads(member.preferences)
    
    return {
        "id": member.id,
        "name": member.name,
        "avatar": member.avatar,
        "role": member.role.value,
        "conditions": conditions,
        "custom_restrictions": custom_restrictions,
        "preferences": preferences
    }


@router.post("/analyze")
async def analyze_ingredient_label(
    file: UploadFile = File(...),
    user: User = Depends(check_ai_rate_limit("analyze_ingredient_image")),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze an ingredient label image for family safety
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Get family profile from database (filtered by user)
        members = await crud.get_all_members(session, user_id=user.id)
        family_profile = {"members": [member_to_dict(m) for m in members]}
        
        if not family_profile["members"]:
            raise HTTPException(
                status_code=400, 
                detail="Please add family members first before scanning ingredients"
            )
        
        # Analyze with Gemini Vision
        result = ai_service.analyze_ingredient_image(
            image_data=image_data,
            family_profile=family_profile,
            mime_type=file.content_type or "image/jpeg"
        )
        
        return result
    except AIOutOfScope as e:
        raise HTTPException(status_code=400, detail={"error": "out_of_scope", "message": str(e)})
    except AIBlocked as e:
        raise HTTPException(status_code=422, detail={"error": "blocked", "message": str(e)})
    except AIInvalidOutput as e:
        raise HTTPException(status_code=502, detail={"error": "invalid_model_output", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")
