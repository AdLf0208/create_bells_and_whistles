# Create: Bells & Whistles — a Horizon port

**Create: Bells & Whistles** is a Minecraft mod. Immersive detailing for the Create ecosystem. This repository is a **port of it to [Horizon](https://github.com/horizon-rust/horizon)**, the Rust engine for Minecraft Java 26.3. It carries the complete source of the port plus the content files it ships, and installs as a single `.hmod` package.

Upstream: [aesefficio/BellsAndWhistlesMod](https://github.com/aesefficio/BellsAndWhistlesMod) — licence **GPL-3.0-or-later**.

| | |
|---|---|
| Upstream mod | Create: Bells & Whistles ([source](https://github.com/aesefficio/BellsAndWhistlesMod)) |
| Ported to | Horizon 0b14f8a, Minecraft Java 26.3, mod API `0.2` |
| Package | `bellsandwhistles.hmod` (install it with the Horizon launcher) |
| Licence | **GPL-3.0-or-later** — the upstream mod's licence; see [Licence and credit](#licence-and-credit) |

## What this port implements

| # | id | template | states | light | tags | recipes |
| 1 | `andesite_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 2 | `brass_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 3 | `copper_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 4 | `andesite_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 5 | `brass_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 6 | `copper_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 7 | `andesite_door_step` | `minecraft:ladder` | 8 | 0 | — | 2 |
| 8 | `brass_door_step` | `minecraft:ladder` | 8 | 0 | — | 2 |

## Not yet ported

- **Create is not ported.** The wrench behaviour, Create's panel placement
- **The headlight uses `minecraft:lever`.** Its `powered` state and
- **Custom shapes** for the rails, headlight and pilots are not declared.
- **Nine pilots have no recipe** (Create's polished-cut stones).
- **Recipe materials are substituted** (see the map above); the recipes are
- **Stonecutting recipes are carried but not crafted in the e2e.** The
- **No block entity, entity, menu, renderer, config or network code** — the
- **The creative tab's position** differs from upstream (which inserts into

## Installing

1. Install the [Horizon launcher](https://github.com/horizon-rust/horizon/releases) (0.2.70 or newer).
2. Add `bellsandwhistles.hmod` to the instance's mods.
3. The package is pinned to a specific Horizon build; the launcher checks that pin.

## Licence and credit

Create: Bells & Whistles was created by its upstream authors; the code, models and assets in the original mod
remain theirs and are used here under **GPL-3.0-or-later**. The Rust in this repository is a clean-room
rewrite for Horizon, not a translation of the original source.

- `LICENSE` — the upstream licence text.
- `LICENSE-NOTICE.md` — what this port carries and where it came from.
- The upstream project: https://github.com/aesefficio/BellsAndWhistlesMod

## Technical details

```
horizon-mod.toml   package manifest (id, version, api, [native] pin)
Cargo.toml         the crate; depends on `horizon-mod-api` from the fetched SDK
src/               lib.rs (the one `impl Hooks`), runtime.rs (pure logic + tests), glue
assets/ data/      the content the package ships
tools/             content generators and the e2e scenario
```

- Build: `cargo horizon-mod build` (packages; it does not compile against the game).
- Test: `cargo test`, `cargo clippy --all-targets -- -D warnings`.
- In-game: `ports/tools/launcher-game.sh run bellsandwhistles` in the campaign tree, or install the
  `.hmod` and play; the harness scenario is `tools/e2e.sh`.

This repository is generated from the campaign's port at `ports/bellsandwhistles/`; the port's own
`notes.md` is the full record (decisions, traps, evidence).
