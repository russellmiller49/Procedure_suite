 
Phase 0 — Guardrails, flags, and measurements
Objective
Make changes safely, allow quick rollback, and measure improvements at each phase.
Codex tasks
1.	Add modules/infra/settings.py
o	Centralize env flags (examples):
	SKIP_WARMUP (bool)
	BACKGROUND_WARMUP (bool)
	WAIT_FOR_READY_S (float, default 0)
	CPU_WORKERS (int, default 1)
	LLM_CONCURRENCY (int, default 2–4)
	LLM_TIMEOUT_S (float)
	ENABLE_REDIS_CACHE / ENABLE_LLM_CACHE (bool)
2.	Add modules/infra/perf.py
o	timed(name) context manager logging durations
o	optional structured log helper
3.	Add scripts/smoke_run.sh
o	start server
o	hit /health, /ready
o	hit a minimal “predict/coder” request
4.	Ensure no PHI is logged:
o	add a helper safe_log_text(text)->str that redacts or hashes (optional)
Acceptance
•	Smoke script passes locally.
•	Every phase can be toggled via env flags.
 
Phase 1 — Liveness vs readiness + warmup that never hangs users
Objective
Fix Railway deploy timeouts and prevent the first user from hanging on a model-loading lock.
Core idea 
•	/health = liveness (always 200, fast)
•	/ready = readiness (200 only after models loaded)
•	Main endpoints fail fast (503 + Retry-After) while warming up.
•	Avoid blocking the event loop on a threading.Lock by never acquiring it inside async def.
Codex tasks
1.	In FastAPI app init:
o	Add app state:
	app.state.model_ready: bool = False
	app.state.model_error: Optional[str] = None
	app.state.ready_event: asyncio.Event
2.	Implement lifespan warmup behavior:
o	If SKIP_WARMUP=true: don’t warm
o	Else if BACKGROUND_WARMUP=true: start background warmup using loop.run_in_executor(...) and return immediately.
3.	In the warmup thread:
o	call your lazy loaders (get_spacy_model(), get_ml_model())
o	on success: set app.state.model_ready=True and signal:
	loop.call_soon_threadsafe(app.state.ready_event.set)
o	on failure: set model_error
4.	Endpoints:
o	GET /health: always 200, includes "ready": app.state.model_ready
o	GET /ready: 200 only if ready, else 503
5.	Add a shared dependency (or decorator) require_ready(request) used by any heavy endpoint:
o	If ready: continue
o	If not ready:
	if WAIT_FOR_READY_S > 0: await asyncio.wait_for(app.state.ready_event.wait(), timeout=WAIT_FOR_READY_S)
	else immediately raise HTTPException(503, headers={"Retry-After": "10"})
Acceptance
•	Railway can mark service up via /health even while warming.
•	First user request never hangs; returns 503 quickly while warming.
 
Phase 2 — CPU-bound sklearn/spaCy offload (no event-loop blocking)
Objective
Ensure sklearn .predict() and spaCy processing never block the event loop.
Guidance 
await on a sync CPU function does not help; you must move it into a thread (or process).
•	On Railway (memory constrained), prefer threads (shared memory), not process pools.
•	Limit underlying BLAS/OpenMP threads to avoid oversubscription. scikit-learn docs explicitly call out OMP_NUM_THREADS, MKL_NUM_THREADS, OPENBLAS_NUM_THREADS. Scikit-learn
Codex tasks
1.	Create a dedicated CPU executor:
o	In lifespan: app.state.cpu_executor = ThreadPoolExecutor(max_workers=settings.CPU_WORKERS)
o	Default CPU_WORKERS=1 for Railway (safe baseline).
2.	Create helper:
o	modules/infra/executors.py
	async def run_cpu(app, fn, *args, **kwargs) that uses:
	loop.run_in_executor(app.state.cpu_executor, functools.partial(fn,*args,**kwargs))
3.	Wrap CPU-bound steps:
o	sklearn inference: await run_cpu(app, model.predict, [note])
o	spaCy: await run_cpu(app, nlp, text)
4.	Ensure your lazy model getters are sync but only called:
o	in warmup thread OR
o	inside run_cpu (so the lock never blocks the event loop)
5.	Add env vars in Railway/Docker (Phase 6 will finalize):
o	OMP_NUM_THREADS=1
o	MKL_NUM_THREADS=1
o	OPENBLAS_NUM_THREADS=1
o	optionally: NUMEXPR_NUM_THREADS=1, VECLIB_MAXIMUM_THREADS=1
Acceptance
•	Under concurrent requests, server still answers /health quickly.
•	CPU inference doesn’t stall all requests.
 
Phase 3 — LLM calls: immediate async + concurrency limit + backoff (no “batch wait”)
Objective
Make LLM calls truly async, manage rate limits, and avoid adding artificial latency.
Guidance Don’t add a 100ms “wait for batching” for real-time completions; most chat APIs don’t accept multiple prompts in one request anyway, and the wait just adds latency.
•	Use immediate async requests, with:
o	a global semaphore (smooth spikes, prevent 429)
o	retries with exponential backoff + jitter
Codex tasks
1.	Build an async LLM client:
o	modules/llm/client.py
o	Use httpx.AsyncClient stored on app.state.llm_http
o	Set timeouts from settings
2.	Add a global LLM semaphore:
o	app.state.llm_sem = asyncio.Semaphore(settings.LLM_CONCURRENCY)
3.	Wrap every outbound LLM call:
o	async with app.state.llm_sem: ...
4.	Add retry policy:
o	on 429 / transient 5xx: exponential backoff with jitter
o	cap total retry time to LLM_TIMEOUT_S
5.	(Optional but useful) Add a provider-agnostic “429 handler”:
o	if rate-limited, return 503 upstream (or partial result) with "retry_after" info
Acceptance
•	Concurrent notes do not trigger “token spikes” as badly (semaphore smooths).
•	No artificial 100ms buffering.
 
