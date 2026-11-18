#!/usr/bin/env python3
"""Check the declared state space and the default placement of the 36 blocks.

Called by tools/e2e.sh with the open game's control socket.

1. Registry: `setblock` every state of every block's template and assert the
   command accepts it. That is the state space the content declares
   (9 x 8 + 3 x 64 + 24 + 19 x 4 + 2 x 6 + 2 x 1 = 378 states).
2. World: place each block's default state in a valid support context, wait for
   the client to see it and read it back with every default property. The
   blockstate binding itself is checked by tools/e2e.sh against the game log
   (no "blockstate definition of bellsandwhistles" error).

`MODE=vanilla` runs the same two checks on the six vanilla template blocks
(107 states), the differential: the same state space without the mod content.
Exits 1 with the first mismatch.
"""

import json
import subprocess
import sys

# (block id, template key), in the creative tab's order.
BLOCKS = [
    ("andesite_bogie_steps", "ladder"),
    ("brass_bogie_steps", "ladder"),
    ("copper_bogie_steps", "ladder"),
    ("andesite_grab_rails", "ladder"),
    ("brass_grab_rails", "ladder"),
    ("copper_grab_rails", "ladder"),
    ("andesite_door_step", "ladder"),
    ("brass_door_step", "ladder"),
    ("copper_door_step", "ladder"),
    ("ornate_iron_trapdoor", "trapdoor"),
    ("headlight", "lever"),
    ("station_platform", "pumpkin"),
    ("metro_casing", "iron_block"),
    ("corrugated_metro_casing", "iron_block"),
    ("metro_panel", "end_rod"),
    ("corrugated_metro_panel", "end_rod"),
    ("metro_trapdoor", "trapdoor"),
    ("metro_window", "trapdoor"),
    ("andesite_pilot", "pumpkin"),
    ("brass_pilot", "pumpkin"),
    ("copper_pilot", "pumpkin"),
    ("metal_pilot", "pumpkin"),
    ("polished_andesite_pilot", "pumpkin"),
    ("polished_granite_pilot", "pumpkin"),
    ("polished_diorite_pilot", "pumpkin"),
    ("polished_deepslate_pilot", "pumpkin"),
    ("polished_dripstone_pilot", "pumpkin"),
    ("polished_tuff_pilot", "pumpkin"),
    ("polished_calcite_pilot", "pumpkin"),
    ("polished_limestone_pilot", "pumpkin"),
    ("polished_scoria_pilot", "pumpkin"),
    ("polished_scorchia_pilot", "pumpkin"),
    ("polished_crimsite_pilot", "pumpkin"),
    ("polished_ochrum_pilot", "pumpkin"),
    ("polished_veridium_pilot", "pumpkin"),
    ("polished_asurine_pilot", "pumpkin"),
]

HORIZONTAL = ["north", "south", "east", "west"]
FACES = ["down", "up", "north", "south", "west", "east"]
TEMPLATES = {
    "ladder": {
        "vanilla": "minecraft:ladder",
        "props": [("facing", HORIZONTAL), ("waterlogged", ["false", "true"])],
        "support": (0, 0, 1),
        "default": {"facing": "north", "waterlogged": "false"},
    },
    "trapdoor": {
        "vanilla": "minecraft:iron_trapdoor",
        "props": [
            ("facing", HORIZONTAL),
            ("half", ["top", "bottom"]),
            ("open", ["false", "true"]),
            ("powered", ["false", "true"]),
            ("waterlogged", ["false", "true"]),
        ],
        "support": (0, -1, 0),
        "default": {
            "facing": "north",
            "half": "bottom",
            "open": "false",
            "powered": "false",
            "waterlogged": "false",
        },
    },
    "lever": {
        "vanilla": "minecraft:lever",
        "props": [
            ("face", ["floor", "wall", "ceiling"]),
            ("facing", HORIZONTAL),
            ("powered", ["false", "true"]),
        ],
        "support": (0, 0, 1),
        "default": {"face": "wall", "facing": "north", "powered": "false"},
    },
    "pumpkin": {
        "vanilla": "minecraft:carved_pumpkin",
        "props": [("facing", HORIZONTAL)],
        "support": None,
        "default": {"facing": "north"},
    },
    "end_rod": {
        "vanilla": "minecraft:end_rod",
        "props": [("facing", FACES)],
        "support": (0, -1, 0),
        "default": {"facing": "up"},
    },
    "iron_block": {
        "vanilla": "minecraft:iron_block",
        "props": [],
        "support": None,
        "default": {},
    },
}


def combinations(props, index=0, current=None):
    if current is None:
        current = {}
    if index == len(props):
        yield dict(current)
        return
    name, values = props[index]
    for value in values:
        current[name] = value
        yield from combinations(props, index + 1, current)
    del current[name]


def main():
    sock, ctl, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    if mode not in ("mod", "vanilla"):
        raise SystemExit(f"mode must be mod or vanilla, not {mode}")

    def run(*args):
        out = subprocess.run([ctl, "--socket", sock, *args], text=True, capture_output=True)
        try:
            return json.loads(out.stdout)
        except json.JSONDecodeError:
            raise SystemExit(f"ctl {' '.join(args)}: {out.stdout}{out.stderr}")

    if mode == "vanilla":
        targets = [
            (TEMPLATES[template]["vanilla"], template)
            for template in ("ladder", "trapdoor", "lever", "pumpkin", "end_rod", "iron_block")
        ]
    else:
        targets = [(f"bellsandwhistles:{block_id}", template) for block_id, template in BLOCKS]

    # ---------------------------------------------------------- 1. registry
    x, y, z = 0, 120, 0
    accepted = 0
    for target, template in targets:
        for values in combinations(TEMPLATES[template]["props"]):
            state = ",".join(f"{k}={v}" for k, v in values.items())
            literal = f"{target}[{state}]" if state else target
            reply = run("setblock", str(x), str(y), str(z), literal)
            if not reply.get("ok"):
                raise SystemExit(f"{literal}: setblock refused {reply}")
            accepted += 1
    print(f"{mode}: {accepted} states accepted by the registry")

    # ------------------------------------------------------------- 2. world
    placed = 0
    for index, (target, template) in enumerate(targets):
        spec = TEMPLATES[template]
        px, py, pz = 20 + index % 8, 100 + (index // 8) * 3, 0
        support = spec["support"]
        if support is not None:
            sx, sy, sz = px + support[0], py + support[1], pz + support[2]
            run("setblock", str(sx), str(sy), str(sz), "minecraft:stone")
        run("setblock", str(px), str(py), str(pz), "minecraft:air")
        run("setblock", str(px), str(py), str(pz), target)
        run("wait", "3")
        reply = run("block", str(px), str(py), str(pz))
        if reply.get("block") != target:
            raise SystemExit(
                f"{target} default at {px},{py},{pz} reads {reply.get('block')!r}"
            )
        got = reply.get("state", "")
        for key, want in spec["default"].items():
            if f"{key}={want}" not in got:
                raise SystemExit(f"{target} default reads {got!r}, missing {key}={want}")
        placed += 1
    print(f"{mode}: {placed}/{len(targets)} blocks place and read back their default state")


if __name__ == "__main__":
    main()
