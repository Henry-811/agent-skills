#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys

def build_response(prompt: str):
    if not prompt.strip():
        return None

    rules = []

    # concept-exploration: 新产品/新业务域/用户可感知新 feature 默认触发；不依赖用户明说"模糊"
    if re.search(
        r"(新产品|新业务域|新功能|新增[^，。；\n]{0,20}功能|新\s*feature|\bnew\s+(feature|product|domain)\b|用户可感知.*(feature|功能)|设计.*(新功能|feature|产品)|产品方向|业务方向|概念|用户场景|MVP|需求不清|逻辑不闭环|产品.*(探索|思路))",
        prompt,
        re.I,
    ):
        rules.append(
            "涉及新产品、新业务域或用户可感知的新功能时，先读取 `concept-exploration`，产出或复用 Concept Brief。只有实质性方向缺口才需澄清；等价规格已明确时不要重复询问。"
        )

    # product-check: 只保留有业务含义的词或短语，去掉"功能/状态/流程"等单字泛词
    if re.search(
        r"(新接口|API|跨模块|业务规则|用户流程|权限|并发|数据模型|schema|状态机|领域|验收标准|新功能|新增[^，。；\n]{0,20}功能|新\s*feature|\bnew\s+feature\b|功能扩展|功能设计|功能验证)",
        prompt,
        re.I,
    ):
        rules.append(
            "业务分析/功能验证若属于中等及以上变更，读取 `product-check`：设计时更新 Feature Spec 与验收场景，验证时对照现有规格给出证据。纯知识讨论不要求生成规格或进入实现。"
        )

    # dev-principles: 动词 AND 代码对象双命中，避免"讨论 hook 设计"误触发
    action_pat = re.compile(r"(写|改|修复|实现|重构|新增|删除|审查|测试|(?<![a-z0-9_])(review|write|edit|fix|implement|refactor|test)(?![a-z0-9_]))", re.I)
    object_pat = re.compile(r"(代码|文件|组件|页面|脚本|函数|类|模块|配置|新功能|新增.*功能|(?<![a-z0-9_])(code|API|hook|skill|bug|feature|config)(?![a-z0-9_]))", re.I)
    # Strip explicit negations, not the entire prompt or a co-located review request.
    clauses = re.split(r"[，。；,;\n]", prompt)
    no_code_pat = re.compile(r"(不写代码|不改代码|不动代码|无需写代码|不要写代码|不要改代码|只讨论不实现|仅讨论不实现|\bdo not (write|edit|change)|\bno code changes\b)", re.I)
    actionable = [no_code_pat.sub("", clause) for clause in clauses]
    if any(action_pat.search(clause) and object_pat.search(clause) for clause in actionable):
        rules.append(
            "编写、修改、重构或审查代码/配置前，读取 `dev-principles` 主文件和命中的 references。检查默认生产路径、参数/异常契约和适用的 R1-R9；按风险验证，不能用 mock 通过冒充真实路径已验证。"
        )

    if not rules:
        return None
    context = "Methodology routing hints (match task intent; keywords are not enforcement):\n" + "\n".join(f"- {rule}" for rule in rules)
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        },
    }


def main() -> None:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError("hook input must be a JSON object")
    prompt = payload.get("prompt")
    if prompt is None or prompt == "":
        prompt = payload.get("user_prompt", "")
    if prompt is None:
        prompt = ""
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    response = build_response(prompt)
    if response is not None:
        json.dump(response, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    for stream, encoding in ((sys.stdin, "utf-8-sig"), (sys.stdout, "utf-8"), (sys.stderr, "utf-8")):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=encoding)
    try:
        main()
    except Exception as exc:
        # Advisory hook: report failures without blocking the user's prompt.
        print(f"methodology-guard hook failed: {exc}", file=sys.stderr)
        json.dump(
            {
                "systemMessage": f"methodology-guard hook failed: {exc}",
            },
            sys.stdout,
            ensure_ascii=False,
        )
