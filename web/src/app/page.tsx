"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import RecipeCard from "@/components/RecipeCard";
import type { RecipeResult, SearchResponse } from "@/types/recipes";
import { llmGenerateRecipes, type LlmRecipe } from "@/lib/llm";

export default function Home() {
  const [q, setQ] = useState("");               // ingredients
  const [cuisine, setCuisine] = useState("");   // cuisine
  const [calCap, setCalCap] = useState<number | "">(""); // calorie cap
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<RecipeResult[]>([]);
  const [llmRecipes, setLlmRecipes] = useState<LlmRecipe[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function runSearch() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get<SearchResponse>("/recipes/search", {
        params: { q, max_time: 20, limit: 2 },
      });
      setResults(data.results ?? []);
    } catch {
      setError("Couldn’t load saved recipes. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function runGenerate() {
    setLoading(true);
    setError(null);
    try {
      const ingredients = q.split(",").map(s => s.trim()).filter(Boolean);
      const recipes = await llmGenerateRecipes({
        ingredients,
        cuisine: cuisine || undefined,
        calorie_cap: calCap ? Number(calCap) : undefined,
        count: 2,
      });
      setLlmRecipes(recipes);
    } catch {
      setError("AI generation failed. Check your LLM server and try again.");
    } finally {
      setLoading(false);
    }
  }

  // hit Enter to generate
  function onEnter(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") runGenerate();
  }

  return (
    <main className="min-h-screen flex flex-col items-center">
      
      <section className="w-full max-w-6xl pt-16 pb-6 px-6 flex flex-col items-center text-center">
        <motion.h1
          className="text-3xl md:text-5xl font-semibold tracking-tight"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <motion.span
            // Subtle flash / shimmer without changing your color palette
            animate={{ textShadow: [
              "0 0 0px rgba(255,255,255,0.0)",
              "0 0 12px rgba(255,255,255,0.08)",
              "0 0 0px rgba(255,255,255,0.0)"
            ] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
          >
            Digital Dietician.AI
          </motion.span>
        </motion.h1>

        {/* Inputs stack, centered like ChatGPT */}
        <div className="w-full max-w-2xl mt-6 space-y-2">
          <input
            className="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-4 py-3 outline-none focus:border-neutral-600"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={onEnter}
            placeholder="Tell me what you’re craving-Ill whip up a recipe just for you."
            aria-label="Ingredients"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <input
              className="bg-neutral-900 border border-neutral-800 rounded-xl px-4 py-2 outline-none focus:border-neutral-600"
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
              onKeyDown={onEnter}
              placeholder="Cuisine (optional)"
              aria-label="Cuisine"
            />
            <input
              type="number"
              className="bg-neutral-900 border border-neutral-800 rounded-xl px-4 py-2 outline-none focus:border-neutral-600"
              value={calCap}
              onChange={(e) =>
                setCalCap(e.target.value === "" ? "" : parseInt(e.target.value, 10))
              }
              onKeyDown={onEnter}
              placeholder="Calorie cap (optional)"
              aria-label="Calorie cap"
              min={0}
            />
          </div>

          {/* Buttons stack like ChatGPT: big primary + small secondary label underneath */}
          <div className="flex flex-col items-center gap-1 pt-2">
            <button
              onClick={runGenerate}
              disabled={loading}
              className="px-6 py-3 rounded-xl bg-white text-black disabled:opacity-60"
            >
              {loading ? "Generating…" : "Let’s Diet"}
            </button>
            <button
              onClick={runSearch}
              disabled={loading}
              className="text-xs opacity-80 hover:opacity-100 underline underline-offset-4 disabled:opacity-50"
            >
              {loading ? "Loading saved recipes…" : "Saved recipes"}
            </button>
          </div>
        </div>

        {error && (
          <div className="w-full max-w-2xl mt-4 rounded-xl border border-red-800 bg-red-900/20 text-red-200 px-4 py-2">
            {error}
          </div>
        )}
      </section>

      {/* AI results */}
      {llmRecipes.length > 0 && (
        <section className="w-full max-w-6xl px-6 space-y-2">
          <h2 className="text-lg font-semibold">AI suggestions</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {llmRecipes.map((rec, i) => (
              <div key={i} className="rounded-2xl border border-neutral-800 p-4 bg-neutral-900/40">
                <h3 className="text-xl font-semibold mb-1">{rec.title}</h3>
                {rec.cuisine && <div className="text-xs opacity-70 mb-2">{rec.cuisine} cuisine</div>}
                <div className="text-xs opacity-80 mb-2">
                  {rec.macros.calories} kcal · P{rec.macros.protein} C{rec.macros.carbs} F{rec.macros.fat}
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-1">Ingredients</h4>
                    <ul className="list-disc pl-5 space-y-1 text-sm">
                      {rec.ingredients.map((it, idx) => <li key={idx}>{it}</li>)}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Instructions</h4>
                    <ol className="list-decimal pl-5 space-y-1 text-sm">
                      {rec.instructions.map((s, idx) => <li key={idx}>{s}</li>)}
                    </ol>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Saved results */}
      <section className="w-full max-w-6xl px-6 mt-8 mb-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((r) => (
            <RecipeCard key={`${r.id}-${r.score ?? r.title}`} r={r} />
          ))}
        </div>
      </section>
    </main>
  );
}
