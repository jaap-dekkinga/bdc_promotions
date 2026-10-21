"""PreToolUse hook: Jaap must approve every email send and every deploy.

Claude Code pipes the tool call as JSON on stdin. If the call would send an
email or ship code to the live site, this prints a permissionDecision of
"ask", so Claude Code stops and asks Jaap even in auto mode or a scheduled
run. Everything else passes through untouched (no output, exit 0).
If the input can't be read, it asks too: this hook fails closed.

It matches text, so it can be fooled by deliberate obfuscation (aliases,
variables) and it can't see a click on "Send" in a browser tool. It also
asks on harmless commands that merely mention `git push`; that's on purpose.
"""
import json
import re
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

# Pushing to main deploys bedc.shop (static.yml). Any push is asked about,
# because a branch push can be merged or retargeted later in the same run.
# `git -C dir push`, `git -c k=v push` and `git.exe push` count too.
DEPLOY_CMD = re.compile(
    r"\bgit(\.exe)?\b[^\n;&|]*\bpush\b"
    r"|\bgh\s+pr\s+merge\b"
    r"|\bgh\s+workflow\s+run\b"
    r"|\bgh\s+run\s+rerun\b"
    r"|(\bgh\s+api\b|api\.github\.com)[^\n]*(pulls/\d+/merge|/merges|/dispatches|/pages|git/refs|/contents/)",
    re.I,
)
DEPLOY_TOOL = re.compile(r"auto_merge|merge_pull_request|push_files|create_or_update_file|delete_file", re.I)


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
    command = str(command or "")

    if EMAIL_TOOL.search(tool) or EMAIL_CMD.search(command):
        ask("Sending email needs Jaap's OK (hook: .claude/hooks/require_approval.py). Drafts are fine; sending is not.")
    if DEPLOY_TOOL.search(tool) or DEPLOY_CMD.search(command):
        ask("Pushing, merging or running a workflow can deploy bedc.shop and needs Jaap's OK (hook: .claude/hooks/require_approval.py).")


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
