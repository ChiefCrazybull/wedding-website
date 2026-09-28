"""Our Story photo manager -- a small local web app.

Launch it with photo-manager.bat (or `python _tool/photo_manager.py`) from
img/Our Story/.  It serves a page on 127.0.0.1 that lists the Countries,
Mexico and States galleries, shows one trip's photos in their real display
order, and lets you add, delete and drag-reorder them.  Saving renames the
files to the canonical numbering, archives originals in img_backup, and
updates the images array in our-story.html.

Standard library only.  The JPEG resizing and compression happens in the
browser (canvas), so there is nothing to install.
"""

import base64
import io
import json
import mimetypes
import os
import secrets
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import country_codes as CC        # noqa: E402
import gallery_data as G          # noqa: E402
import save_engine as S           # noqa: E402

# _tool -> Our Story -> img -> repo root
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TOKEN = secrets.token_urlsafe(24)
MAX_BODY = 512 * 1024 * 1024      # a save can carry several full-size originals
IDLE_TIMEOUT = 40                 # seconds without a heartbeat before shutting down

_heartbeat = {"seen": False, "at": 0.0}


def watchdog(httpd):
    """Exit once the page stops checking in, so closing the tab closes the tool.

    Reloading the page only pauses the heartbeat for a moment, so a refresh
    does not take the server down with it.
    """
    while True:
        time.sleep(5)
        if _heartbeat["seen"] and time.time() - _heartbeat["at"] > IDLE_TIMEOUT:
            print("browser tab closed; shutting down.", flush=True)
            httpd.shutdown()
            return


def repo_sanity_check():
    missing = [p for p in ("our-story.html", os.path.join("img", "Our Story"))
               if not os.path.exists(os.path.join(ROOT, p))]
    if missing:
        raise SystemExit(
            "This does not look like the wedding-website repo.\n"
            "Expected to find %s under %s\n"
            "Run the tool from img/Our Story/ inside the repo."
            % (" and ".join(missing), ROOT))


# --------------------------------------------------------------------- the API

def api_galleries():
    html = S.load_html(ROOT)
    data = G.parse_our_story(html)
    badges = S.badge_report(ROOT)
    out = []
    for folder, _array, _sep in G.GALLERIES:
        entries = data[folder]
        hits = G.scan_folder(S.img_dir(ROOT, folder), entries)
        items = []
        for e in entries:
            items.append({
                "index": e["index"],
                "name": e["name"],
                "nameEs": e["nameEs"],
                "subtitle": e["subtitle"],
                "base": G.entry_base(e),
                "count": len(hits[e["index"]]),
            })
        out.append({
            "folder": folder,
            "entries": items,
            "badge": badges[folder],
            "newDefaults": S.new_entry_defaults(ROOT, folder),
        })
    return {
        "galleries": out,
        "flags": S.list_flags(ROOT),
        "countryFlags": CC.lookup_table(),
    }


def api_validate_new(body):
    """Check a draft entry's fields without writing anything."""
    folder = body.get("folder")
    fields = body.get("fields") or {}
    clean = S.validate_new_entry(ROOT, folder, fields)
    entry = S.draft_entry(folder, clean)
    base = G.entry_base(entry)
    sep = entry["sep"]
    return {
        "fields": clean,
        "base": base,
        "sep": sep,
        "sampleNames": [G.target_name(base, sep, i) for i in (1, 2, 3)],
        "line": S.render_entry(folder, clean, [G.target_name(base, sep, 1)]),
    }


def api_entry(folder, index):
    _html, _entries, entry = S.find_entry(ROOT, folder, index)
    info = S.describe_entry(ROOT, folder, entry)
    info["newFolder"] = [
        {"file": n, "bytes": os.path.getsize(os.path.join(S.new_dir(ROOT, folder), n))}
        for n in S.list_files(S.new_dir(ROOT, folder))
        if os.path.splitext(n)[1].lower() in G.IMAGE_EXTS
    ]
    return info


def _plan_from_body(body):
    folder = body["folder"]
    if body.get("newEntry"):
        # A draft the browser is holding; validated again here so the checks are
        # against the file as it is right now, not as it was when the form opened.
        clean = S.validate_new_entry(ROOT, folder, body["newEntry"])
        entry = S.draft_entry(folder, clean)
    else:
        index = int(body["entryIndex"])
        _html, _entries, entry = S.find_entry(ROOT, folder, index, body.get("entryName"))
    uploads = body.get("uploads") or {}
    meta = {k: {mk: mv for mk, mv in v.items() if mk not in ("compressed", "original")}
            for k, v in uploads.items()}
    plan = S.compute_plan(ROOT, folder, entry, body.get("items") or [], meta)
    return plan, uploads


def api_plan(body):
    plan, _uploads = _plan_from_body(body)
    plan.pop("items", None)
    return plan


def api_save(body):
    plan, uploads = _plan_from_body(body)
    payloads = {}
    for uid, u in uploads.items():
        try:
            compressed = base64.b64decode(u["compressed"], validate=True)
            original = base64.b64decode(u["original"], validate=True)
        except Exception as exc:
            raise S.SaveError("could not decode the upload for %s: %s"
                              % (u.get("origName") or uid, exc))
        if not compressed:
            raise S.SaveError("the compressed image for %s came through empty"
                              % (u.get("origName") or uid))
        payloads[uid] = (compressed, original or compressed)
    result = S.apply_plan(ROOT, plan, payloads)
    index = plan["entryIndex"]
    if index is None:
        # A newly created entry: find where it landed in the array.
        entries = G.parse_our_story(S.load_html(ROOT))[plan["folder"]]
        matches = [e["index"] for e in entries if e["name"] == plan["entryName"]]
        if not matches:
            raise S.SaveError("the files were written but %s could not be found in "
                              "our-story.html afterwards" % plan["entryName"])
        index = matches[0]
        result["created"] = True
    result["entry"] = api_entry(plan["folder"], index)
    return result


