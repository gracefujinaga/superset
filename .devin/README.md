# Devin CLI Integration for Apache Superset

This directory contains Devin CLI configuration for the Apache Superset project.

## Setup Overview

Devin CLI is integrated into this repository to provide AI-assisted development capabilities. The configuration includes:

### Configuration Files

- **`.devin/config.json`** - Project-level configuration with permissions and import settings
- **`.devin/config.local.json`** - Personal overrides (gitignored)
- **`.devin/mcp_config.json`** - MCP server configurations
- **`.devin/mcp_config.local.json`** - Personal MCP server overrides with secrets (gitignored)

### Skills

Custom skills are available in `.devin/skills/`:

**Development Skills:**
- **`precheck`** - Run pre-commit validation on staged files
- **`test-run`** - Run pytest tests with appropriate configurations  
- **`frontend-dev`** - Start the React/TypeScript development server
- **`backend-dev`** - Start the Flask backend development server
- **`github`** - Interact with GitHub repositories through GitHub MCP integration

**Nightly Scan Skills:**
- **`security-check`** - Perform comprehensive security analysis
- **`bug-scan`** - Identify existing bugs and defects
- **`latent-bugs`** - Detect hidden bugs and edge cases

### Rules

- **`AGENTS.md`** - Project-specific development guidelines and context (also linked as `CLAUDE.md`, `GPT.md`, `GEMINI.md`)

## Usage

### Running Skills

Invoke skills using the `/` command:

**Development:**
```
/precheck        # Run pre-commit validation
/test-run         # Run tests
/frontend-dev     # Start frontend dev server
/backend-dev      # Start backend dev server
/github           # Interact with GitHub repositories
```

**Nightly Scans:**
```
/security-check   # Perform security analysis
/bug-scan         # Identify bugs and defects
/latent-bugs      # Detect hidden bugs and edge cases
```

### Nightly Scan Automation

The repository includes a GitHub Actions workflow for automated nightly scans:

**Workflow:** `.github/workflows/nightly-scan.yml`

**What it does:**
- Runs automatically every night at 2 AM UTC
- Executes the three scan skills sequentially
- Generates comprehensive reports
- Creates PRs with fixes when issues are found
- Comments on clean runs when no issues are found
- Uploads scan results as artifacts

**Skills used:**
1. **Security Check** - Identifies vulnerabilities and security issues
2. **Bug Scan** - Detects existing bugs and defects
3. **Latent Bugs** - Finds hidden bugs and edge cases

**Output locations:**
- Scan results: `scan-results/` directory
- Reports: `reports/` directory
- GitHub Actions artifacts (30-day retention)

**Manual triggering:**
You can manually trigger the workflow from GitHub Actions tab or use:
```bash
gh workflow run nightly-scan.yml
```

**Observability:**
- Summary statistics (total findings, by category, by severity)
- Trend analysis over time
- Coverage statistics
- Performance metrics
- Comparison with previous scans

### Permissions

The configuration pre-approves common development commands:
- File read/write operations
- Git commands
- Python/pip/poetry commands
- npm/npx/node commands
- pre-commit hooks
- Docker commands
- GitHub MCP tools (except delete_repo)

Destructive commands like `sudo` and `rm` are denied for safety.

### Development Workflow

1. Make your changes
2. Run `/precheck` to validate code quality
3. Run `/test-run` to execute relevant tests
4. Commit and push

## Configuration Details

### Permissions

The `config.json` allows common development tools and commands while blocking dangerous operations. Modify these permissions as needed for your workflow.

### Import Settings

Devin CLI imports configuration from:
- Cursor (`.cursor/rules/`)
- Windsurf (`.windsurf/rules/`)
- Claude Code (`.claude/`)

This ensures compatibility with other AI coding tools you may use.

### MCP Servers

Devin CLI is configured with MCP servers for extended capabilities:
- **GitHub** - For GitHub API access (configure token in `.devin/mcp_config.local.json`)

#### GitHub Integration

The GitHub MCP server enables the AI agent to interact directly with GitHub through natural language:

**Capabilities:**
- Repository management (create, search, get repo info)
- File operations (create/update files, push changes, get contents)
- Issue management (create, list, update issues)
- Pull request operations (create, review, merge PRs)
- Code search across repositories
- Branch and git operations

**Setup:**

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with `repo` scope (or more specific scopes as needed)
   - Copy the token

2. Add the token to `.devin/mcp_config.local.json`:

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

**Usage Examples:**
- "Create a new issue for the bug in the login form"
- "Review the latest PR and add comments"
- "Search for repositories that use React and TypeScript"
- "Create a new branch and update the README file"
- "Get the commit history for the main branch"

**Permissions:**
- All GitHub MCP tools are allowed except `delete_repo`
- Configure additional restrictions in `.devin/config.json` if needed

### AGENTS.md

The project's `AGENTS.md` file contains Superset-specific development guidelines, including:
- Pre-commit requirements
- Code standards (TypeScript, Python typing)
- Testing strategies
- Security guidelines
- Architecture patterns

This context is automatically available to Devin CLI during sessions.

## Getting Started

If you're new to Devin CLI:

1. Ensure Devin CLI is installed
2. Navigate to this project directory
3. Start a Devin CLI session
4. Use `/help` to see available commands
5. Invoke skills using `/skill-name`

## Customization

### Adding New Skills

Create a new skill in `.devin/skills/your-skill/SKILL.md`:

```markdown
# Your Skill Name

Description of what the skill does.

## Usage

```
/your-skill [args]
```

## What it does

Detailed explanation of the skill's behavior.

## Context

Any relevant context about when to use this skill.
```

### Modifying Permissions

Edit `.devin/config.json` to add or remove permissions:

```json
{
  "permissions": {
    "allow": ["Exec(your-command)"],
    "deny": ["Exec(dangerous-command)"]
  }
}
```

### Personal Overrides

Use `.devin/config.local.json` for personal settings that shouldn't be committed:

```json
{
  "permissions": {
    "allow": ["Exec(personal-tool)"]
  }
}
```

This file is automatically gitignored.

## Support

For Devin CLI documentation, see: https://devin.ai/docs

For Superset development guidelines, see: `AGENTS.md` in the project root.