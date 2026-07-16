---
emoji: 🏷️
name: Issue Triage
description: Triage new issues by type and priority, detect duplicates, ask clarifying questions, and assign ownership.
on:
  issues:
    types: [opened]
    roles: all
permissions:
  contents: read
  issues: read
strict: true
tools:
  github:
    mode: gh-proxy
    toolsets: [default]
safe-outputs:
  add-labels:
    allowed:
      - bug
      - documentation
      - duplicate
      - enhancement
      - invalid
      - question
      - wontfix
      - priority:high
      - priority:medium
      - priority:low
    max: 3
  add-comment:
    max: 1
    issues: true
    pull-requests: false
  assign-to-user:
    allowed: [softchris]
    max: 1
    target: triggering
  noop:
    report-as-issue: false
---

# Issue Triage

## Task

Triage the triggering issue. Classify it, check for duplicates, request clarification if needed, and route ownership.

1. Read the issue title, body, existing labels, and author.
2. Search for similar open issues and recently closed issues before deciding whether the issue is a duplicate.
3. Add exactly one type label when confident:
   - `bug` for broken behavior or regressions
   - `enhancement` for feature requests or product improvements
   - `documentation` for docs or content gaps
   - `question` when the issue is primarily a support question or needs clarification
   - `invalid` when it is clearly out of scope or not actionable
4. Add exactly one priority label:
   - `priority:high` for security, data loss, broken core flows, or release-blocking problems
   - `priority:medium` for normal bugs or meaningful feature work
   - `priority:low` for low-impact polish, minor docs fixes, or nice-to-have ideas
5. If the report is unclear or missing key details, add the `question` label and leave one concise comment with only the clarifying questions needed to continue.
6. If the issue is a clear duplicate, add the `duplicate` label and leave one concise comment that links to the canonical issue and explains the match.
7. Assign actionable issues to `softchris`. This repository currently has only one collaborator, so route triaged work there.
8. If no visible change is needed, call `noop` with a short explanation.

## Output rules

- Keep comments short, specific, and friendly.
- Do not invent facts that are not in the issue or the repository context.
- Do not mark an issue as duplicate unless you can cite a specific matching issue.
- Prefer the smallest set of labels needed to express type, priority, and duplicate/question state.
