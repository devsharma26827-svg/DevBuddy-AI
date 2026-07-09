"""Flask API and static-file host for the DevBuddy AI web client.

The domain implementation remains in agents.py, engine.py and utils.py.  This
module is deliberately an adapter: it owns web sessions, validates requests,
serializes pipeline events, and delegates every operation to the existing code.
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import shutil
import tempfile
import threading
import uuid
import zipfile
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_file, send_from_directory

from agents import AgentRegistry, ProjectIntelligenceAgent
from engine import OrchestrationEngine
import utils

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
CONFIG_KEYS = (
    "GEMINI_API_KEY", "GEMINI_MODEL", "GEMINI_KEY_AGENT_1",
    "GEMINI_KEY_AGENT_2", "GEMINI_KEY_AGENT_3", "GEMINI_KEY_AGENT_4",
    "GEMINI_KEY_AGENT_5", "GITHUB_TOKEN", "LINKEDIN_ACCESS_TOKEN",
    "LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET",
)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
_sessions: dict[str, dict[str, Any]] = {}
_session_lock = threading.Lock()
_pipeline_lock = threading.Lock()  # Gemini configuration is process-global.


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__binary__": True, "size": len(value)}
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _state() -> tuple[str, dict[str, Any]]:
    sid = request.headers.get("X-Session-ID") or request.cookies.get("devbuddy_session")
    if not sid or sid not in _sessions:
        sid = uuid.uuid4().hex
        registry = AgentRegistry()
        with _session_lock:
            _sessions[sid] = {
                "registry": registry,
                "engine": OrchestrationEngine(registry),
                "project_path": None,
                "results": None,
                "github_url": None,
                "config": {key: os.getenv(key, "") for key in CONFIG_KEYS},
            }
    return sid, _sessions[sid]


def _response(payload: Any, status: int = 200):
    sid, _ = _state()
    response = jsonify(payload)
    response.status_code = status
    response.headers["X-Session-ID"] = sid
    response.set_cookie("devbuddy_session", sid, httponly=True, samesite="Lax")
    return response


def _error(message: str, status: int = 400):
    return _response({"error": message}, status)


def _require_results(state: dict[str, Any]):
    if not state.get("results"):
        raise ValueError("Run the analysis pipeline first.")


def _agents_payload(state: dict[str, Any]):
    return [{"name": a.name, "description": a.description, "icon": a.icon,
             "color": a.color} for a in state["registry"].get_all_agents()]


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/styles.css")
def styles():
    return send_from_directory(FRONTEND_DIR, "styles.css")


@app.get("/script.js")
def script():
    return send_from_directory(FRONTEND_DIR, "script.js")


@app.get("/api/bootstrap")
def bootstrap():
    _, state = _state()
    config = state["config"]
    return _response({
        "agents": _agents_payload(state),
        "status": {
            "gemini": any(config.get(k) for k in CONFIG_KEYS if k.startswith("GEMINI_") and k != "GEMINI_MODEL"),
            "github": bool(config.get("GITHUB_TOKEN")),
            "linkedin": bool(config.get("LINKEDIN_ACCESS_TOKEN")),
        },
        "model": config.get("GEMINI_MODEL") or "gemini-2.5-flash",
        "project": _project_payload(state) if state.get("project_path") else None,
        "results": _json_safe(state.get("results")),
        "github_url": state.get("github_url"),
    })


def _project_payload(state: dict[str, Any]):
    path = state["project_path"]
    stats = utils.get_project_summary(path)
    return {"name": Path(path).name, "path": path, "summary": stats,
            "tree": utils.get_directory_tree(path)}


@app.post("/api/project/path")
def select_path():
    _, state = _state()
    path = str((request.get_json(silent=True) or {}).get("path", "")).strip()
    if not path or not os.path.isdir(path):
        return _error("The specified directory does not exist or is not a directory.")
    state.update(project_path=os.path.abspath(path), results=None, github_url=None)
    return _response({"project": _project_payload(state)})


@app.post("/api/project/upload")
def upload_zip():
    sid, state = _state()
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename or not uploaded.filename.lower().endswith(".zip"):
        return _error("Choose a valid .zip project archive.")
    target = Path(tempfile.gettempdir()) / "devbuddy_sessions" / sid
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(uploaded.read())) as archive:
            root = target.resolve()
            for member in archive.infolist():
                destination = (target / member.filename).resolve()
                if root != destination and root not in destination.parents:
                    raise ValueError("Archive contains an unsafe path.")
            archive.extractall(target)
        visible = [p for p in target.iterdir() if not p.name.startswith(".") and p.name != "__MACOSX"]
        resolved = visible[0] if len(visible) == 1 and visible[0].is_dir() else target
        state.update(project_path=str(resolved), results=None, github_url=None)
        return _response({"project": _project_payload(state)})
    except (zipfile.BadZipFile, ValueError) as exc:
        shutil.rmtree(target, ignore_errors=True)
        return _error(f"Unable to extract archive: {exc}")


@app.post("/api/pipeline")
def run_pipeline():
    sid, state = _state()
    if not state.get("project_path"):
        return _error("Select a project before running the pipeline.")

    # Dynamic Key Loading: Reload the latest environment variables from .env
    dotenv_path = str(BASE_DIR / ".env")
    import dotenv
    dotenv.load_dotenv(dotenv_path, override=True)

    # Synchronize session config with the freshly loaded environment variables
    for key in CONFIG_KEYS:
        state["config"][key] = os.environ.get(key, "").strip()

    config = state["config"]
    global_key = config.get("GEMINI_API_KEY", "")
    if not global_key and not any(config.get(f"GEMINI_KEY_AGENT_{i}") for i in range(1, 6)):
        return _error("Configure at least one Gemini API key first.")

    def stream():
        with _pipeline_lock:
            previous = {k: os.environ.get(k) for k in CONFIG_KEYS}
            try:
                for key, value in config.items():
                    if value:
                        os.environ[key] = value
                    else:
                        os.environ.pop(key, None)
                # Match the legacy UI's explicit Agent 1 key refresh.
                fresh = ProjectIntelligenceAgent(api_key=config.get("GEMINI_KEY_AGENT_1") or global_key)
                for i, agent in enumerate(state["registry"]._agents):
                    if isinstance(agent, ProjectIntelligenceAgent):
                        state["registry"]._agents[i] = fresh
                for event in state["engine"].run_pipeline(state["project_path"], gemini_api_key=global_key):
                    if event.get("event") == "pipeline_done":
                        state["results"] = event.get("results")
                    yield json.dumps(_json_safe(event), ensure_ascii=False) + "\n"
            except Exception as exc:
                yield json.dumps({"event": "pipeline_error", "error": str(exc)}) + "\n"
            finally:
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    response = Response(stream(), mimetype="application/x-ndjson")
    response.headers["X-Session-ID"] = sid
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/api/results")
def results():
    _, state = _state()
    return _response({"results": _json_safe(state.get("results")), "github_url": state.get("github_url")})


@app.get("/api/artifacts/<int:agent_index>/<path:filename>")
def artifact(agent_index: int, filename: str):
    _, state = _state()
    try:
        _require_results(state)
        agents = state["registry"].get_all_agents()
        if agent_index < 0 or agent_index >= len(agents):
            return _error("Unknown agent.", 404)
        value = state["results"].get(agents[agent_index].name, {}).get("artifacts", {}).get(filename)
        if value is None:
            return _error("Artifact not found.", 404)
        data = value if isinstance(value, bytes) else str(value).encode("utf-8")
        mime = "application/pdf" if filename.endswith(".pdf") else "text/plain"
        return send_file(io.BytesIO(data), mimetype=mime, as_attachment=True, download_name=filename)
    except ValueError as exc:
        return _error(str(exc))


@app.post("/api/github/publish")
def github_publish():
    _, state = _state()
    try:
        _require_results(state)
        body = request.get_json(silent=True) or {}
        name = str(body.get("repo_name", "")).strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", name):
            return _error("Repository name may only contain letters, numbers, dots, dashes and underscores.")
        errors = state["results"].get("qa_analysis", {}).get("errors", [])
        if errors and not body.get("confirm_qa_bypass"):
            return _error("Confirm the critical QA warning before publishing.")
        agent = state["registry"].get_all_agents()[3]
        result = agent.deploy(state["project_path"], state["config"].get("GITHUB_TOKEN", ""), name,
                              str(body.get("description", "")), bool(body.get("private", True)),
                              str(body.get("license", "MIT")))
        if result.get("status") == "success":
            state["github_url"] = result.get("repo_url")
        return _response({"result": _json_safe(result), "github_url": state.get("github_url")})
    except ValueError as exc:
        return _error(str(exc))


@app.post("/api/linkedin/diagnostics")
def linkedin_diagnostics():
    _, state = _state()
    token = state["config"].get("LINKEDIN_ACCESS_TOKEN", "")
    if not token:
        return _error("Configure a LinkedIn access token first.")
    result = state["registry"].get_all_agents()[4].run_diagnostics(token)
    return _response({"result": _json_safe(result)})


@app.post("/api/linkedin/regenerate")
def linkedin_regenerate():
    _, state = _state()
    try:
        _require_results(state)
        context = {"project_analysis": state["results"].get("project_analysis"),
                   "qa_analysis": state["results"].get("qa_analysis"),
                   "gemini_api_key": state["config"].get("GEMINI_API_KEY", "")}
        result = state["registry"].get_all_agents()[4].run(state["project_path"], context)
        if result.get("status") == "success":
            state["results"]["linkedin_branding"] = context.get("linkedin_branding")
        return _response({"result": _json_safe(result), "branding": _json_safe(context.get("linkedin_branding"))})
    except ValueError as exc:
        return _error(str(exc))


@app.post("/api/linkedin/publish")
def linkedin_publish():
    _, state = _state()
    body = request.get_json(silent=True) or {}
    text = str(body.get("text", "")).strip()
    token = state["config"].get("LINKEDIN_ACCESS_TOKEN", "")
    if not token or not text:
        return _error("A LinkedIn token and non-empty post are required.")
    member_id = str(body.get("member_id") or "me")
    result = state["registry"].get_all_agents()[4].publish_post(token, text, member_id)
    return _response({"result": _json_safe(result)})


@app.get("/api/config")
def get_config():
    _, state = _state()
    return _response({"values": {k: (state["config"].get(k, "") if k == "GEMINI_MODEL" else "") for k in CONFIG_KEYS},
                      "configured": {k: bool(state["config"].get(k)) for k in CONFIG_KEYS}})


@app.post("/api/config")
def save_config():
    _, state = _state()
    body = request.get_json(silent=True) or {}
    dotenv_path = str(BASE_DIR / ".env")
    import dotenv
    for key in CONFIG_KEYS:
        if key in body:
            value = str(body[key]).strip()
            # Blank password fields mean "leave the existing secret unchanged".
            if value or key == "GEMINI_MODEL":
                state["config"][key] = value
                os.environ[key] = value
                try:
                    dotenv.set_key(dotenv_path, key, value)
                except Exception as e:
                    app.logger.error(f"Failed to set dotenv key {key}: {e}")
    return _response({"saved": True, "configured": {k: bool(state["config"].get(k)) for k in CONFIG_KEYS}})


@app.errorhandler(413)
def too_large(_):
    return _error("The ZIP exceeds the 100 MB upload limit.", 413)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False, threaded=True)
