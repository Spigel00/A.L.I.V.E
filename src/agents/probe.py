"""
Probe Agent: System Validation Agent

A minimal agent that exists solely to validate the A.L.I.V.E framework.
Receives tasks, writes static spec files, and emits completion signals.

This agent does NOT:
- Perform reasoning
- Read the roster
- Call other agents
- Modify system files
"""

from pathlib import Path
from typing import Optional

from adk.agent import Agent
from adk.a2a import A2A
from adk.skills.file_tools import write_file
from adk.skills.a2a_tools import emit_task_complete


class ProbeAgent(Agent):
    """
    Validation agent that proves A2A routing and file-based state work.
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize the Probe agent.
        
        Args:
            workspace_root: Absolute path to the ALIVE workspace
        """
        self.workspace_root = Path(workspace_root)
        self.logs_path = self.workspace_root / "logs"
        
        # Initialize base agent
        super().__init__(
            agent_id="probe",
            system_instruction="You are a validation probe. Write specs and signal completion."
        )
        
        # Initialize A2A protocol
        self.a2a = A2A(agent_id=self.agent_id)
        
        # Register A2A listener
        self._register_listeners()
    
    def _register_listeners(self):
        """Register A2A message listeners."""
        self.a2a.on("DELEGATED_TASK", self._handle_delegated_task)
    
    def _handle_delegated_task(self, message: dict):
        """
        Handle incoming DELEGATED_TASK messages.
        
        Args:
            message: A2A message with format:
                {
                    "type": "DELEGATED_TASK",
                    "task_id": "TASK-XXX",
                    "payload": str
                }
        """
        task_id = message.get("task_id")
        
        if not task_id:
            return
        
        # Write static spec file
        self._write_spec(task_id)
        
        # Emit task complete signal
        emit_task_complete(self.a2a, self.agent_id, task_id)
    
    def _write_spec(self, task_id: str):
        """
        Write static validation spec file.
        
        Args:
            task_id: Task identifier
        """
        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Static spec content
        spec_content = """# Probe Agent Report

The ALIVE framework routed this task correctly.
A2A signaling works.
File-based state works.
"""
        
        # Write spec file
        spec_filename = f"{self.agent_id}_{task_id}_spec.md"
        spec_path = self.logs_path / spec_filename
        
        write_file(str(spec_path), spec_content)
    
    def start(self):
        """
        Start the Probe agent.
        
        Begins listening for A2A messages.
        """
        self.a2a.start()
    
    def stop(self):
        """
        Stop the Probe agent.
        
        Stops listening for A2A messages.
        """
        self.a2a.stop()
