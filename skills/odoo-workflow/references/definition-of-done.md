# Definition of done - commands

Read this before reporting an Odoo change as done. Placeholders: `<python>`, `<odoo_root>`,
`<conf>` come from `odoo_trace env` (a `-` there means not found: ask, never guess); `<module>`
is the module changed; `<tmp>` is a scratch directory outside the repository. Write every value
out in full in each command - shell variables do not survive between tool calls. `odoo-bin`
below means `<python> <odoo_root>/odoo-bin`; give `odoo_trace` the same flags the `env` call
needed. The commands below were run on 18 and 19; 16/17 forms are unverified unless the pack
says otherwise.

## 1. Install and test on one throwaway database

```bash
odoo-bin -c <conf> -d scratch_<module> -i <module> --test-tags /<module> --http-port=<free_port> --workers=0 --max-cron-threads=0 --stop-after-init > <tmp>/<module>-install.log 2>&1; echo "exit=$?"
grep -E " (ERROR|CRITICAL) |failed, [0-9]+ error\(s\) of [0-9]+ tests" <tmp>/<module>-install.log
grep -E " WARNING " <tmp>/<module>-install.log | grep -E "<module>|odoo\.schema|access rules"
```

- `--test-tags /<module>` turns tests on by itself (18 and 19) and runs the module's standard
  tests, at install and post install.
- A test run always starts the HTTP server, `--no-http` or not. `<free_port>` is one where
  `lsof -nP -iTCP:<free_port> -sTCP:LISTEN` prints nothing. On a taken port (a dev server on
  8069) the run ends with `Address already in use` and `exit=1`, with no log line to grep.
  `--workers=0` because with workers (a conf `workers = N`) the tests run but no summary line
  is logged.
- Done means: `exit=0`, no `ERROR`/`CRITICAL` line, the summary line `0 failed, 0 error(s) of N
  tests` with N > 0, and every `WARNING` on the module explained (a `required` field on a table
  with rows, a model without access rules, a missing column, a missing manifest key). `of 0
  tests` (logged as a `WARNING`) means no test ran: write tests for the change.
- A `-u` run on a database where the module is not installed runs no test yet exits 0 with
  `of 0 tests`, which is why install and tests share one database.
- Demo data: use the project CI's setting. Unknown: no demo - 16-18 load demo by default, add
  `--without-demo=all`; 19 loads none by default (`--with-demo` turns it on).
- If `scratch_<module>` already exists from an earlier run, drop it first (section 6).
- Never pass `-i` or `-u` to a named database (the conf `db_name`, staging, dev, a customer
  copy) unless the user asks for it by name.

## 2. Upgrade (the Brief has a `migration` row)

Migration scripts run only on `-u` of a database whose installed version is lower than the
script's version, never on a fresh install. The script's version must not be higher than the
manifest `version` either: `migrations/1.1/` with the manifest still at `1.0` is skipped without
a word. Test on a copy of a database the user names that still has the previous module version:

```bash
odoo-bin db -c <conf> duplicate <source_db> upg_<module>
odoo-bin -c <conf> -d upg_<module> -u <module> --max-cron-threads=0 --stop-after-init > <tmp>/<module>-upgrade.log 2>&1; echo "exit=$?"
grep -E "Running upgrade|Deleting .*@ir\.model\.fields" <tmp>/<module>-upgrade.log
```

Check the log as in section 1. The last grep shows the scripts that ran (`Running upgrade`) and
the fields removed (`Deleting`): a removed stored field whose column still exists is dropped with
its data, silently and with `exit=0`, while a pre-script that renamed the column leaves nothing to
drop. A renamed or moved field therefore needs its `Running upgrade` line. Then check the moved
data with a query on `upg_<module>`, then drop it (section 6). `odoo-bin db duplicate` copies the
filestore and first terminates every connection to `<source_db>` (a server running on it loses
them); `createdb -T` copies no filestore and fails while anything is connected to the source. No
such database: say "upgrade not tested" in the PR body instead of claiming it.

## 3. Files that never load

```bash
odoo_trace unlisted <module>
```

Every file it lists must be added to the manifest (`data` in load order, the right `assets`
bundle, an `import` in `__init__.py`) or explained (a `data/template` CSV read by a chart
template, a file loaded from a hook).

## 4. i18n - whenever a string changed

