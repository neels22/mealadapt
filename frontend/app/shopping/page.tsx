'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Check, 
  ShoppingCart, 
  Loader2,
  Sparkles,
  ChevronDown,
  ChevronUp,
  X
} from 'lucide-react';
import { api } from '@/lib/api';
import { ShoppingList, ShoppingItem, SavedRecipe } from '@/lib/types';
import ProtectedRoute from '@/components/ProtectedRoute';

const CATEGORIES = [
  { value: 'produce', label: '🥬 Produce', color: 'bg-green-100 text-green-700' },
  { value: 'dairy', label: '🥛 Dairy', color: 'bg-blue-100 text-blue-700' },
  { value: 'meat', label: '🥩 Meat', color: 'bg-red-100 text-red-700' },
  { value: 'seafood', label: '🐟 Seafood', color: 'bg-cyan-100 text-cyan-700' },
  { value: 'pantry', label: '🥫 Pantry', color: 'bg-amber-100 text-amber-700' },
  { value: 'bakery', label: '🍞 Bakery', color: 'bg-orange-100 text-orange-700' },
  { value: 'frozen', label: '🧊 Frozen', color: 'bg-indigo-100 text-indigo-700' },
  { value: 'beverages', label: '🥤 Beverages', color: 'bg-purple-100 text-purple-700' },
  { value: 'other', label: '📦 Other', color: 'bg-gray-100 text-gray-700' },
];

function getCategoryStyle(category?: string) {
  const cat = CATEGORIES.find(c => c.value === category);
  return cat?.color || 'bg-gray-100 text-gray-700';
}

function getCategoryLabel(category?: string) {
  const cat = CATEGORIES.find(c => c.value === category);
  return cat?.label || category || 'Other';
}

