# Bells & Whistles — port notes

Ported from **Create: Bells & Whistles 0.4.7-1.21.1**
(`sudoLev/BellsAndWhistlesMod`, release tag `v0.4.7`, commit
`fb2e040f70ddaf8d98101c6bd484ad597954e804`) for Minecraft Java 26.3 on
Horizon **`0a875da91dbb0fdcb7ba8c42c11341aa229af51a`** / horizon-mixins
**`e59da9094f0c2fdda6c627fe9eff22dec6a906f0`** (0.3.0 repinned from
`0b14f8a`; the retired `.hnmod` bundle was built at `c9d474d` / `d9c83d7`;
see the migration section). Upstream analysis: [`FINDINGS.md`](FINDINGS.md).

**Licence: GPL-3.0** — not "or later". The pinned jar's own
`META-INF/neoforge.mods.toml` declares `license="GPL-3.0"`, its `LICENSE` is
the GPL version 3 text, and the "or any later version" wording appears only in
that text's generic application example, not in a project-specific grant
(`gradle.properties:mod_license=GPL-3.0`; the campaign source map's
`GPL-3.0-or-later` is the claim the artefact corrects). The port ships the
upstream mod's own textures, models and lang under that licence. It is
**local-only until the maintainer approves publishing** (ARCHITECTURE.md §8).

