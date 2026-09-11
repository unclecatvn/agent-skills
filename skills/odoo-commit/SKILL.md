---
name: odoo-commit
description: >
  Guides Odoo-style commit creation following official Odoo git guidelines.
  Drafts `[TAG] module: short description` messages, checks whether to amend or
  create a new commit, stages files explicitly, commits via `git commit -F`,
  and keeps local history clean before PRs. Auto-invokes for commit-related
  requests in Odoo repositories and takes priority over generic commit skills.
---

## Workflow

1. Run `git diff --stat` and `git status --short` to see what changed, plus
   `git log -1 --oneline` (and `git log @{u}.. --oneline` if a remote-tracking
   branch exists) to see the last local commit and whether it's still unpushed.
2. If the change is a direct continuation or fix of that unpushed `HEAD` commit,
   skip drafting a new message and fold it in instead of creating a second commit
   for the same logical change:

   ```bash
   git add <file>
   git commit --amend --no-edit   # or drop --no-edit to also revise the message
   ```

   Otherwise, draft a new commit message.
3. Stage relevant files by name - never `git add -A` or `git add .`.
4. Write the commit message to a temporary file, then commit with `git commit -F`:

```bash
cat > /tmp/odoo-commit-message.txt <<'EOF'
[TAG] module: short description

Optional body line.
EOF
git commit -F /tmp/odoo-commit-message.txt
```

   Any equivalent temp-file flow is fine (for example, using PowerShell's
   `Set-Content` or another editor) as long as the final commit is created with
   `git commit -F <file>`.

5. Before opening a pull request, squash your own back-and-forth commits into one
   clean commit per logical change (per [OCA guidelines](https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests#mergesquash-your-own-commits)):
   the rest of the world doesn't need your intermediate "fix bug 1", "fix bug 2"
   history - only the final state and a clear summary. For a single trailing fix,
   `git commit --amend` (step 2) is usually enough; for folding several commits
   into one, use an interactive rebase instead:

   ```bash
   git rebase -i HEAD~N   # N = number of commits to fold
   ```

   Keep the first line as `pick` with the real `[TAG] module: description` message,
   mark the rest `fixup` (drop their messages) or `squash` (merge messages):

   ```
   pick 1949129 [IMP] module: Introduce feature A
   fixup d2cf643 Fix bug 1 of feature A
   fixup 42bd9e8 Fix bug 2 of feature A
   fixup 7f767d5 Fix bug 3 of feature A
   ```

   Either way, only rewrite commits that are still local/unpushed, or on a branch
   you alone own - never amend or rebase shared history without confirming with
   the user first.

6. Report the resulting commit hash and subject.

Do not bypass pre-commit hooks. If a hook fails, fix the issue,
re-stage the changes, and create the commit again.

## Format

```
[TAG] module: short description

Optional body explaining WHY, not what. What is visible in the diff.
Focus on motivation, constraints, and decisions made.

task-XXXX, opw-XXXXXX
```

## Subject Line Rules

- `[TAG] module: description` - tag in brackets, then module name, colon, space, description
- Target the **whole header** (`[TAG] module: description`) at about 50 characters for
  readability; 72 is a hard ceiling, not something to aim for
- Self-test: the header must read as a valid sentence after "if applied, this commit
  will `<header>`" - e.g. `[IMP] base: prevent to archive users linked to active
  partners` -> *"if applied, this commit will prevent to archive users linked to
  active partners"*
- Never use single, vague words like "bugfix" or "improvements" as the description -
  it must be self-explanatory and state the reason for the change
- Imperative mood: "add", "fix", "remove" - not "added", "fixes"
- No trailing period
- Module = technical module name (e.g. `hhc`, `plc`, `nhso_stddataset`, `imc`)
- Avoid touching multiple modules in one commit - split per module so each can be
  reverted independently. If truly unavoidable, list the modules or use `various`

## Tags

- `[FIX]` - bug fix; used in stable versions, also valid for recent dev bugs
- `[REF]` - refactoring: feature heavily rewritten
- `[ADD]` - adding new modules
- `[REM]` - removing resources: dead code, views, modules
- `[REV]` - reverting commits
- `[MOV]` - moving files (no content change; use git mv)
- `[REL]` - release commits: major/minor stable versions
- `[IMP]` - improvements: most incremental dev changes
- `[MERGE]` - merge commits / forward port of bug fixes
- `[CLA]` - signing Odoo Individual Contributor License
- `[I18N]` - translation file changes
- `[PERF]` - performance patches
- `[CLN]` - code cleanup
- `[LINT]` - linting passes

## Body Rules

- Skip body when subject is self-explanatory
- Include body for: non-obvious WHY, breaking changes, migration notes, task references
- **Explain WHY, not WHAT** - the diff already shows what changed. WHAT is only worth
  spelling out when a technical choice or trade-off was involved, and then explain
  WHY that choice was made
- Don't force brevity for its own sake: official Odoo guidance explicitly says not to
  hesitate being verbose when the reasoning deserves it. Every line should still earn
  its place - no restating the diff, no filler
- Wrap at 72 characters per line
- Reference task IDs at the end: `task-XXXX`, `opw-XXXXXX`, `Fixes #123`, `Closes #123`

## What Never Goes In

- "This commit does X" - the diff says what
- "I", "we", "now", "currently"
- AI attribution of any kind: `Co-Authored-By: Claude ...` trailers, `Generated with Claude Code`
  lines, session links. If the tooling injects one, remove it before committing
- Restating the file name or module when the subject already says it

## Pull Requests

- Title = the commit header (`[TAG] module: description`); one logical change per PR
- Body explains WHY and how it was verified (test command, screenshots for views); the diff shows WHAT
- No AI attribution anywhere in the body: no "Generated with" footer, no `Co-Authored-By`, no session links
- Do not add or edit author/reviewer lines; git already records the author

## Examples

Examples from the [official Odoo git guidelines](https://www.odoo.com/documentation/19.0/contributing/development/git_guidelines.html):

```
[REF] models: use `parent_path` to implement parent_store

This replaces the former modified preorder tree traversal (MPTT) with the
fields `parent_left`/`parent_right`[...]
```

```
[FIX] account: remove frenglish

[...]

Closes #22793
Fixes #22769
```

```
[FIX] website: remove unused alert div, fixes look of input-group-btn

Bootstrap's CSS depends on the input-group-btn element being the first/last
child of its parent. This was not the case because of the invisible and
useless alert.
```

Header-only, illustrating the "valid sentence" self-test:
```
[IMP] base: prevent to archive users linked to active partners
```
