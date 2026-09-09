from scripts import lock_dependencies


def test_runtime_lock_keeps_transitive_extras(monkeypatch):
    graph = {
        "agent": ["jwt[crypto]>=2", "base"],
        "jwt": ["crypto; extra == 'crypto'", "unneeded; extra == 'docs'"],
        "crypto": ["ffi"],
        "ffi": [],
        "base": [],
    }
    monkeypatch.setattr(lock_dependencies.metadata, "requires", lambda name: graph[name])
    assert lock_dependencies.runtime_dependencies(["agent"]) == {
        "agent",
        "jwt",
        "crypto",
        "ffi",
        "base",
    }


def test_extra_discovered_after_base_package_is_still_processed(monkeypatch):
    graph = {"agent": ["jwt[crypto]"], "jwt": ["crypto; extra == 'crypto'"], "crypto": []}
    monkeypatch.setattr(lock_dependencies.metadata, "requires", lambda name: graph[name])
    assert lock_dependencies.runtime_dependencies(["agent", "jwt"]) == {"agent", "jwt", "crypto"}
