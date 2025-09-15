import { api } from "@/lib/api";

export type LlmRecipe = {
  title: string;
  cuisine?: string | null;
  ingredients: string[];
  instructions: string[];
  macros: { calories: number; protein: number; carbs: number; fat: number };
};

export async function llmGenerateRecipes(input: {
  ingredients: string[];
  cuisine?: string;
  calorie_cap?: number;
  count?: number; // default 2
}) {
  const { data } = await api.post("/recipes/llm_generate", {
    ...input,
    count: input.count ?? 2,
  });

  if (Array.isArray((data as any)?.recipes)) return (data as any).recipes as LlmRecipe[];
  return [data as LlmRecipe]; // backwards-compatible
}
