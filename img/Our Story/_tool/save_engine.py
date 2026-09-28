"""Work out and apply the file changes for one Our Story gallery entry.

Everything that touches the filesystem lives here.  A save is planned first
(`compute_plan`, which writes nothing and drives the preview panel) and then
applied (`apply_plan`).  The apply is staged through a scratch directory inside
the same folder so rename cycles are safe, and every move is recorded so a
failure part-way through can be rolled back.
"""

import io
import os
import re
import shutil
import time
import unicodedata

import gallery_data as G
import photo_meta as M

STAGE_PREFIX = ".pm-stage-"
TRASH_DIRNAME = "_deleted"
UNMATCHED_DIRNAME = "_unmatched"

# Column at which each field starts on an existing array line, so an inserted
# entry lines up with its neighbours. Measured from our-story.html; a value that
# overruns its column just falls back to a single space, which is what a few of
# the existing long lines already do.
ENTRY_COLUMNS = {
    "Countries": [("name", 8), ("nameEs", 39), ("flag", 76), ("images", 88)],
    "States": [("name", 8), ("nameEs", 34), ("flag", 63), ("flagImg", 75),
               ("filePrefix", 126), ("images", 156)],
}

# The three "N and counting" badges, keyed by the heading each one follows.
COUNT_BADGE_HEADING = {
    "Countries": "os-countries-h2",
    "Mexico": "os-mexico-h2",
    "States": "os-states-h2",
}


class SaveError(Exception):
    pass


# ------------------------------------------------------------------- helpers

def img_dir(root, folder):
    return os.path.join(root, "img", "Our Story", folder)


def backup_dir(root, folder):
    return os.path.join(root, "img_backup", "Our Story", folder)


def new_dir(root, folder):
    return os.path.join(root, "img", "Our Story", folder, "New")


def list_files(path):
    try:
        return sorted(n for n in os.listdir(path)
                      if os.path.isfile(os.path.join(path, n)))
    except OSError:
        return []


def unique_path(directory, filename):
    """A path in `directory` that does not exist yet, based on `filename`."""
    stem, ext = os.path.splitext(filename)
    candidate = os.path.join(directory, filename)
    n = 1
    while os.path.exists(candidate):
        candidate = os.path.join(directory, "%s-%d%s" % (stem, n, ext))
        n += 1
    return candidate


def safe_ext(name, default=".jpg"):
    ext = os.path.splitext(name or "")[1].lower()
    return ext if ext else default


def load_html(root):
    with io.open(os.path.join(root, "our-story.html"), encoding="utf-8", newline="") as f:
        return f.read()


def line_ending(text):
    """The newline the file already uses (our-story.html is entirely CRLF)."""
    return "\r\n" if "\r\n" in text else "\n"


def encode_html_text(value):
    """Turn what was typed into the entity style already used in the arrays.

    Idempotent: a draft is validated once when the form is submitted and again
    when it is saved, so escaping an already-escaped entity would turn
    `&amp;` into `&amp;amp;`. An `&` that already begins an entity is left be.
    """
    text = (value or "").strip()
    text = re.sub(r"&(?![A-Za-z][A-Za-z0-9]*;|#\d+;|#x[0-9A-Fa-f]+;)", "&amp;", text)
    # A middle dot separates the parts of a Mexico subtitle, always spaced.
    text = re.sub(r"\s*[·•]\s*", " &middot; ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def decode_html_text(value):
    """Inverse of encode_html_text, for showing stored text back in a form."""
    text = (value or "").replace("&middot;", "·")
    return text.replace("&amp;", "&")


def default_base(name):
    """The filename stem a new state/country should use, from its English name.

    Follows the existing data: ampersands spell out ("Bosnia &amp; Herzegovina"
    -> "Bosnia and Herzegovina.jpg") and accents are dropped, since every
    filename in these folders is plain ASCII.
    """
    text = (name or "").replace("&amp;", " and ").replace("&", " and ")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^A-Za-z0-9 ]", "", text)
    return " ".join(text.split())


def find_entry(root, folder, entry_index, expected_name=None):
    html = load_html(root)
    data = G.parse_our_story(html)
    if folder not in data:
        raise SaveError("unknown gallery folder %r" % folder)
    entries = data[folder]
    if not (0 <= entry_index < len(entries)):
        raise SaveError("entry index %d out of range for %s" % (entry_index, folder))
    entry = entries[entry_index]
    if expected_name is not None and entry["name"] != expected_name:
        raise SaveError(
            "our-story.html changed underneath the tool: expected %r at index %d "
            "of %s but found %r. Reload the tool and try again."
            % (expected_name, entry_index, folder, entry["name"]))
    return html, entries, entry


