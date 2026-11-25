#!/bin/bash
# usage: run-tests.sh <out> ; runs from repo root of the trial copy
S=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad
OUT=${1:-$S/trial/out}; FLAT=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad/flat1125; W=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad/refs1125/references/workshop/library-1
ROOT=${2:-$S/trial/repo}; ORIG=$ROOT/integration/runtime-fixes/SEST.RuntimeFixes.dll
RT=$OUT/SEST.RuntimeFixes.dll; UI=$OUT/SEST.ContactsFix.dll
export MONO_PATH=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad/deps1125:$OUT
cd $ROOT
t(){ n=$1; shift; o=$("$@" 2>&1); c=$?; if [ $c = 0 ]; then echo "PASS $n"; else echo "FAIL $n ($c)"; echo "$o" | grep -viE "^\s*$" | grep -iE "fail|error|exception|expected|mismatch|missing|not " | head -${LINES_PER:-12} | sed 's/^/    /'; fi; }
t runtime-api-preservation python3 integration/beta-feature-parity/tests/check_runtime_contract.py $ORIG $RT
t native-bindings mono $OUT/NativeBindingTests.exe $FLAT $RT $W
t native-plugin-transpilers mono $OUT/HookTests.exe $FLAT $RT $UI $W
t runtime-history-policy-parity mono $OUT/RuntimeParityTests.exe $FLAT $ORIG $RT
t price-factory-caching mono $OUT/CatalogueRuntimeTests.exe $FLAT $RT $UI
t identify-path-detours mono $OUT/PathTests.exe $W/3790594162/IdentifyExpanded.dll
t bounded-loader-scheduler mono $OUT/LoaderTests.exe
t assembly-preload-policy mono $OUT/AssemblyPolicyTests.exe $W $FLAT/Seapower-Scripts.dll
t beta-api-regressions mono $OUT/BetaApiTests.exe $W $FLAT/Seapower-Scripts.dll
t cost-rows mono $OUT/CostRowsTests.exe $FLAT $RT
t world-operations mono $OUT/WorldOperationsTests.exe $FLAT $RT $W
t world-battle-flow mono $OUT/WorldBattleFlowTests.exe $FLAT $UI $W/3813157776/DynamicCampaignMod.dll
t mission-awards mono $OUT/MissionAwardsTests.exe $FLAT $RT $W
t world-placed-storms mono $OUT/WorldStormsTests.exe $FLAT $RT $W/3813157776/DynamicCampaignMod.dll integration/test-campaigns/Test_Campaigns/dynamic_campaigns/sest-test-hormuz-weather/sest-weather.json
t storm-sidecar-builder python3 -m unittest discover -s tools/tests -p test_make_sest_weather.py
t loader-source-contracts python3 integration/beta-anchorchain/test_source_contract.py
t local-battle-weather mono $OUT/LocalWeatherTests.exe $FLAT $RT $W/3813157776/DynamicCampaignMod.dll integration/test-campaigns/Test_Campaigns/dynamic_campaigns/sest-test-hormuz-weather
t sea-ice-model-and-bindings mono $OUT/SeaIceTests.exe $FLAT $RT
t ice-shelves-and-icebergs mono $OUT/IceFeaturesTests.exe
t sea-ice-table python3 -m unittest discover -s tools/tests -p test_sea_ice_model.py
t campaign-map-sea-ice mono $OUT/CampaignIceTests.exe $FLAT $RT $W/3813157776/DynamicCampaignMod.dll integration/test-campaigns/Test_Campaigns/dynamic_campaigns
