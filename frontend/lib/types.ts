export enum Role {
  ADULT = "Adult",
  CHILD = "Child",
  BABY = "Baby"
}

export enum ConditionType {
  DIABETES = "Diabetes",
  HIGH_URIC_ACID = "High Uric Acid",
  HYPERTENSION = "Hypertension",
  HEART_DISEASE = "Heart Disease",
  KIDNEY_DISEASE = "Kidney Disease",
  CELIAC = "Celiac (Gluten-Free)",
  LACTOSE_INTOLERANCE = "Lactose Intolerance",
  PEANUT_ALLERGY = "Peanut Allergy"
}

export interface HealthCondition {
  type: ConditionType;
  enabled: boolean;
  notes?: string;
}

export interface FamilyMember {
  id: string;
  name: string;
  avatar: string;
  role: Role;
  conditions: HealthCondition[];
  custom_restrictions: string[];
  preferences?: Record<string, unknown>;
}

export interface FamilyProfile {
  members: FamilyMember[];
}

export enum VerdictType {
  SAFE = "safe",
  NEEDS_ADAPTATION = "needs_adaptation",
  NOT_RECOMMENDED = "not_recommended"
}

export interface Substitution {
  original: string;
  replacement: string;
  reason: string;
}

export interface Adaptation {
  modifications: string[];
  substitutions: Substitution[];
  preparation_changes: string[];
}

export interface MemberVerdict {
  member_id: string;
  member_name: string;
  verdict: VerdictType;
  reasons: string[];
  concerns: string[];
  adaptations?: Adaptation;
  nutritional_notes?: string;
}

export interface RecipeAnalysis {
  dish_name: string;
  base_description: string;
  overall_safety: string;
  member_verdicts: MemberVerdict[];
  general_tips: string[];
}

// Scan types
export interface IngredientConcern {
  ingredient: string;
  affected_members: string[];
  reason: string;
  severity: 'low' | 'medium' | 'high';
}

export interface ScanResult {
  product_name: string;
  extracted_ingredients: string[];
  overall_safety: string;
  concerns: IngredientConcern[];
  safe_for_all: string[];
  recommendations: string[];
}

// Pantry types
export interface PantryItem {
  id: number;
  name: string;
  category?: string;
  added_at?: string;
}

export interface RecipeSuggestion {
  name: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  prep_time: string;
  matching_ingredients: string[];
  additional_ingredients: string[];
  safety_notes: string;
  family_friendly_score: number;
}

export interface RecipeSuggestionsResponse {
  suggestions: RecipeSuggestion[];
  tips: string[];
}

// Auth types
export interface User {
  id: string;
  email: string;
  name: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
}

export interface UserUpdate {
  name?: string;
  email?: string;
}

export interface PasswordUpdate {
  current_password: string;
  new_password: string;
}

// Saved Recipe types
export interface SavedRecipe {
  id: string;
  dish_name: string;
  recipe_text?: string;
  analysis?: RecipeAnalysis;
  is_favorite: boolean;
  notes?: string;
  tags: string[];
  created_at?: string;
}

export interface SaveRecipeRequest {
  dish_name: string;
  recipe_text: string;
  analysis: RecipeAnalysis;
  tags?: string[];
  notes?: string;
}

export interface UpdateRecipeRequest {
  is_favorite?: boolean;
  notes?: string;
  tags?: string[];
}

export interface SavedRecipesListResponse {
  recipes: SavedRecipe[];
  total: number;
}

// Shopping List types
export interface ShoppingItem {
  id?: number;
  ingredient: string;
  quantity?: string;
  category?: string;
  is_checked: boolean;
  source_recipe_id?: string;
}

export interface ShoppingList {
  id: string;
  name: string;
  items: ShoppingItem[];
  created_at?: string;
  completed_at?: string;
}

export interface CreateShoppingListRequest {
  name: string;
  items?: ShoppingItem[];
}

export interface GenerateShoppingListRequest {
  name: string;
  recipe_ids: string[];
}

export interface AddItemRequest {
  ingredient: string;
  quantity?: string;
  category?: string;
}

export interface UpdateItemRequest {
  is_checked?: boolean;
  quantity?: string;
}

export interface ShoppingListsResponse {
  lists: ShoppingList[];
  total: number;
}

// Meal Plan types
export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface PlannedMeal {
  id?: number;
  plan_id?: string;
  recipe_id: string;
  date: string; // YYYY-MM-DD
  meal_type: MealType;
  servings: number;
  notes?: string;
  dish_name?: string;
  analysis?: RecipeAnalysis;
}

export interface MealPlan {
  id: string;
  week_start: string;
  meals: PlannedMeal[];
  created_at?: string;
}

export interface AddMealRequest {
  recipe_id: string;
  date: string;
  meal_type: MealType;
  servings?: number;
  notes?: string;
}

export interface UpdateMealRequest {
  recipe_id?: string;
  date?: string;
  meal_type?: MealType;
  servings?: number;
  notes?: string;
}

export interface GenerateShoppingFromPlanRequest {
  list_name: string;
}

// Barcode types
export interface NutritionInfo {
  energy_kcal?: number;
  fat?: number;
  saturated_fat?: number;
  carbohydrates?: number;
  sugars?: number;
  fiber?: number;
  proteins?: number;
  salt?: number;
  sodium?: number;
}

export interface BarcodeProduct {
  barcode: string;
  name: string;
  brand: string;
  quantity: string;
  categories: string[];
  ingredients_text: string;
  ingredients_list: string[];
  allergens: string[];
  allergens_text: string;
  nutrition: NutritionInfo;
  nutriscore?: string;
  nova_group?: number;
  image_url?: string;
  image_small_url?: string;
}

export interface BarcodeAnalysisResponse {
  product: BarcodeProduct;
  overall_safety: string;
  concerns: IngredientConcern[];
  safe_for_all: string[];
  recommendations: string[];
}