# ------------------------------------------------------------------ planning

# --------------------------------------------------- creating a new entry

def next_trip_number(entries):
    """One past the highest tripN in MEXICO_TRIPS (trip8 today -> 9)."""
    highest = 0
    for e in entries:
        m = re.match(r"trip(\d+)$", e.get("filePrefix") or "")
        if m:
            highest = max(highest, int(m.group(1)))
    return highest + 1


def new_entry_defaults(root, folder):
    """What the New... form should start out holding."""
    html = load_html(root)
    entries = G.parse_our_story(html)[folder]
    if folder == "Mexico":
        n = next_trip_number(entries)
        return {
            "tripNumber": n,
            "name": "Trip %d" % n,
            "nameEs": "Viaje %d" % n,
            "filePrefix": "trip%d" % n,
            "subtitle": "",
            "subtitleEs": "",
        }
    return {"name": "", "nameEs": "", "flag": "", "flagImg": "", "filePrefix": ""}


def draft_entry(folder, fields):
    """A synthetic entry dict that compute_plan/describe_entry can work with.

    Shaped exactly like one from G.parse_our_story, minus the source spans,
    because a draft is not in our-story.html yet.
    """
    sep = G.GALLERY_BY_FOLDER[folder][2]
    return {
        "index": None,
        "folder": folder,
        "sep": sep,
        "name": fields.get("name") or "",
        "nameEs": fields.get("nameEs") or "",
        "subtitle": fields.get("subtitle") or "",
        # Countries carry no filePrefix in the array; the draft still needs one
        # so entry_base can resolve a stem with no images to learn it from.
        "filePrefix": fields.get("filePrefix") or "",
        "images": [],
        "obj_span": None,
        "images_span": None,
        "isNew": True,
        "newFields": dict(fields),
    }


def validate_new_entry(root, folder, fields):
    """Reject a draft that would clash with what is already there.

    Returns the cleaned field dict (entities applied, base defaulted).
    """
    if folder not in G.GALLERY_BY_FOLDER:
        raise SaveError("unknown gallery %r" % folder)

    html = load_html(root)
    entries = G.parse_our_story(html)[folder]

    clean = dict(fields)
    if folder == "Mexico":
        n = next_trip_number(entries)
        clean["name"] = "Trip %d" % n
        clean["nameEs"] = "Viaje %d" % n
        clean["filePrefix"] = "trip%d" % n
        clean["subtitle"] = encode_html_text(fields.get("subtitle"))
        clean["subtitleEs"] = encode_html_text(fields.get("subtitleEs"))
        if not clean["subtitle"] or not clean["subtitleEs"]:
            raise SaveError("a Mexico trip needs both the English and the Spanish "
                            "subtitle - they are shown under the trip name")
    else:
        clean["name"] = encode_html_text(fields.get("name"))
        clean["nameEs"] = encode_html_text(fields.get("nameEs"))
        if not clean["name"]:
            raise SaveError("the English name is required")
        if not clean["nameEs"]:
            raise SaveError("the Spanish name is required - the list is sorted by it, "
                            "so leaving it blank changes where this appears in Spanish "
                            "(repeat the English name if they are the same)")
        clean["filePrefix"] = (fields.get("filePrefix") or "").strip() \
            or default_base(clean["name"])
        if not re.match(r"^[A-Za-z0-9][A-Za-z0-9 ]*$", clean["filePrefix"]):
            raise SaveError("the filename prefix %r should be plain letters, digits and "
                            "spaces - every photo in these folders is named that way"
                            % clean["filePrefix"])
        if folder == "States":
            if not (clean.get("flagImg") or clean.get("flag")):
                raise SaveError("pick a flag image, or switch to an emoji flag")
            if clean.get("flagImg"):
                flag_path = os.path.join(flags_dir(root), clean["flagImg"])
                if not os.path.isfile(flag_path):
                    raise SaveError("%s is not in States/Flags" % clean["flagImg"])
                clean["flag"] = ""
            else:
                clean["flagImg"] = ""
        else:
            clean["flag"] = (fields.get("flag") or "").strip()
            clean["flagImg"] = ""

    # Nothing may collide with an existing entry.
    base = clean["filePrefix"]
    for e in entries:
        if e["name"].lower() == clean["name"].lower():
            raise SaveError("%s is already in the %s list" % (clean["name"], folder))
        if clean["nameEs"] and e["nameEs"].lower() == clean["nameEs"].lower():
            raise SaveError("the Spanish name %r is already used by %s"
                            % (clean["nameEs"], e["name"]))
        if G.entry_base(e).lower() == base.lower():
            raise SaveError("%s already names its photos %s*.jpg - pick a different "
                            "filename prefix" % (e["name"], base))

    # And no stray files may already be sitting where its photos will go.
    probe = draft_entry(folder, clean)
    probe["index"] = -1
    existing = G.scan_folder(img_dir(root, folder), entries + [probe]).get(-1) or []
    if existing:
        raise SaveError("%s already contains %s - move or delete %s before creating "
                        "this entry" % (folder, ", ".join(n for _, n in existing[:5]),
                                        "them" if len(existing) > 1 else "it"))
    return clean


