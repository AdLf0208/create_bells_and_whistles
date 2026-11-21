#!/usr/bin/env python3
"""Validate the content tree against the prepared 26.3 tables.

Checks, without starting the game:
- every state of every template is matched by a variant in the mod's
  blockstate (the same expansion the game's loader does), every variant names
  only properties the template has, every `default_state` is a template state,
  and every `shapes` selector covers the property's values;
- every model and texture the blockstates, item definitions and their parents
  name resolves (mod or vanilla), and the vanilla built-in models are skipped;
- every loot-table item, recipe ingredient and recipe result names a known
  vanilla item or one of the mod's own blocks/items.

Usage:
    python3 tools/validate_content.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = pathlib.Path("/home/adlf/Desktop/horizon/.local/horizon-client/26.3")
NS = "bellsandwhistles"

facts = json.loads((RES / "facts.json").read_text())
states_by_block = collections.defaultdict(list)
for record in facts["states"]:
    name, props = record[0], record[4]
    states_by_block[name].append(props.get("properties", {}))

declarations = {}
for path in (ROOT / "data" / NS / "horizon/block").glob("*.json"):
    declarations[path.stem] = json.loads(path.read_text())

items = json.loads((RES / "items.json").read_text())
mod_ids = {f"{NS}:{path.stem}" for path in (ROOT / "data" / NS / "horizon/block").glob("*.json")}
item_ids = set(items) | mod_ids

errors = []


def variant_matches(variant_key, props):
    for part in variant_key.split(","):
        if not part:
            continue
        key, value = part.split("=")
        if props.get(key) != value:
            return False
    return True


for block, declaration in sorted(declarations.items()):
    template = declaration["template"]
    template_states = states_by_block[template]
    blockstate = json.loads((ROOT / f"assets/{NS}/blockstates/{block}.json").read_text())
    variants = blockstate.get("variants")
    if variants is None:
        errors.append(f"{block}: multipart blockstate not supported by this check")
        continue
    keys = list(variants)
    for props in template_states:
        if not any(variant_matches(key, props) for key in keys):
            errors.append(f"{block}: no variant binds {props}")
            break
    template_props = set().union(*[set(p) for p in template_states]) if template_states else set()
    for key in keys:
        for part in key.split(","):
            if not part:
                continue
            name = part.split("=")[0]
            if name not in template_props:
                errors.append(f"{block}: variant {key!r} names unknown property {name}")
                break
    default_id = facts["defaults"][template]
    default = dict(facts["states"][default_id][4].get("properties", {}))
    default.update(declaration.get("default_state", {}))
    if not any(props == default for props in template_states):
        errors.append(f"{block}: default_state {declaration.get('default_state')} is not a template state")
    if "shapes" in declaration:
        prop = declaration["shapes"]["property"]
        want = {props.get(prop) for props in template_states}
        got = set(declaration["shapes"]["values"])
        if want != got:
            errors.append(f"{block}: shapes values {sorted(got)} != {sorted(want)}")


def model_path(model_id):
    namespace, path = model_id.split(":") if ":" in model_id else ("minecraft", model_id)
    if namespace == NS:
        return ROOT / "assets" / NS / "models" / f"{path}.json"
    return RES / "assets" / namespace / "models" / f"{path}.json"


def texture_exists(texture_id):
    namespace, path = texture_id.split(":") if ":" in texture_id else ("minecraft", texture_id)
    if namespace == NS:
        return (ROOT / "assets" / NS / "textures" / f"{path}.png").exists()
    return (RES / "assets" / namespace / "textures" / f"{path}.png").exists()


seen = set()


def walk(model_id):
    if model_id in seen:
        return
    seen.add(model_id)
    path = model_path(model_id)
    if not path.exists():
        errors.append(f"missing model {model_id} ({path})")
        return
    model = json.loads(path.read_text())
    parent = model.get("parent")
    if parent:
        parent = parent if ":" in parent else f"minecraft:{parent}"
        if not parent.startswith("minecraft:builtin/"):
            walk(parent)
    for value in model.get("textures", {}).values():
        if isinstance(value, str) and not value.startswith("#"):
            if not texture_exists(value):
                errors.append(f"model {model_id}: texture {value} missing")
        elif isinstance(value, dict) and "sprite" in value:
            if not texture_exists(value["sprite"]):
                errors.append(f"model {model_id}: sprite {value['sprite']} missing")


for block in declarations:
    blockstate = json.loads((ROOT / f"assets/{NS}/blockstates/{block}.json").read_text())
    for variant in blockstate.get("variants", {}).values():
        walk(variant["model"])
    item = json.loads((ROOT / f"assets/{NS}/items/{block}.json").read_text())
    walk(item["model"]["model"])

for path in (ROOT / "data" / NS / "loot_table/blocks").glob("*.json"):
    table = json.loads(path.read_text())
    for pool in table["pools"]:
        for entry in pool["entries"]:
            if entry["type"] == "minecraft:item" and entry["name"] not in item_ids:
                errors.append(f"loot {path.stem}: item {entry['name']} unknown")


def ingredient_ok(ingredient):
    if isinstance(ingredient, list):
        return all(ingredient_ok(value) for value in ingredient)
    if ingredient.startswith("#"):
        return True
    return ingredient in item_ids


for path in (ROOT / "data" / NS / "recipe").glob("*.json"):
    recipe = json.loads(path.read_text())
    bad = []
    for key in ("ingredients",):
        if key in recipe:
            bad.extend(value for value in recipe[key] if not ingredient_ok(value))
    if "ingredient" in recipe and not ingredient_ok(recipe["ingredient"]):
        bad.append(recipe["ingredient"])
    for value in recipe.get("key", {}).values():
        if not ingredient_ok(value):
            bad.append(value)
    if bad:
        errors.append(f"recipe {path.stem}: unknown ingredients {bad}")
    if recipe["result"]["id"] not in item_ids:
        errors.append(f"recipe {path.stem}: unknown result {recipe['result']['id']}")


# ---------------------------------------------------------------- recipe rules
#
# The same rules the runtime tests apply, plus the one the tests cannot see: a
# grid that a *vanilla* 26.3 recipe also fills is ambiguous, because the recipe
# manager picks one of the matches and the port cannot say which. Vanilla's
# shaped match is tried at every offset and in both mirror orientations and
# every cell outside the pattern must be empty.

vanilla_recipes = {}
for path in (RES / "data/minecraft/recipe").glob("*.json"):
    try:
        record = json.loads(path.read_text())
    except json.JSONDecodeError:
        continue
    if record.get("type") in ("minecraft:crafting_shaped", "minecraft:crafting_shapeless"):
        vanilla_recipes[path.stem] = record

vanilla_tags = {}
for path in (RES / "data/minecraft/tags/item").rglob("*.json"):
    record = json.loads(path.read_text())
    vanilla_tags[f"minecraft:{path.relative_to(RES / 'data/minecraft/tags/item').with_suffix('').as_posix()}"] = record.get("values", [])


def tag_members(tag, seen=()):
    """The item ids a vanilla item tag resolves to."""
    if tag in seen:
        return set()
    members = set()
    for value in vanilla_tags.get(tag, []):
        if isinstance(value, dict):
            value = value.get("id", "")
        if value.startswith("#"):
            members |= tag_members(value[1:], seen + (tag,))
        else:
            members.add(value)
    return members


def accepts(allowed, cell):
    if allowed is None:
        return cell is None
    if cell is None:
        return False
    if isinstance(allowed, list):
        return any(accepts(value, cell) for value in allowed)
    if allowed.startswith("#"):
        return cell in tag_members(allowed[1:])
    return cell == allowed


def grid_of(recipe):
    """The 3x3 grid one craft of a shaped recipe fills."""
    grid = [[None] * 3 for _ in range(3)]
    for y, row in enumerate(recipe["pattern"]):
        for x, symbol in enumerate(row):
            if symbol != " ":
                grid[y][x] = recipe["key"][symbol]
    return grid


def shaped_matches(recipe, grid):
    pattern = recipe["pattern"]
    height, width = len(pattern), len(pattern[0])
    for dy in range(4 - height):
        for dx in range(4 - width):
            for mirror in (False, True):
                ok = True
                for gy in range(3):
                    for gx in range(3):
                        px, py = gx - dx, gy - dy
                        if 0 <= px < width and 0 <= py < height:
                            symbol = pattern[py][width - 1 - px if mirror else px]
                            allowed = None if symbol == " " else recipe["key"][symbol]
                        else:
                            allowed = None
                        if not accepts(allowed, grid[gy][gx]):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    return True
    return False


def entities(recipe):
    """A shapeless recipe's or a stonecutter's ingredients, as a sorted multiset."""
    if recipe.get("type") == "minecraft:stonecutting":
        return [str(recipe["ingredient"])]
    return sorted(str(value) for value in recipe.get("ingredients", []))


recipes = {}
for path in (ROOT / "data" / NS / "recipe").glob("*.json"):
    recipes[path.stem] = json.loads(path.read_text())

table = {stem: r for stem, r in recipes.items() if r["type"] != "minecraft:stonecutting"}
for (stem, first), (other, second) in (
    (a, b)
    for index, a in enumerate(sorted(table.items()))
    for b in sorted(table.items())[index + 1 :]
):
    if first["result"]["id"] == second["result"]["id"] and first["result"].get("count", 1) == second["result"].get("count", 1):
        continue
    clash = False
    if "pattern" in first and "pattern" in second:
        clash = shaped_matches(second, grid_of(first)) or shaped_matches(first, grid_of(second))
    elif "ingredients" in first and "ingredients" in second:
        clash = entities(first) == entities(second)
    if clash:
        errors.append(
            f"recipes {stem} and {other} fill the same grid: "
            f"{first['result']['id']} and {second['result']['id']} cannot both be crafted"
        )

for stem, recipe in sorted(table.items()):
    for vanilla, record in sorted(vanilla_recipes.items()):
        if record["result"]["id"].startswith(f"{NS}:"):
            continue
        if "pattern" in recipe and "pattern" in record:
            clash = shaped_matches(record, grid_of(recipe))
        elif "ingredients" in recipe and "ingredients" in record:
            clash = sorted(str(value) for value in record["ingredients"]) == entities(recipe)
        else:
            continue
        if clash:
            errors.append(
                f"recipe {stem} fills the grid of vanilla {vanilla} "
                f"({record['result']['id']}), so the craft is ambiguous"
            )

for block in declarations:
    if f"{NS}:{block}" not in item_ids:
        errors.append(f"block {block} has no item")

print(f"blocks={len(declarations)} models={len(seen)}")
if errors:
    for error in errors:
        print(f"ERROR: {error}")
    sys.exit(1)
print("OK: every template state binds, every model/texture resolves, every loot/recipe item exists")
