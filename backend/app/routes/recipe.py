from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import RecipeRequest, RecipeAnalysis
from app.models.user import User
from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app.middleware.rate_limit import check_ai_rate_limit
from app.database import get_session

router = APIRouter()


@router.post("/analyze", response_model=RecipeAnalysis)
async def analyze_recipe(
    request: RecipeRequest,
    user: User = Depends(check_ai_rate_limit("analyze_recipe")),
    session: AsyncSession = Depends(get_session)
):
    """Analyze a recipe against family dietary needs"""
    try:
        analysis = ai_service.analyze_recipe(
            recipe_text=request.recipe_text,
            family_profile=request.family_profile
        )
        return analysis
    except AIOutOfScope as e:
        raise HTTPException(status_code=400, detail={"error": "out_of_scope", "message": str(e)})
    except AIBlocked as e:
        raise HTTPException(status_code=422, detail={"error": "blocked", "message": str(e)})
    except AIInvalidOutput as e:
        raise HTTPException(status_code=502, detail={"error": "invalid_model_output", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
