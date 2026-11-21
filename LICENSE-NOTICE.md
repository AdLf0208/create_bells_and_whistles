# Bells & Whistles for Horizon — licence notice

This package is a **derivative work** of **Create: Bells & Whistles** and is distributed under
the **same licence as the original: the GNU General Public License, version 3 (GPL-3.0), not
"or later"**. The pinned jar's own `META-INF/neoforge.mods.toml` declares `license="GPL-3.0"`,
its `LICENSE` is the GPL version 3 text, and the "or any later version" wording appears only in
that text's generic application example, not in a project-specific grant. The full licence text
is `LICENSE` beside this file (the canonical GPL v3 text from
<https://www.gnu.org/licenses/gpl-3.0.txt>).

## What the original is

- **Original mod:** Create: Bells & Whistles 0.4.7-1.21.1 for Minecraft 1.21.1 NeoForge, mod id
  `bellsandwhistles` (jar `bellsandwhistles-0.4.7-1.21.1.jar`). Its `gradle.properties` declares
  `mod_license = GPL-3.0`; its repository `LICENSE` is the GNU GPL v3 text.
- **Author / source:** `sudoLev` — <https://github.com/sudoLev/BellsAndWhistlesMod>, read at
  release tag **`v0.4.7`**, commit `fb2e040f70ddaf8d98101c6bd484ad597954e804`.
- **This port:** a clean-room Rust rewrite for **Horizon** (Minecraft Java 26.3), written from
  the mod's own registry, classes and data files, its public documentation and its observable
  behaviour. The Rust code is not a translation of the mod's Java code and contains none of it.

## What this package carries

- The **code**: `src/lib.rs` (the one `impl mod_api::Hooks`, empty by design — the slice has no
  gameplay hook) and `src/runtime.rs` (the pure catalogue and its 10 tests, no game types).
- The **content**: `assets/bellsandwhistles/` and `data/bellsandwhistles/` —
  the original mod's own blockstates, block and item models, textures and the seven language
  files, plus the 26.3 data that declares the 36 blocks, their items, their self-drop loot
  tables, 44 recipes, the climbable and mineable/pickaxe tags and the creative tab. The textures,
  models, blockstates and lang are the original mod's GPL-licensed assets, carried unchanged
  except for the documented 26.3 format conversions in `notes.md`.
- **Complete corresponding source.** The source of everything in this package travels with it:
  `src/` is the compiled source of the code, `horizon-mod.toml` and `Cargo.toml` are its
  manifests, and the content is generated reproducibly by `tools/gen_content.py` in the port tree
  from the inventory recorded in `FINDINGS.md` and the catalogue in `src/runtime.rs`. Anyone who
  redistributes this package must ship that source under GPL-3.0 as well.

## Authors

The Rust rewrite and the 26.3 content conversion were written for this campaign; the assets,
models, blockstates and names are the original mod's and remain under GPL-3.0. The port
keeps the original's licence, gives the original author credit, and makes no claim of
endorsement.
