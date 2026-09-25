# Project: Google Maps Local Lead Extractor & Manager

## Overview

A personal tool to find local business leads on Google Maps that **don't have a website** — filtered by niche and location — and manage outreach status manually through a dashboard.

**Owner's goal:** Automate finding local businesses (in the user's own country) that are missing a website, so they can be pitched web development/design services. Everything must run for **free** (no paid APIs, no paid LLMs).

**Learning goal alongside the build:** Learn AI Agents using classic LangChain (`AgentExecutor`), using this project as the hands-on example, before later rebuilding it with LangGraph.

---

## Core Requirements

- Input: a natural language prompt describing niche + location (e.g., "dentists in Lahore")
- Output columns per lead:
  - `name`
  - `address`
  - `phone` (cleaned/normalized format)
  - `has_website` (boolean condition — only businesses WITHOUT a website are kept)
  - `niche` (tag, e.g. "dentists")
  - `status` (manual: Pending / No Reply / Conversion)
  - `first_seen` (timestamp)
- Dashboard to view leads grouped by niche and manually update status
- Must stay within free usage — Apify free monthly credit + free Hugging Face LLM (no paid APIs)

---

## Key Decisions Made (with reasoning)

| Decision | Choice | Why |
|---|---|---|
| Data source | **Apify — Google Maps Scraper actor (Compass)**, accessed via Apify's API/`apify-client` | Switched from Google's official Places API. Returns name, address, phone, website, rating, reviews, category, hours all in one call — no field-tier complexity, and **no credit card / billing account required** for the free tier (unlike Google Cloud). Note: this works by scraping Google Maps' public pages via Apify's infrastructure, which is against Google's Maps ToS even though it's a widely-used commercial product — a trade-off knowingly accepted for simplicity and zero-setup-cost |
| Free quota | **$5 free platform credit/month** (resets monthly, no rollover), actor costs **~$4 per 1,000 results** → **~1,250 free results/month** | For 5 niches/month, that's ~250 raw results/niche average — comfortably enough for local market use |
| Query coverage | Google Maps still caps ~500 results per single search query regardless of provider, so the agent still needs query variations per niche | Same agentic reasoning value as before — deciding when a niche needs broader/alternate query phrasing to get full coverage |
| Usage tracking | Simple `usage_log` counter table in SQLite, tracking $ credit used vs. the $5/month cap | Cheap safeguard to avoid running out of free credit mid-task without noticing |
| Rating filter | NOT a hard filter — display-only column, decided manually | Avoids burning the small Pro-tier quota on every search; only fetch rating for a shortlist if ever needed |
| LLM | Free Hugging Face models only | Zero cost constraint |
| Database tool design | Structured tool (`search_leads(niche, status)`), NOT text-to-SQL | Free/small HF models are unreliable at generating correct SQL; a structured tool with fixed safe parameters avoids bad/unsafe queries entirely |
| Deduplication | Fuzzy dedup (not exact-match) | Same business can appear slightly differently across query variations (e.g., "City Dental" vs "City Dental Clinic") — fuzzy matching catches these, exact matching misses them |
| Phone formatting | Normalize to one consistent format | Places API returns inconsistent phone formats; normalization avoids broken sorting/searching/dialing later |
| Database | SQLite | Free, zero-setup, single-file, sufficient for personal-scale use — dashboard needs persistent storage (not just CSV) to save manual status updates |
| Dashboard | Streamlit, multi-page | Free, pure Python, fast to build a functional internal tool without separate frontend work |
| Niche browsing layout | Dropdown selector (not tabs, not stacked sections) | Simplest to scale as more niches get added over time |
| Manual lead import | New `import_leads_tool` supports CSV and Excel, with a simple `label` field | Owner has pre-existing manually-collected leads to bring in. Label maps directly into the existing `niche` field (no separate "source" column) — keeps schema simple, imported leads appear in the same niche browsing/search as scraped ones. Column mapping uses deterministic header-matching rules (not LLM-based) for reliability with free models. Imported rows go through the same dedup/cleanup pipeline as scraped leads for consistency |
| Embeddings / RAG | **Dropped entirely** — not used anywhere in the project | Originally planned as a general "we'll use free HF embeddings" commitment early on, but no actual feature ended up needing them: dedup uses `rapidfuzz` (string similarity, the right tool for catching name variations), search uses structured DB lookups (exact niche/status match), not semantic search. The one plausible use case — normalizing niche labels so "dentists" and "dental clinics" don't fragment into separate categories — is instead solved with a simple **niche dropdown + "add new" option** on the Extract Leads page, avoiding the added complexity of embeddings/vector comparison for no real benefit at this project's scale |

