#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Telepact site build script
#
# This script:
#   1. Copies doc/ and doc/learn-by-example/ into the MkDocs docs directory
#   2. Rewrites relative links that point outside doc/ to GitHub URLs
#   3. Runs mkdocs build to produce the static site in site/site/
#
# Usage:
#   cd site && bash build.sh          # full build
#   cd site && bash build.sh serve    # live preview on localhost:8000
# ---------------------------------------------------------------------------
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="${SITE_DIR}/docs"

GITHUB_BASE="https://github.com/Telepact/telepact"
GITHUB_BLOB="${GITHUB_BASE}/blob/main"
GITHUB_TREE="${GITHUB_BASE}/tree/main"

# ── 1. Clean previous copied files ────────────────────────────────────────
rm -rf "${DOCS_DIR}/guide" "${DOCS_DIR}/learn-by-example"
mkdir -p "${DOCS_DIR}/guide" "${DOCS_DIR}/learn-by-example"

# ── 2. Copy doc/ into docs/guide/ ─────────────────────────────────────────
for f in "${REPO_ROOT}"/doc/*.md; do
    cp "$f" "${DOCS_DIR}/guide/"
done

# Copy learn-by-example files
for f in "${REPO_ROOT}"/doc/learn-by-example/*.md; do
    cp "$f" "${DOCS_DIR}/learn-by-example/"
done

# Rename README.md → index.md for MkDocs
if [ -f "${DOCS_DIR}/learn-by-example/README.md" ]; then
    mv "${DOCS_DIR}/learn-by-example/README.md" "${DOCS_DIR}/learn-by-example/index.md"
fi

# ── 3. Rewrite links in guide/ files ──────────────────────────────────────
# Links from doc/*.md that reference files outside doc/ (e.g. ../lib/...)
# are rewritten to full GitHub URLs.

rewrite_guide_links() {
    local file="$1"

    # Rewrite ../lib/*/README.md → GitHub blob link
    sed -i "s|\.\./lib/\([^)]*\)|${GITHUB_BLOB}/lib/\1|g" "$file"

    # Rewrite ../sdk/*/README.md → GitHub blob link
    sed -i "s|\.\./sdk/\([^)]*\)|${GITHUB_BLOB}/sdk/\1|g" "$file"

    # Rewrite ../example/*/README.md and ../example/ → GitHub link
    sed -i "s|\.\./example/\([^)]*\)|${GITHUB_BLOB}/example/\1|g" "$file"
    sed -i "s|\.\./example/\?)|${GITHUB_TREE}/example)|g" "$file"

    # Rewrite ../common/* → GitHub blob link
    sed -i "s|\.\./common/\([^)]*\)|${GITHUB_BLOB}/common/\1|g" "$file"

    # Rewrite raw.githubusercontent.com links to stay as-is (already absolute)
    # no-op, they're fine
}

for f in "${DOCS_DIR}"/guide/*.md; do
    rewrite_guide_links "$f"
done

# ── 4. Rewrite links in learn-by-example/ files ──────────────────────────
# Links like ../faq.md → ../guide/faq.md
# Links like ../extensions.md → ../guide/extensions.md

rewrite_tutorial_links() {
    local file="$1"

    # ../somefile.md → ../guide/somefile.md (for files that were in doc/)
    sed -i 's|\.\./\([a-z_-]*\.md\)|../guide/\1|g' "$file"
}

for f in "${DOCS_DIR}"/learn-by-example/*.md; do
    rewrite_tutorial_links "$f"
done

# ── 5. Build or serve ─────────────────────────────────────────────────────
cd "${SITE_DIR}"

if [ "${1:-}" = "serve" ]; then
    echo "Starting MkDocs dev server…"
    python -m mkdocs serve
else
    echo "Building static site…"
    python -m mkdocs build
    echo "Done — output in ${SITE_DIR}/site/"
fi
