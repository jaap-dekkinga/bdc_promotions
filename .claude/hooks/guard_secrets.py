"""PreToolUse hook: keep tokens out of files, commands and messages.

The repo is public and bedc.shop serves files from it, so a token written
anywhere here is a leaked token. This denies a tool call when:
  - anything it would write or run contains something that looks like a
    token (a Printful-style 30+ character mixed-case key, a GitHub token,
    a private key, or "Authorization: Bearer <literal>");
  - a command tries to read or print the stored Printful token
    (Credential Manager "bdc-printful", $PRINTFUL_TOKEN, CredRead...), or to
    store a secret (`gh secret set`, `cmdkey /pass`): only Jaap does that.
    Listing the environment (`env`, `printenv`, `gci env:`) counts too;
  - a file written outside scripts/printful_*.py and these hooks contains
    code that reads the token (get_token(), CredRead, import printful_api).
Only scripts/printful_api.py reads the token, inside the printful_*.py scripts.
`python .claude/hooks/guard_secrets.py scan` checks tracked files (CI).

It can't catch a token that is split up or encoded on purpose.
"""
import json
import re
import sys

TOKEN_PATTERNS = [
    # Printful private tokens and similar API keys: long, mixed case, with digits.
    re.compile(r"(?<![A-Za-z0-9_\-])(?=[A-Za-z0-9]*[a-z])(?=[A-Za-z0-9]*[A-Z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{30,64}(?![A-Za-z0-9_\-])"),
    re.compile(r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"Authorization:\s*Bearer\s+(?![\"']?\s*[\$%{+(])[A-Za-z0-9._\-]{12,}", re.I),
]
# Reading, printing or storing the token. Merely naming it (docs, commit
# messages, `env -u PRINTFUL_TOKEN`) is fine.
READS_TOKEN = re.compile(
    r"\$\{?PRINTFUL_TOKEN|\$env:PRINTFUL_TOKEN|env:\\?PRINTFUL|\bprintenv\b|\b(Get-ChildItem|gci|dir|ls)\s+env:"
    r"|(^|[;&|(`]\s*)env\s*($|[|;&>])|GetEnvironmentVariable"
    r"|(os\.environ|getenv)[^\n]*PRINTFUL_TOKEN|CredRead|Get-StoredCredential|\bvaultcmd\b"
    r"|get_token|_token_from_credential_manager|(import|from)\s+printful_api\b"
    r"|\bgh\s+secret\s+set\b|\bcmdkey\b[^\n]*(/pass|bdc-printful)",
    re.I | re.M,
)
# Code that reads the token may only live in the Printful scripts and these hooks.
CODE_READS_TOKEN = re.compile(r"get_token\s*\(|_token_from_credential_manager|CredRead|(import|from)\s+printful_api\b")
TOKEN_CODE_FILES = re.compile(r"(^|[/\\])(scripts[/\\]printful_\w+\.py|\.claude[/\\]hooks[/\\]\w+\.py)$")
SHELL_TOOLS = {"Bash", "PowerShell"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason + " (hook: .claude/hooks/guard_secrets.py)",
        }
    }))
    sys.exit(0)


def scan_repo():
    """CI mode: fail if any tracked text file contains something token-like."""
    import subprocess
    files = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True, check=True).stdout.split("\0")
    hits = []
    for name in filter(None, files):
        try:
            with open(name, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable
        for no, line in enumerate(lines, 1):
            for pattern in TOKEN_PATTERNS:
                found = pattern.search(line)
                if found:  # CI logs are public: never print any part of the match
                    hits.append(f"{name}:{no}: looks like a secret")
    if hits:
        print("\n".join(hits))
        print("::error::Possible secret in tracked files. Revoke it, remove it, and see CLAUDE.md.")
        sys.exit(1)
    print(f"OK: no token-like strings in {len([f for f in files if f])} tracked files")


def main():
    if sys.argv[1:] == ["scan"]:
        scan_repo()
        return
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(call, dict):
        return
    tool = str(call.get("tool_name") or "")
    tool_input = call.get("tool_input") if isinstance(call.get("tool_input"), (dict, list, str)) else {}

    for text in strings(tool_input):
        for pattern in TOKEN_PATTERNS:
            found = pattern.search(text)
            if found:
                hint = found.group(0)[:4] + "…"
                deny(f"This looks like a secret ({hint}). Never write tokens into files, commands or messages; "
                     "the token belongs in GitHub Secrets or Windows Credential Manager only.")

    if tool in SHELL_TOOLS:
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        if READS_TOKEN.search(str(command)):
            deny("Commands may not read, print or store the Printful token. Run scripts/printful_sync.py "
                 "or printful_create.py without mentioning it; only Jaap stores it.")
    if tool in WRITE_TOOLS and isinstance(tool_input, dict):
        path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if not TOKEN_CODE_FILES.search(path):
            for text in strings({k: v for k, v in tool_input.items() if k not in ("file_path", "notebook_path")}):
                if CODE_READS_TOKEN.search(text):
                    deny("Only scripts/printful_*.py may contain code that reads the Printful token.")


if __name__ == "__main__":
    main()
