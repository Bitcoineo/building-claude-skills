#!/usr/bin/env bash
# extract-commits.sh - Extract structured commit data from git history as JSON
#
# Usage:
#   extract-commits.sh [OPTIONS]
#
# Options:
#   --from <ref>      Start of range (tag, commit, branch). Default: latest tag or root
#   --to <ref>        End of range. Default: HEAD
#   --since <date>    Only include commits after this date (ISO 8601 or relative)
#   --until <date>    Only include commits before this date
#   --path <path>     Restrict to commits touching this path (monorepo support)
#   --include-merges  Include merge commits (excluded by default)
#
# Output:
#   JSON array of commit objects. Each object has:
#     hash, short_hash, author, date, subject, body, type, scope, is_breaking
#
# Exit codes:
#   0 - Success
#   1 - Not a git repository
#   2 - Invalid ref provided

set -euo pipefail

# --- Defaults ---
FROM_REF=""
TO_REF="HEAD"
SINCE=""
UNTIL=""
FILTER_PATH=""
INCLUDE_MERGES=false

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from)      FROM_REF="$2"; shift 2 ;;
    --to)        TO_REF="$2"; shift 2 ;;
    --since)     SINCE="$2"; shift 2 ;;
    --until)     UNTIL="$2"; shift 2 ;;
    --path)      FILTER_PATH="$2"; shift 2 ;;
    --include-merges) INCLUDE_MERGES=true; shift ;;
    -h|--help)
      sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
    *)
      echo "{\"error\": \"Unknown option: $1\"}" >&2
      exit 1
      ;;
  esac
done

# --- Validate environment ---
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo '{"error": "Not inside a git repository"}' >&2
  exit 1
fi

# --- Resolve FROM_REF ---
if [[ -z "$FROM_REF" ]]; then
  # Default: latest tag, or root commit if no tags exist
  FROM_REF=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD 2>/dev/null || echo "")
  if [[ -z "$FROM_REF" ]]; then
    echo '{"error": "No commits found in repository"}' >&2
    exit 1
  fi
fi

# --- Validate refs ---
for ref_name in FROM_REF TO_REF; do
  ref_val="${!ref_name}"
  if ! git rev-parse --verify "$ref_val" &>/dev/null; then
    echo "{\"error\": \"Invalid ref: $ref_val\"}" >&2
    exit 2
  fi
done

# --- Build git log command ---
LOG_ARGS=()

if [[ "$INCLUDE_MERGES" == false ]]; then
  LOG_ARGS+=(--no-merges)
fi

if [[ -n "$SINCE" ]]; then
  LOG_ARGS+=(--since="$SINCE")
fi

if [[ -n "$UNTIL" ]]; then
  LOG_ARGS+=(--until="$UNTIL")
fi

# Use ASCII record/unit separators to avoid delimiter collisions
# RS (0x1e) between commits, US (0x1f) between fields
FORMAT="%H%x1f%h%x1f%an%x1f%aI%x1f%s%x1f%b%x1e"

LOG_ARGS+=(--format="$FORMAT")

RANGE="${FROM_REF}..${TO_REF}"

PATH_ARGS=()
if [[ -n "$FILTER_PATH" ]]; then
  PATH_ARGS=(-- "$FILTER_PATH")
fi

# --- Extract and convert to JSON ---
if [[ ${#PATH_ARGS[@]} -gt 0 ]]; then
  RAW=$(git log "$RANGE" "${LOG_ARGS[@]}" "${PATH_ARGS[@]}" 2>/dev/null || echo "")
else
  RAW=$(git log "$RANGE" "${LOG_ARGS[@]}" 2>/dev/null || echo "")
fi

if [[ -z "$RAW" ]]; then
  echo "[]"
  exit 0
fi

# Parse commits into JSON using awk
echo "$RAW" | awk -v RS=$'\x1e' -v FS=$'\x1f' '
BEGIN {
  printf "["
  first = 1
}
NF >= 5 {
  hash = $1
  short_hash = $2
  author = $3
  date = $4
  subject = $5
  body = $6

  # Trim whitespace
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", hash)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", short_hash)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", author)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", date)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", subject)
  gsub(/^[[:space:]]+|[[:space:]]+$/, "", body)

  if (hash == "") next

  # Parse conventional commit: type(scope)!: description
  type = "other"
  scope = ""
  is_breaking = "false"

  # Check for breaking change indicator in conventional commit prefix
  if (subject ~ /^[a-z]+([(][^)]*[)])?[!]:/) {
    is_breaking = "true"
  }
  if (body ~ /BREAKING CHANGE:/ || body ~ /BREAKING-CHANGE:/) {
    is_breaking = "true"
  }

  # Extract type and scope from conventional commit format
  if (match(subject, /^[a-z]+([(][^)]*[)])?[!]?:/)) {
    match(subject, /^[a-z]+/)
    type = substr(subject, RSTART, RLENGTH)
    if (match(subject, /[(][^)]*[)]/)) {
      scope = substr(subject, RSTART+1, RLENGTH-2)
    }
  }

  # Escape JSON special characters
  gsub(/\\/, "\\\\", subject)
  gsub(/"/, "\\\"", subject)
  gsub(/\t/, "\\t", subject)
  gsub(/\\/, "\\\\", body)
  gsub(/"/, "\\\"", body)
  gsub(/\t/, "\\t", body)
  gsub(/\n/, "\\n", body)
  gsub(/\r/, "", body)
  gsub(/\\/, "\\\\", author)
  gsub(/"/, "\\\"", author)

  if (!first) printf ","
  first = 0

  printf "\n  {"
  printf "\"hash\":\"%s\",", hash
  printf "\"short_hash\":\"%s\",", short_hash
  printf "\"author\":\"%s\",", author
  printf "\"date\":\"%s\",", date
  printf "\"subject\":\"%s\",", subject
  printf "\"body\":\"%s\",", body
  printf "\"type\":\"%s\",", type
  printf "\"scope\":\"%s\",", scope
  printf "\"is_breaking\":%s", is_breaking
  printf "}"
}
END {
  printf "\n]\n"
}
'
