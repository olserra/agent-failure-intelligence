from afi.policy import Policy


def test_read_roots():
    p = Policy()
    assert p.read_allowed("/public/a.txt")
    assert p.read_allowed("/workspace/x/y.md")
    assert not p.read_allowed("/system/secrets.txt")
    assert not p.read_allowed("/publicity/x")  # prefix trick must not pass


def test_write_roots():
    p = Policy()
    assert p.write_allowed("/workspace/out.md")
    assert not p.write_allowed("/system/config")
    assert not p.write_allowed("/public/x")


def test_http_allowlist():
    p = Policy()
    assert p.fetch_allowed("https://docs.example.com/setup")
    assert not p.fetch_allowed("https://collect.evil.example/exfil")
    assert not p.fetch_allowed("https://docs.example.com.evil.example/x")


def test_denied_tools():
    assert "message.send" in Policy().denied_tools
