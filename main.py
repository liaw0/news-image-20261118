#!/usr/bin/env python3
"""THE WORLD — Wednesday 18 November 2026.

A newspaper front page drawn from code for make.fun news-image-20261118:
the day's world news in one 1024x1024 image. Pure Python standard library
(own PNG encoder, own 5x7 bitmap font, own shape drawing). No network,
no randomness, no clock: two runs write byte-identical output.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# --- 5x7 bitmap font (each glyph: 7 rows of 5 bits) -------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "•": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, thick=2):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            inner = math.isqrt(max(0, (r - thick) * (r - thick) - dy * dy)) if abs(dy) < r - thick else 0
            self.rect(cx - dx, cy + dy, dx - inner, 1, c)
            self.rect(cx + inner + 1, cy + dy, dx - inner, 1, c)

    def polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(min(ys), 0), min(max(ys), self.h - 1) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            if len(xs) >= 2:
                xs.sort()
                self.rect(int(xs[0]), y, int(xs[-1]) - int(xs[0]) + 1, 1, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_right(self, s, x_right, y, scale, c):
        self.text(s, x_right - text_width(s, scale), y, scale, c)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        return out + struct.pack(">I", binascii.crc32(tag + payload) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))


# --- palette ----------------------------------------------------------------
PAPER = (245, 240, 230)
INK = (18, 18, 18)
NAVY = (24, 38, 66)
RED = (192, 45, 40)
AMBER = (232, 163, 61)
GREY = (120, 120, 122)

# --- scenes -----------------------------------------------------------------


def draw_masthead(cv):
    cv.rect(0, 0, W, 80, NAVY)
    cv.text("THE WORLD", 20, 12, 8, PAPER)
    cv.text_right("18 NOV 2026", 1004, 26, 4, AMBER)
    cv.rect(0, 80, W, 6, RED)


def draw_lead(cv):
    cv.text("GULF IN FLAMES", 20, 94, 8, INK)
    cv.text("U.S. STRIKES IRAN MISSILE SITE ON QESHM ISLAND", 20, 158, 3, RED)
    cv.text("AS IRAN FIRES DRONES AT BAHRAIN AND KUWAIT", 20, 182, 3, RED)
    x0, y0, x1, y1 = 20, 218, 1004, 540
    # dusk sky in bands
    cv.rect(x0, y0, x1 - x0, 82, (58, 44, 66))
    cv.rect(x0, y0 + 82, x1 - x0, 80, (120, 72, 60))
    cv.rect(x0, y0 + 162, x1 - x0, 60, (214, 130, 60))
    # low sun
    cv.circle(880, 300, 26, (240, 220, 170))
    cv.circle(880, 300, 18, (248, 232, 190))
    # sea
    cv.rect(x0, 440, x1 - x0, y1 - 440, (24, 64, 82))
    for yy, wx, ww in ((458, 60, 180), (478, 420, 240), (498, 120, 300),
                       (516, 560, 260), (530, 300, 200)):
        cv.hline(wx, yy, ww, (48, 100, 120))
    # Qeshm island ridge
    cv.polygon([(100, 440), (180, 412), (330, 406), (480, 418), (640, 440)],
               (28, 30, 38))
    # missile site: tower, dish, launcher
    cv.rect(296, 392, 8, 18, (70, 72, 78))
    cv.circle(300, 388, 6, (180, 182, 186))
    cv.line(320, 410, 345, 388, (60, 62, 68), 3)
    # explosion over the site
    cv.circle(345, 385, 30, (230, 120, 30))
    cv.circle(345, 385, 20, (240, 190, 60))
    cv.circle(345, 385, 11, (250, 235, 160))
    for ang in range(0, 360, 60):
        a = math.radians(ang)
        tipx = int(345 + 44 * math.cos(a))
        tipy = int(385 + 44 * math.sin(a))
        bx = int(345 + 26 * math.cos(a + 0.35))
        by = int(385 + 26 * math.sin(a + 0.35))
        cx = int(345 + 26 * math.cos(a - 0.35))
        cy = int(385 + 26 * math.sin(a - 0.35))
        cv.polygon([(tipx, tipy), (bx, by), (cx, cy)], (240, 170, 50))
    # smoke drifting up-right
    cv.circle(362, 350, 16, (95, 95, 100))
    cv.circle(378, 330, 12, (105, 105, 110))
    cv.circle(390, 312, 9, (115, 115, 120))
    # jets with contrails
    for jx, jy, s in ((700, 255, 1), (770, 300, 1)):
        cv.line(jx - 130, jy - 12, jx - 14, jy, (220, 220, 220), 2)
        cv.polygon([(jx, jy - 8), (jx + 34, jy), (jx, jy + 8), (jx + 10, jy)],
                   (30, 30, 35))
    # drones: small crosses with dotted trails
    for dx, dy in ((600, 250), (650, 275), (820, 240), (880, 270)):
        cv.line(dx - 40, dy, dx - 8, dy, (200, 200, 205), 1)
        cv.hline(dx - 4, dy, 9, (20, 20, 24))
        cv.vline(dx, dy - 4, 9, (20, 20, 24))
    # radar spit, far left
    cv.polygon([(30, 440), (90, 440), (60, 428)], (28, 30, 38))
    cv.circle(60, 424, 5, (180, 182, 186))
    # tanker on the right, on fire
    cv.rect(700, 468, 260, 30, (12, 12, 16))
    cv.hline(700, 468, 260, (200, 90, 60))
    cv.rect(920, 448, 40, 20, (200, 200, 205))
    cv.rect(900, 455, 10, 13, (60, 60, 64))
    cv.circle(800, 458, 18, (230, 120, 30))
    cv.circle(800, 458, 12, (245, 200, 70))
    cv.circle(802, 432, 12, (100, 100, 105))
    cv.circle(814, 414, 9, (112, 112, 117))
    cv.circle(826, 398, 7, (122, 122, 127))


def draw_panel_frame(cv, x):
    cv.rect(x, 552, 322, 138, PAPER)
    cv.rect(x, 552, 322, 2, INK)


def draw_panel_kerch(cv):
    x = 20
    draw_panel_frame(cv, x)
    cv.rect(x, 552, 322, 78, (178, 190, 202))
    cv.rect(x, 630, 322, 60, (28, 70, 102))
    for yy, wx, ww in ((648, 40, 90), (666, 180, 110), (680, 90, 70)):
        cv.hline(wx, yy, ww, (60, 110, 150))
    # bridge deck in two pieces, middle span fallen
    cv.rect(x + 10, 610, 120, 5, (240, 240, 238))
    cv.rect(x + 185, 610, 125, 5, (240, 240, 238))
    cv.line(x + 135, 612, x + 175, 648, (240, 240, 238), 4)
    cv.rect(x + 170, 652, 14, 6, (200, 200, 198))
    # pylons and cables
    cv.rect(x + 50, 556, 10, 56, (240, 240, 238))
    cv.rect(x + 252, 556, 10, 56, (240, 240, 238))
    cv.line(x + 55, 556, x + 20, 610, (240, 240, 238), 1)
    cv.line(x + 55, 556, x + 90, 610, (240, 240, 238), 1)
    cv.line(x + 257, 556, x + 222, 610, (240, 240, 238), 1)
    cv.line(x + 257, 556, x + 292, 610, (240, 240, 238), 1)
    # smoke and fire at the gap
    cv.circle(x + 150, 600, 10, (105, 105, 110))
    cv.circle(x + 160, 588, 8, (118, 118, 122))
    cv.circle(x + 170, 606, 6, (235, 130, 40))
    cv.text("BRIDGE FALLS", x, 698, 3, INK)
    cv.text("UKRAINE HITS KERCH LINK", x, 726, 2, INK)
    cv.text("AGAIN; ROAD ARCH", x, 744, 2, INK)
    cv.text("COLLAPSES INTO STRAIT", x, 762, 2, INK)


def draw_flag_us(cv, x, y):
    for i in range(7):
        cv.rect(x, y + i * 4, 46, 4, RED if i % 2 == 0 else (240, 240, 238))
    cv.rect(x, y, 18, 14, (30, 50, 110))


def draw_flag_cn(cv, x, y):
    cv.rect(x, y, 46, 30, (200, 30, 25))
    cv.circle(x + 10, y + 8, 4, (250, 220, 60))
    for dx, dy in ((22, 6), (28, 10), (28, 16), (22, 20)):
        cv.circle(x + dx, y + dy, 2, (250, 220, 60))


def draw_flag_ru(cv, x, y):
    cv.rect(x, y, 46, 10, (240, 240, 238))
    cv.rect(x, y + 10, 46, 10, (30, 90, 180))
    cv.rect(x, y + 20, 46, 10, (200, 30, 25))


def draw_panel_summit(cv):
    x = 351
    draw_panel_frame(cv, x)
    cv.rect(x, 552, 322, 48, (64, 64, 96))
    cv.rect(x, 600, 322, 50, (190, 120, 70))
    cv.rect(x, 650, 322, 40, (230, 170, 100))
    # skyline
    for bx, bw, bh in ((0, 34, 34), (40, 26, 52), (72, 40, 28), (118, 30, 44),
                       (154, 36, 60), (196, 28, 36), (230, 34, 50),
                       (270, 26, 30), (300, 22, 42)):
        cv.rect(x + bx, 690 - bh, bw, bh, (20, 28, 48))
    # three flags on poles
    for fx, draw in ((x + 30, draw_flag_us), (x + 138, draw_flag_cn),
                     (x + 246, draw_flag_ru)):
        cv.vline(fx - 2, 566, 76, (90, 90, 94))
        draw(cv, fx, 566)
    cv.text("XI, PUTIN, TRUMP", x, 698, 3, INK)
    cv.text("FIRST TRILATERAL SUMMIT", x, 726, 2, INK)
    cv.text("TO OPEN IN SHENZHEN", x, 744, 2, INK)
    cv.text("ON THURSDAY", x, 762, 2, INK)


def draw_panel_ebola(cv):
    x = 682
    draw_panel_frame(cv, x)
    cv.rect(x, 552, 322, 138, (122, 42, 36))
    # spiked virus ball
    cx, cy = x + 130, 622
    for ang in range(0, 360, 36):
        a = math.radians(ang)
        cv.line(int(cx + 38 * math.cos(a)), int(cy + 38 * math.sin(a)),
                int(cx + 54 * math.cos(a)), int(cy + 54 * math.sin(a)),
                (200, 90, 70), 3)
    cv.circle(cx, cy, 38, (160, 50, 45))
    cv.circle(cx - 12, cy - 10, 8, (140, 40, 38))
    cv.circle(cx + 14, cy + 8, 6, (140, 40, 38))
    cv.circle(cx + 4, cy - 16, 5, (180, 70, 60))
    # white cross badge
    cv.circle(x + 268, 668, 18, (240, 240, 238))
    cv.rect(x + 264, 656, 8, 24, RED)
    cv.rect(x + 256, 664, 24, 8, RED)
    # clinic tent
    cv.polygon([(x + 218, 685), (x + 300, 685), (x + 259, 640)], (240, 240, 238))
    cv.rect(x + 255, 656, 8, 16, RED)
    cv.rect(x + 251, 660, 16, 8, RED)
    cv.text("EBOLA DOUBLES", x, 698, 3, INK)
    cv.text("OUTBREAK IN CONGO TOPS", x, 726, 2, INK)
    cv.text("11,000 CASES; 5,400", x, 744, 2, INK)
    cv.text("DEAD", x, 762, 2, INK)


def draw_briefs(cv):
    cv.rect(20, 810, 984, 2, INK)
    cv.text("ALSO TODAY", 20, 820, 3, RED)
    briefs = [
        "PELTOLA WINS ALASKA SENATE SEAT; DEMOCRATS REACH 56",
        "NVIDIA REPORTS $115.8BN REVENUE; OUTLOOK $130BN",
        "NORTH KOREA FIRES MISSILES AFTER U.S.-SOUTH KOREA DRILLS",
        "CYCLONE AKVAN NEARS INDIA; LANDFALL EXPECTED 20 NOV",
        "RUSSIAN MILITARY PLANE CRASHES IN SIBERIA; 19 DEAD",
        "MOLDOVA CLOSES AIRSPACE AS RUSSIAN DRONES ENTER",
    ]
    y = 848
    for line in briefs:
        cv.rect(20, y + 3, 8, 8, RED)
        cv.text(line, 36, y, 2, INK)
        y += 19


def draw_footer(cv):
    cv.rect(0, 962, W, 62, NAVY)
    cv.text("WEDNESDAY 18 NOV 2026", 20, 984, 3, PAPER)
    cv.text_right("BBC / REUTERS / AP / AL JAZEERA", 1004, 984, 3, AMBER)


def main():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    draw_panel_kerch(cv)
    draw_panel_summit(cv)
    draw_panel_ebola(cv)
    draw_briefs(cv)
    draw_footer(cv)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = png_bytes(cv)
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes" % (path, len(data)))


if __name__ == "__main__":
    main()

