#!/usr/bin/env python3
"""Structural validation for the no-mistakes Claude Code plugin.

Not a functional test of the skills themselves (that requires a live Claude
Code session and `claude plugin eval`, which this CI does not run). This
checks the plugin's on-disk contract: manifests parse and carry required
fields, every skill directory has a SKILL.md with valid frontmatter, the
bundled MCP config parses, and the eval fixtures are well-formed.

Exit codes: 0 clean, 1 a check failed.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: invalid JSON ({exc})")
        return None


# plugin.json
plugin_path = ROOT / ".claude-plugin" / "plugin.json"
plugin = load_json(plugin_path)
if plugin is not None:
    for field in ("name", "version", "description", "license"):
        check(field in plugin, f"{plugin_path}: missing required field '{field}'")
    mcp_ref = plugin.get("mcpServers")
    if mcp_ref:
        check((ROOT / mcp_ref).exists(), f"{plugin_path}: mcpServers path '{mcp_ref}' does not exist")

# marketplace.json
market_path = ROOT / ".claude-plugin" / "marketplace.json"
market = load_json(market_path)
if market is not None:
    check("plugins" in market and market["plugins"], f"{market_path}: no plugins listed")
    for entry in market.get("plugins", []):
        src = entry.get("source", "")
        check((ROOT / src).resolve() == ROOT.resolve() or (ROOT / src).exists(),
              f"{market_path}: plugin source '{src}' does not resolve")

# .mcp.json (bundled MCP server config)
mcp_path = ROOT / ".mcp.json"
if mcp_path.exists():
    mcp = load_json(mcp_path)
    if mcp is not None:
        check("mcpServers" in mcp, f"{mcp_path}: missing 'mcpServers' key")

# Every skill directory needs a SKILL.md with name + description frontmatter.
skills_dir = ROOT / "skills"
skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
check(bool(skill_dirs), f"{skills_dir}: no skill directories found")

for sdir in skill_dirs:
    skill_md = sdir / "SKILL.md"
    check(skill_md.exists(), f"{sdir}: missing SKILL.md")
    if not skill_md.exists():
        continue
    text = skill_md.read_text(encoding="utf-8")
    check(text.startswith("---\n"), f"{skill_md}: does not start with YAML frontmatter delimiter")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        check(end != -1, f"{skill_md}: frontmatter block never closes")
        frontmatter = text[4:end] if end != -1 else ""
        check("name:" in frontmatter, f"{skill_md}: frontmatter missing 'name:'")
        check("description:" in frontmatter, f"{skill_md}: frontmatter missing 'description:'")

# eval fixtures, where present, must be well-formed.
for evals_path in skills_dir.glob("*/evals/evals.json"):
    evals = load_json(evals_path)
    if evals is None:
        continue
    check("skill_name" in evals, f"{evals_path}: missing 'skill_name'")
    check(isinstance(evals.get("evals"), list) and evals["evals"], f"{evals_path}: 'evals' must be a non-empty list")
    for item in evals.get("evals", []):
        for field in ("id", "prompt", "expected_output"):
            check(field in item, f"{evals_path}: eval entry missing '{field}'")

if errors:
    print(f"validate-plugin: {len(errors)} finding(s)")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)

print("validate-plugin: clean")
sys.exit(0)