### Explicitly out of scope (parked for later, not being built now)
- WhatsApp click-to-chat links
- Auto-generated outreach message drafts
- Map view of leads
- Auto niche-tagging via LLM
- Rating as a hard filter

---

## Architecture

### Agent Tools (LangChain `AgentExecutor`)
1. **`apify_maps_tool`** — calls the Apify Google Maps Scraper actor via the Apify API, returns raw place results (name, address, phone, website, rating, etc.) for a query
2. **`fuzzy_dedup_tool`** — removes near-duplicate businesses across multiple query variations (e.g., different phrasings of the same niche)
3. **`phone_cleanup_tool`** — normalizes phone numbers into one consistent format
4. **`search_leads_tool`** — structured lookup into the SQLite database by `niche` and/or `status`, powers natural-language search in the dashboard
5. **`import_leads_tool(file_path, label)`** — reads a manually-collected CSV or Excel file, maps its columns to our schema (name/address/phone/website) via flexible header matching, runs the rows through the same `fuzzy_dedup_tool` and `phone_cleanup_tool`, tags them with `label` as their niche, and saves to the database. Same function is used by both the agent (conversational trigger, e.g. "import leads from downloads/electricians.csv, label them electricians") and a dedicated dashboard upload page — no duplicate logic

### Non-agent helper (plain Python, no @tool decorator)
- **`tools/filters.py` → `filter_no_website()`** — keeps only leads without a website. NOT given to the agent as a tool, because "does this lead have a website" is a fixed rule, not a decision — giving the LLM something to decide that has one correct answer every time only adds risk for no benefit (see Module 1 principle: not everything needs to be agentic)

### Agent Reasoning Flow (ReAct-style loop)
```
User prompt: "Find dentists in Lahore with no website"
  → Thought: need to search Google Maps (via Apify) for this niche/location
  → Action: apify_maps_tool("dentists in Lahore")
  → Observation: raw results
  → Thought: may need query variations for full coverage
  → Action: apify_maps_tool("dental clinic Lahore")
  → Observation: more raw results (some overlapping)
  → Thought: dedup + clean + filter to no-website only
  → Action: fuzzy_dedup_tool, phone_cleanup_tool
  → Observation: clean lead list
  → Thought: enough coverage, done
  → Final: save leads to SQLite under niche="dentists"
```

### Data Flow
```
User prompt (Streamlit "Extract Leads" page)
   ↓
AgentExecutor (plans queries, calls tools, filters, dedups)
   ↓
SQLite database (leads table)
   ↓
Streamlit dashboard reads/writes DB (status updates, niche browsing, search)
```

---

## Tech Stack

- **Agent framework:** LangChain (`AgentExecutor`, classic agent — NOT LangGraph, for this build)
- **LLM:** Free Hugging Face model (specific model TBD when we reach implementation)
- **Data source:** Apify — Google Maps Scraper actor, via `apify-client` (Python SDK) or Apify REST API
- **Database:** SQLite
- **Dashboard:** Streamlit (multi-page app)
- **Dedup logic:** `rapidfuzz` (fuzzy string matching, free/open-source)
- **Phone normalization:** `phonenumbers` (free/open-source Python library)
- **Manual import parsing:** `pandas` + `openpyxl` (reads both CSV and Excel files, free/open-source)

---

