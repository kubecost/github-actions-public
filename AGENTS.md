# Repository Guidelines

This is a **public** repository of GitHub Actions maintained by Kubecost. It holds one action per top-level folder.
Assume everything here, including commit messages, issues and pull-request text, is world-readable and will be copied
into other organizations' workflows.

- Repository: https://github.com/kubecost/github-actions-public
- Consumers use `kubecost/github-actions-public/<action>@<commit-sha> # <action>/vX.Y.Z`.
- This file is the shared guidance for coding agents. Tool-specific instruction files should import it, not repeat it.

## Public repository rules

- **Never commit** secrets, tokens, account IDs, IAM role names or ARNs, internal hostnames, internal repository
  names, personal paths or email addresses. Examples use placeholders (`<commit-sha>`, `vars.AWS_ROLE_TO_ASSUME`).
- Do not describe internal infrastructure, internal workflows or unreleased product plans in code comments, READMEs
  or examples.
- The code for the actions' runtimes is built and released elsewhere. `kc-pr-agent` only wraps a published image.
  Do not copy runtime source into this repository, and do not link to repositories the public cannot read.
- Treat every input an action receives as untrusted. Examples must gate who can trigger paid or privileged work (for
  example `author_association` checks on comment events, skipping fork pull requests).
- Never use `pull_request_target` or `workflow_run` to check out and run pull-request code.

## Layout

```
<action>/
  action.yaml        # required; the action definition
  README.md          # required; inputs, outputs, permissions, usage with a SHA pin
  examples/          # sanitized, copy-paste workflows
scripts/             # repository tooling (PEP 723 uv scripts)
.github/workflows/   # ci.yml, update-image-pins.yml, release.yml
```

Current actions: `kc-pr-agent` (runs the PR-Agent container; composite action).

## Dos and Don'ts

- **Do** pin every third-party action to a full commit SHA with a version comment on the same line
  (`uses: owner/repo@<sha> # v1.2.3`), the format Dependabot rewrites.
- **Do** pin container images by tag and digest: `<image>:<tag>@sha256:<digest>`. Keep an image reference on **one
  line** in the form `NAME_IMAGE: <image>:<tag>@sha256:<digest>`; `scripts/update_image_pins.py` and
  `scripts/check_actions.py` match that line.
- **Do** declare minimal `permissions` on every workflow and job (start from `permissions: {}` or `contents: read`).
- **Do** keep behavior changes backwards compatible within a major version; a breaking change to inputs, outputs or
  required permissions needs a new major tag and a README note.
- **Do** use `uv` for Python and PEP 723 headers for standalone scripts (`#!/usr/bin/env -S uv run --script`,
  `requires-python`, dependencies), `rich` for console output, and `just` for tasks. Make scripts executable.
- **Don't** add dependencies, new third-party actions or new top-level folders without asking.
- **Don't** reformat or reorder files you are not changing. Match the surrounding style (120-character lines).
- **Don't** hand-edit the image digest in an `action.yaml`; run `just update-pins` and review the diff.

## Commands

| Task | Command |
| --- | --- |
| List tasks | `just` |
| Lint everything (pre-commit: hygiene, actionlint, ruff, action validation) | `just lint` |
| Validate every action (metadata, README, SHA and digest pins) | `just check` |
| Report image pins that are behind the latest stable release | `just pins-check` |
| Refresh image pins (tag + digest) | `just update-pins` |

CI (`ci.yml`) runs pre-commit and `scripts/check_actions.py` on pull requests and `main`. Run `just lint` and
`just check` before every commit.

## Adding an action

1. Create `<action>/` (lowercase, hyphenated) with `action.yaml`, `README.md` and `examples/<name>.yml`.
2. `action.yaml` needs `name`, `description`, `inputs` with descriptions and defaults, and `runs`. Pin every `uses:`
   to a SHA with a version comment and every image to `tag@sha256:digest`.
3. The README documents inputs, outputs, required permissions and credentials, a SHA-pinned usage snippet, and what a
   caller's `env` exposes to the action.
4. Add a row to the table in the root `README.md`.
5. If the action names a container image in a `*_IMAGE` value, use a `public.ecr.aws/...` image so
   `update-image-pins.yml` can refresh it without credentials; otherwise extend `scripts/update_image_pins.py` first.
6. Add the folder to `.github/dependabot.yml` under `github-actions` `directories`.
7. Run `just lint` and `just check`, then open a pull request.

## Releases

Run the `release` workflow (`workflow_dispatch` on `main`) with the action folder and a semantic version. It validates
the actions, tags `<action>/vX.Y.Z`, moves the floating `<action>/vX` tag and creates a GitHub Release with generated
notes. Tags are per action, so releasing one action never moves another's tags. A runtime image bump arrives through
the weekly `update-image-pins` pull request; merging it does not release by itself.

## Commits and pull requests

Use Conventional Commits (`feat:`, `fix:`, `chore(deps):`). One focused purpose per pull request. Do not push, tag or
publish a release without being asked.
