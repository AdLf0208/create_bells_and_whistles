# Bells & Whistles — port notes

Ported from **Create: Bells & Whistles 0.4.7-1.21.1**
(`sudoLev/BellsAndWhistlesMod`, release tag `v0.4.7`, commit
`fb2e040f70ddaf8d98101c6bd484ad597954e804`) for Minecraft Java 26.3 on
Horizon **c9d474d** / horizon-mixins **d9c83d7**. Upstream analysis:
[`FINDINGS.md`](FINDINGS.md).

**Licence: GPL-3.0** (`gradle.properties:mod_license=GPL-3.0`; the repository
`LICENSE` is the GPL v3 text; the campaign source map records
`GPL-3.0-or-later`). The port ships the upstream mod's own textures, models and
lang under that licence. It is **local-only until the maintainer approves
publishing** (ARCHITECTURE.md §8).

> **2026-11-18 — migrated to the SDK format (mod API 0.2), version 0.2.0.**
> Horizon's mod-API merge retired `.hnmod`; this port is now one flat
> `bellsandwhistles.hmod` (36 blocks and their data + `src/lib.rs`) built against
> SDK `0b14f8a` / mixins `e59da90`. `src/runtime.rs` is byte-identical to the
> retired bundle and the content is the same 323 files. The retired tree is in
> `ports/_shared/evidence/bellsandwhistles/retired-hnmod-0.1.0/`; the recipe,
> ladder, traps and changelog are in
> [`## Migration to the SDK format (0.2.0)`](#migration-to-the-sdk-format-020-2026-11-18)
> at the end of this file. The e2e section below is **historical** (0.1.0,
> `--dev-mod content/`): no launcher is installed, so the 0.2.0 package was not
> re-run in game.

Status: **slice 1 implemented and verified in-game (0.1.0).** The slice is content
only: the 36 decorative blocks `ModBlocks` registers, their block items,
self-drop loot, the 44 recipes that 26.3 can express, the climbable and
pickaxe tags, and one creative tab. There is no block entity, entity, menu,
renderer, config or network code. The test-only catalogue model pins the
content (10/10 tests, clippy clean); the `.hmod` builds and checks; the e2e
passes in default, counterfactual and negative modes. The staged ladder
reached `stage` (exit 0); `check` was killed by the campaign-wide
`clean-targets.sh` race (exit 143) and is requeued, so `test`, `build` and
`ctl` are still pending (see the environment note below).

**0.2.0 (SDK package) status:** compile-and-test verified — `cargo test` 10/10, clippy
0 warnings, `fmt --check` clean, `cargo horizon-mod check` and `fits` exit 0, two builds
byte-identical. Not re-run in game: no `horizon-launcher` here (gap 10 in the migration
section).

## Scope: what is in the slice

`ModBlocks.java:23-102` registers **36** blocks and `ModItems.java` registers no
standalone items, so every item is a block item. Upstream's own tab
(`ModCreativeModeTabs.java:19-62`) lists exactly those 36, in this order:

| # | id | template | states | light | tags | recipes |
|---|---|---|---:|---:|---|---:|
| 1 | `andesite_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 2 | `brass_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 3 | `copper_bogie_steps` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 4 | `andesite_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 5 | `brass_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 6 | `copper_grab_rails` | `minecraft:ladder` | 8 | 0 | climbable | 2 |
| 7 | `andesite_door_step` | `minecraft:ladder` | 8 | 0 | — | 2 |
| 8 | `brass_door_step` | `minecraft:ladder` | 8 | 0 | — | 2 |
| 9 | `copper_door_step` | `minecraft:ladder` | 8 | 0 | — | 2 |
| 10 | `ornate_iron_trapdoor` | `minecraft:iron_trapdoor` | 64 | 0 | pickaxe | 1 |
| 11 | `headlight` | `minecraft:lever` | 24 | **15** | pickaxe | 2 |
| 12 | `station_platform` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 2 |
| 13 | `metro_casing` | `minecraft:iron_block` | 1 | 0 | pickaxe | 1 |
| 14 | `corrugated_metro_casing` | `minecraft:iron_block` | 1 | 0 | pickaxe | 1 |
| 15 | `metro_panel` | `minecraft:end_rod` | 6 | 0 | pickaxe | 2 |
| 16 | `corrugated_metro_panel` | `minecraft:end_rod` | 6 | 0 | pickaxe | 2 |
| 17 | `metro_trapdoor` | `minecraft:iron_trapdoor` | 64 | 0 | pickaxe | 1 |
| 18 | `metro_window` | `minecraft:iron_trapdoor` | 64 | 0 | pickaxe | 1 |
| 19 | `andesite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 20 | `brass_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 21 | `copper_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 22 | `metal_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 23 | `polished_andesite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 2 |
| 24 | `polished_granite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 2 |
| 25 | `polished_diorite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 2 |
| 26 | `polished_deepslate_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 2 |
| 27 | `polished_dripstone_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 28 | `polished_tuff_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 29 | `polished_calcite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 30 | `polished_limestone_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 31 | `polished_scoria_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 32 | `polished_scorchia_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 33 | `polished_crimsite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 34 | `polished_ochrum_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 35 | `polished_veridium_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |
| 36 | `polished_asurine_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 0 |

State total: 9×8 + 3×64 + 1×24 + 19×4 + 2×6 + 2×1 = **378**.

## Content adaptations to 26.3

1. **Templates.** Horizon has no Create, so each Create-derived class maps to
   the vanilla class it extends: `MetalLadderBlock` → `minecraft:ladder`
   (facing + waterlogged, climbable), `TrainTrapdoorBlock` /
   `TrapDoorBlock` → `minecraft:iron_trapdoor`, `PilotBlock` /
   `PlatformBlock` → `minecraft:carved_pumpkin` (horizontal facing),
   `PanelBlock` → `minecraft:end_rod` (six-way facing), plain casings →
   `minecraft:iron_block`, and the face-attached headlight → the only vanilla
   face-attached-horizontal block without a menu, `minecraft:lever`.
2. **The headlight's lever state.** Upstream's headlight has `face` ×
   `facing` (12 states). The lever template adds `powered` (24 states), so the
   blockstate binds all 24 and right-click toggles the lever state (and its
   redstone output). The model ignores `powered`; the light is a constant 15
   from the block declaration. This is the price of the missing vanilla
   face-attached block; `minecraft:grindstone` was rejected because its
   right-click opens a grindstone menu.
3. **Shapes.** Only the station platform and the panels declare `shapes`: the
   platform's upstream `SHAPE` rotated by the blockstate's y quarter turns,
   and Create's `CASING_3PX` three-pixel plate per facing. The rails,
   headlight and pilots keep the template shape (the pilot's upstream boxes
   extend outside the block, from y=-12 to 14).
4. **Recipes: Create materials mapped.** 26.3 has no Create items, so the
   carried recipes substitute vanilla materials and are documented here:
   `create:andesite_alloy` → `minecraft:andesite`; `c:ingots/brass` and
   `create:brass_sheet` → `minecraft:copper_ingot`; `c:nuggets/brass`,
   `create:brass_nugget` and `create:copper_nugget` →
   `minecraft:copper_nugget`; `c:ingots/copper` / `create:copper_sheet` →
   `minecraft:copper_ingot`; `create:iron_sheet` → `minecraft:iron_ingot`;
   `create:ornate_iron_window` → `minecraft:iron_bars`; `c:glass` →
   `minecraft:glass`; `create:polished_cut_{andesite,deepslate,diorite,
   granite,tuff}` and their stairs → the vanilla `polished_*` block and
   stairs. The nine Create-only polished-cut stones (asurine, calcite,
   crimsite, dripstone, limestone, ochrum, scoria, scorchia, veridium) have
   **no** recipe, because no vanilla item stands in for them.
5. **Recipe files are flat.** 26.3 reads `data/<ns>/recipe/*.json`; upstream's
   nested folders are flattened and the two `door_steps/<metal>_grab_rails`
   recipes take their output's name (`<metal>_door_step`). 44 of upstream's
   52 recipes are carried.
6. **Loot `random_sequence`.** Upstream writes
   `"random_sequence": "minecraft:blocks/acacia_log"` in almost every table
   (a datagen copy-paste); the port writes
   `bellsandwhistles:blocks/<id>` and uses 26.3's pool-level `condition`.
7. **Tags.** `#minecraft:climbable` gets the six rail blocks and
   `#minecraft:mineable/pickaxe` the 27 stone/metal blocks, exactly as
   upstream's `BlockTagProvider` does. `"replace": false` is dropped: 26.3
   merges tags from every namespace.
8. **Assets.** Blockstates and models are the upstream files; the NeoForge
   `render_type` field is dropped (26.3 decides transparency from the sprite,
   as vanilla's ladder model does) and the 1.21 `models/item/*.json` files
   are referenced from 26.3's `items/*.json` model definitions. Textures and
   the seven lang files are copied byte for byte.
9. **Creative tab.** Horizon has no vanilla-tab insertion, so the mod has one
   tab (`Bells & Whistles`, icon `bellsandwhistles:metal_pilot`) listing the
   same 36 blocks in the same order.

## Runtime

[`mixins/bellsandwhistles/runtime.rs`](mixins/bellsandwhistles/runtime.rs) is a
test-only catalogue (`Template`, `Block`, `BLOCKS`) that the content generator
and the notes read from. It has **10 tests**: 36 unique valid ids, every block
has an item and a self-drop, only the headlight emits light (15), the climbable
set is the six rails, the pickaxe set is the 27 stone/metal blocks, the
templates' state spaces total 378, the nine Create-only pilots have no recipe,
27 blocks carry 44 unique recipes, and every recipe stem names a known block.
There is no gameplay hook, so the bundle has one `[[module]]` and no
`[[injection]]`.

Skills: superpowers/using-superpowers,brainstorming,writing-plans,test-driven-development,systematic-debugging,verification-before-completion; BeautifulRust/rust-best-practices,rust-port

## Verification

### Runtime (standalone crate)

| Command | Result |
|---|---|
| `cargo fmt` / `cargo fmt --check` | exit 0 |
| `cargo test --locked --offline` | exit 0, **10 passed; 0 failed** |
| `cargo clippy --all-targets --locked --offline -- -D warnings` | exit 0, **0 warnings** |

### Staged pin (`stage → check → test → build`)

| Step | Command | Result |
|---|---|---|
| stage | `tools/horizon.py stage` | exit 0, `staging_seconds: 367`, `stage_changed: true` at c9d474d |
| check | `tools/horizon.py check` | **exit 143 (SIGTERM)**: the shared `ports/tools/clean-targets.sh` deleted `target/mixins` and `target/horizon-cargo` while the check was compiling, then the transient unit was terminated. Requeued (`target/run-direct.sh`); see the environment note. |
| test | `tools/horizon.py test` | PENDING (queued behind check) |
| build | `tools/horizon.py build` | PENDING (queued) |

The runtime tests also run embedded under `game::bellsandwhistles::tests` once
the staged `test` step completes; the standalone 10/10 above is the same
module.

### Content

| Step | Command | Result |
|---|---|---|
| build | `cargo-horizon-mod build` (from `content/`) | exit 0, `target/horizon-mod/bellsandwhistles.hmod` |
| check | `cargo-horizon-mod check content/bellsandwhistles.hmod` | exit 0, `bellsandwhistles 0.4.7-1.21.1 (mod, API 0.2, both)`, **158,394 bytes**, SHA-256 `b36202e9…e6ac0af`, 324 files, unsigned, "no code: content only" |
| static | `tools/validate_content.py` | 36 blocks, 86 models: every template state binds, every model/texture resolves, every loot/recipe item exists |

Delivered `.hmod`: [`content/bellsandwhistles.hmod`](content/bellsandwhistles.hmod),
**158,394 bytes**, SHA-256
`b36202e93b59ca552c0d2add1c19d9bbc363f1db0bb598660499fe041e6ac0af`,
324 entries (323 asset/data files + `horizon-mod.toml`), unsigned, "no code:
content only".

### In-game e2e (`tools/e2e.sh`, offscreen renderer, The End)

The runs below use the **same pin's** fast binaries from
`ports/dyenamics/target/horizon-cargo/fast` (`CTL=`/`GAME=`), because the
shared cleanup killed this port's own staged build; the content is loaded with
`--dev-mod content/`, exactly as the final run does. The campaign already uses
this cross-port binary path for content ports (e.g. `supplementaries`' e2e
with `CTL=…/dyenamics/…`).

| Run | Result |
|---|---|
| default | **PASS** (`target/e2e-probe.log`): 378/378 states accepted, 36/36 blocks place and read back their default state, 36/36 items give, the tab lists 36, placement reads ladder north / lever wall+north / end rods up / trapdoors bottom / pumpkins horizontal, the six climbable rails and 27 pickaxe blocks are tagged (cross controls absent), the headlight emits 15 and a casing 0, eight blocks drop themselves, six recipes craft and four controls stay empty, unknown ids are refused |
| counterfactual (`COUNTERFACTUAL=1`) | **PASS** (`target/e2e-cf-probe.log`): 107/107 vanilla template states accepted, 6/6 templates place and read back, the six templates drop only themselves, five vanilla recipe grids craft nothing, unknown mod ids refused |
| negative (`COUNTERFACTUAL=1 NEGATIVE=1`) | **exit 1, as required**: the false claim "a vanilla ladder drops a Bells & Whistles item" fails (`NEGATIVE: the false claim failed as required (minecraft:ladder dropped no mod item)`) |

The probe log's final line still says "378 states bind" from the run before
the wording change; the check itself prints "378 states accepted by the
registry" and "36/36 blocks place and read back their default state".

### Environment note (staged ladder)

The host rebooted at 02:18 and the campaign-wide
`ports/tools/clean-targets.sh` ran while the first `check` was compiling: it
deletes every port's `target/mixins` (and with `--all` every
`target/horizon-cargo`), so the staged source and artifacts vanished and the
transient unit received SIGTERM (`check exit 143`). The ladder was requeued as
[`target/run-direct.sh`](target/run-direct.sh) under the campaign lock. The
runtime, content, `.hmod` and e2e evidence above do not depend on that build:
the e2e loads this port's `content/` with `--dev-mod` and uses the same pin's
fast binaries.

`ports/tools/clean-targets.sh --dry-run` was run at the end (69 G free before;
it would remove every port's `target/mixins` and incremental caches). The real
clean was left to the orchestrator: it is campaign-wide and 20 jobs were
building in parallel, so running it here would have deleted their staged
sources mid-build. This port's own `target/` is 7.8 MB; the delivered
`content/` and `.hmod` are outside it.

## Gaps and deviations

1. **Create is not ported.** The wrench behaviour, Create's panel placement
   helper and copycat face-hiding, and the train-door forms
   (`folding_metro_door`, `sliding_metro_door`) are deferred. The two door
   forms are not registered by `ModBlocks` at 0.4.7 anyway.
2. **The headlight uses `minecraft:lever`.** Its `powered` state and
   right-click toggle are a template artefact; the light is constant 15.
3. **Custom shapes** for the rails, headlight and pilots are not declared.
4. **Nine pilots have no recipe** (Create's polished-cut stones).
5. **Recipe materials are substituted** (see the map above); the recipes are
   not upstream's exact ingredients, because Create is absent.
6. **Stonecutting recipes are carried but not crafted in the e2e.** The
   crafting path is proved for six recipes; the stonecutter menu path is not
   exercised.
7. **No block entity, entity, menu, renderer, config or network code** — the
   slice is content only. That is the whole mod at this version: there is no
   gameplay logic to port.
8. **The creative tab's position** differs from upstream (which inserts into
   vanilla tabs); Horizon content mods cannot.
9. **Map colour** is the template's (upstream copied mossy cobblestone/stone
   map colours); it was not visually checked headless.

## Files

```
horizon-mod.toml                             the only manifest: id, version 0.2.0, api 0.2,
                                             side both, registries, [native] SDK pins
Cargo.toml                                   one crate, horizon-mod-api from .horizon/sdk/
bellsandwhistles.hmod                        delivered 331-entry SDK package (native + content)
assets/bellsandwhistles/                     36 blockstates, 45 block models,
                                             36 item models, 36 item definitions,
                                             44 textures, 7 lang files
data/bellsandwhistles/horizon/               36 block declarations, 1 tab
data/bellsandwhistles/loot_table/            36 self-drop tables
data/bellsandwhistles/recipe/                44 recipes
data/minecraft/tags/block/                   climbable, mineable/pickaxe
src/lib.rs                                   the one impl mod_api::Hooks (empty by design)
src/runtime.rs                               test-only catalogue, 10 tests, byte-identical
                                             to the retired mixins/bellsandwhistles/runtime.rs
LICENSE, LICENSE-NOTICE.md                   GPL-3.0-or-later, inside the package
README.md                                    inside the package
.gitignore                                   /target, /.horizon, /Cargo.lock
FINDINGS.md, notes.md                        the record
tools/gen_content.py                         reproduces assets/ and data/
tools/state_check.py                         the 378-state + default-placement check
tools/craft_check.py                         the recipe checks
tools/validate_content.py                    the static content/model/recipe check
tools/e2e.sh                                 default/counterfactual/SELFTEST, needs a
                                             launcher-built game
```

Retired with the `.hnmod` format and kept as evidence in
`ports/_shared/evidence/bellsandwhistles/retired-hnmod-0.1.0/`: `mixins/`,
`compatibility.json`, `rust-toolchain.toml`, `content/` (the 0.1.0 content package), `tools/horizon.py`.
`Cargo.lock` was deleted (never packed).

## Skills used

- Superpowers: `test-driven-development` (the catalogue tests were written
  first; the first run failed on `station_platform_stonecutter`, then went
  green), `systematic-debugging` (the shape-rotation index bug and the
  unnamespaced recipe ids were found by the static validator), and
  `verification-before-completion` (every claim below is a command output).
- Beautiful Rust:
  `ports/_shared/skills/BeautifulRust/skills/rust-best-practices/SKILL.md`;
  `cargo fmt`, `cargo clippy --all-targets --locked --offline -- -D warnings`
  and `cargo test --locked --offline` clean, no `allow`/`expect` needed.

## Migration to the SDK format (0.2.0, 2026-11-18)

Horizon's mod-API merge (#16941, launcher ≥ 0.2.70, PR #17992) retired `.hnmod`. This port had no
registry submission before the purge, so **0.2.0 is its first publication** — there is no closed
PR to supersede. One flat `bellsandwhistles.hmod` now carries the content *and* the code. Pins: SDK
nightly **`0b14f8acfd97fa2c750e42795249dcc981178ca4`** (2026-11-18, `package_format` 6,
`content_api` "0.2"), horizon-mixins **`e59da9094f0c2fdda6c627fe9eff22dec6a906f0`**, mod API
`0.2`. The SDK is cached in-tree at `ports/_shared/sdk/0b14f8a/`, copied into `.horizon/sdk/`
(gitignored, 21 MB) so the whole ladder stayed offline, and never packed.

**Done in this order.** The retired paths were moved to
`ports/_shared/evidence/bellsandwhistles/retired-hnmod-0.1.0/` **before** the first
`cargo horizon-mod build` (the tool refuses a project root holding retired package paths); then
`src/runtime.rs` was copied with `cp` and proved with `cmp` + `sha256sum`; `cargo test` ran on the
new crate **before any glue existed** (10/10); only then was the `impl Hooks` added (10/10 again).
There is no behaviour glue in this port, so no `todo!()` red run exists — see trap 3.

### Where the retired tree is, and the file map

| 0.1.0 path | 0.2.0 | Evidence |
|---|---|---|
| `mixins/bellsandwhistles/runtime.rs` | `src/runtime.rs`, **copied**, `cmp` + sha256 identical (`81f9989180c606736325087ef89ad5c7a42ce59a766cf3608f4f31fc34242199`), and identical inside the package | `retired-hnmod-0.1.0/mixins/bellsandwhistles/runtime.rs` |
| `mixins/bellsandwhistles/horizon-mixin.toml` (1 `[[module]]`, 0 `[[injection]]`) | no plan: `src/lib.rs` declares `pub mod runtime;` and the one `#[mod_api::horizon_mod] impl Hooks` (empty — nothing to hook) | `retired-hnmod-0.1.0/mixins/bellsandwhistles/` |
| `content/assets/` (204 files) | `assets/` — the same tree, moved with `mv`; byte-identical to the source and inside the package | `retired-hnmod-0.1.0/content-package-0.1.0/` (the unpacked 0.1.0 package) |
| `content/data/` (119 files) | `data/` — same | same |
| `content/horizon-mod.toml` (content-only, `api = "0.2"`, version `0.4.7-1.21.1`) | merged into the root `horizon-mod.toml`: `id`/`name`/`description`/`authors`/`api`/`side`/`capabilities` kept, `version` → **0.2.0**, plus `[native]` | `retired-hnmod-0.1.0/content/horizon-mod.toml` |
| `content/bellsandwhistles.hmod` (158,394 B content-only package) and `content/target/horizon-mod/…` | not needed: content is inside the one package | `retired-hnmod-0.1.0/content/` |
| `compatibility.json`, `rust-toolchain.toml` | `[native]` in `horizon-mod.toml` (`game = "26.3"`, both 40-hex commits); the pinned commit decides the toolchain | `retired-hnmod-0.1.0/` |
| `tools/horizon.py` (stage/check/test/build/ctl ladder) | deleted: staging, `.hnmod` packaging and the game build belong to the retired format | `retired-hnmod-0.1.0/tools-horizon.py` |
| `Cargo.lock` | deleted, never packed: it changes the artifact (trap 5) | not kept |

**Kept and updated:** `tools/e2e.sh` (now requires a launcher-built game, with an optional
`CONTROL_GAME` differential and `SELFTEST=1`), `tools/gen_content.py`, `tools/state_check.py`,
`tools/craft_check.py`, `tools/validate_content.py`, `notes.md`, `FINDINGS.md`, `LICENSE`,
`LICENSE-NOTICE.md` (new), `README.md` (new — it is packed inside the `.hmod`).

### Content diff (the "unchanged" evidence)

The content was **moved**, not copied: `git`-less tree, so the proof is two diffs.

- **New package vs the port root:** 323 files under `assets/` + `data/`; size list and sha256 list
  identical (`evidence/bellsandwhistles/sdk-entries.log`; the unpacked package was diffed file by
  file). The package's content *is* the source tree.
- **Retired 0.1.0 package vs the new root:** 322 of 323 files byte-identical. The one difference is
  `assets/bellsandwhistles/lang/ru_ru.json` — 7,841 B in the 0.1.0 package, 7,775 B in the tree
  (five corrected Russian lines: the three door steps, the ornate iron trapdoor and the station
  platform). The package was built at **01:51** and that file was edited at **03:52**, so the
  delivered 0.1.0 `.hmod` was already stale against its own source. The 0.2.0 package carries the
  **newer** file; the stale one was not restored (trap 2).

### Helper → hook table (every `[[module]]` and `[[injection]]` mapped)

| 0.1.0 | 0.2.0 | Mapping notes |
|---|---|---|
| `[[module]] runtime` (`crate::game::bellsandwhistles`) | `src/runtime.rs` as an ordinary module (`pub mod runtime;`) | `Template`, `Block`, `BLOCKS` and the 10 tests unchanged; `runtime.rs` is `#[cfg(test)]`-only, so the non-test crate is empty |
| *(no `[[injection]]`)* | `impl Hooks for Mod {}` — **empty by design** | the slice has no gameplay hook; the 36 blocks are registered from `data/<id>/horizon/block/*.json`, which needs no code |
| the `content` half as a separate `.hmod` loaded with `--dev-mod content` | the flat package's own `assets/` + `data/` | the retired format's content half and its load step are gone |
| `game.native_*` calls | none | there were none to map: the module was test-only |

### The ladder (measured 2026-11-18)

Every compile ran in a `ports/tools/build-slot.sh` lease with `BUILD_LOCAL=1` (trap 6),
`CARGO_INCREMENTAL=0`, no `--target-dir`, and the `cd` inside the wrapped command.

| Step | Command | Result | Evidence |
|---|---|---|---|
| runtime only, no glue | `cargo test --offline` | **10 passed**, 0 failed | `sdk-test-runtime-only.log` |
| tests with the `impl Hooks` | `cargo test --offline` | **10 passed**, 0 failed (0 doc-tests) | `sdk-test.log` |
| lints | `cargo clippy --all-targets --offline -- -D warnings` | exit 0, **0 warnings** | `sdk-clippy.log` |
| format | `cargo fmt --check` (**not** `--all`) | exit 0, empty diff | `sdk-fmt.log` |
| package | `rm -f Cargo.lock && cargo horizon-mod build` | `SDK 0b14f8a (build 0b14f8acfd97fa2c750e42795249dcc981178ca4) in ./.horizon/sdk` / `Built ./target/horizon-mod/bellsandwhistles.hmod` | `sdk-build.log` |
| registry check | `cargo horizon-mod check bellsandwhistles.hmod` | **EXIT 0**, verbatim below | `sdk-check.log` |
| fits | `cargo horizon-mod fits bellsandwhistles.hmod --build nightly` | `0b14f8a  made for`, **EXIT 0** | `sdk-fits.log` |
| second build | `rm -f Cargo.lock && cargo horizon-mod build` | identical bytes (`cmp`), same sha256 | `sdk-build-second.log`, `sdk-sha256.log` |
| runtime untouched | `unzip -p bellsandwhistles.hmod src/runtime.rs \| sha256sum` | `81f99891…2199` = the retired file | `sdk-sha256.log` |
| static content | `python3 tools/validate_content.py` | `blocks=36 models=86` / `OK: every template state binds, every model/texture resolves, every loot/recipe item exists` | this run |
| clean-target re-run | `cargo test --offline` after `rm -rf target` | **10 passed**, 0 failed, from scratch (1m 28s) | `sdk-test-final-clean-target.log` |

```
$ cargo horizon-mod check bellsandwhistles.hmod
bellsandwhistles 0.2.0 (native-mod, format native-1/0b14f8acfd97fa2c750e42795249dcc981178ca4/e59da9094f0c2fdda6c627fe9eff22dec6a906f0, for 26.3)
  180757 bytes, SHA-256 eb007e38766bbce05ded7c5fad8a3531f1f2d229a01030d17bd125a174e3a32c, unsigned
  native source: unsandboxed; not executed by the registry check. Compile and test against the exact pinned Horizon and Mixins revisions before review.

$ cargo horizon-mod fits bellsandwhistles.hmod --build nightly
Bells & Whistles:
0b14f8a  made for
```

### Package

`bellsandwhistles.hmod` — **180,757 B**, SHA-256
`eb007e38766bbce05ded7c5fad8a3531f1f2d229a01030d17bd125a174e3a32c`, **331 entries**:
`horizon-mod.toml`, `Cargo.toml`, `LICENSE` (35,149 B, the GPL v3 text), `LICENSE-NOTICE.md`,
`README.md`, `src/lib.rs`, `src/runtime.rs`, `uses.json`, **204** `assets/` files and **119**
`data/` files. Built **twice with identical bytes** (reproducible). No `Cargo.lock`. The licence
travels **inside** the package, as GPL-3.0-or-later requires.

`uses.json` (from the package, `sdk-uses-from-package.json`) has **21 entries**, `made_for`
`0b14f8a`, and **no hook entry at all**. The real subscriptions are three —
`capability:registries`, `macro:horizon_mod`, `trait:Hooks`. The other 18 (`15 type`, `2 part`,
`1 handle`) are the tool's name-based over-approximation: the catalogue's `Block` struct is read as
the SDK's `Block` declaration (`fields_hash`, `built_at: src/runtime.rs:71`), and `part:block` /
`part:item` come from the words in the catalogue's comments. No behaviour is claimed from them.

### Traps **new** to this port (the reference recipes' traps were already known)

1. **A content-carrying native package splits the old tree.** `cargo horizon-mod build` packs
   `assets/` and `data/` at the project root and refuses `content/` as an unexpected package path.
   Move `content/assets` → `assets`, `content/data` → `data`, merge `content/horizon-mod.toml`
   into the root manifest, and only then move the rest of `content/` to evidence.
2. **A delivered 0.1.0 package can be staler than its own source tree.** `lang/ru_ru.json` was
   edited after the 0.1.0 `.hmod` was built, so the diff is 322/323, not 323/323. The new package
   must carry the *source tree's* file; do not "restore" the stale zip's copy to make a diff say
   zero.
3. **There is no glue to be red.** `src/runtime.rs` is entirely `#[cfg(test)] mod tests`, so the
   non-test crate is empty and the campaign's "glue first red on `todo!()`" step has nothing to
   fail: the pre-glue run and the post-glue run are the same 10 tests. Recorded as a fact rather
   than simulated with a `todo!()` that no caller would ever reach.
4. **The catalogue's type names collide with the SDK's declarations in `uses.json`.** `Block`,
   `Block.id`, `Block.template`, `part:block` and `part:item` all appear because the tool matches
   names in the source, not because the port calls them. Read `uses.json` as an over-approximation
   (the same finding `chisel`/`enderstorage` recorded) and report only `capability`,
   `macro` and the trait.
5. **`tools/gen_content.py` would have overwritten the root manifest** with its old content-only
   one (no `[native]`, version `0.4.7-1.21.1`). Its manifest write is removed and `--out` now
   defaults to the port root; `validate_content.py`'s `ROOT` likewise moved from `content/` to the
   root. Both are the port's own tools, so this is a real trap for a later regeneration.
6. **`BUILD_LOCAL=1` on every step.** The SDK is a 21 MB tree inside the port (`.horizon/sdk/`) and
   the slot runner's automatic forward would sync the whole port to the far box; the local lease is
   the supported path for an SDK package (same finding as `chisel`). The SDK was copied from
   `ports/framedblocks/.horizon/sdk` (same pin, gitignored), so no step needed the network.

### Gaps after the migration

Everything in *Gaps and deviations* above still stands (Create not ported, the headlight's lever
template, custom shapes, nine recipe-less pilots, substituted recipe materials, stonecutting not
crafted in the scenario, the creative tab's position, map colour). Added by this format:

10. **No in-game run of the 0.2.0 package.** The scenario needs a game the launcher built with this
    package (`horizon-launcher native-build ports/bellsandwhistles --instance <i>
    --trust-native-code`), and `horizon-launcher` is not installed here: there is no game build at
    `0b14f8a` and no shared `horizon-ctl` for that pin (`ports/_shared/bin/` has `1d63e0a5` and
    `41f822b6` only). The compile-and-test gate (`cargo test` 10/10, clippy, fmt, `check`, `fits`,
    a reproducible package, the static content validator) is green; the behaviour evidence is the
    0.1.0 run, whose content is the same 323 files and whose code was test-only then too.
11. **The live creative-tab listing is not asserted any more.** The 0.1.0 run read
    `.horizon-cache/mod-content/creative-inventory.json`, which only the `--dev-mod` content path
    writes; a launcher-built package produces no such file and `horizon-ctl` has no creative-tab
    reader. `tools/e2e.sh` asserts the package's tab entry list (36) and 36 successful `give`s
    instead — weaker than the 0.1.0 check, and recorded as a gap rather than quietly dropped.
12. **No diagnostics.** The SDK exports no logger and a native mod may not add a crate; this port
    never logged anything, so nothing was lost.
13. **`side` is `both`** because the blocks are content both halves need; a client-only package
    would not receive them.

### Changelog (0.2.0)

> **0.2.0 — first publication, as an SDK `.hmod`.** This is the first registry version of Bells &
> Whistles: there is no earlier submission to supersede. Horizon's mod-API merge (launcher ≥
> 0.2.70) retired `.hnmod`, so the port ships as one flat package (mod API `0.2`) built against SDK
> `0b14f8a` / mixins `e59da90` for 26.3. It carries the mod's 36 decorative station, metro and
> train blocks and everything that makes them work — block items, self-drop loot, 44 recipes, the
> climbable and mineable/pickaxe tags and one creative tab — in the same package as `src/lib.rs`
> (the one `impl mod_api::Hooks`, empty because this slice has no gameplay hook) and
> `src/runtime.rs` (the pure catalogue, byte-identical to the retired bundle, 10 tests). The
> blocks copy vanilla templates because the original's Create classes are absent: the headlight is
> a lever with a constant light 15, and the nine Create-only polished-cut pilots are
> creative-only. GPL-3.0-or-later, with `LICENSE` and `LICENSE-NOTICE.md` inside the package.

Skills: superpowers/using-superpowers,brainstorming,writing-plans,test-driven-development,systematic-debugging,verification-before-completion; BeautifulRust/rust-best-practices,rust-port