Export the template from the scratch database, where the module is installed:

- 16-18: `mkdir -p <module_path>/i18n` first (the export does not create it: `FileNotFoundError`,
  exit 1), then `odoo-bin -c <conf> -d scratch_<module> --i18n-export=<module_path>/i18n/<module>.pot --modules=<module>`
  (`--modules` is required; the output path does not restrict the export).
- 19: `odoo-bin i18n export -c <conf> -d scratch_<module> <module>` writes
  `<module_path>/i18n/<module>.pot`.

Then refresh every `.po` the module ships, keeping its file name (`vi_VN.po` stays `vi_VN.po`):

```bash
msgmerge --quiet --update --no-fuzzy-matching --backup=none <module_path>/i18n/<lang>.po <module_path>/i18n/<module>.pot
msgfmt --check -o /dev/null <module_path>/i18n/<lang>.po
```

Plain `msgmerge --update` writes `#, fuzzy` guesses that Odoo loads as real translations and
leaves `.po~` backups. To export a language from the database instead, on 19 put the module
before `-l` (`-l` takes several values) and pin the file name with `-o`, after loading the
language: `odoo-bin i18n loadlang -c <conf> -d scratch_<module> -l vi_VN`, then
`odoo-bin i18n export -c <conf> -d scratch_<module> <module> -l vi_VN -o <module_path>/i18n/vi_VN.po`.
Without `-o` the file is named by the language's ISO code (`vi.po`). The export's `Ignoring not
found languages: vi_VN` warning is harmless (`-l vi` avoids it); before `loadlang` it stops
with `No valid language has been provided`.

## 5. Lint

Run the project's configured linter on the changed files when the repository has one (`ruff`
in `pyproject.toml` / `ruff.toml`, `.pre-commit-config.yaml`, `.pylintrc` with `pylint-odoo`).
None configured: skip and say so; do not impose one.

## 6. Drop the scratch databases

```bash
odoo-bin db -c <conf> drop scratch_<module>
```

The options go before the subcommand. `db drop` removes the filestore too; `dropdb` leaves
`<data_dir>/filestore/<db>` behind.

## 7. Security (also the Step 6 fallback when the review agent is not installed)

- [ ] Every new model has `ir.model.access.csv` rows; groups are the narrowest that work.
- [ ] Company-bound models have the company record rule; relational fields to company-bound
      comodels have `check_company=True`.
- [ ] Every `sudo()` / `with_user(SUPERUSER_ID)` has its Brief `security` row: what it bypasses
      and the access check, token, or group check done before it. Bound results end in `_sudo`
      and never leave the method.
- [ ] Controllers: `auth=` is the narrowest that works; `csrf=False` only with the caller's
      authentication stated in the PR body; no record reached by id without an access check.
- [ ] `cr.execute` uses parameters or `SQL()` (17+), never string formatting of input.
- [ ] Fields with sensitive data carry `groups=`.

## 8. Hygiene - per git repository

A workspace can hold several repositories (for example `erp`, `erp-external`, `erp-internal`).
List the repositories the change touched, then run every check with `git -C <repo>`:

```bash
for f in <changed files>; do git -C "$(dirname "$f")" rev-parse --show-toplevel; done | sort -u
git -C <repo> diff HEAD -U0 | grep -E '^\+[^+]' | grep -inE 'ponytail:|Co-Authored-By|Generated with'
git -C <repo> ls-files -z --others --exclude-standard | (cd <repo> && xargs -0 grep -inE 'ponytail:|Co-Authored-By|Generated with' /dev/null)
git -C <repo> diff <base>...HEAD -U0 | grep -E '^\+[^+]' | grep -inE 'ponytail:|Co-Authored-By|Generated with'
git -C <repo> log <base>..HEAD --format=%B | grep -inE 'Co-Authored-By|Generated with'
```

Only added lines are checked, so deleting a forbidden line never trips it. `-i` because git's
own trailer spelling is `Co-authored-by`. Every check must print nothing. Any message from `git`
itself is a failed check, not a pass: `fatal: not a git repository`, or from `git diff` outside a
repository `warning: Not a git repository` and a usage text. The last two lines cover work
already committed on the branch (`<base>` is the branch the PR targets). The PR body follows the
same rule: WHY plus test evidence, no generated-with footer.
