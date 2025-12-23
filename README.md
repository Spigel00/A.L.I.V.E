# A.L.I.V.E — Agent-Based Operating System

An agent-based operating system built with **ADK (Agent Development Kit)** and **A2A (Agent-to-Agent)** protocol.

## 🏗️ Architecture

```
ALIVE/
├── docs/
│   ├── engineering_os.md      # System rules and behaviors
│   └── agent_roster.md        # Agent identity and capabilities
├── logs/
│   └── active_spec.md         # Consolidated specifications
├── src/
│   ├── adk/                   # Agent Development Kit (runtime)
│   │   ├── a2a.py            # Event-based communication protocol
│   │   ├── agent.py          # Base agent class
│   │   ├── instruction.py    # Instruction schema
│   │   ├── skill.py          # Skill base class
│   │   └── skills/           # Agent tools
│   ├── agents/               # Agent implementations
│   │   ├── librarian.py     # Coordination agent
│   │   └── probe.py         # Validation agent
│   └── core/
│       └── manager.py        # System bootstrapper
```

## 🧠 Core Principles

- **Single OS Model**: All agents follow `engineering_os.md` rules
- **File-Based State**: Files are the single source of truth
- **Event-Based Communication**: A2A protocol for agent coordination
- **Declarative Roster**: Agent identity defined in Markdown, not code
- **No Shared Memory**: Agents communicate only via A2A and files

## 🚀 Quick Start

### 1. Run Interactive Mode

```bash
cd ALIVE
python3 -m src.core.manager
```

### 2. Programmatic Usage

```python
import sys
sys.path.insert(0, 'src')

from core.manager import Manager
from agents.probe import ProbeAgent

# Initialize system
manager = Manager()
probe = ProbeAgent(str(manager.workspace_root))

# Start agents
manager.start()
probe.start()

# Submit task
task_id = manager.submit_task("probe validation test")

# Check status
print(manager.get_status())

# Stop system
probe.stop()
manager.stop()
```

## 📋 System Flow

```
Human Input
  ↓
Manager (generates TASK-XXX)
  ↓ A2A: NEW_TASK
Librarian (routes based on capabilities)
  ↓ A2A: DELEGATED_TASK
Agent (executes task)
  ↓ writes: logs/{agent_id}_{task_id}_spec.md
  ↓ A2A: TASK_COMPLETE
Librarian (consolidates)
  ↓ appends to: logs/active_spec.md
  ↓ verifies & deletes temp spec
```

## 🎯 Current Agents

### Librarian
- **Role**: Coordination & state consolidation
- **Capabilities**: task_routing, spec_consolidation
- **Behavior**: Routes tasks, collects specs, maintains active_spec.md

### Probe
- **Role**: System validation
- **Capabilities**: probe
- **Behavior**: Validates A2A routing and file-based state

## 🔧 Adding New Agents

1. **Define in roster** (`docs/agent_roster.md`):
```yaml
## your_agent
capabilities:
  - your_capability
```

2. **Create agent file** (`src/agents/your_agent.py`):
```python
from adk.agent import Agent
from adk.a2a import A2A

class YourAgent(Agent):
    def __init__(self, workspace_root: str):
        super().__init__(agent_id="your_agent", system_instruction="...")
        self.a2a = A2A(agent_id=self.agent_id)
        self.a2a.on("DELEGATED_TASK", self._handle_task)
    
    def _handle_task(self, message: dict):
        # Your logic here
        pass
```

3. **Start the agent** in your manager setup

## 📝 A2A Message Types

### NEW_TASK
```json
{
  "type": "NEW_TASK",
  "task_id": "TASK-XXX",
  "payload": "task description"
}
```

### DELEGATED_TASK
```json
{
  "type": "DELEGATED_TASK",
  "task_id": "TASK-XXX",
  "payload": "task description"
}
```

### TASK_COMPLETE
```json
{
  "type": "TASK_COMPLETE",
  "agent_id": "agent_name",
  "task_id": "TASK-XXX"
}
```

## 🧪 Validation

Run the validation test:

```bash
cd ALIVE
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from core.manager import Manager
from agents.probe import ProbeAgent

manager = Manager()
probe = ProbeAgent(str(manager.workspace_root))
manager.start()
probe.start()

task_id = manager.submit_task("probe test")
print(f"Task {task_id} submitted")

probe.stop()
manager.stop()
EOF
```

## 🔍 Key Files

- **`docs/agent_roster.md`**: Agent definitions (data, not code)
- **`docs/engineering_os.md`**: System behavior and agent archetypes
- **`logs/active_spec.md`**: Consolidated task specifications
- **`src/core/manager.py`**: System entry point
- **`src/adk/a2a.py`**: Event bus implementation

## 📖 Design Philosophy

**Files are Memory. Code is Behavior.**

- Agents don't store state in memory
- All state transitions are file-based
- Communication is purely event-driven
- System can restart without state loss
- Deterministic, auditable execution flow

## 🛠️ Development

No external dependencies required. Pure Python 3.

```bash
# Verify imports
python3 -c "import sys; sys.path.insert(0, 'src'); from core.manager import Manager; print('✓ System ready')"
```

## 📄 License

MIT License - Built by Ganesh Karupoor Swaminaathan

---

**Status**: Phase 1 Complete — System validation successful
