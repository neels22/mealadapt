# MealAdapt — Hackathon Presentation

---

## Slide 1: Title

- **MealAdapt** — One kitchen. Many needs.
- AI-powered recipe adaptation for families with diverse dietary needs
- **Visual:** Hero screenshot of the home page

---

## Slide 2: The Problem

- Families juggle **diabetes, allergies, hypertension, baby safety** — all at the same dinner table
- Cooking separate meals is exhausting; existing recipe apps serve **one diet at a time**
- Parents constantly ask: *"Can my baby eat this? Will this spike Dad's blood sugar?"*

---

## Slide 3: What MealAdapt Does

- Enter any recipe or dish name — AI analyzes it against **every family member's profile** at once
- Each person gets a verdict: **Safe**, **Needs Adaptation**, or **Not Recommended**
- Returns specific **substitutions** (e.g., swap sugar for stevia), cooking modifications, and nutritional notes
- Supports 8 conditions (Diabetes, Hypertension, Celiac, Peanut Allergy, etc.) + baby-safe rules

---

## Slide 4: Key Features

- **Adapt Recipe** — AI dietary analysis for the whole family from any recipe or dish name
- **Scan Labels** — Gemini Vision reads ingredient labels from photos and checks safety
- **Barcode Scanner** — Look up packaged products via Open Food Facts + AI safety check
- **My Pantry** — Track ingredients at home, get family-safe recipe suggestions
- **Meal Planner & Shopping Lists** — Weekly calendar, save favorites, auto-generate categorized shopping lists

---

## Slide 5: Tech Stack & Architecture

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16 + TypeScript + Tailwind CSS |
| **Backend** | FastAPI (Python), 30+ async endpoints, JWT auth |
| **Database** | SQLite (dev) / PostgreSQL (prod) via SQLModel |
| **AI** | Google Gemini 2.0 Flash — text + vision, structured JSON output via Pydantic schemas |
| **External** | Open Food Facts API (barcode lookup) |
| **Infra** | Docker, GitHub Actions, Render |

**AI Safety Pipeline:** Scope Gate (cheap enum call blocks non-food misuse) → Structured Generation (schema-enforced JSON analysis) — with per-user rate limiting and input size caps.

---

## Slide 6: Live Demo

1. **Sign up & add family** — Dad (Diabetes), Baby Emma, Mom (Peanut Allergy)
2. **Adapt "Chicken Pad Thai"** — show per-member verdicts, substitutions, warnings
3. **Scan an ingredient label** — photo → AI reads ingredients → safety check
4. **Pantry suggestions** — add ingredients → get family-safe recipe ideas
5. **Meal plan & shopping list** — save recipe to calendar → auto-generate shopping list

---

## Slide 7: Challenges & Tradeoffs

| Challenge | What We Did |
|-----------|------------|
| Consistent LLM output | Gemini `response_schema` + Pydantic — validated JSON every time |
| Prompt injection / misuse | Two-stage pipeline: cheap scope gate blocks bad inputs before expensive analysis runs |
| Multi-person analysis in one call | Family profile as structured context; single prompt returns all verdicts |
| Label reading accuracy | Replaced Tesseract OCR with Gemini Vision — multimodal beats traditional OCR |
| Cost control | Per-user daily rate limits, input size caps, scope gate rejects early |

**Key tradeoff:** Gemini Flash over larger models — 10x faster, good-enough accuracy for dietary analysis.

---

## Slide 8: Takeaways

- **Structured output** (`response_schema`) eliminated JSON parsing bugs and made AI outputs reliable
- **Layered security** matters — system instructions alone aren't enough; scope gates + rate limiting + input validation
- **Dietary analysis is surprisingly nuanced** — baby safety alone (no honey, choking hazards, sodium) required careful prompt engineering
- **AI-assisted development** (Cursor) enabled building 9 full features in a focused sprint

---

## Slide 9: Team Contributions

| Team Member | Area | What They Built |
|-------------|------|-----------------|
| **Indraneel Sarode** | Database, Infra & Core | 14 SQLModel tables, CRUD layer, Docker setup, CI/CD, API client, shared types, error handling, deployment |
| **Jahnavi Kedia** | Family Profiles & Recipe AI | Family member CRUD, health condition profiles, Gemini recipe analysis with scope gate, per-member verdicts UI |
| **Harishita Gupta** | Scan, Barcode & Pantry | Gemini Vision label scanning, Open Food Facts barcode lookup, pantry tracking, recipe suggestions from ingredients |
| **Ashish Bhusal** | Meal Planner & Shopping | Weekly meal calendar, saved recipes with favorites, auto-generated shopping lists, shopping item management |
| **Nishan Paudel** | Auth & User Management | JWT auth (register, login, refresh tokens), password hashing, route protection, rate limiting, login/signup UI |

---

## Slide 10: Thank You & Q&A

- **MealAdapt** — One kitchen. Many needs.
- Next.js + FastAPI + Google Gemini AI
- **Questions?**
