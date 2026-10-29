"""Submit the packages locked in uv.lock to the GitHub dependency graph.

Run by .github/workflows/dependency-submission.yml through the dependency submission API.
Standard library only, so the job needs no install step.
"""

import json
import os
import tomllib
import urllib.request
from datetime import UTC, datetime

with open("uv.lock", "rb") as file:
    packages = tomllib.load(file)["package"]

root = next(p for p in packages if p.get("source") in ({"virtual": "."}, {"editable": "."}))
locked = [p for p in packages if p is not root]


def find(dep: dict) -> dict | None:
    """Return the locked package a dependency entry points to (uv adds `version` when a name is locked twice)."""
    matches = (p for p in locked if p["name"] == dep["name"] and dep.get("version", p["version"]) == p["version"])
    return next(matches, None)


def purl(package: dict) -> str:
    return f"pkg:pypi/{package['name']}@{package['version']}"


def reachable(deps: list[dict]) -> set[str]:
    """Return the package URLs reachable from `deps`, following the extras each entry enables."""
    seen = set()
    stack = list(deps)
    while stack:
        dep = stack.pop()
        package = find(dep)
        if package is None:
            continue
        for extra in [None, *dep.get("extra", [])]:
            if (purl(package), extra) in seen:
                continue
            seen.add((purl(package), extra))
            if extra is None:
                stack += package.get("dependencies", [])
            else:
                stack += package.get("optional-dependencies", {}).get(extra, [])
    return {url for url, _ in seen}


runtime_deps = root.get("dependencies", [])
dev_deps = [dep for group in root.get("dev-dependencies", {}).values() for dep in group]
runtime = reachable(runtime_deps)
direct = {purl(p) for p in map(find, runtime_deps + dev_deps) if p}

resolved = {
    purl(p): {
        "package_url": purl(p),
        "relationship": "direct" if purl(p) in direct else "indirect",
        "scope": "runtime" if purl(p) in runtime else "development",
        "dependencies": [purl(d) for d in map(find, p.get("dependencies", [])) if d],
    }
    for p in locked
}

env = os.environ
snapshot = {
    "version": 0,
    "sha": env["GITHUB_SHA"],
    "ref": env["GITHUB_REF"],
    "job": {"correlator": f"{env['GITHUB_WORKFLOW']}_{env['GITHUB_JOB']}", "id": env["GITHUB_RUN_ID"]},
    "detector": {
        "name": "uv-lock-submission",
        "version": "1.0.0",
        "url": f"{env['GITHUB_SERVER_URL']}/{env['GITHUB_REPOSITORY']}",
    },
    "scanned": datetime.now(UTC).isoformat(timespec="seconds"),
    "manifests": {"uv.lock": {"name": "uv.lock", "file": {"source_location": "uv.lock"}, "resolved": resolved}},
}
request = urllib.request.Request(
    f"{env['GITHUB_API_URL']}/repos/{env['GITHUB_REPOSITORY']}/dependency-graph/snapshots",
    data=json.dumps(snapshot).encode(),
    headers={
        "Authorization": f"Bearer {env['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    method="POST",
)
with urllib.request.urlopen(request) as response:
    print(f"Submitted {len(resolved)} packages: {response.read().decode()}")
