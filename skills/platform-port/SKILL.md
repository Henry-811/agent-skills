---
name: platform-port
description: Web UI 移植到小程序、App 或 WebView 时，对照源码验证结构、主题、交互与运行效果。先核实目标框架、版本和渲染器，再选择平台属性与替代方案；不用于普通 Web 页面开发。
---

# 跨平台 UI 移植规范

## 0. 迁移执行流程

技术规则再完整，不按流程执行就只是文档。以下是迁移任何页面/组件时的**强制执行顺序**。

### 0.1 读完再动手

- **MUST** 完整读完 Web 源文件 — **滚到底**，不是读了前半段就开始写代码
- 对于页面级组件，MUST 展开所有 section/折叠区/modal，确认没有遗漏的功能块
- 读完后列出 Web 页面的**完整结构大纲**（每个 section 的标题、icon、subtitle、子组件），作为后续对照基准

### 0.2 全量枚举差异

- **MUST** 枚举目标页面上**所有可见组件**（Header、Form、Card、Button、Modal、Footer 等）
- 对每个组件逐项比较：结构、颜色、字号、间距、icon、交互状态
- 输出完整差异清单（表格形式），标注每项的严重度
- **ANTI-PATTERN**：只看到最显眼的差异就开始修，修完一个等用户指出下一个

### 0.3 按已授权范围完成

- 按严重度处理已授权范围内的差异；只有改变产品行为、扩大范围或存在不可逆影响时再请求决策
- 完成范围内的修复，不等用户逐项指出；可分批实现和验证
- 修完后做 §10.0 回归验证

### 0.4 先确认目标能力

先读取 lockfile、项目配置与现有组件，记录框架版本、目标平台、基础库、渲染器和设备范围。属性是否存在、支持哪些端、是否必须启用，以该版本官方文档和实际构建为准；以下模板只是示例，不是跨端通用处方。颜色优先读取项目 token 和编译结果，不凭记忆套默认色板。

### 0.5 修完后全页回扫

- 不只检查自己改的组件，检查**整个页面**
- 验证产品支持的全部主题；支持 dark/light 时两者都验证，不为移植擅自新增主题
- 对照 §0.1 的结构大纲，确认没有遗漏的 section

---

## 1. 适用范围

本规范主要适用于 **Web 组件迁移到类 DOM 受限运行时**：
- 微信 / 支付宝 / 字节小程序
- Taro / uni-app 等跨端框架
- H5 容器、WebView 嵌入场景

**React Native / Flutter**：复用本规范中"源码还原、主题审计、编译验证、交互一致性"原则，但布局与样式实现应采用平台原生范式（StyleSheet / Widget），不套用 CSS 思维。

---

## 2. 移植前：读源码，不看截图

- **MUST** 打开 Web 端对应的源文件（TSX/Vue + CSS/Tailwind），提取：
  - 项目实际计算的 CSS/token 值及透明度；同名 Tailwind 类可因版本和主题配置而不同
  - 组件逻辑（hash 算法、分组逻辑、状态机）
  - 交互细节（disabled 状态、hover/active 样式、动画时长）
- **ANTI-PATTERN** 凭截图或记忆"大概还原"颜色/间距/字号。人眼对颜色的判断误差很大，尤其是半透明色和深色背景上的色差。


### 2.1 Tailwind 颜色解析（MUST）

读取项目版本、主题覆盖、CSS 变量和编译结果，再确定色值与 alpha。Tailwind 当前色板使用 OKLCH，项目还可自定义 token；目标平台不支持该色彩语法时，转换为支持的色彩空间并检查色域与视觉误差，不能直接套旧 RGB 表。

