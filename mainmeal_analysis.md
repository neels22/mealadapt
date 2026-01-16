# MainMeal Project Analysis & Notes

## Project Overview
**Name:** MainMeal  
**Tagline:** "One kitchen. Many needs."  
**Core Purpose:** AI-powered recipe adaptation system that modifies any recipe to suit multiple family members with different dietary needs, health conditions, and age requirements.

## Problem Statement
- Families have diverse dietary needs (chronic conditions, age-specific requirements, allergies)
- Cooking separate meals is time-consuming and impractical
- Unclear how to safely adapt one recipe for everyone
- Parents struggle with toddler food safety and picky eating
- People with conditions (diabetes, high uric acid, hypertension) need specialized meal planning

## Solution
An AI system that:
1. Takes any recipe as input
2. Analyzes it against family member profiles
3. Provides personalized verdicts and adaptations
4. Ensures safety for all dietary restrictions and age groups

---

## Core Features

### 1. **Scan Ingredient Label**
- Camera integration for scanning food labels
- OCR to extract ingredient lists
- Safety check against family profiles
- Manual ingredient entry option

### 2. **Adapt Recipe**
- Input: Recipe text or dish name
- AI analyzes recipe against all family profiles
- Outputs:
  - Base dish description
  - Per-person verdicts (Safe/Needs Adaptation/Not Recommended)
  - Detailed explanations
  - Specific adaptation instructions
  - Alternative suggestions

### 3. **My Pantry**
- Ingredient inventory management
- Recipe suggestions based on available ingredients
- "Try Sample" feature for demo
- "Find Recipes" search functionality

### 4. **Family Profile Management**
- Add/remove family members
- Role assignment (Adult/Child/Baby)
- Dietary restrictions and allergies
- Chronic conditions tracking:
  - Diabetes
  - High Uric Acid
  - Hypertension
  - Heart Disease
  - Kidney Disease
  - Celiac (Gluten-Free)
  - Lactose Intolerance
  - Peanut Allergy
- Visual avatars for each member
- Expandable/collapsible member details

### 5. **Safety Filters**
- Diabetic-Safe
- Low-Sodium
- Baby-Safe
- Additional condition-specific filters

---

## Technical Architecture

### Frontend Stack
- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS (based on UI design)
- **Deployment:** Vercel
- **UI Components:** Custom components with soft, warm color palette

### Backend Stack
- **Framework:** FastAPI (Python)
- **AI Integration:** Anthropic Claude API
- **Data Format:** Structured JSON for profiles and responses

### AI Agent Architecture
- **Model:** Anthropic Claude (Sonnet or Opus)
- **Prompt Engineering:** Structured prompts with family profiles
- **Response Format:** JSON with consistent schema
- **Capabilities:**
  - Recipe analysis
  - Nutritional assessment
  - Safety evaluation
  - Adaptation generation
  - Alternative suggestions

### Data Structure

#### Family Profile Schema
```json
{
  "family": [
    {
      "id": "member_id",
      "name": "string",
      "avatar": "emoji/icon",
      "role": "Adult|Child|Baby",
      "conditions": [
        {
          "type": "Diabetes|Hypertension|etc",
          "severity": "mild|moderate|severe",
          "enabled": true
        }
      ],
      "allergies": ["Peanut", "etc"],
      "dietary_restrictions": ["Gluten-Free", "etc"],
      "preferences": {
        "spice_tolerance": "low|medium|high",
        "texture_preferences": []
      }
    }
  ]
}
```

#### Recipe Analysis Response Schema
```json
{
  "dish_name": "string",
  "base_description": "string",
  "overall_safety": "safe|caution|unsafe",
  "member_verdicts": [
    {
      "member_id": "string",
      "member_name": "string",
      "verdict": "safe|needs_adaptation|not_recommended",
      "reasons": ["string"],
      "concerns": ["string"],
      "adaptations": {
        "modifications": ["string"],
        "substitutions": [
          {
            "original": "ingredient",
            "replacement": "alternative",
            "reason": "string"
          }
        ],
        "preparation_changes": ["string"]
      },
      "nutritional_notes": "string"
    }
  ],
  "general_tips": ["string"]
}
```

---

## UI/UX Design System

