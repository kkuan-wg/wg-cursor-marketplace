---
description: Documentation conventions for SDD artifacts, READMEs, and API docs
alwaysApply: false
globs: "**/*.md,**/README*,**/openapi*.yaml,**/openapi*.json,output/**/*"
---

# Documentation Conventions

## READMEs

- Use sentence case for headings.
- Include a **Quick Start** section that gets someone running in five minutes.
- Code examples should be complete and runnable.

## Code comments

- **TypeScript:** Use **TSDoc** / JSDoc for exported public APIs when the project does so elsewhere.
- **Python:** Docstrings on public modules/classes/functions per **PEP 257** / team style.
- Document **why**, not **what**, in inline comments.
- Do not comment obvious code.

## API documentation

- Use **OpenAPI 3.x** for HTTP APIs; keep it aligned with server models (Pydantic, DTOs, etc.) and live routes.
- Include example requests and responses.
- Document **error** responses and status codes, not only success cases.

## Specs and SDD

- Feature specs and **`REQ-...`** traceability live in product-owned docs; link from PRs when required.
- When writing stories, always include the `REQ-...` ID in the story header and in Gherkin scenarios when relevant.
