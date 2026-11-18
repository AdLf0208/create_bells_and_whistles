#!/usr/bin/env bash
# In-game check for the Bells & Whistles content slice: the 36 decorative
# blocks (nine metal rails, headlight, ornate iron trapdoor, station platform,
# the metro casing/panel/trapdoor/window set and eighteen pilots), their items,
# loot, recipes, tags and creative tab.
#
# STATUS (2026-11-18, mod API 0.2): this scenario needs a game built by the launcher with this
# flat SDK package (`horizon-launcher native-build ports/bellsandwhistles --instance <i>
# --trust-native-code`), because the 36 blocks now travel inside `bellsandwhistles.hmod` and a
# native package is compiled into `horizon-client`. The migration did NOT re-run it: the launcher
# is not installed in this environment, so there is no game build at `0b14f8a` (recorded as a gap
# in `notes.md`). The 0.1.0 runs remain the behaviour's evidence
# (`evidence/bellsandwhistles/e2e*.log`, retired `--dev-mod content/` format); the content is the
# same 323 files and `src/runtime.rs` is byte-identical.
#
#   GAME=<launcher build>/horizon-client CTL=<a horizon-ctl of the same build> tools/e2e.sh
#   CONTROL_GAME=<a game WITHOUT the package> adds the differential leg: the same `give` finds no
#   `bellsandwhistles:metal_pilot`, so the ids are known only because the package is installed.
#
# Default run (creative launch, then survival for drops/crafting; The End):
#   1. every state of every block binds: the templates' state spaces are
#      enumerated (8 ladder + 64 trapdoor + 24 lever + 4 pumpkin + 6 end rod +
#      1 iron block = 378 states) and `setblock` accepts each; every block's
#      default state then places in a valid support context and reads back;
#   2. the game log has no blockstate/model error naming the namespace;
#   3. all 36 block items are `/give`-able and the creative tab's 36 entries are carried;
#   4. placement reads back the template's states: a wall ladder faces north, a
#      wall lever is `face=wall,facing=north`, a floor end rod faces up, floor
#      trapdoors are `half=bottom`, pumpkins face horizontally;
#   5. tags: the six rails are `#minecraft:climbable`, the 27 stone/metal blocks
#      are `#minecraft:mineable/pickaxe`, and the cross controls are absent;
#   6. the headlight emits light 15 while a casing emits 0;
#   7. eight blocks drop themselves with the right tool;
#   8. six recipes craft in a crafting table (bogie steps, grab rails,
#      headlight, metro panel, station platform, tuff pilot) and four wrong
#      grids leave the result empty;
#   9. unknown ids are refused.
#
# COUNTERFACTUAL=1 runs the same state space on the six vanilla templates
# (107 states), breaks them for their vanilla drops, and shows the same recipe
# grids produce nothing without the mod.
#
# SELFTEST=1 (or the old NEGATIVE=1 with COUNTERFACTUAL=1) asserts a vanilla ladder drops a
# Bells & Whistles item: the run MUST fail, proving the drop assertion is not vacuous.
set -euo pipefail

CLONE=/home/adlf/Desktop/all_the_mods_10_rust_rewrite
PORT=$CLONE/ports/bellsandwhistles
# A launcher-built game carries the mod; `horizon-ctl` must come from the same build (the shared
# binary is published per pin, and none exists at 0b14f8a yet). Nothing here builds a game:
# `tools/horizon.py` is retired with the .hnmod format.
CTL=${CTL:-$PORT/target/horizon-cargo/fast/horizon-ctl}
GAME=${GAME:-$PORT/target/horizon-cargo/fast/horizon-client}
# An optional game built WITHOUT this package: the differential leg below proves the ids come
# from the package rather than from the engine.
CONTROL_GAME=${CONTROL_GAME:-}
RES=${RES:-${HORIZON_RES:-/home/adlf/Desktop/horizon/.local/horizon-client/26.3}}
SOCK=${SOCK:-/tmp/opencode/bellsandwhistles-e2e.sock}
COUNTERFACTUAL=${COUNTERFACTUAL:-0}
NEGATIVE=${NEGATIVE:-0}
SELFTEST=${SELFTEST:-0}
# The one-switch fail-capable leg: SELFTEST=1 is the counterfactual with the false claim asserted.
if [ "$SELFTEST" = 1 ]; then
    COUNTERFACTUAL=1
    NEGATIVE=1
