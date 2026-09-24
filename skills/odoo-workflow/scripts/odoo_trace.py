#!/usr/bin/env python3
"""Trace the Python side of an Odoo project from source: models, fields, methods, xmlids,
module load order and files that never load. Stdlib only, Python >= 3.8, read-only.

Output is file:line with absolute paths; every command ends with a 'VERDICT:' line
('roots' prints it on stderr so its stdout stays a clean path list).
Exit codes: 0 found, 1 NOT FOUND, 2 setup error (roots or core not located, bad args) or answer unknown.

Runtime (see 'env'): flags > .claude/odoo.json > .claude/launch.json (odoo-bin config)
> the one *.conf whose addons_path covers cwd, in the nearest ancestor (from the parent up) or its
subdirs. Version: --version, else odoo/release.py; a version in .claude/odoo.json or .odoo-version
that disagrees with release.py is a setup error.
Long lists are capped for hub models (model: 15 extensions, 15 copies; method: 10 hooks per def;
unlisted: one line per directory of more than 5 files); --all lifts the caps.
"""
import argparse
import ast
import bisect
import configparser
import csv
import difflib
import glob
import json
import os
import re
import sys
from xml.parsers import expat

SKIP_DIRS = {'.git', 'node_modules', 'static', 'i18n', 'i18n_extra', '__pycache__', 'tests', 'migrations', 'upgrades'}
KINDS = {'Model': 'Model', 'TransientModel': 'Transient', 'AbstractModel': 'Abstract'}
RELATIONAL = ('Many2one', 'One2many', 'Many2many')
FIELD_TYPES = RELATIONAL + ('Boolean', 'Integer', 'Float', 'Monetary', 'Char', 'Text', 'Html', 'Date', 'Datetime',
                            'Binary', 'Image', 'Selection', 'Reference', 'Many2oneReference', 'Json', 'Properties')
# MetaModel magic fields: 18.0 models.py:278-293, 19.0 orm/models.py:472-473 (BaseModel) and 285-292
MAGIC = {'id': 'Id', 'display_name': 'Char', 'create_uid': 'Many2one', 'create_date': 'Datetime',
         'write_uid': 'Many2one', 'write_date': 'Datetime'}
LOG_FIELDS = tuple(MAGIC)[2:]
SUBCLASS = {'Image': 'Binary', 'Reference': 'Selection', 'Many2oneReference': 'Integer'}  # field class bases
CAP = 15  # lines per list on hub models unless --all
DATA_KEYS = ('data', 'demo', 'init_xml', 'update_xml', 'demo_xml')
ASSET_EXT = ('.js', '.css', '.scss', '.sass', '.less', '.xml')  # ASSET_EXTENSIONS, odoo/tools/constants.py
XMLID_TAGS = {'record', 'template', 'menuitem', 'asset', 'report', 'act_window'}  # tools/convert.py _tags (+ pre-17)
IMPORT_RX = re.compile(r'^[ \t]*((?:from(?:[ \t]+[\w.]+|[ \t]*\.[\w.]*)[ \t]+import[ \t]+'
                       r'(?:\([^)]*\)|.*?(?:\\\n.*?)*$))|import[ \t]+odoo\.addons\..*$)', re.M)
E = {}  # resolved runtime: version, major, odoo_root, conf, python, dev_db, roots, src (where each came from)
MODS, SHADOWED, TEXT, CLS, BY_MODEL, MANI, IMPORTS, DEPTH, CONSTS, ID2C = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
PYCLS, IMPS = {}, {}  # per file: top-level ClassDefs by name; names bound by a top-level `from X import`


class SetupError(Exception):
    pass


