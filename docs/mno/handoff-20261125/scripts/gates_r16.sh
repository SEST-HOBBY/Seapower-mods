#!/bin/bash
# Record, check, test (the packs and manifest are already built). Says where anything fails.
set -u
S=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad
cd /home/user/sest-storms
export PATH=$S/bin:$PATH
COUNT=$(python3 -c "import json;print(json.load(open('docs/releases/20261107/upload-manifest.json'))['file_count'])")
PKG=$(sha256sum integration/dist/SEST_Integration/beta-support/SEST-Beta-Features.zip | cut -d' ' -f1)
grep -q "VERIFIED: all $COUNT canonical" <(tr -s ' \n' ' ' < docs/releases/20261107/README-FIRST.txt) || { echo "FAIL README count is not $COUNT"; exit 1; }
python3 $S/scripts/update_validation_r16.py $COUNT $PKG || exit 1
echo "== gates"
for c in "tools/check_pack_fidelity.py" "tools/check_campaign_coverage.py" "tools/check_dependencies.py" "tools/check_load_order.py" "tools/preflight.py --all" "tools/check_weapon_employment.py" "tools/check_alias_bases.py" "tools/check_scenarios.py" "tools/check_stale_phrases.py" "tools/check_inventory.py" "tools/check_game_version.py" "tools/check_vanilla_drift.py --since 1bda58a6" "tools/check_combat_costs.py" "integration/world-sandbox/check_dynamic_campaign.py integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json"; do
  python3 $c > $S/gate.log 2>&1; e=$?; echo "  $e $c"; [ $e != 0 ] && { grep -iE "FAIL|error|missing|stale" $S/gate.log | head -8 | cut -c1-400 | sed 's/^/      /'; tail -2 $S/gate.log | cut -c1-300 | sed 's/^/      /'; }
done
echo "== tests"
python3 -m unittest discover -s tools/tests -p 'test_*.py' > $S/fin-tools.log 2>&1; echo "  tools exit=$? $(tail -1 $S/fin-tools.log)"; grep -E "^(FAIL|ERROR):" $S/fin-tools.log | head -20
python3 -m unittest integration/campaign/test_build_pack.py integration/campaign/test_playtest_revision.py integration/campaign/test_red_line_pacing.py > $S/fin-camp.log 2>&1; echo "  campaign exit=$? $(tail -1 $S/fin-camp.log)"; grep -E "^(FAIL|ERROR):" $S/fin-camp.log | head -20
echo "== done: $COUNT files, package $PKG"
