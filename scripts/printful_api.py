"""Minimal Printful API client for the Be DC scripts (standard library only).

Where the token comes from, in order:
  1. the PRINTFUL_TOKEN environment variable (GitHub Actions secret), or
  2. Windows Credential Manager, generic credential "bdc-printful"
     (add it yourself with:  cmdkey /generic:bdc-printful /user:printful /pass
      and paste the token at the prompt, so it never lands in shell history).

The token is only ever put in the Authorization header. It is never printed,
logged, written to a file, or included in an error message.
Set PRINTFUL_STORE_ID (not secret) only if you use an account-level token.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.printful.com"
CREDENTIAL_TARGET = "bdc-printful"
USER_AGENT = "bdc-printful-scripts/1.0"
MAX_IMAGE_BYTES = 5 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


class PrintfulError(Exception):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """urllib copies the Authorization header to redirect targets, even on
    another host. API calls never follow redirects, so the token can't leak."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_api_opener = urllib.request.build_opener(_NoRedirect)


def _is_printful_host(url):
    parts = urllib.parse.urlparse(url or "")
    host = parts.hostname or ""
    return parts.scheme == "https" and (host == "printful.com" or host.endswith(".printful.com"))


class _PrintfulOnlyRedirect(urllib.request.HTTPRedirectHandler):
    """Image downloads may follow redirects, but only to other Printful hosts."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _is_printful_host(newurl):
            raise PrintfulError(f"image redirect to a non-Printful host refused: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_image_opener = urllib.request.build_opener(_PrintfulOnlyRedirect)


def _token_from_credential_manager():
    _require_entry_script("printful_sync.py", "printful_create.py")
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR),
        ]

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]
    cred = ctypes.POINTER(CREDENTIAL)()
    if not advapi32.CredReadW(CREDENTIAL_TARGET, 1, 0, ctypes.byref(cred)):  # 1 = generic
        return None
    try:
        blob = ctypes.string_at(cred.contents.CredentialBlob, cred.contents.CredentialBlobSize)
    finally:
        advapi32.CredFree(cred)
    # cmdkey stores the secret as UTF-16; other tools may use UTF-8.
    for encoding in ("utf-16-le", "utf-8"):
        try:
            text = blob.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
        if text.isascii() and text.isprintable():
            return text
    return None


def _require_entry_script(*allowed):
    """Refuse unless the running program is one of these scripts in this folder.

    The hooks match text, so an agent could still write its own file (any
    extension) that imports this module. This check doesn't depend on text:
    the token and writes are only available to the real sync/create scripts,
    not to python -c, a copy, or a helper file."""
    main = getattr(sys.modules.get("__main__"), "__file__", None) or ""
    here = os.path.dirname(os.path.abspath(__file__))
    ok = {os.path.normcase(os.path.join(here, name)) for name in allowed}
    if not main or os.path.normcase(os.path.abspath(main)) not in ok:
        raise PrintfulError("The Printful token can only be used by " + " or ".join(
            f"scripts/{name}" for name in allowed) + ", run directly.")


def get_token():
    _require_entry_script("printful_sync.py", "printful_create.py")
    token = os.environ.get("PRINTFUL_TOKEN", "").strip() or _token_from_credential_manager()
    if not token:
        raise PrintfulError(
            "No Printful token found. In GitHub: set the PRINTFUL_TOKEN repository secret. "
            f"On this PC: run  cmdkey /generic:{CREDENTIAL_TARGET} /user:printful /pass  "
            "and paste the token at the prompt.")
    return token


def _error_message(err):
    try:
        data = json.loads(err.read().decode("utf-8"))
        return (data.get("error") or {}).get("message") or data.get("result") or err.reason
    except (ValueError, AttributeError, UnicodeDecodeError):
        return err.reason


def request(method, path, body=None, token=None, auth=True, retries=4, allow_write=False):
    """Call the Printful API and return the "result" part of the response.

    Only GET is allowed unless the caller passes allow_write=True; only
    printful_create.py --apply does, after the owner's approval."""
    if not path.startswith("/"):
        raise PrintfulError(f"bad API path: {path!r}")
    if method != "GET" and not allow_write:
        raise PrintfulError(f"{method} {path}: writes are only allowed from printful_create.py --apply")
    if method != "GET":
        _require_entry_script("printful_create.py")
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = "Bearer " + (token or get_token())
        store_id = os.environ.get("PRINTFUL_STORE_ID", "").strip()
        if store_id:
            headers["X-PF-Store-Id"] = store_id
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    for attempt in range(retries + 1):
        req = urllib.request.Request(API + path, data=data, headers=headers, method=method)
        try:
            with _api_opener.open(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8")).get("result")
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < retries:
                try:
                    wait = max(0, min(int(err.headers.get("Retry-After") or 2 ** attempt), 60))
                except ValueError:  # an HTTP date instead of seconds
                    wait = 2 ** attempt
                time.sleep(wait)
                continue
            raise PrintfulError(f"{method} {path}: HTTP {err.code}: {_error_message(err)}") from None
        except urllib.error.URLError as err:
            raise PrintfulError(f"{method} {path}: {err.reason}") from None


def list_store_products(token):
    products, offset = [], 0
    while True:
        page = request("GET", f"/store/products?offset={offset}&limit=100", token=token) or []
        products.extend(page)
        if len(page) < 100:
            return products
        offset += 100


def download_image(url, dest_without_ext):
    """Download a Printful image (https, *.printful.com only). Returns the saved path."""
    if not _is_printful_host(url):
        host = urllib.parse.urlparse(url or "").hostname
        raise PrintfulError(f"refusing to download image from {host or 'an empty or non-https URL'}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with _image_opener.open(req, timeout=30) as resp:
        ext = IMAGE_TYPES.get(resp.headers.get_content_type())
        if not ext:
            raise PrintfulError(f"not a JPEG/PNG/WebP image: {url}")
        content = resp.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise PrintfulError(f"image over {MAX_IMAGE_BYTES // 1024 // 1024} MB: {url}")
    path = str(dest_without_ext) + ext
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)
    return path
