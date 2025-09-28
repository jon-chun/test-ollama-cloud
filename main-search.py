# main_search.py
import os
import ollama
from dotenv import load_dotenv
from ollama._types import ResponseError  # for robust retries

# -----------------------------
# Config
# -----------------------------
LOCAL_FLAG = False            # True => talk to local daemon; False => Ollama Cloud
USE_WEB_TOOLS = True         # Require web tools for freshness queries

MODEL_LOCAL = "qwen3:4b"     # Your local model (must be pulled locally)
# Try these in order on cloud; the first that responds will be used
MODEL_CLOUD_CANDIDATES = [
    "qwen3:4b",              # safe fallback that often exists
    "gpt-oss:20b-cloud",     # example cloud SKU from docs
    "gpt-oss:120b-cloud",    # bigger example; may not be enabled for all accounts
    # Add/remove based on what your account supports
]

SYSTEM_PROMPT = (
    "You are a careful research assistant.\n"
    "Today's date is September 28, 2025 (America/New_York).\n"
    "When a question concerns recent releases, announcements, prices, schedules, or anything likely to change, "
    "you MUST call web_search (and optionally web_fetch) to verify before answering. "
    "Be concise."
)

USER_QUESTION = "what is ollama's new cloud web search feature posted on their blog in September 2025"

# -----------------------------
# Host + API key
# -----------------------------
host_str = "http://127.0.0.1:11434" if LOCAL_FLAG else "https://ollama.com"

load_dotenv()
api_key = os.getenv("OLLAMA_API_KEY")

# web_search/web_fetch REQUIRE an API key (doc: Sep 2025)
if USE_WEB_TOOLS and not api_key:
    raise ValueError(
        "OLLAMA_API_KEY is required for web_search/web_fetch. "
        "Add it to your environment or .env."
    )

headers = {"Authorization": f"Bearer {api_key}"} if api_key else None

# One client handles chat AND the tool calls (so headers carry over)
client = ollama.Client(host=host_str, headers=headers)

# -----------------------------
# Select model (cloud probes, local optional pull)
# -----------------------------
def pick_cloud_model():
    """Return the first cloud model that responds to a tiny chat, else raise."""
    probe_messages = [{"role": "system", "content": "probe"}, {"role": "user", "content": "ok?"}]
    for mid in MODEL_CLOUD_CANDIDATES:
        try:
            _ = client.chat(model=mid, messages=probe_messages)
            print(f"[cloud] Using model: {mid}")
            return mid
        except ResponseError as e:
            print(f"[cloud] Skipping {mid}: {e}")
        except Exception as e:
            print(f"[cloud] Skipping {mid}: {e}")
    raise RuntimeError(
        f"No working cloud model from candidates: {MODEL_CLOUD_CANDIDATES}. "
        "Check your account/region model availability."
    )

if LOCAL_FLAG:
    MODEL = MODEL_LOCAL
    try:
        # Optional: ensure local weights exist; remove if you pre-pulled via CLI
        client.pull(MODEL)
    except Exception as e:
        print(f"(non-fatal) local pull skipped/failed for '{MODEL}': {e}")
else:
    # IMPORTANT: do NOT pull in cloud mode
    MODEL = pick_cloud_model()

# -----------------------------
# Tools wiring (use CLIENT methods to inherit headers)
# -----------------------------
available_tools = {}
tools_arg = []
if USE_WEB_TOOLS:
    available_tools = {
        "web_search": client.web_search,
        "web_fetch": client.web_fetch,
    }
    tools_arg = [client.web_search, client.web_fetch]

# -----------------------------
# Conversation loop
# -----------------------------
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_QUESTION},
]

while True:
    print(f"API Host: {host_str}")
    if api_key:
        print(f"API Key: {api_key[:5]}...")

    response = client.chat(
        model=MODEL,
        messages=messages,
        tools=tools_arg,   # enable tool use
        think=True
    )

    if getattr(response.message, "thinking", None):
        print("Thinking:", response.message.thinking)
    if getattr(response.message, "content", None):
        print("Content:", response.message.content)

    messages.append(response.message)

    # Handle tool calls
    tool_calls = getattr(response.message, "tool_calls", None)
    if tool_calls:
        print("Tool calls:", tool_calls)
        for tc in tool_calls:
            fn_name = tc.function.name
            fn = available_tools.get(fn_name)
            if fn:
                args = tc.function.arguments or {}
                print(f"Calling tool '{fn_name}' on {host_str}")
                result = fn(**args)  # headers already attached via client
                rtxt = str(result)
                print("Result:", (rtxt[:200] + "..."))
                # Add back into the chat with modest truncation to control context size
                messages.append({"role": "tool", "content": rtxt[:8000], "tool_name": fn_name})
            else:
                messages.append({"role": "tool", "content": f"Tool {fn_name} not found", "tool_name": fn_name})
    else:
        break
