'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Plus, Trash2, Sparkles, Loader2, X } from 'lucide-react';
import { api } from '@/lib/api';
import { PantryItem, RecipeSuggestionsResponse } from '@/lib/types';
import RecipeSuggestions from '@/components/RecipeSuggestions';

const SAMPLE_INGREDIENTS = [
  'Chicken breast', 'Rice', 'Onion', 'Garlic', 'Tomatoes', 
  'Olive oil', 'Salt', 'Pepper', 'Eggs', 'Milk'
];

export default function PantryPage() {
  const [items, setItems] = useState<PantryItem[]>([]);
  const [newItem, setNewItem] = useState('');
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState<RecipeSuggestionsResponse | null>(null);
  const [suggestingLoading, setSuggestingLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPantryItems();
  }, []);

  const loadPantryItems = async () => {
    try {
      const data = await api.getPantryItems();
      setItems(data);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load pantry:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItem.trim()) return;

    try {
      const item = await api.addPantryItem(newItem.trim());
      setItems([item, ...items]);
      setNewItem('');
      setSuggestions(null);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to add item:', err);
      }
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    try {
      await api.deletePantryItem(itemId);
      setItems(items.filter(i => i.id !== itemId));
      setSuggestions(null);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to delete item:', err);
      }
    }
  };

  const handleClearPantry = async () => {
    if (!confirm('Clear all items from your pantry?')) return;
    
    try {
      await api.clearPantry();
      setItems([]);
      setSuggestions(null);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to clear pantry:', err);
      }
    }
  };

  const handleTrySample = async () => {
    for (const ingredient of SAMPLE_INGREDIENTS) {
      try {
        const item = await api.addPantryItem(ingredient);
        setItems(prev => [item, ...prev]);
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.error('Failed to add sample item:', err);
        }
      }
    }
    setSuggestions(null);
  };

  const handleGetSuggestions = async () => {
    setSuggestingLoading(true);
    setError(null);

    try {
      const result = await api.suggestRecipes();
      setSuggestions(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get suggestions');
    } finally {
      setSuggestingLoading(false);
    }
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
        <h1 className="text-3xl font-bold mb-2">My Pantry</h1>
        <p className="text-[var(--text-secondary)]">
          Track your ingredients and get recipe suggestions
        </p>
      </div>

      {/* Add Ingredient */}
      <div className="card">
        <form onSubmit={handleAddItem} className="flex gap-2">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add an ingredient (e.g., chicken, rice, tomatoes)"
            className="flex-1 p-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)]"
          />
          <button
            type="submit"
            disabled={!newItem.trim()}
            className="btn-primary px-4 disabled:opacity-50"
          >
            <Plus className="w-5 h-5" />
          </button>
        </form>

        {/* Quick Actions */}
        <div className="flex gap-2 mt-4">
          <button
            onClick={handleTrySample}
            className="btn-secondary text-sm"
            disabled={loading}
          >
            Try Sample
          </button>
          {items.length > 0 && (
            <button
              onClick={handleClearPantry}
              className="text-sm text-red-600 hover:text-red-700 px-3"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Pantry Items */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">
          🥗 Your Ingredients ({items.length})
        </h2>

        {loading ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-[var(--text-secondary)]" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-[var(--text-secondary)] text-center py-8">
            Your pantry is empty. Add some ingredients to get started!
          </p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-2 bg-[var(--background)] px-3 py-2 rounded-full group"
              >
                <span className="text-sm">{item.name}</span>
                <button
                  onClick={() => handleDeleteItem(item.id)}
                  className="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Find Recipes Button */}
        {items.length > 0 && (
          <button
            onClick={handleGetSuggestions}
            disabled={suggestingLoading}
            className="w-full btn-primary mt-6 flex items-center justify-center gap-2"
          >
            {suggestingLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Finding recipes...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Find Recipes with These Ingredients
              </>
            )}
          </button>
        )}

        {error && (
          <p className="mt-4 text-sm text-red-600 text-center">{error}</p>
        )}
      </div>

      {/* Recipe Suggestions */}
      {suggestions && <RecipeSuggestions suggestions={suggestions} />}

      {/* Tips */}
      <div className="card bg-[var(--accent-yellow)]/30">
        <h3 className="font-semibold mb-2">💡 Tips</h3>
        <ul className="text-sm space-y-1 text-[var(--text-secondary)]">
          <li>• Add ingredients you have at home</li>
          <li>• The more ingredients you add, the better suggestions you&apos;ll get</li>
          <li>• Recipe suggestions consider your family&apos;s dietary needs</li>
        </ul>
      </div>

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by Google Gemini AI
      </p>
    </div>
  );
}
