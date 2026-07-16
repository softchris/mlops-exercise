---
emoji: 🧭
description: Triage new issues by type and priority, detect duplicates, request missing details, and assign ownership.
on:
  issues:
    types: [opened, reopened]
  roles: all
permissions:
  contents: read
  issues: read
  pull-requests: read
tools:
  github:
    mode: gh-proxy
    toolsets: [default]
safe-outputs:
  add-labels:
    allowed: [type:bug, type:feature, type:question, type:docs, type:maintenance, priority:p0, priority:p1, priority:p2, priority:p3, status:needs-info, status:duplicate, status:triaged]
    max: 10
  add-comment:
    max: 1
  assign-to-user:
    allowed: [softchris]
    max: 1
  close-issue:
    state-reason: duplicate
    max: 1
---

# Issue Triage

## Task

Triage the newly opened issue.

1. Classify the issue and add exactly one `type:*` label and exactly one `priority:*` label.
2. Check for likely duplicates by comparing title, symptoms, stack traces, and affected files with existing issues.
3. If the report is unclear or missing key context, add label `status:needs-info` and post one concise comment with clarifying questions.
4. If it is a clear duplicate, add label `status:duplicate`, comment with the matching issue reference and rationale, then close as duplicate.
5. If it is actionable and not a duplicate, add label `status:triaged` and assign to `softchris`.

## Triage rules

- Type labels:
  - `type:bug` for incorrect behavior, errors, regressions
  - `type:feature` for feature requests or enhancements
  - `type:question` for support or usage questions
  - `type:docs` for documentation-only requests
  - `type:maintenance` for refactor/dependency/chore work
- Priority labels:
  - `priority:p0` blocker, critical outage, security risk, data loss
  - `priority:p1` high impact and urgent, no reliable workaround
  - `priority:p2` normal priority
  - `priority:p3` low impact or nice-to-have

## Safe Outputs

- Use configured safe outputs only: `add-labels`, `add-comment`, `assign-to-user`, `close-issue`.
- Use `noop` with a short reason if no visible action is needed.
