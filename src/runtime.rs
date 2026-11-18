// Bells and Whistles for Horizon — the decorative content catalogue (pure).
//
// Ported from Create: Bells & Whistles 0.4.7-1.21.1
// (sudoLev/BellsAndWhistlesMod, GPL-3.0-or-later) for Minecraft Java 1.21.1
// NeoForge. Upstream source was read for the registry, the block classes and
// the datagen shapes; this is a clean-room Rust rewrite. The slice is
// content-only: the 36 decorative blocks and their items, loot, recipes, tags
// and creative tab are declared in ../content, and this model is the single
// place their template, light, tag membership, item, loot and recipe coverage
// are spelled out (ModBlocks.java:20-99, ModCreativeModeTabs.java:22-63).

#[cfg(test)]
mod tests {
    use std::collections::BTreeSet;

    /// The vanilla template a block copies: its behaviour class and states.
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub enum Template {
        /// `minecraft:ladder`: `facing` × `waterlogged`.
        Ladder,
        /// `minecraft:iron_trapdoor`: `facing` × `half` × `open` × `powered` ×
        /// `waterlogged`.
        IronTrapdoor,
        /// `minecraft:lever`: `face` × `facing` × `powered`.
        Lever,
        /// `minecraft:carved_pumpkin`: `facing`.
        CarvedPumpkin,
        /// `minecraft:end_rod`: `facing`, all six directions.
        EndRod,
        /// `minecraft:iron_block`: one state.
        IronBlock,
    }

    impl Template {
        /// The number of states the template's state definition has.
        pub const fn state_count(self) -> u16 {
            match self {
                Template::Ladder => 8,
                Template::IronTrapdoor => 64,
                Template::Lever => 24,
                Template::CarvedPumpkin => 4,
                Template::EndRod => 6,
                Template::IronBlock => 1,
            }
        }
    }

