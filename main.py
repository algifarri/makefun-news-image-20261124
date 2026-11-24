"""news-image-20261124: a broadsheet front page summing up Tuesday 24 Nov 2026.

Pure Python stdlib. Draws a 1024x1024 newspaper poster from scratch:
own 5x7 bitmap letterface, own rasteriser (rects, discs, triangles, lines)
and a hand-rolled PNG writer. No network, no clock, no randomness, so
every run writes the exact same bytes to /output/entry.png.

Stories (all first reported on Tuesday 24 November 2026):
  HERO  World Chess Championship Game 1 begins in Geneva: defending
        champion Gukesh (India) v challenger Sindarov (Uzbekistan),
        both 20, the youngest title match in history, $2.5m prize fund.
  SEA   Ukraine says its drones sank the Russian corvette Merkury off
        Benghazi, Libya.
  KYIV  Russian strikes kill 15 in the Kyiv region; 14 missing after a
        drone hits a home in Dymer.
  DELHI Modi and Nepal PM Balendra Shah flag off the Saryu-Kamala
        Express (Ayodhya-Janakpur); AI centre opens at IIT Patna.
  FIRE  24 dead in the Indonesia candy-factory fire in Banten; about
        30 still missing as the search goes on.
  BRIEF COP31 fallout shifts to COP32 in Addis Ababa; Iran vows to
        counter a US Hormuz blockade; Nvidia soars as Huang returns
        as CEO; India-China border talks in Arunachal Pradesh.
"""

import os
import struct
import zlib
from math import sqrt

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (22, 22, 26)
NAVY = (18, 33, 61)
RED = (178, 34, 34)
GOLD = (198, 148, 52)
WHITE = (255, 255, 255)
GREY = (96, 96, 100)
SEA = (11, 42, 74)
SEA_LT = (24, 78, 122)
ORANGE = (232, 116, 24)
YELLOW = (244, 196, 48)
TEAL = (16, 120, 110)
SMOKE = (150, 150, 150)
DARK = (40, 44, 52)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
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
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "X2": (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}
FONT["\u00b7"] = (".....", ".....", ".....", ".##..", ".##..", ".....", ".....")
FONT["\u2014"] = FONT["-"]
FONT["\u2013"] = FONT["-"]
FONT["\u2019"] = FONT["'"]
FONT["\u00d7"] = FONT["X2"]


def text_width(text, s):
    return len(text) * 6 * s - s


