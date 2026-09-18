# API 与可观测性

### API 契约设计

- **MUST** API 是跨边界契约，不是实现细节的自然外露。新增或变更 API 前，先明确调用方、使用场景、请求/响应模型、错误语义和兼容性影响；不能边写后端边让前端"看接口猜行为"。
- **SHOULD** REST / RPC / Command API 按语义选择：资源型 CRUD、可缓存读取优先 REST；动作型流程、跨聚合命令、非资源语义优先 RPC/Command。**ANTI-PATTERN**：为了形式上 RESTful，把业务动作硬塞成含糊的资源名。
- **MUST** 删除字段、修改字段语义、改变状态码或错误码等破坏性 API 变更先执行 R8。证据确认无影响时直接删除；证据不足先补证据，不能靠保留 alias 代替调查。确认有影响时按消费者独立性选择策略：能协调全部内部消费者时可受控原子切换，存在独立外部消费者、多客户端版本混部或回滚依赖时使用版本化、灰度、迁移窗口或临时兼容层。临时兼容必须可观测，并同时定义 owner、退出条件/信号、最晚移除节点和删除任务，不得永久化。生产取证必须遵守授权、最小权限和数据最小化要求。
- **MUST** 错误响应结构稳定：至少包含机器可判断的错误码、用户/调用方可理解的消息、必要的 details 和 request/correlation id。调用方不得解析自然语言错误消息来做业务判断。
- **SHOULD** 请求/响应 schema 类型化并可校验；跨前后端协作时，优先通过 OpenAPI/JSON Schema/共享类型生成 client 或校验器，减少手写 DTO 漂移。
- **SHOULD** 写操作如果可能被重试，必须设计幂等策略（Idempotency-Key、业务唯一约束、去重表或天然幂等命令），并明确重复提交的返回语义。
- **SHOULD** 列表 API 明确分页、排序、过滤、总数语义和默认限制；禁止无上限返回集合。

#### API Contract Checklist

新增或修改 API / DTO / 外部服务调用时，必须产出 API Contract：

| 字段 | 要求 |
|---|---|
| 调用方 | 谁调用、为什么调用、同步/异步、是否多客户端或外部公开 |
| Endpoint / Command | REST path + method，或 RPC/Command 名称；说明选择理由 |
| Request | 参数、schema、必填/可选、默认值、校验规则、权限前提 |
| Response | 成功响应 schema、状态码、空结果语义、字段兼容性 |
| Error | 稳定错误结构、错误码、HTTP status / transport status、details、correlation id |
| Idempotency | 写操作是否可重试；幂等键、唯一约束、重复提交返回语义 |
| Pagination / Sorting / Filtering | 列表接口的分页、排序、过滤、total 语义和默认/最大 limit |
| Evolution / Compatibility | 发布状态、静态消费者、经授权的生产调用证据、部署拓扑与回滚依赖；选择直接删除、受控切换或有界兼容。证据未知时列补证据或风险升级动作；若兼容，列 owner、退出条件/信号、最晚移除节点和删除任务 |
| Observability | 关键日志字段、指标、trace/correlation id、告警条件 |

**门槛检查**：调用方需要猜字段语义、错误语义、重复提交行为或分页语义时，API Contract 未闭环，不进入实现。

### 可观测性

- **MUST** 关键用户路径、跨系统边界、异步任务和失败分支必须有可追踪信号。不能只在异常栈里留下线索，也不能只靠用户反馈发现生产问题。
- **SHOULD** 日志使用结构化字段，至少包含事件名、业务主键、request/correlation id、调用方、结果状态和耗时；禁止记录密钥、Token、个人敏感信息或完整大对象。
- **SHOULD** 指标围绕用户影响和系统健康定义：请求量、错误率、延迟分布、队列积压、重试/熔断、关键业务成功率。**ANTI-PATTERN**：只埋无行动价值的计数器，出了问题无法定位影响范围。
- **SHOULD** Trace 跨进程传播 correlation/trace id；外部 API、数据库热点查询、队列任务、长耗时步骤应形成 span，能串起一次用户请求的完整链路。
- **MUST** 会影响用户结果或数据正确性的失败保留可追踪信号，并按影响提供可见错误或告警。无业务影响的幂等清理、遥测自身失败等可按 implementation reference 注明理由后受控忽略；避免日志失败再次写日志形成递归。
- **SHOULD** 异步任务记录生命周期：queued / started / succeeded / failed / retrying / exhausted，并把重试次数、下一次重试时间、最终失败原因暴露给排障入口。
- **SHOULD** 告警必须可行动：绑定明确 owner、影响范围、阈值理由和排障入口。不要对单次可恢复抖动告警；应对持续错误率、SLO burn、队列堆积、数据不一致等用户影响告警。

#### Observability Plan 输出

新增或修改关键路径、异步任务、外部依赖、失败分支、告警或排障入口时，必须产出 Observability Plan：

| 字段 | 要求 |
|---|---|
| 关键路径 | 用户动作、系统边界、异步任务或外部调用链路 |
| 日志事件 | event name、业务主键、correlation/request id、调用方、结果状态、耗时、错误原因 |
| 指标 | 请求量、错误率、延迟、队列积压、重试/熔断、关键业务成功率等可行动指标 |
| Trace | 需要传播的 trace/correlation id、关键 span、外部 API / DB / queue 边界 |
| 告警 | 触发条件、阈值理由、owner、影响范围、排障入口 |
| 隐私与安全 | 禁止记录的密钥、Token、个人敏感信息和完整大对象 |
| 验证方式 | 如何在测试、staging 或生产只读检查中确认信号存在且字段可用 |

**门槛检查**：关键路径失败后无法定位影响范围、业务主键、调用链或最终失败原因时，Observability Plan 未闭环，不进入实现或交付。

---
