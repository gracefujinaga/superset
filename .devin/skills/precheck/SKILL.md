# Pre-commit Check

Run pre-commit validation on staged files to ensure code quality before pushing.

## Usage

Invoke this skill after making changes to validate code quality:

```
/precheck
```

## What it does

- Stages all changes
- Runs pre-commit hooks on staged files
- Handles auto-fixes by re-staging and re-running
- Reports any remaining issues that need manual fixes

## Context

Based on the Superset development guidelines, pre-commit should always be run before pushing to match CI and prevent unrelated failures.