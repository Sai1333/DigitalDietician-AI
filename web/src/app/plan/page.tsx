"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function PlanPage() {
  const [protein, setProtein] = useState(120);
  const [cap, setCap] = useState(1800);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);

  async function makePlan() {
    setLoading(true);
    try {
      const { data } = await api.get("/plan/day", { params: { protein_target: protein, calorie_cap: cap } });
      setData(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">Day Plan</h1>
      <div className="flex gap-2 items-center">
        <input type="number" className="bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
          value={protein} onChange={e=>setProtein(parseInt(e.target.value||"120",10))} />
        <input type="number" className="bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
          value={cap} onChange={e=>setCap(parseInt(e.target.value||"1800",10))} />
        <button onClick={makePlan} className="px-4 py-2 rounded-xl bg-white text-black" disabled={loading}>
          {loading ? "Planning…" : "Make Plan"}
        </button>
      </div>

      {data && (
        <div className="mt-6 space-y-3">
          <div className="text-sm opacity-80">
            Targets: {data.targets.calories} kcal, {data.targets.protein} g protein
          </div>
          {data.meals.map((m: any) => (
            <div key={m.id} className="rounded-2xl border border-neutral-800 p-4 bg-neutral-900/40">
              <div className="font-semibold">{m.title}</div>
              <div className="text-xs mt-1 opacity-80">
                {m.macros.calories} kcal · P {m.macros.protein}g · C {m.macros.carbs}g · F {m.macros.fat}g
              </div>
            </div>
          ))}
          <div className="text-sm font-semibold">
            Totals: {data.totals.calories} kcal · P {data.totals.protein}g · C {data.totals.carbs}g · F {data.totals.fat}g
          </div>
        </div>
      )}
    </main>
  );
}
