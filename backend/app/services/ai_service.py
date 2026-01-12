import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.models.recipe import RecipeAnalysis

load_dotenv()


class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model_name = "gemini-2.0-flash"
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"✅ Gemini AI configured successfully with {self.model_name}")
            except Exception as e:
                print(f"⚠️ Failed to configure Gemini: {e}")
        else:
            print("⚠️ GEMINI_API_KEY not found in environment variables")
    
    def analyze_recipe(self, recipe_text: str, family_profile: dict) -> RecipeAnalysis:
        """
        Analyze a recipe against family dietary needs using Gemini
        """
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not configured. Please create a .env file in the backend directory with:\n"
                "GEMINI_API_KEY=your_api_key_here\n\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        if not self.client:
            raise ValueError("Gemini client not initialized. Check your API key.")
        
        prompt = self._build_analysis_prompt(recipe_text, family_profile)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4000,
                )
            )
            
            # Parse response
            response_text = response.text
            analysis_data = self._parse_ai_response(response_text)
            
            return RecipeAnalysis(**analysis_data)
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")
    
    def analyze_ingredient_image(self, image_data: bytes, family_profile: dict, mime_type: str = "image/jpeg") -> dict:
        """
        Analyze an ingredient label image using Gemini Vision
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured.")
        
        if not self.client:
            raise ValueError("Gemini client not initialized.")
        
        members_info = []
        for member in family_profile.get("members", []):
            conditions = [c["type"] for c in member.get("conditions", []) if c.get("enabled")]
            members_info.append({
                "name": member["name"],
                "role": member["role"],
                "conditions": conditions
            })
        
        prompt = f"""{self._get_system_context()}

Analyze this ingredient label image. Extract all ingredients you can read and check them against this family's dietary needs.

FAMILY MEMBERS:
{json.dumps(members_info, indent=2)}

Respond in JSON format (no markdown code blocks):
{{
  "product_name": "Product name if visible, otherwise 'Unknown Product'",
  "extracted_ingredients": ["ingredient1", "ingredient2", ...],
  "overall_safety": "safe|caution|unsafe",
  "concerns": [
    {{
      "ingredient": "ingredient name",
      "affected_members": ["member names who should avoid this"],
      "reason": "why it's a concern",
      "severity": "low|medium|high"
    }}
  ],
  "safe_for_all": ["ingredients safe for everyone"],
  "recommendations": ["what to do - buy it, avoid it, or use with caution"]
}}

If you cannot read the image clearly, still provide your best analysis with a note about image quality."""

        try:
            import base64
            image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            return self._parse_ai_response(response.text)
        except Exception as e:
            raise ValueError(f"Gemini Vision API error: {str(e)}")
    
    def suggest_recipes_from_ingredients(self, ingredients: list, family_profile: dict) -> dict:
        """
        Suggest recipes based on available ingredients and family dietary needs
        """
        if not self.api_key or not self.client:
            raise ValueError("Gemini not configured.")
        
        members_info = []
        for member in family_profile.get("members", []):
            conditions = [c["type"] for c in member.get("conditions", []) if c.get("enabled")]
            members_info.append({
                "name": member["name"],
                "role": member["role"],
                "conditions": conditions
            })
        
        prompt = f"""{self._get_system_context()}

Based on these available ingredients, suggest 3-5 recipes that would be suitable for this family.

AVAILABLE INGREDIENTS:
{', '.join(ingredients)}

FAMILY MEMBERS:
{json.dumps(members_info, indent=2)}

