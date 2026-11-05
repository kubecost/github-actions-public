# kc-pr-agent

A composite GitHub Action that runs PR-Agent, a self-hosted AI agent that describes, reviews and suggests
improvements for pull requests. It is based on the open-source [PR-Agent](https://github.com/The-PR-Agent/pr-agent).
The action logs in to Amazon ECR Public and runs the published runtime image `public.ecr.aws/u8u5i0e2/kc-pr-agent`,
pinned by tag and digest in `action.yaml`. This folder only wraps that image; the agent itself is built and released
separately.

## Usage

Pin the action to a commit SHA and keep the release tag in a comment:

```yaml
- uses: kubecost/github-actions-public/kc-pr-agent@<commit-sha> # kc-pr-agent/v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    # model and behavior settings, for example CONFIG__MODEL, see below
```

A complete workflow, with the trust checks a public repository needs, is in
[`examples/pr-agent.yml`](examples/pr-agent.yml).

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `artifact_path` | `''` | CI artifact file (relative to `GITHUB_WORKSPACE` or absolute) added as extra context. |
| `artifact_instructions` | `''` | How the model should interpret the artifact. |
| `workflow-summary-show-detailed-output` | `''` (acts as `true`) | Append each tool's output to the job summary. |
| `workflow-summary-show-cost` | `''` (acts as `true`) | Append estimated AI usage and cost to the job summary. |

A non-empty input wins. When an input is empty, the matching variable in the step's `env` is used
(`ARTIFACT_PATH`, `ARTIFACT_INSTRUCTIONS`, `GITHUB_ACTION_CONFIG__WORKFLOW_SUMMARY_SHOW_DETAILED_OUTPUT`,
`GITHUB_ACTION_CONFIG__WORKFLOW_SUMMARY_SHOW_COST`), and if that is unset too the built-in default applies.

## Outputs

| Output | Meaning |
| --- | --- |
| `agent-version` | PR-Agent runtime version, available once the container starts. |

## Configuration

PR-Agent reads its settings from the step's environment, using the names documented upstream
(<https://docs.pr-agent.ai/>): `CONFIG__MODEL`, `GITHUB_ACTION_CONFIG__AUTO_REVIEW`, provider keys such as
`OPENAI__KEY`, and so on. A repository `.pr_agent.toml` can override defaults that the workflow does not set.

Only an allowlist of the calling step's `env` is forwarded into the container, by name, so values never appear on the
command line:

- `GITHUB_*` (the GitHub context and `GITHUB_TOKEN`), `ARTIFACT_*`, `PR_AGENT_*` and `LOG_LEVEL`
- Model provider credentials and settings: `AWS_*`, `OPENAI_*`, `AZURE_*`, `ANTHROPIC_*`, `GOOGLE_*` and `VERTEX*`
- `RUNNER_TEMP`, `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE`
- PR-Agent settings, which are any upper-case name containing a double underscore (`CONFIG__MODEL`, `OPENAI__KEY`,
  `PR_REVIEWER__EXTRA_INSTRUCTIONS`)

Anything else is not forwarded. That includes the runner's OIDC variables (`ACTIONS_ID_TOKEN_REQUEST_URL` and
`ACTIONS_ID_TOKEN_REQUEST_TOKEN`), so granting `id-token: write` does not hand the container the means to mint tokens.
A secret whose name matches the list above still reaches the container, so put only what PR-Agent needs in `env`, and
never unrelated secrets.

## Requirements

- A runner with Docker (`ubuntu-latest` works).
- For Bedrock models, AWS credentials from an earlier step (for example `aws-actions/configure-aws-credentials` with
  OIDC). The role needs `bedrock:InvokeModel`, `bedrock:GetInferenceProfile` and `bedrock:ListInferenceProfiles`.
- For the authenticated ECR Public pull, the role also needs `ecr-public:GetAuthorizationToken` and
  `sts:GetServiceBearerToken`. Without credentials the login step is skipped and the pull is anonymous, which can hit
  registry rate limits on busy runners.
- Job permissions: `contents: read`, `issues: write`, `pull-requests: write`, and `id-token: write` for OIDC.

## Versioning

Releases are tagged `kc-pr-agent/vX.Y.Z`, with a floating `kc-pr-agent/vX` tag. Pin a commit SHA rather than a tag.
Each release pins its runtime image by tag and digest in `action.yaml`, and that digest is what runs.
