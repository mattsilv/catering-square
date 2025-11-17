# Workflow Guidelines

## Before Starting

- Start from GitHub issue (create with approval if missing)
- Review README.md table of contents for project context

## Issue Workflow (Plan → Implement → Validate)

### Planning Phase

- Document plan in issue before coding (no ad-hoc changes)
- Use context7 API for dependency/cloud best practices
- If multiple valid solutions exist, ask brief clarifying question

### Issue Format

- Keep issues concise: include key file paths, edge cases, and success criteria
- Before closing: validate success and comment results
- Log unexpected findings during work

### Validation Phase

Before marking complete: run success validation and document results in issue comment

- Don't write brittle unit tests unless code is genuinely complex
- Do validate the actual feature works as specified before closing issue

## File Documentation

Every non-trivial file needs a top-of-file comment block:

```
Purpose: Handles user authentication and session management
Related: auth_middleware.py, user_models.py, token_service.py
Refactor if: >500 lines OR >5 unrelated functions OR deeply nested logic
```

Include:

- Purpose (1-2 sentences explaining what this file does)
- Related files (key dependencies or files that work with this one)
- Refactoring warnings (file size thresholds, complexity signals)

Common refactoring triggers:

- Backend: >500 lines, >5 top-level functions with unrelated purposes
- Frontend: >400 lines, >3 distinct UI concerns in one component
- Any file: deeply nested logic (>3 levels), multiple responsibilities

## Standard File Structure

### Python Backend

- /routes/ - API endpoint definitions
- /services/ - Business logic (keep routes thin)
- /models/ - Database schemas
- /utils/ - Pure functions, helpers
- /config/ - Settings, environment vars
- Use SQLAlchemy models as single source of truth for data schema; define transformations once in service layer, never duplicate mapping logic across routes
- Run linter (flake8/ruff for Python, ESLint for JS) before committing; auto-fix what's possible, document any ignored rules in issue

### Next.js/React Frontend

- /app/ or /pages/ - Routes (Next.js conventions)
- /components/ - Reusable UI components
- /lib/ - Client utilities, API calls
- /hooks/ - Custom React hooks
- /types/ - TypeScript definitions
- Define API response types once in /types/; use Zod schemas for runtime validation and transformation at API boundaries

**CSS:** Use CSS Modules for component styles; centralize design tokens (colors, spacing, typography) in global variables file

## Documentation & Context

- README.md = token-efficient TOC with minimal context for 10x engineers
- Detailed feature docs in /docs/ folder, linked from README

### Post-Completion Updates

- Update docs with learned nuances from implementation
- Propose global, token-efficient agent instructions (not project-specific rules)

## API/JSON Testing

- Test in /sandbox/[github-issue-number]/ before implementing
- Store real API response examples in codebase near processing logic
- Document exact data traversal method in issue
- Once new API integration code added/tested in prod codebase, delete related sandbox folder

### API Logging (Critical)

Log all external API requests → SQL table with:

- timestamp, response time, object size, raw JSON

Confirm with PM if prod logging required.
Purge: >7 days or >50k rows.

## Success Validation Checklist

Expand validation requirements by type:

- Feature changes: Manual test primary user path (API call → verify response)
- Backend logic: Run relevant function with sample inputs, log outputs
- UI changes: Load affected page/component, verify visual + interaction → capture desktop (1920px) and mobile (375px) screenshots, confirm UI clarity and appropriate spacing
- Integrations: Test sandbox endpoint with real-ish data, capture response  