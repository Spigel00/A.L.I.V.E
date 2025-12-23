"""
Skill Base Class

Base class for agent skills (tools).
Placeholder for future permission and audit layers.
"""

from typing import Any, Callable


class Skill:
    """
    Base class for agent skills.
    """
    
    def __init__(self, name: str, func: Callable):
        """
        Initialize a skill.
        
        Args:
            name: Skill identifier
            func: Callable function implementing the skill
        """
        self.name = name
        self.func = func
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the skill.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of skill execution
        """
        return self.func(*args, **kwargs)
