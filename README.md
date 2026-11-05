# github-actions-public

These actions are built for Kubecost's own repositories. They are published openly so that the open-source projects
that use them, and anyone else, can see exactly what runs in their workflows. You are welcome to use them, but they
are not supported as a general-purpose product.

Public GitHub Actions maintained by Kubecost. Each action lives in its own folder and is used as
`kubecost/github-actions-public/<action>@<commit-sha>`.

| Action                                 | What it does                                                                |
| -------------------------------------- | --------------------------------------------------------------------------- |
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

The license is intentionally the same as upstream [PR-Agent](https://github.com/The-PR-Agent/pr-agent)'s
[LICENSE](https://github.com/The-PR-Agent/pr-agent/blob/main/LICENSE), including its copyright line, because
`kc-pr-agent` runs a build of that project.
