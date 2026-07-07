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
│ Built-in Tools      │ shell, read, write
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
| **github/copilot-plugins** | Official GitHub plugins |
| **github/awesome-copilot** | Community plugins |
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
copilot plugin update
copilot plugin uninstall workiq
copilot plugin marketplace update
```

> Use `--plugin-dir /path/to/plugin` for local plugin development

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

---

## Your Turn!

Open **Module 7** in `docs/workshop/07-plugins.md`

**Start from Exercise 1** and work through as many as you can

- **Exercise 1** — Explore official plugins
- **Exercise 2** — Explore work-iq-mcp
- **Exercise 3** — Install a community plugin
- **Exercise 4** — Database plugin integration
- **Exercise 5** — Create a custom plugin
- **Exercise 6** — Plugin security review
- **Exercise 7** — Plugin discovery

Timebox: **~12 minutes**