function ShoppingContent() {
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [newItemInput, setNewItemInput] = useState('');
  const [expandedLists, setExpandedLists] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadLists();
  }, []);

  const loadLists = async () => {
    try {
      setLoading(true);
      const response = await api.getShoppingLists();
      setLists(response.lists);
      // Auto-expand first list if exists
      if (response.lists.length > 0 && expandedLists.size === 0) {
        setExpandedLists(new Set([response.lists[0].id]));
      }
    } catch (error) {
      console.error('Failed to load shopping lists:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleListExpanded = (listId: string) => {
    const newExpanded = new Set(expandedLists);
    if (newExpanded.has(listId)) {
      newExpanded.delete(listId);
    } else {
      newExpanded.add(listId);
    }
    setExpandedLists(newExpanded);
  };

  const handleToggleItem = async (listId: string, item: ShoppingItem) => {
    if (!item.id) return;
    
    try {
      const updated = await api.updateShoppingItem(item.id, { is_checked: !item.is_checked });
      setLists(lists.map(list => {
        if (list.id === listId) {
          return {
            ...list,
            items: list.items.map(i => i.id === item.id ? { ...i, is_checked: updated.is_checked } : i)
          };
        }
        return list;
      }));
    } catch (error) {
      console.error('Failed to update item:', error);
    }
  };

  const handleDeleteItem = async (listId: string, itemId: number) => {
    try {
      await api.deleteShoppingItem(itemId);
      setLists(lists.map(list => {
        if (list.id === listId) {
          return {
            ...list,
            items: list.items.filter(i => i.id !== itemId)
          };
        }
        return list;
      }));
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const handleAddItem = async (listId: string, ingredient: string) => {
    if (!ingredient.trim()) return;
    
    try {
      const item = await api.addShoppingItem(listId, { ingredient: ingredient.trim() });
      setLists(lists.map(list => {
        if (list.id === listId) {
          return {
            ...list,
            items: [...list.items, item]
          };
        }
        return list;
      }));
      setNewItemInput('');
    } catch (error) {
      console.error('Failed to add item:', error);
    }
  };

  const handleDeleteList = async (listId: string) => {
    if (!confirm('Delete this shopping list?')) return;
    
    try {
      await api.deleteShoppingList(listId);
      setLists(lists.filter(l => l.id !== listId));
    } catch (error) {
      console.error('Failed to delete list:', error);
    }
  };

  // Group items by category
  const groupItemsByCategory = (items: ShoppingItem[]) => {
    const grouped: Record<string, ShoppingItem[]> = {};
    items.forEach(item => {
      const category = item.category || 'other';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(item);
    });
    return grouped;
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
        <h1 className="text-3xl font-bold mb-2">Shopping Lists</h1>
        <p className="text-[var(--text-secondary)]">
          Create and manage your grocery lists
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          <Plus className="w-5 h-5" />
          New List
        </button>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="btn-secondary flex-1 flex items-center justify-center gap-2"
        >
          <Sparkles className="w-5 h-5" />
          Generate from Recipes
        </button>
      </div>

      {/* Shopping Lists */}
      {loading ? (
        <div className="card flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-green)]" />
        </div>
      ) : lists.length === 0 ? (
        <div className="card text-center py-12">
          <ShoppingCart className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">No shopping lists yet</h3>
          <p className="text-[var(--text-secondary)] text-sm">
            Create a new list or generate one from your saved recipes
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {lists.map(list => {
            const isExpanded = expandedLists.has(list.id);
            const groupedItems = groupItemsByCategory(list.items);
            const checkedCount = list.items.filter(i => i.is_checked).length;
            const totalCount = list.items.length;
            
            return (
              <div key={list.id} className="card">
                {/* List Header */}
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleListExpanded(list.id)}
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{list.name}</h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      {checkedCount}/{totalCount} items checked
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteList(list.id);
                      }}
                      className="p-2 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-[var(--text-secondary)]" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-[var(--text-secondary)]" />
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                {totalCount > 0 && (
                  <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-[var(--accent-green)] transition-all"
                      style={{ width: `${(checkedCount / totalCount) * 100}%` }}
                    />
                  </div>
                )}

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="mt-4 space-y-4">
                    {/* Add Item Input */}
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newItemInput}
                        onChange={(e) => setNewItemInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleAddItem(list.id, newItemInput);
                          }
                        }}
                        placeholder="Add an item..."
                        className="flex-1 px-4 py-2 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] text-sm"
                      />
                      <button
                        onClick={() => handleAddItem(list.id, newItemInput)}
                        className="px-4 py-2 bg-[var(--accent-green)] text-[var(--text-primary)] rounded-full hover:bg-[#98C5AA] transition-colors"
                      >
                        <Plus className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Items by Category */}
                    {Object.entries(groupedItems).map(([category, items]) => (
                      <div key={category}>
                        <div className={`inline-block px-2 py-1 rounded-full text-xs font-medium mb-2 ${getCategoryStyle(category)}`}>
                          {getCategoryLabel(category)}
                        </div>
                        <div className="space-y-2">
                          {items.map(item => (
                            <div 
                              key={item.id}
                              className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                                item.is_checked ? 'bg-gray-50' : 'bg-[var(--background)]'
                              }`}
                            >
                              <button
                                onClick={() => handleToggleItem(list.id, item)}
                                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                                  item.is_checked 
                                    ? 'bg-[var(--accent-green)] border-[var(--accent-green)]' 
                                    : 'border-gray-300 hover:border-[var(--accent-green)]'
                                }`}
                              >
                                {item.is_checked && <Check className="w-4 h-4 text-white" />}
                              </button>
                              <div className="flex-1">
                                <span className={item.is_checked ? 'line-through text-gray-400' : ''}>
                                  {item.ingredient}
                                </span>
                                {item.quantity && (
                                  <span className="ml-2 text-sm text-[var(--text-secondary)]">
                                    ({item.quantity})
                                  </span>
                                )}
                              </div>
                              <button
                                onClick={() => item.id && handleDeleteItem(list.id, item.id)}
                                className="p-1 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}

                    {list.items.length === 0 && (
                      <p className="text-center text-[var(--text-secondary)] py-4">
                        No items yet. Add some above!
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateListModal 
          onClose={() => setShowCreateModal(false)} 
          onCreate={(list) => {
            setLists([list, ...lists]);
            setExpandedLists(new Set([list.id, ...expandedLists]));
            setShowCreateModal(false);
          }}
        />
      )}

      {/* Generate Modal */}
      {showGenerateModal && (
        <GenerateListModal 
          onClose={() => setShowGenerateModal(false)} 
          onGenerate={(list) => {
            setLists([list, ...lists]);
            setExpandedLists(new Set([list.id, ...expandedLists]));
            setShowGenerateModal(false);
          }}
        />
      )}

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by Google Gemini AI
      </p>
    </div>
  );
}

// Create List Modal
function CreateListModal({ 
  onClose, 
  onCreate 
}: { 
  onClose: () => void; 
  onCreate: (list: ShoppingList) => void;
}) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) return;
    
    setLoading(true);
    try {
      const list = await api.createShoppingList({ name: name.trim() });
      onCreate(list);
    } catch (error) {
      console.error('Failed to create list:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full">
        <h3 className="text-xl font-bold mb-4">Create New List</h3>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="List name (e.g., Weekly Groceries)"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] mb-4"
          autoFocus
        />
        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button 
            onClick={handleCreate} 
            disabled={loading || !name.trim()}
            className="btn-primary flex-1 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Generate List Modal
function GenerateListModal({ 
  onClose, 
  onGenerate 
}: { 
  onClose: () => void; 
  onGenerate: (list: ShoppingList) => void;
}) {
  const [name, setName] = useState('');
  const [recipes, setRecipes] = useState<SavedRecipe[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadRecipes();
  }, []);

  const loadRecipes = async () => {
    try {
      const response = await api.getSavedRecipes();
      setRecipes(response.recipes);
    } catch (error) {
      console.error('Failed to load recipes:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecipe = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleGenerate = async () => {
    if (!name.trim() || selectedIds.size === 0) return;
    
    setGenerating(true);
    try {
      const list = await api.generateShoppingList({
        name: name.trim(),
        recipe_ids: Array.from(selectedIds)
      });
      onGenerate(list);
    } catch (error) {
      console.error('Failed to generate list:', error);
      alert('Failed to generate shopping list. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-lg w-full max-h-[80vh] overflow-hidden flex flex-col">
        <h3 className="text-xl font-bold mb-4">Generate from Recipes</h3>
        
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="List name"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)] mb-4"
        />

        <p className="text-sm text-[var(--text-secondary)] mb-2">
          Select recipes to generate ingredients from:
        </p>

        <div className="flex-1 overflow-y-auto space-y-2 mb-4 max-h-60">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-[var(--accent-green)]" />
            </div>
          ) : recipes.length === 0 ? (
            <p className="text-center text-[var(--text-secondary)] py-8">
              No saved recipes yet. Save some recipes first!
            </p>
          ) : (
            recipes.map(recipe => (
              <div 
                key={recipe.id}
                onClick={() => toggleRecipe(recipe.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors border-2 ${
                  selectedIds.has(recipe.id)
                    ? 'border-[var(--accent-green)] bg-green-50'
                    : 'border-transparent bg-[var(--background)] hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                    selectedIds.has(recipe.id)
                      ? 'bg-[var(--accent-green)] border-[var(--accent-green)]'
                      : 'border-gray-300'
                  }`}>
                    {selectedIds.has(recipe.id) && <Check className="w-3 h-3 text-white" />}
                  </div>
                  <span className="font-medium">{recipe.dish_name}</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button 
            onClick={handleGenerate} 
            disabled={generating || !name.trim() || selectedIds.size === 0}
            className="btn-primary flex-1 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate ({selectedIds.size})
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ShoppingPage() {
  return (
    <ProtectedRoute>
      <ShoppingContent />
    </ProtectedRoute>
  );
}
