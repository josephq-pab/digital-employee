# EVAL_RULES.md

## 最小验收标准

### 1. 运行验收

- [ ] `scripts/run_dev.sh` 能无报错执行
- [ ] 输出为合法 JSON 格式
- [ ] 输出包含所有 OUTPUT_SCHEMA 字段

### 2. 逻辑验收

- [ ] 风险等级为"高"时，`escalation_recommended` 必须为 `true`
- [ ] 风险等级为"中"时，`escalation_recommended` 应为 `false`（但含建议动作）
- [ ] `reasoning.facts_extracted` 非空（必须从输入提炼事实，不能为空）
- [ ] `reasoning.rules_applied` 非空（必须列出应用规则）

### 3. 区分度验收

- [ ] 同一项目，改变 `escalation_requested: true`，输出中 `escalation_recommended` 必须为 `true`
- [ ] 无风险点 + 进度正常 → 评级必须为"正常"
- [ ] 有风险点自述 + 滞后描述 → 评级必须为"关注"或更高

### 4. 可复核性验收

- [ ] `reasoning.raw_signal` 必须包含触发判断的原始关键词
- [ ] 人工阅读 `reasoning` 后可独立判断结论是否合理

## 测试用例清单

| 用例ID | 输入特征 | 预期风险等级 | 预期升级 |
|--------|----------|--------------|----------|
| TC01 | 正常进度，无风险点 | 低 | false |
| TC02 | 进度滞后，有风险自述 | 中 | false |
| TC03 | escalation_requested=true | - | true |
| TC04 | 进度严重滞后（"严重"关键词） | 高 | true |
| TC05 | 空白risk_points+正常进度 | 低 | false |
