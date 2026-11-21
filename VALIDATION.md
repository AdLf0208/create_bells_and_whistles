# Validation — `bellsandwhistles` 0.3.0

The 0.3.0 slice is the carried-recipe family. Every command below was run in a
`ports/tools/build-slot.sh` lease (`BUILD_LOCAL=1`, `CARGO_INCREMENTAL=0`, no `--target-dir`),
and every log lives in `ports/_shared/evidence/bellsandwhistles/` (ladder) or
`ports/_shared/evidence/bellsandwhistles-e2e/` (game legs). A log that NAMES the package prints
the sha it ran against; the sha of the delivered file is
`f0ed2230ec123b016e617b0132f56f71c29e5e1c6090c9ded967e564dde0d0ca` (184,884 B, 327 entries).

## 1. Red — the rules before the data was fixed

| What | Command | Result | Log |
|---|---|---|---|
| unit: two recipes fill one grid | `cargo test --offline` | **FAILED**: `brass_bogie_steps and copper_bogie_steps fill the same crafting grid (6 … vs 6 …), so one can never be crafted` (3 failed, 13 passed) | `red-0.3.0-test.log` |
| game: the same, through the 0.2.1 recipe data | `RECIPES_ONLY=1 DATA=<0.2.1 recipes> tools/e2e.sh` | **EXIT:1**, `FAIL copper_bogie_steps: crafted 6 …brass_bogie_steps, expected 6 …copper_bogie_steps` (+3) | `bellsandwhistles-e2e/e2e-0.3.0-red-recipes.log` |
| static: a grid vanilla also fills | `python3 tools/validate_content.py` | **exit 1**, `ERROR: recipe andesite_door_step fills the grid of vanilla andesite_slab (minecraft:andesite_slab), so the craft is ambiguous` | run output, quoted in `notes.md` |

## 2. Green — the package ladder (pin `0a875da`)

| Step | Command | Result | Log |
|---|---|---|---|
| tests | `cargo test --offline` | 16 passed, 0 failed | `sdk-test.log` |
| lints | `cargo clippy --all-targets --offline -- -D warnings` | exit 0, 0 warnings | `sdk-clippy.log` |
| format | `cargo fmt --check` | exit 0 | `sdk-fmt.log` |
| build | `rm -f Cargo.lock && cargo horizon-mod build` | built | `sdk-0.3.0-build.log` |
| build again | same command, fresh lock | `cmp` identical, same sha256 | `sdk-0.3.0-sha256.log` |
| registry check | `cargo horizon-mod check bellsandwhistles.hmod` | EXIT 0, `bellsandwhistles 0.3.0 (native-mod, format native-1/0a875da…/e59da909…)`, 184,884 B, SHA-256 `f0ed2230…d0ca` | `sdk-check.log` |
| fits, the pin | `cargo horizon-mod fits bellsandwhistles.hmod --build 0a875da` | `0a875da  made for`, EXIT 0 | `sdk-fits-0a875da.log` |
| fits, a different build | `cargo horizon-mod fits bellsandwhistles.hmod --build 0b14f8a` | `0b14f8a  fits`, EXIT 0 | `sdk-fits-0b14f8a.log` |
| static content | `python3 tools/validate_content.py` | `blocks=36 models=86` + `OK: every template state binds, every model/texture resolves, every loot/recipe item exists` | — |
| package gate | `python3 ports/tools/verify-sdk-package.py bellsandwhistles` | `1/1 package(s) verified` | — |

The first `fits --build 0b14f8a` answered `does not fit: 3 items changed` (`Block`, `Recipe`,
`text::Text`): the tool matches local type names against the SDK's declarations, so the catalogue's
types were renamed (`BlockSpec`, `CarriedRecipe`, `Json::Word`, `Grid`) and the other build fits.

## 3. Green — the game legs (launcher build at `0a875da`)

`ports/tools/launcher-game.sh build bellsandwhistles` printed `Compiling bellsandwhistles (1 of 1)`
(the launcher reuses a build whose `horizon-mod.toml` is byte-identical, so the manifest version
must change between builds — `build-0.3.0.log`).

| Leg | Command | Result | Log |
|---|---|---|---|
| default + control differential | `tools/e2e.sh` (with `CONTROL_GAME` exported) | `PASS: 378 states accepted, … every carried recipe crafts and consumes its ingredients, unknown ids are refused` + `EXIT:0`; the control game's 40 `PASS … without the package …` lines precede it | `e2e-0.3.0-default.log` |
| control | `GAME=<control>/horizon-client tools/e2e.sh` | `FAIL: state check failed` (`unknown block name`) + `EXIT:1` | `e2e-0.3.0-control.log` |
| selftest | `SELFTEST=1 tools/e2e.sh` | `FAIL: SELFTEST: the false claim failed as required (minecraft:ladder dropped no mod item)` + `EXIT:1` | `e2e-0.3.0-selftest.log` |
| gate | `python3 ports/tools/check-e2e-logs.py bellsandwhistles-e2e --strict` | `logs=7 ok=7 missing-exit=0 bad-exit=0`, exit 0 | — |

The recipe phase is 30 crafting-table cases and 10 stonecutter cases; `notes.md` quotes a
transcript line of each kind, and the coverage table names every family with its state.

## 4. Artifact

`bellsandwhistles.hmod` — 184,884 B, SHA-256
`f0ed2230ec123b016e617b0132f56f71c29e5e1c6090c9ded967e564dde0d0ca`, **327 entries**:
`horizon-mod.toml`, `Cargo.toml`, `LICENSE`, `LICENSE-NOTICE.md`, `README.md`, `src/lib.rs`,
`src/runtime.rs`, `uses.json`, 204 `assets/` files and 119 `data/` files (40 of them recipes).
Declared version **0.3.0**, `api = "0.2"`, `[native]` `0a875da` / `e59da90`. No `Cargo.lock`.
