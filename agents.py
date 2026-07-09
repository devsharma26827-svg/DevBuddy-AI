"""
Agents module for ProjectPilot AI.
Defines the BaseAgent class, Project Intelligence Agent, Testing & QA Agent,
Documentation Agent (PDF), GitHub Deployment Agent, and LinkedIn Branding Agent.
Uses clean object-oriented inheritance, centralized configuration, and rich docstrings.
"""

from abc import ABC, abstractmethod
import json
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Type, Any, Optional
from pydantic import BaseModel, Field # type: ignore[import-not-found]
import requests # type: ignore[import-not-found]

# Import ReportLab modules for PDF generation
from reportlab.lib.pagesizes import letter # type: ignore[import-not-found]
from reportlab.lib import colors # type: ignore[import-not-found]
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether # type: ignore[import-not-found]
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore[import-not-found]
from reportlab.pdfgen import canvas # type: ignore[import-not-found]

# Import GitPython for repository control
import git # type: ignore[import-not-found]

import utils
import gemini_config

# Constants for prompt token optimizations
CONCISE_PROMPT_GUIDELINE = (
    "\n\n[STRICT LIMITATION]: Keep your output extremely concise. Maximum 300 words. "
    "Use bullet points instead of paragraphs wherever possible. Avoid duplicate explanations "
    "and essays. Return structured formats directly."
)

def get_license_text(license_name: str, project_name: str) -> str:
    """
    Generates standard LICENSE text for selected templates.
    """
    year = datetime.now().year
    holder = "ProjectPilot AI Developers"
    
    if license_name == "MIT":
        return f"""MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    elif license_name == "Apache 2.0":
        return f"""Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {year} {holder}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
    elif license_name == "GPL v3":
        return f"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {year} {holder}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
    elif license_name == "BSD 3-Clause":
        return f"""BSD 3-Clause License

Copyright (c) {year}, {holder}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
    elif license_name == "Mozilla MPL 2.0":
        return f"""Mozilla Public License Version 2.0
==================================

Copyright (c) {year} {holder}. All rights reserved.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
    elif license_name == "Unlicense":
        return """This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
"""
    return ""