def api_file(folder, which, name):
    """Bytes of one gallery photo, for the thumbnails."""
    if folder not in G.GALLERY_BY_FOLDER:
        raise ValueError("unknown gallery %r" % folder)
    roots = {
        "img": S.img_dir(ROOT, folder),
        "new": S.new_dir(ROOT, folder),
        "flags": S.flags_dir(ROOT),
    }
    if which not in roots:
        raise ValueError("unknown source %r" % which)
    base_dir = roots[which]
    # Reject anything that is not a plain filename directly inside base_dir.
    if name != os.path.basename(name) or name in ("", ".", ".."):
        raise ValueError("bad filename")
    path = os.path.join(base_dir, name)
    if os.path.commonpath([os.path.realpath(path), os.path.realpath(base_dir)]) != \
            os.path.realpath(base_dir):
        raise ValueError("bad filename")
    if not os.path.isfile(path):
        raise FileNotFoundError(name)
    with open(path, "rb") as f:
        return f.read(), mimetypes.guess_type(name)[0] or "application/octet-stream"


# ------------------------------------------------------------------ the server

class Handler(BaseHTTPRequestHandler):
    server_version = "OurStoryPhotoManager/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        if "/api/save" in (args[0] if args else ""):
            sys.stderr.write("  %s\n" % (fmt % args))

    # -- plumbing ----------------------------------------------------------
    def _send(self, code, body, content_type, extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def _authorised(self, query):
        supplied = (self.headers.get("X-PM-Token")
                    or (query.get("token") or [None])[0])
        return supplied is not None and secrets.compare_digest(supplied, TOKEN)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ValueError("request body too large (%d bytes)" % length)
        chunks, remaining = [], length
        while remaining > 0:
            chunk = self.rfile.read(min(remaining, 1 << 20))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        return json.loads(b"".join(chunks).decode("utf-8") or "{}")

    # -- routes ------------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)

        if path in ("/", "/index.html"):
            with io.open(os.path.join(HERE, "ui.html"), encoding="utf-8") as f:
                page = f.read().replace("__PM_TOKEN__", TOKEN)
            return self._send(200, page, "text/html; charset=utf-8")

        if not path.startswith("/api/"):
            return self._send(404, "not found", "text/plain; charset=utf-8")
        if not self._authorised(query):
            return self._json(403, {"error": "bad or missing session token"})

        try:
            if path == "/api/galleries":
                return self._json(200, api_galleries())
            if path == "/api/entry":
                return self._json(200, api_entry(
                    (query.get("folder") or [""])[0],
                    int((query.get("index") or ["-1"])[0])))
            if path == "/api/file":
                data, ctype = api_file((query.get("folder") or [""])[0],
                                       (query.get("src") or ["img"])[0],
                                       unquote((query.get("name") or [""])[0]))
                return self._send(200, data, ctype)
        except FileNotFoundError as exc:
            return self._json(404, {"error": "no such file: %s" % exc})
        except (S.SaveError, ValueError) as exc:
            return self._json(400, {"error": str(exc)})
        except Exception as exc:
            traceback.print_exc()
            return self._json(500, {"error": "%s: %s" % (type(exc).__name__, exc)})

        return self._json(404, {"error": "unknown endpoint %s" % path})

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)
        if not self._authorised(query):
            return self._json(403, {"error": "bad or missing session token"})

        try:
            if path == "/api/ping":
                _heartbeat["seen"] = True
                _heartbeat["at"] = time.time()
                return self._json(200, {"ok": True})
            if path == "/api/shutdown":
                self._json(200, {"ok": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            body = self._read_body()
            if path == "/api/validatenew":
                return self._json(200, api_validate_new(body))
            if path == "/api/plan":
                return self._json(200, api_plan(body))
            if path == "/api/save":
                print("  saving %s / %s ..." % (body.get("folder"), body.get("entryName")), flush=True)
                result = api_save(body)
                for line in result["log"]:
                    print("    " + line, flush=True)
                return self._json(200, result)
        except S.SaveError as exc:
            print("  SAVE FAILED: %s" % exc, flush=True)
            return self._json(400, {"error": str(exc)})
        except (ValueError, KeyError) as exc:
            traceback.print_exc()
            return self._json(400, {"error": "%s: %s" % (type(exc).__name__, exc)})
        except Exception as exc:
            traceback.print_exc()
            return self._json(500, {"error": "%s: %s" % (type(exc).__name__, exc)})

        return self._json(404, {"error": "unknown endpoint %s" % path})


def main():
    repo_sanity_check()
    no_browser = "--no-browser" in sys.argv
    port = 0
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    httpd.daemon_threads = True
    host, bound = httpd.socket.getsockname()[:2]
    url = "http://%s:%d/?token=%s" % (host, bound, TOKEN)

    print("Our Story photo manager", flush=True)
    print("  repo: %s" % ROOT, flush=True)
    print("  url:  %s" % url, flush=True)
    print("  Close the browser tab (or press Ctrl+C here) to stop.", flush=True)
    print()
    if no_browser:
        print("  --no-browser given; open the url above yourself.", flush=True)
    else:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()
        threading.Thread(target=watchdog, args=(httpd,), daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        try:
            input("\nSomething went wrong. Press Enter to close.")
        except EOFError:
            pass