def wrap(text, s, maxw):
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, s) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def border(self, x, y, w, h, c, t=3):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(sqrt(r * r - dy * dy))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        steps = max(dx, dy, 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.disc(x, y, max(1, t // 2), c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= y < max(ay, by):
                    xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def text(self, x, y, s, c, txt):
        cx = x
        for ch in txt.upper():
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "#":
                        self.fill_rect(cx + col * s, y + r * s, s, s, c)
            cx += 6 * s
        return cx

    def text_c(self, cx, y, s, c, txt):
        return self.text(cx - text_width(txt, s) // 2, y, s, c, txt)

    def block(self, x, y, s, c, txt, maxw, lead=None):
        lead = lead if lead is not None else 9 * s
        for ln in wrap(txt, s, maxw):
            self.text(x, y, s, c, ln)
            y += lead
        return y


# ---------------------------------------------------------------- pictures
def draw_board(cv, x, y, cell):
    light, dark = (240, 217, 181), (181, 136, 99)
    for r in range(8):
        for f in range(8):
            cv.fill_rect(x + f * cell, y + r * cell, cell, cell,
                         light if (r + f) % 2 == 0 else dark)
    back = "RNBQKBNR"
    for f in range(8):
        # black back rank + pawns on top rows, white on bottom rows
        for (row, ch, col) in ((0, back[f], INK), (1, "P", INK),
                               (6, "P", WHITE), (7, back[f], WHITE)):
            cx = x + f * cell + cell // 2
            cy = y + row * cell + cell // 2
            cv.disc(cx, cy, cell // 2 - 3, col)
            cv.disc(cx, cy, cell // 2 - 5,
                    WHITE if col == INK else (30, 30, 34))
            cv.text(cx - 6, cy - 7, 2, col, ch)
    cv.border(x, y, cell * 8, cell * 8, INK, 3)


def draw_flag_india(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3, (255, 153, 51))
    cv.fill_rect(x, y + h // 3, w, h // 3, WHITE)
    cv.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (19, 136, 8))
    cv.disc(x + w // 2, y + h // 2, h // 6, (6, 60, 150))
    cv.border(x, y, w, h, INK, 2)


def draw_flag_uzbek(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3, (0, 153, 181))
    cv.fill_rect(x, y + h // 3, w, h // 3, WHITE)
    cv.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (30, 181, 58))
    cv.fill_rect(x, y + h // 3 - 2, w, 3, (206, 17, 38))
    cv.fill_rect(x, y + 2 * h // 3 - 2, w, 3, (206, 17, 38))
    cv.disc(x + w // 5, y + h // 6, h // 9, WHITE)
    cv.border(x, y, w, h, INK, 2)


def draw_ship(cv, x, y, w):
    # hull
    cv.triangle([(x, y), (x + w, y), (x + w - 26, y + 34)], DARK)
    cv.fill_rect(x + 8, y, w - 34, 34, DARK)
    cv.fill_rect(x + 8, y, w - 34, 6, (70, 76, 88))
    # superstructure + funnel + mast
    cv.fill_rect(x + w // 2 - 10, y - 34, 70, 34, (88, 92, 100))
    cv.fill_rect(x + w // 2 + 66, y - 52, 14, 52, (60, 64, 72))
    cv.line(x + w // 2 - 30, y - 34, x + w // 2 - 30, y - 74, (200, 200, 200), 3)
    # flames amidships, rising from the deck
    for (fx, fw, fh) in ((x + w // 2 - 46, 30, 46), (x + w // 2 - 8, 24, 62),
                         (x + w // 2 + 22, 26, 40)):
        cv.triangle([(fx, y), (fx + fw // 2, y - fh),
                     (fx + fw, y)], ORANGE)
        cv.triangle([(fx + 6, y), (fx + fw // 2, y - fh + 18),
                     (fx + fw - 6, y)], YELLOW)
    # smoke (kept low and right of the flames so it clears the sub text)
    for (sx, sy, sr) in ((x + w // 2 - 20, y - 80, 14),
                         (x + w // 2 + 6, y - 105, 18),
                         (x + w // 2 + 30, y - 130, 22)):
        cv.disc(sx, sy, sr, SMOKE)
    cv.text_c(x + w // 2, y + 10, 2, WHITE, "MERKURY")


def draw_building(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (120, 122, 128))
    cv.fill_rect(x, y, w, 8, (88, 90, 96))
    for r in range(2):
        for c in range(4):
            cv.fill_rect(x + 10 + c * 28, y + 14 + r * 22, 18, 16,
                         YELLOW if (r + c) % 3 == 0 else (52, 56, 64))
    cv.triangle([(x + w // 2 - 26, y), (x + w // 2, y - 30),
                 (x + w // 2 + 26, y)], ORANGE)
    cv.disc(x + w // 2 - 44, y - 30, 11, SMOKE)
    cv.disc(x + w // 2 + 48, y - 40, 12, SMOKE)


def draw_train(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, TEAL)
    cv.fill_rect(x, y, w, 8, (12, 84, 76))
    cv.fill_rect(x + 16, y + 18, 52, 22, (210, 235, 240))
    cv.fill_rect(x + w - 68, y + 18, 52, 22, (210, 235, 240))
    cv.disc(x + w // 2, y + 30, 10, GOLD)
    cv.fill_rect(x, y + h - 8, w, 8, (12, 84, 76))
    cv.line(x - 14, y + h + 12, x + w + 14, y + h + 12, INK, 3)
    cv.line(x - 14, y + h + 22, x + w + 14, y + h + 22, INK, 3)


def draw_flame(cv, cx, y, s):
    cv.triangle([(cx - 34 * s, y), (cx, y - 78 * s),
                 (cx + 34 * s, y)], ORANGE)
    cv.triangle([(cx - 20 * s, y), (cx, y - 52 * s),
                 (cx + 20 * s, y)], YELLOW)
    cv.triangle([(cx - 10 * s, y), (cx, y - 28 * s),
                 (cx + 10 * s, y)], (255, 240, 180))
    cv.fill_rect(cx - 52 * s, y, 104 * s, 6, DARK)


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.fill_rect(0, 0, W, 96, NAVY)
    cv.text_c(W // 2, 14, 5, WHITE, "THE WORLD IN ONE DAY")
    cv.text_c(W // 2, 64, 2, GOLD, "TUESDAY \u00b7 24 NOVEMBER 2026")
    cv.fill_rect(0, 96, W, 6, RED)

    # ---- hero: chess -------------------------------------------- x16 y112
    cv.fill_rect(16, 112, 616, 380, WHITE)
    cv.border(16, 112, 616, 380, INK, 3)
    cv.text(32, 128, 2, RED, "GENEVA \u00b7 WORLD CHESS CHAMPIONSHIP \u00b7 GAME 1")
    draw_board(cv, 32, 168, 33)
    cv.text(316, 168, 4, INK, "GUKESH")
    cv.text(316, 204, 4, INK, "v SINDAROV")
    draw_flag_india(cv, 316, 252, 64, 40)
    cv.text(392, 264, 2, INK, "INDIA")
    draw_flag_uzbek(cv, 316, 306, 64, 40)
    cv.text(392, 318, 2, INK, "UZBEKISTAN")
    cv.text(316, 362, 3, RED, "YOUNGEST TITLE")
    cv.text(316, 392, 3, RED, "MATCH EVER")
    cv.text(316, 432, 2, INK, "$2.5M PRIZE FUND")
    cv.text(32, 452, 2, GREY, "SINDAROV PLAYS WHITE \u00b7 GUKESH BLACK")

    # ---- warship panel ------------------------------------------ x648 y112
    cv.fill_rect(648, 112, 360, 380, SEA)
    cv.border(648, 112, 360, 380, INK, 3)
    cv.text(664, 128, 2, GOLD, "WAR AT SEA")
    cv.block(664, 156, 3, WHITE, "UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA",
             328, lead=26)
    cv.block(664, 244, 2, GOLD, "CORVETTE MERKURY ABLAZE AT BENGHAZI",
             328, lead=20)
    cv.fill_rect(664, 292, 328, 4, SEA_LT)
    draw_ship(cv, 676, 420, 304)
    cv.fill_rect(664, 458, 328, 18, SEA_LT)
    cv.text(664, 466, 1, WHITE, "KYIV CLAIMS DRONE STRIKE")

    # ---- row B: three panels ------------------------------------ y508 h284
    panels = [
        (16, "UKRAINE", "RUSSIAN STRIKES KILL 15 IN KYIV REGION",
         "DRONE HITS A HOME IN DYMER \u00b7 14 MISSING", "building"),
        (352, "INDIA \u00b7 NEPAL", "MODI, NEPAL PM FLAG OFF NEW TRAIN",
         "SARYU-KAMALA EXPRESS LINKS AYODHYA AND JANAKPUR", "train"),
        (688, "INDONESIA", "24 DEAD IN INDONESIA FACTORY FIRE",
         "CANDY PLANT IN BANTEN \u00b7 ABOUT 30 STILL MISSING", "flame"),
    ]
    for (px, kick, head, sub, art) in panels:
        cv.fill_rect(px, 508, 320, 284, WHITE)
        cv.border(px, 508, 320, 284, INK, 3)
        cv.text(px + 16, 524, 2, RED, kick)
        cv.block(px + 16, 550, 3, INK, head, 288, lead=26)
        cv.block(px + 16, 636, 2, GREY, sub, 288, lead=20)
        if art == "building":
            draw_building(cv, px + 96, 724, 128, 56)
        elif art == "train":
            draw_train(cv, px + 56, 716, 208, 48)
        else:
            draw_flame(cv, px + 160, 776, 1)

    # ---- in brief strip ----------------------------------------- y808
    cv.fill_rect(16, 808, 992, 168, NAVY)
    cv.border(16, 808, 992, 168, INK, 3)
    cv.text(32, 822, 2, GOLD, "IN BRIEF")
    briefs = [
        (32, 852, "COP31 FALLOUT: FOCUS SHIFTS TO COP32 IN ADDIS ABABA"),
        (520, 852, "IRAN VOWS TO COUNTER US BLOCKADE OF HORMUZ"),
        (32, 916, "NVIDIA SOARS AS HUANG RETURNS AS CEO"),
        (520, 916, "INDIA, CHINA HOLD BORDER TALKS IN ARUNACHAL"),
    ]
    for (bx, by, txt) in briefs:
        cv.text(bx, by, 2, GOLD, "\u00b7")
        cv.block(bx + 20, by, 2, WHITE, txt, 440, lead=20)

    cv.text_c(W // 2, 988, 1, GREY,
              "DRAWN FROM REPORTS OF TUESDAY 24 NOVEMBER 2026")
    return cv


def png_bytes(cv):
    raw = b"".join(b"\x00" + bytes(cv.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
