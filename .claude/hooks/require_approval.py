"""PreToolUse hook: Jaap must approve every email send, every deploy of
bedc.shop, and every new Printful product. Nothing else asks.

Claude Code pipes the tool call as JSON on stdin. If the call would send an
email, change `main` (which bedc.shop pulls) or create a Printful product,
this prints a permissionDecision of "ask", so Claude Code stops and asks Jaap,
even in auto mode or a scheduled run. Everything else passes through
untouched (no output, exit 0). If the input can't be read, it asks too.

It matches text, so it can't catch deliberate obfuscation or a click on
"Send" in a browser tool. The Printful token itself is guarded in code: the
Printful client in scripts/ hands it only to the sync and create scripts.
"""
import json
import os
import re
import subprocess
import sys

# Mail tools only (gmail, outlook, ...): SendMessage between Claude sessions is not email.
EMAIL_TOOL = re.compile(r"(gmail|mail|outlook).*send|send.*(gmail|mail|outlook)", re.I)
EMAIL_CMD = re.compile(
    r"\b(sendmail|mutt|msmtp|Send-MailMessage|smtplib)\b"
    r"|(^|[;&|]\s*)mail\s"
    r"|smtps?://|--mail-rcpt"
    r"|gmail\.googleapis\.com\S*/send",
    re.I | re.M,
)

# bedc.shop pulls main, so anything that changes main is a deploy. A push of a
# feature branch is not; it only asks when it targets main (see push_reaches_main).
PUSH = re.compile(r"\bgit(\.exe)?\b[^\n;&|]*?\bpush\b([^\n;&|]*)", re.I)
TARGETS_MAIN = re.compile(r"(^|[\s:+])(refs/heads/)?(main|master)(\s|$)|--all\b|--mirror\b", re.I)
DEPLOY_CMD = re.compile(
    r"\bgh\s+pr\s+merge\b"
    r"|\bgh\s+workflow\s+run\b"
    r"|\bgh\s+run\s+rerun\b"
    r"|(\bgh\s+api\b|api\.github\.com)[^\n]*(pulls/\d+/merge|/merges|/dispatches|/pages|git/refs|/contents/)",
    re.I,
)
DEPLOY_TOOL = re.compile(r"auto_merge|merge_pull_request|push_files|create_or_update_file|delete_file", re.I)

# Creating a Printful product: the create script plus the apply flag anywhere in
# one command (quoted, abbreviated or on another line all count). The script
# name is built here so the secret guard doesn't mistake this file for a caller.
CREATE_SCRIPT = "printful" + "_create"
CREATE_AND_APPLY = re.compile(CREATE_SCRIPT + r".*(--a|\bapply\b)", re.I | re.S)

# A command split over lines (\ in bash, ` in PowerShell) is matched as one line.
CONTINUATION = re.compile(r"(\\|`)\r?\n")


def current_branch():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        out = subprocess.run(["git", "-C", root, "symbolic-ref", "--short", "-q", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def push_reaches_main(command):
    for match in PUSH.finditer(command):
        args = match.group(2)
        if TARGETS_MAIN.search(args):
            return True
        refs = [a for a in args.split() if not a.startswith("-")][1:]  # after the remote name
        if not refs or any(r == "HEAD" or r.startswith("HEAD:") for r in refs):
            if current_branch() in ("main", "master", "", "HEAD"):
                return True  # pushes the current branch, which is main (or unknown)
    return False


def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def check(call):
    tool = str(call.get("tool_name") or "")
    tool_input = call.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else tool_input
    if isinstance(command, list):
        command = " ".join(map(str, command))
    command = CONTINUATION.sub(" ", str(command or ""))

    if EMAIL_TOOL.search(tool) or EMAIL_CMD.search(command):
        ask("Sending email needs Jaap's OK (hook: .claude/hooks/require_approval.py). Drafts are fine; sending is not.")
    if CREATE_AND_APPLY.search(command):
        ask("Creating a Printful product needs Jaap's OK. Check the dry-run payload first "
            "(hook: .claude/hooks/require_approval.py).")
    if DEPLOY_TOOL.search(tool) or DEPLOY_CMD.search(command) or push_reaches_main(command):
        ask("This changes main, which bedc.shop deploys from, so it needs Jaap's OK "
            "(hook: .claude/hooks/require_approval.py).")


def main():
    try:
        call = json.load(sys.stdin)
        if not isinstance(call, dict):
            raise ValueError("tool call is not a JSON object")
        check(call)
    except SystemExit:
        raise
    except Exception as e:
        ask(f"Approval hook couldn't read this tool call ({e}), so it asks to be safe.")


if __name__ == "__main__":
    main()
