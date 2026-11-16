# 按用户意图选择组件

先确认结果是否已经在页面中清楚可见。若还需要一个组件，判断用户必须回应吗、稍后还能找到信息吗、是否需要边看主内容边操作。以下是常见分歧，具体名称沿用项目的组件库。

| 用户意图 | 常用选择与适用条件 | 何时换一种做法 |
|---|---|---|
| 得知刚完成的操作 | 简短、可错过的结果可用 Toast。用 Material 风格的 Snackbar 时可附一个可选动作，如“已归档 · 撤销”。部分组件库也支持带动作的 Toast。 | 必须处理的问题留在相关对象旁。失败文件行显示原因和重试入口；影响整个页面的持续状态可用 Banner。关键恢复途径要能在提示消失后找到。 |
| 回应重要后果 | 重要消息需要立即回应才继续时，用 Alert dialog 说明对象、后果和具名选项。普通 Dialog 可承载一个独立短任务，如重命名。 | 能撤销且低代价的高频操作可直接执行并反馈；单纯通知无需模态确认。 |
| 从几种操作中选择 | 桌面对象旁的“更多”适合 Menu；在移动端，用户已经发起一个动作，还要澄清如何执行时可用 Action sheet，如退出时选择保存或放弃草稿。 | 选择字段值优先用 Select；需要输入搜索时考虑 Combobox。Bottom sheet 描述容器，里面也可以放筛选表单，不一定是动作列表。 |
| 查看或编辑附加内容 | 与单个触发点有关的少量控件可用 Popover；查看详情且需连续比对主列表时可用非模态 Drawer。 | 任务需要专注、分多步或应支持独立链接和浏览器返回时，考虑独立页面。模态 Drawer 要能关闭并合理恢复焦点。 |
| 学会下一步 | 一个图标的名字或快捷键可用 Tooltip；当前任务中值得提示的新能力可用教学浮层。多个相互依赖的步骤确实需要演示时，再串成可跳过的 Tour。 | 主操作难以发现时先改善文案、布局或空状态。关键信息提供触屏和键盘可达的入口；需要用户点击按钮的内容使用支持交互的浮层。 |

**跨端例。** 为订单选择状态时，桌面下拉框与手机原生选择器可以写回同一个值。若手机把多个筛选项收进同一面板，需明确是立即应用还是先编辑草稿再统一应用，并说明系统返回或取消对草稿的影响。只有呈现或操作确实不同的地方才分端说明。

**遇到未收录的组件。** 找到它最相近的交互职责，核对当前组件库的官方用法和平台惯例，把选择及验收例写到本次页面方案。有可复用的取舍再补进参考页。

来源：[Material Snackbar](https://developer.android.com/develop/ui/compose/components/snackbar) · [Fluent Toast](https://fluent2.microsoft.design/components/web/react/core/toast/usage) · [Fluent Drawer](https://fluent2.microsoft.design/components/web/react/core/drawer/usage) · [W3C Alert Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/) · [Apple Action Sheets](https://developer.apple.com/design/human-interface-guidelines/action-sheets) · [Fluent Onboarding](https://fluent2.microsoft.design/onboarding)
