"""
Instruction Schema

Lightweight instruction structure for reasoning agents.
"""

from typing import List, Optional


class Instruction:
    """
    Structured instruction for agent tasks.
    """
    
    def __init__(
        self,
        context: str = "",
        goal: str = "",
        rules: Optional[List[str]] = None
    ):
        """
        Initialize an instruction.
        
        Args:
            context: Background information and current state
            goal: What needs to be accomplished
            rules: List of constraints and requirements
        """
        self.context = context
        self.goal = goal
        self.rules = rules or []
    
    def to_dict(self) -> dict:
        """
        Convert instruction to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "context": self.context,
            "goal": self.goal,
            "rules": self.rules
        }
    
    def to_text(self) -> str:
        """
        Convert instruction to text format.
        
        Returns:
            Text representation
        """
        parts = []
        
        if self.context:
            parts.append(f"Context:\n{self.context}")
        
        if self.goal:
            parts.append(f"Goal:\n{self.goal}")
        
        if self.rules:
            parts.append("Rules:")
            for rule in self.rules:
                parts.append(f"- {rule}")
        
        return "\n\n".join(parts)
