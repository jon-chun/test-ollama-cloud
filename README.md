# Ollama Web Search Agent

This README gives you everything you need to **set up, run, and extend** the Ollama search agent for both local and cloud workflows.

This project is a **Python-based search agent** that integrates with [Ollama's Web Search API](https://ollama.com/) and supports both **local** and **cloud** execution. It allows a model to dynamically call external tools (`web_search` and `web_fetch`) to retrieve up-to-date information, reducing hallucinations and enabling **long-running research tasks**.

The project demonstrates how to:

* Run models **locally** with Ollama daemon.
* Switch seamlessly to **cloud-based execution**.
* Use Ollama's new **web search capabilities** introduced in September 2025.
* Build a **tool-augmented agent loop** that calls external functions when needed.

---

## Features

* **Two Modes**:

  * `LOCAL_FLAG=True` → run with local Ollama daemon (`127.0.0.1:11434`).
  * `LOCAL_FLAG=False` → run against Ollama's hosted cloud models.
* **Web Tools Integration**:

  * `web_search` for retrieving search results from the web.
  * `web_fetch` for fetching page content given a URL.
* **Dynamic Tool Selection**:

  * The agent can decide to call tools mid-conversation, adding results back into context.
* **Automatic Cloud Model Selection**:

  * Gracefully tests multiple cloud models and picks the first available.
* **Secure API Key Management**:

  * Uses `.env` to store your `OLLAMA_API_KEY`.
* **Multi-turn Conversations**:

  * Maintains chat history between user, assistant, and tools.

---

## Project Structure

```
├── main_search.py       # Main agent code
├── README.md            # Documentation (this file)
├── .env.example         # Example environment variable file
└── requirements.txt     # Python dependencies
```

---

## Requirements

### Software

* Python **3.9+** (tested on 3.12)
* Ollama daemon (`ollama serve`) for local execution
* Pip for package installation

### Python Libraries

Install dependencies:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
ollama>=0.6.0
python-dotenv>=1.0.0
```

---

## Configuration

### Environment Variables

Create a `.env` file at the root of the project:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
OLLAMA_API_KEY=sk-your-api-key-here
```

> **Note:**
> The API key is **required for both local and cloud modes** when using `web_search` or `web_fetch`.

---

### Flags in `main_search.py`

| Flag                     | Description                                                | Default    |
| ------------------------ | ---------------------------------------------------------- | ---------- |
| `LOCAL_FLAG`             | Run locally (`True`) or against cloud (`False`).           | `True`     |
| `USE_WEB_TOOLS`          | Enable or disable `web_search` and `web_fetch` tool usage. | `True`     |
| `MODEL_LOCAL`            | Name of the local model to use. Example: `qwen3:4b`.       | `qwen3:4b` |
| `MODEL_CLOUD_CANDIDATES` | Ordered list of cloud model IDs to try sequentially.       | See code.  |

---

## Setup Instructions

### 1. Install Ollama Daemon (Local Mode Only)

Follow official Ollama installation instructions:

* **MacOS**:

  ```bash
  brew install ollama
  ```
* **Linux / Windows**:
  See [Ollama Downloads](https://ollama.com/download).

Start the daemon:

```bash
ollama serve
```

Verify:

```bash
curl http://127.0.0.1:11434
```

---

### 2. Pull Local Model (Only if `LOCAL_FLAG=True`)

```bash
ollama pull qwen3:4b
```

This ensures the model is available locally before running.

---

### 3. Run the Agent

Start the script:

```bash
python main_search.py
```

---

## How It Works

### Architecture

1. **Chat Loop**

   * Maintains a list of messages between the user, assistant, and tools.

2. **Tool Calls**

   * The assistant can request a `web_search` or `web_fetch` operation.
   * The result is added back into the conversation as a `tool` message.

3. **Dynamic Model Selection**

   * In cloud mode, the script iterates through a list of model IDs and uses the first available.

4. **Real-Time Web Integration**

   * Reduces hallucinations by grounding answers with **live web data**.

---

### Example Flow

**User Input:**

```
what is ollama's new engine
```

**Agent Output:**

```
Thinking: I should call web_search to find recent announcements about Ollama's new engine.
```

**Tool Call:**

```
Tool calls: [web_search(query='Ollama new engine', max_results=3)]
```

**Final Answer:**

```
Ollama has introduced two major engine updates in 2025:

1. Enhanced Model Scheduling (Sept 23, 2025)
   - Optimized GPU memory allocation
   - Multi-GPU support
   - Performance gains (85.54 tokens/s → 52.02 tokens/s)

2. Multimodal Engine (May 15, 2025)
   - Vision model support
   - Multimodal tasks: image and video understanding
```

---

## Troubleshooting

| Error                                                | Cause                                       | Solution                                   |
| ---------------------------------------------------- | ------------------------------------------- | ------------------------------------------ |
| `Authorization header with Bearer token is required` | `OLLAMA_API_KEY` missing or not loaded      | Set key in `.env` and reload shell.        |
| `model 'qwen3:480b-cloud' not found`                 | Model ID not available in your cloud region | Update `MODEL_CLOUD_CANDIDATES` list.      |
| `ValueError: OLLAMA_API_KEY not found`               | `.env` file missing or misconfigured        | Copy from `.env.example` and add key.      |
| `ConnectionRefusedError` on local mode               | Ollama daemon not running                   | Run `ollama serve` in a separate terminal. |

---

## Example `.env.example`

```bash
# Ollama API Key for web tools
OLLAMA_API_KEY=sk-your-api-key-here
```

---

## Future Improvements

* [ ] Automatic cloud/local fallback
* [ ] Retry failed tool calls with exponential backoff
* [ ] Support for context windows > 32k tokens
* [ ] Dockerfile for reproducible deployment

---

## Reference

* **Official Docs**: [https://ollama.com/docs](https://ollama.com/docs)
* **Ollama GitHub**: [https://github.com/ollama](https://github.com/ollama)
* **Ollama Web Search Announcement** (Sept 2025)

> Web search and fetch APIs are now available with generous free tiers for individuals and paid tiers for production usage.

---

## License

This project is licensed under the MIT License.
See [LICENSE](LICENSE) for details.

---

## Demo

**Run locally:**

```bash
LOCAL_FLAG=True python main_search.py
```

**Run against cloud:**

```bash
LOCAL_FLAG=False python main_search.py
```

---

## Output Example

```
API Host: http://127.0.0.1:11434
API Key: sk-09bc1...
Thinking: Okay, let's search for Ollama's new engine release notes...
Tool calls: [web_search(query='Ollama new engine')]
Result: results=[ ... trimmed ... ]
Content:
Ollama has introduced two major engine updates in 2025:
1. Enhanced Model Scheduling (Sept 23, 2025)
2. Multimodal Engine (May 15, 2025)
```

---


