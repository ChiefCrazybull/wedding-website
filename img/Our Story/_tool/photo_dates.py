"""When a photo was taken, read from its EXIF block.

Plain Python, no Pillow: this only needs one tag, so it finds the EXIF/TIFF
block in a JPEG, PNG or WebP and walks IFD0 -> Exif sub-IFD for
DateTimeOriginal (falling back to DateTimeDigitized, then IFD0 DateTime).

The site copies in img/Our Story/ were re-encoded through a canvas and have
no EXIF, so the date normally comes from the untouched original archived in
img_backup/ (see save_engine.backups_by_position).
"""

import struct

READ_LIMIT = 512 * 1024          # EXIF sits near the start of the file

TAG_DATETIME = 0x0132
TAG_EXIF_IFD = 0x8769
TAG_ORIGINAL = 0x9003
TAG_DIGITIZED = 0x9004


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
        with open(path, "rb") as fh:
            data = fh.read(READ_LIMIT)
        tiff = _tiff_block(data)
        if not tiff or len(tiff) < 8:
            return None
        endian = {b"II": "<", b"MM": ">"}.get(tiff[:2])
        if not endian:
            return None
        ifd0 = _read_ifd(tiff, struct.unpack(endian + "I", tiff[4:8])[0], endian)
        exif = {}
        if TAG_EXIF_IFD in ifd0:
            sub = struct.unpack(endian + "I", ifd0[TAG_EXIF_IFD][2])[0]
            exif = _read_ifd(tiff, sub, endian)
        for table, tag in ((exif, TAG_ORIGINAL), (exif, TAG_DIGITIZED), (ifd0, TAG_DATETIME)):
            if tag in table:
                got = _normalise(_ascii(tiff, table[tag], endian))
                if got:
                    return got
    except (OSError, struct.error, ValueError):
        pass
    return None
