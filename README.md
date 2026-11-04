# github-actions-public

Public GitHub Actions maintained by Kubecost. Each action lives in its own folder and is used as
`kubecost/github-actions-public/<action>@<commit-sha>`.

| Action | What it does |
| --- | --- |
| [`kc-pr-agent`](kc-pr-agent/README.md) | Runs the PR-Agent AI reviewer (describe, review, improve) on pull requests. |

## Using an action

Pin a commit SHA and keep the release tag as a comment so Dependabot can propose updates:

```yaml
- uses: kubecost/github-actions-public/kc-pr-agent@<commit-sha> # kc-pr-agent/v1
```

Releases are tagged `<action>/vX.Y.Z`, with a floating `<action>/vX` tag. See each action's README for inputs,
permissions and an example workflow, and [SECURITY.md](SECURITY.md) for how to consume them safely.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md). Licensed under the [MIT License](LICENSE).