def flags_dir(root):
    return os.path.join(root, "img", "Our Story", "States", "Flags")


def list_flags(root):
    """Every flag PNG in States/Flags, noting which states already use one."""
    html = load_html(root)
    entries = G.parse_our_story(html)["States"]
    used = {}
    for e in entries:
        m = re.search(r'flagImg:\s*"([^"]*)"', html[e["obj_span"][0]:e["obj_span"][1]])
        if m and m.group(1):
            used[m.group(1)] = e["name"]
    out = []
    for name in sorted(list_files(flags_dir(root))):
        if os.path.splitext(name)[1].lower() in (".png", ".jpg", ".jpeg", ".svg", ".webp"):
            out.append({"file": name, "usedBy": used.get(name)})
    return out


def suggest_flag(state_name, flags):
    """The flag file whose name matches the state, if there is one."""
    slug = re.sub(r"[^a-z0-9]+", "-", default_base(state_name).lower()).strip("-")
    if not slug:
        return ""
    names = [f["file"] for f in flags]
    for candidate in ("%s-flag-icon-256.png" % slug, "%s.png" % slug):
        if candidate in names:
            return candidate
    for f in names:
        if f.startswith(slug + "-") or f.startswith(slug + "."):
            return f
    return ""


def backups_by_position(root, folder, base, sep):
    """{position: [backup filename, ...]} for one entry, any extension."""
    out = {}
    for name in list_files(backup_dir(root, folder)):
        pos = G.file_position(base, sep, name)
        if pos is not None:
            out.setdefault(pos, []).append(name)
    return out


def taken_for(root, folder, site_path, backups):
    """Capture time for a gallery photo, or None.

    The site copy has had its EXIF stripped by compression, so look at the
    archived original(s) first and only fall back to the site file.
    """
    for name in backups:
        got = M.taken_at(os.path.join(backup_dir(root, folder), name))
        if got:
            return got
    return M.taken_at(site_path)


def crop_source(root, folder, site_size, backups):
    """The archived original to crop from, when it is the same picture.

    The site copy is capped at 1400px, so cropping a portrait one to 4:3 would
    leave a 1050x788 photo; the full-size original gives a proper 1400x1050.
    It only counts if its shape matches the site copy -- a photo that was
    already cropped by hand before archiving must not come back uncropped --
    and if a browser can decode it.
    """
    if not site_size:
        return None
    ratio = site_size[0] / site_size[1]
    for name in backups:
        if safe_ext(name) not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        size = M.image_size(os.path.join(backup_dir(root, folder), name))
        if size and size[0] >= site_size[0] and abs(size[0] / size[1] / ratio - 1) <= 0.01:
            return name
    return None


def off_ratio_count(root, folder, names):
    """How many of these gallery files are not landscape 4:3."""
    return sum(1 for n in names
               if not M.is_four_three(M.image_size(os.path.join(img_dir(root, folder), n))))


