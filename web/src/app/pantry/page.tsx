"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { PantryItemIn, PantryItemOut } from "@/types/pantry";

export default function PantryPage() {
  const [items, setItems] = useState<PantryItemOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState<PantryItemIn>({ name: "", quantity: 1, unit: "unit" });
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.get<PantryItemOut[]>("/pantry/list");
      setItems(data);
    } catch (e: any) {
      setError("Failed to load pantry");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function addItem(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setError(null);
    try {
      await api.post("/pantry/add", {
        name: form.name.trim(),
        quantity: form.quantity ?? 1,
        unit: form.unit || "unit",
        expiry_date: form.expiry_date || null,
      });
      setForm({ name: "", quantity: 1, unit: "unit" });
      await load();
    } catch (e: any) {
      setError("Failed to add item");
    }
  }

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">Pantry</h1>

      <form onSubmit={addItem} className="grid md:grid-cols-5 gap-2 items-end">
        <div className="md:col-span-2">
          <label className="block text-xs opacity-70 mb-1">Name</label>
          <input
            className="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="e.g., egg, rice, paneer"
            required
          />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Qty</label>
          <input
            type="number"
            className="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
            value={form.quantity ?? 1}
            onChange={(e) => setForm({ ...form, quantity: parseFloat(e.target.value || "1") })}
            min={0}
            step="0.5"
          />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Unit</label>
          <input
            className="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
            value={form.unit || "unit"}
            onChange={(e) => setForm({ ...form, unit: e.target.value })}
            placeholder="unit / g / ml / piece"
          />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Expiry (optional)</label>
          <input
            type="date"
            className="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-2"
            value={(form.expiry_date as string) || ""}
            onChange={(e) => setForm({ ...form, expiry_date: e.target.value })}
          />
        </div>
        <div className="md:col-span-5 flex gap-2">
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-white text-black"
            disabled={!form.name.trim()}
          >
            Add Item
          </button>
          <button
            type="button"
            onClick={load}
            className="px-4 py-2 rounded-xl border border-neutral-700"
          >
            Refresh
          </button>
        </div>
      </form>

      {loading && <p className="mt-4">Loading…</p>}
      {error && <p className="mt-4 text-red-400">{error}</p>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3 mt-6">
        {items.map((it) => (
          <div key={it.id} className="rounded-2xl border border-neutral-800 p-4 bg-neutral-900/40">
            <div className="flex items-center justify-between">
              <div className="font-semibold">{it.name}</div>
              <div className="text-xs opacity-70">{it.quantity} {it.unit}</div>
            </div>
            {it.expiry_date && (
              <div className="text-xs opacity-80 mt-1">Expires: {it.expiry_date}</div>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