Respond in JSON format (no markdown code blocks):
{{
  "suggestions": [
    {{
      "name": "Recipe name",
      "description": "Brief description",
      "difficulty": "easy|medium|hard",
      "prep_time": "estimated time",
      "matching_ingredients": ["ingredients from pantry used"],
      "additional_ingredients": ["ingredients needed but not in pantry"],
      "safety_notes": "any dietary considerations for the family",
      "family_friendly_score": 1-5
    }}
  ],
  "tips": ["General cooking tips based on available ingredients"]
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=3000,
                )
            )
            
            return self._parse_ai_response(response.text)
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")
    
    def _get_system_context(self) -> str:
        return """You are a professional nutritionist and dietary expert specializing in family meal planning. Your role is to:

1. Analyze recipes against specific health conditions and dietary restrictions
2. Provide accurate, safe, and practical adaptations
3. Consider age-appropriate modifications (especially for babies and children)
4. Flag potential safety concerns clearly
5. Offer creative substitutions that maintain flavor and nutrition
6. Use evidence-based nutritional knowledge

Safety Guidelines:
- For babies (under 2 years): No honey, whole nuts, raw eggs, high-sodium foods, choking hazards, limit sugar
- For diabetes: Focus on low glycemic index, portion control, complex carbs over simple sugars
- For high uric acid: Avoid high-purine foods (organ meats, certain seafood, excessive red meat, beer)
- For hypertension: Limit sodium (under 1500mg/day), avoid processed foods, recommend herbs/spices over salt
- For heart disease: Low saturated fat, no trans fats, limit cholesterol
- For kidney disease: Monitor potassium, phosphorus, and protein intake
- For celiac/gluten-free: Absolutely no wheat, barley, rye, or cross-contaminated foods
- For lactose intolerance: Avoid dairy or suggest lactose-free alternatives
- For peanut allergy: Absolutely no peanuts or peanut products, watch for cross-contamination

Always respond in valid JSON format with the specified structure. Be practical and specific with adaptations."""
    
    def _build_analysis_prompt(self, recipe_text: str, family_profile: dict) -> str:
        members_info = []
        for member in family_profile.get("members", []):
            conditions = [c["type"] for c in member.get("conditions", []) if c.get("enabled")]
            members_info.append({
                "id": member["id"],
                "name": member["name"],
                "role": member["role"],
                "conditions": conditions,
                "restrictions": member.get("custom_restrictions", [])
            })
        
        return f"""{self._get_system_context()}

Analyze the following recipe for a family with diverse dietary needs.

RECIPE:
{recipe_text}

FAMILY MEMBERS:
{json.dumps(members_info, indent=2)}

Provide a comprehensive analysis in the following JSON format (respond ONLY with valid JSON, no markdown code blocks):
{{
  "dish_name": "Name of the dish",
  "base_description": "Brief description of the dish and its main components",
  "overall_safety": "safe|caution|unsafe",
  "member_verdicts": [
    {{
      "member_id": "id from family members",
      "member_name": "name",
      "verdict": "safe|needs_adaptation|not_recommended",
      "reasons": ["Specific reasons for this verdict"],
      "concerns": ["Any safety concerns - leave empty array if none"],
      "adaptations": {{
        "modifications": ["Modification instructions - leave empty if not needed"],
        "substitutions": [
          {{
            "original": "ingredient to replace",
            "replacement": "what to use instead",
            "reason": "why this substitution helps"
          }}
        ],
        "preparation_changes": ["Cooking method changes - leave empty if not needed"]
      }},
      "nutritional_notes": "Additional nutritional guidance specific to this person"
    }}
  ],
  "general_tips": ["Tips for cooking this dish for the whole family"]
}}

Be specific, practical, and safety-focused. Only respond with valid JSON, no explanation before or after."""
    
    def analyze_ingredients(self, ingredients: list, family_profile: dict) -> dict:
        """
        Analyze a list of ingredients against family dietary needs
        """
        if not self.api_key or not self.client:
            raise ValueError("Gemini not configured.")
        
        members_info = []
        for member in family_profile.get("members", []):
            conditions = [c["type"] for c in member.get("conditions", []) if c.get("enabled")]
            members_info.append({
                "name": member["name"],
                "role": member["role"],
                "conditions": conditions
            })
        
        prompt = f"""{self._get_system_context()}

Analyze these ingredients for family safety:

INGREDIENTS:
{', '.join(ingredients)}

FAMILY MEMBERS:
{json.dumps(members_info, indent=2)}

Respond in JSON format (no markdown code blocks):
{{
  "overall_safety": "safe|caution|unsafe",
  "concerns": [
    {{
      "ingredient": "ingredient name",
      "affected_members": ["member names who should avoid this"],
      "reason": "why it's a concern",
      "severity": "low|medium|high"
    }}
  ],
  "safe_for_all": ["ingredients safe for everyone"],
  "recommendations": ["what to do - buy it, avoid it, or use with caution"]
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2000,
                )
            )
            
            return self._parse_ai_response(response.text)
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")

    def extract_ingredients_from_recipes(self, recipes: list) -> list:
        """
        Extract ingredients with quantities from recipe texts for shopping list generation
        """
        if not self.api_key or not self.client:
            raise ValueError("Gemini not configured.")
        
        # Build recipe info
        recipe_texts = []
        for i, recipe in enumerate(recipes, 1):
            recipe_texts.append(f"Recipe {i}: {recipe.get('dish_name', 'Unknown')}\n{recipe.get('recipe_text', '')}")
        
        prompt = f"""{self._get_system_context()}

Extract all ingredients needed for these recipes and combine them into a shopping list. 
Merge similar ingredients and sum up quantities where possible.

RECIPES:
{chr(10).join(recipe_texts)}

Respond in JSON format (no markdown code blocks):
{{
  "ingredients": [
    {{
      "ingredient": "ingredient name (standardized, e.g., 'chicken breast' not 'chicken')",
      "quantity": "combined quantity with unit (e.g., '2 lbs', '3 cups')",
      "category": "produce|dairy|meat|seafood|pantry|bakery|frozen|beverages|other"
    }}
  ]
}}

Guidelines:
- Combine similar ingredients (e.g., 2 cups + 1 cup flour = 3 cups flour)
- Use standard grocery categories
- Be specific with ingredient names
- Include all necessary ingredients, even common ones like salt and oil"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=3000,
                )
            )
            
            result = self._parse_ai_response(response.text)
            return result.get("ingredients", [])
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")
    
    def _parse_ai_response(self, response_text: str) -> dict:
        """Parse AI response and extract JSON"""
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {str(e)}\nResponse was: {response_text[:500]}")


# Singleton instance
ai_service = AIService()