Phase 4 — Parallelize the 3-agent pipeline safely (and reduce LLM spikes)
Objective
Reduce end-to-end latency while respecting dependencies and rate limits.
Guidance 
•	If _extract_basic_fields is just “date/name/etc.” it can run on raw text and doesn’t need parsed output (unless parsing is doing OCR or redaction).
•	Parallel calls increase TPM spikes → more 429s. Mitigate with:
o	semaphore (Phase 3)
o	or “merge strategy”: fold basic extraction into the parse prompt
Codex tasks
1.	Restructure pipeline scheduling:
o	Start Parse and BasicExtract concurrently:
	parse_task = create_task(parse(note))
	basic_task = create_task(extract_basic(note)) # against raw text
o	Await parse only:
	parsed = await parse_task
o	Start summarize immediately:
	summary = await summarize(parsed)
o	Await basics later:
	basics = await basic_task
o	Finally structure:
	structured = await structure(summary, basics)
2.	Decide extraction implementation:
o	Prefer deterministic extractors (regex/rules) for basics → zero extra LLM load.
o	If using LLM for basics:
	keep it behind semaphore
	consider merging into parse prompt (single call)
3.	Add per-stage timing metrics (Phase 0 utility):
o	parse_duration, summarize_duration, structure_duration, total_duration
4.	Add “rate-limit aware” behavior:
o	if basics LLM gets 429, proceed with empty basics but keep parse/summarize results.
Acceptance
•	Latency improves vs strict sequential.
•	Under load, LLM calls remain bounded by semaphore.
 
Phase 5 — Orchestrator concurrency: overlap CPU prep with I/O, but keep CPU in threads
Objective
Make the full coding pipeline concurrency-safe:
•	CPU work in threads
•	I/O work async
•	overlap independent steps
Codex tasks
1.	Convert orchestrator entrypoint to async:
o	async def predict_codes(note: str) -> ...
2.	Run CPU inference in run_cpu(...) (Phase 2)
3.	Overlap cheap steps with inference or with LLM calls when safe:
o	difficulty_task = create_task(classify(...))
o	context_task = create_task(prepare_rule_context(...))
4.	Add a “time budget”:
o	if LLM not done by LLM_TIMEOUT_S, return ML/rules best-effort with a flag
Acceptance
•	Under concurrency, throughput scales without event-loop stalls.
•	You can degrade gracefully when LLM is slow.
 
Phase 6 — Railway deploy strategy: workers, memory, and env tuning
Objective
Avoid memory blowups and keep deploy stable.
Critical update 
•	Uvicorn --workers uses spawn (not prefork), so each worker is a fresh process → memory duplication is expected. uvicorn.dev
•	If you need prefork copy-on-write sharing, that’s Gunicorn --preload territory (with caveats about threads/connections pre-fork). Rippling
Codex tasks
1.	Default command for Railway:
o	uvicorn ... --workers 1 --limit-concurrency <N>
o	rely on async + threadpool for concurrency
2.	Add env vars (Railway project variables):
o	OMP_NUM_THREADS=1
o	MKL_NUM_THREADS=1
o	OPENBLAS_NUM_THREADS=1 Scikit-learn
3.	Optional “higher RAM plan” mode:
o	Add a second start command using Gunicorn prefork + preload:
	Only if you can confirm memory headroom and you’re careful not to start threads pre-fork
o	Note: Uvicorn docs indicate the legacy uvicorn.workers integration is deprecated and recommends uvicorn-worker package. uvicorn.dev
o	Codex should implement this as an alternate Procfile / start script, not the default.
4.	Health checks:
o	Configure Railway health check to hit /health (not /ready).
Acceptance
•	No OOM on deploy.
•	No long cold-start deploy failures.
 
Phase 7 — Caching (LLM + ML) with PHI-safe keys
Objective
Reduce repeat work, improve speed and cost.
Codex tasks
1.	Add cache interface + memory cache (always on).
2.	Add optional Redis cache behind flag.
3.	Cache LLM outputs:
o	key = sha256(model + prompt + prompt_version)
o	store response text (or parsed JSON)
4.	Cache ML predictions:
o	key = sha256(normalized_note_text)
5.	Ensure no raw note text is stored as keys or logs.
Acceptance
•	Repeat requests return faster.
•	Cache can be disabled instantly.
 
Phase 8 —Streaming for “doctor waiting” UX 
Objective
Improve perceived latency (time-to-first-token) without batching.
Codex tasks
1.	Add SSE or streaming endpoint variant (if your frontend supports it).
2.	If provider supports streaming:
o	stream chunks to client
3.	If provider doesn’t:
o	stream progress events (stage timings / “parse done”, “summary done”, etc.)
Acceptance
•	User sees early feedback quickly.
 
Explicitly DO NOT implement 
1.	Do not add “BatchLLMProcessor” with max_wait_ms for chat/completions.
2.	Only consider batching for:
o	embeddings endpoints (many support list inputs)
o	offline bulk jobs (provider batch APIs)

