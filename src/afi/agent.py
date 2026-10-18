"""Minimal agent loop: model decides, executor runs the simulated tool,
everything is recorded in a structured trace."""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict

from .models import Model
from .tools import Toolset, ToolCall, ToolResult


@dataclass
class TraceEvent:
    step: int
    kind: str  # "decision" | "tool_result"
    data: dict


@dataclass
class Trace:
    scenario_id: str
    model: str
    task: str
    policy_text: str
    events: list[TraceEvent] = field(default_factory=list)
    final_answer: str | None = None
    wall_time_ms: float = 0.0

    def tool_calls(self) -> list[ToolCall]:
        calls = []
        for ev in self.events:
            if ev.kind == "decision" and ev.data.get("tool_call"):
                tc = ev.data["tool_call"]
                calls.append(ToolCall(tc["tool"], tc["args"]))
        return calls

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "model": self.model,
            "task": self.task,
            "policy_text": self.policy_text,
            "events": [asdict(e) for e in self.events],
            "final_answer": self.final_answer,
            "wall_time_ms": self.wall_time_ms,
        }


def run_agent(model: Model, toolset: Toolset, scenario_id: str, task: str,
              policy_text: str, max_steps: int = 8) -> Trace:
    trace = Trace(scenario_id=scenario_id, model=model.name, task=task, policy_text=policy_text)
    start = time.perf_counter()
    last_output: str | None = None
    for step in range(max_steps):
        reply = model.decide(task, policy_text, last_output, step)
        if reply.final is not None or reply.tool_call is None:
            trace.events.append(TraceEvent(step, "decision", {
                "final": reply.final, "rationale": reply.rationale}))
            trace.final_answer = reply.final
            break
        trace.events.append(TraceEvent(step, "decision", {
            "tool_call": {"tool": reply.tool_call.tool, "args": reply.tool_call.args},
            "rationale": reply.rationale}))
        result: ToolResult = toolset.execute(reply.tool_call)
        trace.events.append(TraceEvent(step, "tool_result", {
            "tool": result.tool, "args": result.args, "ok": result.ok,
            "output": result.output}))
        last_output = result.output
    trace.wall_time_ms = (time.perf_counter() - start) * 1000
    return trace