> **2026-11-21 — 0.3.0: the carried-recipe family, complete and unambiguous.** Repinned to
> `0a875da`; all 40 carried recipes are parsed by the tests and crafted in game (30 at a crafting
> table, 10 at a stonecutter), asserting output id and count and that the ingredients were
> consumed. Three defects came out of it and are fixed: the four brass recipes were the *same
> grids* as their copper counterparts (both metals mapped to copper) so one of each pair could
> never be crafted; four `*_pilot_from_cut` files were exact duplicates of their base file; and the
> andesite door step filled vanilla's `andesite_slab` grid. Details, red proofs and the in-game
> transcripts: [`## 0.3.0 — the recipe family`](#030--the-recipe-family-2026-11-21).

> **2026-11-18 — migrated to the SDK format (mod API 0.2), version 0.2.0.**
> Horizon's mod-API merge retired `.hnmod`; this port is now one flat
> `bellsandwhistles.hmod` (36 blocks and their data + `src/lib.rs`) built against
> SDK `0b14f8a` / mixins `e59da90`. `src/runtime.rs` is byte-identical to the
> retired bundle and the content is the same 323 files. The retired tree is in
> `ports/_shared/evidence/bellsandwhistles/retired-hnmod-0.1.0/`; the recipe,
> ladder, traps and changelog are in
> [`## Migration to the SDK format (0.2.0)`](#migration-to-the-sdk-format-020-2026-11-18)
> at the end of this file. The e2e section below is **historical** (0.1.0,
> `--dev-mod content/`): no launcher was installed then, so the 0.2.0 package was
> not re-run in game. **0.2.1 re-ran it** (launcher build at `0b14f8a`) and also
> corrected `src/runtime.rs`'s header licence line, the only diff from 0.2.0's copy.
> **0.3.0 repinned to `0a875da` and crafted every carried recipe in game** — see the 0.3.0
> section at the end of this file.

Status: **slice 1 implemented and verified in-game (0.1.0).** The slice is content
only: the 36 decorative blocks `ModBlocks` registers, their block items,
self-drop loot, the 44 recipe files that 26.3 can express (40 unique after
0.3.0), the climbable and
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

**0.2.1 status (2026-11-19, licence-label correction):** `Cargo.toml` and the
`horizon-mod.toml` comment now say **GPL-3.0** (they said `GPL-3.0-or-later`, contradicting
the jar, the entry and the port's own README/NOTICE). No behaviour change: the content is
unchanged, `src/runtime.rs` differs from 0.2.0 only in its header licence line. Rebuilt
byte-identically, ladder green, and re-run in game (launcher build at `0b14f8a`) — see
[`## 0.2.1 — the licence label inside the package`](#021--the-licence-label-inside-the-package-2026-11-19).

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
| 23 | `polished_andesite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 24 | `polished_granite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 25 | `polished_diorite_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
| 26 | `polished_deepslate_pilot` | `minecraft:carved_pumpkin` | 4 | 0 | pickaxe | 1 |
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
   `create:brass_sheet` → **`minecraft:gold_ingot`**; `c:nuggets/brass` and
   `create:brass_nugget` → **`minecraft:gold_nugget`** (0.3.0: brass is the
   yellow metal, one-to-one with copper→copper — before, both mapped to copper
   and the four brass crafting recipes were the same grids as the copper ones);
   `create:copper_nugget` → `minecraft:copper_nugget`; `c:ingots/copper` /
   `create:copper_sheet` → `minecraft:copper_ingot`; `create:iron_sheet` →
   `minecraft:iron_ingot`;
   `create:ornate_iron_window` → `minecraft:iron_bars`; `c:glass` →
   `minecraft:glass`; `create:polished_cut_{andesite,deepslate,diorite,
   granite,tuff}` and their stairs → the vanilla `polished_*` block and
   stairs. The nine Create-only polished-cut stones (asurine, calcite,
   crimsite, dripstone, limestone, ochrum, scoria, scorchia, veridium) have
   **no** recipe, because no vanilla item stands in for them.
5. **Recipe files are flat.** 26.3 reads `data/<ns>/recipe/*.json`; upstream's
   nested folders are flattened and the two `door_steps/<metal>_grab_rails`
   recipes take their output's name (`<metal>_door_step`). 40 of upstream's
   52 recipes are carried: the nine Create-only pilots keep none, and the four
   `polished_{andesite,deepslate,diorite,granite}_pilot_from_cut` files are
   dropped because their `create:polished_cut_*` ingredient has no distinct
   26.3 stand-in (they would be byte-for-byte duplicates of the base file —
   dead data, notes said so in 0.3.0). `polished_tuff_pilot` keeps its recipe
   because vanilla has no polished tuff of its own to duplicate.
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

[`src/runtime.rs`](src/runtime.rs) is a test-only catalogue (`Shape`,
`BlockSpec`, `BLOCKS`, and the carried recipes parsed from the shipped JSON)
that the content generator and the notes read from. It has **16 tests**: 10 for
the blocks (36 unique valid ids, every block has an item and a self-drop, only
the headlight emits light 15, the climbable set is the six rails, the pickaxe
set is the 27 stone/metal blocks, the templates' state spaces total 378, the
nine Create-only pilots have no recipe, 27 blocks carry 40 unique recipe files,
and every recipe stem names a known block) and 6 for the recipe family:

- `the_carried_recipe_files_are_exactly_the_catalogue` — the files under
  `data/bellsandwhistles/recipe/` and `BLOCKS` name the same 40 stems;
- `no_two_carried_recipes_fill_the_same_grid` — vanilla's match (every offset,
  both mirror orientations, every cell outside the pattern empty) over every
  pair, so two crafting-table recipes can never shadow each other;
- `no_two_stonecutting_recipes_offer_the_same_result`;
- `every_carried_recipe_uses_a_resolvable_item` (no `create:*`, every id
  namespaced, counts 1-64);
- `brass_recipes_name_gold_and_copper_recipes_name_copper` (the metals are one
  to one);
- `the_two_headlight_files_are_mirror_images` (why that pair may share a grid).

The parser is a ~150-line recursive-descent reader for the recipe JSON subset
inside the test module, so the rules run on the shipped data instead of a
second hand-written table. There is no gameplay hook, so the package has one
empty `impl mod_api::Hooks`.

Skills: superpowers/using-superpowers,brainstorming,writing-plans,test-driven-development,systematic-debugging,verification-before-completion; BeautifulRust/rust-best-practices,rust-port

Skills: superpowers/using-superpowers,writing-plans,verification-before-completion; BeautifulRust/none (no Rust change) — documentation-consistency job (2026-11-19): pin line corrected to `0b14f8a`/`e59da90`, licence label to `GPL-3.0`, no code touched.

## Verification

### Runtime (standalone crate)

| Command | Result |
|---|---|
| `cargo fmt` / `cargo fmt --check` | exit 0 |
| `cargo test --locked --offline` | exit 0, **16 passed; 0 failed** (0.3.0) |
| `cargo clippy --all-targets --locked --offline -- -D warnings` | exit 0, **0 warnings** |

### 0.3.0 package ladder (2026-11-21, pin `0a875da`)

Every log is in `ports/_shared/evidence/bellsandwhistles/` and each one names the sha it ran
against.

| Step | Command | Result |
|---|---|---|
| tests | `cargo test --offline` | **16 passed; 0 failed** — `sdk-test.log` |
| lints | `cargo clippy --all-targets --offline -- -D warnings` | exit 0, 0 warnings — `sdk-clippy.log` |
| format | `cargo fmt --check` | exit 0 — `sdk-fmt.log` |
| build | `rm -f Cargo.lock && cargo horizon-mod build` | `Built …/bellsandwhistles.hmod` — `sdk-0.3.0-build.log` |
| reproducible | second build, `cmp` the delivered file | **byte-identical**, same sha256 — `sdk-0.3.0-sha256.log` |
| registry check | `cargo horizon-mod check bellsandwhistles.hmod` | **EXIT 0**, `bellsandwhistles 0.3.0 (native-mod, format native-1/0a875da…/e59da909…)`, 184,884 B, SHA-256 `f0ed2230…d0ca` — `sdk-check.log` |
| fits, the pin | `cargo horizon-mod fits bellsandwhistles.hmod --build 0a875da` | `0a875da  made for`, EXIT 0 — `sdk-fits-0a875da.log` |
| fits, a different build | `cargo horizon-mod fits bellsandwhistles.hmod --build 0b14f8a` | `0b14f8a  fits`, EXIT 0 — `sdk-fits-0b14f8a.log` |
| static content | `python3 tools/validate_content.py` | `blocks=36 models=86` / `OK: every template state binds, every model/texture resolves, every loot/recipe item exists` (plus the two recipe rules and the vanilla-shadow check) |
| gate | `python3 ports/tools/verify-sdk-package.py bellsandwhistles` | **1/1** |

The second `fits` run first answered `does not fit: 3 items changed` — `Block`, `Recipe` and
`text::Text` — because the tool matches local type names against the SDK's declarations
(the handover's trap 3). The catalogue's types were renamed to `BlockSpec`, `CarriedRecipe` and
`Json::Word` (and `Body` to `Grid`), after which the other build answers `fits`.

### Staged pin (`stage → check → test → build`)

| Step | Command | Result |
|---|---|---|
| stage | `tools/horizon.py stage` | exit 0, `staging_seconds: 367`, `stage_changed: true` at c9d474d |
| check | `tools/horizon.py check` | **exit 143 (SIGTERM)**: the shared `ports/tools/clean-targets.sh` deleted `target/mixins` and `target/horizon-cargo` while the check was compiling, then the transient unit was terminated. Requeued (`target/run-direct.sh`); see the environment note. |
| test | `tools/horizon.py test` | PENDING (queued behind check) |
| build | `tools/horizon.py build` | PENDING (queued) |

The 0.1.0 staged-ladder rows above are history: the retired format's `tools/horizon.py` is
gone, and the 0.3.0 package (a launcher-compiled `.hmod`) is verified by the ladder in the
previous section.

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
   not upstream's exact ingredients, because Create is absent. Brass is gold,
   copper is copper, andesite is andesite (the alloy has no stand-in).
6. ~~**Stonecutting recipes are carried but not crafted in the e2e.**~~
   **Closed in 0.3.0**: `tools/recipe_check.py` drives all 10 stonecutting
   recipes through a real stonecutter — the offers from `ctl menu`, the cell
   clicked with `click-gui`, the selected result's id and count asserted, the
   input consumed — and the same grids on the control game offer no mod recipe.
   The harness fact that cost four runs: **a station must be opened by
   right-clicking the block (`ctl interact`) with the player beside it and
   looking at it**. `ctl use` sets the station but leaves the screen in
   `playing`, and then every slot click silently misses (the carried stack is
   still carried, `click-slot 600` deposits nowhere; probes in
   `evidence/bellsandwhistles/`).
7. **No block entity, entity, menu, renderer, config or network code** — the
   slice is content only. That is the whole mod at this version: there is no
   gameplay logic to port.
8. **The creative tab's position** differs from upstream (which inserts into
   vanilla tabs); Horizon content mods cannot.
9. **Map colour** is the template's (upstream copied mossy cobblestone/stone
   map colours); it was not visually checked headless.
10. **`uses.json` over-approximates the recipe code** (0.3.0). The package's
    `uses.json` lists `hook:ingredient`, `hook:items`, `method:Hooks::ingredient`,
    `method:Hooks::items`, `handle:Item::new` and `handle:Tag::id` because the
    tool matches the *words* `ingredient`/`items` in the recipe tests. The real
    subscriptions are still three: `capability:registries`, `macro:horizon_mod`,
    `trait:Hooks`. No behaviour is claimed from the names (the same finding as
    0.2.0's catalogue `Block`).
11. **`Cargo.toml`'s version is 0.3.0 as well** (0.2.1 deliberately left it at
    0.2.0). The identity is `horizon-mod.toml`'s version either way.
12. **The andesite door step is two andesite, not three.** Three andesite in a
    row is exactly vanilla `andesite_slab`'s grid, so which recipe the crafting
    table offered was the recipe manager's order (the mod's won in this build,
    but that is not guaranteed). Two andesite is the nearest grid vanilla does
    not claim; the output stays 8. `validate_content.py` now fails any carried
    grid that a vanilla 26.3 crafting recipe also fills.

## Files

```
horizon-mod.toml                             the only manifest: id, version 0.3.0, api 0.2,
                                             side both, registries, [native] SDK pins (0a875da)
Cargo.toml                                   one crate (version 0.3.0), horizon-mod-api from
                                             .horizon/sdk/
bellsandwhistles.hmod                        delivered 327-entry SDK package (native + content)
assets/bellsandwhistles/                     36 blockstates, 45 block models,
                                             36 item models, 36 item definitions,
                                             44 textures, 7 lang files
data/bellsandwhistles/horizon/               36 block declarations, 1 tab
data/bellsandwhistles/loot_table/            36 self-drop tables
data/bellsandwhistles/recipe/                40 recipes (30 crafting, 10 stonecutting)
data/minecraft/tags/block/                   climbable, mineable/pickaxe
src/lib.rs                                   the one impl mod_api::Hooks (empty by design)
src/runtime.rs                               test-only catalogue, 16 tests (10 blocks, 100
                                             recipe rules), the recipe JSON reader
LICENSE, LICENSE-NOTICE.md                   GPL-3.0, inside the package
README.md                                    inside the package
.gitignore                                   /target, /.horizon, /Cargo.lock
FINDINGS.md, notes.md                        the record
tools/gen_content.py                         reproduces assets/ and data/
tools/state_check.py                         the 378-state + default-placement check
tools/recipe_check.py                        crafts every carried recipe (table + stonecutter),
                                             asserts output/count/consumption; --mode absent is
                                             the control-game differential
tools/validate_content.py                    the static content/model/recipe check
tools/e2e.sh                                 default/counterfactual/SELFTEST/RECIPES_ONLY, needs
                                             a launcher-built game
VALIDATION.md                                the 0.3.0 ladder evidence in one place
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
travels **inside** the package, as GPL-3.0 requires.

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

10. **No in-game run of the 0.2.0 package** — **closed in 0.2.1** (2026-11-19): the launcher
    (`0.2.78`) is installed, `ports/tools/launcher-game.sh build bellsandwhistles --rebuild`
    compiled the package into a game at `0b14f8a`, and the default, counterfactual and control
    legs are recorded in `evidence/bellsandwhistles-e2e/` (see the 0.2.1 section). The paragraph
    below is the state on 2026-11-18. The scenario needed a game the launcher built with this
    package (`horizon-launcher native-build ports/bellsandwhistles --instance <i>
    --trust-native-code`), and `horizon-launcher` was not installed then: there was no game build at
    `0b14f8a` and no shared `horizon-ctl` for that pin (`ports/_shared/bin/` has `1d63e0a5` and
    `41f822b6` only). The compile-and-test gate (`cargo test` 10/10, clippy, fmt, `check`, `fits`,
    a reproducible package, the static content validator) was green; the behaviour evidence was the
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
> creative-only. GPL-3.0, with `LICENSE` and `LICENSE-NOTICE.md` inside the package.

## 0.2.1 — the licence label inside the package (2026-11-19)

**The defect.** The delivered 0.2.0 package declared **GPL-3.0-or-later** in two files that
travel *inside* the `.hmod`: `Cargo.toml:13` and the `horizon-mod.toml` header comment. The
registry entry, the pinned jar and this port's own `README.md` / `LICENSE-NOTICE.md` all say
**GPL-3.0**, so the package contradicted its own listing.

**The evidence** (read from the pinned jar, not guessed): `META-INF/neoforge.mods.toml`
declares `license="GPL-3.0"`; the jar's `LICENSE` is the GPL v3 text with **no
project-specific "or any later version" grant** (that wording appears only in the text's
generic application example); `gradle.properties` says `mod_license = GPL-3.0`. The source
map's `GPL-3.0-or-later` is the claim the artefact corrects. `iceandfire` is different — its
upstream `LICENSE` header does grant "or any later version", so its `-or-later` label is
right and was not touched.

**Changed in 0.2.1.**

- `Cargo.toml:13` → `license = "GPL-3.0"`.
- `horizon-mod.toml` header → `# Licence: GPL-3.0 … no project-specific "or later" version`;
  `version` → **0.2.1**.
- `src/runtime.rs:4` header → `GPL-3.0` — the only change to that file.
- `tools/gen_content.py` docstring → `GPL-3.0`.
- `horizon-mod.toml`'s migration note no longer claims `src/runtime.rs` is byte-identical to the
  retired bundle: it is "unchanged except its header licence line (0.2.1)".
- `FINDINGS.md` marks the source-map claim as the one the jar corrects.
- `README.md`, `LICENSE-NOTICE.md`, `notes.md`: already corrected by the doc-consistency job;
  checked, nothing contradicts.
- **No behaviour change.** The 204 `assets/` + 119 `data/` files are byte-identical.
- `Cargo.toml`'s package `version` stays `0.2.0`: the job bumped `horizon-mod.toml` only, and
  Cargo's name/version are not the mod's identity (the manifest says so; `imfast` ships the same
  split). The registry and `check` read the `horizon-mod.toml` version.

**Verification (fresh runs 2026-11-19; every log in `evidence/bellsandwhistles/`).**

| Step | Command | Result | Log |
|---|---|---|---|
| tests | `cargo test --offline` | **10 passed; 0 failed** | `sdk-0.2.1-test.log` |
| lints | `cargo clippy --all-targets --offline -- -D warnings` | exit 0, 0 warnings | `sdk-0.2.1-clippy.log` |
| format | `cargo fmt --check` | exit 0 | `sdk-0.2.1-fmt.log` |
| build | `rm -f Cargo.lock && cargo horizon-mod build` | exit 0 | `sdk-0.2.1-build.log` |
| reproducible | second build, `cmp` the delivered file | identical, same sha256 | `sdk-0.2.1-sha256.log` |
| registry check | `cargo horizon-mod check bellsandwhistles.hmod` | **EXIT 0** | `sdk-0.2.1-check.log` |
| fits | `cargo horizon-mod fits bellsandwhistles.hmod --build 0b14f8a` | `0b14f8a  made for`, exit 0 | `sdk-0.2.1-fits.log` |
| label inside | `unzip -p … Cargo.toml \| grep '^license'` | `license = "GPL-3.0"` | `sdk-0.2.1-licence-inside-package.log` |
| label inside | `unzip -p … horizon-mod.toml \| grep -i gpl` | `# Licence: GPL-3.0, …` | same |

**Package:** `bellsandwhistles.hmod`, **181,037 B**, SHA-256
`b0b240ef02790d9da2d5ebafe1e07b0ceecde0aafb45bad84c1d50b885cdb986`, 331 entries (the
0.2.0 package was 180,757 B / `eb007e38…`). `check` prints
`bellsandwhistles 0.2.1 (native-mod, …)`. Grepping the unpacked package for
`GPL-3.0-or-later` finds **nothing**.

**In game** (`launcher-game.sh build bellsandwhistles --rebuild`, then `run bellsandwhistles`;
logs in `evidence/bellsandwhistles-e2e/`, `check-e2e-logs.py bellsandwhistles-e2e --strict`
= 3/3 ok):

| Leg | Result |
|---|---|
| default | `PASS: 378 states accepted, … unknown ids are refused` + `EXIT:0` |
| counterfactual (`COUNTERFACTUAL=1`) | `PASS: counterfactual differential` + `EXIT:0` |
| control (same Nightly, no package) | `FAIL: state check failed` (`unknown block name` for `bellsandwhistles:andesite_bogie_steps`) + `EXIT:1` |

Skills: superpowers/using-superpowers,verification-before-completion; BeautifulRust/rust-best-practices — licence-label job (2026-11-19): `GPL-3.0` in `Cargo.toml`/`horizon-mod.toml`/`src/runtime.rs`, 0.2.1 rebuild, full ladder and the three in-game legs.

## 0.3.0 — the recipe family (2026-11-21)

### The slice, and the gap it closes

The port's own gap list said:

> **Stonecutting recipes are carried but not crafted in the e2e.** The crafting path is proved for
> six recipes; the stonecutter menu path is not exercised.

and the campaign's parity ruling (2026-11-20) makes the recipe family the sharpest case: *a carried
recipe that is never crafted is dead data*. 0.3.0 takes the whole family — **all 40 carried recipes**
— through a real game: 30 at a crafting table and 10 at a stonecutter, each asserting its declared
output id and count, that the grid (or the stonecutter's input) emptied, and that nothing else on
the mod's side appeared. The control game runs the same grids with the package absent and must
craft nothing and offer no `bellsandwhistles:` recipe.

### The defects the family exposed (each proved before it was fixed)

**1. The four brass crafting recipes were the same grids as their copper counterparts.**
Upstream's brass recipes name `c:ingots/brass` / `c:nuggets/brass` and its copper ones
`c:ingots/copper` / `c:nuggets/copper` (jar: `data/bellsandwhistles/recipe/{bogie_steps,door_steps,
grab_rails,pilots}/*.json`), but `tools/gen_content.py` mapped **both** to
`minecraft:copper_ingot` / `minecraft:copper_nugget`. Two recipes that fill one grid cannot both be
crafted: the recipe manager offers one.

The unit red (`cargo test --offline`, log `red-0.3.0-test.log`):

```
---- runtime::tests::no_two_carried_recipes_fill_the_same_grid stdout ----
thread 'runtime::tests::no_two_carried_recipes_fill_the_same_grid' panicked at src/runtime.rs:1093:17:
brass_bogie_steps and copper_bogie_steps fill the same crafting grid (6 bellsandwhistles:brass_bogie_steps vs 6 bellsandwhistles:copper_bogie_steps), so one can never be crafted
```

and the game said the same thing through the old package
(`e2e-0.3.0-red-recipes.log`, the delivered 0.2.1 recipe data with the 0.3.0 harness):

```
FAIL copper_bogie_steps: crafted 6 bellsandwhistles:brass_bogie_steps, expected 6 bellsandwhistles:copper_bogie_steps
FAIL copper_door_step: crafted 8 bellsandwhistles:brass_door_step, expected 8 bellsandwhistles:copper_door_step
FAIL copper_grab_rails: crafted 8 bellsandwhistles:brass_grab_rails, expected 8 bellsandwhistles:copper_grab_rails
FAIL copper_pilot: crafted 1 bellsandwhistles:brass_pilot, expected 1 bellsandwhistles:copper_pilot
FAIL: 4 recipe(s) failed: ['copper_bogie_steps', 'copper_door_step', 'copper_grab_rails', 'copper_pilot']
```

**Fix:** brass maps to **gold** (`c:ingots/brass` + `create:brass_sheet` → `minecraft:gold_ingot`,
`c:nuggets/brass` + `create:brass_nugget` → `minecraft:gold_nugget`), copper stays copper — one to
one, so each of the eight metal items has its own recipe. `ITEM_MAP`/`TAG_MAP` and the seven
affected recipe files carry it; the unit test `brass_recipes_name_gold_and_copper_recipes_name_copper`
pins the rule.

**2. Four `polished_*_pilot_from_cut.json` files were duplicates of their base file.** Upstream
distinguishes `polished_andesite` from Create's `create:polished_cut_andesite`; the port mapped both
to `minecraft:polished_andesite`, so `polished_andesite_pilot` and `polished_andesite_pilot_from_cut`
became the same recipe file twice (and the same for deepslate, diorite and granite). The 0.2.1 run
"crafted" both copies into the same item — dead data. **Fix:** the four are dropped (44 → 40
recipe files); the recipe is still carried and crafted, and the 0.3.0 log shows one line per
surviving file.

**3. The andesite door step filled vanilla's `andesite_slab` grid.** `tools/validate_content.py`
grew the same collision rules plus a **vanilla-shadow** check against the prepared 26.3 recipe
files, and its first run said:

```
ERROR: recipe andesite_door_step fills the grid of vanilla andesite_slab (minecraft:andesite_slab), so the craft is ambiguous
```

Three andesite in a row is vanilla's slab recipe; which one the table offered was the recipe
manager's order (in the red run the mod's won, which is luck, not a contract). **Fix:** the andesite
door step takes **two** andesite (`["##"]`), the nearest grid vanilla does not claim; the output
stays 8. `RECIPE_PATCHES` in `gen_content.py` records it so a regeneration reproduces the file,
and the new validator rule fails any future grid that a vanilla recipe also fills.

**4. The two headlight files are one grid.** `headlight` and `headlight_2` are mirror images and
26.3's shaped match tries both orientations, so one grid crafts the headlight — the pair is exempt
from the collision rule (same output, same count) and
`the_two_headlight_files_are_mirror_images` pins why.

### The harness fact: a station is opened by `interact`, not `use`

`ctl use X Y Z` sets the station but leaves the screen in `playing`; every station-slot click then
silently misses — the carried stack stays carried, `click-slot 600` deposits nowhere, and an
inventory click lands one table over (`click-slot 9` put the item in slot 16). A real right-click
does it: stand beside the block, `look-at-block`, `interact`. Then the input lands in slot 600, the
offers appear in `ctl menu`'s `info.recipes`, `click-gui` on a recipe cell sets `info.selected` and
`info.result`, and `click-slot 650` takes the product. Probes:
`evidence/bellsandwhistles/probe-station-use-vs-interact.log` and `probe-station-interact.log`.
Four in-game runs were spent on `use` before this was found; `tools/recipe_check.py` records it in
the docstring so the next station leg starts there.

### Red → green (in game)

| Leg | Log | Result |
|---|---|---|
| red (0.2.1 recipe data, 0.3.0 harness) | `e2e-0.3.0-red-recipes.log` | `FAIL: 4 recipe(s) failed …` + `EXIT:1` |
| default (0.3.0 package) | `e2e-0.3.0-default.log` | 73 `PASS` lines (40 recipes + 33 others), `PASS: 378 states accepted, … every carried recipe crafts and consumes its ingredients, unknown ids are refused` + `EXIT:0` |
| control-game differential (inside the default log) | same | 40 `PASS … without the package …` lines, then the modded leg |
| control (same Nightly, no package) | `e2e-0.3.0-control.log` | `FAIL: state check failed` (`unknown block name` for `bellsandwhistles:andesite_bogie_steps`) + `EXIT:1` |
| SELFTEST | `e2e-0.3.0-selftest.log` | `FAIL: SELFTEST: the false claim failed as required (minecraft:ladder dropped no mod item)` + `EXIT:1` |

`python3 ports/tools/check-e2e-logs.py bellsandwhistles-e2e --strict` → **7/7 ok**.

Sample stonecutter transcripts (the differential is the second cell's result):

```
PASS andesite_bogie_steps_stonecutting: bellsandwhistles:andesite_bogie_steps x4 from one minecraft:andesite
     (cell 1 was bellsandwhistles:andesite_door_step x6), the input was consumed
PASS brass_bogie_steps_stonecutting: bellsandwhistles:brass_bogie_steps x3 from one minecraft:gold_ingot
     (cell 1 was bellsandwhistles:brass_door_step x6), the input was consumed
PASS station_platform_stonecutter: bellsandwhistles:station_platform x2 from one minecraft:smooth_stone
     (cell 0 was minecraft:smooth_stone_slab x2), the input was consumed
```

### Coverage (family by family, from the jar)

| Family | State | Evidence |
|---|---|---|
| 36 blocks, their block items, default/placement states | tested | `state_check.py` in `e2e-0.3.0-default.log`: 378 states accepted, 36 place and read back |
| self-drop loot tables (36) | tested (8 broken with the right tool) | `drops:` lines; the full set is the loot data |
| `#minecraft:climbable` and `#minecraft:mineable/pickaxe` | tested (positive + cross controls) | `TAG_CLIMB` … / `TAG_BAD_*` absent |
| headlight light 15 | tested | `ctl light` = `f` vs casing `0` |
| creative tab | carried; the live listing is not readable on a launcher build (0.2.0 gap 11) | 36 gives + the package's tab JSON |
| **30 crafting-table recipes** | **tested** | one `PASS <stem>: N <id>, the grid emptied …` line each: output, count, consumption, no foreign mod item |
| **10 stonecutting recipes** | **tested** | one `PASS <stem>: <id> xN from one …` line each: offer list, selected cell, result, input consumed, differential cell |
| recipes' materials (Create absent) | substituted, documented | the map above; brass→gold, copper→copper |
| nine Create-only pilots' recipes | not ported (no 26.3 stand-in) | `notes.md` gap 4 |
| Create's wrench, panel helper, copycat, train doors | not ported | gap 1 (Create is not a dependency of any registered block) |
| custom shapes for rails/headlight/pilots | not ported | gap 3 |
| block entity, entity, menu, renderer, config, network | not ported | gap 7 — the jar at 0.4.7 ships none |

### Changelog (0.3.0)

> **0.3.0 — the carried recipes, complete and unambiguous.** An update of the 0.2.1 package, built
> at the campaign pin `0a875da` (mixins `e59da90`). Every one of the mod's 40 carried recipes is now
> crafted in game and asserted — 30 at a crafting table, 10 at a stonecutter — with its output id
> and count and its ingredients' consumption, and the same grids prove absent on a game without the
> package. Three recipe defects are fixed on the way: the brass recipes were the same grids as the
> copper ones (both metals mapped to copper; brass is gold now), four `_from_cut` pilot files were
> duplicates of their base file (dropped), and the andesite door step filled vanilla's
> `andesite_slab` grid (two andesite now). Same 36 blocks, items, loot, tags and tab; no hook, no
> block entity, no menu.

Skills: superpowers/using-superpowers,brainstorming,writing-plans,test-driven-development,systematic-debugging,verification-before-completion; BeautifulRust/rust-best-practices — 0.3.0 recipe-family job (2026-11-21): the recipe JSON reader, the six recipe rules (red → green), the brass→gold and duplicate-recipe fixes, `recipe_check.py` (table + stonecutter + absent mode), the repin to `0a875da`, the package ladder and the four game legs.
