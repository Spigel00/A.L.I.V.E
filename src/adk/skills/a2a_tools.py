"""
A2A Tools

Helper utilities for A2A communication.
"""

from adk.a2a import A2A


def emit_task_complete(a2a: A2A, agent_id: str, task_id: str):
    """
    Emit a TASK_COMPLETE message.
    
    Args:
        a2a: A2A instance
        agent_id: ID of agent completing the task
        task_id: ID of completed task
    """
    message = {
        "type": "TASK_COMPLETE",
        "agent_id": agent_id,
        "task_id": task_id
    }
    
    # Send to librarian by default
    a2a.send(to_agent="librarian", message=message)
