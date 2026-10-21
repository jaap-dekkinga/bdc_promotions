"""PreToolUse hook: Jaap must approve every email send and every deploy.

Claude Code pipes the tool call as JSON on stdin. If the call would send an
email or ship code to the live site, this prints a permissionDecision of
"ask", so Claude Code stops and asks Jaap even in auto mode or a scheduled
run. Everything else passes through untouched (no output, exit 0).
"""
import json
import re
import sys

# Mail tools only (gmail, outlook, ...): SendMessage between Claude sessions is not email.
EMAIL_TOOL = re.compile(r"(gmail|mail|outlook).*send|send.*(gmail|mail|outlook)", re.I)
EMAIL_CMD = re.compile(
    r"\b(sendmail|mutt|msmtp|Send-MailMessage)\b"
    r"|(^|[;&|]\s*)mail\s"
    r"|gmail\.googleapis\.com\S*/send",
    re.I,
)

# Pushing to main deploys bedc.shop (static.yml). Any push is asked about,
# because a branch push can be merged or retargeted later in the same run.
DEPLOY_CMD = re.compile(
    r"\bgit\s+push\b"
    r"|\bgh\s+pr\s+merge\b"
    r"|\bgh\s+workflow\s+run\b"
    r"|\bgh\s+run\s+rerun\b"
    r"|\bgh\s+api\b.*(/merges|/dispatches|/pages)",
    re.I,
)
DEPLOY_TOOL = re.compile(r"auto_merge|merge_pull_request|push_files|create_or_update_file", re.I)


def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return
    tool = call.get("tool_name", "")
    command = str((call.get("tool_input") or {}).get("command", ""))

    if EMAIL_TOOL.search(tool) or EMAIL_CMD.search(command):
        ask("Sending email needs Jaap's OK (hook: .claude/hooks/require_approval.py). Drafts are fine; sending is not.")
    if DEPLOY_TOOL.search(tool) or DEPLOY_CMD.search(command):
        ask("Pushing, merging or running a workflow can deploy bedc.shop and needs Jaap's OK (hook: .claude/hooks/require_approval.py).")


if __name__ == "__main__":
    main()
