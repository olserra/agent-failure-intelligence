from afi.dedup import deduplicate, fingerprint
from afi.verify import Violation


def test_same_fingerprint_merges():
    v1 = Violation("fs-read-scope", "fs.read", "/system/secrets.txt", "d")
    v2 = Violation("fs-read-scope", "fs.read", "/system/secrets.txt", "d")
    failures = deduplicate([("s1", v1), ("s2", v2)])
    assert len(failures) == 1
    assert failures[0].occurrences == 2
    assert failures[0].first_scenario == "s1"


def test_distinct_targets_stay_distinct():
    v1 = Violation("fs-read-scope", "fs.read", "/a", "d")
    v2 = Violation("fs-read-scope", "fs.read", "/b", "d")
    assert fingerprint(v1) != fingerprint(v2)
    assert len(deduplicate([("s1", v1), ("s2", v2)])) == 2