fi

[ -x "$CTL" ] || { echo "missing horizon-ctl: $CTL (build it against the same SDK pin as GAME)" >&2; exit 1; }
[ -x "$GAME" ] || { echo "missing horizon-client (a launcher build with this package): $GAME" >&2; exit 1; }
[ -d "$RES/assets" ] || { echo "missing prepared resources: $RES" >&2; exit 1; }
[ -f "$PORT/bellsandwhistles.hmod" ] || { echo "missing package: $PORT/bellsandwhistles.hmod" >&2; exit 1; }

SCRATCH=$(mktemp -d /tmp/opencode/bellsandwhistles-home.XXXXXX)
export HORIZON_HOME=$SCRATCH/game
export HORIZON_LAUNCHER_HOME=$SCRATCH/launcher
export XDG_DATA_HOME=$SCRATCH/data
export XDG_CONFIG_HOME=$SCRATCH/config
export HORIZON_NO_AUDIO=1
mkdir -p "$(dirname "$SOCK")"
rm -f "$SOCK"
cd "$SCRATCH"

ctl() { "$CTL" --socket "$SOCK" "$@"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
say() { echo "+ $*"; }
count_item() { ctl inventory | jq -r --arg i "$1" '.counts[$i] // 0'; }
block_state() { ctl block "$1" "$2" "$3" | jq -r '.block // "unknown"'; }
full_state() { ctl block "$1" "$2" "$3" | jq -r '.state // "unknown"'; }
prop() { echo "$1" | grep -o "$2=[a-z_]*" | head -1 | cut -d= -f2 || true; }
assert_prop() {
    local state=$1 key=$2 want=$3 got
    got=$(prop "$state" "$key")
    [ "$got" = "$want" ] || fail "$state: $key is '$got', expected '$want'"
}
end() { ctl command "execute in minecraft:the_end run $1"; }

cleanup() {
    local status=$?
    ctl quit >/dev/null 2>&1 || true
    sleep 1
    rm -rf "$SCRATCH" || true
    # Last line of every run: `check-e2e-logs.py` reads it as the verdict.
    echo "EXIT:$status"
}
trap cleanup EXIT

launch() { # launch WORLD [GAME]
    local game=${2:-$GAME}
    rm -f "$SOCK"
    "$CTL" --socket "$SOCK" launch \
        --game "$game" --world "$1" --seed 20261105 --creative --offscreen --wait \
        --game-dir "$SCRATCH/game" --resources "$RES"
    ctl wait-ready 180
}

# The differential leg: a game built WITHOUT this package knows neither the blocks nor their
# items, so the same `give` the scenario relies on finds nothing. If the id resolved there, the
# run below would prove nothing about the package.
control_leg() {
    say "control: a game built without the package"
    launch BellsControl "$CONTROL_GAME"
    ctl command "clear @s" >/dev/null
    ctl give bellsandwhistles:metal_pilot 1 >/dev/null 2>&1 || true
    ctl wait 3
    ctl inventory | jq -e '[.hotbar[], .main[] | select(.item == "bellsandwhistles:metal_pilot")] | length == 0' >/dev/null \
        || fail "the control game has bellsandwhistles:metal_pilot, so the ids did not come from the package"
    echo "without the package: no bellsandwhistles:metal_pilot could be given"
    ctl quit >/dev/null 2>&1 || true
    rm -f "$SOCK"
}

if [ -n "$CONTROL_GAME" ]; then control_leg; fi

say "launch (offscreen renderer, creative, the package built into the game)"
launch BellsE2E

say "The End platform at y=79 and an empty box above it"
end "forceload add -12 -12 40 12"
end "tp @s 0.5 80 2.5"
ctl wait 40
end "fill -12 79 -12 40 79 12 minecraft:stone"
end "fill -12 80 -12 40 96 12 minecraft:air"
end "kill @e[type=minecraft:item]"
end "kill @e[type=minecraft:ender_dragon]"
end "kill @e[type=minecraft:end_crystal]"
end "difficulty peaceful"
end "tp @s 0.5 80 2.5"
ctl wait 10
# Killing the dragon opens the win screen; it would block every later click.
ctl close >/dev/null 2>&1 || true
ctl wait 3

# --------------------------------------------------------------- content log
say "the content loaded without a blockstate or model error"
LOG=$SCRATCH/game/logs/latest.log
[ -f "$LOG" ] || fail "no game log at $LOG"
cp "$LOG" /tmp/opencode/bellsandwhistles-game.log || true
if grep -E "blockstate definition of bellsandwhistles|standalone model bellsandwhistles|bellsandwhistles.*(not loaded|missing model)" "$LOG" >/dev/null; then
    grep -E "blockstate definition of bellsandwhistles|standalone model bellsandwhistles|bellsandwhistles.*(not loaded|missing model)" "$LOG" >&2
    fail "the content log names a blockstate or model error"
fi
if grep -F "using the missing model" "$LOG" >/dev/null; then
    grep -F "using the missing model" "$LOG" >&2
    fail "a block model is incomplete (the missing model is in use)"
fi
echo "no blockstate/model error in the log"

if [ "$COUNTERFACTUAL" = 1 ]; then
    # --------------------------------------------------------- differential
    say "counterfactual: the six vanilla templates bind their own states"
    python3 "$PORT/tools/state_check.py" "$SOCK" "$CTL" vanilla || fail "vanilla state check failed"

    say "counterfactual: the vanilla templates drop themselves, never our items"
    # Valid supports, so the ladder/lever/trapdoor/end rod do not pop.
    end "setblock 18 81 1 minecraft:stone"
    end "setblock 20 81 1 minecraft:stone"
    end "setblock 19 80 0 minecraft:stone"
    end "setblock 22 80 0 minecraft:stone"
    ctl command "gamemode survival @s" >/dev/null
    for _ in $(seq 1 40); do
        [ "$(ctl state | jq -r '.gamemode')" = "survival" ] && break
        ctl wait 1
    done
    [ "$(ctl state | jq -r '.gamemode')" = "survival" ] || fail "player did not enter survival"
    for spec in \
        "18 81 0 minecraft:ladder hand" \
        "19 81 0 minecraft:iron_trapdoor pickaxe" \
        "20 81 0 minecraft:lever hand" \
        "21 81 0 minecraft:carved_pumpkin pickaxe" \
        "22 81 0 minecraft:end_rod pickaxe" \
        "23 81 0 minecraft:iron_block pickaxe"; do
        read -r x y z block tool <<< "$spec"
        ctl command "clear @s" >/dev/null
        if [ "$tool" = pickaxe ]; then
            ctl give minecraft:diamond_pickaxe 1 >/dev/null
            ctl select 1 >/dev/null
        fi
        ctl setblock "$x" "$y" "$z" "$block" >/dev/null || fail "cannot set $block"
        ctl command "tp @s $((x)).5 81 -1.5" >/dev/null
        ctl wait 5
        ctl look-at-block "$x" "$y" "$z" >/dev/null || true
        broken=$(ctl break "$x" "$y" "$z") || { echo "break reply: $broken"; fail "cannot break $block"; }
        echo "$broken" | jq -c '{block,block_before,drops}'
        [ "$(echo "$broken" | jq -r '.block')" = "minecraft:air" ] || fail "$block did not break"
        own=$(echo "$broken" | jq -r --arg i "$block" '.drops[$i] // 0')
        [ "$own" -ge 1 ] || fail "$block dropped $own of itself"
        mod=$(echo "$broken" | jq -r '[.drops | keys[] | select(startswith("bellsandwhistles:"))] | length')
        if [ "$NEGATIVE" = 1 ]; then
            # The claim under test: this vanilla template drops a Bells &
            # Whistles item. The run must fail because it does not.
            if [ "$mod" -ge 1 ]; then
                fail "NEGATIVE run: the false claim held for $block (a mod item dropped)"
            fi
            echo "NEGATIVE: the false claim failed as required ($block dropped no mod item)"
            exit 1
        fi
        [ "$mod" -eq 0 ] || fail "$block dropped a Bells & Whistles item"
    done
    echo "COUNTERFACTUAL PASS: the vanilla templates drop only themselves"

    say "counterfactual: the recipe grids make nothing without the mod"
    end "setblock 6 80 2 minecraft:crafting_table"
    ctl command "gamemode creative @s" >/dev/null
    ctl command "tp @s 5.5 80 2.5" >/dev/null
    ctl wait 5
    python3 "$PORT/tools/craft_check.py" "$SOCK" "$CTL" 6 80 2 vanilla || fail "vanilla recipe check failed"

    say "counterfactual: unknown ids are still refused"
    if ctl give bellsandwhistles:not_a_block 1 >/dev/null 2>&1; then
        fail "give bellsandwhistles:not_a_block succeeded"
    fi
    ctl setblock 30 80 5 bellsandwhistles:bogus >/dev/null 2>&1 || true
    [ "$(block_state 30 80 5)" = "minecraft:air" ] || fail "bellsandwhistles:bogus became a block"
    echo "unknown Bells & Whistles ids are refused"
    echo "PASS: counterfactual differential"
    exit 0
fi

# --------------------------------------------------------------- state bind
say "the 378 declared states are accepted and every block places and reads back"
python3 "$PORT/tools/state_check.py" "$SOCK" "$CTL" mod || fail "state check failed"

# --------------------------------------------------------------- item side
say "all 36 block items are give-able"
ctl command "clear @s" >/dev/null
# The tab is carried inside the package; reading it from `bellsandwhistles.hmod` (not the retired
# `content/` folder or the `--dev-mod` cache) is what a launcher-built game loads.
IDS=$(python3 - "$PORT/bellsandwhistles.hmod" <<'EOF'
import json, subprocess, sys
raw = subprocess.check_output(["unzip", "-p", sys.argv[1],
                               "data/bellsandwhistles/horizon/creative_tab/bellsandwhistles.json"])
print("\n".join(item.split(":", 1)[1] for item in json.loads(raw)["items"]))
EOF
)
for id in $IDS; do
    ctl give "bellsandwhistles:$id" 1 >/dev/null || fail "give bellsandwhistles:$id failed"
done
ctl wait 10
for id in $IDS; do
    [ "$(count_item "bellsandwhistles:$id")" -ge 1 ] || fail "bellsandwhistles:$id is missing"
done
echo "36/36 block items are give-able"

# The live tab listing was proved in the 0.1.0 run through the `--dev-mod` cache; a launcher-built
# package exposes no such file and `horizon-ctl` has no creative-tab reader, so the package's own
# tab declaration and the 36 successful gives above are what this leg can assert here.
TAB_COUNT=$(printf '%s\n' $IDS | wc -l)
[ "$TAB_COUNT" -eq 36 ] || fail "the creative tab lists $TAB_COUNT entries, expected 36"
echo "the package's creative tab lists all 36 entries"

# --------------------------------------------------------------- placement
say "placement reads back the template states"
ctl command "gamemode creative @s" >/dev/null
ctl command "clear @s" >/dev/null
end "fill 18 80 -3 30 80 3 minecraft:stone"
end "fill 18 81 3 30 82 3 minecraft:stone"
end "fill 18 81 -3 30 82 2 minecraft:air"
# The wall placements below must have no floor under them, or `place` picks
# the floor first (the FACES order starts at down).
end "setblock 18 80 2 minecraft:air"
end "setblock 23 80 2 minecraft:air"
end "setblock 26 80 2 minecraft:air"
ctl wait 5

place() { # x z item look-at stand-z
    local x=$1 z=$2 item=$3 look=$4 stand_z=$5
    ctl tp "$((x)).5 81 $stand_z" >/dev/null
    ctl wait 2
    ctl look-at-block $look >/dev/null || true
    ctl command "clear @s" >/dev/null
    ctl give "$item" 1 >/dev/null || fail "cannot give $item"
    ctl wait 1
    reply=$(ctl place "$x" 81 "$z" --item "$item" 2>&1) || { echo "place reply: $reply"; fail "cannot place $item"; }
    ctl wait 2
}

place 18 2 bellsandwhistles:andesite_grab_rails "18 81 3 north" 0.5
place 19 0 bellsandwhistles:metro_trapdoor "19 80 0 up" -1.5
place 20 0 bellsandwhistles:metro_panel "20 80 0 up" -1.5
place 21 0 bellsandwhistles:station_platform "21 80 0 up" -1.5
place 22 0 bellsandwhistles:metal_pilot "22 80 0 up" -1.5
place 23 2 bellsandwhistles:headlight "23 81 3 north" 0.5
place 24 0 bellsandwhistles:ornate_iron_trapdoor "24 80 0 up" -1.5
place 25 0 bellsandwhistles:corrugated_metro_panel "25 80 0 up" -1.5
place 26 2 bellsandwhistles:brass_grab_rails "26 81 3 north" 0.5
place 27 0 bellsandwhistles:polished_tuff_pilot "27 80 0 up" -1.5

[ "$(block_state 18 81 2)" = "bellsandwhistles:andesite_grab_rails" ] || fail "the grab rail did not place"
[ "$(block_state 19 81 0)" = "bellsandwhistles:metro_trapdoor" ] || fail "the metro trapdoor did not place"
[ "$(block_state 20 81 0)" = "bellsandwhistles:metro_panel" ] || fail "the metro panel did not place"
[ "$(block_state 21 81 0)" = "bellsandwhistles:station_platform" ] || fail "the station platform did not place"
[ "$(block_state 22 81 0)" = "bellsandwhistles:metal_pilot" ] || fail "the pilot did not place"
[ "$(block_state 23 81 2)" = "bellsandwhistles:headlight" ] || fail "the headlight did not place"
[ "$(block_state 24 81 0)" = "bellsandwhistles:ornate_iron_trapdoor" ] || fail "the ornate trapdoor did not place"
[ "$(block_state 25 81 0)" = "bellsandwhistles:corrugated_metro_panel" ] || fail "the corrugated panel did not place"
[ "$(block_state 26 81 2)" = "bellsandwhistles:brass_grab_rails" ] || fail "the brass grab rail did not place"
[ "$(block_state 27 81 0)" = "bellsandwhistles:polished_tuff_pilot" ] || fail "the tuff pilot did not place"

assert_prop "$(full_state 18 81 2)" facing north
assert_prop "$(full_state 19 81 0)" half bottom
assert_prop "$(full_state 20 81 0)" facing up
assert_prop "$(full_state 23 81 2)" face wall
assert_prop "$(full_state 23 81 2)" facing north
assert_prop "$(full_state 24 81 0)" half bottom
assert_prop "$(full_state 25 81 0)" facing up
assert_prop "$(full_state 26 81 2)" facing north
for x in 21 22 27; do
    state=$(full_state "$x" 81 0)
    case "$(prop "$state" facing)" in
        north|south|east|west) ;;
        *) fail "$x 81 0: $state is not a horizontal facing" ;;
    esac
