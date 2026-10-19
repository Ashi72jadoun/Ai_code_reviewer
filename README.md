# ⚡ Aura Code Reviewer

An autonomous, AI-driven code review and refactoring agent built with Python, Streamlit, Groq (Llama/Qwen models), Ruff, and Bandit. Aura scans local repositories, extracts uncommitted changes, performs deterministic security checks, and provides senior-engineer-level contextual feedback via a sleek SaaS-style web interface.

---

## 🚀 Key Features

- **🔍 Git Diff Extraction**: Automatically targets and reads uncommitted repository changes using Python subprocess.
- **🛡️ Static Security & Linting**: Integrates Bandit for vulnerability scanning and Ruff for fast code linting.
- **🧠 Context-Aware AI Review**: Sends code diffs along with full file context to Groq LLM (qwen/qwen3.8-27b) for intelligent logical bug detection.
- **🎨 Premium Web Interface**: Built with Streamlit, featuring custom dynamic Dark/Light mode toggles, brand watermarking (AJ), and an intuitive SaaS user experience.

---
---

## 📸 Dashboard & UI Preview

### 🌙 Dark Mode Interface
> *Featuring the clean dark gradient layout, and SaaS metrics overview.*
![Dark Mode](assets/dark_mode.png)

### ☀️ Light Mode Interface
> *Seamlessly toggle to light mode directly from the main UI with a single click.*
![Light Mode](assets/light_mode.png)

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Frontend**: Streamlit
- **AI / LLM API**: Groq Cloud SDK (qwen/qwen3.8-27b)
- **Code Quality Tools**: Ruff, Bandit
- **Version Control**: Git

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd ai-code-reviewer

##Create and activate a virtual environment
##bash
python -m venv venv
.\venv\Scripts\Activate

##Install dependencies:
##Bash
pip install -r requirements.txt

 ##Configure environment variables
Create a .env file in the root directory and add your Groq API key:
##code snippet
GROQ_API_KEY=your_actual_groq_api_key_here

##Run the Web Application:
##Bash
streamlit run app.py

📂 Project Architecture
ai-code-reviewer/
├── assets/
│   └── aj_watermark.png       # Custom brand watermark logo
├── diff_extractor.py          # Extracts uncommitted Git changes
├── static_analyzer.py         # Runs Ruff and Bandit security scans
├── context_gatherer.py        # Fetches full file context for LLM awareness
├── llm_reviewer.py            # Orchestration script interacting with Groq API
├── app.py                     # Streamlit frontend with Dark/Light mode toggle
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation


🛡️ License
Built as an advanced AI portfolio project. Feel free to customize and scale!