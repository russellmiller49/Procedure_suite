const MESSAGES: Record<string, string> = {
  stale_revision: "This case changed since you opened it. Reload before saving.",
  stale_approval: "This draft changed. Reload and review before approval.",
  approval_context_mismatch: "Only the current draft can be approved.",
  approval_review_required: "Resolve before approval:",
  evidence_span_mismatch: "An evidence excerpt no longer matches its source document.",
  evidence_context_mismatch: "Evidence points at a document outside this case.",
  event_date_required: "Enter the procedure date before saving.",
  revision_invalid: "The draft fails the launch contract:",
  claude_not_configured: "Claude is not configured on the server (set ANTHROPIC_API_KEY).",
  case_label_exists: "A case with this label already exists.",
};

export async function api<T = unknown>(path: string, method = "GET", body?: unknown): Promise<T> {
  const response = await fetch("/api/v1/workbench" + path, {
    method,
    cache: "no-store",
    headers: body === undefined ? {} : {"Content-Type": "application/json"},
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    const detail = result.detail;
    const code: string = typeof detail === "string" ? detail : detail?.code || `HTTP ${response.status}`;
    const errors = Array.isArray(detail?.errors)
      ? " " + detail.errors.map((e: any) => (typeof e === "string" ? e : `${(e.loc || []).join("/")}: ${e.msg}`)).join("; ").replaceAll("_", " ")
      : "";
    throw new Error((MESSAGES[code] || code.replaceAll("_", " ")) + errors);
  }
  return response.json();
}
