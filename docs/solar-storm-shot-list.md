# Solar Storm — approved 10-minute shot list

This is the production lock for the approved narration. It maps the 30 master
assets to approximately 78 visual shots. A visual shot changes every 4–8
seconds; it is not a new narration chapter.

## Asset rule

Existing `scene_XX_*.png` files are immutable master images. For the 18 masters
listed below, create only these non-destructive child variants in
`assets/solar_storm_documentary/variants/`:

`scene_XX_<slug>_medium.png` and `scene_XX_<slug>_close.png`.

Use a meaningful 16:9 reframing of the original at 1920x1080; do not invent
objects, change factual content, add text, or modify the master image. The
remaining 12 masters are single-shot assets and receive FFmpeg motion only.

| Master | Required variants | Focus |
|---|---|---|
| 02 serene sun | medium, close | solar texture, tiny Earth |
| 03 sunspot loops | medium, close | sunspot and coronal loops |
| 06 interplanetary transit | medium, close | CME path and Earth |
| 07 earth magnetosphere | medium, close | shield and incoming particles |
| 10 telegraph office | medium, close | operators, red aurora |
| 11 telegraph sparks | medium, close | telegraph key and sparks |
| 12 modern Earth orbit | medium, close | city network and satellites |
| 14 cargo ship night | medium, close | ship and navigation detail |
| 15 aircraft cockpit aurora | medium, close | cockpit and aurora |
| 16 datacenter servers | medium, close | racks and fibre detail |
| 17 power substation | medium, close | transformers and lines |
| 18 power transformer | medium, close | transformer and induced current |
| 19 city rolling blackout | medium, close | lit/dark districts |
| 20 financial NOC | medium, close | clock/network infrastructure |
| 21 city skyline aurora | medium, close | skyline and aurora |
| 23 space weather center | medium, close | analyst and displays |
| 26 power-grid control room | medium, close | operator and wall display |
| 28 emergency preparedness | medium, close | flashlight, radio, battery |

## Chapters and visual shots

`W` means the original master wide framing. `M` and `C` mean the required
medium and close child variants. Reuse is permitted only when the narration
focus and motion direction differ.

| Chapter / target | Visual shots in order |
|---|---|
| 01 — 0:00–0:30 Hook | 01-W slow push; 01-W Earth detail crop; 01-W presenter crop; 01-W title hold |
| 02 — 0:30–1:00 The calm Sun | 02-W; 02-M solar surface; 02-C texture; 02-W tiny-Earth detail |
| 03 — 1:00–1:30 Sunspots and flare | 03-W; 03-M sunspot; 03-C coronal loops; 04-W flare rise |
| 04 — 1:30–2:00 CME | 04-W flare detail; 05-W CME expansion; 05-W plasma edge; 06-W Sun-to-Earth scale |
| 05 — 2:00–2:30 Travel time | 06-M CME path; 06-C Earth arrival end; 06-W reverse drift; 05-W departing plasma |
| 06 — 2:30–3:00 Earth’s shield | 07-W; 07-M shield; 07-C particle deflection; 08-W compression |
| 07 — 3:00–3:30 Aurora and 1859 | 08-W compressed field detail; 09-W aurora; 10-W office; 10-M operators |
| 08 — 3:30–4:00 Telegraph to digital world | 10-C red-sky window; 11-W key; 11-M sparks; 11-C brass contact; 12-W modern Earth |
| 09 — 4:00–4:30 Satellites and GPS | 12-M city network; 12-C satellite detail; 13-W satellite; 14-W cargo ship; 14-M navigation detail |
| 10 — 4:30–5:00 Aviation and internet | 15-W aircraft; 15-M cockpit; 15-C aurora outside; 16-W data center; 16-M server aisle |
| 11 — 5:00–5:30 What the internet depends on | 16-C fibre/server detail; 16-W slow pull; 17-W substation; 17-M transformer yard |
| 12 — 5:30–6:00 Power-grid risk | 17-C transmission detail; 18-W transformer; 18-M induced-current detail; 18-C equipment close-up |
| 13 — 6:00–6:30 A city losing power | 19-W city-wide view; 19-M flickering district; 19-C dark streets; 19-W slow pull-out |
| 14 — 6:30–7:00 Hidden systems | 20-W NOC; 20-M synchronized systems; 20-C clock/network detail; 12-C city-network callback |
| 15 — 7:00–7:30 Modern warning signs | 21-W city aurora; 21-M skyline; 21-C aurora detail; 22-W low-orbit satellite; 22-W atmosphere drag detail |
| 16 — 7:30–8:00 Monitoring the Sun | 23-W center; 23-M analyst; 23-C display detail; 24-W observatory craft; 25-W CME model |
| 17 — 8:00–8:30 Protecting systems | 25-W model detail; 26-W control room; 26-M operator; 26-C control-display detail; 27-W magnetic shield |
| 18 — 8:30–9:00 What people can do | 27-W hopeful hold; 28-W preparedness kit; 28-M flashlight/radio; 28-C battery detail |
| 19 — 9:00–9:30 Reflection | 29-W sunrise; 29-W Earth-atmosphere detail; 02-W calm-Sun callback; 29-W slow pull-out |
| 20 — 9:30–10:00 Mamase ending | 29-W final horizon; 30-W cyan planet; 30-W orbital-light detail; 30-W final logo-safe hold |

## Handoff to Antigravity

1. Generate exactly 36 child variants in the listed `variants/` directory.
2. Validate every child as PNG, 1920x1080, and keep the master aspect/story.
3. Write `docs/solar-storm-child-asset-manifest.md` with source master, child
   filename, dimensions, bytes, and crop focus.
4. Do not build a ZIP, alter narration, change master files, or edit application
   code, configuration, agent instructions, or skills.
