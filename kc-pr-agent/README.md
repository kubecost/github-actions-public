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
| `workflow-summary-show-detailed-output` | `true` | Append each tool's output to the job summary. |
| `workflow-summary-show-cost` | `true` | Append estimated AI usage and cost to the job summary. |

## Outputs

| Output | Meaning |
| --- | --- |
| `agent-version` | PR-Agent runtime version, available once the container starts. |

## Configuration

PR-Agent reads its settings from the step's environment, using the names documented upstream
(<https://docs.pr-agent.ai/>): `CONFIG__MODEL`, `GITHUB_ACTION_CONFIG__AUTO_REVIEW`, provider keys such as
`OPENAI__KEY`, and so on. A repository `.pr_agent.toml` can override defaults that the workflow does not set.

**Everything in the calling step's `env` is forwarded into the container**, by name, so values never appear on the
command line. Put only what PR-Agent needs there, and never unrelated secrets.

## Requirements

- A runner with Docker (`ubuntu-latest` works).
- For Bedrock models, AWS credentials from an earlier step (for example `aws-actions/configure-aws-credentials` with
  OIDC). The role needs `bedrock:InvokeModel`, `bedrock:GetInferenceProfile` and `bedrock:ListInferenceProfiles`.
- For the authenticated ECR Public pull, the role also needs `ecr-public:GetAuthorizationToken` and
  `sts:GetServiceBearerToken`. Without credentials the login step is skipped and the pull is anonymous, which can hit
  registry rate limits on busy runners.
- Job permissions: `contents: read`, `issues: write`, `pull-requests: write`, and `id-token: write` for OIDC.

## Versioning and the image pin

Releases are tagged `kc-pr-agent/vX.Y.Z`, with a floating `kc-pr-agent/vX` tag that moves with each release. Prefer a
commit SHA. The runtime image is pinned as `<image>:<tag>@sha256:<digest>` and refreshed weekly by a pull request from
`update-image-pins.yml`, so a new agent release reaches this action only after that pull request is merged. The digest in
`action.yaml` is what runs.

## Known gaps

The `workflow-summary-show-metrics` input arrives with the first runtime release that contains the summary metrics
table; it is added here when the pin advances to that release.
