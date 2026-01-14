import { 
  FamilyProfile, 
  FamilyMember, 
  RecipeAnalysis, 
  ScanResult, 
  PantryItem, 
  RecipeSuggestionsResponse,
  User,
  AuthResponse,
  LoginCredentials,
  RegisterData,
  UserUpdate,
  PasswordUpdate,
  SavedRecipe,
  SaveRecipeRequest,
  UpdateRecipeRequest,
  SavedRecipesListResponse,
  ShoppingList,
  ShoppingItem,
  CreateShoppingListRequest,
  GenerateShoppingListRequest,
  AddItemRequest,
  UpdateItemRequest,
  ShoppingListsResponse,
  MealPlan,
  PlannedMeal,
  AddMealRequest,
  UpdateMealRequest,
  GenerateShoppingFromPlanRequest,
  BarcodeProduct,
  BarcodeAnalysisResponse
} from './types';

// Validate API URL is set
const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    console.error('NEXT_PUBLIC_API_URL environment variable is required');
  }
  throw new Error('NEXT_PUBLIC_API_URL environment variable is required. Please set it in your .env.local file.');
}

// Token management
const TOKEN_KEY = 'mealadapt_token';
const REFRESH_TOKEN_KEY = 'mealadapt_refresh_token';

// Flag to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const setToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
};

export const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setRefreshToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
};

export const removeRefreshToken = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

export const removeAllTokens = (): void => {
  removeToken();
  removeRefreshToken();
};

// Helper to get auth headers
const getAuthHeaders = (): Record<string, string> => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

  // Refresh the access token using the refresh token