def read(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def norm(path, base):
    return os.path.realpath(os.path.join(base, os.path.expanduser(os.path.expandvars(path.strip()))))


def up_files(rel):
    d = os.path.realpath(os.getcwd())
    while True:
        if os.path.isfile(os.path.join(d, rel)):
            yield os.path.join(d, rel)
        if os.path.dirname(d) == d:
            return
        d = os.path.dirname(d)


def read_conf(path):
    cp = configparser.RawConfigParser(strict=False)
    try:
        cp.read(path)
        opts = dict(cp.items('options')) if cp.has_section('options') else {}
    except (configparser.Error, UnicodeDecodeError):
        return {}
    return {k: v for k, v in opts.items() if v not in ('False', 'false', 'None', '')}


def conf_addons(path, base=None):
    """addons_path of a conf. Odoo resolves relative entries against the directory odoo-bin runs in
    (18.0 odoo/tools/config.py:549-551, 19.0 config.py:790 _normalize): BASE when known, else the conf's
    directory, a guess 'env' reports."""
    return [norm(p, base or os.path.dirname(path)) for p in read_conf(path).get('addons_path', '').split(',')
            if p.strip()]


def covers(addons, cwd):
    return any(a == cwd or a.startswith(cwd + os.sep) or cwd.startswith(a + os.sep) for a in addons)


def argval(argv, *names):
    for i, a in enumerate(argv):
        for n in names:
            if a == n and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith(n + '='):
                return a[len(n) + 1:]
    return None


def launch_odoo(path, cwd):
    """(source, settings) of the first launch.json configuration running odoo-bin whose addons cover cwd."""
    try:
        cfgs = json.loads(read(path)).get('configurations') or []
    except ValueError:
        return None
    base = os.path.dirname(os.path.dirname(path))
    for cfg in cfgs:
        argv = [str(a).replace('${workspaceFolder}', base)
                for a in [cfg.get('runtimeExecutable') or ''] + (cfg.get('runtimeArgs') or cfg.get('args') or [])]
        bins = [a for a in argv if os.path.basename(a) == 'odoo-bin']
        if not bins:
            continue
        run_dir = norm(str(cfg.get('cwd') or '.').replace('${workspaceFolder}', base), base)
        conf, addons = argval(argv, '-c', '--config'), argval(argv, '--addons-path')
        conf = conf and norm(conf, run_dir)
        addons = [norm(p, run_dir) for p in addons.split(',') if p.strip()] if addons else None
        if not covers(addons or (conf and conf_addons(conf, run_dir)) or [], cwd):
            E.setdefault('notes', []).append('%s config "%s": addons_path does not cover cwd, skipped'
                                             % (path, cfg.get('name', '?')))
            continue
        pys = [a for a in argv[:2] if os.path.basename(a).startswith('python')]
        return 'config "%s"' % cfg.get('name', '?'), {
            'odoo_root': os.path.dirname(norm(bins[0], run_dir)), 'conf': conf, 'run_dir': conf and run_dir,
            'addons': addons, 'python': pys[0] if pys else None, 'dev_db': argval(argv, '-d', '--database')}
    return None


def series(value, source):
    """'18.0' / 'saas~17.4' from a version string such as '18', '18.0' or 'saas~17.4'."""
    m = re.match(r'\s*(saas~)?(\d+)(?:\.(\d+))?\s*$', str(value))
    if not m:
        raise SetupError('%s: %r is not an Odoo version such as 18.0' % (source, value))
    return '%s%s.%s' % (m.group(1) or '', m.group(2), m.group(3) or 0)


def resolve(args):
    cwd, src, claims = os.path.realpath(os.getcwd()), {}, []

    def put(key, value, source):
        if value and key not in E:
            E[key], src[key] = value, source
    put('odoo_root', args.odoo_root and norm(args.odoo_root, cwd), 'flag')
    put('conf', args.conf and norm(args.conf, cwd), 'flag')
    put('addons', args.addons and [norm(p, cwd) for p in args.addons.split(',') if p.strip()], 'flag')
    put('version', args.odoo_version and series(args.odoo_version, '--version'), 'flag')
    for p in up_files(os.path.join('.claude', 'odoo.json')):
        try:
            data = json.loads(read(p))
        except ValueError as e:
            raise SetupError('%s: %s' % (p, e)) from None
        base, py = os.path.dirname(os.path.dirname(p)), data.get('python')
        claims += [(p, series(data['odoo_version'], p))] if data.get('odoo_version') else []
        for k in ('odoo_root', 'conf'):
            put(k, data.get(k) and norm(data[k], base), p)
        put('python', py and (norm(py, base) if os.sep in py else py), p)
        put('dev_db', data.get('dev_db'), p)
        put('addons', data.get('addons') and [norm(a, base) for a in data['addons']], p)
        break
    for p in up_files('.odoo-version'):  # the version pin of earlier releases of this skill
        claims.append((p, series(next((x for x in read(p).splitlines() if x.strip()[:1] not in ('', '#')), ''), p)))
        break
    for p in up_files(os.path.join('.claude', 'launch.json')):
        got = launch_odoo(p, cwd)
        if got:
            for k, v in got[1].items():
                put(k, v, '%s %s' % (p, got[0]))
            break
    d = os.path.dirname(cwd)
    while 'conf' not in E and not ('odoo_root' in E and 'addons' in E):
        cands = sorted(set(glob.glob(os.path.join(d, '*.conf')) + glob.glob(os.path.join(d, '*', '*.conf'))))
        hits = [c for c in cands if covers(conf_addons(c), cwd)]
        if len(hits) > 1:
            raise SetupError('several confs cover %s:\n  %s\npin one: write .claude/odoo.json {"conf": "<one of them>"}'
                             % (cwd, '\n  '.join(hits)))
        put('conf', hits and hits[0], 'discovered (the one *.conf whose addons_path covers cwd)')
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    if 'conf' in E:
        opts, cdir = read_conf(E['conf']), os.path.dirname(E['conf'])
        run_dir = E['run_dir'] if src.get('run_dir') == src['conf'] else None
        if not run_dir and any(not os.path.isabs(os.path.expanduser(os.path.expandvars(p.strip())))
                               for p in opts.get('addons_path', '').split(',') if p.strip()):
            E.setdefault('notes', []).append(
                'relative addons_path entries of %s resolved against its directory; Odoo resolves them against '
                'the directory odoo-bin runs in' % E['conf'])
        put('addons', conf_addons(E['conf'], run_dir), 'conf addons_path')
        put('dev_db', opts.get('db_name'), 'conf db_name')
        put('data_dir', opts.get('data_dir') and norm(opts['data_dir'], run_dir or cdir), 'conf data_dir')
        for d in [cdir] + [os.path.dirname(a) for a in E.get('addons') or []]:
            if os.path.isfile(os.path.join(d, 'odoo-bin')) or os.path.isfile(os.path.join(d, 'odoo', 'release.py')):
                put('odoo_root', d, 'conf (%s)' % ('its directory' if d == cdir else 'parent of an addons_path entry'))
                break
    if 'odoo_root' not in E:
        raise SetupError('Odoo core not located. Tried: --odoo-root/--conf flags, .claude/odoo.json, '
                         '.claude/launch.json (odoo-bin config), a *.conf covering %s in an ancestor or its subdirs.%s'
                         '\nWrite <project>/.claude/odoo.json: {"odoo_version": "18.0", "odoo_root": "/path/to/odoo", '
                         '"conf": "/path/to/odoo.conf"}' % (cwd, ''.join('\n' + n for n in E.get('notes', []))))
    release = os.path.join(E['odoo_root'], 'odoo', 'release.py')
    m = os.path.isfile(release) and re.search(r'''^version_info\s*=\s*\(\s*['"]?((?:saas~)?\d+)['"]?\s*,\s*(\d+)''',
                                              read(release), re.M)
    if not m:
        raise SetupError('%s is not an Odoo checkout (no version_info in odoo/release.py)' % E['odoo_root'])
    core = '%s.%s' % m.groups()
    bad = ['%s in %s' % (v, p) for p, v in claims if v != core]
    if bad and 'version' not in E:
        raise SetupError('version sources disagree: %s, but %s in %s. Ask the user which one is right and fix '
                         'the other.' % ('; '.join(bad), core, release))
    if E.get('version', core) != core:
        E.setdefault('notes', []).append('--version %s overrides %s in %s' % (E['version'], core, release))
    for p, v in claims + [(release, core)]:
        put('version', v, p)
    E['major'] = int(re.match(r'(?:saas~)?(\d+)', E['version']).group(1))
    E['src'] = src
    build_roots()


def has_modules(d):
    """19.0 config.py:777-784 _is_addons_path: some subdir holds __init__.py and __manifest__.py."""
    return any(all(os.path.isfile(os.path.join(d, e, f)) for f in ('__init__.py', '__manifest__.py'))
               for e in os.listdir(d))


def build_roots():
    """Addons roots in odoo.addons.__path__ order; the first root holding a module wins.
    18.0 module.py:121-140: the package's own odoo/addons first (odoo/addons/__init__.py extend_path),
    then addons_data_dir, then addons_path; config.py:539-547 defaults addons_path to odoo/addons,
    <root>/addons when unset. 19.0 module.py:141-153: odoo/addons first ("already present"), data dir,
    addons_path (config.py:788-802 expands globs, skips non-addons dirs; 18 takes entries as they are),
    then addons_community_dir = <root>/addons (config.py:1000-1002) when missing."""
    root, major = E['odoo_root'], E['major']
    core, community = os.path.join(root, 'odoo', 'addons'), os.path.join(root, 'addons')
    roots, E['skipped'] = [(core, 'odoo/addons (always first)')], []
    data_dir = E.get('data_dir') or (
        os.path.expanduser('~/Library/Application Support/Odoo') if sys.platform == 'darwin' else
        os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'Odoo'))
    dd = os.path.join(data_dir, 'addons', E['version'])
    if os.path.isdir(dd) and os.access(dd, os.R_OK) and has_modules(dd):
        roots.append((dd, 'data_dir addons'))
    addons = E.get('addons')
    if addons is None and major < 19:
        addons, E['src']['addons'] = [core, community], 'Odoo default (no addons_path)'
    for a in addons or []:
        for p in sorted(p for p in glob.glob(a) if os.path.isdir(p) and has_modules(p)) \
                if major >= 19 and re.search(r'[*?[]', a) else [a]:
            if not os.path.isdir(p) or (major >= 19 and not has_modules(p)):
                E['skipped'].append(p)
            elif p not in [r for r, _ in roots]:
                roots.append((p, 'addons_path'))
    if major >= 19 and community not in [r for r, _ in roots] and os.path.isdir(community):
        roots.append((community, 'addons_community_dir, auto-added by Odoo 19'))
    E['roots'] = roots
    names = ('__manifest__.py',) if major >= 19 else ('__manifest__.py', '__openerp__.py')
    for r, _ in roots:
        for e in sorted(os.listdir(r)):
            if any(os.path.isfile(os.path.join(r, e, n)) for n in names):
                if e in MODS:
                    SHADOWED.setdefault(e, []).append(os.path.join(r, e))
                else:
                    MODS[e] = os.path.join(r, e)
    if 'base' not in MODS:
        raise SetupError('core not located: no root holds base/__manifest__.py (roots: %s); never write NOT FOUND '
                         'against custom roots only' % ', '.join(r for r, _ in roots))


# ---------------------------------------------------------------- modules, manifests, load order

def manifest(mod):
    if mod not in MANI:
        path = os.path.join(MODS.get(mod, ''), '__manifest__.py')
        if not os.path.isfile(path):
            path = path.replace('__manifest__.py', '__openerp__.py')
        try:
            MANI[mod] = ast.literal_eval(read(path)) if os.path.isfile(path) else {}
        except (ValueError, SyntaxError) as e:
            print('UNPARSED %s: %s' % (path, e))
            MANI[mod] = {}
    return MANI[mod]


def depends(mod):
    deps = list(manifest(mod).get('depends') or [])
    return ['base'] if E['major'] >= 19 and not deps and mod != 'base' else deps  # 19.0 module.py:436-440


def depth(mod, stack=()):
    """18.0 graph.py:31-41, 151-153: depth = max(depth of depends) + 1, 0 without depends.
    19.0 module_graph.py:175-181: same, but a 'test_*' module takes the depth of its last dependency."""
    if mod not in DEPTH:
        deps = [d for d in depends(mod) if d in MODS and d not in stack]
        if E['major'] >= 19 and mod.startswith('test_') and deps:
            DEPTH[mod] = depth(max(deps, key=lambda d: (depth(d, stack + (mod,)), order_name(d))), stack + (mod,))
        else:
            DEPTH[mod] = max(depth(d, stack + (mod,)) for d in deps) + 1 if deps else 0
    return DEPTH[mod]


def order_name(mod):
    deps = [d for d in depends(mod) if d in MODS]
    if E['major'] >= 19 and mod.startswith('test_') and deps:  # 19.0 module_graph.py:166-172
        return order_name(max(deps, key=lambda d: (depth(d), order_name(d)))) + ' ' + mod
    return mod


def load_key(mod):
    """base loads alone first (18.0 loading.py:407-409; 19.0 module_graph.py:184-186 phase 0), then 18.0
    graph.py:109-116 iterates by (depth, name) and 19.0 module_graph.py:224-225 by (phase, depth, order_name).
    Assumes a plain load: during -i/-u, modules being installed load in a later pass."""
    return (-1, 0, '') if mod == 'core' else (0 if mod == 'base' else 1, depth(mod), order_name(mod))


def closure(mod):
    """(modules MOD depends on, itself included; {missing dependency: [modules requiring it]})."""
    seen, missing, todo = set(), {}, [mod]
    while todo:
        m = todo.pop()
        if m not in seen:
            seen.add(m)
            for d in depends(m):
                if d in MODS:
                    todo.append(d)
                else:
                    missing.setdefault(d, []).append(m)
    return seen, missing


