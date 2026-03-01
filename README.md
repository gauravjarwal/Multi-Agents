# 🤖 Multi-Agent AI System

A multi-agent AI system where **Agent A (Orchestrator)** and **Agent B (Executor)** collaborate to fulfill **any** user request. Built with a **Python/Flask backend** powered by **Google Gemini** and a **vanilla JavaScript frontend**.

---

## 📐 Architecture

```
┌──────────────┐     HTTP/JSON     ┌──────────────────────────────┐
│   Frontend   │ ◄──────────────► │      Flask API (app.py)       │
│  (HTML/JS)   │                   │                              │
└──────────────┘                   │   ┌──────────────────────┐   │
                                   │   │     Agent A           │   │
                                   │   │   (Orchestrator)      │   │
                                   │   │                       │   │
                                   │   │ 1. Decompose (Gemini) │   │
                                   │   │ 2. Resolve deps       │   │
                                   │   │ 3. Compile (Gemini)   │   │
                                   │   └──────────┬───────────┘   │
                                   │              │               │
                                   │        Message Queue         │
                                   │        (async option)        │
                                   │              │               │
                                   │   ┌──────────▼───────────┐   │
                                   │   │     Agent B           │   │
                                   │   │    (Executor)         │   │
                                   │   │                       │   │
                                   │   │  Execute any sub-task │   │
                                   │   │  using Gemini         │   │
                                   │   └──────────────────────┘   │
                                   └──────────────────────────────┘
```

### How It Works

1. **User** sends any natural-language request
2. **Agent A** uses Gemini to decompose it into logical sub-tasks (with dependencies)
3. **Agent A** resolves dependencies — if task_2 depends on task_1, it injects task_1's result as context
4. Each sub-task is sent to **Agent B**, which uses Gemini to execute it
5. **Agent A** collects all results and uses Gemini to compile a final, coherent answer

### Agent Roles

| Agent | Role | How It Works |
|-------|------|-------------|
| **Agent A** | Orchestrator | Uses Gemini to decompose any request into sub-tasks, resolves dependencies, compiles final answer |
| **Agent B** | Executor | Uses Gemini to execute any individual sub-task — no hardcoded task types |

### Communication

Agents communicate in two ways (configurable per endpoint):

1. **Synchronous** (`POST /api/query`) — Agent A directly calls Agent B's methods
2. **Asynchronous** (`POST /api/query/async`) — Messages routed through an async `MessageQueue` (bonus feature)

---

## 🚀 How to Run

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your Gemini API key

# Start the server
python app.py
```

The API will be running at **http://localhost:5000**.

### 2. Frontend Setup

Simply open the frontend in a browser:

```bash
cd frontend
open index.html          # macOS
# xdg-open index.html   # Linux
# start index.html      # Windows
```

Or serve it with any static file server:

```bash
python3 -m http.server 3000 --directory frontend
# Then visit http://localhost:3000
```

---

## 🧪 Sample Inputs & Outputs

### Example 1: Multi-step Creative Request

**Input:**
```
Write a short poem about AI, then translate it to French.
```

**Agent A decomposes into:**
1. `task_1`: Write a short poem about AI
2. `task_2`: Translate the poem to French *(depends on task_1)*

**Output:**
```
Step 1 (Write a short poem about AI):
  Silicon dreams in circuits flow,
  A mind of code begins to grow...

Step 2 (Translate the poem to French):
  Rêves de silicium dans les circuits coulent,
  Un esprit de code commence à grandir...

Final Answer:
  Here is your poem about AI and its French translation: ...
