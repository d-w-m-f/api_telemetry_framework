---
name: update-repo-map
description: >
  Reconciles the "Directory structure" tree in the root CLAUDE.md with the actual repository layout.
  Use this whenever a top-level file or directory was added, removed, or had its purpose change; before
  committing a structural change; or when asked to "update the repo map", "fix the directory structure in
  CLAUDE.md", "sync the repo map", or "check if CLAUDE.md is stale". Also trigger proactively if, while
  doing unrelated work, you notice CLAUDE.md's tree no longer matches what's on disk -- e.g. an "empty
  scaffold" note for a directory that now has real files in it.
---

# Update repo map

CLAUDE.md's "Directory structure" block is the fast, cheap alternative to an AI agent reading this whole
repo to find its way around: a hand-annotated tree, each line a path plus a one-line comment on what it is
and why it matters. It only earns that role if it's actually accurate — a stale annotation (a directory
marked "empty scaffold" that got filled in, a wrong file count, a description of behavior that no longer
holds) is worse than no map at all, because it actively misleads instead of just being silent. This skill's
only job is closing that gap on demand.

## Steps

1. **Read CLAUDE.md's current "Directory structure" code block in full.** Note the exact depth shown per
   branch — it's uneven on purpose (e.g. `src/sandbox/api/` currently goes 4 levels deep, `deployment/`
   goes 0). Match that same judgment call for new paths: go deep enough to be useful, not so deep it
   duplicates what a `docs/` file already explains in prose.

2. **Scan the real tree.** Use `Glob`/`Bash` (`find`/`ls`) at the depth the existing block implies, excluding
   the same things `.gitignore` excludes plus their usual siblings: `node_modules/`, `.git/`, `.angular/`,
   `__pycache__/`, `target/`, `dist/`, `*.pyc`, build artifacts. Don't invoke any heavier tooling — this repo
   is small enough that a plain scan is fast and complete.

3. **Diff the block against the scan, in both directions:**
   - Paths on disk with no line in the block → need a new line.
   - Paths in the block no longer on disk → the line must be removed.
   - Paths present in both → **don't just confirm they still exist. Check whether the annotation's actual
     claim still holds.** "Empty scaffold" for a directory that now has files, "one implementation" for a
     dir that now has two, a stale pointer to a doc that moved — these are the failures this skill exists
     to catch, and they don't show up by checking presence/absence alone. Open the path (or enough of it)
     to verify the claim, don't assume the old annotation is still true.

4. **Leave unchanged annotations exactly as they are.** Don't rewrite a line just because you're touching
   the file — only lines that are new, removed, or factually wrong get touched. Gratuitous rewording makes
   the diff noisy and harder for a human to review.

5. **For a new or corrected line, write one comment in the existing style** — terse, states what the path is
   and why it matters (not a restatement of the filename), occasionally pointing at another doc (e.g.
   `see spec/bootstrap.md`) instead of duplicating that doc's content inline. Read enough of the new path's
   actual contents to write something true, not a guess from the name alone.

6. **Edit the block in place**, keeping the loose column-alignment of the comments (`#`) that the existing
   block uses — eyeball the surrounding lines and match their spacing rather than applying a fixed column
   number, since the existing block isn't rigidly aligned to one.

7. **Report what changed** — a short list of paths added, removed, or corrected, and why. Don't silently
   edit and move on: the whole point is that drift here is easy to miss, so the fix should be visible too.
   If nothing was stale, say so explicitly rather than staying quiet — a clean scan is a useful answer too.