def dotted_files(base, dotted):
    """(files Python runs to import DOTTED from package dir BASE: each package __init__.py on the way,
    then the module; the path DOTTED names)."""
    out = []
    for part in dotted.split('.') if dotted else []:
        base = os.path.join(base, part)
        f = next((f for f in (base + '.py', os.path.join(base, '__init__.py')) if os.path.isfile(f)), None)
        if f:
            out.append(f)
    return out, base


def import_base(path, node):
    """(package dir, dotted rest) where ImportFrom NODE of PATH starts; None for a name outside the roots."""
    base, dotted = os.path.dirname(path), node.module or ''
    for _ in range(node.level - 1):
        base = os.path.dirname(base)
    parts = dotted.split('.')
    if node.level:
        return base, dotted
    return (MODS[parts[2]], '.'.join(parts[3:])) if parts[:2] == ['odoo', 'addons'] and len(parts) > 2 \
        and parts[2] in MODS else None


def imports(mod, others=False):
    """{path: import rank} of the .py files of MOD that its __init__.py chain imports, in execution order;
    with OTHERS, also those that other modules import as odoo.addons.MOD.*"""
    if (mod, others) in IMPORTS:
        return IMPORTS[mod, others]
    mdir, order, pkg = MODS[mod], {}, 'odoo.addons.%s' % mod

    def visit(path):
        if path not in order and path.startswith(mdir + os.sep):
            order[path] = len(order)
            follow(path)

    def follow(path):
        for m in IMPORT_RX.finditer(TEXT[path][1] if path in TEXT else read(path)):
            if not (re.match(r'from\s*\.', m.group(1)) or pkg in m.group(1)):
                continue
            try:
                nodes = ast.parse(m.group(1)).body
            except SyntaxError:
                continue
            for node in nodes:
                if isinstance(node, ast.ImportFrom):
                    start = import_base(path, node)
                    found, p = dotted_files(*start) if start else ([], None)
                    for f in found + [f for alias in node.names if p for f in dotted_files(p, alias.name)[0]]:
                        visit(f)
                else:
                    for alias in node.names:
                        for f in dotted_files(mdir, alias.name[len(pkg) + 1:])[0] \
                                if alias.name.startswith(pkg + '.') else []:
                            visit(f)
    if os.path.isfile(os.path.join(mdir, '__init__.py')):
        visit(os.path.join(mdir, '__init__.py'))
    for path in files_with(pkg) if others else []:
        if not path.startswith(mdir + os.sep):
            follow(path)
    IMPORTS[mod, others] = order
    return order


def module_files(mod, exts, skip=SKIP_DIRS):
    for dp, dns, fns in os.walk(MODS[mod]):
        dns[:] = sorted(d for d in dns if d not in skip)
        for f in sorted(fns):
            if f.endswith(exts):
                yield os.path.join(dp, f)


# ---------------------------------------------------------------- model index (AST)

def texts():
    if not TEXT:
        for mod in MODS:
            for p in module_files(mod, '.py'):
                if not p.endswith('__manifest__.py'):
                    TEXT[p] = (mod, read(p))
        # one string holding every source: a needle costs one C-level scan instead of a Python loop
        E['paths'], E['starts'], pos = list(TEXT), [], 0
        for p in E['paths']:
            E['starts'].append(pos)
            pos += len(TEXT[p][1]) + 1
        E['big'] = '\0'.join(TEXT[p][1] for p in E['paths'])
    return TEXT


def files_with(needle):
    texts()
    big, starts, out, i = E['big'], E['starts'], [], E['big'].find(needle)
    while i != -1:
        k = bisect.bisect_right(starts, i) - 1
        out.append(E['paths'][k])
        i = big.find(needle, starts[k + 1]) if k + 1 < len(starts) else -1
    return out


def value(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError, TypeError):
        if isinstance(node, (ast.List, ast.Tuple)):
            return [e.value for e in node.elts if isinstance(e, ast.Constant)]
        return None


def eff_name(cls, attrs):
    """18.0 models.py:246-250: _name, else a one-item _inherit, else the class name as is.
    19.0 orm/models.py:241-248: _name, else a str _inherit, else derived from the class name."""
    inherit = attrs.get('_inherit', (None,))[0]
    if E['major'] >= 19:
        name = attrs['_name'][0] if '_name' in attrs else (inherit if isinstance(inherit, str) else None)
        return name or re.sub(r'(?<=[^_])([A-Z])', r'.\1', cls).lower()
    if '_name' in attrs:
        return attrs['_name'][0] or cls
    inh = [inherit] if isinstance(inherit, str) else list(inherit or ())
    return inh[0] if len(inh) == 1 else cls


def base_names(node):
    return [b.attr if isinstance(b, ast.Attribute) else getattr(b, 'id', '') for b in node.bases]


def class_info(node, path, mod):
    attrs = {}
    for st in node.body:
        if isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None:
            for t in st.targets if isinstance(st, ast.Assign) else [st.target]:
                if getattr(t, 'id', None) in ('_name', '_inherit', '_inherits', '_auto', '_log_access', '_register'):
                    attrs[t.id] = (value(st.value), st.lineno)
    bases = base_names(node)
    kind = next((KINDS[b] for b in bases if b in KINDS), None)
    if (not kind and '_name' not in attrs and '_inherit' not in attrs) or attrs.get('_register', (True,))[0] is False:
        return None
    raw = attrs.get('_inherit', (None,))[0]
    inherit = [raw] if isinstance(raw, str) else [i for i in raw or () if isinstance(i, str)]
    name = eff_name(node.name, attrs)
    c = {'path': path, 'line': node.lineno, 'module': mod, 'cls': node.name, 'kind': kind or '?', 'name': name,
         'inherit': inherit, 'inherits': attrs.get('_inherits', ({},))[0] or {}, 'attrs': attrs, 'node': node,
         'role': 'extend' if name in inherit else 'define', 'unimported': path not in imports(mod)}
    ID2C[id(c)] = c
    return c


def classes(path):
    if path not in CLS:
        mod, text = TEXT[path]
        try:
            body = ast.parse(text, path).body
        except (SyntaxError, ValueError) as e:
            print('UNPARSED %s: %s' % (path, getattr(e, 'msg', e)))
            body = []
        CONSTS[path] = {t.id: st.value for st in body if isinstance(st, ast.Assign)
                        for t in st.targets if isinstance(t, ast.Name)}
        PYCLS[path] = {st.name: st for st in body if isinstance(st, ast.ClassDef)}
        IMPS[path] = {a.asname or a.name: (st, a.name) for st in body if isinstance(st, ast.ImportFrom)
                      for a in st.names}
        out, todo = [], list(body)
        while todo:
            st = todo.pop(0)
            if isinstance(st, ast.ClassDef):
                out += [c for c in [class_info(st, path, mod)] if c]
            elif isinstance(st, (ast.If, ast.Try)):
                todo[:0] = st.body + st.orelse + [s for h in getattr(st, 'handlers', []) for s in h.body]
        CLS[path] = out
    return CLS[path]


def cls_key(c):
    return load_key(c['module']), imports(c['module']).get(c['path'], 1 << 20), c['line']


def by_model(model):
    """(classes whose effective name is MODEL, classes that copy MODEL into another model), in load order."""
    if model not in BY_MODEL:
        # MODEL reaches a class only through _name/_inherit (or, in 19, its class name): skip files that
        # mention it elsewhere only, e.g. env['MODEL'] or comodel_name='MODEL'
        rx = re.compile(r'''\b_(?:name|inherit)\b(?:(?!\n[ \t]*(?:def |class |@|[A-Za-z_]\w*[ \t]*[:=]))[\s\S])'''
                        r'''{0,4000}?['"]%s['"]''' % re.escape(model))
        paths = [p for p in dict.fromkeys(files_with("'%s'" % model) + files_with('"%s"' % model))
                 if rx.search(TEXT[p][1])]
        if E['major'] >= 19:
            paths += files_with('class %s(' % ''.join(p[:1].upper() + p[1:] for p in model.split('.')))
        own, copies = [], []
        for path in dict.fromkeys(paths):
            for c in classes(path):
                if c['name'] == model:
                    own.append(c)
                elif model in c['inherit']:
                    copies.append(c)
        BY_MODEL[model] = (sorted(own, key=cls_key), sorted(copies, key=cls_key))
    return BY_MODEL[model]


def live(model):
    return [c for c in by_model(model)[0] if not c['unimported']]


def definer(model):
    return next((c for c in live(model) if c['role'] == 'define'), None)


