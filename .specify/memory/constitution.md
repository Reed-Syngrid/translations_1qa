<!--
Sync Impact Report
==================
Version change: (none) → 1.0.0
Modified principles: N/A (initial fill from template)
Added sections: None
Removed sections: None
Templates: plan-template.md ✅ (Constitution Check aligns); spec-template.md ✅ (no change);
  tasks-template.md ✅ (task types compatible); .cursor/commands/*.md ✅ (no CLAUDE refs, constitution refs valid)
Follow-up TODOs: None
-->

# Metabase Translations 1QA Constitution

## Core Principles

### I. Source of Truth

Upstream or authoritative locale files and key sets define what MUST be translated. New keys or
locales MUST align with the declared source; ad-hoc additions without alignment are prohibited.
Rationale: Prevents drift and ensures translations track the actual product surface.

### II. Completeness & Coverage

All required locales and keys MUST be present for a release-ready set. Missing keys for a
declared locale, or missing locales for a declared set, are defects and MUST be tracked and
resolved before sign-off. Rationale: Incomplete translations break UX and accessibility.

### III. Consistency

The same key MUST carry the same meaning and usage across locales. Placeholders, variables, and
format specifiers (e.g. `{0}`, `%s`) MUST be preserved exactly in translations. Rationale:
Prevents runtime errors and preserves functionality across languages.

### IV. Review & QA

All translation changes MUST pass defined QA before acceptance. At minimum: lint/format checks,
completeness checks against the source key set, and optional human or automated review as
defined by the project. Rationale: Catches errors early and maintains quality.

### V. Traceability & Versioning

Translation updates MUST be traceable to the source string set or product version they target.
Changes SHOULD be documented (e.g. changelog or commit scope) so that regressions and
coverage gaps can be investigated. Rationale: Enables audits and safe rollbacks.

## Translation & Locale Constraints

- File format, encoding (e.g. UTF-8), and naming conventions MUST be documented and enforced.
- Locale codes MUST follow a single standard (e.g. BCP 47 / ISO 639) used consistently.
- Technology stack and tooling (e.g. i18n framework, extraction/merge scripts) MUST be
  specified in the implementation plan for any feature touching translations.

## Development Workflow

- New or changed source strings MUST trigger translation workflow (e.g. keys added, strings
  updated, then locales updated or flagged for translation).
- Code review MUST verify that translation-related changes comply with this constitution.
- Before release, a completeness and consistency check MUST be run against the source of truth.

## Governance

This constitution supersedes conflicting local practices for translation and QA work. Amendments
require documentation of the change, approval (as defined by the project), and an update to this
file with version and last-amended date. All PRs and reviews that touch translations MUST verify
compliance with the principles above. Complexity or exceptions MUST be justified and recorded.
Use the project README or agent guidance in `.cursor` for runtime development and command usage.

**Version**: 1.0.0 | **Ratified**: 2025-03-11 | **Last Amended**: 2025-03-11
