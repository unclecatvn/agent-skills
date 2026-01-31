# AI Agents Setup for Odoo 19 Skills

This document provides instructions for setting up Odoo 19 skills with various AI IDEs.

## Claude Code (Cursor/Windsurf)

### Step 1: Configure Settings

Create or edit `~/.claude/settings.json`:

```json
{
  "documentation": [
    "/Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/SKILL.md"
  ]
}
```

### Step 2: (Optional) Configure Context Rules

Create `~/.claude/rules/coding-style.md`:

```markdown
# Odoo 19 Coding Style

Follow Odoo 19 development guidelines from the skills.

## Python

- Use `@api.depends` for computed fields
- Use `@api.constrains` for validation
- Use `@api.ondelete` for delete validation (Odoo 19)
- Use `<list>` not `<tree>` in views
- Use direct attributes not `attrs`

## XML

- Use `<list>` for list views
- Use `invisible=""` not `attrs="{'invisible': [...]}"`

## JavaScript

- Use `_t()` for translations
- Use OWL hooks properly
```

### Step 3: Verify Installation

In Claude Code terminal:

```bash
# Test skill loading
python -c "import sys; print('Claude Code ready')"
```

---

## Continue.dev

### Step 1: Create Continue Config

Create `.continuerc.yaml`:

```yaml
rules:
  - path: skills/odoo/19.0/SKILL.md
    type: documentation
```

### Step 2: Configure in Continue UI

1. Open Continue
2. Go to Settings → Config
3. Add documentation path
4. Save and reload

---

## Aider

### Step 1: Add to .aider.conf

```
# Add Odoo 19 skills
--add-skills-file
/Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/SKILL.md
```

### Step 2: Reload Aider

```bash
aider --reload
```

---

## Cursor (with Cline)

### Step 1: Add to .cursorrules

```
# Always reference Odoo 19 skills for Odoo development
When working with Odoo 19 code, always reference the Odoo 19 skills in /Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/
```

### Step 2: Configure .cursorrules

Create `.cursorrules` in your project root:

```markdown
# Odoo 19 Development

For Odoo 19 development tasks, reference the skills at:
- /Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/SKILL.md

Key Odoo 19 changes:
- Use <list> not <tree>
- Use direct attributes not attrs
- Use @api.ondelete for delete validation
```

---

## Repo (Continue fork)

### Step 1: Add to Repo Config

Create `.repo/config.yaml`:

```yaml
documentation:
  - /Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/SKILL.md
```

---

## Swirl

### Step 1: Add to Swirl Config

Create `~/.config/swirl/rules.yaml`:

```yaml
rules:
  - name: Odoo 19 Development
    documentation:
      - /Users/unclecat/dtg/odoo-skills-19/skills/odoo/19.0/SKILL.md
```

---

## Generic Setup (Any AI Tool)

For any AI tool that supports documentation:

1. **Add the SKILL.md path** to your documentation sources
2. **Optionally add coding-style rules** from `CLAUDE.md`
3. **Reload/restart** your AI tool
4. **Test** by asking an Odoo 19 development question

### Example Prompt to Test

```
How do I create a computed field in Odoo 19 with dotted dependencies?
```

Expected answer should reference `odoo-19-decorator-guide.md` or `odoo-19-field-guide.md`.

---

## Troubleshooting

### Skills Not Loading

1. Verify the path exists
2. Check file permissions
3. Ensure SKILL.md is valid YAML front matter

### Outdated Information

1. Pull latest changes from the skills repository
2. Check version in SKILL.md matches your needs

### Specific IDE Issues

Check your IDE's documentation for:
- How to configure documentation paths
- How to reload configuration
- Any specific syntax requirements

---

## Updating Skills

To update the Odoo 19 skills:

```bash
cd /Users/unclecat/dtg/odoo-skills-19
git pull origin main
```

Then reload your AI tool.

---

## Feedback

For issues or suggestions:
1. Check the guide files in `dev/`
2. Refer to specific guide when reporting issues
3. Include examples from your codebase