def parents(model):
    out = []
    for c in live(model):
        out += [p for p in c['inherit'] if p not in (model, 'base') and p not in out]
    return out


def chain(model):
    """[(model, via)]: MODEL, its _inherit parents breadth-first, then 'base', which every model but
    'base' inherits (18.0 models.py:733-736, 19.0 orm/model_classes.py:166-169)."""
    out, seen, i = [(model, 'self')], {model}, 0
    while i < len(out):
        for p in parents(out[i][0]):
            if p not in seen:
                seen.add(p)
                out.append((p, 'parent ' + p))
        i += 1
    return out + ([('base', 'base')] if model != 'base' else [])


def all_model_names():
    return sorted(set(re.findall(r'''(?<!\w)_(?:name|inherit)\s*=\s*(?:\w+\s*=\s*)?['"]([\w.]+)['"]''',
                                 texts() and E['big'])))


def core_file(transient=False):
    if E['major'] >= 19:
        return os.path.join(E['odoo_root'], 'odoo', 'orm', 'models_transient.py' if transient else 'models.py')
    return os.path.join(E['odoo_root'], 'odoo', 'models.py')


def core_line(pattern, path=None):
    """path:line of the first line matching PATTERN (the core ORM file by default)."""
    path = path or core_file()
    for i, line in enumerate(read(path).splitlines() if os.path.isfile(path) else [], 1):
        if re.search(pattern, line):
            return '%s:%d' % (path, i)
    return path


# ---------------------------------------------------------------- rendering helpers

def lit(n, width=40):
    if isinstance(n, ast.Constant):
        s = repr(n.value)
    elif isinstance(n, ast.Name):
        s = n.id
    elif isinstance(n, ast.Attribute):
        s = lit(n.value, 99) + '.' + n.attr
    elif isinstance(n, ast.Lambda):
        s = 'lambda'
    elif isinstance(n, ast.Call):
        s = lit(n.func, 99) + '(..)'
    else:
        s = '[..]' if isinstance(n, (ast.List, ast.Tuple)) else '..'
    return s if len(s) <= width else s[:width - 2] + '..'


def const(name, path, hops=0):
    """Value node of the module-level constant NAME of PATH, following `from X import NAME` into the roots."""
    if path not in texts() or hops > 3:
        return None
    classes(path)
    if name in CONSTS[path] or name not in IMPS[path]:
        return CONSTS[path].get(name)
    node, real = IMPS[path][name]
    start = import_base(path, node)
    leaf = dotted_files(*start)[1] if start else None
    f = leaf and next((f for f in (leaf + '.py', os.path.join(leaf, '__init__.py')) if os.path.isfile(f)), None)
    return const(real, f, hops + 1) if f else None


def sel_keys(n, path=None):
    """Keys of a static selection list, following a module-level constant of PATH (or one it imports)."""
    if isinstance(n, ast.Name) and path:
        n = const(n.id, path) or n
    if isinstance(n, (ast.List, ast.Tuple)):
        return [e.elts[0].value for e in n.elts
                if isinstance(e, ast.Tuple) and e.elts and isinstance(e.elts[0], ast.Constant)]
    return None


def cls_line(c, role):
    return '%s:%d %s %s %s%s%s' % (c['path'], c['line'], c['module'], c['cls'], role,
                                   ' UNIMPORTED' if c['unimported'] else '',
                                   ' _inherit=[%s]' % ', '.join(c['inherit']) if c['inherit'] else '')


def verdict(text, code, stream=None):
    print('VERDICT: ' + text, file=stream or sys.stdout)
    return code


def closest(word, names):
    return ', '.join(difflib.get_close_matches(word, sorted(set(names)), 3, 0.5)) or 'none'


def shadow_notes(mods):
    for m in sorted(set(mods) & set(SHADOWED)):
        print('shadowed: %s also at %s (an earlier root wins, that copy never loads)' % (m, ', '.join(SHADOWED[m])))


def no_model(model):
    return verdict('NOT FOUND: model %s has no definition in the roots; closest models: %s'
                   % (model, closest(model, [m for m in all_model_names() if m != model])), 1)


# ---------------------------------------------------------------- commands

def cmd_env():
    s, prev = E['src'], None
    for k in ('version', 'odoo_root', 'conf', 'python', 'dev_db'):
        print('%-9s %s  [%s]' % (k, E.get(k) or '-', 'same' if prev and s.get(k) == prev else s.get(k, 'not found')))
        prev = s.get(k)
    print('addons    %s' % s.get('addons', 'none: only core roots'))
    for i, (r, why) in enumerate(E['roots'], 1):
        print('  r%d %s  [%s]' % (i, r, why))
    for p in E['skipped']:
        print('  skipped %s (missing or no module inside)' % p)
    if SHADOWED:
        print('shadowed (first root wins): ' + ', '.join('%s (%s)' % (m, ', '.join(p))
                                                          for m, p in sorted(SHADOWED.items())))
    for n in E.get('notes', []) + (['rules verified on 18.0/19.0 source only; unverified for 16/17']
                                   if E['major'] < 18 else []):
        print('note: ' + n)
    return verdict('Odoo %s, %d roots, %d modules, base at %s'
                   % (E['version'], len(E['roots']), len(MODS), MODS['base']), 0)


def cmd_roots():
    for r, _ in E['roots']:
        print(r)
    return verdict('%d roots (Odoo %s)' % (len(E['roots']), E['version']), 0, sys.stderr)


def capped(cls, show_all):
    """CLS limited to CAP, those outside the core checkout first, in load order."""
    if show_all or len(cls) <= CAP:
        return cls
    keep = set(map(id, sorted(cls, key=lambda c: (c['path'].startswith(E['odoo_root'] + os.sep), cls_key(c)))[:CAP]))
    return [c for c in cls if id(c) in keep]


def cmd_model(model, show_all=False):
    own, copies = by_model(model)
    exts = [c for c in own if c['role'] == 'extend' and not c['unimported']]  # defines and UNIMPORTED always print
    hidden = set(map(id, exts)) - set(map(id, capped(exts, show_all)))
    for c in own:
        if id(c) not in hidden:
            print(cls_line(c, c['role']))
    if hidden:
        print('+%d more extensions (--all lists them) in: %s' % (len(hidden), ', '.join(
            dict.fromkeys(c['module'] for c in exts if id(c) in hidden))))
    for c in capped(copies, show_all):
        print(cls_line(c, 'copies %s into %s: not %s' % (model, c['name'], model)))
    if not show_all and len(copies) > CAP:
        print('+%d more classes copy %s into other models (--all lists them)' % (len(copies) - CAP, model))
    shadow_notes(c['module'] for c in own + copies)
    d = definer(model)
    if not d and own:
        return verdict('NOT FOUND: %d classes extend %s but none defines it; is the root of its defining module '
                       'missing from addons_path?' % (len(own), model), 1)
    if not d:
        return no_model(model)
    lv = live(model)

    def last(attr, default):  # the newest class setting ATTR wins, as in the registry class MRO
        return next(((c['attrs'][attr][0], '%s:%d' % (c['path'], c['attrs'][attr][1])) for c in reversed(lv)
                     if attr in c['attrs']), default)
    auto = last('_auto', (d['kind'] != 'Abstract', '%s default' % d['kind']))
    log = last('_log_access', (auto[0], 'defaults to _auto'))
    inherits = {}
    for c in lv:
        inherits.update(c['inherits'])
    ps = ['%s%s' % (p, '' if definer(p) else ' (NOT DEFINED in the roots)') for p in parents(model)]
    print('type=%s _auto=%s (%s) _log_access=%s (%s) parents=[%s] _inherits=%s'
          % (d['kind'], auto[0], auto[1], log[0], log[1], ', '.join(ps), inherits or '{}'))
    ndef = sum(c['role'] == 'define' for c in lv)
    return verdict('%s defined in %s (%s:%d); %d extensions%s' % (
        model, d['module'], d['path'], d['line'], len(lv) - ndef,
        '; %d more classes redefine it from scratch' % (ndef - 1) if ndef > 1 else ''), 0)


def fdefs(c):
    """{field: (line, Call, type)} for `name = fields.X(...)` and `name: T = fields.X(...)` in a class body."""
    if 'fields' not in c:
        c['fields'] = {}
        for st in c['node'].body:
            tgt = st.targets[0] if isinstance(st, ast.Assign) and len(st.targets) == 1 else getattr(st, 'target', None)
            f = getattr(getattr(st, 'value', None), 'func', None)
            if not isinstance(st, (ast.Assign, ast.AnnAssign)) or not isinstance(tgt, ast.Name):
                continue
            if isinstance(f, ast.Attribute) and getattr(f.value, 'id', None) == 'fields':
                c['fields'][tgt.id] = (st.lineno, st.value, f.attr)
            elif getattr(f, 'id', None) in FIELD_TYPES:
                c['fields'][tgt.id] = (st.lineno, st.value, f.id)
    return c['fields']


