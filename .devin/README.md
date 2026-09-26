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
- **PR tracking data**: `pr_tracking/` directory (historical PR scores and trends)
- **PR scoring dashboard**: `reports/pr-scoring-dashboard.html` (auto-refreshing)

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
- **Engineering Leader Dashboard**: Real-time HTML status dashboard with auto-refresh
- **Metrics & Analytics**: Throughput, effectiveness, and system health metrics
- **Success/Failure Signals**: External notifications for system status
- **Programmatic Session Management**: Full observability with status tracking and progress monitoring
- **PR Scoring Dashboard**: Track PR performance over time with bug detection and fix quality scores
- **Metrics Tracking Dashboard**: Comprehensive time-series tracking of all system metrics

### PR Tracking and Scoring

The system includes comprehensive PR tracking and scoring to measure automation effectiveness over time:

**PR Metrics:**
- **Bug Detection Score (0-100)**: How accurately were bugs identified
  - True positive rate
  - False positive rate
  - Severity accuracy
  - Detection completeness

- **Fix Quality Score (0-100)**: How good were the applied fixes
  - Code quality (linting, style, complexity)
  - Test coverage added
  - Documentation updates
  - No regressions introduced
  - Performance impact

- **Overall Score (0-100)**: Weighted average (40% bug detection, 60% fix quality)
- **Letter Grade**: A (90+), B (80+), C (70+), D (60+), F (<60)

**Features:**
- **Historical Storage**: All PR scores stored in `pr_tracking/` directory
- **PR Tagging**: Automatic PR comments with scores and grades
- **Trend Analysis**: Track scoring trends over time
- **Dashboard**: Real-time PR scoring dashboard with auto-refresh
- **Top PRs**: Identify best performing PRs
- **Grade Distribution**: View distribution of grades across all PRs

**PR Scoring Dashboard:**
- Summary statistics (total PRs, average scores, grade distribution)
- Trend analysis (improving/declining/stable)
- Top performing PRs with detailed scores
- Metric comparison (bug detection vs fix quality)
- Auto-refresh every 60 seconds

### Metrics Tracking Dashboard

**Location:** `reports/metrics-tracking-dashboard.html`

The metrics tracking dashboard provides comprehensive time-series visualization of all system metrics:

**Features:**
- **Recent Trends Card**: Compare last 7 days vs previous 7 days for key metrics
  - Success rate trend
  - Findings per day trend
  - Bug detection score trend
  - Fix quality score trend
  - Overall PR score trend

- **Daily Metrics Table (Last 30 Days)**:
  - Sessions run per day
  - Success rate percentage
  - Total findings per day
  - PRs scored per day
  - Average bug detection score
  - Average fix quality score
  - Average overall score
  - Color-coded values (green ≥80, orange ≥60, red <60)

- **Weekly Aggregates**:
  - Sessions per week
  - Weekly success rate
  - Total findings per week
  - PRs scored per week
  - Weekly average scores
  - Week-over-week comparisons

**Data Sources:**
- Session data from `logs/` directory
- PR scoring data from `pr_tracking/` directory
- Metrics data from `reports/` directory

**Trend Indicators:**
- ↑ Increasing (green)
- ↓ Decreasing (red)
- → Stable (gray)

**Auto-refresh:** Every 60 seconds

### Engineering Leader Q&A

**"Is the system working?"**
- Health Score (0-100) and status (excellent/good/fair/poor)
- Success rate percentage
- Real-time status dashboard with auto-refresh

**"How effective is it?"**
- Quality score (0-100) combining success rate, fix rate, and coverage
- Throughput metrics (sessions per day, findings per hour)
- Average scan time and total findings

**"Are things getting better?"**
- Finding trend (increasing/decreasing/stable)
- Quality trend (improving/degrading/stable)
- Comparison vs baseline with percentage changes

**"Should I be concerned?"**
- Risk level assessment (LOW/MEDIUM/HIGH)
- Attention needed indicators
- Action items with priorities and deadlines

**"Are the PRs getting better?"**
- PR scoring trends (improving/declining/stable)
- Bug detection accuracy over time
- Fix quality improvements
- Grade distribution changes
- Top performing PRs identification

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