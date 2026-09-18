# Agent Skills

面向 Codex、Claude Code 等 coding agent 的通用开发方法论与 skills。通用内容只在本仓库维护，宿主差异放在 adapters，安装目录只保存运行副本。

## 内容与边界

| 路径 | 用途 |
|---|---|
| AGENTS.md | 通用开发、协作与评审规则的权威源 |
| CLAUDE.md | Claude Code 的薄入口，通过 import 加载共同规则 |
| skills/concept-exploration | 明确产品问题、核心概念与 MVP |
| skills/product-check | 业务规则、用户流程和验收场景校验 |
| skills/dev-principles | 编码规范、风险路由、R1-R9 与验证细则 |
| skills/platform-port | Web 到其他运行时的 UI 移植检查 |
| adapters/ | 宿主专属说明及 hook 配置片段 |
| hooks/methodology_guard.py | 可选关键词提醒，不是强制执行保障 |
| scripts/manage.py | 用户级安装与只读漂移校验 |
| tests/ | 安装安全性、适配命令与 prompt 回归 |

不分发个人 settings.json、凭证、会话、缓存、插件目录或原配置仓库的 Git 历史。四个自定义 skill 来自迁移前已合并的版本，保留 R8/R9 与跨层不变量台账。

## 从 GitHub 安装

仓库发布到 `Henry-811/agent-skills` 后，可以直接让 Codex 执行：

```text
使用 $skill-installer 从 GitHub 仓库 Henry-811/agent-skills 安装这些路径：
skills/concept-exploration
skills/product-check
skills/dev-principles
skills/platform-port
```

这适合首次安装。内置 `skill-installer` 在目标 skill 已存在时会停止，不负责原地覆盖更新。

## 安装、更新与校验

要求 Python 3.9+。以下命令从仓库根目录执行；系统只有 `python3` 时使用对应命令。

```sh
# 默认只安装四个 skills
python scripts/manage.py install --target codex
python scripts/manage.py install --target claude-code

# 只读检查：缺失、变更、额外文件都会报告并返回非零退出码
python scripts/manage.py check --target codex
python scripts/manage.py check --target claude-code

# 可选：同时安装全局方法论与 hook 脚本
python scripts/manage.py install --target codex --rules --hook-script

# 仓库内容更新后，同步已有运行副本；冲突文件会先备份
python scripts/manage.py install --target codex --replace
python scripts/manage.py install --target claude-code --replace
```

安装目标：Codex skills 为 `~/.agents/skills`，Claude Code skills 为 `~/.claude/skills`。全局规则分别为 `$CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`）和 `~/.claude/CLAUDE.md`。

- 相同文件不重复写入；发现内容冲突时，在写入任何文件前停止。
- 已审阅冲突且需要替换时，可显式加 `--replace`。旧内容备份到 `~/.agent-skills-backups/`，备份中的 paths.txt 按序对应原路径。
- 管理中的 skill 出现额外文件时，即使 `--replace` 也停止；不会删除可能是用户新增的内容。
- 不修改其他 skills、settings.json、config.toml 或 hook 信任记录。批次写入逐文件原子替换，但不承诺整个批次事务性；中断后可先 check，再恢复/重试。
- `--home <目录>` 可选择隔离的用户目录；此时不继承进程的 CODEX_HOME。另有 `--codex-home <目录>` 显式覆盖 Codex 配置目录。
- 全局规则是整份生成文件，不自动合并个人规则。有自定义内容时先审阅并决定保留方式，不直接加 `--replace`。

### 日常更新方式

本仓库是唯一权威源，安装目录只是运行副本。以后在本仓库更新内容后，可以直接告诉 Codex：

```text
检查 agent-skills 与 Codex、Claude Code 已安装 skills 的差异；运行测试，然后用仓库的 manage.py 同步两边。不要改 settings.json、config.toml 或其他 skills；有额外文件或测试失败就停止并报告。
```

Codex 会先运行 `check` 和测试，再用带备份的 `install --replace` 同步。这个流程不会后台自动拉取：如果在另一台机器上使用，还需要先 `git pull`；如果只在当前仓库编辑，则直接同步即可。

## 可选 Hooks

`--hook-script` 只复制脚本，不注册或信任 hook。查看目标宿主的 `adapters/<target>/hooks.example.json`，将对应条目合并到现有配置：Codex 使用 hooks.json，Claude Code 使用 settings.json。保留其他事件/handler，已有同一 handler 时更新而非重复添加。

模板假设 `python` 在宿主 PATH 中；按实际环境选择解释器。Codex 定义变更后需在 `/hooks` 中审阅并信任。关键词提醒可能误报或漏报，不能代替实际读取 skill 与运行验证。

## 项目级使用

仓库本身的 AGENTS.md/CLAUDE.md 只在相应发现范围内生效，不等于其他项目自动加载。上述安装脚本仅实现用户级安装。项目级接入应按各宿主官方规则安装到项目目录，并与已有指令合并；不要把全局安装与项目级安装混为一谈。

## 维护与测试

先修改本仓库，再检查并同步到安装目录，不要在多个副本分别维护规则。

```sh
python -m unittest discover -s tests -v
```

安装测试使用临时目录，不依赖或改写开发者真实的个人配置。Windows 的 Codex hook 模板测试验证含空格的 CODEX_HOME 路径；其他平台会明确跳过该 Windows shell 测试，不宣称已做多平台实机验证。

尚未指定对外分发许可证；发布前应明确许可范围。

## 官方参考

- [Agent Skills 规范](https://agentskills.io/specification)
- [Codex Skills](https://developers.openai.com/docs/build-skills)
- [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Claude Code Memory](https://code.claude.com/docs/en/memory)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
