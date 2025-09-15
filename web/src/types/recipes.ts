// apps/api/web/src/types/recipes.ts

export interface RecipeResult {
    id: number;
    title: string;
    ingredients: string;
    time_minutes: number;
    macros?: {
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    };
    score?: number;
    explanation?: string;
  }
  
  export interface SearchResponse {
    results: RecipeResult[];
  }
  
  export interface SuggestResponse {
    results: RecipeResult[];
  }
  