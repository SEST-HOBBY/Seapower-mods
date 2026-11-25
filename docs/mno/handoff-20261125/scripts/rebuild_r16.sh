#!/bin/bash
# R16 candidate: Sea Power 0.9.3 Build 261123 (ea653e49), Dynamic Campaign Mod 1.0.2, 24 Nov 23:53 capture.
set -u
S=/tmp/claude-0/-home-user-Seapower-mods/b99d05e7-e016-5078-a9ab-c2deb264ce5c/scratchpad
ROOT=/home/user/sest-storms; BASE=62b8c2c71
cd $ROOT; C=integration/beta-feature-parity/candidates/R16-20261125; CAP=$S/refs1125
export MONO_PATH=$S/deps1125:$S/R16s PATH=$S/bin:$PATH
mkdir -p $C
rm -rf $S/R16s && $S/bin/pwsh -NoProfile -File integration/beta-feature-parity/build-roslyn.ps1 -Capture $CAP -Output $S/R16s 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tail -1
[ -f $S/R16s/AnchorChain.dll ] || { echo "FAIL build"; exit 1; }
pack(){
  cp $S/R16s/AnchorChain.dll $S/R16s/SEST.*.dll $S/R16s/build-receipt.json $S/R16s/validation.json $C/ 2>/dev/null
  git diff $BASE -- integration/beta-feature-parity integration/beta-anchorchain ':(exclude)integration/beta-feature-parity/candidates' > $S/R16s-SOURCE-CHANGES.patch
  prev=""; for f in $S/chain/prev-*.json; do prev="$prev --repair-previous $f"; done
  python3 integration/beta-feature-parity/package.py --candidate $C --output $S/R16s-package.zip --source-patch $S/R16s-SOURCE-CHANGES.patch --repair-base $S/chain/base.json $prev \
    --repair-previous integration/beta-feature-parity/candidates/R13-20261111/build-receipt.json \
    --repair-previous integration/beta-feature-parity/candidates/R14-20261114/build-receipt.json || { echo FAIL package; exit 1; }
}
python3 integration/beta-feature-parity/verify.py --capture $CAP --candidate $S/R16s --flat-references $S/flat1125 --mono mono --powershell pwsh > $S/verify-r16-1.log 2>&1 || { echo "FAIL verify pass 1"; tail -14 $S/verify-r16-1.log; exit 1; }
echo "verify pass 1: $(tail -1 $S/verify-r16-1.log)"
pack
rm -rf $S/R16s-pkg $S/prevR15b $S/prevGPT && mkdir -p $S/R16s-pkg $S/prevR15b/pkg $S/prevGPT/pkg
git show f2da3f0fa:integration/campaign/setup/beta-support/SEST-Beta-Features.zip > $S/prevR15b/SEST-Beta-Features.zip
git show 089527cfa:integration/campaign/setup/beta-support/SEST-Beta-Features.zip > $S/prevGPT/SEST-Beta-Features.zip
for d in prevR15b prevGPT; do python3 -I -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $S/$d/SEST-Beta-Features.zip $S/$d/pkg; done
python3 -I -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" $S/R16s-package.zip $S/R16s-pkg
python3 integration/beta-feature-parity/verify.py --capture $CAP --candidate $S/R16s --flat-references $S/flat1125 --mono mono --powershell pwsh \
  --previous-package $S/prevR15b/SEST-Beta-Features.zip --previous-payload $S/prevR15b/pkg/payload --previous-capture $S/refs1122 \
  --repair-package $S/R16s-pkg > $S/verify-r16-2.log 2>&1 || { echo "FAIL verify pass 2 (cross-build)"; tail -16 $S/verify-r16-2.log; exit 1; }
echo "verify pass 2: $(tail -1 $S/verify-r16-2.log)"
pack
python3 -I -c "import zipfile,sys;open(sys.argv[2],'wb').write(zipfile.ZipFile(sys.argv[1]).read('README-FIRST.txt').replace(b'\r\n',b'\n'))" $S/R16s-package.zip $C/README-FIRST.txt
python3 -I -c "
import zipfile,json,sys;r=json.loads(zipfile.ZipFile(sys.argv[1]).read('repair-receipt.json'));print('repair previous sets:',len(r['previous_files']))
b=json.loads(zipfile.ZipFile(sys.argv[1]).read('payload/build-receipt.json'));print('revision:',b['candidate_revision']);print('game:',b.get('target_game_sha256','')[:12])" $S/R16s-package.zip
python3 integration/beta-feature-parity/build-workshop-support.py --package $S/R16s-package.zip | tail -1 || { echo FAIL support; exit 1; }
echo "== candidate done"
