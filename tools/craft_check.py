#!/usr/bin/env python3
"""Craft the Bells & Whistles recipes in a real crafting table.

Called by tools/e2e.sh with the open game's control socket. Uses the harness's
crafting grid (`ctl screen`: slots 100-108 row-major, result 200), gives the
ingredients, and asserts each carried recipe and an empty control. The table is
replaced before every case, so a failed/untaken result cannot leak into the
next grid. `MODE=vanilla` runs the same grids with the vanilla stand-ins and
asserts an empty result (the differential: the recipes are the mod's).
"""

import json
import subprocess
import sys

GRID = {
    (0, 0): 100, (1, 0): 101, (2, 0): 102,
    (0, 1): 103, (1, 1): 104, (2, 1): 105,
    (0, 2): 106, (1, 2): 107, (2, 2): 108,
}


def shaped(rows, key):
    """Slots per item for a shaped pattern."""
    targets = {}
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == " ":
                continue
            targets.setdefault(key[char], []).append(GRID[(x, y)])
    return targets


def main():
    sock, ctl, x, y, z, mode = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]

    def run(*args):
        out = subprocess.run([ctl, "--socket", sock, *args], text=True, capture_output=True)
        try:
            return json.loads(out.stdout)
        except json.JSONDecodeError:
            raise SystemExit(f"ctl {' '.join(args)}: {out.stdout}{out.stderr}")

    def wait(ticks=4):
        run("wait", str(ticks))

    def slots():
        screen = run("screen")
        if "slots" not in screen:
            raise SystemExit(f"no menu is open: {screen}")
        return screen["slots"]

    def find(item):
        for slot in slots():
            if slot.get("item") == item:
                return slot["slot"]
        raise SystemExit(f"missing ingredient {item} in the inventory")

    def result():
        stack = [s for s in slots() if s["slot"] == 200]
        if not stack or not stack[0].get("item"):
            return None
        return stack[0]

    def place(item, targets):
        slot = find(item)
        run("click-slot", str(slot))
        wait(1)
        for target in targets:
            run("click-slot", str(target), "right")
            wait(1)
        run("click-slot", str(slot))
        wait(2)

    def setup(items):
        try:
            run("close")
        except SystemExit:
            pass
        wait(5)
        run("setblock", x, y, z, "minecraft:air")
        run("setblock", x, y, z, "minecraft:crafting_table")
        wait(2)
        run("command", f"tp @s {float(x) - 0.5} {y} {float(z) + 0.5}")
        wait(3)
        run("command", "clear @s")
        for item, count in items:
            run("give", item, str(count))
        wait(3)
        run("interact", x, y, z)
        wait(5)

    failures = []

    def case(label, items, targets, want_item, want_count):
        setup(items)
        for item, target in targets.items():
            place(item, target)
        got = result()
        print(f"{label} ->", json.dumps(got))
        if not got or got.get("item") != want_item or got.get("count") != want_count:
            failures.append(f"{label}: expected {want_count} {want_item}, got {got}")

    def empty(label, items, targets):
        setup(items)
        for item, target in targets.items():
            place(item, target)
        got = result()
        print(f"{label} ->", json.dumps(got))
        if got is not None:
            failures.append(f"{label}: control crafted {got['item']}")

    if mode == "vanilla":
        # The same grid shapes with materials the mod's recipes do not name:
        # nothing crafts, so the default run's results are the mod's recipes.
        empty(
            "vanilla 7 stone (bogie pattern)",
            [("minecraft:stone", 7)],
            {"minecraft:stone": [100, 102, 103, 105, 106, 107, 108]},
        )
        empty(
            "vanilla 2 iron ingots + 4 iron nuggets (grab-rail pattern)",
            [("minecraft:iron_ingot", 2), ("minecraft:iron_nugget", 4)],
            {
                "minecraft:iron_ingot": [103, 105],
                "minecraft:iron_nugget": [100, 102, 106, 108],
            },
        )
        empty(
            "vanilla 3 dirt (metro panel pattern)",
            [("minecraft:dirt", 3)],
            {"minecraft:dirt": [100, 101, 102]},
        )
        empty(
            "vanilla 2 sticks (station platform control)",
            [("minecraft:stick", 2)],
            {"minecraft:stick": [100, 101]},
        )
        empty(
            "vanilla 4 stone + 2 stone stairs (pilot pattern)",
            [("minecraft:stone", 4), ("minecraft:stone_stairs", 2)],
            {"minecraft:stone": [103, 105, 106, 108], "minecraft:stone_stairs": [101, 107]},
        )
    else:
        case(
            "7 andesite -> 6 andesite bogie steps",
            [("minecraft:andesite", 7)],
            {"minecraft:andesite": shaped(["# #", "# #", "###"], {"#": "minecraft:andesite"})["minecraft:andesite"]},
            "bellsandwhistles:andesite_bogie_steps",
            6,
        )
        case(
            "2 copper ingots + 4 copper nuggets -> 8 brass grab rails",
            [("minecraft:copper_ingot", 2), ("minecraft:copper_nugget", 4)],
            {
                "minecraft:copper_ingot": shaped(["I I", "# #", "I I"], {"I": "minecraft:copper_nugget", "#": "minecraft:copper_ingot"})["minecraft:copper_ingot"],
                "minecraft:copper_nugget": shaped(["I I", "# #", "I I"], {"I": "minecraft:copper_nugget", "#": "minecraft:copper_ingot"})["minecraft:copper_nugget"],
            },
            "bellsandwhistles:brass_grab_rails",
            8,
        )
        case(
            "3 iron nuggets + torch -> 2 headlights",
            [("minecraft:iron_nugget", 3), ("minecraft:torch", 1)],
            {
                "minecraft:iron_nugget": shaped(["# ", "#I", "# "], {"#": "minecraft:iron_nugget", "I": "minecraft:torch"})["minecraft:iron_nugget"],
                "minecraft:torch": [104],
            },
            "bellsandwhistles:headlight",
            2,
        )
        case(
            "3 metro casing -> 16 metro panels",
            [("bellsandwhistles:metro_casing", 3)],
            {"bellsandwhistles:metro_casing": shaped(["###"], {"#": "bellsandwhistles:metro_casing"})["bellsandwhistles:metro_casing"]},
            "bellsandwhistles:metro_panel",
            16,
        )
        case(
            "smooth stone slab + smooth stone -> 2 station platforms",
            [("minecraft:smooth_stone_slab", 1), ("minecraft:smooth_stone", 1)],
            {"minecraft:smooth_stone_slab": [100], "minecraft:smooth_stone": [101]},
            "bellsandwhistles:station_platform",
            2,
        )
        case(
            "4 polished tuff + 2 polished tuff stairs -> polished tuff pilot",
            [("minecraft:polished_tuff", 4), ("minecraft:polished_tuff_stairs", 2)],
            {
                "minecraft:polished_tuff": shaped([" I ", "# #", "#I#"], {"#": "minecraft:polished_tuff", "I": "minecraft:polished_tuff_stairs"})["minecraft:polished_tuff"],
                "minecraft:polished_tuff_stairs": [101, 107],
            },
            "bellsandwhistles:polished_tuff_pilot",
            1,
        )
        empty(
            "7 stone (bogie pattern control)",
            [("minecraft:stone", 7)],
            {"minecraft:stone": shaped(["# #", "# #", "###"], {"#": "minecraft:stone"})["minecraft:stone"]},
        )
        empty(
            "2 stone + 4 sticks (grab-rail pattern control)",
            [("minecraft:stone", 2), ("minecraft:stick", 4)],
            {
                "minecraft:stone": [103, 105],
                "minecraft:stick": [100, 102, 106, 108],
            },
        )
        empty(
            "3 dirt (metro panel control)",
            [("minecraft:dirt", 3)],
            {"minecraft:dirt": [100, 101, 102]},
        )
        empty(
            "2 sticks (station platform control)",
            [("minecraft:stick", 2)],
            {"minecraft:stick": [100, 101]},
        )

    run("close")
    wait(3)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        raise SystemExit(1)
    print(f"recipe PASS ({mode})")


if __name__ == "__main__":
    main()
