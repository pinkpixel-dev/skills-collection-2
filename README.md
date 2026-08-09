# Skills Collection 2

A large collection of AI/agent skills, resources, references, scripts, and supporting assets.

Related repos:

- This repo: `https://github.com/pinkpixel-dev/skills-collection-2`
- Companion repo: `https://github.com/pinkpixel-dev/skills-collection-1`

## Install

You can install these skills manually for your agents. Examples for Claude Code, Codex, and Antigravity below. Claude users can also install the complete collection as a plugin.

### Download the repository

Clone the repository:

```bash
git clone https://github.com/pinkpixel-dev/skills-collection-2.git
cd skills-collection-2
```

You can also download the repository as a ZIP file from GitHub and extract it on your computer.

### Choose an installation scope

A global installation makes a skill available across your projects. A workspace installation keeps the skill inside one project.

| Provider | Global directory | Workspace directory |
| --- | --- | --- |
| Claude Code | `~/.claude/skills` | `<workspace-root>/.claude/skills/` |
| Codex | `~/.codex/skills` | `<workspace-root>/.codex/skills` |
| Antigravity | `~/.gemini/config/skills/` | `<workspace-root>/.agents/skills/` |

Replace `<workspace-root>` with the path to your project before you run a workspace command.

### Copy the skill folders

Choose one or more folders from this repository's `skills/` directory. Copy each complete folder into the directory for your provider and scope.

For example, this installs `avoid-ai-writing` globally for Codex:

```bash
mkdir -p ~/.codex/skills
cp -R SKILLS/avoid-ai-writing ~/.codex/skills/
```

This example installs the same skill globally for Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -R SKILLS/avoid-ai-writing ~/.claude/skills/
```

This example installs it globally for Antigravity:

```bash
mkdir -p ~/.gemini/config/skills
cp -R SKILLS/avoid-ai-writing ~/.gemini/config/skills/
```

To install every skill, copy all folders inside `skills/` into the selected provider directory. Keep each skill as a separate folder.

After the copy is complete, restart or reload your provider so it can discover the new skills.

## License

[Apache 2.0](LICENSE). Imported skills can include their own license or attribution files. Keep those files with the skill.

Made with 💖 by [Pink Pixel](https://pinkpixel.dev)
