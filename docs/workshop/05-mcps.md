# Module 5: MCP Servers

## Prerequisites

- Completed Modules 1-5
- Understanding of JSON configuration
- Node.js and npm installed

## Learning Objectives

- Understand the Model Context Protocol (MCP)
- Configure remote and local MCP servers
- Use the GitHub MCP server for repository operations
- Add custom MCP servers to extend Copilot's capabilities
- Manage MCP servers with slash commands

## Concepts

### What is MCP?

Model Context Protocol (MCP) is an open standard that extends AI capabilities:

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Copilot CLI │────▶│ MCP Server │────▶│ External │
│ │ │ │ │ Resources │
└─────────────┘ └─────────────┘ └─────────────┘
 │
 ┌──────┴──────┐
 │ Tools │
 │ Prompts │
 │ Resources │
 └─────────────┘
```

### Debugging MCP Servers

MCP server errors surface directly in session output and in MCP server details, making it easier to diagnose connection and configuration issues. Errors are displayed when:
- A server fails to start
- A connection cannot be established
- A tool invocation fails
- Configuration is invalid

Use `/mcp` inside a session or `copilot mcp list` / `copilot mcp get <name>` from your shell to inspect configured servers and their status.

### Server Types

| Type | Protocol Name | Location | Use Case |
|------|---------------|----------|----------|
| Remote (HTTP) | `http` | Hosted externally | Team-wide tools, cloud services |
| Remote (SSE) | `sse` | Hosted externally | HTTP+SSE transport |
| Local (STDIO) | `local` or `stdio` | Runs on your machine | Local resources, custom tools |
| Built-in | N/A | Included with Copilot | GitHub integration |

> **Note:** `local` and `stdio` are equivalent in Copilot CLI configuration. The `copilot mcp add` command uses the transport names `stdio`, `http`, and `sse`.

### Configuration Location

> **Note:** Copilot CLI reads MCP configuration from:
> - `~/.copilot/mcp-config.json` (user-level)
> - `.mcp.json` (project-level, in repository root)
> - `.github/mcp.json` (workspace-level)
> - Installed plugins that bundle MCP servers

MCP servers are configured in:
- Default: `~/.copilot/mcp-config.json` (user) or `.mcp.json` (project)
- Custom: Set via `COPILOT_HOME`

Workspace and plugin MCP servers are merged with your personal `~/.copilot/mcp-config.json` configuration.

### Workspace MCP Configuration

Workspace MCP configuration can live in `.mcp.json` or `.github/mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Enterprise Policy Enforcement

> [!IMPORTANT]
> Organization administrators can block third-party MCP servers via policy enforcement. When a policy is active, users in the organization will be prevented from connecting to MCP servers that are not on the allow-list. This is enforced at the CLI level — blocked servers will not start or connect.

> MCP policy enforcement requires a Copilot Enterprise or Business subscription with organization-level policy management. Behavior may vary depending on how your org admin has configured the policy.

### `copilot mcp` CLI Command

> The `copilot mcp` top-level command lets you manage MCP servers directly from the command line without starting an interactive session:
>
> ```text
> # List configured MCP servers
> copilot mcp list
>
> # Add a local stdio server
> copilot mcp add context7 -- npx -y @upstash/context7-mcp
>
> # Add a remote HTTP server
> copilot mcp add --transport http notion https://mcp.notion.com/mcp
>
> # Add a remote server with auth header
> copilot mcp add --transport http --header "Authorization: Bearer token" stripe https://mcp.stripe.com
>
> # Add a local server with environment variables
> copilot mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_xxx -- npx -y @modelcontextprotocol/server-github
>
> # Remove an MCP server
> copilot mcp remove memory
>
> # Show details for a specific server
> copilot mcp get memory
> ```
>
> Additional options for `mcp add`: `--transport` (stdio/http/sse), `--env` (repeatable), `--header` (repeatable), `--timeout`, `--tools` (filter), `--json`, and `--show-secrets`.
>
> This is useful for scripting MCP configuration and managing servers in CI/CD environments.

### MCP Remote Server Auto-Retry

Remote MCP servers (HTTP/SSE) retry transient network failures such as connection timeouts, temporary DNS failures, and HTTP 5xx errors before surfacing the error.

### MCP OAuth HTTPS Redirect

