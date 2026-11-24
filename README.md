# makefun-news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/algifarri/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/algifarri/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single-page newspaper poster that sums up Tuesday 24 November 2026:
Game 1 of the World Chess Championship begins in Geneva (Gukesh v
Sindarov, both 20, the youngest title match in history), Ukraine says it
sank the Russian corvette Merkury off Libya, Russian strikes kill 15 in
the Kyiv region, Modi and Nepal's PM flag off the Saryu-Kamala Express,
24 dead in the Indonesia factory fire, and four items in brief. The
picture is drawn from scratch at run time — no stock photo, no downloaded
asset, no network at all.

## How it is drawn

`main.py` is a small pure-stdlib Python program. It carries its own
5×7 bitmap letterface, a tiny rasteriser (rectangles, discs, triangles,
lines), and a hand-rolled PNG writer built on `zlib` and `struct`. Every
run produces the exact same bytes, because nothing in the program reads
the clock, the network, or any random source.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png`, a 1024×1024 PNG under 1 MiB.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ajkq5baq&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
