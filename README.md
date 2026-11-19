# ⚡ Revision-Ai (v2.2) ⚡
> **Autonomous Local AI PC Controller & Automation Suite // Project Revision**

Revision-Ai is an open-source, local-first PC controller and automation tool built directly for the **Project Revision** ecosystem. It bridges powerful LLMs (Gemini, Claude, Llama, OpenAI via OpenRouter, Groq, or direct endpoints) with real local Python process execution in a protected environment.

---

## 🚀 Key Features

* **Project Revision Noir & Crimson UI:** CustomTkinter interface styled in the signature high-contrast void black (`#08090c`) and tactical crimson (`#ff1e38`) palette.
* **Full Application Builder:** Instruct Revision-Ai to write and launch full GUI apps, utilities, calculators, and system automation scripts.
* **Subprocess Sandbox & AST Checks:** Executes generated code safely with real-time console feedback.
* **Embedded Eco Mesh Relay:** Contributes to the distributed community hosting of the Rev Network gateway on port 8766.
* **Local Auth & Verification:** Offline-first credential and node registration storage (`users.json`).

---

## ⚡ Quick Start

```cmd
run.bat
```
Or manually:
```cmd
pip install -r requirements.txt
python main.py
```

---

## 📂 Project Structure
```text
Revision-Ai/
├── modules/
│   ├── ai_engine.py      # LLM API connection (OpenRouter, Groq, OpenAI)
│   ├── auth.py           # Local authentication & node verification
│   ├── executor.py       # Sandboxed subprocess code runner
│   ├── guardrails.py     # Prompt security & filter engine
│   ├── mesh_node.py      # Background community P2P relay
│   └── pc_scanner.py     # Local installed applications scanner
├── config.json           # API keys & active model settings
├── main.py               # CustomTkinter Project Revision GUI
├── requirements.txt      # Python dependencies
└── run.bat               # 1-click startup launcher
```