MCP servers using OAuth authentication support HTTPS redirect URIs via a self-signed certificate fallback. This enables OAuth flows in environments where only HTTPS redirect URIs are permitted by the identity provider.

### Built-in GitHub MCP Server Controls

Copilot CLI includes a built-in GitHub MCP server with a default subset of tools. You can customize which tools are available:

```bash
# Add a specific tool to the GitHub MCP server
copilot --add-github-mcp-tool "create_issue"

# Add a toolset (group of related tools)
copilot --add-github-mcp-toolset "repos"

# Enable ALL GitHub MCP tools (overrides --add-github-mcp-tool/toolset)
copilot --enable-all-github-mcp-tools

# Disable the built-in GitHub MCP server entirely
copilot --disable-builtin-mcps

# Disable a specific MCP server by name
copilot --disable-mcp-server "my-custom-server"
```

Use `--add-github-mcp-tool "*"` or `--add-github-mcp-toolset "all"` to enable everything. The `--disable-mcp-server` flag works for any MCP server (built-in or configured), and can be used multiple times.

## Hands-On Exercises

### Exercise 1: Explore the GitHub MCP Server

**Goal:** Use the built-in GitHub MCP server.

**Steps:**

1. Start Copilot:
 ```bash
 copilot
 ```

2. View current MCP configuration:
 ```
 /mcp
 ```

 > The MCP view lists configured servers by source, including user, workspace, plugin, and built-in servers.

3. The GitHub MCP server is pre-configured. Try using it:
 ```
 What are the open issues in this repository?
 ```

4. If you have a GitHub repository:
 ```
 Show me the recent pull requests
 ```

5. GitHub MCP provides tools for:
 - Viewing issues and PRs
 - Reading repository content
 - Accessing organization info
 - Interacting with GitHub resources

**Expected Outcome:**
Copilot can access GitHub resources through the built-in MCP server.

> [!TIP]
> Manually editing `~/.copilot/mcp-config.json` is straightforward. The command structure for MCP config follows the standard MCP specification. Verify the JSON syntax is valid before restarting Copilot.

### Exercise 2: Configure a Remote MCP Server

**Goal:** Add a remote MCP server (Exa search).

