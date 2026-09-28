"""Header-only facts about a photo: when it was taken and how big it is.

Plain Python, no Pillow. Only the first few hundred KB of a file are read:

  - taken_at():   the EXIF block in a JPEG, PNG or WebP, walked IFD0 -> Exif
                  sub-IFD for DateTimeOriginal (falling back to
                  DateTimeDigitized, then IFD0 DateTime).
  - image_size(): pixel dimensions as displayed, i.e. with the EXIF
                  Orientation tag applied, the same way browsers draw it.

The site copies in img/Our Story/ were re-encoded through a canvas and have
no EXIF, so the date normally comes from the untouched original archived in
img_backup/ (see save_engine.backups_by_position).
"""

import struct

READ_LIMIT = 512 * 1024          # EXIF and the frame header sit near the start

TAG_ORIENTATION = 0x0112
TAG_DATETIME = 0x0132
TAG_EXIF_IFD = 0x8769
TAG_ORIGINAL = 0x9003
TAG_DIGITIZED = 0x9004

# JPEG start-of-frame markers carry the dimensions; C4, C8 and CC are not frames.
SOF_MARKERS = set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}

# The gallery's cell shape: landscape 4:3 (1400x1050, 1200x900). A photo within
# this much of 4/3 is treated as 4:3 -- rounding in a resize can leave a pixel
# or two over, which object-fit hides, but anything further visibly crops.
RATIO = 4 / 3
RATIO_TOLERANCE = 0.01


def _read_head(path):
    with open(path, "rb") as fh:
        return fh.read(READ_LIMIT)


def _tiff_block(data):
    """The TIFF-structured EXIF payload inside a file's leading bytes, or None."""
    if data[:2] == b"\xff\xd8":                                  # JPEG
        i = 2
        while i + 4 <= len(data) and data[i] == 0xFF:
            marker = data[i + 1]
            if marker in (0xD9, 0xDA):                           # end / start of scan
                break
            size = struct.unpack(">H", data[i + 2:i + 4])[0]
            seg = data[i + 4:i + 2 + size]
            if marker == 0xE1 and seg[:6] == b"Exif\x00\x00":
                return seg[6:]
            i += 2 + size
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":                        # PNG eXIf chunk
        i = 8
        while i + 8 <= len(data):
            size, ctype = struct.unpack(">I4s", data[i:i + 8])
            if ctype == b"eXIf":
                return data[i + 8:i + 8 + size]
            if ctype == b"IDAT":
                break
            i += 12 + size
        return None
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":           # WebP EXIF chunk
        i = 12
        while i + 8 <= len(data):
            ctype, size = struct.unpack("<4sI", data[i:i + 8])
            if ctype == b"EXIF":
                blk = data[i + 8:i + 8 + size]
                return blk[6:] if blk[:6] == b"Exif\x00\x00" else blk
            i += 8 + size + (size & 1)
        return None
    return None


def _read_ifd(tiff, offset, endian):
    """{tag: (type, count, value_or_offset_bytes)} for one IFD."""
    out = {}
    if offset + 2 > len(tiff):
        return out
    count = struct.unpack(endian + "H", tiff[offset:offset + 2])[0]
    for k in range(count):
        p = offset + 2 + 12 * k
        if p + 12 > len(tiff):
            break
        tag, typ, n = struct.unpack(endian + "HHI", tiff[p:p + 8])
        out[tag] = (typ, n, tiff[p + 8:p + 12])
    return out


def _exif(data):
    """(tiff, endian, ifd0, exif_sub_ifd) or None when there is no EXIF."""
    tiff = _tiff_block(data)
    if not tiff or len(tiff) < 8:
        return None
    endian = {b"II": "<", b"MM": ">"}.get(tiff[:2])
    if not endian:
        return None
    ifd0 = _read_ifd(tiff, struct.unpack(endian + "I", tiff[4:8])[0], endian)
    sub = {}
    if TAG_EXIF_IFD in ifd0:
        sub = _read_ifd(tiff, struct.unpack(endian + "I", ifd0[TAG_EXIF_IFD][2])[0], endian)
    return tiff, endian, ifd0, sub


def _ascii(tiff, field, endian):
    typ, n, raw = field
    if typ != 2:
        return None
    if n <= 4:
        s = raw[:n]
    else:
        off = struct.unpack(endian + "I", raw)[0]
        s = tiff[off:off + n]
    return s.split(b"\x00")[0].decode("ascii", "replace").strip() or None


def _normalise(s):
    """'2026:07:14 18:03:22' -> '2026-07-14T18:03:22', or None if unusable."""
    if not s or len(s) < 19 or s.startswith("0000"):
        return None
    date, _, time = s[:19].partition(" ")
    parts = date.split(":")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    return "-".join(parts) + "T" + time


def taken_at(path):
    """ISO-ish 'YYYY-MM-DDTHH:MM:SS' local capture time, or None."""
    try:
        found = _exif(_read_head(path))
        if not found:
            return None
        tiff, endian, ifd0, sub = found
        for table, tag in ((sub, TAG_ORIGINAL), (sub, TAG_DIGITIZED), (ifd0, TAG_DATETIME)):
            if tag in table:
                got = _normalise(_ascii(tiff, table[tag], endian))
                if got:
                    return got
    except (OSError, struct.error, ValueError):
        pass
    return None


def _raw_size(data):
    """Stored (width, height) of a JPEG, PNG or WebP, before any rotation."""
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 <= len(data):
            if data[i] != 0xFF:
                return None
            marker = data[i + 1]
            if marker == 0xFF:                                   # fill byte
                i += 1
                continue
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:  # no length field
                i += 2
                continue
            size = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in SOF_MARKERS:
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            if marker in (0xD9, 0xDA):
                return None
            i += 2 + size
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X":
            w = 1 + int.from_bytes(data[24:27], "little")
            h = 1 + int.from_bytes(data[27:30], "little")
            return w, h
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            b = int.from_bytes(data[21:25], "little")
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    return None


def image_size(path):
    """(width, height) as a browser displays it, or None if unreadable."""
    try:
        data = _read_head(path)
        size = _raw_size(data)
        if not size:
            return None
        found = _exif(data)
        if found:
            _tiff, endian, ifd0, _sub = found
            field = ifd0.get(TAG_ORIENTATION)
            if field and field[0] == 3:                          # SHORT
                orientation = struct.unpack(endian + "H", field[2][:2])[0]
                if orientation in (5, 6, 7, 8):                  # rotated 90 degrees
                    size = (size[1], size[0])
        return tuple(size)
    except (OSError, struct.error, ValueError):
        return None


def is_four_three(size):
    """True for a landscape photo within RATIO_TOLERANCE of 4:3."""
    if not size or not size[1]:
        return False
    return abs(size[0] / size[1] / RATIO - 1) <= RATIO_TOLERANCE