def kwargs(call):
    return {k.arg: k.value for k in call.keywords if k.arg}


def comodel_node(call, ftype):
    return kwargs(call).get('comodel_name') or (call.args[0] if call.args and ftype in RELATIONAL else None)


def comodel(call, ftype):
    n = comodel_node(call, ftype)
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def selection(call, ftype):
    positional = call.args[0] if call.args and ftype in ('Selection', 'Reference') else None
    return kwargs(call).get('selection') or positional


def label(call, ftype):
    pos = {'Selection': 1, 'Reference': 1, 'Many2one': 1, 'One2many': 2, 'Many2many': 4}.get(ftype, 0)
    n = kwargs(call).get('string') or (call.args[pos] if len(call.args) > pos else None)
    return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def describe(call, ftype, path):
    kw, co, sel = kwargs(call), comodel_node(call, ftype), selection(call, ftype)
    out = [ftype if co is None else '%s(%s)' % (ftype, repr(co.value) if isinstance(co, ast.Constant) else lit(co))]
    if sel is not None:
        out.append('selection=%s' % (sel_keys(sel, path) if sel_keys(sel, path) is not None else lit(sel)))
    for k in ('selection_add', 'related', 'compute', 'store', 'required', 'company_dependent', 'groups'):
        if k in kw:
            out.append('%s=%s' % (k, sel_keys(kw[k], path) if k == 'selection_add' else lit(kw[k])))
    return ' '.join(out)


def field_hits(model, field, prefix='', seen=None):
    """(definitions of FIELD on MODEL, its parents breadth-first, 'base' extensions and _inherits
    comodels; every field name seen on live classes)."""
    seen = seen or {model}
    hits, names, deleg = [], set(), {}
    for m, via in chain(model):
        for c in by_model(m)[0]:
            fd = fdefs(c)
            if not c['unimported']:
                names.update(fd)
                deleg.update(c['inherits'] if m != 'base' else {})
            if field in fd:
                hits.append({'c': c, 'via': prefix[:-3] if prefix and via == 'self' else prefix + via, 'owner': model,
                             'line': fd[field][0], 'call': fd[field][1], 'ftype': fd[field][2]})
    for co, fk in deleg.items():
        if co not in seen:
            seen.add(co)
            sub, subnames = field_hits(co, field, '%s_inherits %s (%s) > ' % (prefix, co, fk), seen)
            hits, names = hits + sub, names | subnames
    return hits, names


def magic(model, field):
    """(output line, None) when FIELD is a magic field of MODEL, else (None, why the magic field is absent).
    MetaModel adds them to the class defining a non-abstract model: id/display_name always (19: on BaseModel,
    so abstract models have them too), create/write uid/date when attrs.get('_log_access', self._auto)
    (18.0 models.py:267-293, 19.0 orm/models.py:268-292); _auto is True on Model/TransientModel, False on
    AbstractModel."""
    if field in ('id', 'display_name'):
        if E['major'] >= 19:
            return '%s core BaseModel via=magic (defined on BaseModel)' % core_line(r'^\s+%s = \w+\(' % field), None
        rule = core_line(r'if not self._abstract and self._name not in')
        for m, _ in chain(model)[:-1]:
            d = definer(m)
            if d and d['kind'] != 'Abstract':
                return '%s core MetaModel via=magic%s (added to non-abstract definer %s:%d, %s)' % (
                    core_line(r"add(_default)?\('%s'" % field), '' if m == model else ' of parent ' + m, d['path'],
                    d['line'], rule), None
        return None, '%s is abstract: MetaModel adds no magic fields (%s)' % (model, rule)
    if field not in LOG_FIELDS:
        return None, None
    rule, reason = core_line(r"attrs.get\('_log_access', self._auto\)"), None
    for m, _ in chain(model)[:-1]:
        d = definer(m)
        if not d or d['kind'] == 'Abstract':
            continue
        auto, log = d['attrs'].get('_auto', (True, None)), d['attrs'].get('_log_access')
        if log[0] if log else auto[0]:
            src = core_line(r"add_default\('%s'" % field)
            ftype = re.search(r"'%s', (?:fields\.)?(\w+)" % field, read(src.rsplit(':', 1)[0]).splitlines()[
                int(src.rsplit(':', 1)[1]) - 1]) if ':' in src else None
            why = '_log_access=True at %s:%d' % (d['path'], log[1]) if log else '_log_access defaults to _auto=True'
            return '%s core MetaModel via=magic%s %s (%s on definer %s:%d; %s)' % (
                src, '' if m == model else ' of parent ' + m, ftype.group(1) if ftype else '', why, d['path'],
                d['line'], rule), None
        if m == model:
            reason = 'log fields not added: %s definer %s:%s has %s; _log_access defaults to _auto (%s)' % (
                model, d['path'], (log or auto)[1], '_log_access=False' if log else '_auto=False and no _log_access',
                rule)
    d = definer(model)
    if reason is None and d and d['kind'] == 'Abstract':
        reason = '%s is abstract: MetaModel adds no magic fields (%s)' % (
            model, core_line(r'if not self._abstract and self._name not in'))
    return None, reason


def winners(hits):
    """Live defs that build the field, most derived first: those of the first model holding one, in its MRO,
    down to the first def whose class the final class does not subclass; that def and the older ones lose
    their attributes (18.0 fields.py:416-422 and models.py:3674, 19.0 orm/fields.py:419-425 and
    orm/model_classes.py:414)."""
    live_ = [h for h in hits if not h['c']['unimported']]
    if not live_:
        return []
    rank = {n: i for i, n in enumerate(c3(live_[0]['owner'], {}))}
    grp = sorted((h for h in live_ if h['owner'] == live_[0]['owner']), key=lambda h: rank.get(id(h['c']), len(rank)))
    out = []
    for h in grp:
        if h['ftype'] not in (grp[0]['ftype'], SUBCLASS.get(grp[0]['ftype'])):
            break
        out.append(h)
    return out


def hop(model, field, depth=0):
    """(hits, field names, winning defs, magic line, why no magic, final class, comodel) of MODEL.FIELD.
    The comodel is the newest comodel_name, else where the newest related= path ends (18.0
    fields.py:637-642, 19.0 orm/fields.py:644-649 copy comodel_name from the related field)."""
    hits, names = field_hits(model, field)
    win, (mhit, reason) = winners(hits), magic(model, field)
    ftype = win[0]['ftype'] if win else MAGIC[field] if mhit else None
    co = next((comodel(h['call'], h['ftype']) for h in win if comodel(h['call'], h['ftype'])), None)
    rel = next((kwargs(h['call'])['related'].value for h in win
                if isinstance(kwargs(h['call']).get('related'), ast.Constant)), None)
    if ftype in RELATIONAL and not co:
        co = 'res.users' if not win else follow(win[0]['owner'], rel, depth + 1) if rel and depth < 5 else None
    return hits, names, win, mhit, reason, ftype, co


def follow(model, path, depth):
    """Comodel where the relational PATH from MODEL ends, None when a hop is missing or unknown."""
    for field in path.split('.'):
        ftype, model = hop(model, field, depth)[5:] if model and definer(model) else (None, None)
        if ftype not in RELATIONAL:
            return None
    return model


def cmd_field(start, path):
    parts, kinds, model = path.split('.'), [], start
    for i, field in enumerate(parts):
        if len(parts) > 1:
            print('hop %d %s.%s' % (i + 1, model, field))
        if not definer(model):
            return no_model(model)
        hits, names, win, mhit, reason, ftype, co = hop(model, field)
        src = next((h for h in win if comodel(h['call'], h['ftype'])), None)
        for h in hits:
            c, desc = h['c'], describe(h['call'], h['ftype'], h['c']['path'])
            if h['ftype'] in RELATIONAL and not comodel(h['call'], h['ftype']):
                desc += ' comodel from %s:%d' % (src['c']['path'], src['line']) if src else \
                    ' comodel %s via related' % co if co else ' comodel: unknown'
            print('%s:%d %s %s via=%s %s%s' % (c['path'], h['line'], c['module'], c['cls'], h['via'], desc,
                                               ' UNIMPORTED' if c['unimported'] else ''))
        if win and len(win) < sum(h['owner'] == win[0]['owner'] and not h['c']['unimported'] for h in hits):
            fpath = os.path.join(E['odoo_root'], 'odoo', 'orm' if E['major'] >= 19 else '', 'fields.py')
            print('final class %s from %s:%d; the older defs of another class lose their attributes (%s)' % (
                ftype, win[0]['c']['path'], win[0]['line'], core_line(r'not isinstance\(self, type\(field\)\)', fpath)))
        for line in (mhit, reason):
            if line:
                print(line)
        if not ftype:
            where = ' (hop %d of %s.%s)' % (i + 1, start, path) if len(parts) > 1 else ''
            return field_missing(model, field, names, reason, where)
        kinds.append('%s(%s)' % (ftype, co) if co else ftype)
        if i + 1 < len(parts) and ftype not in RELATIONAL:
            return verdict('NOT FOUND: %s.%s is %s, not relational: %s.%s stops at hop %d' % (
                model, field, ftype, start, path, i + 1), 1)
        if i + 1 < len(parts) and not co:
            return verdict('UNKNOWN comodel of %s.%s (not a string literal): answer unknown' % (model, field), 2)
        model = co
    if len(parts) > 1:
        return verdict('FOUND %s.%s: %s' % (start, path, ' > '.join(kinds)), 0)
    if win:
        return verdict('FOUND %s' % ('on %s' % start if win[0]['via'] == 'self' else 'via ' + win[0]['via']), 0)
    return verdict('FOUND magic', 0)


