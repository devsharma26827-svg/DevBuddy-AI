# DevBuddy AI
### *"From Project Folder to Production Ready in One Click."*

ProjectPilot AI is a production-quality, agentic AI workspace package designed to analyze project directories and prepare them for production launch. Through a sequential pipeline of 5 specialized agents, it automates architecture intelligence, testing, documentation, CI/CD deployment configuration, and social branding.

---

## 🌟 Key Features & AI Agents
1. **🔍 Project Intelligence Agent**: Discovers primary languages, dependency files, entry points, and high-level architectural patterns.
2. **🧪 Testing Agent**: Inspects existing test structures and creates/suggests a robust `pytest` suite for utility modules.
3. **📝 Documentation Agent**: Audits docstrings and dynamically drafts developer-facing manuals like API references and `README.md`.
4. **🚀 GitHub Deployment Agent**: Auto-generates production-grade GitHub Actions workflows to build, lint, and test automatically on push.
5. **💼 LinkedIn Branding Agent**: Crafts engaging promotional write-ups, viral taglines, and marketing copy for tech communities.

---

## ⚙️ Project Architecture
The project follows a clean, single-point entry layout optimized for ease of comprehension and extension:

- **`backend.py`**: Flask API adapter and web server. It delegates all domain work to the existing agents and engine.
- **`frontend/`**: Responsive HTML, CSS, and vanilla JavaScript interface.
- **`agents.py`**: Defines `BaseAgent` and implementations of the five default agents, alongside the `AgentRegistry`.
- **`engine.py`**: Orchestration execution engine containing logic for sequentially running registered agents and streaming status/logs.
- **`utils.py`**: Helper routines for processing zip files, scanning folder contents, and creating directory trees.
- **`requirements.txt`**: Minimal requirements file.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+** installed on your system.

### Option 1: One-Click Run (Recommended)
You can launch the application with a single click or command:
- **Windows**: Double-click `run.bat` or run:
  ```cmd
  run.bat
  ```
- **macOS/Linux**: Make `run.sh` executable and run it:
  ```bash
  chmod +x run.sh
  ./run.sh
  ```
The script will automatically detect/create the virtual environment (`venv`), install the required dependencies, set up the `.env` configuration file, start the Flask backend, and open `http://127.0.0.1:5000` in your web browser.

---

### Option 2: Manual Setup Instructions

1. **Ensure you are in the project root:**
   ```bash
   cd project_pilot_ai
   ```

2. **Create a Virtual Environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv

   # On Windows
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   ```bash
   # On macOS/Linux
   source venv/bin/activate

   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # On Windows (Command Prompt)
   .\venv\Scripts\activate.bat
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables:**
   Copy the template `.env.example` file to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```

6. **Run the DevBuddy Web Application:**
   ```bash
   python backend.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

---

## 🔌 Extensibility: Adding a New Agent
ProjectPilot AI is built so new agents can be added in seconds:

1. **Inherit from `BaseAgent` in `agents.py`**:
   ```python
   class SecurityAuditorAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               name="Security Auditor Agent",
               description="Checks codebase for secrets and dependency vulnerabilities.",
               icon="🛡️",
               color="#e67e22"
           )
           
       def run(self, project_path: str, context: dict) -> dict:
           # Audit logic here
           return {
               "status": "success",
               "summary": "### 🛡️ Security Audit Done",
               "logs": ["Scanned credentials", "Checked package list"],
               "artifacts": {"security_audit.md": "..."}
           }
   ```
2. **Register the Agent** inside the `AgentRegistry` initializer in `agents.py`:
   ```python
   self.register(SecurityAuditorAgent())
   ```
   The engine and UI will automatically detect, run, and display it without further changes!
