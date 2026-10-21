"""PreToolUse hook: Jaap must approve every email send, every deploy, every
write to the Printful store, and every change to the files that guard them.

Claude Code pipes the tool call as JSON on stdin. If the call would send an
email, ship code to the live site or create/change a Printful product, this prints a permissionDecision of
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

# Creating or changing anything in the Printful store. Any shell command that
# talks to the API directly or names the client is asked about (curl,
# Invoke-RestMethod, python -c, runpy...), because reads go through WebFetch or
# the two scripts. Running any other scripts/printful_*.py is asked about too.
PRINTFUL_WRITE = re.compile(
    r"printful_create(\.py)?\b[^\n]*--a"            # --apply, quoted or not
    r"|\b(import|from|runpy|run_path|run_module)\b[^\n]*\bprintful_create\b"
    r"|\bprintful_create\b[^\n]*\b(import|runpy|run_path|run_module)\b"
    r"|api\.printful\.com|\bprintful_api\b|\ballow_write\b"
    r"|scripts[/\\]printful_(?!sync\.py|create\.py)\w*\.py",
    re.I,
)
# Files that decide what Claude may do: changing them needs Jaap's OK.
PROTECTED_FILES = re.compile(
    r"(^|[/\\])(scripts[/\\]printful_\w*\.py|\.claude[/\\](hooks[/\\][^/\\]+|settings(\.local)?\.json)"
    r"|\.github[/\\]workflows[/\\][^/\\]+)$",
    re.I,
)
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# The create script and "apply" anywhere in one command, even on different lines.
CREATE_AND_APPLY = re.compile(r"printful_create.*(--a|\bapply\b)", re.I | re.S)
# Shell commands that change a protected file (the Write/Edit check can't see these).
PROTECTED_IN_SHELL = re.compile(
    r"scripts[/\\]printful_|\.claude[/\\](hooks|settings)|\.github[/\\]workflows", re.I)
SHELL_WRITES = re.compile(
    r">|\btee\b|\bsed\b[^\n]*\s-i|\b(Set|Add|Clear)-Content\b|\bOut-File\b|\b(cp|mv|rm|del|copy|move|ren)\b"
    r"|\b(Copy|Move|Remove|Rename|New)-Item\b|\btruncate\b|\bgit\s+(checkout|restore|apply|reset|stash|mv|rm|am)\b"
    r"|\bopen\s*\(|write_text|write_bytes|shutil\.", re.I)
# A command split over lines (\ in bash, ` in PowerShell) is matched as one line.
CONTINUATION = re.compile(r"(\\|`)\r?\n")


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
    if PRINTFUL_WRITE.search(command):
        ask("Creating or changing a Printful product needs Jaap's OK. Check the dry-run payload first "
            "(hook: .claude/hooks/require_approval.py).")
    if CREATE_AND_APPLY.search(command):
        ask("Creating a Printful product needs Jaap's OK. Check the dry-run payload first "
            "(hook: .claude/hooks/require_approval.py).")
    if PROTECTED_IN_SHELL.search(command) and SHELL_WRITES.search(command):
        ask("This command may change the Printful scripts, the hooks, Claude's settings or a workflow, "
            "which needs Jaap's OK (hook: .claude/hooks/require_approval.py).")
    if tool in WRITE_TOOLS and isinstance(tool_input, dict):
        path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if PROTECTED_FILES.search(path):
            ask("Changing the Printful scripts, the hooks, Claude's settings or a workflow needs Jaap's OK "
                "(hook: .claude/hooks/require_approval.py).")
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
