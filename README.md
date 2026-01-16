# MealAdapt 🍽️

> One kitchen. Many needs.

**MealAdapt** is an AI-powered recipe adaptation system that helps you cook meals that work for your entire family, even when family members have different dietary needs, health conditions, and age requirements. Whether you're cooking for someone with diabetes, a baby, or someone with allergies, MealAdapt analyzes any recipe and tells you exactly how to adapt it so everyone can enjoy the same meal safely.

## What Problem Does This Solve?

Cooking for a family with diverse dietary needs is challenging. You might have:
- A family member with diabetes who needs low-sugar meals
- A baby who can't eat certain foods
- Someone with high blood pressure who needs low-sodium food
- A person with peanut allergies
- A child who needs age-appropriate meals

Instead of cooking separate meals for everyone, MealAdapt helps you adapt one recipe to work for your entire family. The AI analyzes any recipe against your family's specific needs and provides personalized safety verdicts and adaptation suggestions.

## Complete Feature List

### 1. 👤 User Authentication & Account Management
- **Create an account**: Sign up with your email and password
- **Login/Logout**: Secure login system with JWT tokens
- **Profile Management**: Update your name, email, and password
- **Account Deletion**: Delete your account and all associated data
- **Multi-user Support**: Each user has their own isolated family profiles and data

### 2. 👨‍👩‍👧‍👦 Family Profile Management
- **Add Family Members**: Add as many family members as you need with their names and avatars
- **Assign Roles**: Choose Adult, Child, or Baby for each member
- **Health Conditions**: Toggle specific health conditions for each member:
  - Diabetes
  - High Uric Acid
  - Hypertension (High Blood Pressure)
  - Heart Disease
  - Kidney Disease
  - Celiac Disease (Gluten-Free)
  - Lactose Intolerance
  - Peanut Allergy
- **Custom Restrictions**: Add any custom dietary restrictions or allergies
- **Edit & Delete**: Update member information or remove members as needed
- **Persistent Storage**: All family profiles are saved and persist across sessions

### 3. 🔍 Recipe Adaptation & Analysis
- **Any Recipe Works**: Enter just a dish name (like "chicken curry") or paste a full recipe
- **AI-Powered Analysis**: Google Gemini AI analyzes the recipe against all family members' needs
- **Personalized Verdicts**: For each family member, get one of three verdicts:
  - ✅ **Safe**: Can eat as-is
  - ⚠️ **Needs Adaptation**: Safe with modifications
  - ❌ **Not Recommended**: Too risky, alternatives suggested
- **Detailed Explanations**: Understand why a recipe is safe or unsafe for each person
- **Smart Substitutions**: Get specific ingredient replacements (e.g., "replace white sugar with stevia")
- **Cooking Modifications**: Learn how to adjust cooking methods (e.g., "reduce salt by 50%")
- **Nutritional Notes**: Receive helpful nutritional guidance for each family member
- **General Tips**: Get family-wide cooking tips for the dish

### 4. 📷 Scan Ingredient Labels
- **Camera Integration**: Take a photo of any food product's ingredient label
- **Image Upload**: Upload an image of an ingredient label from your device
- **AI Vision Reading**: Google Gemini Vision reads and extracts all ingredients from the label
- **Safety Check**: Instantly analyzes if the product is safe for your family
- **Concern Highlights**: Shows which ingredients might be problematic and for which family members
- **Recommendations**: Provides specific guidance on whether the product is safe to consume

### 5. 🏠 My Pantry
- **Track Ingredients**: Keep a list of ingredients you currently have in your kitchen
- **Add Ingredients**: Manually add ingredients to your pantry
- **Remove Items**: Delete ingredients as you use them
- **AI Recipe Suggestions**: Get personalized recipe recommendations based on what you have
- **Family-Conscious Suggestions**: All suggested recipes consider your family's dietary needs
- **Missing Ingredients**: See what additional ingredients you might need for suggested recipes

