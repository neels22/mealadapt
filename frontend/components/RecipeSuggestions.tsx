import { RecipeSuggestionsResponse, RecipeSuggestion } from '@/lib/types';
import { Clock, ChefHat, Star, CheckCircle2, ShoppingCart } from 'lucide-react';

interface Props {
  suggestions: RecipeSuggestionsResponse;
}

const DIFFICULTY_CONFIG = {
  easy: { color: 'text-green-600', bg: 'bg-green-100', label: 'Easy' },
  medium: { color: 'text-yellow-600', bg: 'bg-yellow-100', label: 'Medium' },
  hard: { color: 'text-red-600', bg: 'bg-red-100', label: 'Hard' }
};

function RecipeCard({ recipe }: { recipe: RecipeSuggestion }) {
  const difficulty = DIFFICULTY_CONFIG[recipe.difficulty] || DIFFICULTY_CONFIG.medium;

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <h3 className="font-semibold text-lg">{recipe.name}</h3>
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={`w-4 h-4 ${
                i < recipe.family_friendly_score
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-200'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-[var(--text-secondary)] mb-3">{recipe.description}</p>

      {/* Meta */}
      <div className="flex items-center gap-4 mb-3">
        <span className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
          <Clock className="w-4 h-4" />
          {recipe.prep_time}
        </span>
        <span className={`text-xs px-2 py-1 rounded-full ${difficulty.bg} ${difficulty.color}`}>
          {difficulty.label}
        </span>
      </div>

      {/* Matching Ingredients */}
      <div className="mb-3">
        <p className="text-xs font-medium text-[var(--text-secondary)] mb-1 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3 text-green-500" />
          You have:
        </p>
        <div className="flex flex-wrap gap-1">
          {recipe.matching_ingredients.map((ing, i) => (
            <span key={i} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
              {ing}
            </span>
          ))}
        </div>
      </div>

      {/* Additional Ingredients */}
      {recipe.additional_ingredients.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-[var(--text-secondary)] mb-1 flex items-center gap-1">
            <ShoppingCart className="w-3 h-3 text-orange-500" />
            You&apos;ll need:
          </p>
          <div className="flex flex-wrap gap-1">
            {recipe.additional_ingredients.map((ing, i) => (
              <span key={i} className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                {ing}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Safety Notes */}
      {recipe.safety_notes && (
        <p className="text-xs text-[var(--text-secondary)] italic bg-[var(--background)] p-2 rounded-lg">
          💡 {recipe.safety_notes}
        </p>
      )}
    </div>
  );
}

export default function RecipeSuggestions({ suggestions }: Props) {
  return (
    <div className="card space-y-6">
      <div className="flex items-center gap-2">
        <ChefHat className="w-6 h-6 text-[var(--accent-green)]" />
        <h2 className="text-xl font-bold">Recipe Suggestions</h2>
      </div>

      {/* Recipe Cards */}
      <div className="space-y-4">
        {suggestions.suggestions.map((recipe, i) => (
          <RecipeCard key={i} recipe={recipe} />
        ))}
      </div>

      {/* Tips */}
      {suggestions.tips.length > 0 && (
        <div className="bg-[var(--accent-blue)]/30 p-4 rounded-xl">
          <h3 className="font-semibold mb-2">💡 Cooking Tips</h3>
          <ul className="text-sm space-y-1">
            {suggestions.tips.map((tip, i) => (
              <li key={i}>• {tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
