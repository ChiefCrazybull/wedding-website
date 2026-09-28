"""Commit and push, from the tool, the gallery changes it has saved.

Only what the tool itself writes is ever committed: our-story.html and the
three gallery folders (minus their New/ drop boxes). Anything else changed in
the repo is reported but left alone for committing by hand. The browser is
shown the exact file list first and sends it back with the commit request;
if the working tree no longer matches that list, nothing is committed.
"""

import os
import shutil
import subprocess

import gallery_data as G

GALLERY_ROOT = "img/Our Story"
SCOPE = ["our-story.html"] + ["%s/%s" % (GALLERY_ROOT, g[0]) for g in G.GALLERIES]
EXCLUDE = [":(exclude,glob)%s/*/New/**" % GALLERY_ROOT,
           ":(exclude,glob)%s/*/.pm-stage-*/**" % GALLERY_ROOT]

PUSH_TIMEOUT = 180


class GitError(Exception):
    pass


def available():
    return shutil.which("git") is not None


def _git(root, *args, stdin=None, check=True, timeout=60):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")   # never hang on a password prompt
    try:
        p = subprocess.run(
            ["git"] + list(args), cwd=root, input=stdin, capture_output=True,
            env=env, timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        raise GitError("git %s took too long and was stopped" % args[0])
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace").strip()
    if check and p.returncode:
        raise GitError(err or out.strip() or "git %s failed" % args[0])
    return p.returncode, out, err


def _porcelain(root, pathspecs):
    """[(xy, path)] from `git status -z`; a rename reports its new path."""
    _rc, out, _err = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                          "--", *pathspecs)
    parts = out.split("\0")
    entries, i = [], 0
    while i < len(parts):
        rec = parts[i]
        i += 1
        if len(rec) < 4:
            continue
        xy, path = rec[:2], rec[3:]
        if "R" in xy or "C" in xy:
            i += 1                                    # skip the old path
        entries.append((xy, path))
    return entries


def _kind(xy):
    if xy == "??" or "A" in xy:
        return "added"
    if "D" in xy:
        return "deleted"
    return "changed"


def _entry_for(path, bases):
    """'California' for img/Our Story/States/California12.jpg, else None."""
    parts = path.split("/")
    if len(parts) != 4 or "/".join(parts[:2]) != GALLERY_ROOT:
        return None
    for base, name, sep in bases.get(parts[2], []):
        if G.file_position(base, sep, parts[3]) is not None:
            return name
    return None


def _bases(root):
    """{folder: [(base, display name, sep)]}, longest base first."""
    try:
        with open(os.path.join(root, "our-story.html"), encoding="utf-8") as f:
            data = G.parse_our_story(f.read())
    except (OSError, ValueError):
        return {}
    out = {}
    for folder, entries in data.items():
        rows = [(G.entry_base(e), e["name"].replace("&amp;", "&"), e["sep"]) for e in entries]
        out[folder] = sorted(rows, key=lambda r: -len(r[0]))
    return out


def status(root):
    """What a commit from the tool would contain, plus branch/push state."""
    if not available():
        return {"available": False,
                "reason": "git is not installed or not on PATH, so the tool cannot commit."}
    try:
        _git(root, "rev-parse", "--is-inside-work-tree")
    except GitError:
        return {"available": False, "reason": "this folder is not a git repository."}

    files = [{"path": p, "kind": _kind(xy)} for xy, p in _porcelain(root, SCOPE + EXCLUDE)]
    ours = {f["path"] for f in files}
    others = [p for _xy, p in _porcelain(root, ["."]) if p not in ours]

    bases = _bases(root)
    groups = {}
    for f in files:
        if f["path"].startswith(GALLERY_ROOT + "/"):
            label = _entry_for(f["path"], bases) or f["path"].split("/")[2]
        else:
            label = f["path"]
        f["group"] = label
        g = groups.setdefault(label, {"name": label, "added": 0, "changed": 0, "deleted": 0})
        g[f["kind"]] += 1

    _rc, branch, _err = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    rc, ahead, _err = _git(root, "rev-list", "--count", "@{u}..HEAD", check=False)
    return {
        "available": True,
        "branch": branch.strip(),
        "hasUpstream": rc == 0,
        "ahead": int(ahead.strip() or 0) if rc == 0 else 0,
        "files": files,
        "groups": list(groups.values()),
        "otherChanges": len(others),
        "suggestedMessage": suggested_message(groups),
    }


def suggested_message(groups):
    names = [n for n in groups if n != "our-story.html"]
    if not names:
        return "Update Our Story page" if groups else ""
    if len(names) > 4:
        return "Update Our Story photos: %s and %d more" % (", ".join(names[:3]), len(names) - 3)
    return "Update Our Story photos: " + ", ".join(names)


def commit_and_push(root, message, expected_paths):
    """Commit exactly `expected_paths` (if any) and push. Returns what happened."""
    st = status(root)
    if not st["available"]:
        raise GitError(st["reason"])
    paths = [f["path"] for f in st["files"]]
    if sorted(paths) != sorted(expected_paths or []):
        raise GitError("The files changed since you opened this window. Close it and press "
                       "Commit again to see the current list.")

    committed = None
    if paths:
        message = (message or "").strip()
        if not message:
            raise GitError("Write a short commit message first.")
        spec = "\0".join(paths).encode("utf-8")
        # Literal pathspecs so names with spaces or brackets mean just that file,
        # and fed over stdin so a big batch cannot overflow the command line.
        _git(root, "--literal-pathspecs", "add", "-A",
             "--pathspec-from-file=-", "--pathspec-file-nul", stdin=spec)
        # With paths given, commit takes only these -- anything else that happens
        # to be staged stays staged and out of this commit.
        _git(root, "--literal-pathspecs", "commit", "-q", "-m", message,
             "--pathspec-from-file=-", "--pathspec-file-nul", stdin=spec)
        _rc, sha, _err = _git(root, "rev-parse", "--short", "HEAD")
        committed = sha.strip()
    elif not st["ahead"]:
        raise GitError("There is nothing to commit or push.")

    args = ["push"] if st["hasUpstream"] else ["push", "-u", "origin", st["branch"]]
    rc, _out, err = _git(root, *args, check=False, timeout=PUSH_TIMEOUT)
    if rc:
        hint = ""
        if "rejected" in err or "fetch first" in err or "non-fast-forward" in err:
            hint = ("GitHub has changes this computer does not have yet. Pull them first "
                    "(GitHub Desktop: Fetch, then Pull), then press Push here.")
        elif "Authentication" in err or "could not read Username" in err or "403" in err:
            hint = "GitHub did not accept the sign-in. Push once from GitHub Desktop or a terminal."
        return {"committed": committed, "pushed": False, "error": err, "hint": hint,
                "count": len(paths)}
    return {"committed": committed, "pushed": True, "count": len(paths)}