def field_missing(model, field, names, reason, where):
    for c in by_model(model)[1]:
        if field in fdefs(c):
            print('note: %s is defined on %s (%s:%d), which copies %s; a copy never adds fields back to %s'
                  % (field, c['name'], c['path'], fdefs(c)[field][0], model, model))
    labels = {f: label(call, t) for m, _ in chain(model) for c in live(m) for f, (_, call, t) in fdefs(c).items()
              if (label(call, t) or '').lower().replace(' ', '_') == field.lower()}
    names |= (set() if reason and field in ('id', 'display_name') else {'id', 'display_name'}) | (
        set(LOG_FIELDS) if not reason else set())
    near = ['%s (label %r)' % kv for kv in labels.items()] + [
        n for n in difflib.get_close_matches(field, sorted(names), 3, 0.5) if n not in labels]
    return verdict('NOT FOUND: %s.%s%s; closest fields: %s' % (model, field, where, ', '.join(near) or 'none'), 1)


def reg_bases(model):
    """Final bases of MODEL's registry class, replaying _build_model over its classes in load order
    (18.0 models.py:733-770, 19.0 orm/model_classes.py:166-207): LastOrderedSet([cls]), then for each name
    in _inherit + ['base'] the previous bases when it is MODEL itself, else that parent's registry class.
    A class whose _inherit does not list MODEL starts a new registry class."""
    bases = []
    for c in live(model):
        new = [id(c)]
        for p in c['inherit'] + ([] if model == 'base' else ['base']):
            for b in (bases if p == model else [p]):
                if b in new:
                    new.remove(b)
                new.append(b)
        bases = new
    return bases


def c3(node, memo, stack=()):
    """Python's C3 linearization over id(definition class), (path, name) (a plain class of that file used
    as a Python base, e.g. ResConfigModuleInstallationMixin in 18.0 base/models/res_config.py), 'model'
    (a registry class) and ':Model' / ':TransientModel' / ':BaseModel' (the core classes; AbstractModel
    is BaseModel)."""
    if node not in memo:
        if isinstance(node, (int, tuple)):
            path, cdef = (ID2C[node]['path'], ID2C[node]['node']) if isinstance(node, int) else \
                (node[0], PYCLS[node[0]][node[1]])
            defs, heads = {c['cls']: id(c) for c in CLS[path]}, []  # a model class base stays one node
            for b in [] if node in stack else base_names(cdef):
                if b in KINDS:
                    heads.append({'Model': ':Model', 'TransientModel': ':TransientModel'}.get(b, ':BaseModel'))
                elif b in PYCLS[path] and b != cdef.name:
                    heads.append(defs.get(b, (path, b)))
            if isinstance(node, int) and not any(isinstance(h, str) for h in heads):
                heads.append(':BaseModel')
        elif node.startswith(':'):
            heads = {':TransientModel': [':Model'], ':Model': [':BaseModel'], ':BaseModel': []}[node]
        else:
            heads = [] if node in stack else reg_bases(node)
        seqs, out = [list(c3(h, memo, stack + (node,))) for h in heads] + [list(heads)], [node]
        while any(seqs):
            seqs = [q for q in seqs if q]
            head = next((q[0] for q in seqs if not any(q[0] in t[1:] for t in seqs)), None)
            if head is None:
                raise SetupError('no consistent MRO for %s: Odoo cannot build this registry class' % (node,))
            out.append(head)
            for q in seqs:
                if q[0] == head:
                    q.pop(0)
        memo[node] = out
    return memo[node]


def signature(fn):
    a = fn.args
    pos = getattr(a, 'posonlyargs', []) + a.args
    dfl = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    parts = [p.arg + ('=' + lit(v, 16) if v is not None else '') for p, v in zip(pos, dfl)]
    parts += ['*' + a.vararg.arg] if a.vararg else ['*'] if a.kwonlyargs else []
    parts += [k.arg + ('=' + lit(v, 16) if v is not None else '') for k, v in zip(a.kwonlyargs, a.kw_defaults)]
    parts += ['**' + a.kwarg.arg] if a.kwarg else []
    deco = ''.join('@%s ' % lit(d.func if isinstance(d, ast.Call) else d, 30) for d in fn.decorator_list)
    return '%sdef %s(%s)' % (deco, fn.name, ', '.join(parts))


def hooks(fn, method, limit):
    """(whether FN calls super().METHOD, 'name:line,line ...' of the first LIMIT other ._private( calls in FN)."""
    calls, sup = {}, False
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            v, attr = n.func.value, n.func.attr
            if isinstance(v, ast.Call) and getattr(v.func, 'id', None) == 'super' and attr == method:
                sup = True
            elif attr.startswith('_') and not attr.startswith('__') and attr != '_':  # env._() translates
                calls.setdefault(attr, []).append(n.lineno)
    items, limit = sorted(calls.items(), key=lambda kv: kv[1][0]), limit or len(calls)
    text =' '.join('%s:%s' % (k, ','.join(map(str, sorted(set(v))))) for k, v in items[:limit])
    return sup, text + (' +%d more' % (len(items) - limit) if len(items) > limit else '')


def method_node(body, method):
    return next((st for st in reversed(body) if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and st.name == method), None)


def cmd_method(model, method, module=None, show_all=False):
    if not definer(model):
        return no_model(model)
    if module and module not in MODS:
        return verdict('SETUP ERROR: --module %s is not in the roots' % module, 2)
    defs, names, trees = [], set(), {}
    for n in c3(model, {}):
        if isinstance(n, int):
            c = ID2C[n]
        elif isinstance(n, tuple):
            c = {'path': n[0], 'module': TEXT[n[0]][0], 'cls': n[1], 'node': PYCLS[n[0]][n[1]]}
        elif n.startswith(':'):
            path = core_file(n == ':TransientModel')
            if path not in trees:
                trees[path] = ast.parse(read(path), path).body if os.path.isfile(path) else []
            node = next((x for x in trees[path] if isinstance(x, ast.ClassDef) and x.name == n[1:]), None)
            c = {'path': path, 'module': 'core', 'cls': n[1:], 'node': node or ast.ClassDef(body=[])}
        else:
            continue  # a registry class holds no code
        names.update(st.name for st in c['node'].body if isinstance(st, ast.FunctionDef))
        fn = method_node(c['node'].body, method)
        if fn:
            defs.append((c['path'], c['module'], c['cls'], fn))
    if not defs:
        return verdict('NOT FOUND: %s.%s; closest methods: %s' % (model, method, closest(method, names)), 1)
    deps = closure(module)[0] if module else set()
    print('super() order: #1 runs first, each super() reaches the next line')
    for i, (path, mod, cname, fn) in enumerate(defs, 1):
        sup, text = hooks(fn, method, None if show_all else 10)
        tag = '' if not module or mod == 'core' else ' [in depends of %s]' % module if mod in deps else \
            ' [NOT in depends of %s (not guaranteed installed)]' % module
        print('#%d %s:%d %s %s %s super=%s%s%s' % (i, path, fn.lineno, mod, cname, signature(fn),
                                                   'yes' if sup else 'no', tag, ' hooks: ' + text if text else ''))
    shadow_notes(m for _, m, _, _ in defs)
    mods = sorted({m for _, m, _, _ in defs if m in deps}, key=load_key)
    pairs = [(a, b) for i, a in enumerate(mods) for b in mods[i + 1:]
             if a not in closure(b)[0] and b not in closure(a)[0]]
    for a, b in pairs[:10]:
        print('AMBIGUOUS %s / %s: both override %s and neither depends on the other; %s loading first is an '
              'accident of (depth, name)' % (a, b, method, a))
    if len(pairs) > 10:
        print('AMBIGUOUS +%d more pairs' % (len(pairs) - 10))
    path, mod, _, fn = defs[0]
    return verdict('FOUND %d defs of %s on %s; runs first: %s (%s:%d)' % (len(defs), method, model, mod, path,
                                                                          fn.lineno), 0)


