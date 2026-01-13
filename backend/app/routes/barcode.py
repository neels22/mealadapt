"""
Barcode lookup and product analysis routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.barcode_service import barcode_service
from app.services.ai_service import ai_service, AIBlocked, AIOutOfScope, AIInvalidOutput
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import check_ai_rate_limit
from app.models.user import User
from app.database import get_session

router = APIRouter()


class NutritionInfo(BaseModel):
    energy_kcal: Optional[float] = None
    fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    sugars: Optional[float] = None
    fiber: Optional[float] = None
    proteins: Optional[float] = None
    salt: Optional[float] = None
    sodium: Optional[float] = None


class BarcodeProductResponse(BaseModel):
    barcode: str
    name: str
    brand: str
    quantity: str
    categories: List[str]
    ingredients_text: str
    ingredients_list: List[str]
    allergens: List[str]
    allergens_text: str
    nutrition: NutritionInfo
    nutriscore: Optional[str] = None
    nova_group: Optional[int] = None
    image_url: Optional[str] = None
    image_small_url: Optional[str] = None


class IngredientConcern(BaseModel):
    ingredient: str
    affected_members: List[str]
    reason: str
    severity: str


class BarcodeAnalysisResponse(BaseModel):
    product: BarcodeProductResponse
    overall_safety: str
    concerns: List[IngredientConcern]
    safe_for_all: List[str]
    recommendations: List[str]


@router.get("/{barcode}", response_model=BarcodeProductResponse)
async def lookup_barcode(
    barcode: str,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Look up a product by barcode"""
    product = await barcode_service.lookup_product(session, barcode)
    
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found. Make sure the barcode is correct."
        )
    
    return BarcodeProductResponse(
        barcode=product["barcode"],
        name=product["name"],
        brand=product["brand"],
        quantity=product.get("quantity", ""),
        categories=product.get("categories", []),
        ingredients_text=product.get("ingredients_text", ""),
        ingredients_list=product.get("ingredients_list", []),
        allergens=product.get("allergens", []),
        allergens_text=product.get("allergens_text", ""),
        nutrition=NutritionInfo(**product.get("nutrition", {})),
        nutriscore=product.get("nutriscore"),
        nova_group=product.get("nova_group"),
        image_url=product.get("image_url"),
        image_small_url=product.get("image_small_url")
    )


@router.post("/{barcode}/analyze", response_model=BarcodeAnalysisResponse)
async def analyze_barcode(
    barcode: str,
    family_profile: dict,
    user: User = Depends(check_ai_rate_limit("analyze_ingredients")),
    session: AsyncSession = Depends(get_session)
):
    """Analyze a product's ingredients against family profile"""
    # Get product info
    product = await barcode_service.lookup_product(session, barcode)
    
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Product not found"
        )
    
    # Get ingredients to analyze
    ingredients = product.get("ingredients_list", [])
    if not ingredients and product.get("ingredients_text"):
        # Fall back to splitting ingredients text
        ingredients = [i.strip() for i in product["ingredients_text"].split(",") if i.strip()]
    
    if not ingredients:
        # No ingredients to analyze
        return BarcodeAnalysisResponse(
            product=BarcodeProductResponse(
                barcode=product["barcode"],
                name=product["name"],
                brand=product["brand"],
                quantity=product.get("quantity", ""),
                categories=product.get("categories", []),
                ingredients_text=product.get("ingredients_text", ""),
                ingredients_list=product.get("ingredients_list", []),
                allergens=product.get("allergens", []),
                allergens_text=product.get("allergens_text", ""),
                nutrition=NutritionInfo(**product.get("nutrition", {})),
                nutriscore=product.get("nutriscore"),
                nova_group=product.get("nova_group"),
                image_url=product.get("image_url"),
                image_small_url=product.get("image_small_url")
            ),
            overall_safety="safe",
            concerns=[],
            safe_for_all=["No ingredients found to analyze"],
            recommendations=["Ingredient list not available for this product"]
        )
    
    try:
        # Use AI to analyze ingredients
        analysis = ai_service.analyze_ingredients(ingredients, family_profile)
        
        return BarcodeAnalysisResponse(
            product=BarcodeProductResponse(
                barcode=product["barcode"],
                name=product["name"],
                brand=product["brand"],
                quantity=product.get("quantity", ""),
                categories=product.get("categories", []),
                ingredients_text=product.get("ingredients_text", ""),
                ingredients_list=product.get("ingredients_list", []),
                allergens=product.get("allergens", []),
                allergens_text=product.get("allergens_text", ""),
                nutrition=NutritionInfo(**product.get("nutrition", {})),
                nutriscore=product.get("nutriscore"),
                nova_group=product.get("nova_group"),
                image_url=product.get("image_url"),
                image_small_url=product.get("image_small_url")
            ),
            overall_safety=analysis.get("overall_safety", "safe"),
            concerns=[
                IngredientConcern(**c) for c in analysis.get("concerns", [])
            ],
            safe_for_all=analysis.get("safe_for_all", []),
            recommendations=analysis.get("recommendations", [])
        )
    except AIOutOfScope as e:
        raise HTTPException(status_code=400, detail={"error": "out_of_scope", "message": str(e)})
    except AIBlocked as e:
        raise HTTPException(status_code=422, detail={"error": "blocked", "message": str(e)})
    except AIInvalidOutput as e:
        raise HTTPException(status_code=502, detail={"error": "invalid_model_output", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze product: {str(e)}"
        )
