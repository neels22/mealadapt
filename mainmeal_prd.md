# MainMeal - Complete Project Requirements Document

## Table of Contents
1. [Project Setup](#1-project-setup)
2. [Backend Development (FastAPI)](#2-backend-development-fastapi)
3. [Frontend Development (Next.js)](#3-frontend-development-nextjs)
4. [AI Integration](#4-ai-integration)
5. [Feature Implementation](#5-feature-implementation)
6. [Testing & Deployment](#6-testing--deployment)

---

## 1. Project Setup

### 1.1 Initialize Git Repository
```bash
# Create project directory
mkdir mainmeal
cd mainmeal
git init
git branch -M main

# Create .gitignore
echo "node_modules/
.env
.env.local
__pycache__/
*.pyc
.next/
.vercel/
venv/" > .gitignore
```

### 1.2 Backend Setup (FastAPI)
```bash
# Create backend directory
mkdir backend
cd backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.109.0
uvicorn[standard]==0.27.0
anthropic==0.18.1
pydantic==2.6.0
python-dotenv==1.0.1
python-multipart==0.0.6
pytesseract==0.3.10
Pillow==10.2.0
cors==1.0.1
EOF

# Install dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p app/{models,routes,services,utils}
touch app/__init__.py
touch app/main.py
touch app/models/__init__.py
touch app/routes/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
```

### 1.3 Frontend Setup (Next.js)
```bash
# Navigate back to root
cd ..

# Create Next.js app with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

cd frontend

# Install additional dependencies
npm install lucide-react
npm install react-webcam  # For camera feature
npm install tesseract.js   # For OCR (client-side option)
```

### 1.4 Environment Configuration

**Backend (.env)**
```env
# Create backend/.env
ANTHROPIC_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
PORT=8000
ENVIRONMENT=development
```

**Frontend (.env.local)**
```env
# Create frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

---

## 2. Backend Development (FastAPI)

### 2.1 Main Application Setup

**File: `backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes import family, recipe, pantry, scan

load_dotenv()

app = FastAPI(
    title="MainMeal API",
    description="AI-powered recipe adaptation for family dietary needs",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(family.router, prefix="/api/family", tags=["Family"])
app.include_router(recipe.router, prefix="/api/recipe", tags=["Recipe"])
app.include_router(pantry.router, prefix="/api/pantry", tags=["Pantry"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])

@app.get("/")
async def root():
    return {"message": "MainMeal API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2.2 Data Models

**File: `backend/app/models/family.py`**
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Role(str, Enum):
    ADULT = "Adult"
    CHILD = "Child"
    BABY = "Baby"

class ConditionType(str, Enum):
    DIABETES = "Diabetes"
    HIGH_URIC_ACID = "High Uric Acid"
    HYPERTENSION = "Hypertension"
    HEART_DISEASE = "Heart Disease"
    KIDNEY_DISEASE = "Kidney Disease"
    CELIAC = "Celiac (Gluten-Free)"
    LACTOSE_INTOLERANCE = "Lactose Intolerance"
    PEANUT_ALLERGY = "Peanut Allergy"

class HealthCondition(BaseModel):
    type: ConditionType
    enabled: bool = False
    notes: Optional[str] = None

class FamilyMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    avatar: str = "😊"
    role: Role = Role.ADULT
    conditions: List[HealthCondition] = []
    custom_restrictions: List[str] = []
    preferences: Optional[dict] = None

class FamilyProfile(BaseModel):
    members: List[FamilyMember] = []

import uuid
```

**File: `backend/app/models/recipe.py`**
```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class VerdictType(str, Enum):
    SAFE = "safe"
    NEEDS_ADAPTATION = "needs_adaptation"
    NOT_RECOMMENDED = "not_recommended"

class Substitution(BaseModel):
    original: str
    replacement: str
    reason: str

class Adaptation(BaseModel):
    modifications: List[str] = []
    substitutions: List[Substitution] = []
    preparation_changes: List[str] = []

class MemberVerdict(BaseModel):
    member_id: str
    member_name: str
    verdict: VerdictType
    reasons: List[str] = []
    concerns: List[str] = []
    adaptations: Optional[Adaptation] = None
    nutritional_notes: Optional[str] = None

class RecipeAnalysis(BaseModel):
    dish_name: str
    base_description: str
    overall_safety: str
    member_verdicts: List[MemberVerdict]
    general_tips: List[str] = []

class RecipeRequest(BaseModel):
    recipe_text: str
    family_profile: dict
```

### 2.3 AI Service

**File: `backend/app/services/ai_service.py`**
```python
import os
import json
from anthropic import Anthropic
from app.models.recipe import RecipeAnalysis, MemberVerdict

class AIService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_recipe(self, recipe_text: str, family_profile: dict) -> RecipeAnalysis:
        """
        Analyze a recipe against family dietary needs
        """
        prompt = self._build_analysis_prompt(recipe_text, family_profile)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,
            system=self._get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response
        response_text = response.content[0].text
        analysis_data = self._parse_ai_response(response_text)
        
        return RecipeAnalysis(**analysis_data)
    
    def _get_system_prompt(self) -> str:
        return """You are a professional nutritionist and dietary expert specializing in family meal planning. Your role is to:

1. Analyze recipes against specific health conditions and dietary restrictions
2. Provide accurate, safe, and practical adaptations
3. Consider age-appropriate modifications (especially for babies and children)
4. Flag potential safety concerns clearly
5. Offer creative substitutions that maintain flavor and nutrition
6. Use evidence-based nutritional knowledge

Safety Guidelines:
- For babies (under 2 years): No honey, whole nuts, raw eggs, high-sodium foods, choking hazards
- For diabetes: Focus on low glycemic index, portion control, complex carbs
- For high uric acid: Avoid high-purine foods (organ meats, certain seafood, excessive red meat)
- For hypertension: Limit sodium, recommend herbs/spices
- For allergies: Absolutely no cross-contamination risks

Always respond in valid JSON format with the specified structure."""
    
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
        
        return f"""Analyze the following recipe for a family with diverse dietary needs.

RECIPE:
{recipe_text}

FAMILY MEMBERS:
{json.dumps(members_info, indent=2)}

Provide a comprehensive analysis in the following JSON format:
{{
  "dish_name": "Name of the dish",
  "base_description": "Brief description of the dish and its main components",
  "overall_safety": "safe|caution|unsafe",
  "member_verdicts": [
    {{
      "member_id": "id",
      "member_name": "name",
      "verdict": "safe|needs_adaptation|not_recommended",
      "reasons": ["Specific reasons for this verdict"],
      "concerns": ["Any safety concerns"],
      "adaptations": {{
        "modifications": ["Modification instructions"],
        "substitutions": [
          {{
            "original": "ingredient",
            "replacement": "alternative",
            "reason": "why this substitution"
          }}
        ],
        "preparation_changes": ["Cooking method changes"]
      }},
      "nutritional_notes": "Additional nutritional guidance"
    }}
  ],
  "general_tips": ["Tips for cooking this dish for the whole family"]
}}

Be specific, practical, and safety-focused. Only respond with valid JSON."""
    
    def _parse_ai_response(self, response_text: str) -> dict:
        """Parse AI response and extract JSON"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {str(e)}")
    
    def analyze_ingredients(self, ingredients: List[str], family_profile: dict) -> dict:
        """
        Analyze a list of ingredients for safety
        """
        prompt = f"""Analyze these ingredients for family safety:

INGREDIENTS:
{', '.join(ingredients)}

FAMILY MEMBERS:
{json.dumps([{
    'name': m['name'],
    'role': m['role'],
    'conditions': [c['type'] for c in m.get('conditions', []) if c.get('enabled')]
} for m in family_profile.get('members', [])], indent=2)}

Respond in JSON format:
{{
  "overall_safety": "safe|caution|unsafe",
  "concerns": [
    {{
      "ingredient": "ingredient name",
      "affected_members": ["member names"],
      "reason": "why it's a concern",
      "severity": "low|medium|high"
    }}
  ],
  "safe_for_all": ["ingredients safe for everyone"],
  "recommendations": ["general recommendations"]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.3,
            system=self._get_system_prompt(),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_ai_response(response.content[0].text)

ai_service = AIService()
```

### 2.4 API Routes

**File: `backend/app/routes/family.py`**
```python
from fastapi import APIRouter, HTTPException
from app.models.family import FamilyProfile, FamilyMember
from typing import List

router = APIRouter()

# In-memory storage (replace with database in production)
family_profiles = {}

@router.post("/profile", response_model=FamilyProfile)
async def create_profile(profile: FamilyProfile):
    """Create a new family profile"""
    profile_id = "default"  # For MVP, use single profile
    family_profiles[profile_id] = profile
    return profile

@router.get("/profile", response_model=FamilyProfile)
async def get_profile():
    """Get the family profile"""
    profile_id = "default"
    if profile_id not in family_profiles:
        return FamilyProfile(members=[])
    return family_profiles[profile_id]

@router.post("/member", response_model=FamilyMember)
async def add_member(member: FamilyMember):
    """Add a family member"""
    profile_id = "default"
    if profile_id not in family_profiles:
        family_profiles[profile_id] = FamilyProfile(members=[])
    
    family_profiles[profile_id].members.append(member)
    return member

@router.put("/member/{member_id}", response_model=FamilyMember)
async def update_member(member_id: str, member: FamilyMember):
    """Update a family member"""
    profile_id = "default"
    if profile_id not in family_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    for i, m in enumerate(family_profiles[profile_id].members):
        if m.id == member_id:
            family_profiles[profile_id].members[i] = member
            return member
    
    raise HTTPException(status_code=404, detail="Member not found")

@router.delete("/member/{member_id}")
async def delete_member(member_id: str):
    """Delete a family member"""
    profile_id = "default"
    if profile_id not in family_profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    family_profiles[profile_id].members = [
        m for m in family_profiles[profile_id].members if m.id != member_id
    ]
    return {"message": "Member deleted successfully"}
```

**File: `backend/app/routes/recipe.py`**
```python
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

@router.post("/adapt")
async def adapt_recipe(request: RecipeRequest):
    """Get adaptations for a specific member"""
    try:
        analysis = ai_service.analyze_recipe(
            recipe_text=request.recipe_text,
            family_profile=request.family_profile
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**File: `backend/app/routes/scan.py`**
```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ai_service import ai_service
from typing import List
import pytesseract
from PIL import Image
import io

router = APIRouter()

@router.post("/ingredients")
async def scan_ingredients(file: UploadFile = File(...)):
    """Scan ingredient label from image"""
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Extract ingredients (basic parsing)
        ingredients = [
            line.strip() 
            for line in text.split('\n') 
            if line.strip() and not line.startswith(('Ingredients', 'INGREDIENTS'))
        ]
        
        return {
            "raw_text": text,
            "ingredients": ingredients
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

@router.post("/analyze-ingredients")
async def analyze_ingredients(ingredients: List[str], family_profile: dict):
    """Analyze ingredients for family safety"""
    try:
        analysis = ai_service.analyze_ingredients(ingredients, family_profile)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**File: `backend/app/routes/pantry.py`**
```python
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()

class PantryRequest(BaseModel):
    ingredients: List[str]

class RecipeSuggestion(BaseModel):
    name: str
    description: str
    matching_ingredients: List[str]
    additional_ingredients: List[str]

@router.post("/suggest-recipes")
async def suggest_recipes(request: PantryRequest):
    """Suggest recipes based on pantry ingredients"""
    # This would integrate with a recipe database or AI generation
    # For MVP, return mock data or use AI to generate suggestions
    return {
        "suggestions": [
            {
                "name": "Simple Stir Fry",
                "description": "Quick and healthy stir fry",
                "matching_ingredients": request.ingredients[:3],
                "additional_ingredients": ["soy sauce", "garlic"]
            }
        ]
    }
```

### 2.5 Run Backend

**File: `backend/run.py`**
```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

**Command to run:**
```bash
cd backend
python run.py
```

---

## 3. Frontend Development (Next.js)

### 3.1 Project Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── api/
│   ├── scan/
│   │   └── page.tsx
│   ├── adapt/
│   │   └── page.tsx
│   ├── pantry/
│   │   └── page.tsx
├── components/
│   ├── FamilyProfile.tsx
│   ├── MemberCard.tsx
│   ├── RecipeAnalysisDisplay.tsx
│   ├── SafetyBadge.tsx
│   ├── CameraCapture.tsx
├── lib/
│   ├── api.ts
│   ├── types.ts
│   ├── utils.ts
├── public/
└── package.json
```

### 3.2 Type Definitions

**File: `frontend/lib/types.ts`**
```typescript
export enum Role {
  ADULT = "Adult",
  CHILD = "Child",
  BABY = "Baby"
}

export enum ConditionType {
  DIABETES = "Diabetes",
  HIGH_URIC_ACID = "High Uric Acid",
  HYPERTENSION = "Hypertension",
  HEART_DISEASE = "Heart Disease",
  KIDNEY_DISEASE = "Kidney Disease",
  CELIAC = "Celiac (Gluten-Free)",
  LACTOSE_INTOLERANCE = "Lactose Intolerance",
  PEANUT_ALLERGY = "Peanut Allergy"
}

export interface HealthCondition {
  type: ConditionType;
  enabled: boolean;
  notes?: string;
}

export interface FamilyMember {
  id: string;
  name: string;
  avatar: string;
  role: Role;
  conditions: HealthCondition[];
  custom_restrictions: string[];
  preferences?: any;
}

export interface FamilyProfile {
  members: FamilyMember[];
}

export enum VerdictType {
  SAFE = "safe",
  NEEDS_ADAPTATION = "needs_adaptation",
  NOT_RECOMMENDED = "not_recommended"
}

export interface Substitution {
  original: string;
  replacement: string;
  reason: string;
}

export interface Adaptation {
  modifications: string[];
  substitutions: Substitution[];
  preparation_changes: string[];
}

export interface MemberVerdict {
  member_id: string;
  member_name: string;
  verdict: VerdictType;
  reasons: string[];
  concerns: string[];
  adaptations?: Adaptation;
  nutritional_notes?: string;
}

export interface RecipeAnalysis {
  dish_name: string;
  base_description: string;
  overall_safety: string;
  member_verdicts: MemberVerdict[];
  general_tips: string[];
}
```

### 3.3 API Client

**File: `frontend/lib/api.ts`**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  // Family endpoints
  async getFamilyProfile() {
    const res = await fetch(`${API_URL}/api/family/profile`);
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async createFamilyProfile(profile: any) {
    const res = await fetch(`${API_URL}/api/family/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    });
    if (!res.ok) throw new Error('Failed to create profile');
    return res.json();
  },

  async addMember(member: any) {
    const res = await fetch(`${API_URL}/api/family/member`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(member)
    });
    if (!res.ok) throw new Error('Failed to add member');
    return res.json();
  },

  async updateMember(memberId: string, member: any) {
    const res = await fetch(`${API_URL}/api/family/member/${memberId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(member)
    });
    if (!res.ok) throw new Error('Failed to update member');
    return res.json();
  },

  async deleteMember(memberId: string) {
    const res = await fetch(`${API_URL}/api/family/member/${memberId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete member');
    return res.json();
  },

  // Recipe endpoints
  async analyzeRecipe(recipeText: string, familyProfile: any) {
    const res = await fetch(`${API_URL}/api/recipe/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipe_text: recipeText,
        family_profile: familyProfile
      })
    });
    if (!res.ok) throw new Error('Failed to analyze recipe');
    return res.json();
  },

  // Scan endpoints
  async scanIngredients(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_URL}/api/scan/ingredients`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Failed to scan ingredients');
    return res.json();
  },

  async analyzeIngredients(ingredients: string[], familyProfile: any) {
    const res = await fetch(`${API_URL}/api/scan/analyze-ingredients`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ingredients,
        family_profile: familyProfile
      })
    });
    if (!res.ok) throw new Error('Failed to analyze ingredients');
    return res.json();
  },

  // Pantry endpoints
  async suggestRecipes(ingredients: string[]) {
    const res = await fetch(`${API_URL}/api/pantry/suggest-recipes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ingredients })
    });
    if (!res.ok) throw new Error('Failed to suggest recipes');
    return res.json();
  }
};
```

### 3.4 Global Styles

**File: `frontend/app/globals.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #F5EBE0;
  --card-bg: #FFFFFF;
  --text-primary: #6B5446;
  --text-secondary: #8B7566;
  --accent-green: #A8D5BA;
  --accent-blue: #B8D4E8;
  --accent-yellow: #F9E5A8;
  --accent-red: #E8A8A8;
  --accent-pink: #F0C8D0;
}

body {
  background-color: var(--background);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, sans-serif;
}

.card {
  @apply bg-white rounded-2xl shadow-sm p-6;
}

.btn-primary {
  @apply bg-[#A8D5BA] hover:bg-[#98C5AA] text-[#6B5446] font-medium px-6 py-3 rounded-full transition-colors;
}

.btn-secondary {
  @apply bg-[#F5EBE0] hover:bg-[#E5DBD0] text-[#6B5446] font-medium px-6 py-3 rounded-full transition-colors;
}

.badge {
  @apply px-3 py-1 rounded-full text-sm font-medium;
}

.badge-diabetes {
  @apply bg-[#A8D5BA] text-[#2A5A3A];
}

.badge-hypertension {
  @apply bg-[#F0C8D0] text-[#8A3A50];
}

.badge-baby {
  @apply bg-[#F9E5A8] text-[#8A7A2A];
}

.badge-allergy {
  @apply bg-[#E8A8A8] text-[#8A2A2A];
}

.badge-celiac {
  @apply bg-[#B8D4E8] text-[#2A4A6A];
}
```

### 3.5 Main Layout

**File: `frontend/app/layout.tsx`**
```typescript
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MainMeal - One kitchen. Many needs.',
  description: 'AI-powered recipe adaptation for family dietary needs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {children}
        </div>
      </body>
    </html>
  )
}
```

### 3.6 Home Page

**File: `frontend/app/page.tsx`**
```typescript
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Cookie, Camera } from 'lucide-react';
import FamilyProfile from '@/components/FamilyProfile';
import { api } from '@/lib/api';
import { FamilyProfile as FamilyProfileType } from '@/lib/types';

export default function Home() {
  const [profile, setProfile] = useState<FamilyProfileType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await api.getFamilyProfile();
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = () => {
    loadProfile();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center py-8">
        <h1 className="text-5xl font-bold text-[#6B5446] mb-2">
          MainMeal
        </h1>
        <p className="text-[#8B7566] text-lg">
          One kitchen. Many needs.
        </p>
      </div>

      {/* Scan Ingredient Label */}
      <Link href="/scan">
        <div className="card hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold mb-1">
                Scan ingredient label
              </h3>
              <p className="text-[#8B7566] text-sm">
                Check if it's safe for everyone
              </p>
            </div>
            <Camera className="w-6 h-6 text-[#8B7566]" />
          </div>
        </div>
      </Link>

      {/* Action Cards */}
      <div className="grid grid-cols-2 gap-4">
        <Link href="/adapt">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <Search className="w-8 h-8 mb-2 text-[#6B5446]" />
            <h3 className="font-semibold">Adapt Recipe</h3>
          </div>
        </Link>

        <Link href="/pantry">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <Cookie className="w-8 h-8 mb-2 text-[#6B5446]" />
            <h3 className="font-semibold">My Pantry</h3>
          </div>
        </Link>
      </div>

      {/* Family Profile */}
      {!loading && (
        <FamilyProfile 
          profile={profile || { members: [] }} 
          onUpdate={handleProfileUpdate}
        />
      )}

      {/* Safety Filter Badges */}
      <div className="flex gap-3 justify-center flex-wrap">
        <div className="badge badge-diabetes">✓ Diabetic-Safe</div>
        <div className="badge badge-celiac">🧪 Low-Sodium</div>
        <div className="badge badge-baby">☀️ Baby-Safe</div>
      </div>
    </div>
  );
}
```

---

## 4. AI Integration

### 4.1 Prompt Engineering Guidelines

**System Prompt Template** (already in ai_service.py):
- Role definition: Professional nutritionist
- Safety-first approach
- Evidence-based recommendations
- JSON response format
- Specific safety guidelines per condition

**Best Practices:**
1. Always include family profile context
2. Request structured JSON responses
3. Specify safety priorities
4. Include fallback handling
5. Temperature: 0.3 for consistency
6. Max tokens: 4000 for detailed responses

### 4.2 Response Validation

Add validation layer in AI service:

```python
def validate_analysis(analysis: dict) -> bool:
    """Validate AI response structure"""
    required_fields = ['dish_name', 'base_description', 'member_verdicts']
    
    if not all(field in analysis for field in required_fields):
        return False
    
    for verdict in analysis.get('member_verdicts', []):
        if verdict.get('verdict') not in ['safe', 'needs_adaptation', 'not_recommended']:
            return False
    
    return True
```

---

## 5. Feature Implementation

### 5.1 Family Profile Component

**File: `frontend/components/FamilyProfile.tsx`**
```typescript
'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Plus } from 'lucide-react';
import MemberCard from './MemberCard';
import AddMemberModal from './AddMemberModal';
import { FamilyProfile as FamilyProfileType, FamilyMember } from '@/lib/types';
import { api } from '@/lib/api';

interface Props {
  profile: FamilyProfileType;
  onUpdate: () => void;
}

export default function FamilyProfile({ profile, onUpdate }: Props) {
  const [showAddModal, setShowAddModal] = useState(false);

  const handleAddMember = async (member: FamilyMember) => {
    try {
      await api.addMember(member);
      onUpdate();
      setShowAddModal(false);
    } catch (error) {
      console.error('Failed to add member:', error);
    }
  };

  const handleUpdateMember = async (member: FamilyMember) => {
    try {
      await api.updateMember(member.id, member);
      onUpdate();
    } catch (error) {
      console.error('Failed to update member:', error);
    }
  };

  const handleDeleteMember = async (memberId: string) => {
    try {
      await api.deleteMember(memberId);
      onUpdate();
    } catch (error) {
      console.error('Failed to delete member:', error);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold flex items-center gap-2">
          👨‍👩‍👧‍👦 My Family
        </h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-[#A8D5BA] hover:bg-[#98C5AA] text-[#6B5446] px-4 py-2 rounded-full text-sm font-medium transition-colors"
        >
          + Add
        </button>
      </div>

      <div className="space-y-3">
        {profile.members.map((member) => (
          <MemberCard
            key={member.id}
            member={member}
            onUpdate={handleUpdateMember}
            onDelete={handleDeleteMember}
          />
        ))}
      </div>

      {showAddModal && (
        <AddMemberModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddMember}
        />
      )}
    </div>
  );
}
```

### 5.2 Member Card Component

**File: `frontend/components/MemberCard.tsx`**
```typescript
'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { FamilyMember, ConditionType, Role } from '@/lib/types';

interface Props {
  member: FamilyMember;
  onUpdate: (member: FamilyMember) => void;
  onDelete: (memberId: string) => void;
}

const CONDITION_COLORS: Record<ConditionType, string> = {
  [ConditionType.DIABETES]: 'badge-diabetes',
  [ConditionType.HYPERTENSION]: 'badge-hypertension',
  [ConditionType.HIGH_URIC_ACID]: 'badge-celiac',
  [ConditionType.PEANUT_ALLERGY]: 'badge-allergy',
  [ConditionType.HEART_DISEASE]: 'badge-hypertension',
  [ConditionType.KIDNEY_DISEASE]: 'badge-hypertension',
  [ConditionType.CELIAC]: 'badge-celiac',
  [ConditionType.LACTOSE_INTOLERANCE]: 'badge-baby',
};

export default function MemberCard({ member, onUpdate, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);

  const activeConditions = member.conditions.filter(c => c.enabled);

  const toggleCondition = (conditionType: ConditionType) => {
    const updated = {
      ...member,
      conditions: member.conditions.map(c =>
        c.type === conditionType ? { ...c, enabled: !c.enabled } : c
      )
    };
    onUpdate(updated);
  };

  return (
    <div className="bg-[#F5EBE0] rounded-xl p-4">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div className="text-3xl">{member.avatar}</div>
          <div>
            <h3 className="font-semibold">{member.name}</h3>
            <div className="flex gap-2 flex-wrap mt-1">
              {activeConditions.map(c => (
                <span
                  key={c.type}
                  className={`badge ${CONDITION_COLORS[c.type]}`}
                >
                  {c.type}
                </span>
              ))}
            </div>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-[#8B7566]" />
        ) : (
          <ChevronDown className="w-5 h-5 text-[#8B7566]" />
        )}
      </div>

      {expanded && (
        <div className="mt-4 space-y-4 border-t border-[#E5DBD0] pt-4">
          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">Role</label>
            <div className="flex gap-2">
              {Object.values(Role).map(role => (
                <button
                  key={role}
                  onClick={() => onUpdate({ ...member, role })}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    member.role === role
                      ? 'bg-[#F0C8D0] text-[#6B5446]'
                      : 'bg-white text-[#8B7566] hover:bg-[#F5EBE0]'
                  }`}
                >
                  {role === Role.ADULT && '🧑'} 
                  {role === Role.CHILD && '👦'}
                  {role === Role.BABY && '👶'}
                  {' '}{role}
                </button>
              ))}
            </div>
          </div>

          {/* Conditions */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Chronic Conditions
            </label>
            <div className="space-y-2">
              {Object.values(ConditionType).map(conditionType => {
                const condition = member.conditions.find(c => c.type === conditionType);
                const enabled = condition?.enabled || false;

                return (
                  <div
                    key={conditionType}
                    className="flex items-center justify-between p-3 bg-white rounded-lg"
                  >
                    <span className="text-sm">{conditionType}</span>
                    <button
                      onClick={() => toggleCondition(conditionType)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        enabled ? 'bg-[#A8D5BA]' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 bg-white rounded-full transform transition-transform ${
                          enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Delete Button */}
          <button
            onClick={() => {
              if (confirm(`Remove ${member.name} from family?`)) {
                onDelete(member.id);
              }
            }}
            className="w-full bg-[#E8A8A8] hover:bg-[#D89898] text-[#8A2A2A] py-2 rounded-full font-medium transition-colors"
          >
            Remove {member.name}
          </button>
        </div>
      )}
    </div>
  );
}
```

### 5.3 Recipe Adaptation Page

**File: `frontend/app/adapt/page.tsx`**
```typescript
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import RecipeAnalysisDisplay from '@/components/RecipeAnalysisDisplay';
import { RecipeAnalysis, FamilyProfile } from '@/lib/types';

export default function AdaptRecipe() {
  const [recipe, setRecipe] = useState('');
  const [analysis, setAnalysis] = useState<RecipeAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<FamilyProfile | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await api.getFamilyProfile();
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!recipe.trim() || !profile) return;

    setLoading(true);
    try {
      const result = await api.analyzeRecipe(recipe, profile);
      setAnalysis(result);
    } catch (error) {
      console.error('Failed to analyze recipe:', error);
      alert('Failed to analyze recipe. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSurprise = () => {
    const samples = [
      'Spaghetti Carbonara with eggs, bacon, parmesan cheese, and black pepper',
      'Chicken stir fry with soy sauce, garlic, ginger, vegetables, and rice',
      'Tiramisu with ladyfingers, mascarpone, espresso, cocoa powder, and eggs',
    ];
    setRecipe(samples[Math.floor(Math.random() * samples.length)]);
  };

  return (
    <div className="space-y-6">
      <Link href="/" className="inline-flex items-center gap-2 text-[#8B7566] hover:text-[#6B5446]">
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>

      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Adapt a Recipe</h1>
        <p className="text-[#8B7566]">Paste a recipe or type a dish name</p>
      </div>

      <div className="card">
        <label className="block text-sm font-medium mb-2">
          Recipe or dish name
        </label>
        <textarea
          value={recipe}
          onChange={(e) => setRecipe(e.target.value)}
          placeholder="Type a dish name (e.g., 'chicken curry', 'pasta carbonara', 'beef stir fry') or paste a full recipe..."
          className="w-full h-64 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#A8D5BA] resize-none"
        />
        
        <div className="mt-4 flex gap-3">
          <button
            onClick={handleSurprise}
            className="btn-secondary flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Surprise Me
          </button>
          <button
            onClick={handleAnalyze}
            disabled={loading || !recipe.trim() || !profile?.members.length}
            className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : '🔍 Check for My Family'}
          </button>
        </div>

        {!profile?.members.length && (
          <p className="mt-3 text-sm text-[#E8A8A8]">
            Please add family members first
          </p>
        )}

        <p className="mt-4 text-xs text-[#8B7566] text-center">
          Works with dish names or full recipes
        </p>
      </div>

      {analysis && (
        <RecipeAnalysisDisplay analysis={analysis} />
      )}

      <div className="text-center text-xs text-[#8B7566]">
        ✨ Powered by LLM
      </div>
    </div>
  );
}
```

### 5.4 Recipe Analysis Display Component

**File: `frontend/components/RecipeAnalysisDisplay.tsx`**
```typescript
import { RecipeAnalysis, VerdictType } from '@/lib/types';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface Props {
  analysis: RecipeAnalysis;
}

const VERDICT_CONFIG = {
  [VerdictType.SAFE]: {
    icon: CheckCircle2,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    label: 'Safe'
  },
  [VerdictType.NEEDS_ADAPTATION]: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    label: 'Needs Adaptation'
  },
  [VerdictType.NOT_RECOMMENDED]: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    label: 'Not Recommended'
  }
};

export default function RecipeAnalysisDisplay({ analysis }: Props) {
  return (
    <div className="card space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">{analysis.dish_name}</h2>
        <p className="text-[#8B7566]">{analysis.base_description}</p>
      </div>

      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Family Analysis</h3>
        
        {analysis.member_verdicts.map((verdict) => {
          const config = VERDICT_CONFIG[verdict.verdict];
          const Icon = config.icon;

          return (
            <div key={verdict.member_id} className={`p-4 rounded-xl ${config.bgColor}`}>
              <div className="flex items-start gap-3">
                <Icon className={`w-6 h-6 ${config.color} flex-shrink-0 mt-1`} />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold">{verdict.member_name}</h4>
                    <span className={`text-sm ${config.color}`}>
                      {config.label}
                    </span>
                  </div>

                  {verdict.reasons.length > 0 && (
                    <div className="mb-2">
                      <p className="text-sm font-medium mb-1">Reasons:</p>
                      <ul className="text-sm space-y-1">
                        {verdict.reasons.map((reason, i) => (
                          <li key={i}>• {reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {verdict.concerns.length > 0 && (
                    <div className="mb-2">
                      <p className="text-sm font-medium mb-1">Concerns:</p>
                      <ul className="text-sm space-y-1">
                        {verdict.concerns.map((concern, i) => (
                          <li key={i} className="text-red-700">⚠️ {concern}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {verdict.adaptations && (
                    <div className="mt-3 p-3 bg-white rounded-lg">
                      <p className="text-sm font-medium mb-2">Adaptations:</p>
                      
                      {verdict.adaptations.modifications.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-[#8B7566] mb-1">
                            Modifications:
                          </p>
                          <ul className="text-sm space-y-1">
                            {verdict.adaptations.modifications.map((mod, i) => (
                              <li key={i}>✓ {mod}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {verdict.adaptations.substitutions.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-[#8B7566] mb-1">
                            Substitutions:
                          </p>
                          {verdict.adaptations.substitutions.map((sub, i) => (
                            <div key={i} className="text-sm mb-1">
                              <span className="line-through text-red-600">
                                {sub.original}
                              </span>
                              {' → '}
                              <span className="text-green-600 font-medium">
                                {sub.replacement}
                              </span>
                              <p className="text-xs text-[#8B7566] ml-4">
                                {sub.reason}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {verdict.nutritional_notes && (
                    <p className="text-sm text-[#8B7566] mt-2">
                      💡 {verdict.nutritional_notes}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {analysis.general_tips.length > 0 && (
        <div className="bg-[#F9E5A8] p-4 rounded-xl">
          <h4 className="font-semibold mb-2">💡 General Tips</h4>
          <ul className="text-sm space-y-1">
            {analysis.general_tips.map((tip, i) => (
              <li key={i}>• {tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

### 5.5 Additional Components

**AddMemberModal.tsx**, **CameraCapture.tsx**, **PantryPage**, and **ScanPage** - implement similarly following the patterns above and the UI screenshots.

---

## 6. Testing & Deployment

### 6.1 Local Testing

**Test Backend:**
```bash
cd backend
python run.py
# Visit http://localhost:8000/docs for API documentation
```

**Test Frontend:**
```bash
cd frontend
npm run dev
# Visit http://localhost:3000
```

### 6.2 Environment Setup for Deployment

**Vercel Deployment (Frontend):**
```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

**Railway/Render Deployment (Backend):**
- Create `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 6.3 Testing Checklist

- [ ] Family profile CRUD operations
- [ ] Recipe analysis with different conditions
- [ ] Ingredient scanning (if OCR implemented)
- [ ] Responsive design on mobile
- [ ] Error handling for API failures
- [ ] Safe/unsafe ingredient detection
- [ ] Baby-safe adaptations
- [ ] Dietary condition adaptations

### 6.4 Sample Test Recipes

Use these for testing:
1. **Tiramisu** - Tests egg, caffeine, sugar concerns
2. **Fried Rice** - Tests sodium, soy sauce adaptations
3. **Chicken Stir Fry** - Tests vegetable variety, sodium
4. **Peanut Butter Cookies** - Tests allergy detection
5. **Spinach Salad** - Tests baby-safe modifications

---

## 7. Future Enhancements

### Phase 2 Features:
- Database integration (PostgreSQL/MongoDB)
- User authentication
- Recipe saving and favorites
- Meal planning calendar
- Shopping list generation
- Recipe community/sharing

### Phase 3 Features:
- Mobile apps (React Native)
- Barcode scanning
- Nutrition tracking
- Integration with grocery services
- Multi-language support
- Professional dietitian consultation

---

## 8. Cursor-Specific Instructions

### When building with Cursor:

1. **Start with backend structure:**
   - Ask: "Create the FastAPI backend structure with all models and routes as specified"
   - Provide the PRD sections relevant to backend

2. **Then build frontend:**
   - Ask: "Create Next.js frontend with TypeScript and Tailwind following the design system"
   - Reference the UI screenshots for design guidance

3. **For AI integration:**
   - Ask: "Implement the Anthropic Claude integration with proper prompt engineering"
   - Test prompts iteratively

4. **For debugging:**
   - Share error messages completely
   - Ask for specific fixes rather than general help

5. **For styling:**
   - Reference the color palette and component patterns
   - Ask for Tailwind classes that match the screenshots

### Prompt Templates for Cursor:

**Backend Creation:**
"Create a FastAPI application with the following structure: [paste relevant models/routes section]. Use Python best practices and include error handling."

**Frontend Page:**
"Create a Next.js page component for [feature name] that matches this UI design [describe or reference screenshot]. Use TypeScript and Tailwind CSS with the color palette: [paste colors]."

**Component Creation:**
"Create a React component called [ComponentName] that [describe functionality]. It should accept these props: [list props]. Style it with Tailwind to match [design description]."

---

## Appendix: Quick Command Reference

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev

# Deploy
vercel --prod  # Frontend
git push heroku main  # Backend (if using Heroku)
```

---

**END OF PROJECT REQUIREMENTS DOCUMENT**