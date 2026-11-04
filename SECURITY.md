# Security Policy

This repository publishes GitHub Actions that other repositories run with their own tokens and cloud credentials, so
supply-chain integrity matters more than usual.

## Reporting a vulnerability

Report privately through GitHub: <https://github.com/kubecost/github-actions-public/security/advisories/new>.
Please do not open a public issue. This also covers a vulnerability in a runtime image that an action runs; we will
route it to the right maintainers.

## Consuming these actions safely

- Pin to a full commit SHA, not a tag or branch, and keep the release tag in a trailing comment.
- Everything in the `env` of the step that calls an action can reach it. Keep unrelated secrets out of that step.
- Each action pins its runtime image by tag and digest (`<image>:<tag>@sha256:<digest>`). The digest is what runs.
- Grant the job the least `permissions` the action's README lists.

## How this repository is maintained

- Third-party actions are pinned to a commit SHA with a version comment, and updated through Dependabot.
- Runtime image pins are refreshed by a reviewed pull request, never applied automatically.
- Workflows declare minimal `permissions`; `pull_request_target` is not used to run pull-request code.
