# Claude Code Adapter

- 使用宿主提供的 Skill 工具加载已安装 skill；显式调用可用 `/skill-name`。缺少相应工具时读取实际 SKILL.md，不宣称执行了不存在的工具。
- 本仓库的用户级安装目标是 `~/.claude/skills`，全局规则目标是 `~/.claude/CLAUDE.md`。
- 仓库内的 CLAUDE.md 通过 `@AGENTS.md` 引入共同规则；安装脚本生成的全局规则则包含共同内容与本适配说明，不引用源码仓库的绝对路径。
- hook 配置须合并到现有 settings.json；不能以仓库模板覆盖整个个人配置。
- 源码在本仓库；安装目录只是副本。不要在安装目录独立维护规则。

参考：[Memory](https://code.claude.com/docs/en/memory)、[Skills](https://code.claude.com/docs/en/skills)、[Hooks](https://code.claude.com/docs/en/hooks)。