def cmd_depends(module):
    if module not in MODS:
        return verdict('NOT FOUND: module %s not in the roots; closest: %s' % (module, closest(module, MODS)), 1)
    mods, missing = closure(module)
    roots, order = [r for r, _ in E['roots']], sorted(mods, key=load_key)
    rix = {m: roots.index(os.path.dirname(MODS[m])) + 1 for m in order}
    print('roots: ' + ' '.join('r%d=%s' % (i, roots[i - 1]) for i in sorted(set(rix.values()))))
    print('load order (%s): base first, then %s' % (E['version'], '(phase, depth, order_name) module_graph.py:224-225'
                                                    if E['major'] >= 19 else '(depth, name) graph.py:109-116'))
    for i, m in enumerate(order, 1):
        print('%3d %s d%d r%d%s%s' % (i, m, depth(m), rix[m],
                                      ' NOT INSTALLABLE' if manifest(m).get('installable', True) is False else '',
                                      ' shadows %s' % ', '.join(SHADOWED[m]) if m in SHADOWED else ''))
    for m, req in sorted(missing.items()):
        print('MISSING %s (required by %s)' % (m, ', '.join(sorted(req))))
    return verdict('%s closure: %d modules, %d missing' % (module, len(order), len(missing)), 0)


def xml_ids(path):
    out, p = [], expat.ParserCreate()

    def start(tag, attrs):
        if tag in XMLID_TAGS and 'id' in attrs:
            out.append((attrs['id'], p.CurrentLineNumber))
    p.StartElementHandler = start
    try:
        with open(path, 'rb') as f:
            p.ParseFile(f)
    except expat.ExpatError as e:
        print('UNPARSED %s: %s' % (path, e))
    return out


def csv_ids(path):
    out = []
    with open(path, newline='', encoding='utf-8', errors='replace') as f:
        rows = csv.reader(f)
        head = next(rows, None) or []
        if 'id' in head:
            k, prev = head.index('id'), rows.line_num
            for row in rows:
                if len(row) > k:
                    out.append((row[k], prev + 1))
                prev = rows.line_num
    return out


def record_ids(mod, needle=None):
    """[(id, path, line)] of the XML records/templates/menus/reports and CSV rows of MOD."""
    return [(i, path, n) for path in module_files(mod, ('.xml', '.csv')) if not needle or needle in read(path)
            for i, n in (xml_ids(path) if path.endswith('.xml') else csv_ids(path))]


def generated(mod, name):
    """(reason, source line) when Odoo creates MOD.NAME at install, else None. Rules of
    odoo/addons/base/models/ir_model.py (_reflect_models/_reflect_fields/_reflect_selections, same in
    18.0 and 19.0), base/models/ir_module.py create(), odoo/modules/db.py create_categories() and
    account/models/chart_template.py (account.<company id>_<chart template id>)."""
    irm = os.path.join(MODS['base'], 'models', 'ir_model.py')
    deps, tpl = closure(mod)[0], re.match(r'\d+_(.+)', name) if mod == 'account' else None
    if tpl:  # chart templates load per company as account.<company id>_<template id>
        rule, rx = core_line(r'account\.\{(self\.env\.)?company\.id\}_\{xml_?id\}', os.path.join(
            MODS[mod], 'models', 'chart_template.py')), re.compile(r"""['"]%s['"]\s*:""" % re.escape(tpl.group(1)))
        for m in sorted(MODS):
            for path in sorted(glob.glob(os.path.join(MODS[m], 'data', 'template', '*.csv'))):
                for i, line in csv_ids(path):
                    if i == tpl.group(1):
                        return 'chart template row of %s at %s:%d, created for each company using that chart' % (
                            m, path, line), rule
        for path in files_with("'%s'" % tpl.group(1)) + files_with('"%s"' % tpl.group(1)):
            k = rx.search(TEXT[path][1])
            if k and '@template(' in TEXT[path][1]:
                return 'chart template data of %s at %s:%d, created for each company using that chart' % (
                    TEXT[path][0], path, TEXT[path][1].count('\n', 0, k.start()) + 1), rule
    if mod == 'base' and name.startswith('module_category_'):
        for m in sorted(MODS):
            parts = str(manifest(m).get('category') or 'Uncategorized').split('/')
            for k in range(1, len(parts) + 1):
                slug = '_'.join(x.lower() for x in parts[:k]).replace('&', 'and').replace(' ', '_')
                if name == 'module_category_' + slug:
                    return "category '%s' of module %s's manifest" % ('/'.join(parts[:k]), m), core_line(
                        r"xml_id = 'module_category_'", os.path.join(E['odoo_root'], 'odoo', 'modules', 'db.py'))
    if mod == 'base' and name.startswith('module_') and name[7:] in MODS:
        return 'ir.module.module record of %s (every module in the roots)' % name[7:], core_line(
            r"'module_%s' % module.name", os.path.join(MODS['base'], 'models', 'ir_module.py'))
    if name.startswith('model_'):
        for c in (c for p, (m, _) in texts().items() if m == mod for c in classes(p)):
            if c['name'].replace('.', '_') == name[6:] and not c['unimported']:
                return '%s %ss %s at %s:%d (model._module == module)' % (
                    mod, c['role'], c['name'], c['path'], c['line']), core_line(r'if model._module == module', irm)
    kind = 'field' if name.startswith('field_') and '__' in name else \
        'selection' if name.startswith('selection__') and name.count('__') >= 3 else None
    if not kind:
        return None
    xmodel, field, xvalue = (name[6:].split('__', 1) + [None]) if kind == 'field' else name[11:].split('__', 2)
    rx = r'''['"](%s)['"]''' % '[._]'.join(re.escape(p) for p in xmodel.split('_'))
    for model in sorted(m for m in set(re.findall(rx, texts() and E['big'])) if definer(m)):
        owner = definer(model)['module']
        present = owner == mod or owner in deps or load_key(owner) < load_key(mod)  # MODEL exists when MOD loads
        hits = [h for h in field_hits(model, field)[0] if not h['c']['unimported']]
        mine = [h for h in hits if h['c']['module'] == mod]
        if kind == 'selection':
            for h in mine:  # the xmlid takes the declaring module, whichever module reflects MODEL
                keys = (sel_keys(selection(h['call'], h['ftype']), h['c']['path']) or []) + (
                    sel_keys(kwargs(h['call']).get('selection_add'), h['c']['path']) or [])
                if any(str(k).replace('.', '_').replace(' ', '_').lower() == xvalue for k in keys):
                    return '%s declares value of %s.%s at %s:%d (static selection)' % (
                        mod, model, field, h['c']['path'], h['line']), core_line(r'xml_id = selection_xmlid\(m,', irm)
            continue
        rule = core_line(r'module == model._original_module', irm)
        if owner == mod and ([h for h in hits if h['c']['module'] in deps] or magic(model, field)[0]):
            return '%s defines %s (model._original_module) and %s exists when it installs' % (mod, model, field), rule
        if present and mine:
            return '%s defines %s at %s:%d via=%s (module in field._modules)' % (
                mod, field, mine[0]['c']['path'], mine[0]['line'], mine[0]['via']), rule
        adds = [p for c in live(model) if c['module'] == mod for p in c['inherit'] if p != model]
        if present and any(h for p in adds for h in field_hits(p, field)[0] if not h['c']['unimported']):
            return '%s adds a parent of %s that holds %s (model._inherit_module)' % (mod, model, field), rule
    return None


def data_files(mod):
    """Paths, relative to MOD, in its manifest data/demo lists."""
    return {os.path.normpath(p) for k in DATA_KEYS for p in manifest(mod).get(k) or []}


def loads(mod, path):
    return os.path.relpath(path, MODS[mod]) in data_files(mod)


