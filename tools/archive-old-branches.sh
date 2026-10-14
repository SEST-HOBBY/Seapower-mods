#!/usr/bin/env bash
# One-off cleanup of old SEST branches (checked 14 Oct 2026).
#
# Archives 12 old branches as annotated tags (archive/<branch>), then deletes
# them, and deletes 3 branches whose every commit is already in the deploy
# branch. It never deletes the deploy branch (data/deploy-branch.txt on the
# default branch), the default branch or the branches in KEEP, and it only
# touches a branch still at the commit listed below: anything pushed since is
# left alone, even if the push lands while this runs.
#
#   bash tools/archive-old-branches.sh           # preview: changes nothing
#   bash tools/archive-old-branches.sh --apply   # do it
#
# The terminal shows a short summary ending in a RESULT line. The full report
# is written to branch-cleanup-report.txt at the repo root and, in a
# Codespace, opened in the editor. Running it again after it worked is safe.
set -u
APPLY=no; [ "${1:-}" = "--apply" ] && APPLY=yes
EXPECT_ARCHIVE=12
EXPECT_DELETE=3
KEEP="
feature/northern-front-iii-export
sest-dev/loving-bell-3cnvvw
feature/workshop-update-20261013
sest-dev/inspiring-wozniak-8vuckh
feature/aim424-usn2027-flight-model
chore/workshop-refresh-20261013
"
DELETE_ONLY="
sest-dev/sweet-lovelace-3kxsve:a35efb905629a68809ef0b4831e5a37d6f9865b4
feature/world-campaign-draft:50cad91b02719b831cf853dc60f4b4916e7fecb6
sest-dev/peaceful-gauss-e1zvfq:596b086707da37205b0cee5fbc1182f59fc9c124
"
ARCHIVE="
chore/workshop-inventory-20260916:35a47270645756f8bf0881d1974647f11bb89473
chore/workshop-inventory-20260916-notes:fd0c1bdbcd0520c6380ae1e464a9071b080e971b
claude/repo-cleanup-interoperability-hleer5:b3669dfa1af0a4e29deac32dd2f5d7f58203eb22
feature/ras-integration:6c2075af431513a03808173942192d29dba20745
fix/banda-front-lean-finalize:9ed859da5c82c42a793e00807288c4b947bcd85b
fix/campaign-narrative-clarity-20260926:380c1e81173919bf0b489c7f4c24baf2a5b81fce
sest-dev/affectionate-volta-3xqkx6:6dbba32011cd810c6124bf0ba6fec4ff3864853a
sest-dev/beautiful-cerf-i7fqei:b0adc8d2337c75ed37ca13334afd6d6fef8f38e1
sest-dev/kind-faraday-ctr5h0:206b89fcdd0e77ff836a8637d931165d730c415a
sest-dev/quirky-noether-fq5i98:633e55fdb319990be9519570cd960c950699b13a
feature/tasman-shield-defector:cfcd59755dc24f18c6550c0b915826205a906e73
chore/gallery-handoff-20261005:59cf7b178ec46b06d7aa4da63ea9a4ddda38f099
"

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "RESULT: STOPPED. Run this in the Seapower-mods Codespace terminal."; exit 1; }
cd "$ROOT" || exit 1
REPORT="$ROOT/branch-cleanup-report.txt"
: > "$REPORT" || { echo "RESULT: STOPPED. Could not write the report file."; exit 1; }
log() { printf '%s\n' "$*" >> "$REPORT"; }
say() { printf '%s\n' "$*"; printf '%s\n' "$*" >> "$REPORT"; }
open_report() {
  if command -v code >/dev/null 2>&1; then code -r "$REPORT" >/dev/null 2>&1; fi
  echo "The full report is in branch-cleanup-report.txt."
}
stop() { say ""; say "RESULT: STOPPED. $1"; say "Send Claude the file branch-cleanup-report.txt."; open_report; exit 1; }
count() { set -- $1; echo $#; }
br() { if [ "$1" -eq 1 ]; then echo "1 branch"; else echo "$1 branches"; fi; }

if [ "$APPLY" = yes ]; then say "SEST branch cleanup: APPLY"; else say "SEST branch cleanup: PREVIEW (changes nothing)"; fi
log "Run at $(date -u '+%Y-%m-%d %H:%M UTC')"

git fetch -q origin --prune '+refs/heads/*:refs/remotes/origin/*' >> "$REPORT" 2>&1 \
  || stop "Could not read the branches on GitHub. Nothing was changed."
if [ "$(git rev-parse --is-shallow-repository)" = true ]; then
  git fetch -q --unshallow origin >> "$REPORT" 2>&1 || stop "Could not get the full history. Nothing was changed."
fi
DEFAULT=$(git ls-remote --symref origin HEAD 2>> "$REPORT" | awk '$1 == "ref:" { sub("^refs/heads/", "", $2); print $2 }')
DEPLOY=$(git show "refs/remotes/origin/$DEFAULT:data/deploy-branch.txt" 2>/dev/null | tr -d '\r' | grep -v '^#' | awk 'NF { print $1; exit }')
DEPLOY_TIP=$(git rev-parse -q --verify "refs/remotes/origin/$DEPLOY") || DEPLOY_TIP=""
if [ -z "$DEFAULT" ] || [ -z "$DEPLOY" ] || [ -z "$DEPLOY_TIP" ]; then
  stop "Could not find the default branch or the deploy branch. Nothing was changed."
fi
PROTECT="$KEEP $DEFAULT $DEPLOY"
tip() { git rev-parse -q --verify "refs/remotes/origin/$1"; }
is_in() { x=$1; shift; for y in "$@"; do [ "$y" = "$x" ] && return 0; done; return 1; }
load_tags() { TAGS=$(git ls-remote --tags origin 'refs/tags/archive/*' 2>> "$REPORT") || stop "Could not read the tags on GitHub. No branch was deleted."; }
tagged() { printf '%s\n' "$TAGS" | awk -v t="refs/tags/archive/$1" '$2 == t { d = $1 } $2 == t "^{}" { p = $1 } END { print (p != "" ? p : d) }'; }

for p in $DELETE_ONLY $ARCHIVE; do b=${p%%:*}
  is_in "$b" $PROTECT && stop "The plan would remove $b, which must be kept. Nothing was changed."
done
DEL=""; LEASE=""; ARCH=""; ARCH_NAMES=""; DEL_ONLY_NAMES=""; SKIPS=""; GONE=""; GONE_ARCH=""
for p in $DELETE_ONLY; do b=${p%%:*}; s=${p##*:}; t=$(tip "$b")
  if [ -z "$t" ]; then GONE="$GONE $b"; continue; fi
  if [ "$t" != "$s" ]; then SKIPS="$SKIPS $b"; log "left alone: $b (someone pushed to it since the check)"; continue; fi
  if ! git merge-base --is-ancestor "$s" "$DEPLOY_TIP"; then SKIPS="$SKIPS $b"; log "left alone: $b (it has commits $DEPLOY lacks)"; continue; fi
  DEL="$DEL $b"; DEL_ONLY_NAMES="$DEL_ONLY_NAMES $b"; LEASE="$LEASE --force-with-lease=refs/heads/$b:$s"
done
for p in $ARCHIVE; do b=${p%%:*}; s=${p##*:}; t=$(tip "$b")
  if [ -z "$t" ]; then GONE="$GONE $b"; GONE_ARCH="$GONE_ARCH $p"; continue; fi
  if [ "$t" != "$s" ]; then SKIPS="$SKIPS $b"; log "left alone: $b (someone pushed to it since the check)"; continue; fi
  ARCH="$ARCH $p"; ARCH_NAMES="$ARCH_NAMES $b"
done
MISSING_TAGS=""
if [ -n "$GONE_ARCH" ]; then
  load_tags
  for p in $GONE_ARCH; do b=${p%%:*}; s=${p##*:}; [ "$(tagged "$b")" = "$s" ] || MISSING_TAGS="$MISSING_TAGS $b"; done
fi
KEPT=""
for b in $(git for-each-ref --format='%(refname:strip=3)' refs/remotes/origin); do
  [ "$b" = HEAD ] && continue
  is_in "$b" $DEL $ARCH_NAMES || KEPT="$KEPT $b"
done
NA=$(count "$ARCH_NAMES"); ND=$(count "$DEL_ONLY_NAMES"); NK=$(count "$KEPT"); NS=$(count "$SKIPS")
NG=$(count "$GONE"); NM=$(count "$MISSING_TAGS")

log ""; log "Default branch: $DEFAULT"; log "Deploy branch, the one the PC syncs from: $DEPLOY"
log ""; log "Archive as a tag, then delete ($NA):"; for b in $ARCH_NAMES; do log "  $b"; done
log ""; log "Delete, every commit already in $DEPLOY ($ND):"; for b in $DEL_ONLY_NAMES; do log "  $b"; done
log ""; log "Keep ($NK):"; for b in $KEPT; do log "  $b"; done
if [ "$NG" -gt 0 ]; then log ""; log "Already gone from GitHub ($NG):"; for b in $GONE; do log "  $b"; done; fi
if [ "$NM" -gt 0 ]; then log ""; log "Gone, but with no archive tag at the checked commit ($NM):"; for b in $MISSING_TAGS; do log "  $b"; done; fi
if [ "$NS" -gt 0 ]; then log ""; log "Left alone because they changed since the check ($NS):"; for b in $SKIPS; do log "  $b"; done; fi

say ""
say "  Archive as a tag, then delete:  $(br $NA)"
say "  Delete (already in the deploy branch):  $(br $ND)"
say "  Keep:  $(br $NK)"
[ "$NG" -gt 0 ] && say "  Already gone from GitHub:  $(br $NG)"
[ "$NS" -gt 0 ] && say "  Left alone because someone pushed to them:  $(br $NS)"

if [ "$APPLY" != yes ]; then
  say ""
  if [ "$NA" -eq "$EXPECT_ARCHIVE" ] && [ "$ND" -eq "$EXPECT_DELETE" ] && [ "$NS" -eq 0 ]; then
    say "RESULT: LOOKS RIGHT. Nothing has changed yet. To go ahead, type:"
    say "  bash tools/archive-old-branches.sh --apply"
  elif [ $((NA + ND + NS + NM)) -eq 0 ]; then
    say "RESULT: ALREADY DONE. Every old branch is gone and every archive tag is on GitHub."
  else
    say "RESULT: DIFFERENT FROM THE CHECKED PLAN. Nothing has changed. Do not apply;"
    say "send Claude the file branch-cleanup-report.txt."
  fi
  open_report; exit 0
fi

if [ $((NA + ND)) -eq 0 ]; then
  say ""
  if [ $((NS + NM)) -eq 0 ]; then say "RESULT: ALREADY DONE. Every old branch is gone and every archive tag is on GitHub."
  else say "RESULT: NOTHING DELETED. What is left differs from the checked plan; send Claude the file branch-cleanup-report.txt."; fi
  open_report; exit 0
fi

load_tags; NEWTAGS=""
for p in $ARCH; do b=${p%%:*}; s=${p##*:}
  [ "$(tagged "$b")" = "$s" ] && continue
  git -c user.name=SEST-DEV -c user.email=contact@sest.io tag -f -a "archive/$b" "$s" \
    -m "Archived branch $b before removal ($(date '+%-d %b %Y'))" >> "$REPORT" 2>&1 \
    || stop "Could not make the archive tag for $b. No branch was deleted."
  NEWTAGS="$NEWTAGS refs/tags/archive/$b"
done
if [ -n "$NEWTAGS" ]; then
  log ""; log "Pushing the archive tags:"
  git push --atomic origin $NEWTAGS >> "$REPORT" 2>&1 || stop "GitHub did not take the archive tags. No branch was deleted."
fi
load_tags
for p in $ARCH; do b=${p%%:*}; s=${p##*:}
  [ "$(tagged "$b")" = "$s" ] || stop "The archive tag for $b is not on GitHub. No branch was deleted."
  DEL="$DEL $b"; LEASE="$LEASE --force-with-lease=refs/heads/$b:$s"
done
log ""; log "Deleting the branches:"
git push --atomic $LEASE origin --delete $DEL >> "$REPORT" 2>&1 \
  || stop "GitHub refused the deletion, so no branch was deleted. The archive tags are saved. Running the same command again is safe: a branch that changed is left alone."

LEFT=$(git ls-remote --heads origin 2>> "$REPORT" | sed 's#.*refs/heads/##')
for b in $DEL; do printf '%s\n' "$LEFT" | grep -qx "$b" && stop "$b is still on GitHub after the deletion."; done
log ""; log "Branches left on GitHub ($(count "$LEFT")):"; for b in $LEFT; do log "  $b"; done
log ""; log "Archive tags on GitHub:"; git ls-remote --tags origin 'refs/tags/archive/*' 2>> "$REPORT" | grep -v '\^{}' | sed 's#.*refs/tags/#  #' >> "$REPORT"
say ""
say "RESULT: DONE. $(br $NA) archived as tags and deleted, $(br $ND) deleted."
say "$(br $(count "$LEFT")) left on GitHub. You can delete the Codespace now."
open_report
