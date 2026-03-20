'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Sparkles, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { validateRecipeText } from '@/lib/validation';
import RecipeAnalysisDisplay from '@/components/RecipeAnalysisDisplay';
import { RecipeAnalysis, FamilyProfile } from '@/lib/types';

const MAX_RECIPE_LENGTH = 15000;

const SAMPLE_RECIPES = [
  'Spaghetti Carbonara with eggs, bacon, parmesan cheese, and black pepper',
  'Chicken stir fry with soy sauce, garlic, ginger, bell peppers, and rice',
  'Tiramisu with ladyfingers, mascarpone cheese, espresso, cocoa powder, and eggs',
  'Honey glazed salmon with asparagus and lemon butter sauce',
  'Peanut butter cookies with chocolate chips',
  'Classic beef burger with cheddar cheese, lettuce, tomato, and pickles on a brioche bun',
];

export default function AdaptRecipe() {
  const [recipe, setRecipe] = useState('');
  const [analysis, setAnalysis] = useState<RecipeAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<FamilyProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await api.getFamilyProfile();
      setProfile(data);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load profile:', error);
      }
    }
  };

  const handleAnalyze = async () => {
    if (!recipe.trim() || !profile) return;

    const validationError = validateRecipeText(recipe);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await api.analyzeRecipe(recipe, profile);
      setAnalysis(result);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to analyze recipe:', error);
      }
      setError('Failed to analyze recipe. Please check your API connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSurprise = () => {
    const randomRecipe = SAMPLE_RECIPES[Math.floor(Math.random() * SAMPLE_RECIPES.length)];
    setRecipe(randomRecipe);
  };

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
        <h1 className="text-3xl font-bold mb-2">Adapt a Recipe</h1>
        <p className="text-[var(--text-secondary)]">
          Paste a recipe or type a dish name to check if it&apos;s safe for your family
        </p>
      </div>

      {/* Recipe Input Card */}
      <div className="card">
        <label className="block text-sm font-medium mb-2">
          Recipe or dish name
        </label>
        <textarea
          value={recipe}
          onChange={(e) => {
            if (e.target.value.length <= MAX_RECIPE_LENGTH) {
              setRecipe(e.target.value);
            }
          }}
          placeholder="Type a dish name (e.g., 'chicken curry', 'pasta carbonara') or paste a full recipe with ingredients..."
          className="w-full h-48 p-4 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] resize-none text-[var(--text-primary)]"
          maxLength={MAX_RECIPE_LENGTH}
        />
        <div className="flex justify-end mt-1">
          <span className={`text-xs ${recipe.length > MAX_RECIPE_LENGTH * 0.9 ? 'text-red-500' : 'text-[var(--text-secondary)]'}`}>
            {recipe.length.toLocaleString()}/{MAX_RECIPE_LENGTH.toLocaleString()}
          </span>
        </div>
        
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
            className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>🔍 Check for My Family</>
            )}
          </button>
        </div>

        {/* Warnings */}
        {!profile?.members.length && (
          <p className="mt-3 text-sm text-[var(--accent-red)] text-center">
            ⚠️ Please add family members first to analyze recipes
          </p>
        )}

        {error && (
          <p className="mt-3 text-sm text-red-600 text-center">
            {error}
          </p>
        )}

        <p className="mt-4 text-xs text-[var(--text-secondary)] text-center">
          Works with dish names, ingredient lists, or full recipes
        </p>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <RecipeAnalysisDisplay analysis={analysis} recipeText={recipe} />
      )}

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by LLM
      </p>
    </div>
  );
}