def cmd_xmlid(xmlid):
    if '.' not in xmlid:
        return verdict('SETUP ERROR: xmlid must be module.name', 2)
    mod, name = xmlid.split('.', 1)
    if mod not in MODS:
        return verdict('NOT FOUND: module %s not in the roots; closest modules: %s' % (mod, closest(mod, MODS)), 1)
    never = ' (file not in manifest data/demo: never loads)'
    own = [r for r in record_ids(mod, name) if r[0] in (name, xmlid)]
    for i, path, line in own:
        print('%s:%d %s %s%s' % (path, line, mod, i, '' if loads(mod, path) else never))
    others = [(m, r) for m in MODS if m != mod for r in record_ids(m, xmlid) if r[0] == xmlid]
    for m, (_, path, line) in sorted(others, key=lambda x: load_key(x[0])):
        print('%s:%d %s overrides %s%s' % (path, line, m, xmlid, '' if loads(m, path) else never))
    loaded = [r for r in own if loads(mod, r[1])]
    if loaded:
        return verdict('FOUND %s (%s:%d)' % (xmlid, loaded[0][1], loaded[0][2]), 0)
    gen = generated(mod, name)
    if gen:
        return verdict('GENERATED %s at install: %s; source %s' % (xmlid, gen[0], gen[1]), 0)
    if own:
        tpl = os.path.join(MODS[mod], 'data', 'template', '')
        why = 'chart template rows load per company as account.<company id>_%s' % name \
            if any(p.startswith(tpl) for _, p, _ in own) else 'those files never load'
        hook = [h for h in ('pre_init_hook', 'post_init_hook') if manifest(mod).get(h)]
        return verdict('%s: %s is only in files missing from the manifest data/demo; %s%s' % (
            'UNKNOWN' if hook else 'NOT FOUND', xmlid, why,
            '; its %s may load them from Python, not traced' % hook[0] if hook else ''), 2 if hook else 1)
    ids = [i.split('.', 1)[1] if i.startswith(mod + '.') else i for i, _, _ in record_ids(mod)]
    return verdict('NOT FOUND: %s (no record/template/menuitem/asset/report/CSV row, not generated); closest in %s: %s'
                   % (xmlid, mod, closest(name, ids)), 1)


def glob_rx(pattern):
    """Regex for a Python glob(recursive=True) pattern relative to the addons root, as ir_asset uses."""
    parts, out = pattern.strip('/').split('/'), []
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        if part == '**':
            out.append('.*' if last else '(?:.*/)?')
        else:
            out.append(''.join('[^/]*' if ch == '*' else '[^/]' if ch == '?' else re.escape(ch) for ch in part)
                       + ('' if last else '/'))
    return re.compile(''.join(out) + r'\Z')


def asset_globs(man):
    """Globs that add files to a bundle: plain entries, ('prepend'|'append', glob) and
    ('before'|'after'|'replace', target, glob); 'include' and 'remove' add nothing."""
    for entries in (man.get('assets') or {}).values():
        for e in entries:
            if isinstance(e, str):
                yield e
            elif isinstance(e, (list, tuple)) and len(e) >= 2 and e[0] not in ('include', 'remove'):
                yield e[-1]


def xml_asset_globs(mod):
    """Paths of the ir.asset records (<record model="ir.asset"> or <asset>) in MOD's XML files; ir_asset.py
    _fill_asset_paths applies them like manifest entries."""
    for path in module_files(mod, '.xml'):
        text = read(path)
        if 'ir.asset' in text or '<asset' in text:
            for rec in re.findall(r'<record\b[^>]*"(?:theme\.)?ir\.asset"[^>]*>.*?</record>|<asset\b.*?</asset>',
                                  text, re.S):
                m, d = re.search(r'<(?:field name="path"|path)>\s*([^<\s]+)', rec), re.search(
                    r'directive"?\s*[=>]\s*"?(\w+)', rec)
                if m and not (d and d.group(1) in ('include', 'remove')):
                    yield m.group(1)


def cmd_unlisted(module, show_all=False):
    if module not in MODS:
        return verdict('NOT FOUND: module %s not in the roots; closest: %s' % (module, closest(module, MODS)), 1)
    mdir, man, bad, notes = MODS[module], manifest(module), [], []
    for path in module_files(module, ('.xml', '.csv')):
        if loads(module, path):
            continue
        if os.path.relpath(path, mdir).startswith(os.path.join('data', 'template', '')) and path.endswith('.csv'):
            notes.append(path)
        else:
            bad.append((path, 'not in manifest data/demo'))
    bad += [(os.path.join(mdir, r), 'listed in manifest but missing') for r in sorted(data_files(module))
            if not os.path.isfile(os.path.join(mdir, r))]
    py = [p for p in module_files(module, '.py') if p not in imports(module) and not p.endswith('__manifest__.py')]
    other = [p for p in py if p in imports(module, True)] if py else []
    bad += [(p, 'never imported from __init__.py') for p in py if p not in other]
    if other:
        print('note: %d files of %s are imported only by other modules (odoo.addons.%s.*), e.g. %s'
              % (len(other), module, module, other[0]))

    def web(p):
        return module + '/' + os.path.relpath(p, mdir).replace(os.sep, '/')
    left = [p for p in module_files(module, ASSET_EXT, SKIP_DIRS - {'static'})
            if web(p).startswith(module + '/static/src/')]
    for mods in ([module], MODS):  # the module's own bundles first; other modules only when needed
        globs = [glob_rx(g) for m in (mods if left else []) for g in list(asset_globs(manifest(m)))
                 + list(xml_asset_globs(m)) if g.lstrip('/').startswith(module + '/')]
        left = [p for p in left if not any(rx.match(web(p)) for rx in globs)]
    bad += [(p, 'in no assets bundle') for p in left]
    if notes:
        print('note: %d data/template/*.csv are read by the chart template code, not the manifest (e.g. %s)'
              % (len(notes), notes[0]))
    for hook in ('pre_init_hook', 'post_init_hook'):
        if man.get(hook):
            print('note: %s=%s may load files from Python; not traced' % (hook, man[hook]))
    groups = {}
    for path, why in bad:
        groups.setdefault((os.path.dirname(path), why), []).append(path)
    for (folder, why), paths in groups.items():
        if len(paths) > 5 and not show_all:
            print('%s/ %d files %s (--all lists them), e.g. %s' % (folder, len(paths), why, os.path.basename(paths[0])))
        else:
            print('\n'.join('%s %s' % (p, why) for p in paths))
    return verdict('%s: %s' % (module, '%d files never load' % len(bad) if bad else 'all files load'), 0)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='odoo_trace.py', description=__doc__.split('\n\n')[0],
                                 epilog='Exit: 0 found, 1 NOT FOUND, 2 setup error.')
    ap.add_argument('--odoo-root', help='core checkout (dir holding odoo-bin)')
    ap.add_argument('--conf', help='odoo.conf whose addons_path to use')
    ap.add_argument('--addons', help='comma-separated addons paths (replace addons_path)')
    ap.add_argument('--version', dest='odoo_version', help='Odoo series, e.g. 18.0 (default: odoo/release.py)')
    sub = ap.add_subparsers(dest='cmd', metavar='command')
    sub.required = True
    every = argparse.ArgumentParser(add_help=False)
    every.add_argument('--all', action='store_true', dest='show_all', help='no cap on long lists')
    sub.add_parser('env', help='resolved version, core, conf, python, db and roots')
    sub.add_parser('roots', help='roots only, one per line (for $(...) in grep)')
    sub.add_parser('model', parents=[every], help='classes defining, extending or copying MODEL').add_argument('model')
    p = sub.add_parser('field', help='where MODEL.FIELD comes from (self, parents, base, _inherits, magic); '
                                     'FIELD may be a path such as partner_id.country_id.code')
    p.add_argument('model')
    p.add_argument('field')
    p = sub.add_parser('method', parents=[every], help='every def of METHOD on MODEL in super() order, with hooks')
    p.add_argument('model')
    p.add_argument('method')
    p.add_argument('--module', help='tag defs in/out of the depends of MODULE, flag ambiguous order')
    sub.add_parser('depends', help='depends closure in load order').add_argument('module')
    sub.add_parser('xmlid', help='record behind module.name, or why it is generated').add_argument('xmlid')
    sub.add_parser('unlisted', parents=[every], help='files of MODULE that never load').add_argument('module')
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return e.code if not e.code else verdict('SETUP ERROR: bad arguments', 2)
    stream = sys.stderr if args.cmd == 'roots' else sys.stdout
    try:
        resolve(args)
        run = {'env': cmd_env, 'roots': cmd_roots, 'model': lambda: cmd_model(args.model, args.show_all),
               'field': lambda: cmd_field(args.model, args.field),
               'method': lambda: cmd_method(args.model, args.method, args.module, args.show_all),
               'depends': lambda: cmd_depends(args.module), 'xmlid': lambda: cmd_xmlid(args.xmlid),
               'unlisted': lambda: cmd_unlisted(args.module, args.show_all)}
        return run[args.cmd]()
    except SetupError as e:
        print('SETUP ERROR: %s' % e, file=stream)
        return verdict('SETUP ERROR (exit 2)', 2, stream)
    except Exception as e:  # a crash must never read as NOT FOUND (exit 1)
        print('INTERNAL ERROR: %s: %s' % (type(e).__name__, e), file=stream)
        return verdict('INTERNAL ERROR, answer unknown (exit 2)', 2, stream)


if __name__ == '__main__':
    sys.exit(main())
