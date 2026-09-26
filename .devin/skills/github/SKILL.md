# GitHub Operations

Interact with GitHub repositories through the GitHub MCP server integration.

## Usage

```
/github [operation] [details]
```

## Examples

- Create an issue: `/github create issue Bug in login form on the authentication page`
- Review a PR: `/github review PR #123`
- Search code: `/github search react components in dashboard`
- Create branch: `/github create branch feature/new-ui from main`
- Get repo info: `/github get repo info`

## What it does

The GitHub MCP server provides comprehensive GitHub API access:
- Repository management (create, search, get info)
- File operations (create/update files, push changes)
- Issue management (create, list, update issues)
- Pull request operations (create, review, merge PRs)
- Code search across repositories
- Branch and git operations

## Requirements

GitHub integration requires a GitHub Personal Access Token configured in `.devin/mcp_config.local.json`:

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

## Context

This skill uses the GitHub MCP server (@modelcontextprotocol/server-github) which provides direct GitHub API access. The agent can perform GitHub operations through natural language requests, making it easy to manage repositories, issues, pull requests, and other GitHub resources as part of the development workflow.