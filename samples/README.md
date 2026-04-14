# OpenClaw 样本包（PMO 周报 + 项目台账）

## 目的
这是一套可直接用于 OpenClaw / 单Agent 项目推进的真实脱敏样本包。
目标是让 Agent 在不依赖当前会话记忆的情况下，完成样本验收、周报与台账对齐、门控更新，并继续推进到实现前收口。

## 目录说明
- samples/weekly_reports/
  - weekly_report_*.json：连续 3 期真实脱敏周报样本
  - weekly_report_series_latest3.json：3 期样本合集
  - weekly_report_series_index.json：样本索引
- samples/project_ledger/
  - project_ledger_latest3.json：项目台账详细样本（含 3 期进展列）
  - project_ledger_latest3_compact.json：项目台账紧凑视图
- samples/linked/
  - weekly_to_ledger_mapping_latest3.json：周报事项与台账条目的对齐结果
- instructions/
  - openclaw_next_step_prompt.txt：给 OpenClaw 的下一段长指令
  - sample_ingestion_checklist.md：收样与验收检查清单

## 推荐使用顺序
1. 先读取 weekly_report_series_latest3.json
2. 再读取 project_ledger_latest3.json
3. 再读取 weekly_to_ledger_mapping_latest3.json
4. 最后执行 instructions/openclaw_next_step_prompt.txt

## 样本定位
- 这批周报样本可视为 S2 级连续真实脱敏样本
- 这批台账样本可视为与周报同周期配套的主数据样本
- 可用于：
  - 输入契约校验
  - 样本验收
  - 周报与台账联动验证
  - 冒烟测试前的数据准备
  - 演示样例固化前的样本对齐

## 说明
- 已去除邮件链、收发件人、抄送、邮箱地址等无关信息
- 保留了项目总览、申请事项、亮灯事项、新增项目、台账主字段、分期进展等关键内容
- 若对齐结果中存在 unmatched 项，需要在样本验收或术语确认环节补充人工判定
