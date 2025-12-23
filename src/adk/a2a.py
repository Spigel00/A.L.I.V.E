"""
A2A (Agent-to-Agent) Protocol

Event-based communication protocol for agent coordination.
No persistence, no chat, synchronous dispatch.
"""

from typing import Callable, Dict, List


class A2A:
    """
    In-process event bus for agent-to-agent communication.
    """
    
    # Class-level registry for cross-agent communication
    _global_handlers: Dict[str, List[tuple]] = {}
    _instances: Dict[str, 'A2A'] = {}
    
    def __init__(self, agent_id: str):
        """
        Initialize A2A instance for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        """
        self.agent_id = agent_id
        self.handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        # Register this instance globally
        A2A._instances[agent_id] = self
    
    def on(self, event_type: str, handler: Callable):
        """
        Register an event handler for a specific message type.
        
        Args:
            event_type: Type of event to listen for (e.g., "NEW_TASK")
            handler: Callable to invoke when event is received
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        
        # Register globally with agent_id
        key = f"{self.agent_id}:{event_type}"
        if key not in A2A._global_handlers:
            A2A._global_handlers[key] = []
        
        A2A._global_handlers[key].append((self.agent_id, handler))
    
    def send(self, to_agent: str, message: dict):
        """
        Send a message to another agent.
        
        Args:
            to_agent: Target agent ID
            message: Message dictionary with 'type' field required
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
        
        if "type" not in message:
            raise ValueError("Message must contain 'type' field")
        
        event_type = message["type"]
        
        # Look up target agent instance
        target_instance = A2A._instances.get(to_agent)
        
        if target_instance and target_instance.running:
            # Dispatch to target agent's handlers
            handlers = target_instance.handlers.get(event_type, [])
            for handler in handlers:
                handler(message)
        
        # Also check global handlers
        key = f"{to_agent}:{event_type}"
        global_handlers = A2A._global_handlers.get(key, [])
        for agent_id, handler in global_handlers:
            if agent_id == to_agent:
                handler(message)
    
    def start(self):
        """
        Start listening for messages.
        """
        self.running = True
    
    def stop(self):
        """
        Stop listening for messages.
        """
        self.running = False
