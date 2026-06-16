# Project Eye Release Rules

Version: 1.0

Applies To: Contributors, maintainers, AI coding agents, and release operators.

---

## Release Process

Project Eye releases must move through documented validation gates:

1. Confirm current sprint scope.
2. Review product, architecture, API, security, and release documentation.
3. Complete implementation or documentation work.
4. Run required validation checks.
5. Review staged changes.
6. Commit with a logical commit message.
7. Push only validated changes.
8. Prepare release notes or changelog updates when release-facing behavior changes.

Do not release speculative functionality.

---

## Validation Requirements

Every release candidate must verify:

- Scope matches the current sprint.
- No prohibited capabilities were introduced.
- Documentation reflects the implemented system.
- API behavior matches `docs/api/API_SPEC.md`.
- Architecture matches `docs/architecture/ARCHITECTURE.md`.
- Security expectations match `docs/security/SECURITY.md`.
- Deployment checks pass when deployment files are in scope.

For documentation-only phases, validation means Markdown review, consistency review, and staged diff review.

---

## Push Requirements

Before pushing:

- Run the relevant checks for the changed files.
- Review `git status --short`.
- Review `git diff --cached`.
- Confirm no unrelated files are staged.
- Confirm no secrets or local environment files are staged.
- Confirm generated artifacts are excluded.

Pushes must represent coherent, reviewable units of work.

---

## Changelog Requirements

A changelog or release note is required when a change affects:

- User-facing behavior.
- API contracts.
- Architecture decisions.
- Deployment process.
- Security posture.
- Supported version scope.

Documentation-only foundation changes may be summarized in the commit message and pull request description if no formal changelog exists yet.

---

## Rollback Expectations

Every release should be simple to roll back.

Rollback expectations:

- Keep commits focused.
- Avoid mixing unrelated changes.
- Avoid irreversible migrations without a rollback plan.
- Document deployment changes before release.
- Preserve the previous known-good commit.

For Phase 0 documentation releases, rollback is expected to be a standard Git revert.
