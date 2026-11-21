#!/usr/bin/env python3
"""Craft every carried Bells & Whistles recipe in a real game.

The parity rule (AGENTS.md, 2026-11-20): a carried recipe that is never crafted
is dead data. This script drives all of them through `horizon-ctl`:

- every crafting-table recipe in a crafting table (grid slots 100-108, result
  200): the ingredients are given, placed one by one, the result's id and count
  are read back, and taking it must leave the grid empty (the ingredients were
  consumed) and add exactly `count` of the output to the inventory;
- every stonecutting recipe in a stonecutter (station slot 600 = input, 650 =
  result): the control socket's `menu` reports the offers for the input, the
  recipe's cell is clicked with `click-gui`, and the selected result must be the
  declared id and count; taking it consumes the input. A second, different cell
  is selected first to prove the selection is what decides the result;
- `--mode absent` runs the same ingredient grids against a game built WITHOUT
  the package: every table grid must craft nothing and no stonecutter may offer
  a `bellsandwhistles:` recipe. That is the differential that makes the mod leg
  mean something.

Usage:
    python3 tools/recipe_check.py --socket SOCK --ctl CTL --mode mod \\
        --table 6 80 2 --stonecutter 8 80 2 [--data DIR]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NS = "bellsandwhistles"
GRID = {
    (0, 0): 100, (1, 0): 101, (2, 0): 102,
    (0, 1): 103, (1, 1): 104, (2, 1): 105,
    (0, 2): 106, (1, 2): 107, (2, 2): 108,
}
RESULT_SLOT = 200
STATION_INPUT = 600
STATION_RESULT = 650


class Client:
    def __init__(self, ctl: str, socket: str):
        self.ctl = ctl
        self.socket = socket

    def run(self, *args: str):
        out = subprocess.run(
            [self.ctl, "--socket", self.socket, *args], text=True, capture_output=True
        )
        try:
            return json.loads(out.stdout)
        except json.JSONDecodeError:
            raise SystemExit(f"ctl {' '.join(args)}: {out.stdout}{out.stderr}")

    def wait(self, ticks: int = 1) -> None:
        self.run("wait", str(ticks))

    def close(self) -> None:
        try:
            self.run("close")
        except SystemExit:
            pass

    def slots(self) -> list[dict]:
        screen = self.run("screen")
        if "slots" not in screen:
            raise SystemExit(f"no menu is open: {screen}")
        return screen["slots"]

    def stack(self, slot: int) -> dict | None:
        for entry in self.slots():
            if entry["slot"] == slot and entry.get("item"):
                return entry
        return None

    def counts(self) -> dict[str, int]:
        return self.run("inventory").get("counts", {})

    def grid_is_empty(self) -> bool:
        return all(self.stack(slot) is None for slot in GRID.values())

    def empty_inventory_slot(self) -> int:
        for entry in self.slots():
            slot = entry["slot"]
            if slot <= 35 and not entry.get("item"):
                return slot
        raise SystemExit("no empty inventory slot to put a craft into")


def recipes(data: pathlib.Path) -> dict[str, dict]:
    out = {}
    for path in sorted((data / NS / "recipe").glob("*.json")):
        record = json.loads(path.read_text())
        out[path.stem] = record
    return out


def placements(recipe: dict) -> dict[str, list[int]]:
    """Item id -> the grid slots it fills, for one craft of a shaped recipe."""
    targets: dict[str, list[int]] = {}
    for y, row in enumerate(recipe["pattern"]):
        for x, symbol in enumerate(row):
            if symbol != " ":
                item = recipe["key"][symbol]
                targets.setdefault(item, []).append(GRID[(x, y)])
    return targets


def ingredients(recipe: dict) -> list[str]:
    return list(recipe["ingredients"])


def give(client: Client, item: str, count: int) -> None:
    client.run("give", item, str(count))
    client.wait(1)


def place(client: Client, item: str, targets: list[int]) -> None:
    source = None
    for entry in client.slots():
        if entry.get("item") == item and entry["slot"] <= 35:
            source = entry["slot"]
            break
    if source is None:
        raise SystemExit(f"missing ingredient {item} in the inventory")
    client.run("click-slot", str(source))
    client.wait(1)
    for target in targets:
        client.run("click-slot", str(target), "right")
        client.wait(1)
    client.run("click-slot", str(source))
    client.wait(1)


def table_case(client: Client, table: list[int], stem: str, recipe: dict, mode: str) -> str:
    """Craft one table recipe; returns a PASS line or raises SystemExit."""
    client.close()
    client.wait(2)
    x, y, z = table
    client.run("setblock", str(x), str(y), str(z), "minecraft:air")
    client.run("setblock", str(x), str(y), str(z), "minecraft:crafting_table")
    client.wait(2)
    client.run("command", f"tp @s {x - 0.5} {y} {z + 0.5}")
    client.wait(2)
    client.run("command", "clear @s")
    client.wait(1)

    shaped = "pattern" in recipe
    # What one craft needs, and where it goes: item id -> count, and for a
    # shaped recipe the grid slots each item fills.
    need: dict[str, int] = {}
    targets: dict[str, list[int]] = {}
    if shaped:
        for item, slots in placements(recipe).items():
            need[item] = len(slots)
            targets[item] = slots
    else:
        for item in ingredients(recipe):
            need[item] = need.get(item, 0) + 1
    for item, count in need.items():
        if item.startswith(f"{NS}:"):
            if mode == "absent":
                return f"SKIP {stem}: needs {item}, which the package provides"
        give(client, item, count)
    client.wait(2)
    client.run("interact", str(x), str(y), str(z))
    client.wait(2)

    if shaped:
        for item, slots in targets.items():
            place(client, item, slots)
    else:
        free = sorted(GRID.values())
        for item, count in need.items():
            place(client, item, [free.pop(0) for _ in range(count)])

    got = client.stack(RESULT_SLOT)
    if mode == "absent":
        if got:
            raise SystemExit(
                f"FAIL {stem}: the game without the package crafted {got['item']} "
                f"x{got['count']}, so the differential proves nothing"
            )
        return f"PASS {stem}: without the package the grid crafts nothing"

    want_id = recipe["result"]["id"]
    want_count = recipe["result"].get("count", 1)
    if not got:
        raise SystemExit(f"FAIL {stem}: the grid crafted nothing, expected {want_count} {want_id}")
    if got["item"] != want_id or got["count"] != want_count:
        raise SystemExit(
            f"FAIL {stem}: crafted {got['count']} {got['item']}, "
            f"expected {want_count} {want_id}"
        )

    before = client.counts()
    client.run("click-slot", str(RESULT_SLOT))
    client.wait(1)
    client.run("click-slot", str(client.empty_inventory_slot()))
    client.wait(1)
    after = client.counts()
    if not client.grid_is_empty():
        raise SystemExit(f"FAIL {stem}: the grid still holds items, so they were not consumed")
    if after.get(want_id, 0) != before.get(want_id, 0) + want_count:
        raise SystemExit(
            f"FAIL {stem}: the inventory holds {after.get(want_id, 0)} {want_id} "
            f"after the craft, expected {before.get(want_id, 0) + want_count}"
        )
    for item in need:
        if after.get(item, 0) != 0:
            raise SystemExit(
                f"FAIL {stem}: {after[item]} {item} are left after the craft, so the "
                "ingredients were not consumed"
            )
    foreign = [
        item
        for item, count in after.items()
        if item.startswith(f"{NS}:") and item != want_id and count
    ]
    if foreign:
        raise SystemExit(f"FAIL {stem}: the craft also produced {foreign}")
    return (
        f"PASS {stem}: {want_count} {want_id}, the grid emptied and the "
        f"{sum(need.values())} ingredients were consumed"
    )


def stonecutting_case(
    client: Client, cutter: list[int], stem: str, recipe: dict, mode: str
) -> str:
    """Drive one stonecutting recipe through a real stonecutter screen.

    The station must be opened by right-clicking the block (`ctl interact`) with
    the player beside it and looking at it: `ctl use` sets the station but leaves
    the screen in `playing`, and then every slot click silently misses (probes in
    `evidence/bellsandwhistles/`: `use` → the input stays carried, `interact` →
    the input lands in slot 600 and the offers are listed).
    """
    client.close()
    client.wait(2)
    x, y, z = cutter
    client.run("setblock", str(x), str(y - 1), str(z), "minecraft:stone")
    client.run("setblock", str(x), str(y), str(z), "minecraft:stonecutter")
    client.wait(2)
    client.run("command", "clear @s")
    client.wait(1)
    input_item = recipe["ingredient"]
    if input_item.startswith(f"{NS}:"):
        if mode == "absent":
            return f"SKIP {stem}: needs {input_item}, which the package provides"
    give(client, input_item, 1)
    client.wait(2)
    client.run("command", f"tp @s {x - 0.5} {y} {z + 0.5}")
    client.wait(2)
    client.run("look-at-block", str(x), str(y), str(z))
    client.wait(1)
    client.run("interact", str(x), str(y), str(z))
    client.wait(3)
    if (client.run("menu").get("station")) != "Stonecutter":
        raise SystemExit(f"FAIL {stem}: the stonecutter did not open")

    for entry in client.slots():
        if entry.get("item") == input_item and entry["slot"] <= 35:
            client.run("click-slot", str(entry["slot"]))
            break
    else:
        raise SystemExit(f"FAIL {stem}: {input_item} is not in the inventory")
    client.wait(1)
    client.run("click-slot", str(STATION_INPUT))
    client.wait(2)
    if client.stack(STATION_INPUT) is None:
        raise SystemExit(f"FAIL {stem}: {input_item} did not go into the stonecutter's input")

    menu = client.run("menu")
    info = menu.get("info") or {}
    offers = info.get("recipes") or []
    if mode == "absent":
        if any(offer.startswith(f"{NS}:") for offer in offers):
            raise SystemExit(
                f"FAIL {stem}: the game without the package offers {offers}, so the "
                "differential proves nothing"
            )
        return f"PASS {stem}: without the package the stonecutter offers no mod recipe"

    offered = f"{NS}:{stem}"
    if offered not in offers:
        raise SystemExit(f"FAIL {stem}: the stonecutter offers {offers}, not {offered}")
    if len(offers) > 12:
        raise SystemExit(
            f"FAIL {stem}: {len(offers)} offers do not fit the 12 shown cells; "
            "this check does not scroll"
        )
    index = offers.index(offered)
    want_count = recipe["result"].get("count", 1)
    want_result = f"{recipe['result']['id']} x{want_count}"

    def cell(position: int) -> tuple[float, float]:
        """The GUI position of recipe cell `position` (the 4x3 grid)."""
        return (52 + 16 * (position % 4) + 8, 14 + 18 * (position // 4) + 9)

    def select(position: int) -> dict:
        client.run("click-gui", str(cell(position)[0]), str(cell(position)[1]))
        client.wait(2)
        return client.run("menu").get("info") or {}

    # The differential: another cell selects another result, so the cell — not
    # the input alone — decides the craft.
    other = (index + 1) % len(offers)
    other_info = select(other)
    if other_info.get("result") == want_result:
        raise SystemExit(
            f"FAIL {stem}: cell {other} also reports {want_result}, so selecting a "
            "recipe does not decide the result"
        )
    if other_info.get("selected") != other:
        raise SystemExit(
            f"FAIL {stem}: cell {other} selected {other_info.get('selected')}, "
            f"expected {other}"
        )

    info = select(index)
    if info.get("selected") != index:
        raise SystemExit(f"FAIL {stem}: selected {info.get('selected')}, expected {index}")
    if info.get("result") != want_result:
        raise SystemExit(
            f"FAIL {stem}: the selected result is {info.get('result')!r}, expected {want_result!r}"
        )

    before = client.counts()
    client.run("click-slot", str(STATION_RESULT))
    client.wait(1)
    client.run("click-slot", str(client.empty_inventory_slot()))
    client.wait(1)
    after = client.counts()
    if after.get(recipe["result"]["id"], 0) != before.get(recipe["result"]["id"], 0) + want_count:
        raise SystemExit(
            f"FAIL {stem}: the inventory holds {after.get(recipe['result']['id'], 0)} "
            f"{recipe['result']['id']}, expected "
            f"{before.get(recipe['result']['id'], 0) + want_count}"
        )
    if client.stack(STATION_INPUT) is not None:
        raise SystemExit(f"FAIL {stem}: the input was not consumed")
    return (
        f"PASS {stem}: {want_result} from one {input_item} (cell {other} was "
        f"{other_info.get('result')}), the input was consumed"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True)
    parser.add_argument("--ctl", required=True)
    parser.add_argument("--mode", choices=("mod", "absent"), default="mod")
    parser.add_argument("--table", nargs=3, type=int, metavar=("X", "Y", "Z"), required=True)
    parser.add_argument("--stonecutter", nargs=3, type=int, metavar=("X", "Y", "Z"), required=True)
    parser.add_argument("--data", default=str(ROOT / "data"))
    args = parser.parse_args()

    client = Client(args.ctl, args.socket)
    carried = recipes(pathlib.Path(args.data))
    table = {stem: r for stem, r in carried.items() if r["type"] != "minecraft:stonecutting"}
    cutting = {stem: r for stem, r in carried.items() if r["type"] == "minecraft:stonecutting"}
    print(f"{len(carried)} carried recipes: {len(table)} at a crafting table, {len(cutting)} at a stonecutter")

    failures = []
    for stem, recipe in sorted(table.items()):
        try:
            print(table_case(client, args.table, stem, recipe, args.mode), flush=True)
        except SystemExit as failure:
            print(str(failure), file=sys.stderr, flush=True)
            failures.append(stem)
    for stem, recipe in sorted(cutting.items()):
        try:
            print(stonecutting_case(client, args.stonecutter, stem, recipe, args.mode), flush=True)
        except SystemExit as failure:
            print(str(failure), file=sys.stderr, flush=True)
            failures.append(stem)

    client.close()
    client.wait(2)
    if failures:
        print(f"FAIL: {len(failures)} recipe(s) failed: {failures}", file=sys.stderr)
        return 1
    print(f"recipe PASS ({args.mode}): every carried recipe crafts its declared output and consumes its ingredients")
    return 0


if __name__ == "__main__":
    sys.exit(main())