```

### Example 2: Research & Analysis

**Input:**
```
List 5 healthy breakfast ideas and estimate the calories for each.
```

**Agent A decomposes into:**
1. `task_1`: List 5 healthy breakfast ideas
2. `task_2`: Estimate calories for each idea *(depends on task_1)*

### Example 3: Comparison

**Input:**
```
Compare the pros and cons of Python vs JavaScript for backend development.
```

**Agent A decomposes into:**
1. `task_1`: List pros and cons of Python for backend development
2. `task_2`: List pros and cons of JavaScript for backend development
3. `task_3`: Compare and summarise *(depends on task_1, task_2)*

---

## 📁 Project Structure

```
Multi-Agents/
├── backend/
│   ├── app.py              # Flask API – endpoints and server entry point
│   ├── agent_a.py          # Agent A – Orchestrator (decompose, delegate, compile via Gemini)
│   ├── agent_b.py          # Agent B – Executor (runs any sub-task via Gemini)
│   ├── orchestrator.py     # Async orchestrator using MessageQueue
│   ├── message_queue.py    # Async message queue for agent communication
│   ├── config.py           # Configuration and environment variables
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Template for API key
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── style.css           # Design system and styles
│   └── app.js              # Frontend logic and API interaction
└── README.md               # This file
```

---

## ✅ Requirements Checklist

| Requirement | Status |
|------------|--------|
| Agents communicate programmatically | ✅ Function calls + REST API + async message queue |
| Handle at least one user query end-to-end | ✅ Any query works — fully generic |
| Use AI service for natural language | ✅ Google Gemini for decomposition, execution, and compilation |
| Modular and easy to read code | ✅ Clean separation of concerns |
| Clear instructions to run | ✅ This README |
| Source code repository | ✅ |
| README with design explanation | ✅ |
| Sample inputs and outputs | ✅ See above |

---

## 🌟 Bonus Features

| Bonus | Status |
|-------|--------|
| Support multiple tasks/agents | ✅ Arbitrary number of sub-tasks with dependency resolution |
| Handle errors gracefully | ✅ Try/except at every layer, user-friendly error messages |
| Async communication between agents | ✅ `MessageQueue` with `asyncio` (see `orchestrator.py`) |
| Beautiful web frontend | ✅ Dark mode, animations, responsive design |

---

## 🛠️ Design Decisions & Thought Process

### Why Two Agents?

The assignment asks for a multi-agent system. Rather than creating agents that are just glorified function wrappers, I designed agents with **genuinely distinct roles** that mirror real-world agentic AI patterns:

- **Agent A (Orchestrator)** acts as a **planner** — it never executes tasks itself. Its job is to understand intent, break problems down, manage data flow between steps, and present results. This is analogous to a project manager who delegates work.
- **Agent B (Executor)** acts as a **worker** — it receives a single, focused instruction and completes it. It doesn't know about the bigger picture or other tasks. This separation means Agent B can be scaled, replaced, or duplicated without affecting Agent A.

**Alternative considered:** A single agent that does everything. I rejected this because it wouldn't demonstrate the core concept of *agent communication and task delegation* that the assignment tests.

### Why Fully Generic (No Hardcoded Task Types)?

An early version had hardcoded handlers for `get_weather`, `evaluate_math`, and `summarise`. I refactored to a **fully generic** approach where:
- Agent A asks Gemini to decompose *any* query — not just weather/math
- Agent B asks Gemini to execute *any* sub-task — not just predefined ones

**Why this is better:** Hardcoded task types would mean every new capability requires code changes. With the generic approach, the system handles queries it has never seen before — poetry, translations, research, comparisons — without any code modifications.

**Trade-off:** The generic approach relies entirely on the LLM's quality. Hardcoded tools (like a real weather API) can be more precise. But for demonstrating *agentic AI*, the generic approach better shows how LLM-powered agents can reason and collaborate.

### Why Dependency Resolution?

Many multi-step tasks need **sequential data flow**. For example:
> "Write a poem about rain, then translate it to Hindi"

Task 2 (translate) cannot start until task 1 (write poem) completes, because it needs the poem text. My system handles this through:

1. Agent A's decomposition produces a `depends_on` field per task
2. Before executing a dependent task, Agent A injects the results of its dependencies as `context`
3. Agent B receives this context and uses it to complete the task

This is a simplified version of a **DAG (Directed Acyclic Graph) execution engine** — a pattern used in production systems like Apache Airflow and LangGraph.

### Why Google Search Grounding?

When users ask factual or real-time questions (weather, news, scores), a regular LLM can only answer from its training data. By enabling **Google Search grounding** on Agent B, the system can:
- Fetch live weather, news, sports scores
- Access up-to-date information beyond the model's training cutoff
- Provide sourced, verifiable answers

This is the same capability that powers gemini.google.com's ability to answer real-time queries.

### Why Both Sync and Async Communication?

The system supports **two communication patterns**:

1. **Synchronous** (`/api/query`) — Agent A calls `agent_b.execute_task()` directly. Simple, fast, easy to debug.
2. **Asynchronous** (`/api/query/async`) — Messages pass through an `asyncio.Queue`-based `MessageQueue`. Agents are fully decoupled.

**Why both?** The sync path is practical and easy to understand. The async path demonstrates a more scalable, production-like architecture where agents could run on separate processes or machines. Having both shows understanding of the trade-offs.

### Error Handling Philosophy

Errors are handled at **every layer** with graceful degradation:

| Layer | What happens on failure |
|-------|------------------------|
| Gemini decomposition fails | Falls back to treating the entire query as a single task |
| Agent B execution fails | Returns a clear error message; other tasks continue |
| Gemini compilation fails | Falls back to raw step results (still useful) |
| Empty/invalid user input | Returns 400 with a helpful message |
| Network / API key issues | Caught and returned as readable error messages |

The design principle: **never crash, always return something useful.**

### Frontend Design Choice

The frontend is intentionally built with **vanilla HTML, CSS, and JavaScript** — no frameworks. This was deliberate:
- Zero build step — just open `index.html`
- Easy to read and understand for reviewers
- Demonstrates that a polished UI doesn't require React/Vue/Angular
- The chat-based interface makes the multi-step agent pipeline visible and intuitive

---

## 📜 License

MIT — use freely.
