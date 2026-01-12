from fastapi import APIRouter, HTTPException
from app.models.recipe import RecipeRequest, RecipeAnalysis
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/analyze", response_model=RecipeAnalysis)
async def analyze_recipe(request: RecipeRequest):
    """Analyze a recipe against family dietary needs"""
    try:
        analysis = ai_service.analyze_recipe(
            recipe_text=request.recipe_text,
            family_profile=request.family_profile
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