### Color Palette
- **Primary Background:** Warm beige (#F5EBE0)
- **Card Background:** White/Cream
- **Accent Colors:**
  - Soft green (#A8D5BA) - Safe/Positive actions
  - Soft blue (#B8D4E8) - Informational
  - Soft yellow (#F9E5A8) - Baby-related
  - Soft red (#E8A8A8) - Allergies/Warnings
  - Soft pink (#F0C8D0) - Hypertension

### Typography
- **Headers:** Bold, dark brown (#6B5446)
- **Body:** Medium gray-brown
- **Font:** Clean, modern sans-serif

### Component Patterns
1. **Cards:** Rounded corners, subtle shadows, soft backgrounds
2. **Buttons:** Pill-shaped, color-coded by action type
3. **Tags/Badges:** Rounded, condition-specific colors
4. **Icons:** Simple, emoji-style or minimal line icons
5. **Expandable Sections:** Accordion-style with chevron indicators

### Key Screens (from screenshots)

#### Home Screen
- Hero section: "MainMeal" + tagline
- "Scan ingredient label" prominent CTA
- "Adapt Recipe" and "My Pantry" action cards
- "My Family" section with member avatars and condition tags
- Bottom action buttons (Diabetic-Safe, Low-Sodium, Baby-Safe filters)

#### Scan Ingredient Label Screen
- Camera viewfinder with dashed border
- "Tap to take a photo or upload"
- Instructions: "Point your camera at the ingredients list"
- Manual entry option: "Add Ingredients Manually"
- Text input with "Add" button

#### Adapt Recipe Screen
- Large text input area
- Placeholder: "Type a dish name or paste a full recipe"
- "Surprise Me" button for random suggestions
- "Check for My Family" primary CTA
- "Powered by LLM" footer

#### My Pantry Screen
- "Loose Ingredients" input section
- Text field: "Add ingredients you have (press Enter to add)"
- "Try Sample" and "Find Recipes" buttons
- Tips section with bullet points

#### Family Profile Detail Screen
- Member avatar and name at top
- Role selector (Adult/Child/Baby)
- "Chronic Conditions" section with toggles
- Scrollable condition list
- "Remove [Member]" button at bottom
- Collapsible design

---

## Development Workflow (as described)

### Tools Used
1. **Cursor:** AI-assisted code generation and debugging
2. **GitHub:** Version control and collaboration
3. **Vercel:** Automatic deployment
4. **Anthropic API:** Recipe analysis AI
5. **Gemini:** Content and script generation
6. **CapCut:** Video voiceovers
7. **Canva:** Visual design assets
8. **ChatGPT:** Copywriting and editing

### Testing Approach
- Manual testing with real recipes (tiramisu, fried rice, chicken stir fry)
- Iterative prompt refinement for consistent AI outputs
- Safety validation for edge cases
- Cross-browser and mobile testing

---

## Success Metrics (Implied)

1. **Accuracy:** AI correctly identifies dietary conflicts
2. **Usability:** Non-technical users can create profiles and get adaptations
3. **Safety:** No unsafe recommendations for restricted conditions
4. **Practicality:** Adaptations are actually cookable
5. **Consistency:** Similar recipes produce similar analyses

---

## Potential Extensions (Future Considerations)

1. Shopping list generation
2. Meal planning calendar
3. Recipe database integration
4. Nutrition tracking
5. Community recipe sharing
6. Multi-language support
7. Voice input for recipes
8. Barcode scanning for products
9. Integration with grocery delivery services
10. Professional dietitian review feature

---

## Key Technical Challenges to Address

1. **OCR Accuracy:** Ensuring ingredient labels are read correctly
2. **Prompt Engineering:** Getting consistent, safe AI responses
3. **State Management:** Handling family profiles across the app
4. **Error Handling:** Graceful failures for API issues
5. **Mobile Responsiveness:** Camera integration on various devices
6. **Data Persistence:** Storing family profiles and pantry data
7. **Performance:** Fast AI responses for good UX
8. **Security:** Protecting health information (HIPAA considerations if applicable)

---

## Development Priorities

### Phase 1: Core Functionality
1. Family profile CRUD
2. Basic recipe adaptation with AI
3. Simple text input interface
4. Essential conditions (Diabetes, Hypertension, Baby-Safe)

### Phase 2: Enhanced Features
1. Ingredient scanning
2. My Pantry feature
3. Extended condition list
4. Improved UI polish

### Phase 3: Advanced Features
1. Recipe database
2. Meal planning
3. Shopping lists
4. Advanced filtering