### 6. 📚 Recipe Saving & Favorites
- **Save Recipes**: After analyzing a recipe, save it to your personal collection
- **Mark Favorites**: Heart icon to mark your favorite recipes for quick access
- **Recipe Collection**: View all your saved recipes in one place
- **Search Recipes**: Search your saved recipes by name or tags
- **Filter by Favorites**: Toggle between viewing all recipes or just favorites
- **View Full Analysis**: Revisit the complete safety analysis for any saved recipe
- **Delete Recipes**: Remove recipes from your collection

### 7. 🛒 Shopping List Generation
- **Create Lists**: Make multiple shopping lists for different purposes
- **Manual Entry**: Add items to your shopping list manually
- **Generate from Recipes**: Automatically create shopping lists from your saved recipes
- **AI Ingredient Extraction**: Google Gemini AI extracts and combines ingredients from multiple recipes
- **Smart Categorization**: Items are automatically organized by grocery category:
  - Produce (vegetables, fruits)
  - Dairy (milk, cheese, yogurt)
  - Meat & Seafood
  - Pantry Items (spices, oils, canned goods)
  - Bakery Items
  - And more
- **Check Off Items**: Mark items as purchased while shopping
- **Progress Tracking**: See how many items you've completed with a progress bar
- **Add/Remove Items**: Modify your shopping list anytime
- **Delete Lists**: Remove shopping lists you no longer need

### 8. 📅 Meal Planning Calendar
- **Weekly Calendar View**: Plan your meals for the entire week
- **Four Meal Slots**: Schedule recipes for Breakfast, Lunch, Dinner, and Snacks
- **Add Recipes**: Drag or select saved recipes to add to any meal slot
- **Navigate Weeks**: Move forward or backward between weeks
- **Jump to Current Week**: Quick button to return to the current week
- **Today's Indicator**: Visual highlight for today's date
- **Remove Meals**: Delete meals from your plan
- **Generate Shopping List**: Create a complete shopping list from all meals planned for the week
- **One-Click Planning**: Generate shopping list directly from your weekly meal plan

### 9. 📱 Barcode Scanning
- **Product Lookup**: Enter a barcode number to look up product information
- **Open Food Facts Integration**: Uses the free Open Food Facts database (no API key needed)
- **Product Information**: View product name, brand, image, and full ingredient list
- **Nutrition Facts**: See Nutri-Score grade (A-E) and detailed nutrition information
- **Allergen Highlights**: Automatically highlights known allergens in the product
- **AI Safety Analysis**: Analyzes the product against your family profile using Google Gemini
- **Cached Results**: Product information is cached to reduce API calls
- **Integrated with Scan Page**: Easy access from the main scanning interface

## Technology Stack

### Backend
- **Framework**: FastAPI (Python) - Fast, modern web framework
- **Database**: SQLite (development) / PostgreSQL (production) with SQLModel ORM
- **AI Service**: Google Gemini 2.5 Flash API (text and vision capabilities)
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Integration**: Open Food Facts API for barcode scanning

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS with custom design system
- **Icons**: Lucide React
- **State Management**: React Context API for authentication

## Quick Start Guide

### Prerequisites
Before you begin, make sure you have:
- **Python 3.10 or higher** installed on your computer
- **Node.js 18 or higher** installed on your computer
- A **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### Step 1: Backend Setup

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment** (this keeps dependencies separate):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Mac/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`

4. **Install all required packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file**:
   Create a `.env` file in the `backend` folder with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   CORS_ORIGINS=http://localhost:3000
   JWT_SECRET=your_secret_key_here
   ```
   (JWT_SECRET is optional - will use a default if not provided)

6. **Start the backend server**:
   ```bash
   python run.py
   ```
   
   The backend will run at `http://localhost:8000`

### Step 2: Frontend Setup

1. **Open a new terminal window** and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. **Install all required packages**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   Create a `.env.local` file in the `frontend` folder with:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   The frontend will run at `http://localhost:3000`

