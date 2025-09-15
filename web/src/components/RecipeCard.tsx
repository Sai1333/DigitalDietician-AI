import Link from "next/link";
export default function RecipeCard({ r }: { r: any }) {
    const protein = Math.round(r.macros?.protein || 0);
    const calories = Math.round(r.macros?.calories || 0);
    const fat = Math.round(r.macros?.fat || 0);
    const scorePct = Math.round((r.score || 0) * 100);
  
    return (
        <div className="rounded-2xl border border-neutral-800 p-4 bg-neutral-900/40 backdrop-blur hover:border-neutral-700 transition">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold truncate pr-3">
            <Link href={`/recipe/${r.id}`} className="hover:underline">
              {r.title}
            </Link>
          </h3>
          <div className="flex items-center gap-3">
            <span className="text-xs opacity-80">{r.time_minutes ?? 15} min</span>
            <div className="w-10 h-10 rounded-full grid place-items-center border border-neutral-700">
              <span className="text-xs font-semibold">{scorePct}</span>
            </div>
          </div>
        </div>
  
        {r.explanation && <div className="text-xs mt-1 opacity-80">{r.explanation}</div>}
  
        <div className="flex gap-2 mt-3">
          <span className="text-xs px-2 py-1 rounded-full border border-neutral-800 bg-neutral-900/60">
            Prot {protein}g
          </span>
          <span className="text-xs px-2 py-1 rounded-full border border-neutral-800 bg-neutral-900/60">
            Cal {calories}
          </span>
          <span className="text-xs px-2 py-1 rounded-full border border-neutral-800 bg-neutral-900/60">
            Fat {fat}g
          </span>
        </div>
  
        {r.fit && (
          <div className="mt-2 text-xs opacity-80">
            Fit: Ing {r.fit.ingredients} · Time {r.fit.time} · Nut {r.fit.nutrition}
            {typeof r.fit.query === "number" ? <> · Query {r.fit.query}</> : null}
          </div>
        )}
      </div>
    );
  }
  