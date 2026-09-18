# Codex Adapter

- 按当前可用 skills 清单的实际路径读取 SKILL.md，再读取命中的 references。
- 不依赖 Claude 的 Skill tool。CLI/IDE 可用 `$skill-name` 显式选择；桌面应用可通过 Skills 入口选择。
- 本仓库的用户级安装目标是 `~/.agents/skills`；全局规则目标是 `$CODEX_HOME/AGENTS.md`，未设置 CODEX_HOME 时为 `~/.codex/AGENTS.md`。
- hooks 与规则安装独立。修改 hook 定义后，须经宿主审阅和信任；不得修改信任记录绕过检查。
- 源码在本仓库；安装目录只是副本。不要在安装目录独立维护规则。

参考：[Skills](https://learn.chatgpt.com/docs/build-skills)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Hooks](https://learn.chatgpt.com/docs/hooks)。