### Step 3: Access the Application

1. Open your web browser
2. Go to `http://localhost:3000`
3. Create an account or login
4. Start adding family members and exploring features!

## How to Use Each Feature

### Getting Started
1. **Create an Account**: Click "Sign Up" on the home page, enter your email and password
2. **Login**: Use your email and password to access your account
3. **Add Family Members**: Click the "+ Add" button in "My Family" section
4. **Set Health Conditions**: For each member, expand their card and toggle relevant health conditions

### Analyzing a Recipe
1. Click **"Adapt Recipe"** from the home page
2. Type a dish name (e.g., "chicken stir fry") or paste a full recipe
3. Click **"Check for My Family"**
4. Review the results for each family member
5. Click **"Save Recipe"** if you want to keep it for later

### Scanning Ingredient Labels
1. Click **"Scan Ingredient Label"** from the home page
2. Choose **"Take Photo"** (uses your camera) or **"Upload Image"**
3. Point your camera at the ingredient list or select an image
4. The AI will read the ingredients and check safety for your family
5. Review the safety analysis

### Using My Pantry
1. Click **"My Pantry"** from the home page
2. Type ingredients you have and press Enter to add them
3. Click **"Find Recipes"** to get AI suggestions based on your pantry
4. Review suggested recipes and see what additional ingredients you might need

### Saving Recipes
1. After analyzing a recipe, click the **"Save Recipe"** button
2. View all saved recipes in **"My Recipes"** page
3. Click the heart icon to mark favorites
4. Use the search box to find specific recipes
5. Click on any recipe to view its full analysis

### Creating Shopping Lists
1. Go to **"Shopping"** page
2. Click **"Create New List"** or **"Generate from Recipes"**
3. If generating from recipes, select which recipes to include
4. The AI will extract and organize ingredients by category
5. Check off items as you shop
6. Add or remove items manually as needed

### Meal Planning
1. Go to **"Meal Planner"** page
2. Navigate to the week you want to plan
3. Click on any meal slot (breakfast, lunch, dinner, snack)
4. Select a saved recipe to add to that slot
5. Plan meals for the entire week
6. Click **"Generate Shopping List"** to create a list from all planned meals

### Barcode Scanning
1. Go to **"Scan"** page
2. Switch to the **"Barcode"** tab
3. Enter a product's barcode number
4. View product information and nutrition facts
5. See AI-powered safety analysis for your family

## Supported Health Conditions

MealAdapt supports the following health conditions and dietary restrictions:

- **Diabetes**: Low-sugar and low-glycemic index recommendations
- **High Uric Acid**: Avoids high-purine foods
- **Hypertension**: Low-sodium recommendations
- **Heart Disease**: Heart-healthy ingredient suggestions
- **Kidney Disease**: Kidney-friendly modifications
- **Celiac Disease (Gluten-Free)**: Identifies and substitutes gluten-containing ingredients
- **Lactose Intolerance**: Suggests dairy-free alternatives
- **Peanut Allergy**: Flags peanut-containing ingredients and cross-contamination risks
- **Baby-Safe**: Special modifications for babies including:
  - No honey (botulism risk)
  - No whole nuts (choking hazard)
  - No raw eggs
  - Low sodium
  - Appropriate textures

## Complete API Endpoints

### Authentication
- `POST /api/auth/register` - Create a new account
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout (invalidates token)
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile
- `PUT /api/auth/me/password` - Change password
- `DELETE /api/auth/me` - Delete account

### Family Management
- `GET /api/family/profile` - Get family profile
- `POST /api/family/member` - Add a family member
- `PUT /api/family/member/{id}` - Update a family member
- `DELETE /api/family/member/{id}` - Delete a family member

### Recipe Analysis
- `POST /api/recipe/analyze` - Analyze a recipe for family safety