参考：[Tailwind Colors](https://tailwindcss.com/docs/colors)。默认色板只在确认项目未覆盖且版本匹配时使用。

---

## 3. 平台限制识别

移植前建立本项目的能力矩阵：目标端/版本/渲染器、组件层级与裁剪、DOM 或模拟 DOM、CSS 变量/布局/动画、滚动、键盘与安全区。每个限制记录官方依据或实际复现；不能把一种小程序渲染器的限制套到所有平台。源码用于还原意图，截图和真机用于验证结果，两者不能互相替代。

---

## 4. 样式移植规则

### 4.1 颜色两条通道

- **CSS 通道**：SCSS/CSS 中的值 → 用 CSS 变量 `var(--text-primary)`，在主题 class 中覆盖
- **组件 props 通道**：先确认组件是否把值交给 CSS、SVG、Canvas 或原生 API；支持 CSS 变量时可沿用 token，否则使用项目主题 resolver 返回实际颜色。不能仅凭它是 inline prop 就判定不支持变量。

**检查方法**：
```bash
grep -rn 'color="\|stroke="\|fill="\|style={{.*color\|style={{.*background' src/
```
确认每个硬编码色值都有主题分支。

### 4.2 主题适配

实现 light/dark 主题时，三层都要覆盖：

1. **Token 层**：沿用项目主题来源与默认模式，不强制 dark 为默认
2. **切换层**：使用项目已有 class、媒体查询或原生主题机制
3. **组件 props 层**：验证图标、Canvas 和原生组件实际接收到的主题值

**ANTI-PATTERN**：只改了 CSS 变量就以为"主题切换完成了"。

### 4.3 新 CSS 颜色值必须走变量（MUST）

写**任何**新的颜色值到 SCSS 时，**MUST** 使用 CSS 变量而非字面量：
```scss
/* WRONG — 下次改主题时必然遗漏 */
background: rgba(23, 23, 23, 0.4);

/* RIGHT — 在 app.scss 的 dark/light 两处定义 */
background: var(--qt-card-bg);
```

**唯一例外**：品牌色常量（如 `#22c55e` emerald、`#f59e0b` amber）在两种主题下视觉一致时，可直接写。但背景色、边框色、叠加层等**一定会随主题变化的值**，必须走变量。

### 4.4 半透明/玻璃效果的平台补偿

先验证目标设备和渲染器是否支持 `backdrop-filter`，再比较截图、背景透出与文字对比度。确实无法等效时采用实色/更高不透明度等明确降级，并记录差异；不存在通用“增加 30-50%”公式，不凭经验百分比改设计。

---

## 5. 布局移植规则

**核心原则：确定性优先。**

### 5.0 布局结构对比（MUST）

移植组件前，先对比 Web 源码的**布局结构**，不只看视觉元素：
- 哪些区域可滚动 vs 固定（`overflow-y-auto` vs `flex-shrink-0`）
- flex 方向和比例分配（`flex-1` vs `flex-none`）
- 组件嵌套层级（面板 A 和面板 B 是同级还是嵌套？是同一个滚动区域还是独立的？）

**ANTI-PATTERN**：只对着截图对比"元素长什么样"，不看"元素怎么排列的"。

### 5.1 确定性布局

在受限平台中，若 flex 布局依赖浏览器特有行为（`min-width: 0`、`width: 0`、`calc()` 在 flex 子项中、复杂 shrink/grow 交互），应优先改为**更确定性的布局方案**：

| 场景 | 推荐方案 |
|------|---------|
| 两栏面板（rail + content） | `position: absolute` + `left/right` |
| 输入框 + 按钮行 | 容器 View 包裹 input 约束宽度，按钮 `flex-shrink: 0` |
| 内容需要滚动 | 若不需要原生滚动能力（下拉刷新、scroll-into-view、滚动事件监听），优先 View + `overflow-y: auto`；否则用 ScrollView 但必须遵守 §5.2 |
| 弹性宽度子项 | 在目标平台已验证 `calc()` 可稳定工作的前提下，显式宽度通常比复杂 flex 收缩行为更可控；否则优先使用绝对定位或外层容器约束 |

**MUST** 表单原生组件（input/textarea）包一层容器 View 来约束宽度，不直接在原生组件上设 flex。

**MUST** 验证 input 的聚焦、裁剪、键盘和尺寸约束。`alwaysEmbed` 在 Taro 文档中是有平台限制的可选属性，不能无条件加到所有 Input 或 textarea。仅在对应组件/版本支持且问题相关时启用同层渲染选项；其他平台查其组件支持表。显式尺寸或容器约束按实际布局选择。

**示例**（仅适用于已确认支持并需要该行为的 Taro Input）：
```jsx
<Input
  className="xxx"
  alwaysEmbed
  style={{ height: '72rpx', lineHeight: '72rpx' }}
  ...
/>
```
使用前核对 [Taro Input 文档](https://docs.taro.zone/docs/components/forms/input) 与项目版本，不能机械复制。

### 5.2 ScrollView 强制检查项

每次使用 ScrollView，**MUST** 验证滚动方向、可用尺寸、溢出、焦点与键盘、嵌套滚动和产品要求的滚动条显隐。`width: 100%` / `box-sizing` 是可选约束，不适用于所有原生框架；`enhanced` / `showScrollbar` 仅在目标端支持时使用。不要为了套模板隐藏滚动条或用 `overflow: hidden` 裁掉焦点、弹层和内容。

### 5.3 结构重组迁移清单

当拆分/重组组件结构时（如把一个滚动区拆成 scroll + fixed），**MUST** 把旧结构的以下属性逐一迁移到新结构的对应元素：
- `width` / `box-sizing` / `overflow`
- `padding` / `margin`
- 主题相关的 CSS 变量引用

**ANTI-PATTERN**：重组布局时只关注新结构的"功能是否正确"，忘记旧结构上已有的约束。

---

## 6. 交互一致性规则

视觉问题比行为问题更容易发现。**MUST** 逐项检查以下行为：

- [ ] 点击态：是否存在延迟或穿透（300ms delay、事件冒泡到下层）
- [ ] disabled：是否真的禁止交互，不只是视觉变灰
- [ ] loading：是否阻止重复提交（按钮加 loading 锁）
- [ ] focus/blur：输入框聚焦行为是否与 Web 一致
- [ ] 键盘弹起：布局是否被顶乱（底部固定栏、绝对定位元素）
- [ ] Drawer/Modal 打开时：底层是否还能滚动（需阻止穿透滚动）
- [ ] 手势冲突：左滑返回 vs 侧边栏手势、下拉刷新 vs 滚动

---

## 7. 文本与滚动检查

受限平台的文本渲染与浏览器有差异，**SHOULD** 检查：

- [ ] 字号、行高、字重是否与 Web 一致（`font-weight: 500/600` 在部分平台不稳定）
- [ ] 文本是否意外换行（中英文混排宽度不同导致换行偏移）
- [ ] 单行截断 `text-overflow: ellipsis` 是否生效
- [ ] 多行省略（`-webkit-line-clamp`）是否支持
- [ ] 数字、时间、按钮文案长度变化后是否撑破布局
- [ ] 字体回退是否一致（系统字体栈在不同平台不同）

---

## 8. 动画与过渡检查

- **SHOULD** 仅使用平台已验证支持的过渡属性（`transform`、`opacity` 最安全）
- **SHOULD** 避免依赖 `height: auto` 动画（大多数受限平台不支持）
- **MUST** Drawer/Modal 动画期间禁止底层穿透点击
- **SHOULD** 动效时长、缓动函数与 Web 对齐，或在平台不支持时做显式降级（如去掉动画，改为直接切换）
- **SHOULD** `transition` 不生效时检查是否因为属性不支持 `transition`（如 `visibility`、`display`）

---

## 9. 平台 API 替代策略

不要在受限平台中使用浏览器 API，按以下映射替代：

| 浏览器 API | 替代方案 |
|-----------|---------|
| `document.querySelector` / DOM 查询 | 状态驱动渲染（React state/context） |
| `element.getBoundingClientRect` | 平台 selector query（Taro: `createSelectorQuery`） |
| `window.addEventListener('resize')` | 平台 onResize / `Taro.onWindowResize` |
| `localStorage` / `sessionStorage` | 平台 storage API（`Taro.setStorageSync`） |
| `window.location` / `history` | 平台 router（`Taro.navigateTo`） |
| `navigator.clipboard` | `Taro.setClipboardData` |
| `navigator.share` | 平台分享 API |
| `new URL()` / `URLSearchParams` | 先确认运行时支持；缺失时用已验证的解析库/平台 API，保留编码、重复参数、相对路径等语义，不手写 split 解析器 |

**关键**：Taro runtime 提供的 `document` 模拟对象**存在但行为不一致**，调用可能导致白屏且无报错。不要因为"不报 ReferenceError"就以为安全。

---

## 10. 编译与运行验证

### 10.0 每次改动后的回归验证（MUST）

**每个可验证的改动批次后做受影响检查，最终完整回扫：**

- [ ] 宽度：内容是否溢出/被截断？（尤其改了布局结构、用了 ScrollView 后）
- [ ] 双主题：dark 和 light 模式下颜色是否正确？（尤其写了新的 CSS 颜色值后）
- [ ] 滚动条：是否意外出现？
- [ ] 已修复的问题是否被回退？（结构重组最容易丢失之前的修复）

**ANTI-PATTERN**：改完代码直接交付，等用户发现问题再修。每次改动都是潜在的回退风险，必须自己先验证。

### 10.1 手工验证

- **MUST** 每次改动后检查编译产物：
  ```bash
  # CSS 改动
  grep "选择器或属性" dist/pages/xxx/index.wxss
  # JS 改动
  grep "函数名或字符串" dist/pages/xxx/index.js
  ```
- **疑似缓存问题**：先确认构建入口、实际输出目录和源码映射。需要清理时只操作已验证属于本项目的可再生成目录，用当前 shell 的原生命令；不能把缓存问题当作所有“改了没生效”的默认根因。
- **元素检查**：用 Wxml + Computed tab 验证实际计算尺寸

### 10.2 自动化扫描（推荐）

对编译产物做静态扫描，拦截常见问题：

```bash
# 扫描候选不兼容 API；区分业务代码、受支持 polyfill 与框架运行时后判断
grep -c "document\.\|window\.\|localStorage\|getComputedStyle" dist/pages/*/index.js

# 扫描未主题化的硬编码深色值（人工 review 结果）
grep -n "rgba(1[0-5]" dist/pages/*/index.wxss

# 扫描可能不支持的 CSS（按平台）
grep -n "position: fixed\|backdrop-filter\|calc(" dist/pages/*/index.wxss
```

### 10.3 双主题验证清单

- [ ] 文字在背景上可读
- [ ] Logo/图标在两种背景上都可见
- [ ] 输入框与背景有足够对比度
- [ ] 头像颜色在两种主题下都合理
- [ ] 分割线/边框在两种背景上可见
- [ ] Drawer/Modal 遮罩层正常

---

## 11. 常见陷阱速查

| 症状 | 根因 | 修复 |
|------|------|------|
| 内容溢出但 `overflow: hidden` 不裁剪 | 可能是布局或原生组件层级 | 核对渲染器与组件支持；必要时使用受支持的同层选项 |
| 改了 SCSS/TSX 但视觉/行为没变 | 可能是错误入口、主题覆盖或编译缓存 | 先定位真实构建/加载路径，再决定是否清缓存 |
| `flex: 1; width: 0` 不约束宽度 | 平台 flex 实现差异 | 用确定性布局（绝对定位、显式宽度） |
| `document.querySelector` 导致白屏 | 小程序无真实 DOM | 不访问 DOM，用状态驱动 |
| 主题切换后部分元素颜色没变 | 可能是颜色未经过主题或原生 API 不支持变量 | 核对 token 流与最终颜色值 |
| ScrollView 内容比容器宽 | 容器/子元素尺寸约束或平台布局差异 | 检查计算尺寸后约束宽度，不盲换滚动组件 |
| 键盘弹起后布局错乱 | 输入框 focus 触发页面 resize | 用 `adjust-position` 属性或监听键盘高度 |
| 字体粗细不一致 | 字体栈、缺失字重或合成字重 | 核对实际字体资源和设备效果，不按固定字重白名单删除设计 |
| 半透明面板或模糊效果不同 | 背景、色彩空间或渲染器支持差异 | 在目标设备截图对比，必要时记录明确降级，无固定补偿百分比 |

---

## 12. 验收产出物

移植完成后至少产出：

- [ ] **Web 源码映射记录**：每个移植组件对应的 Web 源文件路径 + 提取的关键 CSS 值
- [ ] **平台差异与替代方案记录**：遇到的平台限制 + 采用的补偿方案
- [ ] **主题与设备截图**：覆盖产品支持的主题与目标设备；未验证的平台明确列出
- [ ] **自测 checklist 勾选结果**：§10.0 回归验证 + §10.3 双主题验证
- [ ] **已知未对齐项说明**：因平台限制无法完全对齐的项目，标注原因和接受理由
