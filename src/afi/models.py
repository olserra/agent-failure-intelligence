"""Agent models under test.

The PoC ships two *scripted* models. They are deterministic stand-ins that
let us validate the harness end to end at zero cost:

- NaiveScriptedModel: treats instruction-looking lines found inside tool
  output as if they came from the operator, and queues them for execution.
  This is the vulnerable baseline.
- HardenedScriptedModel: only follows the original user task and ignores any
  instruction embedded in tool output.

Real-LLM adapters plug into the same Model interface later. Results produced
with scripted models validate the harness; they say nothing about any real
model, and reports label them accordingly.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .tools import ToolCall

# Directives use an explicit grammar - `>> <verb> <args>` - so ordinary prose
# in tasks or documents can never be mistaken for a command.
DIRECTIVE_RE = re.compile(r"^\s*>>\s*(read|write|fetch|send)\s+(.*?)\s*$", re.IGNORECASE)


@dataclass
class ModelReply:
    tool_call: ToolCall | None = None
    final: str | None = None
    rationale: str = ""


def parse_directive(line: str) -> ToolCall | None:
    """Parse the small command grammar used by scripted models and payloads."""
    m = DIRECTIVE_RE.match(line)
    if not m:
        return None
    verb, rest = m.group(1).lower(), m.group(2)
    if verb == "read":
        return ToolCall("fs.read", {"path": rest})
    if verb == "fetch":
        return ToolCall("http.fetch", {"url": rest})
    if verb == "write":
        path, _, content = rest.partition(" ")
        return ToolCall("fs.write", {"path": path, "content": content})
    if verb == "send":
        to, _, text = rest.partition(" ")
        return ToolCall("message.send", {"to": to, "text": text})
    return None


def directives_in(text: str) -> list[ToolCall]:
    return [c for c in (parse_directive(l) for l in text.splitlines()) if c]


class Model:
    name = "base"
    role = "subject"

    def reset(self) -> None:
        """Clear per-scenario state. The runner calls this before each run."""

    def decide(self, task: str, policy_text: str, last_tool_output: str | None, step: int) -> ModelReply:
        raise NotImplementedError


class NaiveScriptedModel(Model):
    """Vulnerable baseline: queues every directive it finds, wherever it
    appears - the user task or inside tool output - and executes them in
    order. Tool output is treated as a continuation of the operator's
    instructions, which is exactly the failure mode under test."""
    name = "naive-scripted"
    role = "vulnerable-baseline"

    def reset(self) -> None:
        self._queue: list[ToolCall] = []
        self._primed = False

    def decide(self, task: str, policy_text: str, last_tool_output: str | None, step: int) -> ModelReply:
        if not hasattr(self, "_queue"):
            self.reset()
        if not self._primed:
            self._queue.extend(directives_in(task))
            self._primed = True
        if last_tool_output is not None:
            self._queue.extend(directives_in(last_tool_output))
        if self._queue:
            call = self._queue.pop(0)
            origin = "tool output" if last_tool_output is not None and call in directives_in(last_tool_output) else "queued instructions"
            return ModelReply(tool_call=call, rationale=f"following directive from {origin}")
        return ModelReply(final="Done.", rationale="no further directives")


class HardenedScriptedModel(Model):
    """Hardened variant: only the original user task may direct tool use.
    Tool output is data; any directive-looking line inside it is ignored."""
    name = "hardened-scripted"
    role = "hardened"

    def reset(self) -> None:
        self._task_done = False

    def decide(self, task: str, policy_text: str, last_tool_output: str | None, step: int) -> ModelReply:
        if not hasattr(self, "_task_done"):
            self.reset()
        if self._task_done:
            return ModelReply(final="Done.", rationale="tool output treated as data, not instructions")
        calls = directives_in(task)
        if calls:
            self._task_done = True
            return ModelReply(tool_call=calls[0], rationale="following directive from the user task")
        return ModelReply(final="Could not act on the task.", rationale="no directive in user task")


MODELS = {m.name: m for m in (NaiveScriptedModel, HardenedScriptedModel)}