### Saved Recipes
- `GET /api/recipes/saved` - Get all saved recipes
- `GET /api/recipes/saved/{id}` - Get a single saved recipe
- `POST /api/recipes/saved` - Save a recipe
- `PUT /api/recipes/saved/{id}` - Update saved recipe (favorite, notes, tags)
- `DELETE /api/recipes/saved/{id}` - Delete a saved recipe

### Shopping Lists
- `GET /api/shopping/lists` - Get all shopping lists
- `GET /api/shopping/lists/{id}` - Get a single shopping list
- `POST /api/shopping/lists` - Create a new shopping list
- `POST /api/shopping/lists/generate` - Generate list from recipes (AI)
- `POST /api/shopping/lists/{id}/items` - Add item to list
- `PUT /api/shopping/items/{id}` - Update item (check/uncheck)
- `DELETE /api/shopping/items/{id}` - Delete item from list
- `DELETE /api/shopping/lists/{id}` - Delete a shopping list

### Meal Planning
- `GET /api/meal-plans` - Get meal plan for a specific week
- `POST /api/meal-plans/meals` - Add meal to plan
- `PUT /api/meal-plans/meals/{id}` - Update planned meal
- `DELETE /api/meal-plans/meals/{id}` - Remove meal from plan
- `POST /api/meal-plans/{id}/generate-shopping` - Generate shopping list from meal plan

### Scanning & Barcode
- `POST /api/scan/analyze` - Scan ingredient label image
- `GET /api/barcode/{code}` - Look up product by barcode
- `POST /api/barcode/{code}/analyze` - Analyze product against family

### Pantry
- `GET /api/pantry/items` - Get all pantry items
- `POST /api/pantry/items` - Add pantry item
- `DELETE /api/pantry/items/{id}` - Delete pantry item
- `POST /api/pantry/suggest-recipes` - Get recipe suggestions based on pantry

## Project Structure

```
mealadapt/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py           # Database connection and initialization
│   │   ├── crud.py               # Database operations
│   │   ├── models/
│   │   │   ├── user.py           # User authentication models
│   │   │   ├── family.py         # Family member models
│   │   │   ├── recipe.py         # Recipe analysis models
│   │   │   ├── saved_recipe.py  # Saved recipe models
│   │   │   ├── shopping.py       # Shopping list models
│   │   │   ├── meal_plan.py      # Meal planning models
│   │   │   └── tables.py         # Database table definitions
│   │   ├── routes/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── family.py         # Family management endpoints
│   │   │   ├── recipe.py         # Recipe analysis endpoints
│   │   │   ├── saved_recipes.py  # Saved recipe endpoints
│   │   │   ├── shopping.py       # Shopping list endpoints
│   │   │   ├── meal_plan.py      # Meal planning endpoints
│   │   │   ├── scan.py           # Ingredient scanning endpoints
│   │   │   ├── barcode.py        # Barcode scanning endpoints
│   │   │   └── pantry.py         # Pantry management endpoints
│   │   ├── services/
│   │   │   ├── ai_service.py     # Google Gemini AI integration
│   │   │   ├── auth_service.py   # Authentication & JWT service
│   │   │   └── barcode_service.py # Open Food Facts API integration
│   │   └── middleware/
│   │       ├── auth.py           # JWT authentication middleware
│   │       ├── error_handler.py  # Error handling
│   │       ├── rate_limit.py    # Rate limiting
│   │       ├── request_size.py   # Request size limits
│   │       └── security.py       # Security headers
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   ├── docker-compose.yml        # Docker Compose setup
│   ├── env.example               # Environment variables template
│   └── run.py                    # Server startup script
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Home page
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── signup/
│   │   │   └── page.tsx         # Signup page
│   │   ├── profile/
│   │   │   └── page.tsx         # User profile page
│   │   ├── adapt/
│   │   │   └── page.tsx         # Recipe adaptation page
│   │   ├── recipes/
│   │   │   └── page.tsx          # Saved recipes page
│   │   ├── shopping/
│   │   │   └── page.tsx          # Shopping lists page
│   │   ├── planner/
│   │   │   └── page.tsx          # Meal planning calendar
│   │   ├── scan/
│   │   │   └── page.tsx          # Ingredient scanning page
│   │   ├── pantry/
│   │   │   └── page.tsx          # Pantry management page
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── AuthProvider.tsx      # Authentication context
│   │   ├── ProtectedRoute.tsx    # Route protection
│   │   ├── UserMenu.tsx          # User dropdown menu
│   │   ├── FamilyProfile.tsx     # Family profile display
│   │   ├── MemberCard.tsx        # Family member card
│   │   ├── AddMemberModal.tsx    # Add member modal
│   │   ├── RecipeAnalysisDisplay.tsx # Recipe analysis results
│   │   ├── SavedRecipeCard.tsx   # Saved recipe card
│   │   ├── ScanResultDisplay.tsx # Scan results display
│   │   └── RecipeSuggestions.tsx  # Recipe suggestions
│   ├── lib/
│   │   ├── api.ts                # API client functions
│   │   └── types.ts              # TypeScript type definitions
│   ├── package.json              # Node.js dependencies
│   └── next.config.ts            # Next.js configuration
├── project_completion.md         # Development progress tracker
├── mainmeal_analysis.md          # Project analysis document
├── mainmeal_prd.md               # Product requirements document
└── README.md                     # This file
```

