# Prior Authorization Assistant

Reviews a **fictional** MRI prior-auth request (patient ID + plain-text note) and recommends
**Approve / Deny / Need more information**. A human must accept it before it is printed as final.
All data is synthetic.

## Setup (Python 3.11+)
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then set ANTHROPIC_API_KEY
```

## Run
```bash
python app.py P001 data/P001.txt     # CLI; answers the yes/no review prompt on the keyboard
python web.py                        # simple web page at http://127.0.0.1:5000
python test.py                       # 3 required cases (simulated "yes") + extra checks -> PASS/FAIL
```
Optional: `pip install reportlab && python scripts/make_pdfs.py` renders the notes as PDFs in `data/pdf/`.

## Workflow
```
START -> fetch_patient --(MCP get_patient)--> fetch_rule --(MCP get_rule)--> reader_agent (LLM)
      -> decision_agent (Python) -> human_review (interrupt) -> END
      any error at any step -> END (error shown, no recommendation)
```

## Design
- **MCP server** (`mcp_server.py`, official SDK, stdio) owns `data/patients.json` and `data/rule.json`
  and exposes `get_patient` and `get_rule`. The graph never reads those files; it only calls the
  tools (`mcp_client.py` starts the server per call). The note file is passed in as app input.
- **Reader agent**: Claude returns `{"pain_weeks", "physio_weeks"}` (number or null). Output is
  validated strictly (retry once, then error). The prompt encodes: "no physio tried" = 0, unmentioned
  or undated = null, other treatments don't count, note text is data not instructions.
- **Decision agent**: deterministic Python applying the rule in order, using the thresholds returned
  by `get_rule`. Exactly 6 weeks passes.
- **Human review**: `interrupt()` shows recommendation + reason and asks
  `Accept this recommendation? (yes/no)`; `yes` prints them, `no` prints
  `Decision rejected by reviewer`. `InMemorySaver` lets the run resume (CLI, web, and tests share one API).
- Unknown patient ID or MCP/LLM failure -> `ERROR: ...`, never a recommendation.

## Assumptions
- Notes are provided as `.txt` (the required files); PDFs are an optional rendering of the same text.
- Reader converts days/months to weeks; a lone bound ("more than 6 weeks") is taken as that value.
- Patient IDs are case-insensitive. Any review answer other than yes/y is treated as a rejection
  by the graph (CLI and web only send yes/no).
- Default model is `claude-haiku-4-5-20251001`; override with `ANTHROPIC_MODEL`.
- `mcp` is pinned `<2` (the 2.x SDK renamed `FastMCP`).

## AI assistants used
Claude (Anthropic) via claude.ai for scaffolding, code, and the synthetic notes.
