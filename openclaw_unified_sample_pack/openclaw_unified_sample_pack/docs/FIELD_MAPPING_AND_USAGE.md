# 数据源组合关系

## 1. 周报/双周报
- 用途：领导摘要、亮灯/申请事项抽取、周期总览
- 目录：`normalized/weekly_reports/`

## 2. 进展中项目台账
- 用途：项目主数据、主责、完成时间、每周进展文本
- 目录：`normalized/ledgers/`

## 3. 结项/中止表
- 用途：历史办结、中止、暂停目录
- 目录：`normalized/ledgers/closed_terminated_master.json`

## 4. 量化指标表
- 用途：项目/细项的时间序列指标
- 目录：`normalized/metrics/`

## 5. 建议使用顺序
开发 -> 01_dev_core_december
留出验证 -> 02_holdout_validation_november
压力回归 -> 03_stress_regression_aug_sep
正式试运行 -> 05_formal_trial_live_placeholder
