'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  X,
  Loader2,
  ShoppingCart,
  Calendar,
  Utensils
} from 'lucide-react';
import { api } from '@/lib/api';
import { MealPlan, PlannedMeal, SavedRecipe, MealType } from '@/lib/types';
import ProtectedRoute from '@/components/ProtectedRoute';

const MEAL_TYPES: { value: MealType; label: string; icon: string }[] = [
  { value: 'breakfast', label: 'Breakfast', icon: '🌅' },
  { value: 'lunch', label: 'Lunch', icon: '☀️' },
  { value: 'dinner', label: 'Dinner', icon: '🌙' },
  { value: 'snack', label: 'Snack', icon: '🍎' },
];

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function getMonday(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(d.setDate(diff));
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function PlannerContent() {
  const [currentWeek, setCurrentWeek] = useState<Date>(getMonday(new Date()));
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [recipes, setRecipes] = useState<SavedRecipe[]>([]);
  const [showAddModal, setShowAddModal] = useState<{ date: string; mealType: MealType } | null>(null);
  const [generatingList, setGeneratingList] = useState(false);
  const [selectedMeal, setSelectedMeal] = useState<PlannedMeal | null>(null);

  useEffect(() => {
    loadPlan();
    loadRecipes();
  }, [currentWeek]);

  const loadPlan = async () => {
    try {
      setLoading(true);
      const data = await api.getMealPlan(formatDate(currentWeek));
      setPlan(data);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load meal plan:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadRecipes = async () => {
    try {
      const response = await api.getSavedRecipes();
      setRecipes(response.recipes);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load recipes:', error);
      }
    }
  };

  const handlePrevWeek = () => {
    setCurrentWeek(addDays(currentWeek, -7));
  };

  const handleNextWeek = () => {
    setCurrentWeek(addDays(currentWeek, 7));
  };

  const handleThisWeek = () => {
    setCurrentWeek(getMonday(new Date()));
  };

  const getMealsForDay = (date: string, mealType: MealType): PlannedMeal[] => {
    if (!plan) return [];
    return plan.meals.filter(m => m.date === date && m.meal_type === mealType);
  };

  const handleAddMeal = async (recipeId: string) => {
    if (!showAddModal) return;
    
    try {
      const newMeal = await api.addPlannedMeal({
        recipe_id: recipeId,
        date: showAddModal.date,
        meal_type: showAddModal.mealType,
        servings: 1
      });
      
      // Update local state
      if (plan) {
        setPlan({
          ...plan,
          meals: [...plan.meals, newMeal]
        });
      }
      setShowAddModal(null);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to add meal:', error);
      }
    }
  };

  const handleDeleteMeal = async (mealId: number) => {
    try {
      await api.deletePlannedMeal(mealId);
      if (plan) {
        setPlan({
          ...plan,
          meals: plan.meals.filter(m => m.id !== mealId)
        });
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to delete meal:', error);
      }
    }
  };

  const handleGenerateShopping = async () => {
    if (!plan || plan.meals.length === 0) {
      alert('Add some meals to your plan first!');
      return;
    }
    
    const listName = `Week of ${formatWeekRange()}`;
    
    setGeneratingList(true);
    try {
      await api.generateShoppingFromPlan(plan.id, { list_name: listName });
      alert('Shopping list created! Check your Shopping page.');
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to generate shopping list:', error);
      }
      alert('Failed to generate shopping list. Please try again.');
    } finally {
      setGeneratingList(false);
    }
  };

  const formatWeekRange = () => {
    const endOfWeek = addDays(currentWeek, 6);
    const startMonth = currentWeek.toLocaleString('default', { month: 'short' });
    const endMonth = endOfWeek.toLocaleString('default', { month: 'short' });
    
    if (startMonth === endMonth) {
      return `${startMonth} ${currentWeek.getDate()}-${endOfWeek.getDate()}`;
    }
    return `${startMonth} ${currentWeek.getDate()} - ${endMonth} ${endOfWeek.getDate()}`;
  };

  // Build week days
  const weekDays = DAYS.map((day, i) => ({
    name: day,
    date: formatDate(addDays(currentWeek, i)),
    isToday: formatDate(addDays(currentWeek, i)) === formatDate(new Date())
  }));

  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/" 
        className="inline-flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>

      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Meal Planner</h1>
        <p className="text-[var(--text-secondary)]">
          Plan your meals for the week
        </p>
      </div>

      {/* Week Navigation */}
      <div className="card">
        <div className="flex items-center justify-between">
          <button
            onClick={handlePrevWeek}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          
          <div className="text-center">
            <h2 className="text-xl font-semibold">{formatWeekRange()}</h2>
            <button
              onClick={handleThisWeek}
              className="text-sm text-[var(--accent-green)] hover:underline"
            >
              Go to this week
            </button>
          </div>
          
          <button
            onClick={handleNextWeek}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>

        {/* Generate Shopping Button */}
        <button
          onClick={handleGenerateShopping}
          disabled={generatingList || !plan || plan.meals.length === 0}
          className="w-full mt-4 btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {generatingList ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <ShoppingCart className="w-5 h-5" />
              Generate Shopping List
            </>
          )}
        </button>
      </div>

      {/* Calendar Grid */}
      {loading ? (
        <div className="card flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-green)]" />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div className="min-w-[700px]">
            {/* Day Headers */}
            <div className="grid grid-cols-7 gap-2 mb-2">
              {weekDays.map(day => (
                <div 
                  key={day.date}
                  className={`text-center p-2 rounded-lg ${
                    day.isToday ? 'bg-[var(--accent-green)] text-[var(--text-primary)]' : 'bg-gray-100'
                  }`}
                >
                  <div className="font-semibold">{day.name}</div>
                  <div className="text-sm">{new Date(day.date).getDate()}</div>
                </div>
              ))}
            </div>

            {/* Meal Rows */}
            {MEAL_TYPES.map(mealType => (
              <div key={mealType.value} className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">{mealType.icon}</span>
                  <span className="font-medium text-sm text-[var(--text-secondary)]">{mealType.label}</span>
                </div>
                <div className="grid grid-cols-7 gap-2">
                  {weekDays.map(day => {
                    const meals = getMealsForDay(day.date, mealType.value);
                    
                    return (
                      <div 
                        key={`${day.date}-${mealType.value}`}
                        className="min-h-[80px] bg-[var(--background)] rounded-lg p-2 border border-[#d6d3d1]"
                      >
                        {/* Existing Meals */}
                        {meals.map(meal => (
                          <div 
                            key={meal.id}
                            onClick={() => setSelectedMeal(meal)}
                            className="bg-white rounded-md p-2 mb-1 shadow-sm group relative cursor-pointer hover:bg-[var(--accent-green)]/10 hover:shadow-md transition-all"
                          >
                            <div className="text-xs font-medium truncate pr-5">
                              {meal.dish_name || 'Unknown Recipe'}
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                meal.id && handleDeleteMeal(meal.id);
                              }}
                              className="absolute top-1 right-1 p-1 rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                        
                        {/* Add Button */}
                        <button
                          onClick={() => setShowAddModal({ date: day.date, mealType: mealType.value })}
                          className="w-full p-2 rounded-md border-2 border-dashed border-[#a8a29e] text-[#78716c] hover:border-[var(--accent-green)] hover:text-[var(--accent-green)] hover:bg-[var(--accent-green)]/10 transition-colors flex items-center justify-center"
                        >
                          <Plus className="w-5 h-5" strokeWidth={2.5} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && recipes.length === 0 && (
        <div className="card text-center py-8">
          <Utensils className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">No saved recipes yet</h3>
          <p className="text-[var(--text-secondary)] text-sm mb-4">
            Save some recipes first to add them to your meal plan
          </p>
          <Link href="/adapt" className="btn-primary inline-flex items-center gap-2">
            Adapt a Recipe
          </Link>
        </div>
      )}

      {/* Add Meal Modal */}
      {showAddModal && (
        <AddMealModal
          date={showAddModal.date}
          mealType={showAddModal.mealType}
          recipes={recipes}
          onClose={() => setShowAddModal(null)}
          onAdd={handleAddMeal}
        />
      )}

      {/* View Recipe Modal */}
      {selectedMeal && (
        <ViewRecipeModal
          meal={selectedMeal}
          recipe={recipes.find(r => r.id === selectedMeal.recipe_id)}
          onClose={() => setSelectedMeal(null)}
        />
      )}

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by Google Gemini AI
      </p>
    </div>
  );
}

// Add Meal Modal
function AddMealModal({
  date,
  mealType,
  recipes,
  onClose,
  onAdd
}: {
  date: string;
  mealType: MealType;
  recipes: SavedRecipe[];
  onClose: () => void;
  onAdd: (recipeId: string) => void;
}) {
  const [search, setSearch] = useState('');
  
  const filteredRecipes = recipes.filter(r =>
    r.dish_name.toLowerCase().includes(search.toLowerCase())
  );

  const mealTypeLabel = MEAL_TYPES.find(m => m.value === mealType)?.label || mealType;
  const dateLabel = new Date(date).toLocaleDateString('en-US', { 
    weekday: 'long', 
    month: 'short', 
    day: 'numeric' 
  });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full max-h-[80vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold">Add {mealTypeLabel}</h3>
            <p className="text-sm text-[var(--text-secondary)]">{dateLabel}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search recipes..."
          className="w-full px-4 py-2 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] mb-4"
        />

        <div className="flex-1 overflow-y-auto space-y-2 max-h-60">
          {filteredRecipes.length === 0 ? (
            <p className="text-center text-[var(--text-secondary)] py-8">
              {search ? 'No recipes match your search' : 'No saved recipes yet'}
            </p>
          ) : (
            filteredRecipes.map(recipe => (
              <button
                key={recipe.id}
                onClick={() => onAdd(recipe.id)}
                className="w-full p-3 text-left bg-[var(--background)] rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="font-medium">{recipe.dish_name}</div>
                {recipe.analysis?.base_description && (
                  <div className="text-xs text-[var(--text-secondary)] mt-1 line-clamp-1">
                    {recipe.analysis.base_description}
                  </div>
                )}
              </button>
            ))
          )}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <Link 
            href="/adapt" 
            className="w-full btn-secondary flex items-center justify-center gap-2"
            onClick={onClose}
          >
            <Plus className="w-5 h-5" />
            Add New Recipe
          </Link>
        </div>
      </div>
    </div>
  );
}

// View Recipe Modal
function ViewRecipeModal({
  meal,
  recipe,
  onClose
}: {
  meal: PlannedMeal;
  recipe?: SavedRecipe;
  onClose: () => void;
}) {
  const analysis = meal.analysis || recipe?.analysis;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-lg w-full max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold">{meal.dish_name || 'Recipe'}</h3>
            <p className="text-sm text-[var(--text-secondary)]">
              {new Date(meal.date).toLocaleDateString('en-US', { 
                weekday: 'long', 
                month: 'short', 
                day: 'numeric' 
              })} • {meal.meal_type.charAt(0).toUpperCase() + meal.meal_type.slice(1)}
            </p>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto space-y-4">
          {analysis ? (
            <>
              {/* Description */}
              {analysis.base_description && (
                <div>
                  <p className="text-[var(--text-secondary)]">{analysis.base_description}</p>
                </div>
              )}

              {/* Safety Score */}
              {analysis.safety_score !== undefined && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Safety Score:</span>
                  <span className={`px-2 py-1 rounded-full text-sm font-semibold ${
                    analysis.safety_score >= 80 ? 'bg-green-100 text-green-700' :
                    analysis.safety_score >= 50 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {analysis.safety_score}%
                  </span>
                </div>
              )}

              {/* Warnings */}
              {analysis.warnings && analysis.warnings.length > 0 && (
                <div className="bg-red-50 rounded-lg p-3">
                  <h4 className="font-semibold text-red-700 mb-2">⚠️ Warnings</h4>
                  <ul className="space-y-1">
                    {analysis.warnings.map((warning, i) => (
                      <li key={i} className="text-sm text-red-600">• {warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Adaptations */}
              {analysis.adaptations && analysis.adaptations.length > 0 && (
                <div className="bg-[var(--accent-green)]/10 rounded-lg p-3">
                  <h4 className="font-semibold text-[var(--accent-green-dark)] mb-2">✨ Suggested Adaptations</h4>
                  <ul className="space-y-1">
                    {analysis.adaptations.map((adaptation, i) => (
                      <li key={i} className="text-sm text-[var(--text-secondary)]">• {adaptation}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Nutrition */}
              {analysis.nutrition_per_serving && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <h4 className="font-semibold mb-2">📊 Nutrition per Serving</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {analysis.nutrition_per_serving.calories && (
                      <div>Calories: <span className="font-medium">{analysis.nutrition_per_serving.calories}</span></div>
                    )}
                    {analysis.nutrition_per_serving.protein && (
                      <div>Protein: <span className="font-medium">{analysis.nutrition_per_serving.protein}</span></div>
                    )}
                    {analysis.nutrition_per_serving.carbs && (
                      <div>Carbs: <span className="font-medium">{analysis.nutrition_per_serving.carbs}</span></div>
                    )}
                    {analysis.nutrition_per_serving.fat && (
                      <div>Fat: <span className="font-medium">{analysis.nutrition_per_serving.fat}</span></div>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="text-center text-[var(--text-secondary)] py-8">
              No recipe details available
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <Link 
            href="/recipes" 
            className="w-full btn-secondary flex items-center justify-center gap-2"
            onClick={onClose}
          >
            <Utensils className="w-5 h-5" />
            View All Saved Recipes
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function PlannerPage() {
  return (
    <ProtectedRoute>
      <PlannerContent />
    </ProtectedRoute>
  );
}
