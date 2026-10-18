"""Simulated tools for the AFI PoC.

Every tool runs against an in-memory, fully isolated environment. Nothing here
touches the real filesystem, network, or any third-party service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimEnvironment:
    """Isolated simulated world for one scenario run."""
    files: dict[str, str] = field(default_factory=dict)
    web: dict[str, str] = field(default_factory=dict)  # url -> page content
    sent_messages: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ToolCall:
    tool: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    tool: str
    args: dict[str, Any]
    ok: bool
    output: str


class Toolset:
    """Simulated tools. The executor never blocks a call: the agent under test
    is told the permission policy, and the verifier flags attempts that break
    it. Executing the (simulated) action is what produces observable evidence."""

    def __init__(self, env: SimEnvironment):
        self.env = env

    def execute(self, call: ToolCall) -> ToolResult:
        handler = getattr(self, "_tool_" + call.tool.replace(".", "_"), None)
        if handler is None:
            return ToolResult(call.tool, call.args, False, f"unknown tool: {call.tool}")
        try:
            return handler(**call.args)
        except TypeError as exc:
            return ToolResult(call.tool, call.args, False, f"bad arguments: {exc}")

    def _tool_fs_read(self, path: str) -> ToolResult:
        if path in self.env.files:
            return ToolResult("fs.read", {"path": path}, True, self.env.files[path])
        return ToolResult("fs.read", {"path": path}, False, f"file not found: {path}")

    def _tool_fs_write(self, path: str, content: str) -> ToolResult:
        self.env.files[path] = content
        return ToolResult("fs.write", {"path": path}, True, f"wrote {len(content)} bytes to {path}")

    def _tool_http_fetch(self, url: str) -> ToolResult:
        if url in self.env.web:
            return ToolResult("http.fetch", {"url": url}, True, self.env.web[url])
        return ToolResult("http.fetch", {"url": url}, False, f"no canned response for: {url}")

    def _tool_message_send(self, to: str, text: str) -> ToolResult:
        self.env.sent_messages.append({"to": to, "text": text})
        return ToolResult("message.send", {"to": to}, True, f"message queued to {to}")
