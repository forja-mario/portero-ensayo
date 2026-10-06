"""Atestacion minima del ensayo publico; no publica estados ni usa secretos."""

import json
import os
import re
import urllib.request
from pathlib import Path

REPO = "forja-mario/portero-ensayo"
SHA = re.compile(r"[0-9a-f]{40}\Z")


def get(path):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + REPO + path,
        headers={
            "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def checked(value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError("SHA ilegible")
    return value


def attest(event, needs, read=get):
    if (
        os.environ["GITHUB_REPOSITORY"] != REPO
        or not isinstance(needs, dict)
        or set(needs) != {"pruebas"}
        or needs["pruebas"].get("result") != "success"
    ):
        raise ValueError("repositorio o pruebas no verdes")
    number = event["number"]
    if type(number) is not int or number < 1:
        raise ValueError("numero ilegible")
    pull = read(f"/pulls/{number}")
    base = checked(pull["base"]["sha"])
    head = checked(pull["head"]["sha"])
    if (
        pull["state"] != "open"
        or pull["base"]["ref"] != "main"
        or checked(event["pull_request"]["base"]["sha"]) != base
        or checked(event["pull_request"]["head"]["sha"]) != head
        or checked(read("/git/ref/heads/main")["object"]["sha"]) != base
    ):
        raise ValueError("peticion o main cambiaron")
    merge = checked(read(f"/git/ref/pull/{number}/merge")["object"]["sha"])
    commit = read(f"/git/commits/{merge}")
    tree = checked(commit["tree"]["sha"])
    if [checked(x["sha"]) for x in commit["parents"]] != [base, head]:
        raise ValueError("padres de fusion ajenos")
    run_id = int(os.environ["GITHUB_RUN_ID"])
    attempt = int(os.environ["GITHUB_RUN_ATTEMPT"])
    if run_id < 1 or attempt < 1:
        raise ValueError("ejecucion ilegible")
    return {
        "version": 1,
        "repository": REPO,
        "number": number,
        "base_sha": base,
        "head_sha": head,
        "merge_sha": merge,
        "tree_sha": tree,
        "run_id": run_id,
        "attempt": attempt,
        "result": "success",
    }


if __name__ == "__main__":
    result = attest(
        json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()),
        json.loads(os.environ["FORJA_NEEDS_JSON"]),
    )
    print("FORJA_PORTERO_ATTEST_V1 " + json.dumps(result, sort_keys=True, separators=(",", ":")))
