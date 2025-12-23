"""
Agent Base Class

Minimal base class for all agents in the system.
Does not call LLMs, store memory, or execute tools.
"""


class Agent:
    """
    Base class for all agents.
    """
    
    def __init__(self, agent_id: str, system_instruction: str = ""):
        """
        Initialize an agent.
        
        Args:
            agent_id: Unique identifier for this agent
            system_instruction: System-level instruction defining agent behavior
        """
        self.agent_id = agent_id
        self.system_instruction = system_instruction
    
    def start(self):
        """
        Start the agent. Override in subclasses.
        """
        pass
    
    def stop(self):
        """
        Stop the agent. Override in subclasses.
        """
        pass