def describe_entry(root, folder, entry):
    """Current state of one entry: ordered files plus any inconsistencies."""
    base = G.entry_base(entry)
    sep = entry["sep"]
    hits = G.scan_folder(img_dir(root, folder), [entry])[entry["index"]]
    disk = [{"file": name, "position": pos} for pos, name in hits]
    names = [d["file"] for d in disk]
    canonical = [G.target_name(base, sep, i + 1) for i in range(len(names))]
    bk = backups_by_position(root, folder, base, sep)

    for d in disk:
        d["inArray"] = d["file"] in entry["images"]
        d["backups"] = bk.get(d["position"], [])
        full = os.path.join(img_dir(root, folder), d["file"])
        try:
            d["bytes"] = os.path.getsize(full)
        except OSError:
            d["bytes"] = 0
        d["taken"] = taken_for(root, folder, full, d["backups"])
        size = M.image_size(full)
        d["width"], d["height"] = size or (None, None)
        d["is43"] = M.is_four_three(size)
        d["cropSource"] = crop_source(root, folder, size, d["backups"])

    warnings = []
    if names != canonical:
        warnings.append({
            "kind": "numbering",
            "text": "Filenames do not follow the standard numbering "
                    "(%s ... %s). Saving will renumber them."
                    % (canonical[0], canonical[-1]),
        })
    missing = [i for i in entry["images"] if i not in names]
    if missing:
        warnings.append({
            "kind": "missing",
            "text": "Listed in our-story.html but not on disk: " + ", ".join(missing),
        })
    extra = [n for n in names if n not in entry["images"]]
    if extra:
        warnings.append({
            "kind": "extra",
            "text": "On disk but missing from our-story.html (shown below, saving "
                    "will add them): " + ", ".join(extra),
        })
    no_backup = [d["file"] for d in disk if not d["backups"]]
    if no_backup:
        warnings.append({
            "kind": "nobackup",
            "text": "No original in img_backup for: " + ", ".join(no_backup),
        })

    return {
        "folder": folder,
        "index": entry["index"],
        "name": entry["name"],
        "nameEs": entry["nameEs"],
        "subtitle": entry["subtitle"],
        "base": base,
        "sep": sep,
        "array": entry["images"],
        "photos": disk,
        "warnings": warnings,
    }


