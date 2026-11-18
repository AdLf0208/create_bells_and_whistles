//! Bells & Whistles — the one `impl Hooks` at the crate root.
//!
//! The slice is content only: the 36 decorative blocks and their items, loot, recipes, tags and
//! creative tab are carried in `assets/` and `data/`, and the original mod at 0.4.7 ships no
//! block entity, entity, menu, renderer, config or network code. There is therefore no hook to
//! implement — the empty `impl Hooks` is the whole glue, and it exists because a flat SDK package
//! with code is a native mod.
//!
//! `runtime` is the port's pure catalogue (`Template`, `Block`, `BLOCKS` and its 10 tests): the
//! single place each block's template, light, tag membership, item, loot and recipe coverage is
//! spelled out. It has no `mod_api` types, so `cargo test` alone proves it.
pub mod runtime;

use mod_api::{self, Hooks};

/// The mod's session value. The macro boxes one `Default` instance for the session; nothing is
/// kept in it because this slice registers content from data and never runs code.
#[derive(Default)]
struct Mod;

#[mod_api::horizon_mod]
impl Hooks for Mod {}