## Dashboard Pages (Streamlit)

1. **🏠 Home** (`Home.py`) — overview stats: total leads, per-niche counts, status breakdown (Pending/No Reply/Conversion) — ✅ built & tested
2. **➕ Extract Leads** (`1_Extract_Leads.py`) — dropdown niche selector (fixes niche fragmentation) + business type/city inputs → runs the agent → real counts from `intermediate_steps` — ✅ built, testing pending
3. **📋 Manage Leads** (`2_Manage_Leads.py`) — dropdown to select a niche → table of leads with editable status checkboxes (was called "Leads by Niche" earlier, renamed by owner)
4. **📥 Import Leads** (`3_Import_Leads.py`) — file upload (CSV/Excel) + label textbox → runs `import_leads_tool`
5. **🤖 Agent Assistant** (`4_Agent_Assistant.py`) — general chat interface to the FULL agent (all 3 tools: extract, search, import), not just search — replaces the earlier narrower "Ask My Leads" page concept. Chat-style UI (multi-turn), so the user can type anything conversationally and the agent decides which tool(s) to use
6. **⚙️ Usage** (`5_Usage.py`) — shows Apify credit usage vs. the $5/month free cap, using `usage_log` data already tracked (was called "Settings" earlier, renamed by owner)
7. **🗺️ Roadmap** (`6_Roadmap.py`) — honest, real list of parked/future features (rating filter, WhatsApp links, map view, etc.) — added instead of padding the nav with fake/dead links, since this is meant to be shown on LinkedIn/resume and dead links would hurt credibility more than help

Note: dedicated "Ask My Leads" page was dropped since Agent Assistant now covers that use case, more broadly, in one place.

## Design System (locked)
- **Style:** dark "control panel" theme — precision data tool feel (like Attio/Linear), not a flashy AI-demo look
- **Colors:** `#12151C` background, `#1B1F29` card surface, `#EDEEF0` primary text, `#8B93A3` muted text, `#E8A33D` accent (gold = valuable lead), `#5FA88C` success/Conversion status, `#C96C5C` No Reply status
- **Type:** Sora (headings/UI), JetBrains Mono (data — phone numbers, addresses, counts)
- **Layout:** left-aligned, sharp corners on structural elements, rounded only on interactive elements, sidebar nav with no default Streamlit branding
- Deliberately avoided common AI-generated design tells (cream+terracotta, ALL-CAPS eyebrows, arrow-suffixed buttons, identical-radius card kit, em-dash labels)

---

## Roadmap / Learning Track Status

**Covered so far (theory):**
1. What is an Agent (mental model, loop, agent vs chain vs RAG)
2. Tools (function/tool calling, tool schema, good tool design)
3. ReAct (Thought → Action → Observation reasoning pattern)
4. Memory (short-term scratchpad vs long-term conversational)

**Remaining (to be learned WHILE building this project, not as separate theory modules):**
5. Building a real agent with `AgentExecutor` (hands-on code)
6. Limitations of `AgentExecutor` (felt firsthand during the build)
7. This project — full implementation with classic LangChain
8. *(Future, separate track)* — rebuild this same project using LangGraph, once limitations are well understood

**Build phases (in progress):**
1. Environment & Setup — Apify account + API token (no billing/card needed), Hugging Face token, Python venv + libraries ← *currently here*
2. Build the `apify_maps_tool`
3. Build data processing tools (fuzzy dedup, phone cleanup)
4. Build the database layer (SQLite: leads + usage_log tables)
5. Build the `import_leads_tool` (manual CSV/Excel import, reuses dedup + cleanup)
6. Assemble the agent (AgentExecutor) — wire in all 5 tools
7. Build the Streamlit dashboard (5 pages)
8. Test & refine end-to-end
9. Parked for later (post-MVP): rating display, LangGraph rebuild, map view, etc.

---

## How to use this file
If context is lost in a future conversation, share this file to restore full project understanding — goals, all key decisions (and their reasoning), architecture, stack, and current learning progress.