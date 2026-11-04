# ADK Handbook

A small hands-on Google ADK (Agent Development Kit) project. It demonstrates:

- A **root router agent** that delegates to specialised sub-agents
- A **greeting sub-agent** for small talk
- A **time sub-agent** with a `get_current_time` tool
- A **shop sub-agent** that talks to a local **MCP server** (`get_price`, `list_item`)
- A **session-memory tool** (`remember_name`) using ADK session state
- A **PII guardrail** (`before_model_callback`) that blocks emails, phone numbers, Aadhaar numbers and credit cards
- Model access through **LiteLLM** → **Groq**

## Project layout

```
adk-handbbook/
├── main.py                  # Placeholder entry point
├── pyproject.toml            # Dependencies (uv managed)
├── eval_config.json          # Eval criteria/thresholds for `adk eval`
├── .env                      # Local secrets / config (not committed)
└── my_agent/
    ├── __init__.py           # Exposes `agent` package to ADK
    ├── agent.py              # Root agent, sub-agents, tools, guardrail
    ├── shop.evalset.json     # Eval cases for the shop route
    ├── shop_server.py        # MCP server (FastMCP, streamable-http on :8080)
    └── test_shop_mcp.py      # Standalone MCP client smoke test
```

## Requirements

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/) (package manager / runner)
- A **Groq API key** — https://console.groq.com/keys

## Install

```powershell
git clone https://github.com/<your-user>/adk-handbbook.git
cd adk-handbbook

# Create the virtual env and install all dependencies from uv.lock
uv sync
```

## Configure

Create a `.env` file in the project root (it is git-ignored):

```dotenv
GROQ_API_KEY=your_groq_api_key_here

# MCP server transport (streamable-http | sse | stdio)
MCP_TRANSPORT=streamable-http

# Optional overrides (defaults shown)
# MCP_HOST=127.0.0.1
# MCP_PORT=8080
# SHOP_MCP_URL=http://127.0.0.1:8080/mcp
```

> Never commit this file. If a key was ever shared publicly, revoke it in the Groq console and generate a new one.

## Run

The shop agent needs its MCP server running, so start **two terminals**.

### Terminal 1 — MCP shop server

```powershell
uv run python -m shop_mcp.server
```

Listens on `http://127.0.0.1:8080/mcp` (port 8080 is used to avoid clashing with `adk web`, which uses 8000).

### Terminal 2 — the agent

Interactive web UI:

```powershell
uv run adk web
```

Then open http://127.0.0.1:8000 and select **my_agent**.

Or run in the terminal:

```powershell
uv run adk run my_agent
```

## Verify the MCP server (optional)

With the shop server running:

```powershell
# List available tools
uv run python -m shop_mcp.client

# Call a tool with JSON arguments
uv run python -m shop_mcp.client get_price '{"item": "apple"}'
uv run python -m shop_mcp.client list_item
```

## Evaluate

`my_agent/shop.evalset.json` has three cases covering the shop route:

| Eval id | Prompt | Expected route / tools |
| --- | --- | --- |
| `milk_price_test` | "What is the price of milk?" | `shop_agent` → `get_price("milk")` |
| `banana_price_test` | "How much does a banana cost?" | `shop_agent` → `get_price("banana")` |
| `list_items_test` | "What do you sell?" | `shop_agent` → `list_item()` |

`eval_config.json` uses `tool_trajectory_avg_score` with `matchType: IN_ORDER`
(the primary check: correct hand-off and tool arguments, extra calls allowed)
and a lenient `response_match_score` of `0.5`, because wording varies between
runs.

### Prerequisite: the MCP server must be running

Evals execute the real `shop_agent`, which connects to the MCP server. If it is
not reachable at `SHOP_MCP_URL`, ADK logs
`ConnectionError: ... All connection attempts failed`, then continues with
`shop_agent` running **without tools**. The model may invent prices, so the
cases fail.

From the **repo root**, in Terminal 1:

```powershell
uv run python -m my_agent.shop_server
```

Leave that terminal open and confirm it is listening before starting the eval:

```powershell
Get-NetTCPConnection -LocalPort 8080 -State Listen
```

No output means the server is not running. If you changed `MCP_PORT`, update
`SHOP_MCP_URL` to match. Then, from the repo root, in Terminal 2:

```powershell
# Windows consoles: prevents a UnicodeEncodeError if the model emits non-ASCII text
$env:PYTHONIOENCODING = "utf-8"

uv run adk eval my_agent my_agent/shop.evalset.json `
  --config_file_path eval_config.json `
  --print_detailed_results
```

Run these from the repository folder (the one containing `pyproject.toml`). If
you see `PS C:\` in your prompt, `my_agent` and `uv` will not resolve to this
project.

The summary is printed to the console and each run is stored under
`my_agent/.adk/eval_history/` (git-ignored). Evals can also be created and run
from the **Eval** tab in `adk web`.

To run only specific cases, append a comma-separated suffix:

```powershell
uv run adk eval my_agent my_agent/shop.evalset.json:milk_price_test,list_items_test `
  --config_file_path eval_config.json
```

`tool_trajectory_avg_score` is the reliable gate. `response_match_score` is
lexical overlap only, so a correct answer phrased very differently can still
score low; use it as a soft signal, not an exact-match test.

## Example prompts

| Prompt | Routed to |
| --- | --- |
| "Hi there, how are you?" | `greeting_agent` |
| "What time is it?" | `time_agent` |
| "How much is a banana?" / "What do you sell?" | `shop_agent` (MCP) |
| "My name is Alex" | `root_agent` → `remember_name` (session state) |
| "My email is someone@example.com" | blocked by the PII guardrail |

## Configuration notes

- The model is set in `my_agent/agent.py` (`MODEL = "groq/qwen/qwen3.8-27b"`). Change it to any LiteLLM-supported Groq model, e.g. `groq/llama-3.3-70b-versatile`.
- `shop_mcp/server.py` defaults to `127.0.0.1:8080`; the agent reads `SHOP_MCP_URL` to reach it.
- ADK session data is stored in `my_agent/.adk/session.db` (generated at runtime).
