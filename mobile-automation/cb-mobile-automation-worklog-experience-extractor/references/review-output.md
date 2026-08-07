# Review Output

Use this output shape for retrospective extraction.

## 可沉淀经验

List concise rules, not raw events. Each item should say what future agents should do differently.

## 建议写入已有 Skill

For each item include:

- Target skill or reference.
- Reason.
- Suggested wording if the change is small enough to draft safely.

## 建议新建 Skill

Use only for domains with an independent trigger and workflow. Include proposed skill name, trigger description, and minimal file structure.

## 建议写入项目上下文

Use for repository-specific facts, current status, worktree paths, module progress, or known local tool constraints.

## 建议保留为提示词

Use for reusable but lightweight prompts. Provide copyable prompt text.

## 不建议沉淀

List items that should be ignored or left only in raw logs, with a short reason.

## 需要人工确认的问题

Ask only questions that materially affect persistence:

- Whether a rule should be project-local or reusable.
- Whether a behavior is a preference or a temporary workaround.
- Whether a risky-flow rule is acceptable for future automation.

## Copyable Retrospective Prompt

When useful, provide a prompt like:

```text
请基于本轮聊天记录和项目工作记录，提炼自动化测试工程开发中的可复用经验。

要求：
1. 先找重复性问题和用户多次纠正的地方。
2. 把事件改写成后续 agent 可执行的规则。
3. 区分项目上下文、已有 skill、新 skill、提示词和不建议沉淀。
4. 不保存账号、密码、户号、验证码等敏感信息。
5. 输出候选项给我人工审阅，不要直接改文件。
```
