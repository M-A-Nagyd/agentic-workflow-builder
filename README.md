Absolutely — here is a **clean, professional, hackathon-ready `README.md`** that:

* Clearly explains **what your system does**
* Justifies **design choices** (LLM-verifiable steps vs OS execution)
* Shows **how to run and demo it**
* Reads like a **real engineering project**, not a toy
* Directly addresses questions judges will ask

You can copy-paste this as-is.

---

# 🧠 Agentic Workflow Builder (Unbound Hackathon)

An **Agentic Workflow Builder** that lets users design, execute, and monitor multi-step AI workflows powered by Large Language Models (LLMs), with deterministic validation and full execution traceability.

Instead of manually copy-pasting outputs between AI tools, this system **automates the handoff between AI agents**, retries intelligently, and validates correctness at each step.

---

## 🚀 What This Project Does

This system allows users to:

* ✍️ **Create workflows** composed of multiple LLM-powered steps
* 🤖 **Generate workflows automatically from a natural language prompt**
* 🔁 **Execute steps sequentially with retry logic**
* ✅ **Validate each step using deterministic completion criteria**
* 🔄 **Pass context from one step to the next**
* 📊 **Track execution progress, state, and logs in real time**
* 💾 **Persist workflows and runs in a database**

---

## 🧩 Core Concept: Agentic Workflows

Each **workflow** is a sequence of **steps**.

Each **step** defines:

* The LLM model to use
* The task prompt
* Completion criteria (how we decide if the step “passed”)
* Retry budget

The system executes steps one by one:

1. Call the LLM
2. Validate output
3. If valid → move to next step
4. If invalid → retry
5. If retries exhausted → fail gracefully

---

## 🧠 Important Design Choice (Intentional)

This system **does NOT perform OS-level actions** (e.g., creating files, running shell commands).

Instead, every step is designed so that:

* The LLM produces **textual artifacts** (code, explanations, structured output)
* The system validates correctness **deterministically**

### Why this matters:

* ✅ No unsafe OS permissions
* ✅ Fully verifiable correctness
* ✅ Deterministic, repeatable behavior
* ✅ Model-agnostic and production-safe

This is how real agentic systems (AutoGPT-style planners, AI pipelines) are designed.

---

## 🧪 Completion Criteria (Deterministic Validation)

Each step can define how success is determined:

Supported criteria:

* `length` → minimum output length
* `regex` → must match a pattern (e.g. function definition)
* `contains` → must include a keyword
* `valid_python` → must parse as Python code
* `all` → composite checks

This avoids subjective “LLM judging LLM” and makes results reliable.

---

## 🖥️ User Interface

The UI allows users to:

* Generate workflows from natural language
* Edit workflow JSON manually
* Create workflows
* Run workflows
* Watch execution state in real time:

  * RUNNING
  * COMPLETED
  * FAILED_VALIDATION
  * WAITING_FOR_PROVIDER
* Inspect full logs per step and attempt

---

## 🏗️ Tech Stack

### Backend

* **FastAPI** – API server
* **SQLAlchemy** – ORM
* **SQLite** – Lightweight persistence
* **Unbound API** – LLM provider

### Frontend

* Vanilla **HTML / CSS / JavaScript**
* Polling-based live execution updates

---

## 📂 Project Structure

```
Unbound/
├── app/
│   ├── main.py           # FastAPI app & API routes
│   ├── executor.py       # Workflow execution engine
│   ├── unbound_client.py # Unbound API wrapper
│   ├── completion.py    # Output validation logic
│   ├── schemas.py       # Pydantic schemas
│   ├── models.py        # SQLAlchemy models
│   └── database.py      # DB engine & session
├── static/
│   ├── index.html       # UI
│   ├── app.js           # Frontend logic
│   └── styles.css
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd Unbound
```

### 2️⃣ Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Unbound API key

**Windows (PowerShell):**

```powershell
setx UNBOUND_API_KEY "your_api_key_here"
```

Restart terminal after setting.

---

### 5️⃣ Run the server

```bash
uvicorn app.main:app --reload
```

Open in browser:

```
http://127.0.0.1:8000/static/index.html
```

---

## 🧪 Example Workflow

**Prompt:**

```
Create a workflow that writes Python code to print hello world and explains it.
```

**Generated Workflow:**

```json
{
  "name": "Generated Workflow",
  "steps": [
    {
      "prompt": "Write Python code that prints hello world",
      "criteria_type": "regex",
      "criteria_value": "print\\(\"hello world\"\\)",
      "max_retries": 2
    },
    {
      "prompt": "Explain how the Python code works",
      "criteria_type": "length",
      "criteria_value": { "min": 100 },
      "max_retries": 2
    }
  ]
}
```

---

## 🌟 Bonus Features Implemented

* Retry budget per step
* Workflow generation from natural language
* Persistent execution history
* Live execution state tracking
* Deterministic validation
* Graceful failure handling

---

## 🎯 Why This Stands Out

* Real agentic orchestration (not a simple chat wrapper)
* Deterministic correctness checks
* Clear separation of planning vs execution
* Production-safe design choices
* Transparent execution logs

---

## 🧠 Future Improvements

* Parallel steps & branching workflows
* Manual approval gates
* Cost & token tracking
* Workflow export/import
* Notifications on completion

---

## 🏁 Conclusion

This project demonstrates how to build **reliable, verifiable agentic systems** using LLMs — focusing on correctness, traceability, and real-world constraints.

It goes beyond prompt chaining and shows how AI agents can be orchestrated safely and deterministically.

---


