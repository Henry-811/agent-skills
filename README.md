# Agent Skills

A collection of reusable skills that help coding agents clarify ideas, make better implementation decisions, and verify their work.

Built for developers working with agents such as Codex and Claude Code, these skills capture a development workflow I use and continue to refine: **understand the problem, build the right solution, and check that it works.**

## Why this exists

Coding agents can move quickly from a request to an implementation. But when the goal is unclear, assumptions stay hidden, or business rules are incomplete, writing more code can make the problem harder to solve.

These skills give agents practical guidance for those moments: clarify what a feature means before building it, turn requirements into testable scenarios, inspect the relevant technical risks, and verify the result against the original goal.

The depth of the process should fit the task. A small bug fix should stay small; a new product or a risky change deserves more careful exploration.

## Included skills

| Skill | What it helps with |
| --- | --- |
| [concept-exploration](skills/concept-exploration/SKILL.md) | Clarify the target users, problem, core concepts, assumptions, and MVP before starting a new feature or product. |
| [product-check](skills/product-check/SKILL.md) | Check business rules, user journeys, boundaries, and acceptance scenarios once the direction is clear. |
| [dev-principles](skills/dev-principles/SKILL.md) | Guide implementation and review, with references for architecture, testing, API contracts, observability, and database migrations. |
| [platform-port](skills/platform-port/SKILL.md) | Preserve structure, appearance, and behavior when adapting a web interface to a mini program, app, or WebView. |

The first three skills support the path from an idea to a verified implementation. Use `platform-port` when moving an interface between platforms.

The skill instructions are currently written primarily in Chinese. Feedback on clarity and contributions that make them more accessible in other languages are welcome.

## Install

Use the community [Skills CLI](https://github.com/vercel-labs/skills) with a supported Node.js version:

```sh
npx skills add Henry-811/agent-skills
```

Choose the skills, agents, and installation scope that suit your workflow. To install all four globally for Codex and Claude Code:

```sh
npx skills add Henry-811/agent-skills --skill '*' -a codex claude-code -g
```

To update skills installed through the CLI:

```sh
npx skills update
```

Alternatively, install the collection as a Codex plugin using a CLI that supports `codex plugin`:

```sh
codex plugin marketplace add Henry-811/agent-skills
codex plugin add agent-skills@henry-agent-skills
```

Choose one installation method per environment to avoid duplicate skills. Global rules and optional hooks are separate from skill installation; see [the adapters](adapters/) and [local installation script](scripts/manage.py) for those options.

## Use

Ask your agent to use the relevant skill. For example:

> Use concept-exploration to help me define this feature's purpose, scope, and assumptions before we implement it.

> Use product-check to review these requirements for missing business rules and incomplete user flows.

> Use dev-principles to review this change and identify issues we can verify with code or tests.

These are working guidelines. Their value comes from helping an agent ask better questions, make clearer decisions, and produce evidence for its conclusions.

## Help improve these skills

This collection is a work in progress, shaped by real projects and the mistakes encountered along the way. I would love to hear how it works for you—and where it could be better.

Suggestions, critiques, and contributions are welcome. If a rule is unclear, a workflow feels unnecessarily heavy, or an important scenario is missing, please [open an issue](https://github.com/Henry-811/agent-skills/issues) or submit a pull request.

Concrete examples are especially helpful: what you asked the agent to do, what happened, and what you expected instead. Small, focused improvements are just as valuable as new ideas.

If you change the installation script or hooks, run the existing tests:

```sh
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