## Environment Variables

### Backend (.env)
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `CORS_ORIGINS` - Allowed frontend URLs (comma-separated)
- `JWT_SECRET` - Secret key for JWT tokens (optional, has default)
- `DATABASE_URL` - Database connection string (for PostgreSQL)
- `DB_SCHEMA` - Database schema name (default: mealadapt)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)

## Database

- **Development**: SQLite database (`mainmeal.db`) created automatically in the backend folder
- **Production**: PostgreSQL with Cloud SQL support (see DEPLOYMENT.md)
- All data is isolated per user - each user has their own family profiles, recipes, and lists

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt (12 rounds)
- **JWT Authentication**: Secure token-based authentication with 24-hour expiry
- **CORS Protection**: Configured to only allow requests from specified origins
- **Security Headers**: HTTP security headers implemented
- **Rate Limiting**: API rate limiting to prevent abuse
- **Request Size Limits**: Maximum request size limits to prevent DoS attacks
- **Data Isolation**: Each user's data is completely isolated from others

## Deployment

For production deployment instructions, see:
- `backend/DEPLOYMENT.md` - Complete deployment guide
- `backend/DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist

The application can be deployed using Docker Compose with PostgreSQL support.

## Troubleshooting

### Backend won't start
- Check that Python 3.10+ is installed
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure `.env` file exists with `GEMINI_API_KEY`
- Check that port 8000 is not already in use

### Frontend won't start
- Check that Node.js 18+ is installed
- Verify all dependencies are installed: `npm install`
- Ensure `.env.local` file exists with `NEXT_PUBLIC_API_URL`
- Check that port 3000 is not already in use

### API errors
- Verify backend is running on `http://localhost:8000`
- Check browser console for error messages
- Verify `NEXT_PUBLIC_API_URL` matches backend URL
- Check backend logs for detailed error information

### Database issues
- For SQLite: Ensure write permissions in backend folder
- Database is created automatically on first run
- Check backend logs for database initialization messages

## Future Enhancements

Potential features for future versions:
- Multi-language support
- Recipe community sharing
- Nutrition tracking and calorie counting
- Integration with grocery delivery services
- Mobile app versions (iOS/Android)
- Voice input for recipes
- Meal prep suggestions
- Leftover recipe ideas

## Contributing

This is a personal project. If you'd like to contribute or report issues, please feel free to open an issue or submit a pull request.

## License

MIT License - Feel free to use this project for learning or personal use.

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the API documentation at `http://localhost:8000/docs` when backend is running
3. Check the project completion tracker (`project_completion.md`) for feature status

---

**Made with ❤️ for families with diverse dietary needs**
