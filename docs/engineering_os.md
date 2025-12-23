<!-- Engineering OS: Execution Layer -->
# Engineering Agent OS Handbook by Ganesh Karupoor Swaminaathan

This document serves as the "Source of Truth" for our team to build, deploy, and manage the agentic workforce using the ADK (Agent Development Kit) + A2A (Agent-to-Agent) architecture.

## The Engineering Agent OS

**Architecture:** ADK (Kernel) + A2A (Network) + File-Based State (Memory)

## 1. Introduction: Why This Approach?

We are moving away from "Monolithic AI" (one bot doing everything) to a Decentralized Agent Network.

### The Problem

Large Language Model agents are like junior engineers—if you give them a 50-step task, they hallucinate or get stuck.

### The Solution (ADK + A2A)

We atomize workflows. One agent drafts the plan, another critiques it, and a third executes it. They communicate via a standard protocol (A2A), not chat.

### The Memory (File-Based State)

We use the Kiro/Cursor Standard. Agents do not keep secrets; they write to `product.md`, `tech.md`, and `active_spec.md`. This is the baton they pass.

## 2. Identity & Behavior

Identity is the "Soul" of the agent. It is defined in the ADK `system_instruction`. It tells the model who it is, which dictates how it solves problems.

### The Behavior Library (Top 10 Archetypes)

Select one of these behaviors when initializing an agent.

| Behavior | Role | System Prompt Keyword |
|----------|------|----------------------|
| **The Architect** | High-level decision making. | "Prioritize scalability, cost-efficiency, and open-source." |
| **The Scaffolder** | File/Folder structure setup. | "Focus on standard conventions, strict directory trees." |
| **The Skeptic** | QA & Security review. | "Assume code is insecure. Look for edge cases and leaks." |
| **The Scribe** | Documentation & Specs. | "Translation of abstract ideas into rigid Markdown specs." |
| **The Minimalist** | Refactoring & Cleanup. | "Reduce code complexity. DRY (Don't Repeat Yourself)." |
| **The Runner** | Execution & Deployment. | "Focus on shell commands, Docker, and build pipelines." |
| **The Researcher** | Tech Stack Selection. | "Find verified benchmarks. Ignore marketing hype." |
| **The Translator** | Bridge between Product/Eng. | "Convert business requirements into technical tickets." |
| **The Watchdog** | Performance monitoring. | "Focus on latency, token usage, and memory leaks." |
| **The Diplomat** | API & Contract negotiation. | "Ensure schema compatibility between services." |

## 3. Skills (The Tool Belt)

Skills are executable Python functions registered in ADK. Without skills, an agent is just a chatbot.

### Core Engineering Skills (Top 8)

- **file_manager**: Read/Write access to `docs/` and `src/`. Crucial for maintaining state.
- **git_ops**: `git clone`, `git commit`, `git push`.
- **web_search**: Live access to documentation (e.g., "Latest FastApi docs").
- **shell_exec**: Safe execution of terminal commands (`npm install`, `docker build`).
- **syntax_check**: Running linters (eslint, ruff) to validate code before saving.
- **rag_query**: Searching internal knowledge bases ("How do we handle auth?").
- **image_vision**: Analyzing UI screenshots or diagram inputs.
- **a2a_broadcast**: Signaling the next agent in the chain ("Task A complete, starting Task B").

## 4. Instructions (The Brain)

Instructions bridge the Identity and the Skills. They must follow a strict input-process-output flow.

### The Golden Rule: The "State" Flow

Every instruction should reference the File-Based State.

> "Read `docs/product.md` (Input) -> Think -> Write `docs/tech.md` (Output)."

### Example Instruction Set (The Planner Agent)

```plaintext
CONTEXT: You are the Lead Planner.
INPUT: Read 'docs/tech.md' for architectural decisions.
GOAL: Create a step-by-step implementation plan for the Developer Agent.
RULES:
1. Break tasks into atomic file operations.
2. Verify that every library listed in tech.md is included in requirements.txt.
OUTPUT: Overwrite 'active_spec.md'. Do not output code, only the plan.
```

## 5. Building Best Practices

When using ADK to build your agents, follow the "Manager's Mindset."

### Defining the Role

- **Don't ask:** "What do I want the AI to do?"
- **Ask:** "If I hired a human intern for this specific 10-minute task, what instructions would I give them?"

### Good vs. Bad Pattern

| Feature | ❌ Bad Practice (Vague) | ✅ Good Practice (Atomic & Explicit) |
|---------|------------------------|-------------------------------------|
| **Scope** | "Build a PII scanning app." | "Create a FastAPI boilerplate with one endpoint `/scan` based on tech.md." |
| **Context** | "Use best practices." | "Follow the folder structure defined in `docs/architecture_guidelines.md`." |
| **Handoff** | (No Output defined) | "Update `active_spec.md` with status [x] and trigger the QA_Agent." |
| **Error Handling** | "Try again if it fails." | "If `npm install` fails, read the error log, search the error, and retry once. If it fails twice, stop and alert." |