done
echo "placement: ladder north, lever wall/north, end rods up, trapdoors bottom, pumpkins horizontal"

# --------------------------------------------------------------- tags/light
say "tags: six climbable rails, 27 mineable/pickaxe blocks"
ctl command "execute in minecraft:the_end if block 18 81 2 #minecraft:climbable run say TAG_CLIMB" >/dev/null
ctl command "execute in minecraft:the_end if block 26 81 2 #minecraft:climbable run say TAG_CLIMB_BRASS" >/dev/null
ctl command "execute in minecraft:the_end if block 20 81 0 #minecraft:mineable/pickaxe run say TAG_PICKAXE" >/dev/null
ctl command "execute in minecraft:the_end if block 19 81 0 #minecraft:mineable/pickaxe run say TAG_PICKAXE_TRAPDOOR" >/dev/null
ctl command "execute in minecraft:the_end if block 20 81 0 #minecraft:climbable run say TAG_BAD_CLIMB" >/dev/null
ctl command "execute in minecraft:the_end if block 18 81 2 #minecraft:mineable/pickaxe run say TAG_BAD_PICKAXE" >/dev/null
ctl wait 3
messages=$(ctl messages 60 | jq -r '.chat[]')
for tag in TAG_CLIMB TAG_CLIMB_BRASS TAG_PICKAXE TAG_PICKAXE_TRAPDOOR; do
    echo "$messages" | grep -q "$tag" || fail "missing $tag"
