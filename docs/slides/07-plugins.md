---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
color: #242424
style: |
 section {
 font-family: 'Segoe UI', system-ui, sans-serif;
 }
 h1 {
 color: #0078D4;
 border-bottom: 3px solid #0078D4;
 padding-bottom: 0.3em;
 }
 h2, h3 {
 color: #0078D4;
 }
 code {
 background: #f3f2f1;
 color: #242424;
 }
 pre {
 background: #f3f2f1 !important;
 border-radius: 4px;
 border-left: 4px solid #0078D4;
 }
 table {
 font-size: 0.85em;
 }
 th {
 background: #0078D4;
 color: #ffffff;
 }
 td {
 background: #f3f2f1;
 }
 strong {
 color: #0078D4;
 }
 blockquote {
 border-left: 4px solid #0078D4;
 color: #605e5c;
 background: #f3f2f1;
 padding: 0.5em 1em;
 border-radius: 4px;
 }
 a {
 color: #0078D4;
 }
 footer {
 color: #605e5c;
 }
---

# Module 7: Plugins

### GitHub Copilot CLI Workshop

---

## Copilot Extensibility Stack

```
┌─────────────────────┐
│ Copilot CLI         │
├─────────────────────┤
│ Built-in Tools      │ bash, view, create, edit
├─────────────────────┤
│ MCP Servers         │ Module 5
├─────────────────────┤
│ Skills              │ Module 6
├─────────────────────┤
│ Plugins             │ ← This module
└─────────────────────┘
```

Plugins = **packaged integrations** from the ecosystem

---

## Plugin Sources

| Source | What you'll find |
|--------|-----------------|
| **github/copilot-plugins** | Official GitHub plugins (default marketplace) |
| **github/awesome-copilot** | Community-curated plugins (default marketplace) |
| **microsoft/work-iq-mcp** | Enterprise integrations |
| **GitHub repos** | Direct `owner/repo` installs |
| **Repo subdirectories** | `owner/repo:path` plugin layouts |
| **Git URLs** | Direct git install sources |

```bash
# Search for available plugins
copilot plugin marketplace list
copilot plugin marketplace browse copilot-plugins
```

Inside a session, use `/plugin` for interactive marketplace browsing and plugin management.

---

## Installing a Plugin

Plugins can bundle **skills, agents, hooks, MCP servers, and LSP servers**

```bash
# From a marketplace in a session
/plugin install workiq@copilot-plugins

# From a marketplace in shell
copilot plugin install workiq@copilot-plugins

# From GitHub
copilot plugin install owner/repo
copilot plugin install owner/repo:plugins/my-plugin

# From a git URL
copilot plugin install https://github.com/owner/my-plugin.git
```

> Audit plugin source and permission needs before installing

---

## Plugin Maintenance

```bash
copilot plugin list
copilot plugin update spark@copilot-plugins
copilot plugin update --all
copilot plugin uninstall workiq
copilot plugin marketplace update
```

> `copilot plugin update` needs a plugin name **or** `--all`
> Use `--plugin-dir /path/to/plugin` for local plugin development

---

## `copilot plugins` (plural)

One command for **plugins, MCP servers, skills, instructions, LSPs**

```bash
copilot plugins list
copilot plugins list --kind mcp --kind skill
copilot plugins list --scope user --json

copilot plugins install --skill --scope project ./my-skill/SKILL.md
copilot plugins enable github-mcp-server --mcp
copilot plugins disable my-skill --skill
copilot plugins remove spark@copilot-plugins
```

Kinds: `plugin`, `mcp`, `skill`, `instruction`, `lsp`
Scopes: `user`, `session`, `repository`, `working-directory`,
`organization`, `plugin`, `builtin`, `unknown`

> `/plugin` opens the same view as an interactive dashboard
> A `[plugin-dir]` warning about a bundled plugin directory with no `plugin.json` or `SKILL.md` may print first — benign, the listing that follows is complete

---

## Security Checklist

Before installing any plugin:

- Source code is **open and auditable**
- Actively maintained
- Minimal dependencies
- No known vulnerabilities
- Clear permission requirements

```bash
# Restrict plugin capabilities
copilot --allow-tool 'plugin-name' --deny-tool 'shell(rm)'
```

---

## Plugin Capabilities

- **Skills** — reusable instructions
- **Agents** — specialized personas
- **Hooks** — lifecycle automation
- **MCP servers** — tools and resources
- **LSP servers** — code intelligence
- **Marketplace catalogs** — discoverable plugin listings

Hook and plugin scripts receive `PLUGIN_ROOT`, `PLUGIN_DATA`, and
`COPILOT_PROJECT_DIR` (plus `COPILOT_`/`CLAUDE_` variants)

---

## Your Turn! 🚀

Open **Module 7** in `docs/workshop/07-plugins.md`

**Start from Exercise 1** and work through as many as you can

- **Exercise 1** — Explore official plugins
- **Exercise 2** — Explore work-iq-mcp
- **Exercise 3** — Install a community MCP server
- **Exercise 4** — Database plugin integration
- **Exercise 5** — Create a custom plugin
- **Exercise 6** — Plugin security review
- **Exercise 7** — Plugin discovery
- **Exercise 8** — Inspect everything with `copilot plugins`

⏱️ You have **~12 minutes**
