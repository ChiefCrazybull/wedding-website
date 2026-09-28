"""Parsing and naming rules for the Our Story galleries.

The three galleries under img/Our Story/ are driven by data arrays in
our-story.html (COUNTRIES, STATES, MEXICO_TRIPS).  This module reads those
arrays, works out which files on disk belong to each entry, and computes the
canonical filename for each position.  See README-adding-photos.txt.
"""

import os
import re

GALLERIES = [
    # folder name, JS array name, separator before the position number
    ("Countries", "COUNTRIES", ""),
    ("Mexico", "MEXICO_TRIPS", "_"),
    ("States", "STATES", ""),
]

GALLERY_BY_FOLDER = {g[0]: g for g in GALLERIES}

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".gif", ".tif", ".tiff", ".bmp")


# ---------------------------------------------------------------- html parsing

def _match_bracket(text, start, open_ch, close_ch):
    """Index just past the bracket that closes the one at `start`."""
    depth = 0
    i = start
    in_str = None
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
        elif ch in "\"'":
            in_str = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced %s at offset %d" % (open_ch, start))


def _split_objects(text, offset):
    """Yield (start, end) spans of the top-level { } objects inside text."""
    i = 0
    while i < len(text):
        if text[i] == "{":
            end = _match_bracket(text, i, "{", "}")
            yield (offset + i, offset + end)
            i = end
        else:
            i += 1


def _str_field(obj_text, field):
    m = re.search(r'(?:^|[ ,{])%s *: *"([^"]*)"' % field, obj_text, re.M)
    return m.group(1) if m else None


def _images_span(text, obj_start, obj_end):
    m = re.compile(r"\bimages\s*:\s*\[").search(text, obj_start, obj_end)
    if not m:
        return None
    end = _match_bracket(text, m.end() - 1, "[", "]")
    return (m.end() - 1, end)


def parse_our_story(html):
    """{folder: [entry, ...]} parsed out of our-story.html."""
    out = {}
    for folder, array_name, sep in GALLERIES:
        m = re.search(r"\bconst\s+%s\s*=\s*\[" % array_name, html)
        if not m:
            raise ValueError("could not find `const %s = [` in our-story.html" % array_name)
        arr_start = m.end() - 1
        arr_end = _match_bracket(html, arr_start, "[", "]")
        body = html[arr_start + 1:arr_end - 1]

        entries = []
        for idx, (o_start, o_end) in enumerate(_split_objects(body, arr_start + 1)):
            obj = html[o_start:o_end]
            span = _images_span(html, o_start, o_end)
            images = []
            if span:
                images = re.findall(r'"([^"]*)"', html[span[0] + 1:span[1] - 1])
            entries.append({
                "index": idx,
                "folder": folder,
                "sep": sep,
                "name": _str_field(obj, "name") or "",
                "nameEs": _str_field(obj, "nameEs") or "",
                "subtitle": _str_field(obj, "subtitle") or "",
                "filePrefix": _str_field(obj, "filePrefix"),
                "images": images,
                "obj_span": (o_start, o_end),
                "images_span": span,
            })
        out[folder] = entries
    return out


# ------------------------------------------------------------------- naming

def entry_base(entry):
    """The filename stem shared by every photo in this entry.

    States and Mexico carry it as `filePrefix`.  Countries have no such field,
    so it is recovered from the filenames themselves (the country `name` is not
    usable -- e.g. name "Bosnia &amp; Herzegovina" vs files
    "Bosnia and Herzegovina*.jpg").
    """
    if entry.get("filePrefix"):
        return entry["filePrefix"]
    counts = {}
    for img in entry["images"]:
        stem = re.sub(r"\d+$", "", os.path.splitext(img)[0])
        if stem:
            counts[stem] = counts.get(stem, 0) + 1
    if counts:
        return max(counts.items(), key=lambda kv: (kv[1], len(kv[0])))[0]
    return entry["name"].replace("&amp;", "and")


def target_name(base, sep, position, ext=".jpg"):
    """Canonical filename for a 1-based position (README sections 2 and 3)."""
    if position <= 1:
        return base + ext
    return "%s%s%d%s" % (base, sep, position, ext)


def file_position(base, sep, filename):
    """Position claimed by `filename`, or None if it does not belong to `base`.

    Mirrors the ordering the site itself applies (trailingNumByPrefix /
    trailingNumMexico): a bare `base.jpg` is 0, `base<n>.jpg` is n.  Returning
    0 for the bare name is what keeps the off-pattern `Ireland.jpg` +
    `Ireland1.jpg` and `trip3.jpg` + `trip3_1.jpg` pairs in the right order.
    """
    stem, ext = os.path.splitext(filename)
    if ext.lower() not in IMAGE_EXTS:
        return None
    if stem.lower() == base.lower():
        return 0
    if not stem.lower().startswith(base.lower()):
        return None
    rest = stem[len(base):]
    if sep:
        if not rest.startswith(sep):
            return None
        rest = rest[len(sep):]
    if rest.isdigit():
        return int(rest)
    return None


def scan_folder(folder_path, entries):
    """Map each image file in a folder to the entry whose base matches best.

    Longest base wins, so an entry whose base is a prefix of another entry's
    cannot steal its files.  Returns {entry_index: [(position, filename), ...]}
    sorted into display order.
    """
    bases = sorted(
        ((entry_base(e), e["index"], e["sep"]) for e in entries),
        key=lambda t: -len(t[0]),
    )
    hits = {e["index"]: [] for e in entries}
    try:
        names = os.listdir(folder_path)
    except OSError:
        names = []
    for name in sorted(names):
        if not os.path.isfile(os.path.join(folder_path, name)):
            continue
        for base, idx, sep in bases:
            pos = file_position(base, sep, name)
            if pos is not None:
                hits[idx].append((pos, name))
                break
    for idx in hits:
        hits[idx].sort(key=lambda t: (t[0], t[1]))
    return hits
