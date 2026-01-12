# MainMeal 🍽️

> One kitchen. Many needs.

AI-powered recipe adaptation system that modifies any recipe to suit multiple family members with different dietary needs, health conditions, and age requirements.

## Features

- **Family Profile Management**: Add family members with their health conditions (Diabetes, Hypertension, Allergies, etc.)
- **Recipe Adaptation**: Analyze any recipe against your family's dietary needs
- **AI-Powered Safety**: Get personalized verdicts (Safe / Needs Adaptation / Not Recommended) for each family member
- **Smart Substitutions**: Receive specific ingredient substitutions and cooking modifications

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js 16 with TypeScript & Tailwind CSS
- **AI**: Google Gemini API

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
echo "CORS_ORIGINS=http://localhost:3000" >> .env

# Run the server
python run.py
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run the development server
npm run dev
```

Frontend runs at `http://localhost:3000`

## Usage

1. **Add Family Members**: Click "+ Add" in the "My Family" section
2. **Set Conditions**: Toggle health conditions for each member (Diabetes, Hypertension, etc.)
3. **Analyze Recipes**: Go to "Adapt Recipe" and enter a dish name or full recipe
4. **Review Results**: See personalized safety verdicts and adaptation suggestions for each family member

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/family/profile` | Get family profile |
| POST | `/api/family/member` | Add family member |
| PUT | `/api/family/member/{id}` | Update family member |
| DELETE | `/api/family/member/{id}` | Delete family member |
| POST | `/api/recipe/analyze` | Analyze recipe for family |

## Supported Health Conditions

- Diabetes
- High Uric Acid
- Hypertension
- Heart Disease
- Kidney Disease
- Celiac (Gluten-Free)
- Lactose Intolerance
- Peanut Allergy
- Baby-safe modifications (for members with Baby role)

## Project Structure

```
mainmeal/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── models/              # Pydantic models
│   │   ├── routes/              # API routes
│   │   └── services/            # Gemini AI service
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   └── lib/                     # Types & API client
├── project_completion.md        # Progress tracker
└── README.md
```

## License

MIT