    /// One registered decorative block.
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub struct Block {
        /// The path under `bellsandwhistles:`.
        pub id: &'static str,
        /// The vanilla block whose behaviour, states and shapes it copies.
        pub template: Template,
        /// Light emitted, 0 to 15 (the headlight copies lantern's 15).
        pub light: u8,
        /// Member of `#minecraft:climbable` (the six metal rail blocks).
        pub climbable: bool,
        /// Member of `#minecraft:mineable/pickaxe`.
        pub pickaxe: bool,
        /// The block item exists.
        pub item: bool,
        /// A self-drop loot table exists.
        pub loot: bool,
        /// The carried recipes, by file stem.
        pub recipes: &'static [&'static str],
    }

    /// Every registered block, in the creative tab's order.
    pub const BLOCKS: [Block; 36] = [
        Block {
            id: "andesite_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_bogie_steps", "andesite_bogie_steps_stonecutting"],
        },
        Block {
            id: "brass_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_bogie_steps", "brass_bogie_steps_stonecutting"],
        },
        Block {
            id: "copper_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_bogie_steps", "copper_bogie_steps_stonecutting"],
        },
        Block {
            id: "andesite_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_grab_rails", "andesite_grab_rails_stonecutting"],
        },
        Block {
            id: "brass_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_grab_rails", "brass_grab_rails_stonecutting"],
        },
        Block {
            id: "copper_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_grab_rails", "copper_grab_rails_stonecutting"],
        },
        Block {
            id: "andesite_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_door_step", "andesite_door_step_stonecutting"],
        },
        Block {
            id: "brass_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_door_step", "brass_door_step_stonecutting"],
        },
        Block {
            id: "copper_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_door_step", "copper_door_step_stonecutting"],
        },
        Block {
            id: "ornate_iron_trapdoor",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["ornate_iron_window"],
        },
        Block {
            id: "headlight",
            template: Template::Lever,
            light: 15,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["headlight", "headlight_2"],
        },
        Block {
            id: "station_platform",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["station_platform", "station_platform_stonecutter"],
        },
        Block {
            id: "metro_casing",
            template: Template::IronBlock,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_sheet"],
        },
        Block {
            id: "corrugated_metro_casing",
            template: Template::IronBlock,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["corrugated_metro_sheet"],
        },
        Block {
            id: "metro_panel",
            template: Template::EndRod,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_panel", "metro_panel_from_corrugated"],
        },
        Block {
            id: "corrugated_metro_panel",
            template: Template::EndRod,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[
                "corrugated_metro_panel",
                "corrugated_metro_panel_from_panel",
            ],
        },
        Block {
            id: "metro_trapdoor",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_trapdoor"],
        },
        Block {
            id: "metro_window",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_window"],
        },
        Block {
            id: "andesite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["andesite_pilot"],
        },
        Block {
            id: "brass_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["brass_pilot"],
        },
        Block {
            id: "copper_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["copper_pilot"],
        },
        Block {
            id: "metal_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metal_pilot"],
        },
        Block {
            id: "polished_andesite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[
                "polished_andesite_pilot",
                "polished_andesite_pilot_from_cut",
            ],
        },
        Block {
            id: "polished_granite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_granite_pilot", "polished_granite_pilot_from_cut"],
        },
        Block {
            id: "polished_diorite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_diorite_pilot", "polished_diorite_pilot_from_cut"],
        },
        Block {
            id: "polished_deepslate_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[
                "polished_deepslate_pilot",
                "polished_deepslate_pilot_from_cut",
            ],
        },
        Block {
            id: "polished_dripstone_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_tuff_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_tuff_pilot"],
        },
        Block {
            id: "polished_calcite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_limestone_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_scoria_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_scorchia_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_crimsite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_ochrum_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_veridium_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        Block {
            id: "polished_asurine_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
    ];

    fn ids() -> BTreeSet<&'static str> {
        BLOCKS.iter().map(|block| block.id).collect()
    }

    fn with_recipes() -> Vec<&'static str> {
        BLOCKS
            .iter()
            .filter(|block| !block.recipes.is_empty())
            .map(|block| block.id)
            .collect()
    }

    #[test]
    fn thirty_six_blocks_with_unique_ids() {
        assert_eq!(BLOCKS.len(), 36, "the slice is 36 registered blocks");
        assert_eq!(ids().len(), 36, "ids must be unique");
    }

    #[test]
    fn ids_are_lower_case_resource_paths() {
        for block in BLOCKS {
            assert!(!block.id.is_empty(), "an empty id");
            assert!(
                block
                    .id
                    .bytes()
                    .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_'),
                "{} is not a lower-case resource path",
                block.id
            );
        }
    }

    #[test]
    fn every_block_has_an_item_and_a_self_drop() {
        for block in BLOCKS {
            assert!(block.item, "{} has no block item", block.id);
            assert!(block.loot, "{} has no loot table", block.id);
        }
    }

    #[test]
    fn only_the_headlight_emits_light() {
        let glowing: Vec<&str> = BLOCKS
            .iter()
            .filter(|block| block.light > 0)
            .map(|block| block.id)
            .collect();
        assert_eq!(glowing, ["headlight"], "only the headlight lights");
        assert_eq!(
            BLOCKS
                .iter()
                .find(|block| block.id == "headlight")
                .map(|block| block.light),
            Some(15),
            "the headlight copies lantern's light level"
        );
    }

    #[test]
    fn the_climbable_tag_is_the_six_metal_rails() {
        let climbable: BTreeSet<&str> = BLOCKS
            .iter()
            .filter(|block| block.climbable)
            .map(|block| block.id)
            .collect();
        let expected: BTreeSet<&str> = [
            "andesite_grab_rails",
            "brass_grab_rails",
            "copper_grab_rails",
            "andesite_bogie_steps",
            "brass_bogie_steps",
            "copper_bogie_steps",
        ]
        .into_iter()
        .collect();
        assert_eq!(climbable, expected, "upstream's climbable tag");
        for block in BLOCKS.iter().filter(|block| block.climbable) {
            assert_eq!(
                block.template,
                Template::Ladder,
                "{} climbs on a ladder template",
                block.id
            );
        }
    }

    #[test]
    fn the_pickaxe_tag_is_the_stone_and_metal_set() {
        let pickaxe: BTreeSet<&str> = BLOCKS
            .iter()
            .filter(|block| block.pickaxe)
            .map(|block| block.id)
            .collect();
        let expected: BTreeSet<&str> = [
            "station_platform",
            "metro_casing",
            "corrugated_metro_casing",
            "metro_panel",
            "corrugated_metro_panel",
            "metro_trapdoor",
            "metro_window",
            "ornate_iron_trapdoor",
            "headlight",
            "metal_pilot",
            "andesite_pilot",
            "brass_pilot",
            "copper_pilot",
            "polished_andesite_pilot",
            "polished_asurine_pilot",
            "polished_calcite_pilot",
            "polished_crimsite_pilot",
            "polished_deepslate_pilot",
            "polished_diorite_pilot",
            "polished_dripstone_pilot",
            "polished_granite_pilot",
            "polished_limestone_pilot",
            "polished_ochrum_pilot",
            "polished_scorchia_pilot",
            "polished_scoria_pilot",
            "polished_tuff_pilot",
            "polished_veridium_pilot",
        ]
        .into_iter()
        .collect();
        assert_eq!(pickaxe, expected, "upstream's mineable/pickaxe tag");
        assert_eq!(pickaxe.len(), 27);
    }

    #[test]
    fn the_templates_state_spaces_add_up_to_378() {
        let states: u32 = BLOCKS
            .iter()
            .map(|block| u32::from(block.template.state_count()))
            .sum();
        assert_eq!(states, 378, "every state the 36 blocks declare");

        let ladders = BLOCKS
            .iter()
            .filter(|block| block.template == Template::Ladder)
            .count();
        let trapdoors = BLOCKS
            .iter()
            .filter(|block| block.template == Template::IronTrapdoor)
            .count();
        let pumpkins = BLOCKS
            .iter()
            .filter(|block| block.template == Template::CarvedPumpkin)
            .count();
        let panels = BLOCKS
            .iter()
            .filter(|block| block.template == Template::EndRod)
            .count();
        let casings = BLOCKS
            .iter()
            .filter(|block| block.template == Template::IronBlock)
            .count();
        assert_eq!(
            (ladders, trapdoors, pumpkins, panels, casings),
            (9, 3, 19, 2, 2)
        );
    }

    #[test]
    fn the_nine_create_only_pilots_have_no_recipe() {
        let without: BTreeSet<&str> = BLOCKS
            .iter()
            .filter(|block| block.recipes.is_empty())
            .map(|block| block.id)
            .collect();
        let expected: BTreeSet<&str> = [
            "polished_asurine_pilot",
            "polished_calcite_pilot",
            "polished_crimsite_pilot",
            "polished_dripstone_pilot",
            "polished_limestone_pilot",
            "polished_ochrum_pilot",
            "polished_scorchia_pilot",
            "polished_scoria_pilot",
            "polished_veridium_pilot",
        ]
        .into_iter()
        .collect();
        assert_eq!(
            without, expected,
            "recipes that need Create's polished-cut stones are deferred"
        );
    }

    #[test]
    fn twenty_seven_blocks_carry_forty_four_recipes() {
        assert_eq!(with_recipes().len(), 27);
        let total: usize = BLOCKS.iter().map(|block| block.recipes.len()).sum();
        assert_eq!(total, 44);
        let unique: BTreeSet<&str> = BLOCKS
            .iter()
            .flat_map(|block| block.recipes.iter().copied())
            .collect();
        assert_eq!(unique.len(), 44, "recipe file stems must be unique");
    }

    #[test]
    fn every_recipe_name_belongs_to_a_known_block_or_its_own_family() {
        let known: BTreeSet<&str> = ids();
        for block in BLOCKS {
            for recipe in block.recipes {
                assert!(
                    !recipe.is_empty()
                        && recipe
                            .bytes()
                            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_'),
                    "{}: {recipe:?} is not a recipe file stem",
                    block.id
                );
                let family = recipe
                    .strip_suffix("_stonecutting")
                    .or_else(|| recipe.strip_suffix("_from_cut"))
                    .unwrap_or(recipe);
                assert!(
                    known.contains(family)
                        || family == "headlight_2"
                        || family == "ornate_iron_window"
                        || family == "metro_sheet"
                        || family == "corrugated_metro_sheet"
                        || family == "metro_panel_from_corrugated"
                        || family == "corrugated_metro_panel_from_panel"
                        || family == "station_platform_stonecutter",
                    "{}: recipe {recipe:?} names no known block",
                    block.id
                );
            }
        }
    }
}
