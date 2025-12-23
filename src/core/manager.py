"""
System Manager

System bootstrapper and entry point for A.L.I.V.E.
Initializes A2A bus, instantiates agents, and dispatches tasks.
"""

from pathlib import Path
from typing import Optional

from adk.a2a import A2A
from adk.skills.task_tools import generate_task_id
from agents.librarian import LibrarianAgent


class Manager:
    """
    System entry point and bootstrapper.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize the system manager.
        
        Args:
            workspace_root: Absolute path to ALIVE workspace
        """
        if workspace_root is None:
            # Default to parent directory of src/
            workspace_root = Path(__file__).parent.parent.parent
        
        self.workspace_root = Path(workspace_root)
        
        # Initialize A2A bus (class-level singleton)
        self.a2a = A2A(agent_id="manager")
        
        # Initialize Librarian agent
        self.librarian = LibrarianAgent(str(self.workspace_root))
        
        # System state
        self.running = False
    
    def start(self):
        """
        Start the A.L.I.V.E system.
        """
        # Start A2A bus
        self.a2a.start()
        
        # Start Librarian agent
        self.librarian.start()
        
        self.running = True
    
    def stop(self):
        """
        Stop the A.L.I.V.E system.
        """
        # Stop Librarian agent
        self.librarian.stop()
        
        # Stop A2A bus
        self.a2a.stop()
        
        self.running = False
    
    def submit_task(self, task_description: str) -> str:
        """
        Submit a task to the system.
        
        Args:
            task_description: Human-readable task description
            
        Returns:
            Generated task ID
        """
        if not self.running:
            raise RuntimeError("System is not running. Call start() first.")
        
        # Generate task ID
        task_id = generate_task_id()
        
        # Create NEW_TASK message
        message = {
            "type": "NEW_TASK",
            "task_id": task_id,
            "payload": task_description
        }
        
        # Send to Librarian via A2A
        self.a2a.send(to_agent="librarian", message=message)
        
        return task_id
    
    def get_status(self) -> dict:
        """
        Get system status.
        
        Returns:
            Dictionary containing system state
        """
        return {
            "running": self.running,
            "librarian_status": self.librarian.get_status() if self.running else None
        }


def main():
    """
    Main entry point for standalone execution.
    """
    import sys
    
    # Initialize manager
    manager = Manager()
    
    # Start system
    manager.start()
    
    print("A.L.I.V.E System Started")
    print("=" * 50)
    
    # Interactive mode
    try:
        while True:
            task_input = input("\nEnter task (or 'quit' to exit): ").strip()
            
            if task_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not task_input:
                continue
            
            # Submit task
            task_id = manager.submit_task(task_input)
            print(f"Task submitted: {task_id}")
            
            # Show status
            status = manager.get_status()
            print(f"Active tasks: {status['librarian_status']['active_task_count']}")
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    finally:
        # Stop system
        manager.stop()
        print("A.L.I.V.E System Stopped")


if __name__ == "__main__":
    main()
