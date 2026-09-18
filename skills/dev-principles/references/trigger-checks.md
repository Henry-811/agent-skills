# 实现触发式强制检查

只在命中具体语义风险时执行，**不是**开局全量跑 checklist。代码形态用于发现候选风险，不能跳过语义前提直接判违规。grep 是定位线索，还需沿注册表、接口实现、依赖注入和动态分发追踪实际调用路径。

每一条都是 **MUST**（R7 带 schema staging 例外）。这些规则覆盖 LLM 实现时最容易偷懒的盲区：名字相似就猜、在看见的入口补 gate、测试跑在便利路径而不是产品默认路径——靠 grep / lookup / signature 对照就能抓到，但默认不会做。

| # | 触发条件 | 必须做的检查 |
|---|---|---|
| **R1** | 新增 gate / filter / permission / source / stale / visibility / 任何"过滤数据"的判断 | 从数据定义或字段名出发 grep 所有 readers / writers / service entrypoints，列全部消费这份数据的位置，确认 gate 放在**数据流必经处**而不是"当前在改的入口"。**ANTI-PATTERN**：只在当前改动文件内补 gate。 |
| **R2** | 调 helper / service 有 ≥2 个同类型且语义不同的 positional args（如 file id 与 store id） | 查实际 signature 和 model 契约，记录每个参数的语义来源。可控接口用 keyword args / named options / wrapper type 消除歧义；固定第三方或 positional-only API 不能改签名时，用清晰具名局部变量和参数映射测试验证，不为语法形式强造一层 wrapper。同质集合、坐标/数学运算等本来按位置定义的接口不因此强制改造。 |
| **R3** | 新增 raise / 新异常类型 / 改异常语义 | grep 上游所有 `except` / middleware / global handler / promise `.catch`，确认不会被 broad except 吞掉或错误地映射成无关错误码。**ANTI-PATTERN**：新增 raise 时不查上游捕获点。 |
| **R4** | SQL / ORM predicate 涉及 nullable column 且用 `!=` / `<>` / `NOT IN` / `NOT LIKE` | NULL 三值逻辑：`NULL != 'x'` 评估为 NULL 而不是 TRUE，WHERE 当 false 处理。需要"不等于且包含 NULL"时用 `IS DISTINCT FROM`（Postgres）或显式 `OR col IS NULL`。**ANTI-PATTERN**：把 Python `!=` 的语义直接套到 SQL nullable column。 |
| **R5** | 用 fake / mock / local fallback / in-memory provider 验证受本次变更影响的 provider 或集成行为 | 查明 production **default** invocation 的 provider、backend、branch/config 和 SQL 路径，至少一条 case 在隔离环境执行相同实现与关键查询语义。不是要求访问生产；纯逻辑单测可隔离无关依赖。外部服务不可用时提供契约测试与未验证项，不能宣称真实集成已通过。**ANTI-PATTERN**：用 LocalDocumentProvider 证明 PgvectorProvider 行为；用 SQLite 测试代替 PostgreSQL 方言、扩展或并发语义验证。 |
| **R6** | 新增字段 / 复用相似字段名 / 跨模块借用 model 属性 | 查 model / schema / migration / API contract，确认字段语义而非凭名字猜。相似名字字段（如 `openai_file_id` vs `vector_store_id`、`student_id` vs `student_user_id`）必须看 column 定义 + 写入点 + 读取点，再决定用哪一个。**ANTI-PATTERN**：按字段名相似度推断 API 参数语义。 |
| **R7** | 新增 boolean / timestamp / enum 状态字段（stale / locked / archived / banned / approved / deleted_at 等） | 同一变更集定义：(a) 写入触发者；(b) 读取/gate 消费者；(c) 退出/恢复语义，包括权限、重试和并发约束。有意不可逆的终态或审计事实必须说明不可逆理由、重复操作和后续行为，不强造“清除历史”功能。纯 schema staging 可暂不启用，但必须标注 inert 状态及后续启用点；参与生产行为前生命周期须闭环。 |
| **R8** | 新增或保留跨版本 compatibility alias、deprecated path、legacy/compatibility fallback、双读/双写，或破坏性删除/重命名可能被跨边界、跨部署或持久化消费的 API、event/job payload、schema、外部配置等契约 | **兼容不是默认。**先完成四类取证：(a) grep 静态 readers / writers / callers，并确认契约是否已发布或对外承诺；(b) 已有生产环境时，仅在任务范围已授权的前提下，用批准的只读渠道和最小权限聚合指标、调用遥测或计数查询确认使用与存量，禁止为取证导出敏感 payload；无访问权时记录 operator attestation 或将该项标为 unknown，未发布/无生产数据时记录事实；(c) 确认能否维护窗口原子切换，还是存在旧新版本混部；(d) 确认回滚代码是否依赖旧路径。证据确认无影响时，当前变更直接删除旧路径和断言旧行为仍可用的测试；保留断言旧输入被拒绝/剥离、旧响应字段不再暴露、历史数据只由 migration 消费、downgrade/restore 正确以及审计/安全边界的测试。证据不足时先补证据，不能用 compatibility 代替调查；若因时限必须推进，须由风险 owner 明确接受未知项并选择保守方案。确认有影响时，能协调全部消费者可采用有 preflight、备份/回滚和验证的受控切换；存在独立消费者或混部窗口时才采用有界兼容，并记录 owner、退出条件/信号、最晚移除版本或日期及删除任务。纯进程内私有实现重命名，以及 resilience/degradation、测试 provider 等非旧契约 fallback 不触发 R8，但仍须执行各自适用的静态引用、类型检查、R5 和测试验证。**ANTI-PATTERN**：因“可能有人使用”永久保留兼容层；只做 expand / migrate 而不安排 contract；把旧测试本身当作兼容需求证据。 |
| **R9** | 前端测试涉及 Hook/effect、异步 coordinator、subscription、polling、timer、请求取消/竞态，或服务端状态向本地状态收敛 | 定位 production 入口和真实 coordinator/effect；至少一条测试通过会执行 effect 的 renderer/harness 挂载该入口，使用框架认可的 `act` / flush 机制等待状态收敛，并断言触发、异步副作用和最终状态。只 mock 网络、时钟、浏览器 API 等外部边界；把 `useEffect` 设为 no-op、直接返回伪 Hook 状态、仅测试 reducer/纯函数或手工调用内部 callback 都不能作为该异步行为的覆盖证据。存在 cleanup、取消、过期响应或重复订阅风险时同步覆盖退出/恢复路径。**ANTI-PATTERN**：测试从未运行 production effect，却因为断言了初始 render 就宣称 Hook 已覆盖。 |

未来某条规则仍频繁漏抓，再评估静态检查、测试或阻断式 hook。仅注入 additionalContext 的 hook 是提醒，不是强制执行保障；不能用“hook 已注入”证明 skill 已加载或检查已完成。

---
