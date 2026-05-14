#!/usr/bin/env bash
#
# Install all skills in this repo as symlinks into:
#   ~/.claude/skills/<skill-name>   (Claude Code)
#   ~/.codex/skills/<skill-name>    (Codex CLI)
#
# Behavior:
# - Idempotent: rerunning replaces only existing symlinks; never overwrites real dirs.
# - Cross-machine portable: install paths are resolved from this script's location,
#   so cloning the repo to a different path on another machine just works after
#   running this script again.
# - Auto-discovery: every subdirectory containing a SKILL.md becomes a skill.
#
# Usage:
#   ./install.sh                  # install all skills to both agents
#   ./install.sh --claude-only    # only ~/.claude/skills
#   ./install.sh --codex-only     # only ~/.codex/skills
#   ./install.sh --dry-run        # show what would happen, no changes
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=0
WANT_CLAUDE=1
WANT_CODEX=1

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --claude-only) WANT_CODEX=0 ;;
    --codex-only) WANT_CLAUDE=0 ;;
    -h|--help)
      sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 1
      ;;
  esac
done

TARGETS=()
[ "$WANT_CLAUDE" -eq 1 ] && TARGETS+=("$HOME/.claude/skills")
[ "$WANT_CODEX" -eq 1 ] && TARGETS+=("$HOME/.codex/skills")

if [ ${#TARGETS[@]} -eq 0 ]; then
  echo "No targets selected." >&2
  exit 1
fi

log() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $*"
  else
    echo "$@"
  fi
}

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi
  "$@"
}

echo "Skill source: $HERE"
echo "Targets:      ${TARGETS[*]}"
[ "$DRY_RUN" -eq 1 ] && echo "(dry-run mode: no changes will be made)"
echo

installed=0
skipped=0
for skill_dir in "$HERE"/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  case "$name" in
    .*) continue ;;        # skip .git etc.
    node_modules) continue ;;
  esac
  [ -f "$skill_dir/SKILL.md" ] || continue

  for target_root in "${TARGETS[@]}"; do
    run mkdir -p "$target_root"
    target="$target_root/$name"

    if [ -L "$target" ]; then
      current="$(readlink "$target")"
      if [ "$current" = "$skill_dir" ]; then
        log "  = $target (already linked)"
        continue
      fi
      log "  ↻ relink $target (was → $current)"
      run rm "$target"
    elif [ -e "$target" ]; then
      log "  ⚠ $target exists and is not a symlink — skipping (move/delete it manually to relink)"
      skipped=$((skipped + 1))
      continue
    else
      log "  + $target"
    fi

    run ln -s "$skill_dir" "$target"
    installed=$((installed + 1))
  done
done

echo
echo "Done. Installed/refreshed: $installed link(s). Skipped: $skipped."
echo "Restart Claude Code / Codex CLI to pick up new skills."
