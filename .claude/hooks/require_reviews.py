"""Hooks that stop Claude opening a PR before the review agents ran.

CLAUDE.md and docs/code-review-process.md ask for the `verifier` and
`code-reviewer` subagents before every PR. Claude once skipped them, so:

  record  (PostToolUse on Agent): when Claude starts a verifier or
          code-reviewer subagent, write {branch, agent, time} as one
          file per run in .git/claude-reviews/ (inside .git, so never
          committed or published).
  check   (PreToolUse on Bash/PowerShell): on `gh pr create` or
          `gh pr ready`, deny unless both agents were recorded for the
          branch, and deny if the PR body still says either one was
          "not run".

Limits: it sees that a review was started, not that its findings were
fixed, and it can't see the app's own "Create PR" button.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time

AGENTS = ("verifier", "code-reviewer")
PR_CMD = re.compile(r"\bgh\s+pr\s+(create|ready)\b")
NOT_RUN = re.compile(r"(verifier|code-reviewer)[^\n]*\bnot\s+run\b", re.I)


def git(*args):
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    return out.stdout.strip()


def log_dir():
    git_dir = git("rev-parse", "--absolute-git-dir")
    return pathlib.Path(git_dir) / "claude-reviews" if git_dir else None


def recorded(branch):
    """Agents recorded for a branch. One file per run, because parallel
    subagents appending to one file on Windows can overwrite each other."""
    ran = set()
    path = log_dir()
    if path and path.is_dir():
        for f in path.glob("*.json"):
            try:
                entry = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(entry, dict) and entry.get("branch") == branch:
                ran.add(entry.get("agent"))
    return ran


def which_agent(tool_input):
    kind = str(tool_input.get("subagent_type", ""))
    prompt = str(tool_input.get("prompt", ""))
    for name in AGENTS:
        if kind == name or f".claude/agents/{name}.md" in prompt.replace("\\", "/"):
            return name
    return None


def record(call):
    if call.get("tool_name") not in ("Agent", "Task"):
        return
    tool_input = call.get("tool_input")
    name = which_agent(tool_input if isinstance(tool_input, dict) else {})
    path = log_dir()
    if not name or not path:
        return
    entry = {"branch": git("rev-parse", "--abbrev-ref", "HEAD"), "agent": name, "time": int(time.time())}
    path.mkdir(exist_ok=True)
    (path / f"{name}-{time.time_ns()}-{os.getpid()}.json").write_text(json.dumps(entry), encoding="utf-8")


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def pr_body(command):
    body = command
    match = re.search(r"--body-file[= ]+(\"[^\"]+\"|'[^']+'|\S+)", command)
    if match and match.group(1).strip("\"'") != "-":
        try:
            body += pathlib.Path(match.group(1).strip("\"'")).read_text(encoding="utf-8")
        except OSError:
            pass
    return body


def check(call):
    tool_input = call.get("tool_input")
    command = str(tool_input.get("command", "") if isinstance(tool_input, dict) else tool_input or "")
    if not PR_CMD.search(command):
        return
    head = re.search(r"--head[= ]+(\S+)", command)
    branch = head.group(1) if head else git("rev-parse", "--abbrev-ref", "HEAD")

    ran = recorded(branch)
    missing = [a for a in AGENTS if a not in ran]
    if missing:
        deny(f"No PR yet: run the {' and '.join(missing)} subagent(s) on branch '{branch}' first "
             "(CLAUDE.md Definition of done; High tier = code-reviewer twice). "
             "Hook: .claude/hooks/require_reviews.py")
    if NOT_RUN.search(pr_body(command)):
        deny("The PR body says the verifier or code-reviewer was not run. Paste their real results "
             "into the Testing section. Hook: .claude/hooks/require_reviews.py")


def main():
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(call, dict):
        return
    if sys.argv[1:] == ["record"]:
        record(call)
    else:
        check(call)


if __name__ == "__main__":
    main()
