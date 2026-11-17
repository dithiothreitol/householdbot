#!/usr/bin/env python3
"""Draw the HouseholdBot icon (512 x 512 PNG) with the standard library only.

The avatar from docs/assets/avatar.svg, a roof over two eyes on a mint
square, with the corners rounded and transparent.
  python scripts/make_icon.py   writes householdbot/.claude-plugin/icon.png
"""
import struct
import zlib
from pathlib import Path

SIZE, SS = 512, 3  # supersampling per axis
BG = (189, 233, 207)  # #BDE9CF
FG = (16, 48, 31)  # #10301F
OUT = Path(__file__).resolve().parents[1] / "householdbot" / ".claude-plugin" / "icon.png"

# Same geometry as docs/assets/avatar.svg.
ROOF = ((108, 216), (256, 98), (404, 216))
ROOF_HALF = 20  # half the stroke width; round caps and join
EYES = ((196, 332), (316, 332))
EYE_RX, EYE_RY = 42, 68


def in_rounded_square(x, y, r=104):
    cx = min(max(x, r), SIZE - r)
    cy = min(max(y, r), SIZE - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0 <= x <= SIZE and 0 <= y <= SIZE


def in_ellipse(x, y, c, rx, ry):
    return ((x - c[0]) / rx) ** 2 + ((y - c[1]) / ry) ** 2 <= 1


def near_segment(x, y, p, q, half):
    px, py = q[0] - p[0], q[1] - p[1]
    t = max(0.0, min(1.0, ((x - p[0]) * px + (y - p[1]) * py) / (px * px + py * py)))
    dx, dy = x - (p[0] + t * px), y - (p[1] + t * py)
    return dx * dx + dy * dy <= half * half


def color_at(x, y):
    if not in_rounded_square(x, y):
        return None
    roof = near_segment(x, y, ROOF[0], ROOF[1], ROOF_HALF) or near_segment(x, y, ROOF[1], ROOF[2], ROOF_HALF)
    eyes = any(in_ellipse(x, y, c, EYE_RX, EYE_RY) for c in EYES)
    return FG if roof or eyes else BG


def render():
    rows = []
    for j in range(SIZE):
        row = bytearray([0])
        for i in range(SIZE):
            acc = [0, 0, 0, 0]
            for sj in range(SS):
                for si in range(SS):
                    c = color_at(i + (si + 0.5) / SS, j + (sj + 0.5) / SS)
                    if c:
                        acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]; acc[3] += 255
            n = SS * SS
            alpha = acc[3] // n
            if alpha:
                cover = acc[3] // 255
                row += bytes([acc[0] // cover, acc[1] // cover, acc[2] // cover, alpha])
            else:
                row += b"\x00\x00\x00\x00"
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    OUT.write_bytes(png)
    print(f"wrote {OUT} ({len(png)} bytes)")


if __name__ == "__main__":
    render()
