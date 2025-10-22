#!/usr/bin/env python3
import os, re, sys, subprocess, json, textwrap, pathlib, urllib.request

GITHUB_API = "https://api.github.com"

def fetch_tag_sha(owner, repo, tag, token=None):
    headers = {"Accept":"application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/ref/tags/{tag}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            return data.get("object", {}).get("sha")
    except Exception as e:
        return None

def parse_uses(line):
    m = re.search(r'uses:\s*([\w\-/]+)@(.+)$', line.strip())
    if not m:
        return None
    return m.group(1), m.group(2)

def owner_repo_from_action(action):
    parts = action.split('/')
    owner = parts[0]
    repo = parts[1]
    return owner, repo

def main():
    token = os.environ.get("GITHUB_PAT")
    repo_root = os.getcwd()
    workflows = list(pathlib.Path(".github/workflows").glob("*.yml"))
    for wf in workflows:
        content = wf.read_text()
        changed = False
        new_lines = []
        for line in content.splitlines():
            parsed = parse_uses(line)
            if parsed:
                action, ref = parsed
                if re.match(r'^[0-9A-Za-z._-]+$', ref) and not re.match(r'^[0-9a-f]{40}$', ref):
                    owner, repo = owner_repo_from_action(action)
                    tag = ref
                    print(f"Resolving {action}@{tag}")
                    sha = fetch_tag_sha(owner, repo, tag, token)
                    if sha:
                        new_line = line.replace(f"@{tag}", f"@{sha}")
                        new_lines.append(new_line)
                        changed = True
                        continue
            new_lines.append(line)
        if changed:
            wf.write_text("\n".join(new_lines) + "\n")
            print(f"Pinned refs in {wf}")

if __name__ == "__main__":
    main()