def sanitize_report_text(text: str) -> str:
    """
    Sanitizes raw AI response text to make it safe for ReportLab Paragraph rendering.
    Removes unsupported/dangerous HTML tags, maps allowed tags (b, i, u, br, li),
    strips unicode control characters, and escapes XML entities (amp, lt, gt).
    """
    if not text:
        return ""
        
    text = re.sub(r'<(b|strong)\b[^>]*>', '{{B}}', text, flags=re.IGNORECASE)
    text = re.sub(r'</(b|strong)>', '{{/B}}', text, flags=re.IGNORECASE)
    text = re.sub(r'<(i|em)\b[^>]*>', '{{I}}', text, flags=re.IGNORECASE)
    text = re.sub(r'</(i|em)>', '{{/I}}', text, flags=re.IGNORECASE)
    text = re.sub(r'<(u)\b[^>]*>', '{{U}}', text, flags=re.IGNORECASE)
    text = re.sub(r'</(u)>', '{{/U}}', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '{{BR}}', text, flags=re.IGNORECASE)
    
    text = re.sub(r'<li\b[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '{{BR}}', text, flags=re.IGNORECASE)
    text = re.sub(r'</?ul\b[^>]*>', '', text, flags=re.IGNORECASE)
    
    strip_tags = [
        'img', 'script', 'style', 'iframe', 'svg', 'video', 'audio', 
        'a', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        'table', 'tr', 'td', 'th', 'thead', 'tbody', 'link', 'meta'
    ]
    for tag in strip_tags:
        text = re.sub(rf'</?{tag}\b[^>]*>', '', text, flags=re.IGNORECASE)
        
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    text = "".join(ch for ch in text if ch.isprintable() or ch in '\t\n\r')
    text = re.sub(r'&(?!([a-zA-Z0-9]+|#[0-9]+);)', '&amp;', text)
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    
    text = text.replace('{{B}}', '<b>').replace('{{/B}}', '</b>')
    text = text.replace('{{I}}', '<i>').replace('{{/I}}', '</i>')
    text = text.replace('{{U}}', '<u>').replace('{{/U}}', '</u>')
    text = text.replace('{{BR}}', '<br/>')
    
    return text

def safe_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    """
    Instantiates a ReportLab Paragraph safely.
    """
    try:
        sanitized = sanitize_report_text(text)
        return Paragraph(sanitized, style)
    except Exception:
        return Paragraph("Content could not be rendered safely.", style)


class BaseAgent(ABC):
    """
    Abstract base class representing an AI Agent in the ProjectPilot pipeline.
    """
    
    def __init__(self, name: str, description: str, icon: str, color: str):
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color

    @abstractmethod
    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def get_api_key(self, agent_id: int, context: Dict[str, Any]) -> str:
        import os
        from pathlib import Path
        import dotenv
        
        # Load the latest environment variables from .env dynamically
        try:
            dotenv_path = Path(__file__).resolve().parent / ".env"
            dotenv.load_dotenv(str(dotenv_path), override=True)
        except Exception:
            pass

        # Helper to check if a key is non-empty (allow AQ. and other developer service prefixes)
        def is_likely_valid(k: Any) -> bool:
            if not k or not isinstance(k, str):
                return False
            cleaned = k.strip()
            return len(cleaned) > 0

        try:
            import streamlit as st
            
            # 1. Check agent-specific persistent key
            k = st.session_state.get(f"PERSIST_GEMINI_KEY_AGENT_{agent_id}")
            if is_likely_valid(k):
                return k.strip()
                
            # 2. Check agent-specific widget key
            k = st.session_state.get(f"GEMINI_KEY_AGENT_{agent_id}")
            if is_likely_valid(k):
                return k.strip()
                
            # 3. Check global persistent key
            k = st.session_state.get("PERSIST_GEMINI_API_KEY") or st.session_state.get("PERSIST_GEMINI_KEY")
            if is_likely_valid(k):
                return k.strip()
                
            # 4. Check global widget key
            k = st.session_state.get("GEMINI_API_KEY")
            if is_likely_valid(k):
                return k.strip()
        except Exception:
            pass

        # 5. Check context (Agent-specific first, then Global as fallback)
        k = context.get(f"gemini_key_agent_{agent_id}") or context.get(f"GEMINI_KEY_AGENT_{agent_id}")
        if not is_likely_valid(k):
            k = context.get("gemini_api_key") or context.get("GEMINI_API_KEY")
        if is_likely_valid(k):
            return k.strip()

        # 6. Fallback to environment variables (Agent-specific first, then Global as fallback)
        k = os.getenv(f"GEMINI_KEY_AGENT_{agent_id}")
        if not is_likely_valid(k):
            k = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if is_likely_valid(k):
            return k.strip()

        # 7. Last resort fallback to whatever string is found (if any)
        try:
            import streamlit as st
            raw_fallback = (
                st.session_state.get(f"PERSIST_GEMINI_KEY_AGENT_{agent_id}") or 
                st.session_state.get(f"GEMINI_KEY_AGENT_{agent_id}") or 
                st.session_state.get("PERSIST_GEMINI_API_KEY") or 
                st.session_state.get("PERSIST_GEMINI_KEY") or
                st.session_state.get("GEMINI_API_KEY") or
                context.get(f"gemini_key_agent_{agent_id}") or
                context.get(f"GEMINI_KEY_AGENT_{agent_id}") or
                context.get("gemini_api_key") or
                context.get("GEMINI_API_KEY") or
                os.getenv(f"GEMINI_KEY_AGENT_{agent_id}") or
                os.getenv("GEMINI_API_KEY") or
                os.getenv("GOOGLE_API_KEY") or
                ""
            )
            return raw_fallback.strip()
        except Exception:
            return ""


class ProjectAnalysisSchema(BaseModel):
    project_name: str = Field(description="Visual name of the project based on files or folder name")
    primary_language: str = Field(description="Primary programming language detected")
    detected_stack: List[str] = Field(description="All detected stack details")
    project_type: str = Field(description="Type of project")
    architecture_pattern: str = Field(description="Architecture pattern identified")
    estimated_complexity: str = Field(description="Complexity: Low, Medium, or High")
    entry_point: str = Field(description="Entry point file")
    configuration_files: List[str] = Field(description="Configurations found")
    dependencies: List[str] = Field(description="Main software dependency libraries")
    potential_missing_files: List[str] = Field(description="Missing files recommended")
    project_health_overview: str = Field(description="Assessment of codebase health")
    detailed_markdown_report: str = Field(description="A beautiful detailed markdown report")


class ProjectIntelligenceAgent(BaseAgent):
    """
    Agent 1: Project Intelligence Agent.
    Scans repository architecture once and extracts core configurations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="Project Intelligence Agent",
            description="Scans the repository structure, detects stack, dependencies, entry points, and details architectural patterns using Gemini.",
            icon="<span class='material-symbols-outlined'>terminal</span>",
            color="#3498db"
        )
        self.api_key = api_key

    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logs = [f"Initializing directory scan at: {project_path}"]
            
            # Fetch active key if not already set
            if not getattr(self, "api_key", None) or not self.api_key:
                self.api_key = self.get_api_key(1, context)
                
            if not self.api_key:
                raise ValueError("API Key is missing for Project Intelligence Agent.")
                
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
                
            directory_tree = utils.get_directory_tree(project_path, max_depth=4)
            logs.append("Generating directory structure representation...")
            
            file_contents_block = []
            character_budget = 60000
            accumulated_chars = 0
            
            priority_files = ["requirements.txt", "package.json", "setup.py", "pyproject.toml", 
                              "cargo.toml", "go.mod", "pom.xml", "build.gradle", "dockerfile", 
                              "readme.md", "app.py", "main.py", "index.js"]
                              
            scanned_files = list(utils.scan_project_files(project_path))
            
            def sort_priority(item):
                filename = os.path.basename(item["relative_path"]).lower()
                if filename in priority_files:
                    return (0, priority_files.index(filename))
                return (1, item["relative_path"])
                
            scanned_files.sort(key=sort_priority)
            
            for file_item in scanned_files:
                rel_path = file_item["relative_path"]
                content = file_item["content"]
                
                file_chars = len(content)
                if accumulated_chars + file_chars > character_budget:
                    remaining_budget = character_budget - accumulated_chars
                    if remaining_budget > 100:
                        file_contents_block.append(
                            f"--- File: {rel_path} (Truncated) ---\n{content[:remaining_budget]}\n...\n"
                        )
                    break
                    
                file_contents_block.append(f"--- File: {rel_path} ---\n{content}\n")
                accumulated_chars += file_chars
                
            prompt = f"""
You are the Project Intelligence Agent of ProjectPilot AI.
Analyze the project structures and files to understand its architecture.

Here is the directory tree diagram:
```text
{directory_tree}
```

Here are the contents of key files in the repository:
{"".join(file_contents_block)}

Analyze this project thoroughly and provide a structured assessment in JSON.
{CONCISE_PROMPT_GUIDELINE}
"""
            logs.append("Sending analysis payload to Gemini...")
            
            response_text = gemini_config.generate_gemini_content(
                api_key=self.api_key,
                prompt=prompt,
                response_schema=ProjectAnalysisSchema,
                temperature=0.1,
                logs_accumulator=logs
            )
            
            analysis_data = json.loads(response_text)
            logs.append("[OK] Successfully parsed project analysis.")
            
            config_files_str = ', '.join([f'`{cfg}`' for cfg in analysis_data.get('configuration_files', [])])
            dependencies_str = ', '.join([f'`{dep}`' for dep in analysis_data.get('dependencies', [])])
            missing_files_str = ', '.join([f'`{f}`' for f in analysis_data.get('potential_missing_files', [])])
            
            summary = (
                f"# Project Analysis: {analysis_data.get('project_name')}\n\n"
                f"### Stack & Architecture\n"
                f"- **Primary Language:** {analysis_data.get('primary_language')}\n"
                f"- **Detected Stack:** {', '.join(analysis_data.get('detected_stack', []))}\n"
                f"- **Project Type:** {analysis_data.get('project_type')}\n"
                f"- **Architecture Pattern:** {analysis_data.get('architecture_pattern')}\n"
                f"- **Estimated Complexity:** {analysis_data.get('estimated_complexity')}\n"
                f"- **Entry Point File:** `{analysis_data.get('entry_point')}`\n\n"
                f"### Configuration & Dependencies\n"
                f"- **Configuration Files:** {config_files_str}\n"
                f"- **Key Dependencies:** {dependencies_str}\n\n"
                f"### Health & Readiness\n"
                f"- **Project Health Overview:** {analysis_data.get('project_health_overview')}\n"
                f"- **Recommended / Missing Files:** {missing_files_str}\n\n"
                f"***\n"
                f"{analysis_data.get('detailed_markdown_report')}"
            )
            
            return {
                "status": "success",
                "summary": summary,
                "logs": logs,
                "artifacts": {
                    "project_analysis_report.md": summary,
                    "project_tree.txt": directory_tree
                },
                "project_analysis": analysis_data
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }


class QACheckItem(BaseModel):
    check_name: str = Field(description="Name of the QA check")
    status: str = Field(description="Passed, Warning, or Error")
    details: str = Field(description="Findings summary")


class TestingQAAnalysisSchema(BaseModel):
    passed_checks: List[QACheckItem] = Field(description="List of QA checks that passed")
    warnings: List[QACheckItem] = Field(description="List of QA warnings")
    errors: List[QACheckItem] = Field(description="List of critical errors/risks")
    overall_health_score: int = Field(description="Codebase health score between 0 and 100")
    production_readiness_score: int = Field(description="Readiness score between 0 and 100")
    detailed_qa_report: str = Field(description="Detailed markdown QA report")


class TestingAgent(BaseAgent):
    """
    Agent 2: Testing & QA Agent.
    Reuses Agent 1 context only. Does not scan folder files or send source code.
    """
    
    def __init__(self):
        super().__init__(
            name="Testing & QA Agent",
            description="Analyzes the project structure for syntax errors, smells, security risks, broken dependencies, and QA scores.",
            icon="<span class='material-symbols-outlined'>bug_report</span>",
            color="#e74c3c"
        )

    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logs = ["Initializing QA Audit Scan..."]
        
        api_key = self.get_api_key(2, context)
        if not api_key:
            logs.append("[ERROR] Error: Gemini API Key is missing.")
            raise ValueError("Gemini API Key is missing. Configure GEMINI_KEY_AGENT_2.")
            
        agent1_data = context.get("project_analysis")
        if not agent1_data:
            raise ValueError("Agent 1 structured context is missing. Cannot perform QA audit.")
            
        prompt = f"""
You are the Testing & QA Agent of ProjectPilot AI.
Evaluate the project health and production readiness using ONLY the structured context provided by Agent 1.
Do NOT request code files or directories. Analyze the dependencies, stack details, and configuration file lists.
Formulate checks, errors, warnings, and overall scores based on this data.

Agent 1 Structured Context:
{json.dumps(agent1_data, indent=2)}

{CONCISE_PROMPT_GUIDELINE}
"""
        logs.append("Sending audit request to Gemini (Reusing Agent 1 Context)...")
        try:
            response_text = gemini_config.generate_gemini_content(
                api_key=api_key,
                prompt=prompt,
                response_schema=TestingQAAnalysisSchema,
                temperature=0.1,
                logs_accumulator=logs
            )
            
            qa_data = json.loads(response_text)
            logs.append("[OK] Successfully parsed Testing & QA data.")
            
            summary = (
                f"# Testing & QA Report\n"
                f"### QA Overview Metrics\n"
                f"- **Overall Health Score:** {qa_data.get('overall_health_score')}/100\n"
                f"- **Production Readiness Rating:** {qa_data.get('production_readiness_score')}/100\n\n"
                f"### Audit Checks Summary\n"
                f"- **Passed Checks:** {len(qa_data.get('passed_checks', []))}\n"
                f"- **Warnings & Smells:** {len(qa_data.get('warnings', []))}\n"
                f"- **Errors & Security Risks:** {len(qa_data.get('errors', []))}\n\n"
                f"***\n"
                f"{qa_data.get('detailed_qa_report')}"
            )
            
            context["qa_analysis"] = qa_data
            
            return {
                "status": "success",
                "summary": summary,
                "logs": logs,
                "artifacts": {
                    "qa_audit_report.md": summary
                }
            }
        except Exception as e:
            logs.append(f"[ERROR] Error calling Gemini: {str(e)}")
            raise e


class DocumentationSchema(BaseModel):
    executive_summary: str = Field(description="Executive Summary explaining overall readiness")
    project_overview: str = Field(description="Overview of the project")
    architecture_summary: str = Field(description="Summary of architectural model")
    detected_technologies: str = Field(description="Analysis of tools used")
    folder_structure: str = Field(description="Critique of directory structure")
    issues_found: List[str] = Field(description="Critical issues")
    warnings: List[str] = Field(description="Warnings")
    recommendations: List[str] = Field(description="Actionable recommendations")
    strengths: List[str] = Field(description="Strengths")
    weaknesses: List[str] = Field(description="Weaknesses")
    production_readiness: str = Field(description="Readiness evaluation")
    overall_score_summary: str = Field(description="Overview of evaluation scores")
    detailed_report_md: str = Field(description="Full markdown report")


class NumberedCanvas(canvas.Canvas):
    """
    Custom ReportLab Canvas to dynamically compute total pages and draw headers/footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#7f8c8d"))
        
        # Header (Top Margin)
        self.drawString(54, 750, "ProjectPilot AI - Professional Project Report")
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer (Bottom Margin)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential - For Internal Review Only")
        self.line(54, 52, 558, 52)
        
        self.restoreState()


class DocumentationAgent(BaseAgent):
    """
    Agent 3: Documentation Agent.
    Aggregates findings from Agent 1 and Agent 2 context. Does not call Gemini with file lists/trees.
    """
    
    def __init__(self):
        super().__init__(
            name="Documentation Agent",
            description="Aggregates analysis and audit outputs, compiles a professional report, and generates a downloadable PDF using ReportLab.",
            icon="<span class='material-symbols-outlined'>description</span>",
            color="#f1c40f"
        )

    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logs = ["Initializing Documentation Aggregator Agent..."]
        
        api_key = self.get_api_key(3, context)
        if not api_key:
            logs.append("[ERROR] Error: Gemini API Key is missing.")
            raise ValueError("Gemini API Key is missing. Configure GEMINI_KEY_AGENT_3.")
            
        agent1_data = context.get("project_analysis")
        agent2_data = context.get("qa_analysis")
        directory_tree = utils.get_directory_tree(project_path, max_depth=4)
        
        prompt = f"""
You are the Documentation Agent of ProjectPilot AI.
Compile a professional project report using the structured context from Agent 1 and Agent 2 only.
Do NOT reference external code files or directories.

Agent 1 Context:
{json.dumps(agent1_data, indent=2) if agent1_data else "No Intelligence data"}

Agent 2 Context:
{json.dumps(agent2_data, indent=2) if agent2_data else "No QA data"}

{CONCISE_PROMPT_GUIDELINE}
"""
        logs.append("Sending report synthesis request to Gemini (Reusing Structured Contexts)...")
        try:
            response_text = gemini_config.generate_gemini_content(
                api_key=api_key,
                prompt=prompt,
                response_schema=DocumentationSchema,
                temperature=0.2,
                logs_accumulator=logs
            )
            
            doc_data = json.loads(response_text)
            logs.append("[OK] Successfully parsed project report JSON.")
            
            health_score = agent2_data.get("overall_health_score", 0) if agent2_data else 0
            readiness_score = agent2_data.get("production_readiness_score", 0) if agent2_data else 0
            scores = {"health": health_score, "readiness": readiness_score}
            
            pdf_bytes = b""
            pdf_warnings = []
            try:
                pdf_bytes = self._generate_pdf(doc_data, directory_tree, scores)
                logs.append("[OK] PDF Report Generated Successfully.")
            except Exception as pdf_error:
                pdf_warnings.append(f"PDF compilation failed dynamically: {str(pdf_error)}")
                logs.append(f"[WARN] PDF Generation failed: {str(pdf_error)}")
                
            context["project_report"] = doc_data
            summary = doc_data.get("detailed_report_md", "# Project Documentation Report")
            
            return {
                "status": "success",
                "summary": summary,
                "logs": logs,
                "artifacts": {
                    "project_report.md": summary,
                    "project_report.pdf": pdf_bytes
                },
                "warnings": pdf_warnings
            }
        except Exception as e:
            logs.append(f"[ERROR] Error compiling documentation: {str(e)}")
            raise e

    def _generate_pdf(self, doc_data: Dict[str, Any], tree_str: str, scores: Dict[str, int]) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72
        )
        styles = getSampleStyleSheet()
        primary_color = colors.HexColor('#0f2c59')
        secondary_color = colors.HexColor('#3f72af')
        text_color = colors.HexColor('#2c3e50')
        light_bg = colors.HexColor('#f8f9fa')
        
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=primary_color, spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#7f8c8d'), spaceAfter=20
        )
        h1_style = ParagraphStyle(
            'ReportH1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=secondary_color, spaceBefore=14, spaceAfter=8, keepWithNext=True
        )
        body_style = ParagraphStyle(
            'ReportBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=text_color, spaceAfter=6
        )
        bullet_style = ParagraphStyle(
            'ReportBullet', parent=body_style, leftIndent=15, firstLineIndent=-8, spaceAfter=4
        )
        code_style = ParagraphStyle(
            'ReportCode', parent=styles['Normal'], fontName='Courier', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#27ae60'), spaceAfter=6
        )
        
        story = []
        story.append(safe_paragraph("ProjectPilot AI", subtitle_style))
        story.append(safe_paragraph("Codebase Packaging & Readiness Report", title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=15))
        
        scores_data = [
            [safe_paragraph("<b>Evaluation Metric</b>", body_style), safe_paragraph("<b>Rating / Status</b>", body_style)],
            [safe_paragraph("Codebase Quality & Health", body_style), safe_paragraph(f"<b>Health Score:</b> {scores['health']}/100", body_style)],
            [safe_paragraph("Production Deployment Readiness", body_style), safe_paragraph(f"<b>Production Readiness:</b> {scores['readiness']}/100", body_style)],
        ]
        scores_table = Table(scores_data, colWidths=[280, 224])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f2f6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dfe4ea')),
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 15))
        
        def append_section(title: str, content: str):
            story.append(safe_paragraph(title, h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bdc3c7"), spaceAfter=8))
            story.append(safe_paragraph(content, body_style))
            story.append(Spacer(1, 8))
            
        def append_bullet_section(title: str, bullets: List[str]):
            story.append(safe_paragraph(title, h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bdc3c7"), spaceAfter=8))
            if not bullets:
                story.append(safe_paragraph("None identified.", body_style))
            else:
                for b in bullets:
                    story.append(safe_paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 8))

        append_section("1. Executive Summary", doc_data.get("executive_summary", ""))
        append_section("2. Project Overview", doc_data.get("project_overview", ""))
        append_section("3. Architecture Summary", doc_data.get("architecture_summary", ""))
        append_section("4. Detected Technologies", doc_data.get("detected_technologies", ""))
        
        story.append(safe_paragraph("5. Folder Structure & Modular Critique", h1_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bdc3c7"), spaceAfter=8))
        story.append(safe_paragraph(doc_data.get("folder_structure", ""), body_style))
        
        tree_paragraphs = [safe_paragraph(line.replace(" ", "&nbsp;"), code_style) for line in tree_str.split("\n")]
        tree_table = Table([[p] for p in tree_paragraphs], colWidths=[504])
        tree_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e1e8ed')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(KeepTogether(tree_table))
        story.append(Spacer(1, 10))

        append_bullet_section("6. Critical Issues Found", doc_data.get("issues_found", []))
        append_bullet_section("7. Warnings & Code Smells", doc_data.get("warnings", []))
        append_bullet_section("8. Step-by-Step Recommendations", doc_data.get("recommendations", []))
        append_bullet_section("9. Technical Strengths", doc_data.get("strengths", []))
        append_bullet_section("10. Technical Weaknesses", doc_data.get("weaknesses", []))
        append_section("11. Production Readiness Review", doc_data.get("production_readiness", ""))
        append_section("12. Evaluation & Score Summary", doc_data.get("overall_score_summary", ""))
        
        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()


class GitHubPreflightSchema(BaseModel):
    suggested_repo_name: str = Field(description="Suggested repository name (lowercase, alphanumeric, and dashes/underscores only, e.g. devbuddy-project)")
    suggested_repo_description: str = Field(description="A short, clear GitHub repository description")
    generated_readme: str = Field(description="A highly detailed, professional README.md markdown content (minimum 300 words) containing: Project Title, Description, Features, Tech Stack, Installation Steps, and Usage.")
    generated_gitignore: str = Field(description="Standard .gitignore content based on the project's tech stack")


class GitHubDeploymentAgent(BaseAgent):
    """
    Agent 4: GitHub Deployment Agent.
    Prepares codebase and suggestions for repository publishing using Gemini pre-flight and GitPython deployment.
    """
    
    def __init__(self):
        super().__init__(
            name="GitHub Deployment Agent",
            description="Prepares codebase for repository publishing. Exposes publishing logic to configure remotes, commit, and push directly to GitHub.",
            icon="<span class='material-symbols-outlined'>cloud_upload</span>",
            color="#2ecc71"
        )

    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs pre-flight local Git checks and uses Gemini to suggest repo name, description, README, and gitignore.
        """
        logs = ["Initializing GitHub Deployment pre-flight checks..."]
        
        is_git_init = os.path.exists(os.path.join(project_path, ".git"))
        summary_stats = utils.get_project_summary(project_path)
        file_count = summary_stats.get("file_count", 0)
        
        agent1_data = context.get("project_analysis") or {}
        agent2_data = context.get("qa_analysis") or {}
        project_name = agent1_data.get("project_name", "codebase")
        primary_lang = agent1_data.get("primary_language", "unspecified")
        
        api_key = self.get_api_key(4, context)
        if not api_key:
            logs.append("[WARN] Gemini API Key is missing. Falling back to default pre-flight details.")
            self.suggested_repo_name = "".join([c if c.isalnum() or c in ("-", "_") else "-" for c in project_name]).lower()
            self.suggested_repo_description = "Repository compiled and deployed automatically by DevBuddy AI."
            self.generated_readme = f"# {project_name}\n\nRepository for {project_name}.\n"
            self.generated_gitignore = "# Default ignore\n.env\n__pycache__/\nnode_modules/\nvenv/\n"
        else:
            logs.append("Sending pre-flight generation request to Gemini (acting as Senior DevOps Engineer)...")
            prompt = f"""
You are the Senior DevOps Engineer of ProjectPilot AI.
Analyze the project structured analysis and QA audit results to generate deployment assets.

Project Analysis Context:
{json.dumps(agent1_data, indent=2)}

QA Audit Context:
{json.dumps(agent2_data, indent=2)}

Please perform the following actions:
1. Suggest a sanitized GitHub repository name (lowercase, alphanumerics, dashes or underscores only).
2. Suggest a short, professional repository description.
3. Generate a highly detailed, professional README.md (minimum 300 words) containing:
   - Project Title
   - Description (what the project is about and its purpose)
   - Features (core capabilities)
   - Tech Stack (languages, frameworks, dependencies used)
   - Installation Steps (how to set it up locally)
   - Usage (how to run and interact with it)
4. Generate a standard .gitignore file appropriate for this tech stack (e.g. ignoring node_modules, Python cache files, virtual environments, .env files, etc.)

Provide the output in structured JSON.
"""
            try:
                response_text = gemini_config.generate_gemini_content(
                    api_key=api_key,
                    prompt=prompt,
                    response_schema=GitHubPreflightSchema,
                    temperature=0.2,
                    logs_accumulator=logs
                )
                res_data = json.loads(response_text)
                self.suggested_repo_name = res_data.get("suggested_repo_name")
                self.suggested_repo_description = res_data.get("suggested_repo_description")
                self.generated_readme = res_data.get("generated_readme")
                self.generated_gitignore = res_data.get("generated_gitignore")
                logs.append("[OK] Successfully generated pre-flight assets via Gemini.")
            except Exception as e:
                logs.append(f"[WARN] Gemini generation failed: {str(e)}. Falling back to defaults.")
                self.suggested_repo_name = "".join([c if c.isalnum() or c in ("-", "_") else "-" for c in project_name]).lower()
                self.suggested_repo_description = "Repository compiled and deployed automatically by DevBuddy AI."
                self.generated_readme = f"# {project_name}\n\nRepository for {project_name}.\n"
                self.generated_gitignore = "# Default ignore\n.env\n__pycache__/\nnode_modules/\nvenv/\n"
        
        # Override the project name in project_analysis so the UI text field gets pre-filled with the suggested name
        if "project_analysis" in context:
            context["project_analysis"]["project_name"] = self.suggested_repo_name
            
        suggested_msg = f"feat: initial project structure for {self.suggested_repo_name}"
        release_notes = f"Initial packaging of {project_name} built with {primary_lang}."
        
        summary = (
            "### GitHub Deployment Agent Pre-flight\n"
            "This project is ready to be published to a remote GitHub repository.\n\n"
            "**Repository Stats:**\n"
            f"- **Local Git Status:** {'Initialized' if is_git_init else 'Not Initialized (Will be created dynamically)'}\n"
            f"- **Target Files for Commit:** {file_count} files\n"
            f"- **Suggested Repository Name:** `{self.suggested_repo_name}`\n"
            f"- **Suggested Repository Description:** {self.suggested_repo_description}\n"
            f"- **Suggested Commit Msg:** `{suggested_msg}`\n"
            f"- **Release Summary:** {release_notes}\n\n"
            "**Suggested .gitignore Preview:**\n"
            "```text\n"
            f"{self.generated_gitignore[:300]}...\n"
            "```\n\n"
            "**Suggested README.md Preview:**\n"
            "```markdown\n"
            f"{self.generated_readme[:500]}...\n"
            "```\n\n"
            "> [!NOTE]\n"
            "> The publish form is loaded interactively inside the tab panel below. **Select Yes** to input repository details and publish."
        )
        return {
            "status": "success",
            "summary": summary,
            "logs": logs,
            "artifacts": {
                "readme_preview.md": self.generated_readme,
                "gitignore_preview.txt": self.generated_gitignore
            }
        }

    def deploy(self, project_path: str, github_token: str, repo_name: str, repo_description: str, is_private: bool, license_name: str) -> Dict[str, Any]:
        """
        Commits local files, performs readiness audits, auto-generates missing files,
        updates gitignore, and publishes to a newly created GitHub repository.
        """
        if not github_token:
            return {"status": "failed", "error": "GitHub Personal Access Token is missing."}
            
        generated_files = []
        ignored_files = [".env", ".env.local", ".env.production", ".env.development", "__pycache__", ".pyc", "node_modules", "venv", ".git", ".vscode/settings.json"]
        
        # 1. GitHub Readiness Audit & File Generation
        # README.md
        readme_path = os.path.join(project_path, "README.md")
        if not os.path.exists(readme_path) or (getattr(self, 'generated_readme', '') and len(open(readme_path, 'r', encoding='utf-8').read().strip()) < 50):
            readme_content = getattr(self, 'generated_readme', None)
            if not readme_content:
                readme_content = f"# {repo_name}\n\n{repo_description}\n\nProject uploaded via ProjectPilot AI.\n"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            generated_files.append("README.md")
            
        # LICENSE
        if license_name != "No License":
            license_path = os.path.join(project_path, "LICENSE")
            with open(license_path, "w", encoding="utf-8") as f:
                f.write(get_license_text(license_name, repo_name))
            generated_files.append("LICENSE")
            
        # .gitignore & Auto-Update
        gitignore_path = os.path.join(project_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            gitignore_content = getattr(self, 'generated_gitignore', None)
            if not gitignore_content:
                gitignore_content = "# ProjectPilot AI Ignore Rules\n.env\n__pycache__/\nnode_modules/\nvenv/\n"
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(gitignore_content)
            generated_files.append(".gitignore")
        else:
            existing_ignores = set()
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    existing_ignores.add(line.strip())
            
            suggested_rules = []
            gitignore_content = getattr(self, 'generated_gitignore', '')
            if gitignore_content:
                for line in gitignore_content.split("\n"):
                    rule = line.strip()
                    if rule and not rule.startswith("#"):
                        suggested_rules.append(rule)
            
            needed_ignores = [
                ".env", ".env.local", ".env.production", ".env.development",
                "__pycache__/", "*.pyc", "node_modules/", "venv/", ".vscode/settings.json"
            ]
            for rule in suggested_rules:
                if rule not in needed_ignores:
                    needed_ignores.append(rule)
                    
            ignores_to_add = [ig for ig in needed_ignores if ig not in existing_ignores]
            if ignores_to_add:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n\n# Added by ProjectPilot AI\n")
                    for ig in ignores_to_add:
                        f.write(f"{ig}\n")
                generated_files.append(".gitignore (Updated)")
                
        # requirements.txt
        has_python = False
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in utils.IGNORE_DIRS and not d.startswith(".")]
            if any(file.endswith(".py") for file in files):
                has_python = True
                break
        if has_python:
            req_path = os.path.join(project_path, "requirements.txt")
            if not os.path.exists(req_path):
                with open(req_path, "w", encoding="utf-8") as f:
                    f.write("requests\ngoogle-genai\nstreamlit\npython-dotenv\n")
                generated_files.append("requirements.txt")
                
        # package.json
        has_node = False
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in utils.IGNORE_DIRS and not d.startswith(".")]
            if any(file.endswith((".js", ".ts", ".jsx", ".tsx")) for file in files):
                has_node = True
                break
        if has_node:
            pkg_path = os.path.join(project_path, "package.json")
            if not os.path.exists(pkg_path):
                pkg_content = {
                    "name": repo_name.lower().replace(" ", "-"),
                    "version": "1.0.0",
                    "description": repo_description,
                    "main": "index.js",
                    "scripts": {
                        "start": "node index.js"
                    }
                }
                with open(pkg_path, "w", encoding="utf-8") as f:
                    json.dump(pkg_content, f, indent=2)
                generated_files.append("package.json")
                
        # .env.example
        env_example_path = os.path.join(project_path, ".env.example")
        if not os.path.exists(env_example_path):
            with open(env_example_path, "w", encoding="utf-8") as f:
                f.write("# Environment Configuration Template\nPORT=8080\nAPI_KEY=your_key_here\n")
            generated_files.append(".env.example")
            
        # docs/ folder
        docs_dir = os.path.join(project_path, "docs")
        if not os.path.exists(docs_dir):
            try:
                os.makedirs(docs_dir, exist_ok=True)
                with open(os.path.join(docs_dir, "index.md"), "w", encoding="utf-8") as f:
                    f.write(f"# Documentation for {repo_name}\nWelcome to the documentation.\n")
                generated_files.append("docs/")
            except Exception:
                pass
                
        # Compute Ready Score
        deductions = len(generated_files) * 10
        ready_score = max(100 - deductions, 40)
        
        # 2. Local git repository initialization & commit
        try:
            if not os.path.exists(os.path.join(project_path, ".git")):
                repo = git.Repo.init(project_path)
            else:
                repo = git.Repo(project_path)
            with repo.config_writer() as cw:
                cw.set_value("user", "name", "ProjectPilot AI")
                cw.set_value("user", "email", "pilot@projectpilot.ai")
                
            repo.git.add(A=True)
            if repo.is_dirty(untracked_files=True):
                commit = repo.index.commit("Initial commit by ProjectPilot AI")
                commit_hash = commit.hexsha
            else:
                try:
                    commit_hash = repo.head.commit.hexsha
                except ValueError:
                    commit = repo.index.commit("Initial empty commit by ProjectPilot AI")
                    commit_hash = commit.hexsha
            
            # Create remote repo via GitHub API
            api_url = "https://api.github.com/user/repos"
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            payload = {"name": repo_name, "description": repo_description, "private": is_private, "auto_init": False}
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code != 201:
                error_msg = response.json().get("message", "Failed to create remote repository.")
                return {"status": "failed", "error": f"GitHub API Error: {error_msg}"}
            repo_info = response.json()
            clone_url = repo_info.get("clone_url")
            html_url = repo_info.get("html_url")
            auth_url = clone_url.replace("https://", f"https://{github_token}@")
            if "origin" in repo.remotes:
                origin = repo.remote("origin")
                origin.set_url(auth_url)
            else:
                origin = repo.create_remote("origin", auth_url)
            try:
                active_branch = repo.active_branch.name
            except TypeError:
                active_branch = "master"
            origin.push(refspec=f"{active_branch}:{active_branch}")
            
            return {
                "status": "success",
                "repo_url": html_url,
                "commit_hash": commit_hash,
                "branch": active_branch,
                "license": license_name,
                "files_generated": generated_files,
                "files_ignored": ignored_files,
                "ready_score": ready_score
            }
        except Exception as err:
            return {"status": "failed", "error": str(err)}


class LinkedInBrandingSchema(BaseModel):
    short_version: str = Field(description="A short, catchy LinkedIn launch post (1-2 paragraphs). Must include placeholder tag '[Insert GitHub URL here]'.")
    long_version: str = Field(description="A detailed LinkedIn launch post with bullet points. Must include placeholder tag '[Insert GitHub URL here]'.")
    learning_highlights: List[str] = Field(description="Key educational lessons learned or features built")
    problem_solved: str = Field(description="A 1-paragraph summary of the core problem solved by this project")
    tech_stack: List[str] = Field(description="List of main technologies used")
    hashtags: List[str] = Field(description="Trending launch hashtags")
    project_summary: str = Field(description="A clean 2-sentence summary pitch of the project")


class LinkedInBrandingAgent(BaseAgent):
    """
    Agent 5: LinkedIn Branding Agent.
    Generates branding copy using Gemini by referencing Agent 1 and 2 context.
    """
    
    def __init__(self):
        super().__init__(
            name="LinkedIn Branding Agent",
            description="Crafts professional promotional posts, hashtags, taglines, and learning highlights to showcase the project.",
            icon="<span class='material-symbols-outlined'>campaign</span>",
            color="#9b59b6"
        )

    def run(self, project_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logs = ["Initializing LinkedIn Branding synthesis..."]
        
        api_key = self.get_api_key(5, context)
        if not api_key:
            logs.append("[ERROR] Error: Gemini API Key is missing.")
            raise ValueError("Gemini API Key is missing. Please configure GEMINI_KEY_AGENT_5.")
            
        agent1_data = context.get("project_analysis")
        agent2_data = context.get("qa_analysis")
        
        prompt = f"""
You are the LinkedIn Branding Agent of ProjectPilot AI.
Your role is to craft a professional launch branding package for this project using Agent 1 and 2 context.

Project Context:
{json.dumps(agent1_data, indent=2) if agent1_data else "No Intelligence data"}

QA Context:
{json.dumps(agent2_data, indent=2) if agent2_data else "No QA data"}

Please generate two detailed, engaging LinkedIn launch posts following these instructions:
1. Short Version: Catchy, quick hook, 1-2 paragraphs. Minimum 150 words. Must contain:
   - A strong hook
   - 3-5 bullet points of key learnings/achievements
   - 5-7 relevant hashtags
   - A call-to-action with the placeholder '[Insert GitHub URL here]'
2. Long Version: Structured hook, problem statement, solution details, key features, and call-to-action. Minimum 250 words. Must contain:
   - An engaging and strong hook
   - A clear problem statement and solution description
   - 3-5 detailed bullet points of learnings or structural highlights
   - 5-7 relevant hashtags
   - A call-to-action with the placeholder '[Insert GitHub URL here]'

Provide also:
- Problem Solved.
- Tech Stack details.
- Learning Highlights (3-5 items).
- Recommended Hashtags (5-7 items).
- Project Summary.
"""
        logs.append("Sending launch kit generation request to Gemini...")
        try:
            # Call centralized Gemini configuration helper
            response_text = gemini_config.generate_gemini_content(
                api_key=api_key,
                prompt=prompt,
                response_schema=LinkedInBrandingSchema,
                temperature=0.3,
                logs_accumulator=logs
            )
            
            brand_data = json.loads(response_text)
            logs.append("[OK] Successfully parsed LinkedIn branding package JSON.")
            context["linkedin_branding"] = brand_data
            
            summary = (
                f"# LinkedIn Launch Kit Summary\n\n"
                f"**Project Pitch:** {brand_data.get('project_summary')}\n\n"
                f"**Skills Highlighted:** {', '.join(brand_data.get('tech_stack', []))}\n\n"
                f"**Post Status:** Pre-compiled launch copies are editable inside the tab layout below."
            )
            return {
                "status": "success",
                "summary": summary,
                "logs": logs,
                "artifacts": {
                    "linkedin_branding_kit.json": response_text
                }
            }
        except Exception as e:
            logs.append(f"[ERROR] Error generating branding data: {str(e)}")
            raise e

    def run_diagnostics(self, access_token: str) -> Dict[str, Any]:
        """
        Runs complete token validation and profile lookup diagnostics,
        printing and logging exact HTTP request and response structures.
        """
        debug_logs = []
        token_valid = "No"
        member_access = "No"
        publish_permission = "No"
        missing_scopes = ["w_member_social"]
        suggested_fix = "Please verify your LINKEDIN_ACCESS_TOKEN in .env."
        member_id = None
        expiry = "Unknown"
        scopes = []
        
        try:
            import streamlit as st
            client_id = st.session_state.get("LINKEDIN_CLIENT_ID") or os.getenv("LINKEDIN_CLIENT_ID")
            client_secret = st.session_state.get("LINKEDIN_CLIENT_SECRET") or os.getenv("LINKEDIN_CLIENT_SECRET")
        except Exception:
            client_id = os.getenv("LINKEDIN_CLIENT_ID")
            client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        
        # 1. Attempt token introspection (standard check)
        if client_id and client_secret:
            intro_url = "https://www.linkedin.com/oauth/v2/introspectToken"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "token": access_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
            debug_logs.append("--- [HTTP REQUEST: Token Introspection] ---")
            debug_logs.append(f"POST {intro_url}")
            debug_logs.append(f"Headers: {json.dumps(headers)}")
            debug_logs.append(f"Body: token=[HIDDEN]&client_id={client_id}")
            
            try:
                res = requests.post(intro_url, data=data, headers=headers)
                debug_logs.append("--- [HTTP RESPONSE: Token Introspection] ---")
                debug_logs.append(f"Status Code: {res.status_code}")
                debug_logs.append(f"Response Body: {res.text}")
                
                if res.status_code == 200:
                    info = res.json()
                    active = info.get("active", False)
                    if active:
                        token_valid = "Yes"
                        member_id = info.get("sub")
                        scope_str = info.get("scope", "")
                        scopes = [s.strip() for s in scope_str.split(" ") if s.strip()]
                        exp_ts = info.get("exp")
                        if exp_ts:
                            expiry = datetime.fromtimestamp(exp_ts).strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                debug_logs.append(f"Exception during introspection: {str(e)}")
                
        # 2. Try Userinfo endpoint (OIDC OpenID Connect)
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        headers_userinfo = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        debug_logs.append("--- [HTTP REQUEST: User Profile Info (OIDC)] ---")
        debug_logs.append(f"GET {userinfo_url}")
        debug_logs.append("Headers: Authorization=Bearer [HIDDEN], Accept=application/json")
        
        try:
            res = requests.get(userinfo_url, headers=headers_userinfo)
            debug_logs.append("--- [HTTP RESPONSE: User Profile Info (OIDC)] ---")
            debug_logs.append(f"Status Code: {res.status_code}")
            debug_logs.append(f"Response Body: {res.text}")
            
            if res.status_code == 200:
                token_valid = "Yes"
                member_access = "Yes"
                info = res.json()
                if not member_id:
                    member_id = info.get("sub")
                if "openid" not in scopes:
                    scopes.append("openid")
                if "profile" not in scopes:
                    scopes.append("profile")
        except Exception as e:
            debug_logs.append(f"Exception during userinfo: {str(e)}")
            
        # 3. Try Legacy /v2/me endpoint
        if member_access == "No":
            me_url = "https://api.linkedin.com/v2/me"
            headers_me = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            debug_logs.append("--- [HTTP REQUEST: User Profile Info (Legacy)] ---")
            debug_logs.append(f"GET {me_url}")
            debug_logs.append("Headers: Authorization=Bearer [HIDDEN], X-Restli-Protocol-Version=2.0.0")
            
            try:
                res = requests.get(me_url, headers=headers_me)
                debug_logs.append("--- [HTTP RESPONSE: User Profile Info (Legacy)] ---")
                debug_logs.append(f"Status Code: {res.status_code}")
                debug_logs.append(f"Response Body: {res.text}")
                
                if res.status_code == 200:
                    token_valid = "Yes"
                    member_access = "Yes"
                    info = res.json()
                    if not member_id:
                        member_id = info.get("id")
                    if "r_liteprofile" not in scopes:
                        scopes.append("r_liteprofile")
            except Exception as e:
                debug_logs.append(f"Exception during legacy me: {str(e)}")
                
        # 4. Determine publish permissions and suggested fixes
        if token_valid == "Yes":
            if client_id and client_secret:
                if "w_member_social" in scopes:
                    publish_permission = "Yes"
                    missing_scopes = [s for s in ["w_member_social"] if s not in scopes]
                    suggested_fix = "No action needed. Ready to publish."
                else:
                    publish_permission = "No"
                    missing_scopes = ["w_member_social"]
                    suggested_fix = (
                        "The access token is valid but missing the 'w_member_social' scope. "
                        "Regenerate your token in the Developer Portal with 'Share on LinkedIn' enabled."
                    )
            else:
                publish_permission = "Unknown (Assuming Yes for publish attempt)"
                missing_scopes = []
                suggested_fix = (
                    "Provide LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in your .env "
                    "to introspect precise token scopes. Assuming w_member_social is present."
                )
        else:
            suggested_fix = (
                "The access token is invalid, expired, or rejected. "
                "Verify your token string in the .env file."
            )
            
        return {
            "token_valid": token_valid,
            "member_access": member_access,
            "publish_permission": publish_permission,
            "missing_scopes": missing_scopes,
            "suggested_fix": suggested_fix,
            "member_id": member_id,
            "expiry": expiry,
            "scopes": scopes,
            "debug_logs": debug_logs
        }

    def publish_post(self, access_token: str, post_text: str, member_id: str) -> Dict[str, Any]:
        """
        Publishes a post directly to LinkedIn using the UGC Posts API endpoint.
        Does not fall back to manual copy-paste.
        """
        debug_logs = []
        
        try:
            import streamlit as st
        except ImportError:
            st = None
            
        resolved_member_id = member_id
        if not resolved_member_id or resolved_member_id == "me":
            debug_logs.append("Fetching member URN dynamically via /v2/me...")
            try:
                me_url = "https://api.linkedin.com/v2/me"
                headers_me = {
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
                res_me = requests.get(me_url, headers=headers_me)
                if res_me.status_code == 200:
                    resolved_member_id = res_me.json().get("id")
                    debug_logs.append(f"Successfully retrieved member ID: {resolved_member_id}")
                else:
                    debug_logs.append(f"Failed to fetch dynamic member ID. Status: {res_me.status_code}")
            except Exception as me_err:
                debug_logs.append(f"Exception during /v2/me URN retrieval: {str(me_err)}")
                
        if not resolved_member_id or resolved_member_id == "me":
            resolved_member_id = "me"
            
        ugc_url = "https://api.linkedin.com/v2/ugcPosts"
        headers_ugc = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        payload_ugc = {
            "author": f"urn:li:person:{resolved_member_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        debug_logs.append("--- [HTTP REQUEST: Share Post (Direct UGC)] ---")
        debug_logs.append(f"POST {ugc_url}")
        debug_logs.append(f"Headers: {json.dumps(headers_ugc)}")
        debug_logs.append(f"Body: {json.dumps(payload_ugc)}")
        
        try:
            res = requests.post(ugc_url, json=payload_ugc, headers=headers_ugc)
            debug_logs.append("--- [HTTP RESPONSE: Share Post (Direct UGC)] ---")
            debug_logs.append(f"Status Code: {res.status_code}")
            debug_logs.append(f"Response Body: {res.text}")
            
            try:
                res_data = res.json()
            except Exception:
                res_data = {"raw_response": res.text}
                
            if res.status_code in (200, 201):
                post_id = res_data.get("id")
                post_link = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else ""
                
                if st:
                    if post_link:
                        st.success(f"🚀 Successfully published to LinkedIn! View post: [LinkedIn Post]({post_link})")
                    else:
                        st.success("🚀 Successfully published to LinkedIn!")
                        
                return {
                    "status": "success",
                    "post_id": post_id or "Created",
                    "debug_logs": debug_logs
                }
            else:
                if st:
                    st.error(f"LinkedIn API error (HTTP {res.status_code}):\n\n```json\n{json.dumps(res_data, indent=2)}\n```")
                    
                return {
                    "status": "failed",
                    "reason": f"LinkedIn API Error (HTTP {res.status_code})",
                    "status_code": res.status_code,
                    "error_message": json.dumps(res_data),
                    "suggested_fix": "Verify that scopes, developer settings, and client IDs are correct.",
                    "debug_logs": debug_logs
                }
                
        except Exception as e:
            if st:
                st.error(f"LinkedIn Request failed: {str(e)}")
            return {
                "status": "failed",
                "reason": "Publish Request Exception",
                "status_code": 0,
                "error_message": str(e),
                "suggested_fix": "Check your internet connection or check your access token scope parameters.",
                "debug_logs": debug_logs
            }


class AgentRegistry:
    """
    A registry to manage list of active agents in the pipeline.
    Simplifies adding future agents.
    """
    
    def __init__(self):
        self._agents: List[BaseAgent] = []
        # Register default agents
        self.register(ProjectIntelligenceAgent())
        self.register(TestingAgent())
        self.register(DocumentationAgent())
        self.register(GitHubDeploymentAgent())
        self.register(LinkedInBrandingAgent())

    def register(self, agent: BaseAgent) -> None:
        self._agents.append(agent)

    def get_all_agents(self) -> List[BaseAgent]:
        return self._agents
