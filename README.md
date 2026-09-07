# No-Mistakes

**Three Claude Code skills that stop an agent substituting reasoning for evidence.**

An agent that reasons its way to "this should work" and an agent that ran the command and read the output produce the same sentence. Only one of them knows. These three skills force the difference at the two moments it costs the most — before you build on a premise, and before you claim you're done.

**Claude Code**

```bash
claude plugin marketplace add Nova-Caelum/no-mistakes
claude plugin install no-mistakes
```

**Codex CLI**

```bash
codex plugin marketplace add Nova-Caelum/no-mistakes
codex plugin add no-mistakes@no-mistakes
```

Same repo, same manifest, no separate build — see [Dual-target](#dual-target-claude-code-and-codex).

## The perimeter

| Skill | Fires | Catches |
|---|---|---|
| **assumption-check** | Before design, architecture, or tool selection | **False premises** — "I assume X behaves like Y" becoming load-bearing before anyone tested it |
| **sequential-thinking** | On complex, multi-step, or uncertain-scope problems | **Linear-only reasoning** — teaches revision, branching, and dynamic extension of the [sequential-thinking MCP](https://github.com/modelcontextprotocol/servers), not just a numbered list |
| **verification-before-completion** | Before "done", "fixed", "passing", commits, PRs, handoffs | **False conclusions** — completion claims without fresh empirical evidence |

The first and last are bookends. `assumption-check` guards the input to your reasoning; `verification-before-completion` guards the output. `sequential-thinking` structures what happens in between.

## Why the pair matters more than either alone

Most verification advice is a single gate at the end. That catches a wrong answer but not a wrong question — by the time the final check runs, the wrong premise has already shaped the architecture, and the check dutifully confirms you built the wrong thing correctly.

Running both means a bad premise gets caught in minutes rather than being discovered days later, downstream, as rework.

`verification-before-completion` ships with four reference files covering the specific ways completion claims go wrong:

- `should-work-without-running.md` — reasoning presented as a result
- `partial-check-treated-as-full.md` — a green check on one layer asserted across all of them
- `assumption-swapped-for-verification.md` — the premise quietly standing in for the evidence
- `trusting-agent-success-reports.md` — a subagent's "done" taken at face value

`assumption-check` ships with `evals/evals.json` for measuring whether it actually fires.

## What's in the box

```
.claude-plugin/
├── plugin.json           # plugin manifest
└── marketplace.json      # this repo is its own marketplace
.mcp.json                 # sequential-thinking MCP dependency
skills/
├── assumption-check/
├── sequential-thinking/
└── verification-before-completion/
```

Installing the plugin brings the MCP server with it — the `sequential-thinking` skill teaches a tool, so the tool ships alongside it. Copying a skill folder by hand does not; in that case install [`@modelcontextprotocol/server-sequential-thinking`](https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking) yourself.

Manifests validate clean under `claude plugin validate . --strict`.

## Dual-target: Claude Code and Codex

This plugin installs on **both** Claude Code and Codex CLI from the same repository. Nothing is duplicated and nothing is conditional — the two ecosystems converged on the same plugin shape, and Codex reads the `.claude-plugin/marketplace.json` in this repo directly.

Verified on Codex CLI 0.145.0:

- All three skills register, namespaced `no-mistakes:<skill>`, and appear in the model-visible prompt.
- The bundled MCP server is contributed by the plugin. Controlled test: `codex mcp list | grep -c sequential-thinking` returns `0` with the plugin removed and `1` with it installed.
- Skills are auto-discovered from `skills/`. No explicit `skills` field is needed in either ecosystem.

Codex additionally supports an `interface` block in `plugin.json` for display metadata. It is deliberately omitted here: Claude Code flags unknown fields, and keeping the manifest clean under `claude plugin validate --strict` is worth more than a nicer plugin-browser tile.

## Cherry-picking a single skill

Skills are self-contained. Copy any one folder from `skills/` into `.claude/skills/` in a project, or `~/.claude/skills/` for every project. Only `sequential-thinking` has an external dependency.

## A note on how these fire

These are behavior-shaping skills, not tools. They earn their keep when they fire *before* the mistake, which means the description block matters as much as the body — it's what the model matches against. If you're adapting them, keep the trigger conditions specific and keep the rationalization tables. The tables name the exact excuses a model uses to talk itself out of running the check, and they are the part that does the work.

They fire on demand, but they're most effective wired into a workflow that guarantees they run.

## Attribution

- **assumption-check** — Nova Caelum.
- **sequential-thinking** — Nova Caelum; guidance layer for the MCP server by Anthropic / Model Context Protocol.
- **verification-before-completion** — adapted by Nova Caelum from [`obra/superpowers`](https://github.com/obra/superpowers) (MIT, © 2025 Jesse Vincent).

MIT licensed. See [LICENSE](LICENSE).

---

Built by [Nova Caelum & Co.](https://novacaelum.com)
