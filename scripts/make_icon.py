#!/usr/bin/env python3
"""Draw the HouseholdBot icon (512 x 512 PNG) with the standard library only.

A white house on a teal rounded square, with a teal check mark inside.
  python scripts/make_icon.py   writes householdbot/.claude-plugin/icon.png
"""
import struct
import zlib
from pathlib import Path

SIZE, SS = 512, 3  # supersampling per axis
BG = (31, 111, 120)
FG = (255, 255, 255)
OUT = Path(__file__).resolve().parents[1] / "householdbot" / ".claude-plugin" / "icon.png"


def in_rounded_square(x, y, r=104):
    cx = min(max(x, r), SIZE - r)
    cy = min(max(y, r), SIZE - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r and 0 <= x <= SIZE and 0 <= y <= SIZE


def in_triangle(x, y, a, b, c):
    def side(p, q):
        return (x - q[0]) * (p[1] - q[1]) - (p[0] - q[0]) * (y - q[1])
    d1, d2, d3 = side(a, b), side(b, c), side(c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def near_segment(x, y, p, q, half):
    px, py = q[0] - p[0], q[1] - p[1]
    t = max(0.0, min(1.0, ((x - p[0]) * px + (y - p[1]) * py) / (px * px + py * py)))
    dx, dy = x - (p[0] + t * px), y - (p[1] + t * py)
    return dx * dx + dy * dy <= half * half


def color_at(x, y):
    if not in_rounded_square(x, y):
        return None
    house = in_triangle(x, y, (256, 106), (92, 246), (420, 246)) or (140 <= x <= 372 and 232 <= y <= 404)
    if house:
        tick = near_segment(x, y, (196, 320), (240, 362), 15) or near_segment(x, y, (240, 362), (322, 272), 15)
        return BG if tick else FG
    return BG


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
