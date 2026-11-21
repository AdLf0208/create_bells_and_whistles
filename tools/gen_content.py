#!/usr/bin/env python3
"""Generate the Bells & Whistles content tree from the upstream checkout.

Slice 1 is the 36 decorative blocks the upstream `ModBlocks` registers: the
nine metal rail blocks (grab rails, bogie steps, door steps), the headlight,
the ornate iron trapdoor, the station platform, the metro casing/panel/
trapdoor/window set and the eighteen pilots. Textures, models and lang are
copied from the upstream repository (GPL-3.0, see ../LICENSE). Data
files are rewritten into the 26.3 formats the pinned Horizon loader reads;
every rewrite and every material substitution is noted in ../notes.md.

Usage:
    python3 tools/gen_content.py --upstream ../_shared/upstream/bellsandwhistles
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

NAMESPACE = "bellsandwhistles"

# The vanilla templates the port copies. `state_count` is the template's own
# state space, which the runtime catalogue and the e2e enumerate.
LADDER = "ladder"
TRAPDOOR = "trapdoor"
LEVER = "lever"
PUMPKIN = "pumpkin"
END_ROD = "end_rod"
IRON_BLOCK = "iron_block"

TEMPLATES = {
    LADDER: {
        "template": "minecraft:ladder",
        "properties": {
            "hardness": 0.4,
            "explosion_resistance": 0.4,
            "sounds": "minecraft:iron_block",
            "requires_tool": False,
        },
    },
    "ornate_trapdoor": {
        "template": "minecraft:iron_trapdoor",
        "properties": {
            "hardness": 1.5,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:glass",
            "requires_tool": True,
        },
    },
    TRAPDOOR: {
        "template": "minecraft:iron_trapdoor",
        "properties": {
            "hardness": 2.0,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:iron_block",
            "requires_tool": True,
        },
    },
    LEVER: {
        "template": "minecraft:lever",
        "properties": {
            "hardness": 3.5,
            "explosion_resistance": 3.5,
            "sounds": "minecraft:lantern",
            "light": 15,
            "requires_tool": False,
        },
        "default_state": {"face": "wall", "facing": "north"},
    },
    "platform": {
        "template": "minecraft:carved_pumpkin",
        "properties": {
            "hardness": 2.0,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:stone",
            "requires_tool": True,
        },
    },
    "pilot": {
        "template": "minecraft:carved_pumpkin",
        "properties": {
            "hardness": 5.0,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:iron_block",
            "requires_tool": True,
        },
    },
    END_ROD: {
        "template": "minecraft:end_rod",
        "properties": {
            "hardness": 2.0,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:iron_block",
            "requires_tool": True,
        },
        "default_state": {"facing": "up"},
    },
    IRON_BLOCK: {
        "template": "minecraft:iron_block",
        "properties": {
            "hardness": 2.0,
            "explosion_resistance": 6.0,
            "sounds": "minecraft:iron_block",
            "requires_tool": True,
        },
    },
}

# The station platform's shape: upstream `PlatformBlock.SHAPE`, rotated the
# same way the blockstate's y rotation turns the north model (a clockwise
# quarter turn maps (x, z) to (1 - z, x)).
PLATFORM_NORTH = [
    [0.0, 0.0, 0.5, 1.0, 1.0, 1.0],
    [0.0, 0.3125, 0.25, 1.0, 1.0, 0.5],
]

# Create's `AllShapes.CASING_3PX`: a three-pixel plate on the facing side.
PANEL_SHAPES = {
    "up": [[0.0, 0.8125, 0.0, 1.0, 1.0, 1.0]],
    "down": [[0.0, 0.0, 0.0, 1.0, 0.1875, 1.0]],
    "north": [[0.0, 0.0, 0.0, 1.0, 1.0, 0.1875]],
    "south": [[0.0, 0.0, 0.8125, 1.0, 1.0, 1.0]],
    "west": [[0.0, 0.0, 0.0, 0.1875, 1.0, 1.0]],
    "east": [[0.8125, 0.0, 0.0, 1.0, 1.0, 1.0]],
}


def rotate_north(boxes, quarter_turns):
    """Rotate boxes clockwise about the block centre, (x, z) -> (1 - z, x)."""
    result = boxes
    for _ in range(quarter_turns):
        result = [
            [1.0 - b[5], b[1], b[0], 1.0 - b[2], b[4], b[3]] for b in result
        ]
    return result


def platform_shapes():
    return {
        facing: rotate_north(PLATFORM_NORTH, turns)
        for facing, turns in (
            ("north", 0),
            ("east", 1),
            ("south", 2),
            ("west", 3),
        )
    }


# (id, template key, climbable, pickaxe, recipes)
BLOCKS = [
    ("andesite_bogie_steps", LADDER, True, False,
     ["andesite_bogie_steps", "andesite_bogie_steps_stonecutting"]),
    ("brass_bogie_steps", LADDER, True, False,
     ["brass_bogie_steps", "brass_bogie_steps_stonecutting"]),
    ("copper_bogie_steps", LADDER, True, False,
     ["copper_bogie_steps", "copper_bogie_steps_stonecutting"]),
    ("andesite_grab_rails", LADDER, True, False,
     ["andesite_grab_rails", "andesite_grab_rails_stonecutting"]),
    ("brass_grab_rails", LADDER, True, False,
     ["brass_grab_rails", "brass_grab_rails_stonecutting"]),
    ("copper_grab_rails", LADDER, True, False,
     ["copper_grab_rails", "copper_grab_rails_stonecutting"]),
    ("andesite_door_step", LADDER, False, False,
     ["andesite_door_step", "andesite_door_step_stonecutting"]),
    ("brass_door_step", LADDER, False, False,
     ["brass_door_step", "brass_door_step_stonecutting"]),
    ("copper_door_step", LADDER, False, False,
     ["copper_door_step", "copper_door_step_stonecutting"]),
    ("ornate_iron_trapdoor", "ornate_trapdoor", False, True,
     ["ornate_iron_window"]),
    ("headlight", LEVER, False, True, ["headlight", "headlight_2"]),
    ("station_platform", "platform", False, True,
     ["station_platform", "station_platform_stonecutter"]),
    ("metro_casing", IRON_BLOCK, False, True, ["metro_sheet"]),
    ("corrugated_metro_casing", IRON_BLOCK, False, True,
     ["corrugated_metro_sheet"]),
    ("metro_panel", END_ROD, False, True,
     ["metro_panel", "metro_panel_from_corrugated"]),
    ("corrugated_metro_panel", END_ROD, False, True,
     ["corrugated_metro_panel", "corrugated_metro_panel_from_panel"]),
    ("metro_trapdoor", TRAPDOOR, False, True, ["metro_trapdoor"]),
    ("metro_window", TRAPDOOR, False, True, ["metro_window"]),
    ("andesite_pilot", "pilot", False, True, ["andesite_pilot"]),
    ("brass_pilot", "pilot", False, True, ["brass_pilot"]),
    ("copper_pilot", "pilot", False, True, ["copper_pilot"]),
    ("metal_pilot", "pilot", False, True, ["metal_pilot"]),
    ("polished_andesite_pilot", "pilot", False, True,
     ["polished_andesite_pilot", "polished_andesite_pilot_from_cut"]),
    ("polished_granite_pilot", "pilot", False, True,
     ["polished_granite_pilot", "polished_granite_pilot_from_cut"]),
    ("polished_diorite_pilot", "pilot", False, True,
     ["polished_diorite_pilot", "polished_diorite_pilot_from_cut"]),
    ("polished_deepslate_pilot", "pilot", False, True,
     ["polished_deepslate_pilot", "polished_deepslate_pilot_from_cut"]),
    ("polished_dripstone_pilot", "pilot", False, True, []),
    ("polished_tuff_pilot", "pilot", False, True, ["polished_tuff_pilot"]),
    ("polished_calcite_pilot", "pilot", False, True, []),
    ("polished_limestone_pilot", "pilot", False, True, []),
    ("polished_scoria_pilot", "pilot", False, True, []),
    ("polished_scorchia_pilot", "pilot", False, True, []),
    ("polished_crimsite_pilot", "pilot", False, True, []),
    ("polished_ochrum_pilot", "pilot", False, True, []),
    ("polished_veridium_pilot", "pilot", False, True, []),
    ("polished_asurine_pilot", "pilot", False, True, []),
]

# Upstream recipe path -> the 26.3 file stem. The two door-step recipes lived
# under `recipe/door_steps/` with grab-rail file names; 26.3 recipes are flat,
# so they take their output's name.
#
# `polished_{andesite,deepslate,diorite,granite}_pilot_from_cut` are not
# carried: their ingredient is Create's `polished_cut_*`, and the only 26.3
# stand-in is the same `polished_*` block the base file already uses, so the
# copy would be the same recipe file twice (dead data, 0.3.0). `polished_tuff`
# has no vanilla twin, so its `create:polished_cut_tuff` file IS the recipe.
RECIPE_FILES = {}
for metal in ("andesite", "brass", "copper"):
    for kind in ("bogie_steps", "grab_rails"):
        RECIPE_FILES[f"{kind}/{metal}_{kind}.json"] = f"{metal}_{kind}"
        RECIPE_FILES[f"{kind}/{metal}_{kind}_stonecutting.json"] = (
            f"{metal}_{kind}_stonecutting"
        )
for metal in ("andesite", "brass", "copper"):
    RECIPE_FILES[f"door_steps/{metal}_grab_rails.json"] = f"{metal}_door_step"
    RECIPE_FILES[f"door_steps/{metal}_grab_rails_stonecutting.json"] = (
        f"{metal}_door_step_stonecutting"
    )
RECIPE_FILES.update(
    {
        "headlight.json": "headlight",
        "headlight_2.json": "headlight_2",
        "metro/corrugated_metro_panel_from_panel.json": (
            "corrugated_metro_panel_from_panel"
        ),
        "metro/corrugated_metro_panel.json": "corrugated_metro_panel",
        "metro/corrugated_metro_sheet.json": "corrugated_metro_sheet",
        "metro/metro_panel_from_corrugated.json": "metro_panel_from_corrugated",
        "metro/metro_panel.json": "metro_panel",
        "metro/metro_sheet.json": "metro_sheet",
        "metro/metro_trapdoor.json": "metro_trapdoor",
        "metro/metro_window.json": "metro_window",
        "ornate_iron_window.json": "ornate_iron_window",
        "pilots/andesite_pilot.json": "andesite_pilot",
        "pilots/brass_pilot.json": "brass_pilot",
        "pilots/copper_pilot.json": "copper_pilot",
        "pilots/metal_pilot.json": "metal_pilot",
        "pilots/polished_andesite_pilot.json": "polished_andesite_pilot",
        "pilots/polished_deepslate_pilot.json": "polished_deepslate_pilot",
        "pilots/polished_diorite_pilot.json": "polished_diorite_pilot",
        "pilots/polished_granite_pilot.json": "polished_granite_pilot",
        "pilots/polished_tuff_pilot.json": "polished_tuff_pilot",
        "station_platform.json": "station_platform",
        "station_platform_stonecutter.json": "station_platform_stonecutter",
    }
)

# Create's materials mapped onto 26.3's vanilla ones. Create is not ported, so
# a recipe that kept `create:*` would load without its ingredient; the
# substitution keeps every carried recipe craftable and is recorded in
# ../notes.md. The nine polished-cut stone types with no vanilla equivalent
# keep no recipe at all (see BLOCKS).ITEM_MAP = {
    "create:andesite_alloy": "minecraft:andesite",
    # Brass is the yellow metal, so it maps to vanilla gold and copper to
    # copper — one to one. (Both used to map to copper, which made the four
    # brass crafting recipes the same grids as their copper counterparts, so
    # one of each pair could never be crafted: notes.md, 0.3.0.)
    "create:brass_sheet": "minecraft:gold_ingot",
    "create:brass_nugget": "minecraft:gold_nugget",
    "create:copper_sheet": "minecraft:copper_ingot",
    "create:copper_nugget": "minecraft:copper_nugget",
    "create:iron_sheet": "minecraft:iron_ingot",
    "create:ornate_iron_window": "minecraft:iron_bars",
    "create:polished_cut_andesite": "minecraft:polished_andesite",
    "create:polished_cut_andesite_stairs": "minecraft:polished_andesite_stairs",
    "create:polished_cut_deepslate": "minecraft:polished_deepslate",
    "create:polished_cut_deepslate_stairs": "minecraft:polished_deepslate_stairs",
    "create:polished_cut_diorite": "minecraft:polished_diorite",
    "create:polished_cut_diorite_stairs": "minecraft:polished_diorite_stairs",
    "create:polished_cut_granite": "minecraft:polished_granite",
    "create:polished_cut_granite_stairs": "minecraft:polished_granite_stairs",
    "create:polished_cut_tuff": "minecraft:polished_tuff",
    "create:polished_cut_tuff_stairs": "minecraft:polished_tuff_stairs",
}
TAG_MAP = {
    "c:ingots/brass": "minecraft:gold_ingot",
    "c:nuggets/brass": "minecraft:gold_nugget",
    "c:ingots/copper": "minecraft:copper_ingot",
    "c:nuggets/copper": "minecraft:copper_nugget",
    "c:glass": "minecraft:glass",
}

# Upstream shapes that a 26.3 *vanilla* recipe already fills. The andesite
# door step was three andesite in a row, which is exactly vanilla's
# `andesite_slab` grid, so the dropper could only ever get slabs; two andesite
# is the nearest grid vanilla does not claim (notes.md, 0.3.0).
RECIPE_PATCHES = {
    "andesite_door_step": {"pattern": ["##"]},
}


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value)
    else:
        path.write_text(json.dumps(value, indent=2) + "\n")


def ingredient(value):
    """A 1.21.1 ingredient object as a 26.3 item string or `#tag`."""
    if isinstance(value, str):
        return value if ":" in value else f"minecraft:{value}"
    if isinstance(value, list):
        return [ingredient(v) for v in value]
    if "item" in value:
        item = value["item"]
        return ITEM_MAP.get(item, item if ":" in item else f"minecraft:{item}")
    if "tag" in value:
        tag = value["tag"]
        if tag in TAG_MAP:
            return TAG_MAP[tag]
        return "#" + tag
    raise ValueError(f"unknown ingredient shape: {value!r}")


def upgrade_recipe(old: dict) -> dict:
    """Rewrite one 1.21.1 recipe into the 26.3 recipe schema."""
    new = {"type": old["type"]}
    for key in ("category", "group", "cookingtime", "experience"):
        if key in old:
            new[key] = old[key]
    if "ingredients" in old:
        new["ingredients"] = [ingredient(i) for i in old["ingredients"]]
    if "ingredient" in old:
        new["ingredient"] = ingredient(old["ingredient"])
    if "pattern" in old:
        new["pattern"] = old["pattern"]
    if "key" in old:
        new["key"] = {k: ingredient(v) for k, v in old["key"].items()}
    result = old["result"]
    new["result"] = {"id": result["id"]}
    if result.get("count", 1) != 1:
        new["result"]["count"] = result["count"]
    return new


def collect_models(assets: Path, blockstates: list[str], item_models: list[str]):
    """Every model the 36 blocks reach, and the textures they name."""
    queue = list(blockstates) + list(item_models)
    models: dict[str, dict] = {}
    textures: set[str] = set()
    while queue:
        model_id = queue.pop()
        if not model_id.startswith(f"{NAMESPACE}:"):
            continue
        path = model_id.split(":", 1)[1]
        if path in models:
            continue
        source = assets / "models" / f"{path}.json"
        if not source.exists():
            raise SystemExit(f"missing model {model_id}")
        model = json.loads(source.read_text())
        # `render_type` is a NeoForge field; 26.3 decides transparency from
        # the sprite, as vanilla's own ladder model does.
        model.pop("render_type", None)
        models[path] = model
        parent = model.get("parent")
        if isinstance(parent, str):
            queue.append(parent if ":" in parent else f"minecraft:{parent}")
        for value in model.get("textures", {}).values():
            if isinstance(value, str) and value.startswith(f"{NAMESPACE}:"):
                textures.add(value.split(":", 1)[1])
    return models, textures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "_shared/upstream/bellsandwhistles",
    )
    parser.add_argument(
        "--out", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    upstream = args.upstream.resolve()
    out = args.out.resolve()
    source = upstream / "src/main/resources"
    if not (upstream / "gradle.properties").exists():
        raise SystemExit(f"no upstream checkout at {upstream}")

    assets = out / f"assets/{NAMESPACE}"
    data = out / "data"
    if (out / "assets").exists():
        shutil.rmtree(out / "assets")
    if (out / "data").exists():
        shutil.rmtree(out / "data")

    ids = [block[0] for block in BLOCKS]

    # Blockstates and item models: upstream files, unchanged.
    blockstate_models = []
    for block_id in ids:
        state = json.loads(
            (source / f"assets/{NAMESPACE}/blockstates/{block_id}.json").read_text()
        )
        write(assets / f"blockstates/{block_id}.json", state)
        for variant in state["variants"].values():
            blockstate_models.append(variant["model"])
        item_model = json.loads(
            (source / f"assets/{NAMESPACE}/models/item/{block_id}.json").read_text()
        )
        write(assets / f"models/item/{block_id}.json", item_model)
        # 26.3 item model definitions (1.21.1 stopped at models/item).
        write(
            assets / f"items/{block_id}.json",
            {
                "model": {
                    "type": "minecraft:model",
                    "model": f"{NAMESPACE}:item/{block_id}",
                }
            },
        )

    item_models = [f"{NAMESPACE}:item/{block_id}" for block_id in ids]
    models, textures = collect_models(
        source / f"assets/{NAMESPACE}", blockstate_models, item_models
    )
    for path, model in models.items():
        write(assets / f"models/{path}.json", model)
    for texture in sorted(textures):
        target = assets / f"textures/{texture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            source / f"assets/{NAMESPACE}/textures/{texture}.png",
            target,
        )

    # Lang: upstream's English file and the hand-written translations.
    for lang in (source / f"assets/{NAMESPACE}/lang").glob("*.json"):
        write(assets / f"lang/{lang.name}", json.loads(lang.read_text()))

    # Block declarations.
    for block_id, template, _, _, _ in BLOCKS:
        spec = dict(TEMPLATES[template])
        declaration = {
            "template": spec["template"],
            "properties": spec["properties"],
            "item": True,
        }
        if "default_state" in spec:
            declaration["default_state"] = spec["default_state"]
        if template == "platform":
            declaration["shapes"] = {
                "property": "facing",
                "values": platform_shapes(),
            }
        if template == END_ROD:
            declaration["shapes"] = {
                "property": "facing",
                "values": PANEL_SHAPES,
            }
        write(data / f"{NAMESPACE}/horizon/block/{block_id}.json", declaration)

        # Loot: drop self, survive explosions. Upstream copies vanilla's
        # acacia_log random sequence by mistake; the port names its own.
        write(
            data / f"{NAMESPACE}/loot_table/blocks/{block_id}.json",
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "condition": {"type": "minecraft:survives_explosion"},
                        "entries": [
                            {"type": "minecraft:item", "name": f"{NAMESPACE}:{block_id}"}
                        ],
                        "rolls": 1,
                    }
                ],
                "random_sequence": f"{NAMESPACE}:blocks/{block_id}",
            },
        )

    # Recipes: the upstream datagen, flattened and converted to 26.3.
    for relative, stem in RECIPE_FILES.items():
        old = json.loads((source / f"data/{NAMESPACE}/recipe/{relative}").read_text())
        new = upgrade_recipe(old)
        new.update(RECIPE_PATCHES.get(stem, {}))
        write(data / f"{NAMESPACE}/recipe/{stem}.json", new)

    # Tags: the six climbable metal rails and the 27 stone/metal blocks.
    climbable = [f"{NAMESPACE}:{b[0]}" for b in BLOCKS if b[2]]
    pickaxe = [f"{NAMESPACE}:{b[0]}" for b in BLOCKS if b[3]]
    write(data / "minecraft/tags/block/climbable.json", {"values": climbable})
    write(data / "minecraft/tags/block/mineable/pickaxe.json", {"values": pickaxe})

    # One creative tab for the content (Horizon has no vanilla-tab insertion).
    write(
        data / f"{NAMESPACE}/horizon/creative_tab/{NAMESPACE}.json",
        {
            "title": "Bells & Whistles",
            "icon": f"{NAMESPACE}:metal_pilot",
            "items": [f"{NAMESPACE}:{block_id}" for block_id in ids],
        },
    )

    # The manifest is NOT generated: since the migration to the SDK format (mod API 0.2) the
    # port root carries one `horizon-mod.toml` with `[native]` pins, hand-maintained in the port
    # (the generated content-only manifest would strip the native half).
    print(f"wrote {out} (assets/, data/; horizon-mod.toml is hand-maintained)")


if __name__ == "__main__":
    main()
