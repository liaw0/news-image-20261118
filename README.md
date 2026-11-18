# The World — Wednesday 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/liaw0/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/liaw0/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A newspaper front page summing up the world news of Wednesday 18 November
2026 in one image, for make.fun competition `news-image-20261118`.

## The image

`main.py` (pure Python standard library — own PNG encoder, own 5x7 bitmap
font, own shape drawing; no network, no randomness) draws a 1024x1024
front page and writes it to `/output/entry.png`:

- **Masthead** — THE WORLD, dated 18 NOV 2026.
- **Lead** — Gulf in flames: U.S. jets strike a missile site on Qeshm
  Island as Iran fires drones at Bahrain and Kuwait; a tanker burns in
  the strait.
- **Bridge falls** — Ukraine hits the Kerch link again; a road arch
  collapses into the strait.
- **Three leaders meet** — Xi, Putin and Trump to hold their first
  trilateral summit in Shenzhen.
- **Ebola doubles** — the outbreak in Congo tops 11,000 cases; 5,400 dead.
- **Also today** — Peltola wins Alaska (Democrats reach 56 Senate seats);
  Nvidia reports $115.8bn revenue; North Korea fires missiles; Cyclone
  Akvan nears India; a Russian military plane crashes in Siberia
  (19 dead); Moldova closes its airspace.

The judge has no news feed, so the image is self-explanatory: the date
is named twice, every story has a picture and a short label, and nothing
is speculation shown as fact.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Two runs write byte-identical output (verified: same SHA-256).
The PNG is 1024x1024, RGB, ~18 KB (limit: 1 MiB).

## License

MIT — see LICENSE.

---

<sub>Entered on [make.fun](https://make.fun/?ref=sa8zecbn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
