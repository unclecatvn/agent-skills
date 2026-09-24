#!/usr/bin/env python3
"""Mechanical benchmark: odoo-workflow trace answers, old grep recipe vs bundled helper.

Runs each trace question the way the 1.0.19 skill told the agent to (Step 1 greps with a
ROOTS string, under zsh and under bash) and the way the current skill does (odoo_trace.py),
and scores both against hand-verified answers from the real source. Needs Odoo checkouts:

    python3 tests/bench_odoo_workflow.py --odoo 18.0=/path/odoo/18.0 --odoo 19.0=/path/odoo/19.0 \
        [--workspace /path/project ...]

Prints a Markdown report. Not part of `npm test`.
"""
import argparse
import os
import re
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELPER = os.path.join(ROOT, 'skills', 'odoo-workflow', 'scripts', 'odoo_trace.py')
PY_HIT = re.compile(r'^(.*?\.py)[:-]\d+[:-]')  # match lines path:NN:, -A context lines path-NN-
MAGIC = {'create_uid', 'create_date', 'write_uid', 'write_date'}

# (kind, args, truth, versions). truth: True = exists, False = does not exist.
CASES = [
    ('field', ('sale.order', 'commitment_date'), True, 'own field'),
    ('field', ('sale.order', 'delivery_date'), False, 'invented field'),
    ('field', ('res.partner', 'country_id'), True, 'annotated definition'),
    ('field', ('sale.order', 'access_url'), True, 'from portal.mixin'),
    ('field', ('sale.order', 'activity_ids'), True, 'from mail.activity.mixin'),
    ('field', ('sale.order', 'campaign_id'), True, 'redefined, comodel in utm.mixin'),
    ('field', ('event.booth', 'booth_category_id'), True, 'from prototype parent'),
    ('field', ('event.type.booth', 'partner_id'), False, 'only on the prototype copy'),
    ('field', ('sale.order.line', 'create_date'), True, 'magic, _log_access'),
    ('field', ('sale.report', 'create_date'), False, 'magic off, _auto = False'),
    ('field', ('res.partner', 'country'), False, 'invented hop'),
    ('xmlid', ('base', 'lang_vi_VN'), True, 'record in a data CSV'),
    ('xmlid', ('sales_team', 'group_sale_manager'), True, 'record in XML'),
    ('xmlid', ('sales_team', 'group_sale_admin'), False, 'invented group'),
    ('method', ('sale.order', 'message_post'), True, 'base def in mail.thread'),
    ('method', ('sale.order', '_action_confirm'), True, 'own hook'),
    ('method', ('sale.order', 'action_invented'), False, 'invented method'),
]


