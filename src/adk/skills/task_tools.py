"""
Task Tools

Task management utilities.
"""

# In-memory task counter
_task_counter = 0


def generate_task_id() -> str:
    """
    Generate sequential task ID.
    
    Returns:
        Task ID in format "TASK-XXX"
    """
    global _task_counter
    _task_counter += 1
    return f"TASK-{_task_counter:03d}"
