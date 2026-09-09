#!/usr/bin/env python3
"""Pack the PNG icons into a multi-resolution favicon.ico.

    python3 tools/make_favicon.py

Google only considers a favicon whose square side is a multiple of 48px, so a
32x32-only .ico is skipped and the search result falls back to the globe
placeholder. The ico written here carries 48 and 96 alongside 32 so browsers
still get the small size they prefer in a tab.

Entries store their PNG bytes verbatim rather than a BMP bitmap; every engine
that matters has read PNG-in-ICO since IE6, and it keeps the file small.
"""
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = [32, 48, 96]
OUT = os.path.join(ROOT, "favicon.ico")


def main():
    images = []
    for size in SOURCES:
        name = "favicon-32.png" if size == 32 else "favicon-%d.png" % size
        path = os.path.join(ROOT, name)
        with open(path, "rb") as f:
            images.append((size, f.read()))

    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries, payload = [], []
    for size, data in images:
        # A side of 256 is written as 0; nothing here reaches that, but the
        # modulo keeps the field correct if a larger source is ever added.
        entries.append(struct.pack(
            "<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset
        ))
        payload.append(data)
        offset += len(data)

    with open(OUT, "wb") as f:
        f.write(header)
        for e in entries:
            f.write(e)
        for p in payload:
            f.write(p)

    print("favicon.ico  %s  %d bytes" % (
        " + ".join("%dx%d" % (s, s) for s, _ in images), os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
