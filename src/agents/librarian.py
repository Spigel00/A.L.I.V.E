"""
Librarian Agent: Coordination & State Consolidation

The Librarian is a coordination agent responsible for:
- Receiving tasks via A2A
- Routing tasks to appropriate agents based on capabilities
- Collecting completed task specs
- Consolidating specs into active_spec.md
- Managing task state tracking

This agent does NOT:
- Generate specs
- Execute domain reasoning
- Modify source code

It ONLY routes, collects, and consolidates.

ARCHITECTURE NOTE:
- Reads docs/agent_roster.md directly (data, not code)
- No Python roster abstraction used
- Pure file-based state management
"""

import os
from typing import Dict, List, Optional
from pathlib import Path

from adk.agent import Agent
from adk.a2a import A2A
from adk.skills.file_tools import read_file, write_file, delete_file
from adk.skills.task_tools import generate_task_id


class LibrarianAgent(Agent):
    """
    Coordination agent that routes tasks and consolidates specs.
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize the Librarian agent.
        
        Args:
            workspace_root: Absolute path to the ALIVE workspace
        """
        # Load OS and Roster to determine identity
        self.workspace_root = Path(workspace_root)
        self.os_path = self.workspace_root / "docs" / "engineering_os.md"
        self.roster_path = self.workspace_root / "docs" / "agent_roster.md"
        self.logs_path = self.workspace_root / "logs"
        self.active_spec_path = self.logs_path / "active_spec.md"
        
        # Load configuration files
        self.os_content = self._load_os()
        self.roster = self._load_roster()
        
        # Resolve own identity from roster
        self.identity = self._resolve_identity()
        
        # Initialize base agent with system instruction
        system_instruction = self._build_system_instruction()
        super().__init__(
            agent_id="librarian",
            system_instruction=system_instruction
        )
        
        # Task tracking (in-memory, non-persistent)
        self.active_tasks: Dict[str, dict] = {}  # task_id -> task_info
        self.completion_queue: List[dict] = []  # completed tasks awaiting consolidation
        
        # Initialize A2A protocol
        self.a2a = A2A(agent_id=self.agent_id)
        
        # Register A2A message listeners
        self._register_listeners()
        
    def _load_os(self) -> str:
        """Load the engineering OS document."""
        if not self.os_path.exists():
            return ""
        return read_file(str(self.os_path))
    
    def _load_roster(self) -> dict:
        """
        Load and parse the agent roster from Markdown/YAML format.
        
        Expected format:
        ## agent_id
        capabilities:
          - capability1
          - capability2
        
        Returns:
            Dictionary mapping agent_id to agent metadata
        """
        if not self.roster_path.exists():
            return {}
        
        roster_content = read_file(str(self.roster_path))
        agents = {}
        
        # Parse YAML-like format in Markdown
        lines = roster_content.split('\n')
        current_agent = None
        current_section = None
        
        for line in lines:
            stripped = line.strip()
            
            # Agent header: ## agent_id
            if stripped.startswith('##') and not stripped.startswith('###'):
                current_agent = stripped[2:].strip()
                if current_agent:
                    agents[current_agent] = {
                        'agent_id': current_agent,
                        'capabilities': [],
                        'permissions': []
                    }
                continue
            
            # Section header: capabilities: or permissions:
            if current_agent and ':' in stripped and not stripped.startswith('-'):
                if 'capabilities' in stripped.lower():
                    current_section = 'capabilities'
                elif 'permissions' in stripped.lower():
                    current_section = 'permissions'
                continue
            
            # List item: - item
            if current_agent and current_section and stripped.startswith('-'):
                item = stripped[1:].strip()
                if item:
                    agents[current_agent][current_section].append(item)
        
        return agents
    
    def _resolve_identity(self) -> dict:
        """
        Resolve the Librarian's identity from the roster.
        
        Returns:
            Dictionary containing identity metadata
        """
        if 'librarian' in self.roster:
            return self.roster['librarian']
        
        # Default identity if not found in roster
        return {
            'capabilities': ['task_routing', 'spec_consolidation', 'coordination'],
            'role': 'coordinator'
        }
    
    def _build_system_instruction(self) -> str:
        """
        Build the system instruction for the Librarian agent.
        
        Returns:
            System instruction string
        """
        return """You are the Librarian agent.

Your role is COORDINATION and STATE CONSOLIDATION, not reasoning.

Your responsibilities:
1. Receive tasks via A2A protocol
2. Route tasks to appropriate agents based on capabilities
3. Track task completion
4. Collect and consolidate spec files
5. Maintain active_spec.md as single source of truth

You do NOT:
- Generate specs yourself
- Execute domain reasoning
- Modify source code

You ONLY route, collect, and consolidate.

Follow the Engineering OS rules strictly.
All state is file-based.
Communication is event-based via A2A protocol only.
"""
    
    def _register_listeners(self):
        """Register A2A message listeners."""
        self.a2a.on("NEW_TASK", self._handle_new_task)
        self.a2a.on("TASK_COMPLETE", self._handle_task_complete)
    
    def _handle_new_task(self, message: dict):
        """
        Handle incoming NEW_TASK messages.
        
        Args:
            message: A2A message with format:
                {
                    "type": "NEW_TASK",
                    "task_id": "TASK-XXX",
                    "payload": str
                }
        """
        task_id = message.get("task_id")
        payload = message.get("payload", "")
        
        if not task_id:
            task_id = generate_task_id()
        
        # Store task in active tracking
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "payload": payload,
            "status": "routing",
            "assigned_agent": None
        }
        
        # Route task to appropriate agent
        target_agent = self._route_task(payload)
        
        # Update task tracking
        self.active_tasks[task_id]["assigned_agent"] = target_agent
        self.active_tasks[task_id]["status"] = "delegated"
        
        # Send delegated task via A2A
        self.a2a.send(
            to_agent=target_agent,
            message={
                "type": "DELEGATED_TASK",
                "task_id": task_id,
                "payload": payload
            }
        )
    
    def _route_task(self, payload: str) -> str:
        """
        Route task to the appropriate agent based on capability matching.
        
        Args:
            payload: Task description/payload
            
        Returns:
            Agent ID to delegate to
        """
        payload_lower = payload.lower()
        
        # Match against agent capabilities in roster
        for agent_id, agent_info in self.roster.items():
            if agent_id == "librarian":
                continue  # Skip self
            
            capabilities = agent_info.get('capabilities', [])
            for capability in capabilities:
                if capability.strip().lower() in payload_lower:
                    return agent_id
        
        # Fallback: return librarian (self) if no match
        return "librarian"
    
    def _handle_task_complete(self, message: dict):
        """
        Handle TASK_COMPLETE messages.
        
        Args:
            message: A2A message with format:
                {
                    "type": "TASK_COMPLETE",
                    "agent_id": str,
                    "task_id": "TASK-XXX"
                }
        """
        agent_id = message.get("agent_id")
        task_id = message.get("task_id")
        
        if not agent_id or not task_id:
            return
        
        # Check if task exists and is not already completed (duplicate protection)
        if task_id in self.active_tasks:
            if self.active_tasks[task_id].get("status") == "completed":
                # Duplicate TASK_COMPLETE - ignore
                return
            self.active_tasks[task_id]["status"] = "completed"
        else:
            # Unknown task - may be from restart, proceed with spec collection anyway
            pass
        
        # Add to completion queue for spec collection
        self.completion_queue.append({
            "agent_id": agent_id,
            "task_id": task_id
        })
        
        # Process spec collection
        self._collect_and_consolidate_spec(agent_id, task_id)
    
    def _collect_and_consolidate_spec(self, agent_id: str, task_id: str):
        """
        Collect spec from completed task and consolidate into active_spec.md.
        
        STRICT ORDER:
        1. Read {agent_id}_{task_id}_spec.md
        2. Append to active_spec.md
        3. Verify content exists in active_spec.md
        4. Delete temporary spec file
        5. Update task state
        
        Args:
            agent_id: ID of the agent that completed the task
            task_id: ID of the completed task
        """
        # Step 1: Read temporary spec file
        spec_filename = f"{agent_id}_{task_id}_spec.md"
        spec_path = self.logs_path / spec_filename
        
        if not spec_path.exists():
            # No spec file found - task may not have generated one
            self._cleanup_task(task_id)
            return
        
        try:
            spec_content = read_file(str(spec_path))
        except Exception:
            # File read error - skip this spec
            self._cleanup_task(task_id)
            return
        
        if not spec_content.strip():
            # Empty spec file - nothing to consolidate
            try:
                delete_file(str(spec_path))
            except Exception:
                pass  # Deletion failure is non-critical
            self._cleanup_task(task_id)
            return
        
        # Step 2: Append to active_spec.md
        try:
            self._append_to_active_spec(spec_content, agent_id, task_id)
        except Exception:
            # Append failure - do not delete spec file, allow retry
            return
        
        # Step 3: Verify content exists in active_spec.md
        verification_success = self._verify_consolidation(spec_content)
        
        # Step 4: Delete temporary spec file only if verification succeeds
        if verification_success:
            try:
                delete_file(str(spec_path))
            except Exception:
                pass  # Deletion failure is non-critical if content is consolidated
        
        # Step 5: Update task state
        self._cleanup_task(task_id)
    
    def _append_to_active_spec(self, content: str, agent_id: str, task_id: str):
        """
        Append spec content to active_spec.md.
        
        Args:
            content: Spec content to append
            agent_id: Agent that generated the spec
            task_id: Task ID
        """
        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Read existing content or create new file
        if self.active_spec_path.exists():
            existing_content = read_file(str(self.active_spec_path))
        else:
            existing_content = "# Active Specification\n\n"
        
        # Append new content with metadata header
        separator = f"\n\n---\n## Task: {task_id} (by {agent_id})\n\n"
        updated_content = existing_content + separator + content + "\n"
        
        # Write back to file
        write_file(str(self.active_spec_path), updated_content)
    
    def _verify_consolidation(self, content: str) -> bool:
        """
        Verify that content was successfully appended to active_spec.md.
        
        Args:
            content: Content that should exist in active_spec.md
            
        Returns:
            True if verification succeeds, False otherwise
        """
        if not self.active_spec_path.exists():
            return False
        
        active_spec_content = read_file(str(self.active_spec_path))
        
        # Check if content exists in active spec
        return content.strip() in active_spec_content
    
    def _cleanup_task(self, task_id: str):
        """
        Clean up task from active tracking.
        
        Args:
            task_id: Task ID to clean up
        """
        if task_id in self.active_tasks:
            # Move to completed or archive if needed
            del self.active_tasks[task_id]
        
        # Remove from completion queue
        self.completion_queue = [
            item for item in self.completion_queue 
            if item.get("task_id") != task_id
        ]
    
    def start(self):
        """
        Start the Librarian agent.
        
        Begins listening for A2A messages.
        """
        self.a2a.start()
    
    def stop(self):
        """
        Stop the Librarian agent.
        
        Stops listening for A2A messages and performs cleanup.
        """
        self.a2a.stop()
    
    def get_status(self) -> dict:
        """
        Get current status of the Librarian agent.
        
        Returns:
            Dictionary containing:
            - active_task_count
            - completion_queue_length
            - active_tasks (list of task_ids)
        """
        return {
            "active_task_count": len(self.active_tasks),
            "completion_queue_length": len(self.completion_queue),
            "active_tasks": list(self.active_tasks.keys())
        }