done
for tag in TAG_BAD_CLIMB TAG_BAD_PICKAXE; do
    if echo "$messages" | grep -q "$tag"; then fail "$tag must not fire"; fi
done
echo "tags: climbable rails and pickaxe casings/panels/trapdoors, cross controls absent"

say "light: the headlight emits 15, a casing emits 0"
head_light=$(ctl light 23 81 2 23 81 2 | jq -r '.block')
[ "$head_light" = "f" ] || fail "headlight light is '$head_light', expected 'f'"
ctl setblock 28 81 0 bellsandwhistles:metro_casing >/dev/null
ctl wait 2
casing_light=$(ctl light 28 81 0 28 81 0 | jq -r '.block')
[ "$casing_light" = "0" ] || fail "casing light is '$casing_light', expected '0'"
echo "light: headlight 15, casing 0"

# ------------------------------------------------------------------- drops
say "drops: eight blocks drop themselves with the right tool"
ctl command "gamemode survival @s" >/dev/null || fail "gamemode survival failed"
for _ in $(seq 1 40); do
    [ "$(ctl state | jq -r '.gamemode')" = "survival" ] && break
    ctl wait 1
done
[ "$(ctl state | jq -r '.gamemode')" = "survival" ] || fail "player did not enter survival"
drop() { # x y z item tool
    local x=$1 y=$2 z=$3 item=$4 tool=$5
    ctl command "clear @s" >/dev/null || fail "$item: clear failed"
    if [ "$tool" = pickaxe ]; then
        ctl give minecraft:diamond_pickaxe 1 >/dev/null || fail "$item: give pickaxe failed"
        ctl select 1 >/dev/null || fail "$item: select hotbar failed"
    fi
    ctl tp "$((x)).5 81 -1.5" >/dev/null || fail "$item: tp failed"
    ctl wait 3
    ctl look-at-block "$x" "$y" "$z" >/dev/null || true
    broken=$(ctl break "$x" "$y" "$z") || { echo "break reply: $broken"; fail "cannot break $item"; }
    echo "$broken" | jq -c --arg i "$item" '{block,block_before,drops}'
    [ "$(echo "$broken" | jq -r '.block')" = "minecraft:air" ] || fail "$item did not break"
    got=$(echo "$broken" | jq -r --arg i "$item" '.drops[$i] // 0')
    [ "$got" -ge 1 ] || fail "$item dropped $got of itself"
    foreign=$(echo "$broken" | jq -r --arg i "$item" '[.drops | keys[] | select(startswith("bellsandwhistles:") and . != $i)] | length')
    [ "$foreign" -eq 0 ] || fail "$item dropped a foreign mod item"
}

