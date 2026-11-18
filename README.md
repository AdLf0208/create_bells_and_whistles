# Bells & Whistles for Horizon — the decorative station and metro blocks

A Horizon port of **Create: Bells & Whistles 0.4.7-1.21.1** (`bellsandwhistles`, GPL-3.0-or-later)
carrying the mod's **36 decorative blocks** and their items, loot, recipes, tags and creative tab.

- **Class / tier:** content / data (`ports/ledger.csv`). The carried slice is the whole mod at
  0.4.7: it ships no block entity, entity, menu, renderer, config or network code.
- **Licence:** GPL-3.0-or-later, rank 1 — publishable under the same licence with the complete
  corresponding source. `LICENSE` + `LICENSE-NOTICE.md` travel inside this package.
- **Format:** one flat SDK package (mod API `0.2`) built against the SDK for Horizon
  `0b14f8acfd97fa2c750e42795249dcc981178ca4` and horizon-mixins
  `e59da9094f0c2fdda6c627fe9eff22dec6a906f0`, for Minecraft 26.3.

## The package

One file, `bellsandwhistles.hmod`: `horizon-mod.toml`, `Cargo.toml`, `src/lib.rs` (the one
`impl mod_api::Hooks`), `src/runtime.rs` (the pure catalogue and its 10 tests), the carried
`assets/` + `data/` (204 asset files and 119 data files) and the licence.

## What it does in game

36 blocks in one creative tab (`Bells & Whistles`, icon `bellsandwhistles:metal_pilot`):

| Family | Blocks | Vanilla template |
|---|---|---|
| Grab rails, bogie steps, door steps | 3 × 3 | `minecraft:ladder` |
| Headlight | 1 | `minecraft:lever` (light 15) |
| Trapdoors | 3 | `minecraft:iron_trapdoor` |
| Station platform | 1 | `minecraft:carved_pumpkin` |
| Metro casings | 2 | `minecraft:iron_block` |
| Metro panels | 2 | `minecraft:end_rod` |
| Pilots | 18 | `minecraft:carved_pumpkin` |

Every block has an item, a self-drop loot table and its place in the tab. The six metal rails are
`#minecraft:climbable`; 27 stone/metal blocks are `#minecraft:mineable/pickaxe`. 44 recipes are
carried with the Create materials mapped to vanilla ones (see `notes.md`), and the nine
Create-only polished-cut pilots are creative-only because no vanilla item stands in for them.

The blocks copy **vanilla** templates because the original's Create classes are not here: the
headlight is a lever (so it has a `powered` state and toggles on right click; the model ignores
it), the platform and pilots face horizontally, and the panels face six ways.

## Working on it

```sh
# the pure catalogue, without the game
cargo test
cargo clippy --all-targets -- -D warnings
cargo fmt --check

# the package (the SDK is fetched into .horizon/sdk/ on first use and never packed)
rm -f Cargo.lock
cargo horizon-mod build                 # -> target/horizon-mod/bellsandwhistles.hmod
cargo horizon-mod check bellsandwhistles.hmod
cargo horizon-mod fits bellsandwhistles.hmod --build nightly
```

The content is carried from the jar and must stay unchanged; `tools/gen_content.py` rebuilds it
from the inventory in `FINDINGS.md` and `src/runtime.rs`. `tools/validate_content.py` checks every
template state, model, texture, loot table and recipe statically. Scope, gaps, deviations and the
verification ladder: [`notes.md`](notes.md); the upstream inventory: [`FINDINGS.md`](FINDINGS.md).