def compute_plan(root, folder, entry, items, uploads):
    """Every file action a save would perform. Touches nothing on disk.

    `items` is the ordered list the UI holds: {"kind": "existing", "file": ...}
    or {"kind": "new", "id": ...}.  `uploads` maps a new item's id to its
    metadata (origName, size, dims, quality, fromNew).
    """
    base = G.entry_base(entry)
    sep = entry["sep"]
    folder_img = img_dir(root, folder)

    hits = G.scan_folder(folder_img, [entry])[entry["index"]]
    pos_of = {name: pos for pos, name in hits}
    on_disk = set(pos_of)

    if not items:
        if entry.get("isNew"):
            raise SaveError("add at least one photo before saving - an entry with no "
                            "photos would show up as an empty cell on the page")
        raise SaveError("an entry needs at least one photo -- delete the whole "
                        "entry by hand if that is really what you want")

    seen = set()
    for it in items:
        if it.get("kind") == "existing":
            f = it.get("file")
            if f not in on_disk:
                raise SaveError("%s is no longer in %s on disk -- reload the tool" % (f, folder))
            if f in seen:
                raise SaveError("%s appears twice in the new order" % f)
            if os.path.splitext(f)[1].lower() != ".jpg":
                raise SaveError("%s is not a .jpg -- convert it by hand first "
                                "(README section 1)" % f)
            if it.get("replace") and it["replace"] not in uploads:
                raise SaveError("missing the cropped image for %s" % f)
            seen.add(f)
        elif it.get("kind") == "new":
            if it.get("id") not in uploads:
                raise SaveError("missing upload data for new photo %r" % it.get("id"))
        else:
            raise SaveError("unknown item kind %r" % it.get("kind"))

    kept = [it["file"] for it in items if it.get("kind") == "existing"]
    deleted = [name for _, name in hits if name not in set(kept)]

    bk = backups_by_position(root, folder, base, sep)
    keeper_positions = {pos_of[f] for f in kept}
    deleted_positions = {pos_of[f] for f in deleted}

    renames, adds, replaced = [], [], []
    backup_renames, backup_adds, missing_backups = [], [], []

    for i, it in enumerate(items, 1):
        target = G.target_name(base, sep, i)
        if it["kind"] == "existing":
            old = it["file"]
            renames.append({"from": old, "to": target, "changed": old != target})
            if it.get("replace"):
                meta = uploads[it["replace"]]
                replaced.append({
                    "from": old, "to": target,
                    "bytes": meta.get("bytes") or 0,
                    "width": meta.get("width"),
                    "height": meta.get("height"),
                })
            old_pos = pos_of[old]
            found = bk.get(old_pos, [])
            if not found:
                missing_backups.append(old)
            for b in found:
                b_target = G.target_name(base, sep, i, ext=safe_ext(b))
                backup_renames.append({"from": b, "to": b_target, "changed": b != b_target})
        else:
            meta = uploads[it["id"]]
            adds.append({
                "to": target,
                "source": meta.get("origName") or "(dropped file)",
                "bytes": meta.get("bytes") or 0,
                "width": meta.get("width"),
                "height": meta.get("height"),
                "quality": meta.get("quality"),
                "fromNew": meta.get("fromNew"),
                "id": it["id"],
            })
            backup_adds.append({
                "to": G.target_name(base, sep, i, ext=safe_ext(meta.get("origName"))),
                "source": meta.get("origName") or "(dropped file)",
                "bytes": meta.get("originalBytes") or 0,
                "id": it["id"],
            })

    backup_deletes = []
    for d in deleted:
        for b in bk.get(pos_of[d], []):
            backup_deletes.append(b)

    # Backups with no counterpart in img/ are left alone, unless they sit at a
    # position the new layout now occupies -- then they are stale leftovers
    # (img_backup/.../New York22.jpg is one today) and step aside rather than
    # being mistaken for the original of whatever lands there.
    occupied = {0} | set(range(2, len(items) + 1))
    unmatched = []
    for pos, names in sorted(bk.items()):
        if pos in keeper_positions or pos in deleted_positions:
            continue
        if pos in occupied:
            unmatched.extend(names)

    new_array = [G.target_name(base, sep, i) for i in range(1, len(items) + 1)]

    return {
        "folder": folder,
        "entryIndex": entry["index"],
        "entryName": entry["name"],
        "base": base,
        "sep": sep,
        "items": items,
        "renames": renames,
        "adds": adds,
        "replaced": replaced,
        "deletes": deleted,
        "backupRenames": backup_renames,
        "backupAdds": backup_adds,
        "backupDeletes": backup_deletes,
        "backupUnmatched": unmatched,
        "missingBackups": missing_backups,
        "oldArray": list(entry["images"]),
        "newArray": new_array,
        "arrayChanged": list(entry["images"]) != new_array,
        "fileChanges": (sum(1 for r in renames if r["changed"])
                        + len(adds) + len(replaced) + len(deleted)),
        "newEntry": entry.get("newFields") if entry.get("isNew") else None,
        "entryLine": (render_entry(folder, entry["newFields"], new_array)
                      if entry.get("isNew") else None),
    }


# ------------------------------------------------------------------- applying

class _Txn:
    """Records filesystem moves so they can be undone if a later step fails."""

    def __init__(self):
        self.moves = []      # (src, dst) already performed
        self.created = []    # paths written from scratch
        self.dirs = []       # scratch dirs to remove on success
        self.html = None     # (path, previous text)

    def move(self, src, dst):
        os.replace(src, dst)
        self.moves.append((src, dst))

    def write(self, path, data):
        with open(path, "wb") as f:
            f.write(data)
        self.created.append(path)

    def rollback(self):
        errors = []
        for path in reversed(self.created):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as exc:
                errors.append("%s: %s" % (path, exc))
        for src, dst in reversed(self.moves):
            try:
                if os.path.exists(dst):
                    os.makedirs(os.path.dirname(src), exist_ok=True)
                    os.replace(dst, src)
            except OSError as exc:
                errors.append("%s -> %s: %s" % (dst, src, exc))
        if self.html:
            path, text = self.html
            try:
                with io.open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(text)
            except OSError as exc:
                errors.append("%s: %s" % (path, exc))
        return errors


