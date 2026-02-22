export type UmlsSuggestEntry = {
  term: string;
  preferred_name: string;
  cui: string;
  categories: string[];
};

export async function fetchUmlsSuggest(
  q: string,
  opts?: { category?: string | null; limit?: number; signal?: AbortSignal },
): Promise<UmlsSuggestEntry[]> {
  const query = String(q ?? "").trim();
  if (!query) return [];

  const params = new URLSearchParams();
  params.set("q", query);
  if (opts?.category) params.set("category", String(opts.category));
  params.set("limit", String(Math.max(1, Math.min(50, Number(opts?.limit ?? 20)))));

  const resp = await fetch(`/api/v1/umls/suggest?${params.toString()}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal: opts?.signal,
  });

  if (!resp.ok) return [];
  const data = (await resp.json()) as unknown;
  if (!Array.isArray(data)) return [];

  const out: UmlsSuggestEntry[] = [];
  for (const item of data) {
    if (!item || typeof item !== "object") continue;
    const raw = item as Partial<UmlsSuggestEntry>;
    if (!raw.term || !raw.cui) continue;
    out.push({
      term: String(raw.term),
      preferred_name: String(raw.preferred_name ?? ""),
      cui: String(raw.cui),
      categories: Array.isArray(raw.categories) ? raw.categories.map((c) => String(c)) : [],
    });
  }
  return out;
}

