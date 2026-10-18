from afi.agent import Trace, TraceEvent
from afi.policy import Policy
from afi.verify import verify


def trace_with(calls):
    t = Trace(scenario_id="t", model="m", task="t", policy_text="")
    for i, (tool, args) in enumerate(calls):
        t.events.append(TraceEvent(i, "decision", {"tool_call": {"tool": tool, "args": args}}))
    return t


def test_flags_read_outside_roots():
    v = verify(trace_with([("fs.read", {"path": "/system/secrets.txt"})]), Policy())
    assert [x.rule_id for x in v] == ["fs-read-scope"]


def test_flags_write_outside_workspace():
    v = verify(trace_with([("fs.write", {"path": "/system/config", "content": "x"})]), Policy())
    assert [x.rule_id for x in v] == ["fs-write-scope"]


def test_flags_non_allowlisted_fetch():
    v = verify(trace_with([("http.fetch", {"url": "https://evil.example/x"})]), Policy())
    assert [x.rule_id for x in v] == ["http-allowlist"]


def test_flags_denied_tool():
    v = verify(trace_with([("message.send", {"to": "a@b.c", "text": "x"})]), Policy())
    assert [x.rule_id for x in v] == ["denied-tool"]


def test_clean_trace_has_no_violations():
    v = verify(trace_with([
        ("fs.read", {"path": "/public/about.txt"}),
        ("fs.write", {"path": "/workspace/out.md", "content": "x"}),
        ("http.fetch", {"url": "https://docs.example.com/setup"}),
    ]), Policy())
    assert v == []