[Exa](https://exa.ai) provides AI-powered web search, code search, and company research through a remote MCP server.

**Steps:**

1. View current config file:
 ```bash
 cat ~/.copilot/mcp-config.json
 ```

2. Add the server with `copilot mcp add`:
 ```bash
 copilot mcp add --transport http exa https://mcp.exa.ai/mcp
 ```

3. Verify the configuration:
 ```bash
 copilot mcp get exa
 ```

4. Alternatively, edit the config file directly:
 ```bash
 cat > ~/.copilot/mcp-config.json << 'EOF'
 {
 "mcpServers": {
 "exa": {
 "type": "http",
 "url": "https://mcp.exa.ai/mcp",
 "tools": ["*"]
 }
 }
 }
 EOF
 ```

 > **Note:** Exa's public tools (web search, code search, company research) don't require authentication. Only the corporate/enterprise Exa tools require an API key or OAuth.
 >
 > When editing the config file directly, start a new CLI session or run `copilot mcp list` to verify the stored configuration.

5. Test the Exa search tools:
 ```bash
 copilot
 ```
 ```
 Search the web for current GitHub Copilot CLI features
 ```

**Expected Outcome:**
Remote Exa MCP server configured. Copilot can perform web searches, code searches, and company research via Exa tools.

### Exercise 3: Add a Local MCP Server

**Goal:** Configure a locally-running MCP server.

**Steps:**

1. Install the MCP memory server:
 ```bash
 npm install -g @modelcontextprotocol/server-memory
 ```

2. Add it to your MCP config:
 ```bash
 cat > ~/.copilot/mcp-config.json << 'EOF'
 {
 "mcpServers": {
 "exa": {
 "type": "http",
 "url": "https://mcp.exa.ai/mcp",
 "tools": ["*"]
 },
 "memory": {
 "type": "local",
 "command": "npx",
 "args": [
 "-y",
 "@modelcontextprotocol/server-memory"
 ],
 "tools": ["*"]
 }
 }
 }
 EOF
 ```

 > **Note:** Environment variables referenced in the `command`, `args`, or `cwd` fields are automatically inherited from your shell. Variables that are not referenced in those fields must still be configured in the `"env"` field.

3. Restart Copilot to load the new server:
 ```bash
 copilot
 ```

4. Verify the server is configured:
 ```bash
 copilot mcp list
 ```

5. Test the memory server:
 ```
 Remember that my favorite programming language is Rust
 ```

6. Later in the session:
 ```
 What's my favorite programming language?
 ```

**Expected Outcome:**
Local MCP server runs and provides additional capabilities.

### Exercise 4: File System MCP Server

**Goal:** Add an MCP server for enhanced file operations.

**Steps:**

1. Install the filesystem MCP server:
 ```bash
 npm install -g @modelcontextprotocol/server-filesystem
 ```

 > **Note:** The `~/projects` directory must exist before the filesystem server can start. Create it first with `mkdir -p ~/projects` if needed.

2. Update MCP config with directory restrictions:
 ```bash
 cat > ~/.copilot/mcp-config.json << 'EOF'
 {
 "mcpServers": {
 "exa": {
 "type": "http",
 "url": "https://mcp.exa.ai/mcp",
 "tools": ["*"]
 },
 "filesystem": {
 "type": "local",
 "command": "npx",
 "args": [
 "-y",
 "@modelcontextprotocol/server-filesystem",
 "/home/user/projects"
 ],
 "cwd": "/home/user/projects",
 "tools": ["*"]
 }
 }
 }
 EOF
 ```

 Replace `/home/user/projects` with an absolute path on your machine.


3. Restart Copilot:
 ```bash
 copilot
 ```

4. Check for any MCP server errors:
 ```
 /mcp
 ```

 If there are configuration issues, server status will indicate errors here.

5. Test file operations through MCP:
 ```
 Using the filesystem server, list all TypeScript files in my projects
 ```

**Expected Outcome:**
MCP server provides structured file access with defined boundaries. Any startup errors are visible in the MCP view.

### Exercise 5: MCP Server Management Commands

**Goal:** Master MCP management through the CLI command and interactive MCP view.

**Steps:**

1. **List all servers:**
 ```bash
 copilot mcp list
 ```

2. **Show details for a server:**
 ```bash
 copilot mcp get memory
 ```

3. **Add a new local server:**
 ```bash
 copilot mcp add context7 -- npx -y @upstash/context7-mcp
 ```

4. **Add a remote server with a header:**
 ```bash
 copilot mcp add --transport http \
   --header "Authorization: Bearer $TOKEN" \
   stripe https://mcp.stripe.com
 ```

5. **Use JSON output for scripts:**
 ```bash
 copilot mcp list --json
 copilot mcp get memory --json
 ```

6. **Remove a server:**
 ```bash
 copilot mcp remove memory
 ```

7. **Open the interactive MCP view inside a session:**
 ```bash
 copilot
 ```
 ```
 /mcp
 ```

**Expected Outcome:**
You can manage MCP servers without editing config files and inspect them interactively.

### Exercise 6: Using MCP Tools with Permissions

**Goal:** Control MCP tool access with allow/deny flags.

**Steps:**

1. Allow specific MCP server in programmatic mode:
 ```bash
 copilot -p "Check my GitHub notifications" \
 --allow-tool 'github'
 ```

2. Allow all MCP tools:
 ```bash
 copilot -p "Use memory to store my preferences" \
 --allow-tool 'memory'
 ```

3. Deny specific MCP server while allowing others:
 ```bash
 copilot -p "Analyze the project" \
 --allow-all-tools \
 --deny-tool 'github'
 ```

4. Combine with other tool permissions:
 ```bash
 copilot -p "Review code and check GitHub issues" \
 --allow-tool 'shell(cat)' \
 --allow-tool 'github' \
 --deny-tool 'write'
 ```

**Expected Outcome:**
MCP server tools follow the same permission model as built-in tools.

### Exercise 7: Temporary MCP Configuration

**Goal:** Use additional MCP servers for specific sessions.

**Steps:**

1. Create a temporary MCP config as JSON:
 ```bash
 cat > /tmp/temp-mcp.json << 'EOF'
 {
 "mcpServers": {
 "microsoft-learn": {
 "type": "http",
 "url": "https://learn.microsoft.com/api/mcp"
 }
 }
 }
 EOF
 ```

 > **Note:** The [Microsoft Learn MCP Server](https://github.com/microsoftdocs/mcp) is free and requires no API key. It provides tools for searching Microsoft docs, fetching documentation pages, and finding code samples.

2. Start Copilot with the additional config:
 ```bash
 copilot --additional-mcp-config @/tmp/temp-mcp.json
 ```

3. The temporary servers are available for this session only.

4. Verify:
 ```bash
 copilot mcp list
 ```

5. The base config + temporary config are merged.

6. Test it:
 ```
 Search Microsoft Learn for how to create an Azure Container App with managed identity
 ```

**Expected Outcome:**
Additional MCP servers can be loaded per-session without modifying base config.

## MCP Configuration Reference

### Server Naming

MCP server names (the keys in `"mcpServers"`) support dots (`.`), slashes (`/`), and `@` characters. This enables npm-style names directly as server identifiers:

```json
{
 "mcpServers": {
 "@modelcontextprotocol/server-memory": {
 "type": "local",
 "command": "npx",
 "args": ["-y", "@modelcontextprotocol/server-memory"]
 }
 }
}
```

> npm-style server names may have specific character requirements. Verify server name format with `copilot --help`.

### Remote Server Schema

```json
{
 "mcpServers": {
 "server-name": {
 "type": "http",
 "url": "https://example.com/mcp/",
 "headers": {
 "Authorization": "Bearer ${GITHUB_TOKEN}"
 },
 "tools": ["*"]
 }
 }
}
```

### Local Server Schema

```json
{
 "mcpServers": {
 "server-name": {
 "type": "local",
 "command": "npx",
 "args": ["-y", "@package/server-name"],
 "env": {
 "API_KEY": "${ENV_VAR}"
 },
 "cwd": "~/projects/my-server",
 "tools": ["*"]
 }
 }
}
```

> **Note:** Environment variables referenced in `command`, `args`, or `cwd` are automatically inherited from your shell. Variables not referenced in those fields must still be configured explicitly in the `"env"` field. The `"tools"` field defaults to `["*"]` (all tools) if omitted. You can restrict to specific tools with a list of tool names.

### Common MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| Memory | `@modelcontextprotocol/server-memory` | Persistent memory |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File operations |
| GitHub | Built-in | GitHub integration |
| Exa | `https://mcp.exa.ai/mcp` (remote) | Web search, code search, company research |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Database queries |
| Slack | `@modelcontextprotocol/server-slack` | Slack integration |
| Brave Search | `@anthropic/mcp-server-brave-search` | Web search |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/mcp` | Open the interactive MCP server view |

### Shell Commands

| Command | Description |
|---------|-------------|
| `copilot mcp list` | List configured MCP servers |
| `copilot mcp list --json` | List servers as JSON |
| `copilot mcp get NAME` | Show details for a specific server |
| `copilot mcp add NAME -- COMMAND [ARGS...]` | Add a local stdio server |
| `copilot mcp add --transport http NAME URL` | Add a remote HTTP server |
| `copilot mcp remove NAME` | Remove a server |

## Summary

- ✅ MCP extends Copilot with custom tools and resources
- ✅ Built-in GitHub MCP server provides repository access
- ✅ GitHub MCP server tools/toolsets can be customized with `--add-github-mcp-tool`/`--add-github-mcp-toolset`
- ✅ `--disable-builtin-mcps` and `--disable-mcp-server` for disabling servers
- ✅ Local servers run on your machine for local resources
- ✅ Remote servers connect to external services
- ✅ `copilot mcp` commands manage servers without editing files
- ✅ MCP tool calls display tool name and parameter summary in the timeline
- ✅ MCP servers can request LLM inference (sampling) with user approval
- ✅ MCP server errors surface in session output for easier debugging
- ✅ Org admins can block third-party MCP servers via policy enforcement
- ✅ Server names support npm-style identifiers with `.`, `/`, `@`
- ✅ `--additional-mcp-config` loads temporary servers
- ✅ MCP config loads from user, workspace, plugin, and built-in sources
- ✅ `copilot mcp` CLI command for managing servers from the command line
- ✅ Remote server auto-retry on transient network failures
- ✅ MCP OAuth HTTPS redirect URI via self-signed cert fallback

## Next Steps

→ Continue to [Module 6: Agent Skills](06-skills.md)

## References

- [Adding MCP Servers for Copilot CLI - GitHub Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)
- [About Model Context Protocol - GitHub Docs](https://docs.github.com/en/copilot/concepts/about-mcp)
- [Extending Copilot Coding Agent with MCP - GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp)
- [GitHub MCP Registry](https://github.com/mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
