'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Heart, Search, Loader2, BookOpen } from 'lucide-react';
import { api } from '@/lib/api';
import { SavedRecipe } from '@/lib/types';
import SavedRecipeCard from '@/components/SavedRecipeCard';
import ProtectedRoute from '@/components/ProtectedRoute';

function RecipesContent() {
  const [recipes, setRecipes] = useState<SavedRecipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'favorites'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecipe, setSelectedRecipe] = useState<SavedRecipe | null>(null);

  useEffect(() => {
    loadRecipes();
  }, [filter]);

  const loadRecipes = async () => {
    try {
      setLoading(true);
      const response = await api.getSavedRecipes(filter === 'favorites');
      setRecipes(response.recipes);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load recipes:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (id: string, isFavorite: boolean) => {
    try {
      await api.updateSavedRecipe(id, { is_favorite: isFavorite });
      // Update local state
      setRecipes(recipes.map(r => 
        r.id === id ? { ...r, is_favorite: isFavorite } : r
      ));
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to update recipe:', error);
      }
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteSavedRecipe(id);
      setRecipes(recipes.filter(r => r.id !== id));
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to delete recipe:', error);
      }
    }
  };

  const handleRecipeClick = (recipe: SavedRecipe) => {
    setSelectedRecipe(recipe);
  };

  // Filter recipes by search query
  const filteredRecipes = recipes.filter(recipe => 
    recipe.dish_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    recipe.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

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
        <h1 className="text-3xl font-bold mb-2">My Recipes</h1>
        <p className="text-[var(--text-secondary)]">
          Your saved recipe collection
        </p>
      </div>

      {/* Search and Filter */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search recipes or tags..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] text-sm"
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-[var(--accent-green)] text-[var(--text-primary)]'
                  : 'bg-gray-100 text-[var(--text-secondary)] hover:bg-gray-200'
              }`}
            >
              All Recipes
            </button>
            <button
              onClick={() => setFilter('favorites')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors flex items-center gap-1 ${
                filter === 'favorites'
                  ? 'bg-red-100 text-red-600'
                  : 'bg-gray-100 text-[var(--text-secondary)] hover:bg-gray-200'
              }`}
            >
              <Heart className={`w-4 h-4 ${filter === 'favorites' ? 'fill-current' : ''}`} />
              Favorites
            </button>
          </div>
        </div>
      </div>

      {/* Recipe List */}
      {loading ? (
        <div className="card flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-green)]" />
        </div>
      ) : filteredRecipes.length === 0 ? (
        <div className="card text-center py-12">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">
            {filter === 'favorites' 
              ? 'No favorite recipes yet' 
              : searchQuery 
                ? 'No recipes match your search'
                : 'No saved recipes yet'
            }
          </h3>
          <p className="text-[var(--text-secondary)] text-sm mb-4">
            {filter === 'favorites'
              ? 'Heart your favorite recipes to see them here'
              : searchQuery
                ? 'Try a different search term'
                : 'Analyze a recipe and save it to your collection'
            }
          </p>
          {!searchQuery && filter === 'all' && (
            <Link href="/adapt" className="btn-primary inline-flex items-center gap-2">
              Adapt a Recipe
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-[var(--text-secondary)]">
            {filteredRecipes.length} recipe{filteredRecipes.length !== 1 ? 's' : ''}
          </p>
          {filteredRecipes.map(recipe => (
            <SavedRecipeCard
              key={recipe.id}
              recipe={recipe}
              onToggleFavorite={handleToggleFavorite}
              onDelete={handleDelete}
              onClick={handleRecipeClick}
            />
          ))}
        </div>
      )}

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by LLM
      </p>
    </div>
  );
}

export default function RecipesPage() {
  return (
    <ProtectedRoute>
      <RecipesContent />
    </ProtectedRoute>
  );
}
