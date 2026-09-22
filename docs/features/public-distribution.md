# 公开分发

## Concept Brief

目标用户是希望在 Codex、Claude Code 等 agent 中使用这四项方法论技能的开发者。核心问题是避免手动复制技能以及维护多个副本。用户已确认公开 Henry-811/agent-skills、采用 MIT 许可并提供插件打包。

仓库是权威源；skill 是 skills/ 下包含 SKILL.md 的目录；插件将四项技能作为一个版本化包分发。MVP 是公开 GitHub 安装入口、Skills CLI 的发现与安装、Codex 仓库市场安装，以及对应更新说明。发布到官方公共目录、自动修改全局规则/信任配置不在本次范围。

## 规则与验收

| 规则 | Given / When / Then | 验证方式 |
|---|---|---|
| 公开访问 | 无仓库访问凭证的使用者访问仓库时，可以获取四项技能 | 匿名 HTTP 获取 SKILL.md；公开状态检查 |
| 通用安装 | 给定仓库源，Skills CLI 列举并安装时，四项技能及 references 完整落地 | 在临时项目执行真实 CLI 并比较文件 |
| 插件安装 | 给定仓库市场，Codex 安装 agent-skills 时，读取同一份四项技能 | 隔离 Codex 配置目录，执行 marketplace add 和 plugin add |
| 单一源 | 普通技能和插件使用同一 skills/，两个清单使用相同名称和版本 | 清单校验、安装产物比对 |
| 接入边界 | 安装技能或插件时，只增加对应技能/包；全局规则与 hooks 由使用者另行接入 | 无 MCP/hook 配置声明，真实用户配置不参与安装测试 |
| 更新 | 使用者按所选安装工具更新，维护者发布前更新清单版本 | README 分别说明更新入口；初次发布不宣称已验证跨版本升级 |

主流程是选择安装方式 → 从 GitHub 安装 → 在 agent 中调用技能。无网络或权限不足时由安装工具报告失败，恢复网络/权限后重试；已有副本时先审阅替换，避免多种安装工具同时管理同名 skill。

没有业务数据库、API、事务或前端状态变更。本次仅增加分发元数据、许可和文档，保留技能内容与现有同步脚本。

## 首次交付验证

- GitHub 仓库已设为 public；匿名 HTTP 获取 dev-principles/SKILL.md 返回 200。
- plugin-creator 校验器通过；根 plugin.json 通过 Agent Plugins 1.0.0 官方 JSON Schema 校验；两个清单的名称、版本、描述、作者、仓库与许可一致。
- 使用隔离配置目录执行真实 Codex `plugin marketplace add` 和 `plugin add`，成功安装 0.1.0。市场指向仓库根目录，适配本项目单插件布局，不复制技能到另一个源码目录。
- Skills CLI 1.7.0 从本地仓库向临时项目的 Codex、Claude Code 目录安装全部四项技能成功。两套技能副本与插件缓存中的 11 个文件均逐一通过 SHA256 比对。
- 远程 Skills CLI 安装尝试因本机 GitHub HTTPS 连接重置/超时失败；匿名 HTTP 可达不能替代远程 Git 安装验证。插件 GitHub 市场安装需待本次文件推送后验证。
- 未验证跨版本升级或其他操作系统；本次技能内容与同步脚本未修改。
