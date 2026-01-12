"""
Barcode lookup service using Open Food Facts API.
Updated to work with SQLModel and async sessions.
"""
import httpx
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud


class BarcodeService:
    """Service for looking up product information by barcode"""
    
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v2/product"
    
    async def lookup_product(
        self,
        session: AsyncSession,
        barcode: str
    ) -> Optional[dict]:
        """
        Look up a product by barcode using Open Food Facts API.
        Results are cached in the database to reduce API calls.
        """
        # Check cache first
        cached = await crud.get_barcode_cache(session, barcode)
        if cached:
            return cached.get_product_data()
        
        # Fetch from Open Food Facts
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.OPEN_FOOD_FACTS_URL}/{barcode}.json"
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                
                if data.get("status") != 1:
                    return None
                
                product = data.get("product", {})
                
                # Extract relevant information
                product_info = {
                    "barcode": barcode,
                    "name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
                    "brand": product.get("brands", "Unknown Brand"),
                    "quantity": product.get("quantity", ""),
                    "categories": product.get("categories", "").split(",") if product.get("categories") else [],
                    "ingredients_text": product.get("ingredients_text") or product.get("ingredients_text_en") or "",
                    "ingredients_list": [
                        ing.get("text", "") 
                        for ing in product.get("ingredients", [])
                        if ing.get("text")
                    ],
                    "allergens": product.get("allergens_tags", []),
                    "allergens_text": product.get("allergens", ""),
                    "nutrition": {
                        "energy_kcal": product.get("nutriments", {}).get("energy-kcal_100g"),
                        "fat": product.get("nutriments", {}).get("fat_100g"),
                        "saturated_fat": product.get("nutriments", {}).get("saturated-fat_100g"),
                        "carbohydrates": product.get("nutriments", {}).get("carbohydrates_100g"),
                        "sugars": product.get("nutriments", {}).get("sugars_100g"),
                        "fiber": product.get("nutriments", {}).get("fiber_100g"),
                        "proteins": product.get("nutriments", {}).get("proteins_100g"),
                        "salt": product.get("nutriments", {}).get("salt_100g"),
                        "sodium": product.get("nutriments", {}).get("sodium_100g"),
                    },
                    "nutriscore": product.get("nutriscore_grade"),
                    "nova_group": product.get("nova_group"),
                    "image_url": product.get("image_front_url") or product.get("image_url"),
                    "image_small_url": product.get("image_front_small_url"),
                }
                
                # Cache the result
                await crud.set_barcode_cache(session, barcode, product_info)
                
                return product_info
                
        except Exception as e:
            print(f"Error fetching barcode {barcode}: {e}")
            return None


# Singleton instance
barcode_service = BarcodeService()
