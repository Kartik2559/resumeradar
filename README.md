---
title: ResumeRadar
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

<<<<<<< HEAD
# ResumeRadar 📄

> Semantic resume-JD matching powered by Sentence-BERT — upload resumes, paste a job description, get instant match scores, skill gap analysis, and a ranked summary of all candidates.

**Live Demo:** [huggingface.co/spaces/Kartik-work/resumeradar](https://huggingface.co/spaces/Kartik-work/resumeradar)  
**GitHub:** [github.com/Kartik2559/resumeradar](https://github.com/Kartik2559/resumeradar)

---

## Table of Contents

- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Tech stack](#tech-stack)
- [Run locally](#run-locally)
- [Q&A — everything learned building this](#qa--everything-learned-building-this)
- [Limitations](#limitations)
- [Future scope](#future-scope)
- [Production roadmap](#production-roadmap)

---

## What it does

ResumeRadar is a semantic resume screening tool. Unlike keyword-based ATS systems that miss synonyms and context, ResumeRadar uses sentence embeddings to understand *meaning* — so "built scalable NLP pipelines" correctly matches "experience with large-scale text processing systems."

**Core features:**
- Upload one or multiple resume PDFs simultaneously
- First-page PDF preview for each uploaded resume
- Paste any job description as text
- Instant semantic match score (0–100%) per resume
- Matched skills and missing skills breakdown
- Verdict: Strong / Good / Weak / Poor match
- Summary table ranking all candidates by match score — sortable, comparable at a glance

---

## How it works

```
Resume PDF
    ↓ PyMuPDF extraction
Clean text (≤2048 chars)
    ↓ Sentence-BERT (all-MiniLM-L6-v2)
384-dimensional embedding vector
    ↓
                        ←——— JD text → Sentence-BERT → 384-dim vector
Cosine similarity between both vectors
    ↓
Match score (0.0 – 1.0) → percentage + verdict
    ↓
Keyword scan → matched skills vs missing skills
    ↓
Result dict → Streamlit UI
```

**Why semantic matching beats keyword matching:**

| Approach | "built NLP pipelines" vs "text processing experience" |
|---|---|
| Keyword match | 0% — no shared words |
| Semantic match | 78% — understands they mean the same thing |

---

## Architecture

```
app.py                          ← Streamlit UI + session state management
    ↓ calls
src/
    extractor.py                ← PDF → clean text + first-page preview image
    embedder.py                 ← text → 384-dim numpy vector (singleton cache)
    matcher.py                  ← cosine similarity + skill gap analysis
core/
    logger.py                   ← centralised structured logging (console + file)
config.py                       ← single source of truth for all settings
logs/                           ← daily rotating log files (gitignored)
```

**Dependency flow — one direction only:**
```
app.py → matcher.py → embedder.py → config.py
       → extractor.py              → core/logger.py
```

Each layer knows nothing about the layer above it. This means you can swap the embedding model in `config.py` and nothing else changes.

---

## Project structure

```
resumeradar/
├── src/
│   ├── __init__.py
│   ├── extractor.py        PDF text extraction + preview rendering
│   ├── embedder.py         Sentence-BERT singleton + embed function
│   └── matcher.py          Cosine similarity + skill analysis + verdict
├── core/
│   ├── __init__.py
│   └── logger.py           Configured once, imported everywhere
├── logs/                   Daily log files — app_YYYYMMDD.log
├── app.py                  Streamlit frontend
├── config.py               Constants + MatchConfig dataclass
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | 384-dim, fast, high quality, free |
| PDF extraction | PyMuPDF (fitz) | Fast, accurate, handles preview rendering |
| Similarity | numpy cosine similarity | No external dependency, full control |
| UI | Streamlit | Production-standard for ML demos |
| Logging | Python logging | Centralised, structured, file + console |
| Config | Python dataclasses | Type-safe, single source of truth |

---

## Run locally

```bash
# Clone
git clone https://github.com/Kartik2559/resumeradar
cd resumeradar

# Environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip3 install -r requirements.txt

# Run
streamlit run app.py
```

Opens at `http://localhost:8501`

**First run:** model downloads ~90MB automatically. Cached after that — subsequent runs are instant.

---

## Q&A — everything learned building this

Every concept below was learned by building this project from scratch, line by line.

---

### Embeddings

**Q: What is an embedding?**  
A: An embedding is a dense vector representation of text that captures semantic meaning — where similar meanings produce similar vectors. Unlike token IDs which are arbitrary numbers, embeddings encode relationships so that "love" and "adore" produce nearly identical vectors, while "love" and "database" are far apart.

**Q: Why 384 dimensions specifically?**  
A: 384 is the hidden size of all-MiniLM-L6-v2 — determined by its architecture (6 attention layers, 64 dims per head × 6 heads). It's a design tradeoff: 384 captures ~90% of BERT's quality (768 dims) at 50% the compute cost. You don't choose the size — the model decides it. We use `VECTOR_DIMENSIONS = 384` in config to validate and document it.

**Q: What is the difference between word embeddings and sentence embeddings?**  
A: Word embeddings (Word2Vec, GloVe) produce one static vector per word — "bank" gets the same vector in "river bank" and "bank account." Sentence-BERT produces one vector for the entire sentence after running attention across all tokens and mean-pooling, so context changes the representation. For comparing two documents semantically, sentence embeddings are significantly more accurate.

**Q: What is mean pooling?**  
A: After running all tokens through 6 attention layers, each token has its own 384-dim vector. Mean pooling averages all token vectors element-wise — `(token1 + token2 + ... + tokenN) / N` — producing one 384-dim vector representing the entire sentence. Sentence-BERT uses mean pooling by default because it outperforms CLS token pooling for similarity tasks.

**Q: How is Sentence-BERT different from the pipeline() we used in Week 1?**  
A: `pipeline("sentiment-analysis")` is a general-purpose wrapper for classification tasks — returns a label and score. `SentenceTransformer` is a specialist tool trained specifically for semantic similarity — returns raw numpy vectors ready for mathematical operations. pipeline uses CLS pooling; SBERT uses mean pooling. SBERT was fine-tuned on sentence pairs for similarity, which pipeline was not.

---

### Cosine Similarity

**Q: What is cosine similarity?**  
A: Cosine similarity measures the angle between two vectors — not their distance. Formula: `dot(A, B) / (norm(A) × norm(B))`. Result is between -1 and +1. Two vectors pointing the same direction = 1.0 (identical meaning). Perpendicular = 0.0 (unrelated). Opposite = -1.0 (rare in NLP).

**Q: Why cosine and not Euclidean distance?**  
A: Euclidean distance is affected by vector magnitude — a longer resume would appear "closer" to the JD just because it has more text. Cosine normalises by magnitude, so only direction matters. A 50-word resume and 500-word resume saying the same things get the same cosine score.

**Q: What is a zero vector and why does it cause a crash?**  
A: A zero vector is `[0, 0, 0, ..., 0]` — produced when text is empty or whitespace-only. `norm([0,0,...]) = 0`. Cosine formula divides by `norm(A) × norm(B)` — division by zero → crash. We guard against this: `if norm_a == 0 or norm_b == 0: return 0.0`.

**Q: What does np.clip do?**  
A: Clips a value to a range. `np.clip(value, -1.0, 1.0)` ensures the result never exceeds ±1.0 — floating point arithmetic can produce values like 1.0000002 due to rounding errors. Without clip, downstream percentage calculations would break.

**Q: What are other similarity methods besides cosine?**  
A: BM25 (keyword-based, no embeddings needed, very fast), Euclidean distance (good when magnitude matters), dot product (same as cosine when vectors are normalised), Manhattan distance (sparse vectors), Jaccard similarity (comparing sets, good for skill lists), MMR — Maximal Marginal Relevance (returns diverse results, not just most similar).

---

### PDF Extraction

**Q: Why PyMuPDF (fitz) and not unstructured.io?**  
A: PyMuPDF is lightweight, fast, and handles clean selectable-text PDFs perfectly — exactly what resumes are. unstructured.io handles OCR, scanned documents, tables, mixed content — 20+ dependencies for features we don't need. Right tool for the job. unstructured would be the choice for enterprise document pipelines in Week 3.

**Q: Why do we use a context manager (`with fitz.open()`) instead of `open()` + `close()`?**  
A: Context managers guarantee the file handle closes even if an exception occurs mid-extraction. Without closing, you leak OS file handles — open 1000 PDFs without closing = OS runs out of handles → crash. `with` makes cleanup automatic and exception-safe.

**Q: What is a temporary file and why do we need it?**  
A: Streamlit's `UploadedFile` gives us bytes in memory, no path on disk. PyMuPDF's `fitz.open()` needs a real file path. `tempfile.NamedTemporaryFile` creates a real file on disk with a guaranteed unique name, we write bytes to it, get a path, extract text, then delete it with `tmp_path.unlink()`. It's a bridge between in-memory bytes and disk-based file processing.

**Q: Why do we read `file.read()` once and store in `pdf_bytes`, not call it twice?**  
A: After `file.read()`, the file pointer moves to the end. A second `file.read()` returns `b""` — empty bytes. We store `pdf_bytes = file.read()` once and reuse that variable for both preview generation and temp file writing.

**Q: What is fitz.Matrix and what does (1.5, 1.5) mean?**  
A: Matrix is a transformation applied to the PDF page before rendering. The two numbers are X and Y scale factors. `(1.5, 1.5)` renders at 108 DPI — 1.5× the default 72 DPI. Sharp enough for readable preview, small enough in memory. `(3.0, 3.0)` would be print-quality but 9× larger in RAM.

---

### Architecture and Design

**Q: What is separation of concerns?**  
A: Each file has exactly one job. `extractor.py` knows about PDFs and nothing else. `embedder.py` knows about vectors and nothing else. `matcher.py` knows about comparison and nothing else. `app.py` knows about UI and nothing else. This means changing the embedding model only requires touching `embedder.py` — nothing else breaks.

**Q: Why does compute_match() accept strings not file paths?**  
A: To maintain single responsibility. matcher.py's job is comparing text — it should know nothing about file formats. Accepting strings means matcher can be tested with two plain strings without needing real PDFs, and can work with DOCX, images, or URLs in future by just changing the extractor — matcher stays untouched.

**Q: What is the Singleton pattern?**  
A: One shared instance used everywhere. We load the embedding model once (`_model = None` cache, set on first call) and return the same object on every subsequent call. Without this, every `embed_text()` call would reload 90MB from disk — adding 5–10 seconds per request.

**Q: What is the Accumulator pattern?**  
A: Start with an empty container (`rows = []`), add one item per loop iteration (`rows.append({...})`), use the full result after the loop (`pd.DataFrame(rows)`). More efficient than modifying a DataFrame inside a loop — appending to a list is O(1), DataFrame.append is O(n²).

**Q: Why two try/except blocks — one in extractor.py and one in app.py?**  
A: Two-layer error handling. The service layer (extractor) logs technical details with full context and re-raises. The UI layer (app.py) catches what was re-raised and shows a user-friendly message. Developer gets log entries with file paths and stack traces. User sees "Could not read this PDF — please try another file." Both get the right information.

**Q: What is lazy loading?**  
A: Loading a resource only when it's first needed, not at import time. If we put `model = SentenceTransformer(EMBEDDING_MODEL)` at module level, it loads 90MB whenever the file is imported — even in tests that don't need the model. Wrapping it in a function means it only loads when `embed_text()` is actually called.

---

### Python Concepts

**Q: What is a dataclass and when to use it vs a regular class?**  
A: A dataclass is a class primarily for holding data — Python auto-generates `__init__`, `__repr__`, and `__eq__` from the field declarations, eliminating boilerplate. Use a regular class when the object has complex behaviour and methods. Use a dataclass when the object's primary purpose is storing values with types. `MatchConfig` is a dataclass because it just holds threshold and count settings.

**Q: What is the difference between a module and a package?**  
A: A module is a single `.py` file. A package is a folder of modules with an `__init__.py` that makes it importable as a unit. `logging` is a module. `fastapi` is a package. "Library" is the casual umbrella term for both.

**Q: What are type annotations and why use them?**  
A: Declaring expected input and output types: `def embed_text(text: str) -> np.ndarray`. They serve as live documentation, enable IDE autocomplete, and allow static analysis tools like mypy to catch type errors before deployment. In production codebases at product companies they're enforced at code review.

**Q: What does `__name__` equal in different contexts?**  
A: When a file is run directly, `__name__ = "__main__"`. When imported as a module, `__name__` equals the module path: `"src.extractor"`, `"src.embedder"`, etc. We use `get_logger(__name__)` so log lines automatically show which file produced them.

**Q: What is tuple unpacking?**  
A: Assigning multiple variables from a sequence in one line. `col_left, col_right = st.columns(2)` unpacks the two-element list returned by `st.columns()` into two separate variables. Equivalent to `cols = st.columns(2); col_left = cols[0]; col_right = cols[1]` — but cleaner.

**Q: What does `not in` do in `if "resumes" not in st.session_state`?**  
A: Checks whether a key is absent from a dictionary (or any collection). Returns `True` if the key doesn't exist. Used here to initialise session_state variables exactly once — on first run when the key is absent. Subsequent reruns find the key already present and skip initialisation, preserving stored data.

---

### Session State and Streamlit

**Q: What is a session?**  
A: A temporary conversation between one user and the server — from when they open the app to when they close it. Like a restaurant visit: the waiter remembers your order (session state) during your visit, but forgets everything when you leave (session ends).

**Q: Why does Streamlit need session_state?**  
A: Streamlit reruns the entire script top-to-bottom on every user interaction — every button click, every keystroke, every file upload. Normal Python variables reset to their defaults on each rerun. `st.session_state` is a dictionary that survives reruns, persisting data across interactions within one session.

**Q: What does `key=` on a Streamlit widget do?**  
A: Creates a bidirectional sync between the widget and a session_state variable. The widget reads its initial value from session_state and automatically writes back to session_state when the user interacts with it. Without `key`, you'd have to manually update session_state after every interaction.

**Q: What is stateless vs stateful?**  
A: Stateless — same input always produces same output, no memory between calls (`cosine_similarity()`, `extract_text()`). Stateful — output depends on history, data persists (`session_state.resumes`, a database, a shopping cart). HTTP is stateless by design; session_state adds statefulness within one browser session.

---

### Logging

**Q: Why centralised logging in core/logger.py?**  
A: If every file configured logging independently, Python uses the first configuration it encounters and ignores the rest — producing inconsistent formatting and unpredictable behaviour. One centralised configuration means consistent format, level, and handlers across the entire application.

**Q: What are the logging levels in order?**  
A: DEBUG (10) → INFO (20) → WARNING (30) → ERROR (40) → CRITICAL (50). `setLevel(INFO)` means "show INFO and everything above — filter out DEBUG." Higher number = more serious = always shown when threshold is met.

**Q: Why log AND raise in the same except block?**  
A: The log captures technical details for the developer — file path, error message, timestamp — stored in the log file. The raise propagates the exception to the UI layer which shows the user a friendly message. Logging without raising means the caller thinks the operation succeeded. Raising without logging means you have no record of the failure.

**Q: What is `%(levelname)-8s` in the formatter?**  
A: String padding. `-8s` means left-align and pad to 8 characters. "INFO" (4 chars) becomes "INFO    " (8 chars). "WARNING" (7 chars) becomes "WARNING " (8 chars). This aligns log columns perfectly — essential when scanning thousands of lines at 3am debugging production.

---

### Production concepts

**Q: What is idempotency?**  
A: Calling a function 10 times produces the same result as calling it once. `if logger.handlers: return logger` makes logger setup idempotent — no duplicate handlers, no duplicate log lines, regardless of how many times `get_logger()` is called.

**Q: What is a resource leak?**  
A: Opening a resource (file, database connection, network socket) without closing it. The OS reserves memory and file handles indefinitely. Open 1000 PDFs without closing → OS exhausts file handle limit → crash. Context managers (`with`) prevent this by guaranteeing cleanup.

**Q: Why snake_case for dict keys not Title Case?**  
A: Python convention (PEP8) uses `snake_case` for variable names and dictionary keys. `"match_score"` not `"Match Score"`. Consistent casing prevents key mismatch bugs — `result["match_score"]` vs `result["Match Score"]` are different keys and one will raise a `KeyError`.

**Q: What is O(1) vs O(n) lookup?**  
A: O(1) — constant time — dictionary lookup by key. Doesn't matter if the dict has 10 or 10,000 items, lookup is instant. O(n) — linear time — list search. Must check every item until found. We use `dict` for `session_state.resumes` because we look up resumes by filename — O(1) is essential for responsiveness.

---

## Limitations

**Keyword list for skill extraction:**  
Skills are matched against a hardcoded `TECH_SKILLS` list. Skills not in the list are invisible to the gap analysis — "Kubernetes" would be missed if not in the list.

**English only:**  
all-MiniLM-L6-v2 was trained on English text. Resumes in Hindi, Hinglish, or other languages will produce poor embeddings and inaccurate scores.

**512 token limit:**  
DistilBERT-family models have a 512 token architectural limit. We truncate at ~2048 characters (~512 tokens) as a safety guard. Very long resumes lose content beyond this limit.

**Filename collision:**  
Two resumes with the same filename overwrite each other in session state. In production, unique IDs (UUID or timestamp) would be appended to filenames.

**Stateless session:**  
All data is lost when the browser tab closes. No user accounts, no persistent storage, no cross-session history.

**Scanned PDFs:**  
PyMuPDF extracts selectable text only. Scanned PDF images return empty text — OCR via Tesseract or Amazon Textract would be needed.

---

## Future scope

### Planned improvements (technical)

**1. Dynamic skill extraction from JD (no hardcoded list)**  
Replace the `TECH_SKILLS` keyword list with a proper skill extraction pipeline. Use a Named Entity Recognition (NER) model fine-tuned on job descriptions — `en_core_web_trf` from spaCy or a HuggingFace NER model — to extract skills directly from the JD. Then compare extracted JD skills against extracted resume skills. No manual list maintenance required.

**2. Analyze all resumes against same JD in one click**  
Add a "Analyze All" button that iterates through every resume in `session_state.resumes` and runs `compute_match()` for each. Show a progress bar (`st.progress()`) updating after each resume. Results populate the summary table automatically. Useful for bulk screening of 10+ candidates at once.

**3. Resume management — select, deselect, delete**  
Add checkboxes next to each resume in the selector. Multi-select allows analyzing a subset. A "Remove" button deletes the resume from `session_state.resumes`, `session_state.previews`, and `session_state.results` simultaneously. Prevents the summary table from accumulating stale results from removed candidates.

**4. Must-have skills section**  
Add a text input in the sidebar where the recruiter specifies non-negotiable skills — "Python, SQL, Git" — regardless of whether the JD mentions them. These are appended to `jd_skills` before the gap analysis runs. Any resume missing a must-have skill gets flagged with a red warning regardless of overall match score.

**5. Multilingual support**  
Swap `all-MiniLM-L6-v2` for `paraphrase-multilingual-MiniLM-L12-v2` — same architecture, trained on 50+ languages including Hindi. Resumes and JDs in any supported language would produce accurate semantic embeddings. Config change in one place: `EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"`.

**6. Batch PDF upload via folder**  
Allow uploading a ZIP file containing multiple PDFs. Extract the ZIP server-side, process each PDF, populate the summary table. Enables screening 100 resumes from a ZIP in one upload.

**7. Export results**  
Add a "Download Summary" button that exports the summary DataFrame as CSV or Excel using `df.to_csv()` / `df.to_excel()`. Recruiters can share ranked candidate lists with hiring managers.

**8. Confidence calibration**  
Raw cosine similarity scores are not probabilities. A score of 0.87 doesn't mean "87% likely to be hired." Add a calibration layer that maps raw scores to percentile ranks against a reference corpus of resume-JD pairs. Shows "Top 15% match" rather than raw score.

---

### Production SaaS roadmap

**Authentication and multi-tenancy**  
User accounts via Auth0 or Supabase Auth. Each user gets a `user_id`. All data (resumes, JDs, results) scoped to `user_id`. Multiple recruiters can use the same deployment with fully isolated data.

**Persistent storage**  
Replace session_state with persistent backends. Resumes stored as files in AWS S3 or Google Cloud Storage. Extracted text, embeddings, and results stored in PostgreSQL. Users can return to previous sessions and access historical analysis.

**Vector database for semantic search**  
Store all resume embeddings in Pinecone, Weaviate, or Chroma. When a new JD arrives, query the vector database for top-N semantically similar resumes across the entire candidate pool — not just uploaded ones. Enable "find candidates for this role" from historical applications.

**Async processing pipeline**  
Replace synchronous extraction + embedding with an async queue (Celery + Redis or AWS SQS). Uploading 50 PDFs triggers 50 async workers in parallel. Results appear as they complete. The UI polls for status rather than blocking.

**API layer**  
Expose a REST API via FastAPI so third-party ATS systems can integrate ResumeRadar programmatically. `POST /analyze` accepts resume file + JD text, returns match result JSON. Enables integration with Greenhouse, Lever, Workday.

**Redis semantic caching**  
Cache embeddings by content hash. If the same resume is uploaded twice (same bytes), skip re-embedding and return cached vector. Cache JD embeddings too — 100 resumes screened against same JD means JD is embedded once, not 100 times. Estimated 40–60% cost reduction at scale.

**LangSmith / LangFuse observability**  
Log every embedding call, similarity computation, and result to an observability platform. Track latency per operation, token usage, and match score distributions over time. Alert if average scores drop significantly — possible model drift or data distribution shift.

**A/B testing framework**  
Deploy two embedding models simultaneously — e.g., `all-MiniLM-L6-v2` vs `all-mpnet-base-v2`. Route 50% of traffic to each. Log recruiter actions (which candidates they selected) as ground truth. Measure which model's scores better predict hiring decisions. Promote the winner.

**Fine-tuned domain model**  
Collect recruiter feedback — "this resume was actually a strong match despite low score." Use these labels to fine-tune `all-MiniLM-L6-v2` on domain-specific resume-JD pairs using LoRA. Domain-specific fine-tuning typically improves accuracy by 8–15% on in-domain data.

**MLflow experiment tracking**  
Track every model version, training run, and evaluation metric in MLflow. Compare fine-tuned vs base model on held-out test set. Register the best model in MLflow Model Registry. Serve via MLflow serving endpoint with automatic rollback if new version degrades.

**Drift monitoring**  
Monitor the distribution of incoming resume embeddings over time using Evidently AI. If the distribution shifts significantly — e.g., resumes start mentioning new technologies the model was never trained on — trigger a retraining alert. Prevents silent model degradation.

**Edge deployment for privacy**  
For enterprises with strict data privacy requirements (resumes contain personal data), package a quantized version of the embedding model (INT8, ~45MB) using ONNX Runtime. Run entirely in the browser via WebAssembly or on-device via a local Python process. Resume data never leaves the user's machine.
<<<<<<< HEAD

---

## Resume bullet (for your portfolio)

> "Built ResumeRadar, a semantic resume-JD matching system using Sentence-BERT (all-MiniLM-L6-v2) and cosine similarity. Features multi-resume upload with PDF preview, skill gap analysis, and ranked candidate summary. Production-grade architecture with centralised logging, singleton model caching, two-layer error handling, and session state management. Deployed on HuggingFace Spaces."

---

*Built during Week 2 of an 8-week AI Engineer placement sprint — understanding every line, writing everything from scratch.*
=======
---
title: Resumeradar
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Resume and JD scoring for HR or Personal use
license: mit
---

# Welcome to Streamlit!

Edit `/src/streamlit_app.py` to customize this app to your heart's desire. :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).
>>>>>>> 6193574c982ddf5ba9f86d9c7b22a9725c0c7dc5
=======
>>>>>>> af2e0e060ac2a4b55837ea0e90c5f38054df111c
