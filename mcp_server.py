"""CS 440 Lab 5 — Feature 2: Model Context Protocol (MCP) Server.

Reference: MCP with Claude Lecture (Slides 3, 14, 21, 25, 28)
Exposes the three MCP building blocks to guide the AI agent on the 4x4 Vacuum Q-Learning task:
  1. Tools     (`@mcp.tool`)     — Actions the agent can invoke (`read_context_doc`, `verify_hyperparameters`)
  2. Resources (`@mcp.resource`) — Read-only data exposed like GET handlers (`vacuum://...`)
  3. Prompts   (`@mcp.prompt`)   — Reusable, tested instruction templates (`/audit_hyperparameters`)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

try:
    from mcp.server.fastmcp import FastMCP
    from pydantic import Field
except ImportError:  # Lightweight fallback when `mcp` SDK is not installed in system Python
    def Field(default: Any = ..., **kwargs: Any) -> Any:  # type: ignore[misc]
        return default if default is not ... else None

    class FastMCP:  # type: ignore[no-redef]
        """Minimal decorator-compatible FastMCP fallback for local unit testing."""

        def __init__(self, name: str, log_level: str = "ERROR") -> None:
            self.name = name
            self.log_level = log_level
            self.tools: Dict[str, Callable[..., Any]] = {}
            self.resources: Dict[str, Callable[..., Any]] = {}
            self.prompts: Dict[str, Callable[..., Any]] = {}

        def tool(self, name: str | None = None, description: str = "") -> Callable[..., Any]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                tool_name = name or func.__name__
                self.tools[tool_name] = func
                return func
            return decorator

        def resource(self, uri: str, mime_type: str = "text/plain") -> Callable[..., Any]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                self.resources[uri] = func
                return func
            return decorator

        def prompt(self, name: str | None = None, description: str = "") -> Callable[..., Any]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                prompt_name = name or func.__name__
                self.prompts[prompt_name] = func
                return func
            return decorator

        def run(self) -> None:
            print(f"[{self.name}] MCP server initialized with {len(self.tools)} tools, "
                  f"{len(self.resources)} resources, and {len(self.prompts)} prompts.")

mcp = FastMCP("VacuumRLMCP", log_level="ERROR")

PROJECT_ROOT = Path(__file__).resolve().parent
CONTEXT_DOCS: Dict[str, Path] = {
    "environment.md": PROJECT_ROOT / "context" / "environment.md",
    "q-learning.md": PROJECT_ROOT / "context" / "q-learning.md",
    "exploration.md": PROJECT_ROOT / "context" / "exploration.md",
}


# ==============================================================================
# 1. MCP TOOLS (`@mcp.tool` — Slides 14 & 16)
# ==============================================================================

@mcp.tool(
    name="read_context_doc",
    description="Read the contents of a CS 440 Vacuum RL context document and return it as a string.",
)
def read_context_doc(
    doc_id: str = Field(description="Id of the context document (environment.md, q-learning.md, exploration.md)"),
) -> str:
    """Complete working reference example of `@mcp.tool` (Slide 14)."""
    if doc_id not in CONTEXT_DOCS:
        raise ValueError(f"Doc with id {doc_id} not found. Valid ids: {list(CONTEXT_DOCS)}")
    return CONTEXT_DOCS[doc_id].read_text(encoding="utf-8")


@mcp.tool(
    name="verify_hyperparameters",
    description="Validate the 4 Q-Learning hyperparameters before the agent generates or runs the experiment.",
)
def verify_hyperparameters(
    living_reward: float = Field(default=-0.04, description="Step reward on non-terminal cells"),
    discount_gamma: float = Field(default=0.90, description="Discount factor gamma in (0, 1]"),
    learning_rate_alpha: float = Field(default=0.10, description="TD learning rate alpha in (0, 1]"),
    exploration_epsilon: float = Field(default=0.20, description="Epsilon-greedy exploration rate in [0, 1]"),
) -> str:
    """Validate hyperparameter ranges and return a confirmation string for the agent.

    ===========================================================================
    TODO (Part 5A - MCP Tool Implementation, Slide 14):
    1. Check that `living_reward < 0`, `0 < discount_gamma <= 1`,
       `0 < learning_rate_alpha <= 1`, and `0 <= exploration_epsilon <= 1`
       (raise `ValueError` if invalid, following Slide 14).
    2. Return a summary string confirming the 4 values are valid.
    ===========================================================================
    """
    # TODO (Part 5A): Replace the NotImplementedError below with validation + return string
    raise NotImplementedError(
        "TODO (Part 5A): Implement `verify_hyperparameters` in `mcp_server.py`."
    )


# ==============================================================================
# 2. MCP RESOURCES (`@mcp.resource` — Slides 20–23)
# ==============================================================================

@mcp.resource("vacuum://context", mime_type="application/json")
def list_context_docs() -> list[str]:
    """Direct resource returning the list of available domain context document IDs (Slide 21)."""
    return list(CONTEXT_DOCS.keys())


@mcp.resource("vacuum://hyperparameters", mime_type="application/json")
def get_hyperparameters_resource() -> Dict[str, float]:
    """Direct resource exposing the selected Lab 5 hyperparameters as JSON (Slide 21).

    ===========================================================================
    TODO (Part 5B - MCP Resource Implementation, Slide 21):
    Return a dictionary with your 4 chosen hyperparameters:
      {
          "living_reward": -0.04,
          "discount_gamma": 0.90,
          "learning_rate_alpha": 0.10,
          "exploration_epsilon": 0.20,
      }
    ===========================================================================
    """
    # TODO (Part 5B): Replace the NotImplementedError below with the dictionary return
    raise NotImplementedError(
        "TODO (Part 5B): Implement `get_hyperparameters_resource` in `mcp_server.py`."
    )


# ==============================================================================
# 3. MCP PROMPTS (`@mcp.prompt` — Slides 24–28)
# ==============================================================================

@mcp.prompt(
    name="audit_hyperparameters",
    description="Ready-made expert prompt instructing the agent to solve and audit the 4x4 Vacuum Q-Learning problem.",
)
def audit_hyperparameters_prompt(
    living_reward: str = Field(default="-0.04", description="Selected living reward value"),
) -> str:
    """Reusable prompt template triggered via `/audit_hyperparameters` (Slide 25).

    ===========================================================================
    TODO (Part 5C - MCP Prompt Implementation, Slide 25):
    Return a prompt string instructing the agent to:
    1. Call `verify_hyperparameters` with `living_reward`.
    2. Generate and run the 4x4 Vacuum Q-Learning solution in `src/` and verify
       the policy avoids Obstacle `X` at `(1, 1)` and Trap `-1` at `(3, 1)` to
       reach the Recharge Goal `+10` at `(3, 3)`.
    ===========================================================================
    """
    # TODO (Part 5C): Replace the NotImplementedError below with your prompt string
    raise NotImplementedError(
        "TODO (Part 5C): Implement `audit_hyperparameters_prompt` in `mcp_server.py`."
    )


if __name__ == "__main__":
    mcp.run()