def apply_plan(root, plan, payloads):
    """Carry out a plan. `payloads` maps upload id -> (compressed, original) bytes."""
    folder = plan["folder"]
    folder_img = img_dir(root, folder)
    folder_bk = backup_dir(root, folder)
    trash = os.path.join(folder_bk, TRASH_DIRNAME)
    unmatched_dir = os.path.join(folder_bk, UNMATCHED_DIRNAME)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    stage_img = os.path.join(folder_img, STAGE_PREFIX + stamp)
    stage_bk = os.path.join(folder_bk, STAGE_PREFIX + stamp)

    txn = _Txn()
    deleted_log, aside_log, html_log = [], [], []
    # Photos live flat in the gallery folder, so a new entry needs no directory of
    # its own -- just make sure the folder, its New/ drop box and the matching
    # img_backup folder are all there.
    os.makedirs(folder_img, exist_ok=True)
    os.makedirs(new_dir(root, folder), exist_ok=True)
    os.makedirs(folder_bk, exist_ok=True)
    os.makedirs(stage_img)
    os.makedirs(stage_bk)
    txn.dirs = [stage_img, stage_bk]

    try:
        # 1. Stage the img/ side: keepers move out, new photos are written in.
        img_commits = []
        for i, it in enumerate(plan["items"], 1):
            if it["kind"] == "existing" and it.get("replace"):
                # Cropped: the uncropped copy waits in the stage directory (so a
                # rollback can put it back) and is discarded with it on success.
                # The full-size original in img_backup is left as it is.
                src = os.path.join(folder_img, it["file"])
                txn.move(src, os.path.join(stage_img, "%04d.uncropped.jpg" % i))
                held = os.path.join(stage_img, "%04d.jpg" % i)
                txn.write(held, payloads[it["replace"]][0])
            elif it["kind"] == "existing":
                src = os.path.join(folder_img, it["file"])
                held = os.path.join(stage_img, "%04d.jpg" % i)
                txn.move(src, held)
            else:
                held = os.path.join(stage_img, "%04d.jpg" % i)
                txn.write(held, payloads[it["id"]][0])
            img_commits.append((held, os.path.join(folder_img, _target_for(plan, i))))

        # 2. Stage the img_backup/ side the same way.
        bk_commits = []
        for n, r in enumerate(plan["backupRenames"]):
            src = os.path.join(folder_bk, r["from"])
            if not os.path.exists(src):
                raise SaveError("expected backup %s disappeared" % r["from"])
            held = os.path.join(stage_bk, "r%04d%s" % (n, safe_ext(r["to"])))
            txn.move(src, held)
            bk_commits.append((held, os.path.join(folder_bk, r["to"])))
        for n, a in enumerate(plan["backupAdds"]):
            held = os.path.join(stage_bk, "a%04d%s" % (n, safe_ext(a["to"])))
            txn.write(held, payloads[a["id"]][1])
            bk_commits.append((held, os.path.join(folder_bk, a["to"])))

        # 3. Orphan backups that would collide with a new name step aside.
        if plan["backupUnmatched"]:
            os.makedirs(unmatched_dir, exist_ok=True)
            for b in plan["backupUnmatched"]:
                src = os.path.join(folder_bk, b)
                if os.path.exists(src):
                    dst = unique_path(unmatched_dir, b)
                    txn.move(src, dst)
                    aside_log.append("moved stale original %s aside to %s/%s"
                                     % (b, UNMATCHED_DIRNAME, os.path.basename(dst)))

        # 4. Deletions go to the trash folder, the compressed copy and the
        #    full-size original kept apart so they stay tellable from each other.
        trash_originals = os.path.join(trash, "originals")
        if plan["deletes"]:
            os.makedirs(trash, exist_ok=True)
        if plan["backupDeletes"]:
            os.makedirs(trash_originals, exist_ok=True)
        for name in plan["deletes"]:
            src = os.path.join(folder_img, name)
            if os.path.exists(src):
                dst = unique_path(trash, name)
                txn.move(src, dst)
                deleted_log.append("deleted %s (kept in %s/%s)"
                                   % (name, TRASH_DIRNAME, os.path.basename(dst)))
        for name in plan["backupDeletes"]:
            src = os.path.join(folder_bk, name)
            if os.path.exists(src):
                dst = unique_path(trash_originals, name)
                txn.move(src, dst)
                deleted_log.append("deleted original %s (kept in %s/originals/%s)"
                                   % (name, TRASH_DIRNAME, os.path.basename(dst)))

        # 5. Commit: the target names are all free now, so these are pure creates.
        for held, final in img_commits:
            if os.path.exists(final):
                raise SaveError("%s already exists -- refusing to overwrite it"
                                % os.path.basename(final))
            txn.move(held, final)
        for held, final in bk_commits:
            if os.path.exists(final):
                raise SaveError("img_backup/%s already exists -- refusing to "
                                "overwrite it" % os.path.basename(final))
            txn.move(held, final)

        # 6. our-story.html: either insert a whole new entry (and bump the
        #    "N and counting" badge with it) or rewrite this entry's images array.
        html_path = os.path.join(root, "our-story.html")
        before = load_html(root)
        txn.html = (html_path, before)
        if plan["newEntry"]:
            after = insert_entry(before, folder, plan["newEntry"], plan["newArray"])
            total = len(G.parse_our_story(after)[folder])
            after, was = set_count_badge(after, folder, total)
            html_log.append("added %s to the %s array in our-story.html"
                            % (plan["entryName"], folder))
            if was != total:
                html_log.append("updated the %s count badge %s -> %d" % (folder, was, total))
        else:
            after = rewrite_images_array(before, folder, plan["entryIndex"],
                                        plan["entryName"], plan["newArray"])
        if after != before:
            tmp = html_path + ".pm-tmp"
            with io.open(tmp, "w", encoding="utf-8", newline="") as f:
                f.write(after)
            os.replace(tmp, html_path)
            if not plan["newEntry"]:
                html_log.append("updated the images array for %s in our-story.html"
                                % plan["entryName"])

    except Exception as exc:
        errors = txn.rollback()
        for d in txn.dirs:
            shutil.rmtree(d, ignore_errors=True)
        msg = "Save failed and was rolled back: %s" % exc
        if errors:
            msg += ("\nRollback could not finish cleanly. Check these paths by hand:\n  "
                    + "\n  ".join(errors)
                    + "\nStaging directories: %s" % ", ".join(txn.dirs))
        raise SaveError(msg)

    for d in txn.dirs:
        shutil.rmtree(d, ignore_errors=True)

    # 7. Only once everything above succeeded: clear consumed New/ files.
    #    The untouched original is already archived in img_backup.
    new_log = []
    for a in plan["adds"]:
        if a.get("fromNew"):
            src = os.path.join(new_dir(root, folder), a["fromNew"])
            if os.path.isfile(src):
                try:
                    os.remove(src)
                    new_log.append("removed %s from the New folder" % a["fromNew"])
                except OSError as exc:
                    new_log.append("could not remove New/%s: %s" % (a["fromNew"], exc))

    log = []
    for a in plan["adds"]:
        log.append("added %s (%s KB) from %s"
                   % (a["to"], (a["bytes"] or 0) // 1024, a["source"]))
    for r in plan["renames"]:
        if r["changed"]:
            log.append("renamed %s -> %s" % (r["from"], r["to"]))
    for r in plan["replaced"]:
        log.append("cropped %s to 4:3 (%sx%s, %s KB)"
                   % (r["to"], r["width"], r["height"], (r["bytes"] or 0) // 1024))
    log.extend(deleted_log)
    for b in plan["backupAdds"]:
        log.append("archived original as img_backup/.../%s" % b["to"])
    for b in plan["backupRenames"]:
        if b["changed"]:
            log.append("renamed original %s -> %s" % (b["from"], b["to"]))
    log.extend(aside_log)
    log.extend(new_log)
    log.extend(html_log)

    warnings = []
    if plan["missingBackups"]:
        warnings.append("No original in img_backup for: "
                        + ", ".join(plan["missingBackups"]))
    # The browser compresses before uploading; anything this big means that step
    # did not happen, and the README's ceiling is about 450 KB.
    oversized = ["%s (%d KB)" % (a["to"], (a["bytes"] or 0) // 1024)
                 for a in plan["adds"] + plan["replaced"] if (a["bytes"] or 0) > 500 * 1024]
    if oversized:
        warnings.append("Larger than the gallery's usual 150-400 KB: "
                        + ", ".join(oversized))
    return {"log": log, "warnings": warnings}


def _target_for(plan, position):
    return G.target_name(plan["base"], plan["sep"], position)


# ---------------------------------------------------------------- html rewrite

def _pad_to(line, column):
    """Grow `line` with spaces so the next field starts at `column`."""
    return line + (" " * (column - len(line)) if len(line) < column else " ")


def _images_literal(images):
    return "[" + ",".join('"%s"' % n for n in images) + "]"


def render_entry(folder, fields, images):
    """One array entry, laid out like the ones already in our-story.html."""
    if folder == "Mexico":
        return (
            '      {{ name: "{name}", nameEs: "{nameEs}",\n'
            '        subtitle:   "{subtitle}",\n'
            '        subtitleEs: "{subtitleEs}",\n'
            '        filePrefix: "{filePrefix}",\n'
            '        images: {images} }},'
        ).format(name=fields["name"], nameEs=fields["nameEs"],
                 subtitle=fields["subtitle"], subtitleEs=fields["subtitleEs"],
                 filePrefix=fields["filePrefix"], images=_images_literal(images))

    values = {
        "name": '"%s",' % fields["name"],
        "nameEs": '"%s",' % fields["nameEs"],
        "flag": '"%s",' % fields.get("flag", ""),
        "flagImg": '"%s",' % fields.get("flagImg", ""),
        "filePrefix": '"%s",' % fields["filePrefix"],
        "images": _images_literal(images),
    }
    line = "      {"
    for field, column in ENTRY_COLUMNS[folder]:
        line = _pad_to(line, column) + "%s: %s" % (field, values[field])
    return line.rstrip(",") + " },"


def insertion_index(folder, entries, fields):
    """Where the new entry goes: alphabetical for the lists, last for Mexico.

    Both lists are re-sorted by nameEs when the page renders, so this is purely
    about keeping the source file easy to scan. Countries read as alphabetical by
    English name; States by filePrefix, which is why "Washington, D.C." sits
    under D.
    """
    if folder == "Mexico":
        return len(entries)
    if folder == "States":
        key = lambda f: (f.get("filePrefix") or "").lower()
        new_key = key(fields)
        existing = [(G.entry_base(e) or "").lower() for e in entries]
    else:
        new_key = (fields.get("name") or "").lower()
        existing = [(e["name"] or "").lower() for e in entries]
    for i, k in enumerate(existing):
        if k > new_key:
            return i
    return len(entries)


def insert_entry(html, folder, fields, images):
    """Add a brand-new entry to the COUNTRIES / STATES / MEXICO_TRIPS array."""
    entries = G.parse_our_story(html)[folder]
    if not entries:
        raise SaveError("the %s array looks empty - refusing to guess its layout" % folder)

    nl = line_ending(html)
    text = render_entry(folder, fields, images).replace("\n", nl)

    at = insertion_index(folder, entries, fields)
    if at >= len(entries):
        anchor = entries[-1]["obj_span"]
        line_end = html.find(nl, anchor[1])
        cut = len(html) if line_end == -1 else line_end + len(nl)
        return html[:cut] + text + nl + html[cut:]

    anchor = entries[at]["obj_span"]
    cut = html.rfind(nl, 0, anchor[0])
    cut = 0 if cut == -1 else cut + len(nl)
    return html[:cut] + text + nl + html[cut:]


def count_badge(html, folder):
    """(span, current value) of the "N and counting" badge for a gallery."""
    heading = COUNT_BADGE_HEADING[folder]
    at = html.find('id="%s"' % heading)
    if at == -1:
        return None, None
    m = re.compile(r'(<div class="countries-count">)(\s*\d+\s*)(</div>)').search(html, at)
    if not m:
        return None, None
    return (m.start(2), m.end(2)), int(m.group(2).strip())


def set_count_badge(html, folder, value):
    span, current = count_badge(html, folder)
    if span is None:
        raise SaveError("could not find the count badge under #%s in our-story.html"
                        % COUNT_BADGE_HEADING[folder])
    if current == value:
        return html, current
    return html[:span[0]] + str(value) + html[span[1]:], current


def badge_report(root):
    """Each gallery's badge next to its real entry count, for a load-time check."""
    html = load_html(root)
    data = G.parse_our_story(html)
    out = {}
    for folder in data:
        _span, current = count_badge(html, folder)
        out[folder] = {"badge": current, "entries": len(data[folder])}
    return out


def rewrite_images_array(html, folder, entry_index, entry_name, new_images):
    """Replace one entry's `images: [...]` list, leaving the rest of the line be."""
    data = G.parse_our_story(html)
    entries = data[folder]
    if not (0 <= entry_index < len(entries)):
        raise SaveError("entry index %d out of range" % entry_index)
    entry = entries[entry_index]
    if entry["name"] != entry_name:
        raise SaveError("our-story.html no longer has %r at index %d of %s"
                        % (entry_name, entry_index, folder))
    span = entry["images_span"]
    if not span:
        raise SaveError("%s has no images array to update" % entry_name)
    body = ",".join('"%s"' % n for n in new_images)
    return html[:span[0]] + "[" + body + "]" + html[span[1]:]