def sh(shell, cmd, cwd):
    t = time.time()
    p = subprocess.run([shell, '-c', cmd], cwd=cwd, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode, time.time() - t


def old_recipe(kind, args, shell, core):
    """The 1.0.19 Step 1 commands, verbatim, with ROOTS set as the skill said."""
    roots = 'ROOTS="addons odoo/addons"; '
    if kind == 'xmlid':
        module, name = args
        out, err, _, dt = sh(shell, roots + "grep -rn --include='*.xml' 'id=\"%s\"' $ROOTS" % name, core)
        return bool(out.strip()), len(out) + len(err), dt
    model = args[0].replace('.', r'\.')
    c = (roots +
         "{ grep -rnE --include='*.py' \"_name\\s*=\\s*([A-Za-z_]+\\s*=\\s*)?['\\\"]M['\\\"]\" $ROOTS; "
         "grep -rnE --include='*.py' \"_inherit\\s*=.*['\\\"]M['\\\"]\" $ROOTS; "
         "grep -rnE --include='*.py' -A12 \"_inherit\\s*=\\s*[[(][^])]*$\" $ROOTS | grep -E \"['\\\"]M['\\\"]\"; }"
         ).replace('M', model)
    out1, err1, _, dt1 = sh(shell, c, core)
    files = sorted({m.group(1) for m in map(PY_HIT.match, out1.splitlines()) if m})
    if kind == 'field' and args[1] in MAGIC:
        # 1.0.19 rule: magic fields exist on regular and transient models; no command checks _auto.
        return True, len(out1) + len(err1), dt1
    if not files:
        return False, len(out1) + len(err1), dt1
    quoted = ' '.join("'%s'" % f for f in files)
    if kind == 'field':
        c2 = "grep -nE \"^\\s+%s(\\s*:\\s*[A-Za-z_.]+)?\\s*=\\s*fields\\.\" %s /dev/null" % (args[1], quoted)
    else:
        c2 = "grep -nE \"^\\s+def %s\\(\" %s /dev/null" % (args[1], quoted)
    out2, err2, _, dt2 = sh(shell, c2, core)
    found = bool(out2.strip())
    if kind == 'method' and args[1] == 'message_post':
        found = 'mail/models/mail_thread.py' in out2  # the question is the base signature
    return found, len(out1) + len(err1) + len(out2) + len(err2), dt1 + dt2


def new_helper(kind, args, core, addons):
    base = ['python3', HELPER, '--odoo-root', core, '--addons', addons]
    if kind == 'xmlid':
        cmd = base + ['xmlid', '%s.%s' % args]
    else:
        cmd = base + [kind] + list(args)
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t
    if p.returncode == 2:
        return None, len(p.stdout) + len(p.stderr), dt
    found = p.returncode == 0
    if kind == 'method' and args[1] == 'message_post':
        found = found and 'mail/models/mail_thread.py' in p.stdout
    return found, len(p.stdout) + len(p.stderr), dt


def layout(workspace):
    """Old ROOTS fallback vs helper env from a real project directory."""
    out, _, _, _ = sh('/bin/bash', "find . -maxdepth 4 -name __manifest__.py -exec dirname {} \\; "
                      "| xargs -n1 dirname | sort -u", workspace)
    old_roots = out.split()
    old_core = any(os.path.isdir(os.path.join(workspace, r, 'base')) for r in old_roots)
    p = subprocess.run(['python3', HELPER, 'roots'], cwd=workspace, capture_output=True, text=True)
    new_roots = p.stdout.split() if p.returncode == 0 else []
    new_core = any(os.path.isfile(os.path.join(r, 'base', '__manifest__.py')) for r in new_roots)
    return old_roots, old_core, new_roots, new_core, p.returncode


def mark(v, truth):
    if v is None:
        return 'setup error'
    return ('ok' if v == truth else ('**false NOT FOUND**' if truth else '**invented**'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--odoo', action='append', required=True, help='VERSION=PATH')
    ap.add_argument('--workspace', action='append', default=[])
    a = ap.parse_args()
    zsh = shutil.which('zsh')
    print('# odoo-workflow trace benchmark\n')
    totals = {}
    for spec in a.odoo:
        ver, core = spec.split('=', 1)
        addons = '%s/addons,%s/odoo/addons' % (core, core)
        print('## Odoo %s\n' % ver)
        print('| Case | Truth | 1.0.19 zsh | 1.0.19 bash | helper | bytes bash / helper | s bash / helper |')
        print('|---|---|---|---|---|---|---|')
        for kind, args, truth, note in CASES:
            row = [f'{kind} `{" ".join(args)}` ({note})', 'exists' if truth else 'absent']
            res = {}
            for label, fn in (('zsh', lambda: old_recipe(kind, args, zsh, core) if zsh else (None, 0, 0)),
                              ('bash', lambda: old_recipe(kind, args, '/bin/bash', core)),
                              ('helper', lambda: new_helper(kind, args, core, addons))):
                res[label] = fn()
                t = totals.setdefault(label, [0, 0, 0, 0.0])
                t[0] += res[label][0] == truth
                t[1] += 1
                t[2] += res[label][1]
                t[3] += res[label][2]
            row += [mark(res[k][0], truth) for k in ('zsh', 'bash', 'helper')]
            row.append('%d / %d' % (res['bash'][1], res['helper'][1]))
            row.append('%.1f / %.1f' % (res['bash'][2], res['helper'][2]))
            print('| ' + ' | '.join(row) + ' |')
        print()
    print('## Totals\n')
    print('| Recipe | Correct | Output bytes | Seconds |')
    print('|---|---|---|---|')
    for label, (ok, n, b, s) in totals.items():
        print('| %s | %d/%d | %d | %.1f |' % (label, ok, n, b, s))
    if a.workspace:
        print('\n## Project layout: do the roots include core?\n')
        print('| Workspace | 1.0.19 fallback roots | core? | helper roots | core? |')
        print('|---|---|---|---|---|')
        for ws in a.workspace:
            o, oc, n, nc, rc = layout(ws)
            print('| %s | %s | %s | %s | %s |' % (os.path.basename(ws.rstrip('/')), ', '.join(o) or '-',
                  'yes' if oc else '**no**', ('%d roots' % len(n)) if n else 'exit %d' % rc, 'yes' if nc else '**no**'))


if __name__ == '__main__':
    main()
