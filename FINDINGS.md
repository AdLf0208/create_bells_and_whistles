# Bells & Whistles 0.4.7-1.21.1 — upstream findings

Repository: <https://github.com/sudoLev/BellsAndWhistlesMod>, branch
`1.21-forge`, release tag **`v0.4.7`** = commit
`fb2e040f70ddaf8d98101c6bd484ad597954e804` (the branch head `ba9f2e34` has an
identical `src/main/java` and `src/main/resources`, checked with `git diff`).
`gradle.properties` is `minecraft_version = 1.21.1`,
`mod_version = 0.4.7-1.21.1`, `mod_license = GPL-3.0`; the repository
`LICENSE` is the GNU GPL v3 text and the campaign source map classifies it
**GPL-3.0-or-later**. The port is local-only until the maintainer approves
publishing (ARCHITECTURE.md §8).

The clone was read for behaviour, and the mod's own textures, models, lang and
data were copied into the content tree. It was deleted after this file was
written; the rewrite lives in `../../../bellsandwhistles`.

## What was read

| Area | Files | Behaviour extracted |
|---|---|---|
| Registry | `block/ModBlocks.java:23-102` | 36 blocks; every one is a `BlockItem` too |
| Items | `item/ModItems.java:9-13` | no standalone items: all items are block items |
| Tab | `item/ModCreativeModeTabs.java:19-62` | one tab, icon `metal_pilot`, the 36-block order |
| Rails | `block/custom/MetalGrabRailsBlock.java`, `MetalBogieStepsBlock.java`, `MetalStepBlock.java` | Create's `MetalLadderBlock` (facing + waterlogged, climbable, wrenchable); custom `getShape` boxes |
| Headlight | `block/custom/HeadlightBlock.java` | `FaceAttachedHorizontalDirectionalBlock`: `face` + `facing`, lantern properties (light 15), custom shapes |
| Trapdoors | `block/custom/HeadlightBlock` neighbour, `ModBlocks.java:45,62,65` | Create's `TrainTrapdoorBlock` (a `TrapDoorBlock`); the window is a `TrapDoorBlock(BlockSetType.STONE)` |
| Platform | `block/custom/PlatformBlock.java` | horizontal facing, custom shape, skylight passing |
| Pilots | `block/custom/PilotBlock.java` | horizontal facing, custom cowcatcher shape |
| Panels | `block/custom/PanelBlock.java` | six-way `facing`, Create's `CASING_3PX` shape, copycat-style occlusion, placement helper |
| Data | `src/main/resources/data/bellsandwhistles/{loot_table,recipe}`, `data/minecraft/tags` | 36 self-drop loot tables, 52 recipes, climbable and mineable/pickaxe tags |
| Assets | `src/main/resources/assets/bellsandwhistles/**` | 38 blockstates (two are Create's train-door forms), block/item models, textures, 7 lang files |

## The 36 blocks and the vanilla template each copies

| Family | Blocks | Upstream class | Template |
|---|---|---|---|
| Grab rails / bogie steps / door steps | 3 × 3 | `MetalLadderBlock` | `minecraft:ladder` (`facing` × `waterlogged`) |
| Headlight | 1 | `FaceAttachedHorizontalDirectionalBlock` | `minecraft:lever` (`face` × `facing` × `powered`) |
| Trapdoors | `ornate_iron_trapdoor`, `metro_trapdoor`, `metro_window` | `TrapDoorBlock` | `minecraft:iron_trapdoor` (`facing` × `half` × `open` × `powered` × `waterlogged`) |
| Station platform | 1 | `PlatformBlock` | `minecraft:carved_pumpkin` (`facing`) |
| Metro casings | 2 | `Block` | `minecraft:iron_block` (one state) |
| Metro panels | 2 | `PanelBlock` | `minecraft:end_rod` (`facing`, six directions) |
| Pilots | 18 | `PilotBlock` | `minecraft:carved_pumpkin` (`facing`) |

The full table (id, hardness, sound, tool, tags, recipes) is in
`../notes.md`.

## Material properties copied from the upstream `Properties`

- Rails: `ofFullCopy(Blocks.LADDER).sound(METAL)` → hardness 0.4,
  resistance 0.4, no tool requirement.
- Headlight: `ofFullCopy(Blocks.LANTERN)` → hardness 3.5, resistance 3.5,
  **light 15**, lantern sound, no tool requirement.
- Ornate iron trapdoor: `ofFullCopy(Blocks.STONE).sound(GLASS)` → 1.5 / 6.0,
  glass sound, tool required.
- Metro casing/panel/trapdoor/window: `ofFullCopy(Blocks.MOSSY_COBBLESTONE)
  .sound(METAL)` → 2.0 / 6.0, metal sound, tool required.
- Station platform: `ofFullCopy(Blocks.SMOOTH_STONE)` → 2.0 / 6.0, stone
  sound, tool required.
- Pilots: `ofFullCopy(Blocks.IRON_BLOCK)` → 5.0 / 6.0, metal sound, tool
  required.

## Shapes

- `PlatformBlock.SHAPE` = `[0,0,8,16,16,16] ∪ [0,5,4,16,16,8]` for
  `facing=north`, rotated by the blockstate's y quarter turns.
- `PanelBlock.getShape` = Create's `AllShapes.CASING_3PX`, a three-pixel
  plate on the `facing` side.
- The rails, headlight and pilots have hand-written shapes (some boxes extend
  outside the block, e.g. the pilot from y=-12 to 14); these are **not**
  declared — the templates' shapes stay. Recorded as a deviation.

## Create dependencies (the reason for the template choices)

The mod is a Create add-on. The classes it extends are Create's:
`MetalLadderBlock` (a `LadderBlock` with Create's metal model), 
`TrainTrapdoorBlock` (a `TrapDoorBlock`), `IWrenchable`, and `PanelBlock`
extends `CopycatPanelBlock` with `AllShapes`/`PlacementHelpers`. Horizon has
no Create, so the port maps each class to the vanilla class it derives from
(see the template table). Deferred with the Create dependency:

- **Wrench behaviour** (`IWrenchable`) — no Create wrench item.
- **Panel placement helper / copycat occlusion** — Create's `PlacementHelper`
  and `CopycatSpecialCases`; the port keeps the vanilla template's occlusion
  and the declared `shapes`.
- **Train doors** (`folding_metro_door`, `sliding_metro_door`) — assets exist
  in the jar but `ModBlocks` does not register them at 0.4.7; they are
  Create's train-door blocks (contraption behaviour), out of scope. Their
  blockstates/item models were not carried.
- **Create-material recipes** — see the material map in `../notes.md`.

## Recipes

52 recipe files under `data/bellsandwhistles/recipe`. Nine are for the
Create polished-cut stone types (`asurine`, `calcite`, `crimsite`,
`dripstone`, `limestone`, `ochrum`, `scoria`, `scorchia`, `veridium`) and
cannot be expressed with 26.3 vanilla items; they are deferred (the blocks
stay, creative-only). The other 44 are carried with a documented vanilla
material map (`create:andesite_alloy` → `minecraft:andesite`, brass ingots /
nuggets → copper, sheets → ingots, `create:ornate_iron_window` → iron bars,
`c:glass` → glass). The two door-step recipes lived under `recipe/door_steps/`
with grab-rail file names; 26.3 flattens recipes, so they take their output's
name (`<metal>_door_step`).

## Loot and tags

Every loot table drops its own block with `minecraft:survives_explosion`.
Upstream copies `minecraft:blocks/acacia_log` as the `random_sequence` for
almost every table (a datagen copy-paste bug); the port writes
`bellsandwhistles:blocks/<id>`. The tags are `#minecraft:climbable` (six
rails) and `#minecraft:mineable/pickaxe` (27 stone/metal blocks); upstream
writes `"replace": false`, which 26.3's tag loader does not need.

## Differences from upstream (summary)

1. Vanilla templates instead of Create classes; Create's wrench, placement
   helper and copycat occlusion are not carried.
2. The headlight copies `minecraft:lever` (the only vanilla
   face-attached-horizontal block without a menu) and therefore has a
   `powered` state and toggles/redstone on right-click; the model ignores it.
3. Custom collision/selection shapes are only declared for the platform and
   panels; rails/headlight/pilots keep the template shape.
4. 44 of 52 recipes carried; 9 Create-stone pilots have none.
5. `random_sequence` normalised.
6. No block entity, entity, menu, renderer, config or network code: the whole
   slice is content.
