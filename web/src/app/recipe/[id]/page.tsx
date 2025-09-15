"use client";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { llmGenerateRecipes, type LlmRecipe } from "@/lib/llm";

interface Macros {
  calories?: number;
  protein?: number;
  carbs?: number;
  fat?: number;
}
interface Recipe {
  id: number;
  title: string;
  description?: string;
  ingredients?: string;     // comma-separated in DB
  instructions?: string;    // newline separated in DB
  time_minutes?: number;
  macros?: Macros;          // may be absent for some rows
  cuisine?: string | null;  // optional if you store it
}

function inferCuisineFromTitle(title: string): string | undefined {
  const t = title.toLowerCase();
  const known = ["thai","indian","italian","mexican","japanese","chinese","french","mediterranean","korean"];
  return known.find(k => t.includes(k)) || undefined;
}

export default function RecipeDetail() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI suggestions
  const [aiLoading, setAiLoading] = useState(false);
  const [aiRecipes, setAiRecipes] = useState<LlmRecipe[]>([]);
  const [aiError, setAiError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.get<Recipe>(`/recipes/${params.id}`);
        if ((data as any).detail === "Not found") {
          setError("Recipe not found.");
        } else {
          setRecipe(data);
        }
      } catch {
        setError("Failed to load recipe.");
      } finally {
        setLoading(false);
      }
    }
    if (params?.id) load();
  }, [params?.id]);

  // Parse fields
  const macros = recipe?.macros ?? {};
  const ingredients = useMemo(
    () => (recipe?.ingredients || "")
      .split(",")
      .map(s => s.trim())
      .filter(Boolean),
    [recipe?.ingredients]
  );
  const instructions = useMemo(
    () => (recipe?.instructions || "")
      .split(/\r?\n/)
      .map(s => s.trim())
      .filter(Boolean),
    [recipe?.instructions]
  );

  // Kick off AI suggestions after recipe loads
  useEffect(() => {
    async function gen() {
      if (!recipe) return;
      const cuisine = recipe.cuisine || inferCuisineFromTitle(recipe.title);
      const calorie_cap = typeof macros.calories === "number" ? Math.round(macros.calories) : undefined;
      if (ingredients.length === 0) return;

      setAiLoading(true);
      setAiError(null);
      try {
        const recs = await llmGenerateRecipes({
          ingredients,
          cuisine,
          calorie_cap,
          count: 2,
        });
        setAiRecipes(recs);
      } catch (e) {
        setAiError("Could not generate similar recipes.");
      } finally {
        setAiLoading(false);
      }
    }
    gen();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recipe?.id]); // run once when recipe is loaded

  if (loading) {
    return <main className="max-w-3xl mx-auto p-6">Loading…</main>;
  }
  if (error || !recipe) {
    return (
      <main className="max-w-3xl mx-auto p-6 space-y-4">
        <p className="opacity-80">{error ?? "Recipe not found."}</p>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 rounded-xl border border-neutral-700 hover:bg-neutral-800"
        >
          Go Back
        </button>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{recipe.title}</h1>
          <p className="text-sm opacity-70 mt-1">{recipe.time_minutes ?? 15} min</p>
          {recipe.description && <p className="mt-2 opacity-80">{recipe.description}</p>}
        </div>
        <div className="rounded-2xl border border-neutral-800 p-3 bg-neutral-900/40">
          <div className="text-xs opacity-70">Macros (approx)</div>
          <div className="text-sm mt-1">
            {Math.round(macros.calories || 0)} kcal · P {Math.round(macros.protein || 0)}g · C {Math.round(macros.carbs || 0)}g · F {Math.round(macros.fat || 0)}g
          </div>
        </div>
      </div>

      {/* Ingredients */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Ingredients</h2>
        <ul className="list-disc list-inside space-y-1 opacity-90">
          {ingredients.length > 0 ? (
            ingredients.map((it, i) => <li key={i}>{it}</li>)
          ) : (
            <li className="opacity-70">No ingredients listed.</li>
          )}
        </ul>
      </section>

      {/* Instructions */}
      <section>
        <h2 className="text-lg font-semibold mb-2">Instructions</h2>
        <ol className="list-decimal list-inside space-y-2 opacity-90">
          {instructions.length > 0 ? (
            instructions.map((ln, i) => <li key={i}>{ln}</li>)
          ) : (
            <li className="opacity-70">No instructions provided.</li>
          )}
        </ol>
      </section>

      {/* Actions */}
      <div className="flex gap-2">
        <button className="px-4 py-2 rounded-xl bg-white text-black hover:bg-neutral-200">Cooked 👍</button>
        <button className="px-4 py-2 rounded-xl border border-neutral-700 hover:bg-neutral-800">Not now 👎</button>
      </div>

      {/* AI Suggestions */}
      <section className="pt-4 border-t border-neutral-900">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">AI Similar Recipes</h2>
          {aiLoading && <span className="text-sm opacity-70">Generating…</span>}
        </div>

        {aiError && <p className="text-sm text-red-400 mt-2">{aiError}</p>}

        {aiRecipes.length > 0 && (
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            {aiRecipes.map((rec, idx) => (
              <div key={idx} className="rounded-2xl border border-neutral-800 p-4 bg-neutral-900/40">
                <h3 className="font-semibold">{rec.title}</h3>
                <div className="text-xs opacity-70 mt-1">
                  {rec.cuisine ? `${rec.cuisine} cuisine · ` : ""}{Math.round(rec.macros.calories)} kcal · P{Math.round(rec.macros.protein)} C{Math.round(rec.macros.carbs)} F{Math.round(rec.macros.fat)}
                </div>
                <div className="mt-2 grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs font-medium mb-1">Ingredients</div>
                    <ul className="list-disc pl-5 text-xs space-y-1">
                      {rec.ingredients.slice(0,5).map((i, j) => <li key={j}>{i}</li>)}
                    </ul>
                  </div>
                  <div>
                    <div className="text-xs font-medium mb-1">Steps</div>
                    <ol className="list-decimal pl-5 text-xs space-y-1">
                      {rec.instructions.slice(0,4).map((s, j) => <li key={j}>{s}</li>)}
                    </ol>
                  </div>
                </div>
                {/* Optional: a button to save to DB */}
                {/* <button className="mt-3 px-3 py-1.5 rounded-lg border border-neutral-700 text-xs">Save to My Recipes</button> */}
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