export const refreshAccessToken = async (): Promise<boolean> => {
  // If already refreshing, wait for that to complete
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    removeAllTokens();
    return false;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const res = await fetchWithTimeout(`${API_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (!res.ok) {
        removeAllTokens();
        return false;
      }

      const result = await res.json();
      setToken(result.access_token);
      setRefreshToken(result.refresh_token);
      return true;
    } catch {
      removeAllTokens();
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
};

// Request timeout helper
const fetchWithTimeout = async (
  url: string,
  options: RequestInit = {},
  timeout: number = 30000
): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout - please try again');
    }
    throw error;
  }
};

// Wrapper for authenticated fetch with automatic token refresh and retry logic
const authenticatedFetch = async (
  url: string,
  options: RequestInit = {},
  retries: number = 2
): Promise<Response> => {
  // First attempt with current token
  const headers = {
    ...options.headers,
    ...getAuthHeaders()
  };

  let res: Response;
  try {
    res = await fetchWithTimeout(url, { ...options, headers });
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('timeout')) {
        throw new Error('Request timed out. Please check your connection and try again.');
      }
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        throw new Error('Network error. Please check your internet connection.');
      }
    }
    throw error;
  }

  // If unauthorized, try to refresh token and retry
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry with new token
      const newHeaders = {
        ...options.headers,
        ...getAuthHeaders()
      };
      try {
        res = await fetchWithTimeout(url, { ...options, headers: newHeaders });
      } catch (error) {
        if (error instanceof Error && error.message.includes('timeout')) {
          throw new Error('Request timed out. Please check your connection and try again.');
        }
        throw error;
      }
    }
  }

  // Retry logic for 5xx errors
  if (res.status >= 500 && res.status < 600 && retries > 0) {
    // Wait before retry (exponential backoff)
    await new Promise(resolve => setTimeout(resolve, 1000 * (3 - retries)));
    return authenticatedFetch(url, options, retries - 1);
  }

  return res;
};

export const api = {
  // Auth endpoints
  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const res = await fetchWithTimeout(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Registration failed');
      }
      const result = await res.json();
      setToken(result.access_token);
      setRefreshToken(result.refresh_token);
      return result;
    } catch (error) {
      if (error instanceof Error && error.message.includes('timeout')) {
        throw new Error('Request timed out. Please check your connection and try again.');
      }
      if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
        throw new Error('Network error. Please check your internet connection.');
      }
      throw error;
    }
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const res = await fetchWithTimeout(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Invalid email or password');
      }
      const result = await res.json();
      setToken(result.access_token);
      setRefreshToken(result.refresh_token);
      return result;
    } catch (error) {
      if (error instanceof Error && error.message.includes('timeout')) {
        throw new Error('Request timed out. Please check your connection and try again.');
      }
      if (error instanceof Error && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
        throw new Error('Network error. Please check your internet connection.');
      }
      throw error;
    }
  },

  async logout(): Promise<void> {
    const token = getToken();
    if (token) {
      try {
        await fetchWithTimeout(`${API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: { ...getAuthHeaders() }
        });
      } catch {
        // Ignore logout errors
      }
    }
    removeAllTokens();
  },

  async getCurrentUser(): Promise<User | null> {
    const token = getToken();
    if (!token) return null;
    
    const res = await authenticatedFetch(`${API_URL}/api/auth/me`);
    if (!res.ok) {
      if (res.status === 401) {
        removeAllTokens();
        return null;
      }
      throw new Error('Failed to get user');
    }
    return res.json();
  },

  async updateProfile(data: UserUpdate): Promise<User> {
    const res = await authenticatedFetch(`${API_URL}/api/auth/me`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update profile');
    }
    return res.json();
  },

  async changePassword(data: PasswordUpdate): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/auth/me/password`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to change password');
    }
  },

  async deleteAccount(): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/auth/me`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to delete account');
    }
    removeAllTokens();
  },

  // Family endpoints
  async getFamilyProfile(): Promise<FamilyProfile> {
    const res = await authenticatedFetch(`${API_URL}/api/family/profile`);
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async createFamilyProfile(profile: FamilyProfile): Promise<FamilyProfile> {
    const res = await authenticatedFetch(`${API_URL}/api/family/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    });
    if (!res.ok) throw new Error('Failed to create profile');
    return res.json();
  },

  async addMember(member: FamilyMember): Promise<FamilyMember> {
    const res = await authenticatedFetch(`${API_URL}/api/family/member`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(member)
    });
    if (!res.ok) throw new Error('Failed to add member');
    return res.json();
  },

  async updateMember(memberId: string, member: FamilyMember): Promise<FamilyMember> {
    const res = await authenticatedFetch(`${API_URL}/api/family/member/${memberId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(member)
    });
    if (!res.ok) throw new Error('Failed to update member');
    return res.json();
  },

  async deleteMember(memberId: string): Promise<{ message: string }> {
    const res = await authenticatedFetch(`${API_URL}/api/family/member/${memberId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete member');
    return res.json();
  },

  // Recipe endpoints
  async analyzeRecipe(recipeText: string, familyProfile: FamilyProfile): Promise<RecipeAnalysis> {
    const res = await authenticatedFetch(`${API_URL}/api/recipe/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipe_text: recipeText,
        family_profile: familyProfile
      })
    });
    if (!res.ok) throw new Error('Failed to analyze recipe');
    return res.json();
  },

  // Scan endpoints
  async scanIngredientLabel(file: File): Promise<ScanResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await authenticatedFetch(`${API_URL}/api/scan/analyze`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to scan ingredients');
    }
    return res.json();
  },

  // Pantry endpoints
  async getPantryItems(): Promise<PantryItem[]> {
    const res = await authenticatedFetch(`${API_URL}/api/pantry/items`);
    if (!res.ok) throw new Error('Failed to fetch pantry items');
    return res.json();
  },

  async addPantryItem(name: string, category?: string): Promise<PantryItem> {
    const res = await authenticatedFetch(`${API_URL}/api/pantry/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, category })
    });
    if (!res.ok) throw new Error('Failed to add item');
    return res.json();
  },

  async deletePantryItem(itemId: number): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/pantry/items/${itemId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to delete item');
  },

  async clearPantry(): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/pantry/items`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Failed to clear pantry');
  },

  async suggestRecipes(): Promise<RecipeSuggestionsResponse> {
    const res = await authenticatedFetch(`${API_URL}/api/pantry/suggest-recipes`, {
      method: 'POST'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to get suggestions');
    }
    return res.json();
  },

  // Saved Recipes endpoints
  async getSavedRecipes(favoritesOnly: boolean = false): Promise<SavedRecipesListResponse> {
    const url = new URL(`${API_URL}/api/recipes/saved`);
    if (favoritesOnly) {
      url.searchParams.set('favorites_only', 'true');
    }
    const res = await authenticatedFetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch saved recipes');
    return res.json();
  },

  async getSavedRecipe(recipeId: string): Promise<SavedRecipe> {
    const res = await authenticatedFetch(`${API_URL}/api/recipes/saved/${recipeId}`);
    if (!res.ok) throw new Error('Failed to fetch recipe');
    return res.json();
  },

  async saveRecipe(data: SaveRecipeRequest): Promise<SavedRecipe> {
    const res = await authenticatedFetch(`${API_URL}/api/recipes/saved`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to save recipe');
    }
    return res.json();
  },

  async updateSavedRecipe(recipeId: string, data: UpdateRecipeRequest): Promise<SavedRecipe> {
    const res = await authenticatedFetch(`${API_URL}/api/recipes/saved/${recipeId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update recipe');
    }
    return res.json();
  },

  async deleteSavedRecipe(recipeId: string): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/recipes/saved/${recipeId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to delete recipe');
    }
  },

  // Shopping List endpoints
  async getShoppingLists(): Promise<ShoppingListsResponse> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists`);
    if (!res.ok) throw new Error('Failed to fetch shopping lists');
    return res.json();
  },

  async getShoppingList(listId: string): Promise<ShoppingList> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists/${listId}`);
    if (!res.ok) throw new Error('Failed to fetch shopping list');
    return res.json();
  },

  async createShoppingList(data: CreateShoppingListRequest): Promise<ShoppingList> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to create shopping list');
    }
    return res.json();
  },

  async generateShoppingList(data: GenerateShoppingListRequest): Promise<ShoppingList> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to generate shopping list');
    }
    return res.json();
  },

  async addShoppingItem(listId: string, data: AddItemRequest): Promise<ShoppingItem> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists/${listId}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to add item');
    }
    return res.json();
  },

  async updateShoppingItem(itemId: number, data: UpdateItemRequest): Promise<ShoppingItem> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/items/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update item');
    }
    return res.json();
  },

  async deleteShoppingItem(itemId: number): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/items/${itemId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to delete item');
    }
  },

  async deleteShoppingList(listId: string): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists/${listId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to delete shopping list');
    }
  },

  async completeShoppingList(listId: string): Promise<ShoppingList> {
    const res = await authenticatedFetch(`${API_URL}/api/shopping/lists/${listId}/complete`, {
      method: 'POST'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to complete shopping list');
    }
    return res.json();
  },

  // Meal Plan endpoints
  async getMealPlan(week?: string): Promise<MealPlan> {
    const url = new URL(`${API_URL}/api/meal-plans`);
    if (week) {
      url.searchParams.set('week', week);
    }
    const res = await authenticatedFetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch meal plan');
    return res.json();
  },

  async addPlannedMeal(data: AddMealRequest): Promise<PlannedMeal> {
    const res = await authenticatedFetch(`${API_URL}/api/meal-plans/meals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to add meal');
    }
    return res.json();
  },

  async updatePlannedMeal(mealId: number, data: UpdateMealRequest): Promise<PlannedMeal> {
    const res = await authenticatedFetch(`${API_URL}/api/meal-plans/meals/${mealId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to update meal');
    }
    return res.json();
  },

  async deletePlannedMeal(mealId: number): Promise<void> {
    const res = await authenticatedFetch(`${API_URL}/api/meal-plans/meals/${mealId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to remove meal');
    }
  },

  async generateShoppingFromPlan(planId: string, data: GenerateShoppingFromPlanRequest): Promise<ShoppingList> {
    const res = await authenticatedFetch(`${API_URL}/api/meal-plans/${planId}/generate-shopping`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to generate shopping list');
    }
    return res.json();
  },

  // Barcode endpoints
  async lookupBarcode(barcode: string): Promise<BarcodeProduct> {
    const res = await authenticatedFetch(`${API_URL}/api/barcode/${barcode}`);
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Product not found');
    }
    return res.json();
  },

  async analyzeBarcode(barcode: string, familyProfile: FamilyProfile): Promise<BarcodeAnalysisResponse> {
    const res = await authenticatedFetch(`${API_URL}/api/barcode/${barcode}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(familyProfile)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to analyze product');
    }
    return res.json();
  }
};