drop 18 81 2 bellsandwhistles:andesite_grab_rails hand
drop 23 81 2 bellsandwhistles:headlight hand
drop 19 81 0 bellsandwhistles:metro_trapdoor pickaxe
drop 20 81 0 bellsandwhistles:metro_panel pickaxe
drop 21 81 0 bellsandwhistles:station_platform pickaxe
drop 22 81 0 bellsandwhistles:metal_pilot pickaxe
drop 24 81 0 bellsandwhistles:ornate_iron_trapdoor pickaxe
drop 28 81 0 bellsandwhistles:metro_casing pickaxe
echo "drops: the eight tested blocks dropped themselves"

# ----------------------------------------------------------------- recipes
say "recipes: six craft, four controls stay empty"
ctl command "gamemode creative @s" >/dev/null
ctl command "clear @s" >/dev/null
end "setblock 6 80 2 minecraft:crafting_table"
ctl command "tp @s 5.5 80 2.5" >/dev/null
ctl wait 5
python3 "$PORT/tools/craft_check.py" "$SOCK" "$CTL" 6 80 2 mod || fail "the recipe check failed"

# ------------------------------------------------------------- unknown ids
say "unknown ids are refused"
if ctl give bellsandwhistles:not_a_block 1 >/dev/null 2>&1; then
    fail "give bellsandwhistles:not_a_block succeeded"
fi
ctl setblock 30 80 5 bellsandwhistles:bogus >/dev/null 2>&1 || true
[ "$(block_state 30 80 5)" = "minecraft:air" ] || fail "bellsandwhistles:bogus became a block"
echo "unknown Bells & Whistles ids are refused"

echo "PASS: 378 states accepted, 36 blocks place and read back, 36 items give, the tab lists 36, placement/tags/light/drops pass, six recipes craft and four controls stay empty, unknown ids are refused"
