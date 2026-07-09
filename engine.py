"""
Engine module for ProjectPilot AI.
Implements the sequential orchestration engine that executes registered agents
and yields real-time execution steps, logs, and aggregated output.
"""

import time
from typing import Dict, Any, Generator
from agents import AgentRegistry, BaseAgent

class OrchestrationEngine:
    """
    Manages the sequential execution of agents in the ProjectPilot AI pipeline.
    Communicates execution state back to the caller in real-time using a generator.
    """

    def __init__(self, registry: AgentRegistry):
        """
        Initializes the orchestration engine with a given agent registry.
        
        Args:
            registry (AgentRegistry): The registry containing agents to execute.
        """
        self.registry = registry

    def run_pipeline(self, project_path: str, gemini_api_key: str = None) -> Generator[Dict[str, Any], None, None]:
        """
        Executes all registered agents sequentially and yields progress updates.
        
        Args:
            project_path (str): The absolute path to the project directory to analyze.
            gemini_api_key (str): Optional API Key passed dynamically from the UI.
            
        Yields:
            Dict[str, Any]: A dictionary representing the current execution event and payload.
        """
        agents = self.registry.get_all_agents()
        if not agents:
            yield {
                "event": "error",
                "message": "No agents registered in the pipeline."
            }
            return

        yield {
            "event": "pipeline_start",
            "total_agents": len(agents)
        }

        # Shared execution context across all agents
        context: Dict[str, Any] = {
            "gemini_api_key": gemini_api_key
        }

        for index, agent in enumerate(agents):
            yield {
                "event": "agent_start",
                "agent_name": agent.name,
                "agent_index": index,
                "agent_icon": agent.icon,
                "agent_color": agent.color
            }

            try:
                # Execute agent with context (contains API key)
                agent_result = agent.run(project_path, context)
                
                # Check for explicit failure returned by the agent
                if agent_result.get("status") == "failed":
                    error_msg = agent_result.get("error", "Unknown error occurred.")
                    raise ValueError(error_msg)
                
                # Stream logs one by one for modern terminal-like output feel
                for log in agent_result.get("logs", []):
                    time.sleep(0.2) # Subtle delay for realistic visual transition
                    yield {
                        "event": "agent_log",
                        "agent_name": agent.name,
                        "log": log
                    }

                # Store result in cumulative context
                context[agent.name] = {
                    "summary": agent_result.get("summary", ""),
                    "artifacts": agent_result.get("artifacts", {}),
                    "status": agent_result.get("status", "success")
                }
                
                # IMPORTANT: Propagate any internal structured data returned by agents 
                # (e.g., project_analysis from Agent 1) directly into the shared context
                for key, value in agent_result.items():
                    if key not in ["status", "summary", "logs", "artifacts"]:
                        context[key] = value

                yield {
                    "event": "agent_success",
                    "agent_name": agent.name,
                    "result": context[agent.name]
                }

            except Exception as e:
                # Capture and stream any agent failures gracefully
                error_msg = f"Error in agent {agent.name}: {str(e)}"
                yield {
                    "event": "agent_failed",
                    "agent_name": agent.name,
                    "error": error_msg
                }
                # For critical Agent 1 failure, we can choose to propagate the exception
                # to prevent running further agents with incomplete intelligence data
                context[agent.name] = {
                    "summary": f"Execution failed: {str(e)}",
                    "artifacts": {},
                    "status": "failed"
                }
                # Propagate failure to halt pipeline
                raise e

        yield {
            "event": "pipeline_done",
            "results": context
        }
