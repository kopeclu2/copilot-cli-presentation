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

# Module 13: Configuration & Environment

### GitHub Copilot CLI Workshop

---

## Topics

- User settings (`settings.json`) and settings scopes
- Environment variables reference
- CLI flags quick reference
- IDE integration (`/ide`, `openDiffOnEdit`)
- Accessibility & streamer mode
- Team configuration standardization
- Logging, debugging, and session limits

---

## Configuration File

User settings live in `~/.copilot/settings.json`:

```json
{
  "model": "auto",
  "theme": "github",
  "mouse": true,
  "beep": false,
  "compactPaste": true,
  "includeCoAuthoredBy": true,
  "updateTerminalTitle": true,
  "streamerMode": false
}
```

Override location: `COPILOT_HOME` env var

> ⚠️ `~/.copilot/config.json` is machine-managed and holds your auth token — **never print or share it**

---

## Settings Scopes

| Scope | Location | Set with |
|-------|----------|----------|
| User | `~/.copilot/settings.json` | `/settings <key> <value>` |
| Repo (shared) | `.github/copilot/settings.json` | `/settings --repo ...` |
| Repo (personal) | `.github/copilot/settings.local.json` | `/settings --local ...` |
| Org-managed | Delivered by policy | Read-only, `managed (read-only)` |

Managed settings apply on top of yours and cannot be edited from the CLI

---

## Key Config Options

| Option | Default | Description |
|--------|---------|-------------|
| `model` | (varies) | AI model |
| `compactPaste` | `true` | Collapse large pastes |
| `copyOnSelect` | macOS only | Auto-copy selection |
| `includeCoAuthoredBy` | `true` | Co-authored-by in commits |
| `streamerMode` | `false` | Hide model names/quota |
| `companyAnnouncements` | `[]` | Team startup messages |
| `ide.autoConnect` | `true` | Auto-connect to IDE |
| `ide.openDiffOnEdit` | `true` | Diffs in IDE |
| `footer.show*` | (varies) | Individual status bar items |
| `sandbox.*` | (varies) | Command sandboxing policy |

> `copilot help config` is the authoritative reference

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `COPILOT_GITHUB_TOKEN` | Auth token (highest priority) |
| `COPILOT_HOME` | Override config directory |
| `COPILOT_MODEL` | Default model |
| `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Extra instruction dirs |
| `COPILOT_EDITOR` | Editor for plans/prompts |
| `COPILOT_PROVIDER_*` | Custom model provider (BYOK) |
| `COPILOT_OTEL_*` / `OTEL_*` | OpenTelemetry monitoring |
| `PLAIN_DIFF` | Disable rich diffs |
| `USE_BUILTIN_RIPGREP` | Set `false` to use PATH ripgrep |
| `NO_COLOR` | Disable color output |

> `copilot help environment` is the authoritative reference

---

## Additional CLI Flags

| Flag | Purpose |
|------|---------|
| `-i, --interactive` | Interactive + auto-execute prompt |
| `--output-format json` | JSONL output for scripting |
| `--stream on\|off` | Control streaming |
| `--acp` | Agent Client Protocol server |
| `--no-ask-user` | Fully autonomous |
| `--max-autopilot-continues` | Limit autopilot rounds |
| `--secret-env-vars` | Redact env values |
| `--no-custom-instructions` | Skip AGENTS.md |
| `--screen-reader` | Accessibility mode |
| `--plain-diff` | Disable rich diffs |
| `--context <tier>` | Context window tier |
| `--log-dir` / `--log-level` | Logging control |
| `--plugin-dir` | Load local plugin |
| `--max-ai-credits` | Session AI credit limit |
| `--session-id` | Set/resume session ID |
| `--remote-export` | Read-only web/mobile export |

---

## IDE Integration

```
/ide          # Connect to IDE workspace
/copy         # Copy last response to clipboard
/settings streamerMode on
```

Config options:
- `ide.autoConnect` — auto-connect on startup
- `ide.openDiffOnEdit` — show diffs in IDE

---

## Team Standardization

```json
{
  "companyAnnouncements": [
    "Remember: never commit secrets",
    "Sprint ends this week"
  ],
  "includeCoAuthoredBy": true,
  "model": "auto"
}
```

Share via repository settings:

```
/settings --repo model auto     # .github/copilot/settings.json
/settings --local theme dim     # settings.local.json (uncommitted)
```

---

## Session Limits

Opt-in soft cap on AI credits for a session

```bash
copilot --max-ai-credits 30     # minimum is 30
```

```
/limits                          # interactive dialog
/limits set max-ai-credits 50
/limits predict
/limits unset max-ai-credits
```

> Usage is only known after a response returns, so one call can
> exceed the limit before the next one is blocked

---

## Your Turn! 🚀

Open **Module 13** in `docs/workshop/13-configuration.md`

**Start from Exercise 1** and work through as many as you can

- **Exercise 1** — Explore settings.json and settings scopes
- **Exercise 2** — Environment variable control
- **Exercise 3** — IDE integration
- **Exercise 4** — Streamer mode & accessibility
- **Exercise 5** — Team configuration
- **Exercise 6** — Logging and debugging
- **Exercise 7** — Session limits and AI credits

⏱️ You have **~14 minutes**

---

# 🎉 Workshop Complete!

### What you've learned across all modules:

Installation → Modes → Instructions → Tools → MCP → Skills → Plugins
→ Agents → Hooks → Context → Sessions → Advanced → Configuration

**Next steps:** Practice daily, create custom agents, share skills with your team

> Resources: [docs.github.com/copilot](https://docs.github.com/en/copilot) · [agentskills.io](https://agentskills.io)
