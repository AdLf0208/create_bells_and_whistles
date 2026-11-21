// Bells and Whistles for Horizon — the decorative content catalogue (pure).
//
// Ported from Create: Bells & Whistles 0.4.7-1.21.1
// (sudoLev/BellsAndWhistlesMod, GPL-3.0) for Minecraft Java 1.21.1
// NeoForge. Upstream source was read for the registry, the block classes and
// the datagen shapes; this is a clean-room Rust rewrite. The slice is
// content-only: the 36 decorative blocks and their items, loot, recipes, tags
// and creative tab are declared in ../content, and this model is the single
// place their template, light, tag membership, item, loot and recipe coverage
// are spelled out (ModBlocks.java:20-99, ModCreativeModeTabs.java:22-63).

#[cfg(test)]
mod tests {
    use std::collections::{BTreeMap, BTreeSet};

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
    pub struct BlockSpec {
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
    pub const BLOCKS: [BlockSpec; 36] = [
        BlockSpec {
            id: "andesite_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_bogie_steps", "andesite_bogie_steps_stonecutting"],
        },
        BlockSpec {
            id: "brass_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_bogie_steps", "brass_bogie_steps_stonecutting"],
        },
        BlockSpec {
            id: "copper_bogie_steps",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_bogie_steps", "copper_bogie_steps_stonecutting"],
        },
        BlockSpec {
            id: "andesite_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_grab_rails", "andesite_grab_rails_stonecutting"],
        },
        BlockSpec {
            id: "brass_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_grab_rails", "brass_grab_rails_stonecutting"],
        },
        BlockSpec {
            id: "copper_grab_rails",
            template: Template::Ladder,
            light: 0,
            climbable: true,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_grab_rails", "copper_grab_rails_stonecutting"],
        },
        BlockSpec {
            id: "andesite_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["andesite_door_step", "andesite_door_step_stonecutting"],
        },
        BlockSpec {
            id: "brass_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["brass_door_step", "brass_door_step_stonecutting"],
        },
        BlockSpec {
            id: "copper_door_step",
            template: Template::Ladder,
            light: 0,
            climbable: false,
            pickaxe: false,
            item: true,
            loot: true,
            recipes: &["copper_door_step", "copper_door_step_stonecutting"],
        },
        BlockSpec {
            id: "ornate_iron_trapdoor",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["ornate_iron_window"],
        },
        BlockSpec {
            id: "headlight",
            template: Template::Lever,
            light: 15,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["headlight", "headlight_2"],
        },
        BlockSpec {
            id: "station_platform",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["station_platform", "station_platform_stonecutter"],
        },
        BlockSpec {
            id: "metro_casing",
            template: Template::IronBlock,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_sheet"],
        },
        BlockSpec {
            id: "corrugated_metro_casing",
            template: Template::IronBlock,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["corrugated_metro_sheet"],
        },
        BlockSpec {
            id: "metro_panel",
            template: Template::EndRod,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_panel", "metro_panel_from_corrugated"],
        },
        BlockSpec {
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
        BlockSpec {
            id: "metro_trapdoor",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_trapdoor"],
        },
        BlockSpec {
            id: "metro_window",
            template: Template::IronTrapdoor,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metro_window"],
        },
        BlockSpec {
            id: "andesite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["andesite_pilot"],
        },
        BlockSpec {
            id: "brass_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["brass_pilot"],
        },
        BlockSpec {
            id: "copper_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["copper_pilot"],
        },
        BlockSpec {
            id: "metal_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["metal_pilot"],
        },
        BlockSpec {
            id: "polished_andesite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_andesite_pilot"],
        },
        BlockSpec {
            id: "polished_granite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_granite_pilot"],
        },
        BlockSpec {
            id: "polished_diorite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_diorite_pilot"],
        },
        BlockSpec {
            id: "polished_deepslate_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_deepslate_pilot"],
        },
        BlockSpec {
            id: "polished_dripstone_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_tuff_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &["polished_tuff_pilot"],
        },
        BlockSpec {
            id: "polished_calcite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_limestone_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_scoria_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_scorchia_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_crimsite_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_ochrum_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
            id: "polished_veridium_pilot",
            template: Template::CarvedPumpkin,
            light: 0,
            climbable: false,
            pickaxe: true,
            item: true,
            loot: true,
            recipes: &[],
        },
        BlockSpec {
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
    fn twenty_seven_blocks_carry_forty_recipes() {
        assert_eq!(with_recipes().len(), 27);
        let total: usize = BLOCKS.iter().map(|block| block.recipes.len()).sum();
        assert_eq!(total, 40, "the carried recipe files");
        let unique: BTreeSet<&str> = BLOCKS
            .iter()
            .flat_map(|block| block.recipes.iter().copied())
            .collect();
        assert_eq!(unique.len(), 40, "recipe file stems must be unique");
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
                let family = recipe.strip_suffix("_stonecutting").unwrap_or(recipe);
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

    // ------------------------------------------------------- the recipe family
    //
    // The rules below run on the shipped files themselves
    // (`data/bellsandwhistles/recipe/*.json`), not on a second hand-written
    // table, so the content and this catalogue cannot drift. They are the
    // rules the 26.3 recipe manager applies: a shaped grid matches at any
    // offset and in either mirror orientation (vanilla's `ShapedRecipe`), a
    // shapeless recipe matches any arrangement, and a stonecutter offers every
    // recipe its input allows (so stonecutting recipes never shadow one
    // another, while two crafting-table recipes that fill the same grid do).

    /// The station a recipe is used at.
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    enum Station {
        /// A crafting table: one grid, one result, and a second recipe that
        /// fills the same grid can never be chosen.
        Table,
        /// A stonecutter: every recipe the input allows is offered and the
        /// player picks one, so results do not shadow one another.
        Stonecutter,
    }

    /// One carried recipe, parsed from `data/bellsandwhistles/recipe/<file>.json`.
    #[derive(Clone, Debug, PartialEq, Eq)]
    struct CarriedRecipe {
        /// The file stem (`andesite_bogie_steps`, ...).
        file: String,
        /// The result item id.
        output: String,
        /// How many the craft yields (1 when the file omits it).
        count: u32,
        station: Station,
        body: Grid,
    }

    /// What a recipe's grid or ingredient list is.
    #[derive(Clone, Debug, PartialEq, Eq)]
    enum Grid {
        /// A shaped pattern: its item ids padded to 3x3, plus its own size.
        /// A space in the pattern is `None` and is never matched.
        Shaped {
            grid: Box<[[Option<String>; 3]; 3]>,
            height: usize,
            width: usize,
        },
        /// A shapeless recipe's ingredients, or the stonecutter's one input.
        Loose(Vec<String>),
    }

    /// The subset of JSON the recipe files use: objects, arrays, strings and
    /// numbers.
    #[derive(Clone, Debug, PartialEq)]
    enum Json {
        Word(String),
        Number(f64),
        Array(Vec<Json>),
        Object(Vec<(String, Json)>),
    }

    /// A byte cursor over one recipe file.
    struct Cursor<'a> {
        text: &'a str,
        at: usize,
    }

    impl Cursor<'_> {
        fn skip_space(&mut self) {
            let rest = &self.text[self.at..];
            self.at += rest.len() - rest.trim_start().len();
        }

        fn peek(&self) -> Option<char> {
            self.text[self.at..].chars().next()
        }

        fn take(&mut self) -> Option<char> {
            let c = self.peek()?;
            self.at += c.len_utf8();
            Some(c)
        }

        fn expect(&mut self, want: char) {
            let got = self.take();
            assert_eq!(got, Some(want), "expected {want:?} at byte {}", self.at);
        }

        fn text(&mut self) -> String {
            self.expect('"');
            let mut out = String::new();
            loop {
                match self.take().expect("a string ends with a quote") {
                    '"' => return out,
                    '\\' => match self.take().expect("an escape has a character") {
                        'n' => out.push('\n'),
                        't' => out.push('\t'),
                        other => out.push(other),
                    },
                    c => out.push(c),
                }
            }
        }

        fn number(&mut self) -> f64 {
            let start = self.at;
            while self
                .peek()
                .is_some_and(|c| c.is_ascii_digit() || matches!(c, '-' | '+' | '.' | 'e' | 'E'))
            {
                self.at += 1;
            }
            self.text[start..self.at]
                .parse()
                .expect("a number field parses")
        }

        fn value(&mut self) -> Json {
            self.skip_space();
            match self.peek() {
                Some('"') => Json::Word(self.text()),
                Some('{') => {
                    self.take();
                    let mut fields = Vec::new();
                    self.skip_space();
                    if self.peek() == Some('}') {
                        self.take();
                        return Json::Object(fields);
                    }
                    loop {
                        self.skip_space();
                        let name = self.text();
                        self.skip_space();
                        self.expect(':');
                        let value = self.value();
                        fields.push((name, value));
                        self.skip_space();
                        match self.take() {
                            Some(',') => continue,
                            Some('}') => return Json::Object(fields),
                            other => {
                                panic!("an object ends with }} or ,: {other:?} at {}", self.at)
                            }
                        }
                    }
                }
                Some('[') => {
                    self.take();
                    let mut items = Vec::new();
                    self.skip_space();
                    if self.peek() == Some(']') {
                        self.take();
                        return Json::Array(items);
                    }
                    loop {
                        items.push(self.value());
                        self.skip_space();
                        match self.take() {
                            Some(',') => continue,
                            Some(']') => return Json::Array(items),
                            other => panic!("an array ends with ] or ,: {other:?} at {}", self.at),
                        }
                    }
                }
                Some(c) if c.is_ascii_digit() || c == '-' => Json::Number(self.number()),
                other => panic!("unexpected {other:?} at byte {}", self.at),
            }
        }
    }

    fn parse_json(text: &str) -> Json {
        let mut cursor = Cursor { text, at: 0 };
        let value = cursor.value();
        cursor.skip_space();
        assert_eq!(cursor.at, text.len(), "trailing text after the JSON value");
        value
    }

    fn field<'a>(object: &'a [(String, Json)], name: &str) -> &'a Json {
        object
            .iter()
            .find(|(key, _)| key == name)
            .map(|(_, value)| value)
            .unwrap_or_else(|| panic!("no {name:?} field"))
    }

    fn text_of(value: &Json) -> &str {
        match value {
            Json::Word(text) => text,
            other => panic!("expected a string, got {other:?}"),
        }
    }

    fn strings(value: &Json) -> Vec<String> {
        match value {
            Json::Array(items) => items.iter().map(|item| text_of(item).to_owned()).collect(),
            other => panic!("expected an array of strings, got {other:?}"),
        }
    }

    fn parse_recipe(file: &str, text: &str) -> CarriedRecipe {
        let Json::Object(fields) = parse_json(text) else {
            panic!("{file}: a recipe file is an object")
        };
        let Json::Object(result) = field(&fields, "result") else {
            panic!("{file}: result is an object")
        };
        let output = text_of(field(result, "id")).to_owned();
        let count = result
            .iter()
            .find(|(key, _)| key == "count")
            .map(|(_, value)| match value {
                Json::Number(number) => *number as u32,
                other => panic!("{file}: count is {other:?}"),
            })
            .unwrap_or(1);
        let kind = text_of(field(&fields, "type")).to_owned();
        let (station, body) = match kind.as_str() {
            "minecraft:crafting_shaped" => {
                let pattern = strings(field(&fields, "pattern"));
                let Json::Object(key) = field(&fields, "key") else {
                    panic!("{file}: key is an object")
                };
                let symbol = |c: char| -> String {
                    let name = c.to_string();
                    let (_, item) = key
                        .iter()
                        .find(|(symbol, _)| *symbol == name)
                        .unwrap_or_else(|| {
                            panic!("{file}: the pattern uses {c:?}, the key has no such symbol")
                        });
                    text_of(item).to_owned()
                };
                let height = pattern.len();
                let width = pattern.first().map_or(0, |row| row.chars().count());
                assert!(
                    (1..=3).contains(&height) && (1..=3).contains(&width),
                    "{file}: a {height}x{width} pattern does not fit the 3x3 grid"
                );
                let mut grid: [[Option<String>; 3]; 3] = Default::default();
                for (y, row) in pattern.iter().enumerate() {
                    assert_eq!(
                        row.chars().count(),
                        width,
                        "{file}: the pattern rows differ in width"
                    );
                    for (x, c) in row.chars().enumerate() {
                        if c != ' ' {
                            grid[y][x] = Some(symbol(c));
                        }
                    }
                }
                (
                    Station::Table,
                    Grid::Shaped {
                        grid: Box::new(grid),
                        height,
                        width,
                    },
                )
            }
            "minecraft:crafting_shapeless" => (
                Station::Table,
                Grid::Loose(strings(field(&fields, "ingredients"))),
            ),
            "minecraft:stonecutting" => (
                Station::Stonecutter,
                Grid::Loose(vec![text_of(field(&fields, "ingredient")).to_owned()]),
            ),
            other => panic!("{file}: unknown recipe type {other}"),
        };
        CarriedRecipe {
            file: file.to_owned(),
            output,
            count,
            station,
            body,
        }
    }

    /// The recipe directory, in file-name order.
    fn carried_recipes() -> Vec<CarriedRecipe> {
        let dir = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("data/bellsandwhistles/recipe");
        let mut paths: Vec<std::path::PathBuf> = std::fs::read_dir(&dir)
            .unwrap_or_else(|error| panic!("{}: {error}", dir.display()))
            .flatten()
            .map(|entry| entry.path())
            .filter(|path| path.extension().is_some_and(|ext| ext == "json"))
            .collect();
        paths.sort();
        paths
            .iter()
            .map(|path| {
                let file = path
                    .file_stem()
                    .expect("a recipe file has a stem")
                    .to_string_lossy()
                    .into_owned();
                let text = std::fs::read_to_string(path)
                    .unwrap_or_else(|error| panic!("{}: {error}", path.display()));
                parse_recipe(&file, &text)
            })
            .collect()
    }

    /// The item ids one craft needs, with how many of each.
    fn needed(recipe: &CarriedRecipe) -> BTreeMap<&str, usize> {
        let mut out = BTreeMap::new();
        match &recipe.body {
            Grid::Shaped {
                grid,
                height,
                width,
            } => {
                for row in grid.iter().take(*height) {
                    for id in row.iter().take(*width).flatten() {
                        *out.entry(id.as_str()).or_insert(0) += 1;
                    }
                }
            }
            Grid::Loose(items) => {
                for id in items {
                    *out.entry(id.as_str()).or_insert(0) += 1;
                }
            }
        }
        out
    }

    /// Vanilla's `ShapedRecipe` match: the pattern is tried at every offset and
    /// in both mirror orientations. Every one of the 3x3 cells is checked — the
    /// pattern's own cells for their item (or emptiness, for a space) and every
    /// cell outside the pattern for emptiness — so a grid with an extra item
    /// does not match a smaller pattern.
    fn shaped_accepts(want: &CarriedRecipe, grid: &[[Option<String>; 3]; 3]) -> bool {
        let Grid::Shaped {
            grid: pattern,
            height,
            width,
        } = &want.body
        else {
            panic!("{}: not a shaped recipe", want.file)
        };
        for dy in 0..=(3 - height) {
            for dx in 0..=(3 - width) {
                for mirror in [false, true] {
                    let mut ok = true;
                    'cells: for (gy, row) in grid.iter().enumerate() {
                        for (gx, cell) in row.iter().enumerate() {
                            let px = gx as isize - dx as isize;
                            let py = gy as isize - dy as isize;
                            let inside = px >= 0
                                && py >= 0
                                && (px as usize) < *width
                                && (py as usize) < *height;
                            let expected = if inside {
                                let px = if mirror {
                                    width - 1 - px as usize
                                } else {
                                    px as usize
                                };
                                pattern[py as usize][px].as_deref()
                            } else {
                                None
                            };
                            if cell.as_deref() != expected {
                                ok = false;
                                break 'cells;
                            }
                        }
                    }
                    if ok {
                        return true;
                    }
                }
            }
        }
        false
    }

    /// Does `other`'s rule accept the craft `candidate` describes?
    fn accepts(other: &CarriedRecipe, candidate: &CarriedRecipe) -> bool {
        match (&other.body, &candidate.body) {
            (Grid::Shaped { .. }, Grid::Shaped { grid, .. }) => shaped_accepts(other, grid),
            // A shapeless ingredient list can be arranged in any order, so the
            // rule is the multiset: equal halves always have a fitting arrangement.
            _ => needed(other) == needed(candidate),
        }
    }

    /// Two crafting-table recipes that fill the same grid: only one of them can
    /// ever be chosen, so the other is dead data. A stonecutter lists what its
    /// input allows, so its recipes never shadow one another.
    fn collides(a: &CarriedRecipe, b: &CarriedRecipe) -> bool {
        a.station == Station::Table
            && b.station == Station::Table
            && (accepts(b, a) || accepts(a, b))
    }

    #[test]
    fn the_carried_recipe_files_are_exactly_the_catalogue() {
        let on_disk: BTreeSet<String> = carried_recipes().into_iter().map(|r| r.file).collect();
        let catalogued: BTreeSet<String> = BLOCKS
            .iter()
            .flat_map(|block| block.recipes.iter().map(|name| (*name).to_owned()))
            .collect();
        assert_eq!(
            on_disk, catalogued,
            "every file under data/bellsandwhistles/recipe must be in BLOCKS and back"
        );
    }

    #[test]
    fn no_two_carried_recipes_fill_the_same_grid() {
        let recipes = carried_recipes();
        for (index, a) in recipes.iter().enumerate() {
            for b in &recipes[index + 1..] {
                if a.output == b.output && a.count == b.count {
                    continue;
                }
                assert!(
                    !collides(a, b),
                    "{} and {} fill the same crafting grid ({} {} vs {} {}), so one can never be crafted",
                    a.file,
                    b.file,
                    a.count,
                    a.output,
                    b.count,
                    b.output
                );
            }
        }
    }

    #[test]
    fn no_two_stonecutting_recipes_offer_the_same_result() {
        let recipes = carried_recipes();
        for (index, a) in recipes.iter().enumerate() {
            for b in &recipes[index + 1..] {
                if a.station != Station::Stonecutter || b.station != Station::Stonecutter {
                    continue;
                }
                assert!(
                    !(a.output == b.output && a.count == b.count && needed(a) == needed(b)),
                    "{} and {} are the same stonecutter offer",
                    a.file,
                    b.file
                );
            }
        }
    }

    #[test]
    fn every_carried_recipe_uses_a_resolvable_item() {
        for recipe in carried_recipes() {
            assert!(
                recipe.output.contains(':'),
                "{}: output {:?} is not namespaced",
                recipe.file,
                recipe.output
            );
            assert!(
                recipe.count >= 1 && recipe.count <= 64,
                "{}: a count of {} is not a stack",
                recipe.file,
                recipe.count
            );
            for ingredient in needed(&recipe).keys() {
                assert!(
                    ingredient.contains(':') && !ingredient.starts_with('#'),
                    "{}: ingredient {ingredient:?} is not an item id",
                    recipe.file
                );
                assert!(
                    !ingredient.starts_with("create:"),
                    "{}: ingredient {ingredient} needs Create, which is not ported",
                    recipe.file
                );
            }
        }
    }

    /// The mod's own metals stay apart: brass is not copper. The port maps
    /// Create's brass to vanilla gold (the only yellow metal) and its copper to
    /// copper, one to one — before that, both mapped to copper and the four
    /// brass recipes were the same grids as the copper ones.
    #[test]
    fn brass_recipes_name_gold_and_copper_recipes_name_copper() {
        for recipe in carried_recipes() {
            let ingredient_ids: Vec<&str> = needed(&recipe).keys().copied().collect();
            let has = |id: &str| ingredient_ids.contains(&id);
            if recipe.file.starts_with("brass_") {
                assert!(
                    has("minecraft:gold_ingot") || has("minecraft:gold_nugget"),
                    "{}: a brass recipe names no gold: {ingredient_ids:?}",
                    recipe.file
                );
                assert!(
                    !has("minecraft:copper_ingot") && !has("minecraft:copper_nugget"),
                    "{}: a brass recipe is copper again: {ingredient_ids:?}",
                    recipe.file
                );
            }
            if recipe.file.starts_with("copper_") {
                assert!(
                    has("minecraft:copper_ingot") || has("minecraft:copper_nugget"),
                    "{}: a copper recipe names no copper: {ingredient_ids:?}",
                    recipe.file
                );
            }
        }
    }

    /// Upstream ships the headlight in both orientations. 26.3's shaped match
    /// tries mirrors, so the two files fill one grid — which is why the pair is
    /// exempt from the collision rule and why one grid crafts the headlight.
    #[test]
    fn the_two_headlight_files_are_mirror_images() {
        let recipes = carried_recipes();
        let headlight = recipes
            .iter()
            .find(|recipe| recipe.file == "headlight")
            .expect("headlight.json ships");
        let mirror = recipes
            .iter()
            .find(|recipe| recipe.file == "headlight_2")
            .expect("headlight_2.json ships");
        assert_eq!(
            headlight.output, mirror.output,
            "both files yield the same item"
        );
        assert_eq!(headlight.count, mirror.count);
        let Grid::Shaped { grid, .. } = &mirror.body else {
            panic!("headlight_2 is shaped")
        };
        assert!(
            shaped_accepts(headlight, grid),
            "the second headlight pattern is the first one mirrored, so 26.3 matches both"
        );
    }
}
