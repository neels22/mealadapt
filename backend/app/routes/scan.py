import base64
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
from app.services.ai_service import ai_service
from app import database as db
from app.models.family import FamilyProfile
from app.models.user import User
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/analyze")
async def analyze_ingredient_label(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user)
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
        
        # Get family profile from database (filtered by user if authenticated)
        user_id = current_user.id if current_user else None
        members = await db.get_all_members(user_id=user_id)
        family_profile = {"members": [m.model_dump() for m in members]}
        
        if not family_profile["members"]:
            raise HTTPException(
                status_code=400, 
                detail="Please add family members first before scanning ingredients"
            )
        
        # Encode to base64 for Gemini
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
        
        # Analyze with Gemini Vision
        result = ai_service.analyze_ingredient_image(
            image_data=image_base64,
            family_profile=family_profile,
            mime_type=file.content_type or "image/jpeg"
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")
