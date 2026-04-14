# OpenClaw 统一样本包

这个样本包把以下几类材料统一成可直接给 OpenClaw 使用的结构化数据：

- 长周期 PMO 周报/双周报样本（2025-04 至 2025-12）
- 进展中项目台账主表及每周快照
- 办结/中止/暂停项目目录
- 定量指标时间序列表
- 推荐切片与未来阶段可直接复用的长指令模板

## 样本包目的
1. 支撑开发阶段
2. 支撑演示阶段
3. 支撑模拟试跑与正式试运行准备
4. 支撑未来切换生产业务数据，只替换数据、不改结构

## 推荐切片
- `slices/01_dev_core_december.json`：开发、调试、冒烟、演示主样本
- `slices/02_holdout_validation_november.json`：Week 3 新样本/留出验证
- `slices/03_stress_regression_aug_sep.json`：高复杂度压力回归
- `slices/04_baseline_transition_apr_jul.json`：早期演化背景样本
- `slices/05_formal_trial_live_placeholder.json`：正式试运行/生产切换占位

## 切换生产数据原则
切换到生产时：
1. 保持 `templates/` 的字段结构不变
2. 替换为新的周报、进展中台账、结项中止表、量化指标表
3. 保持同样的输出口径与目录路径
4. 先跑输入检查，再跑新样本适配验证，再进入正式试运行

## 建议先读
1. `normalized/index/source_manifest.json`
2. `docs/SCHEMA_AND_SLICE_RULES.md`
3. `slices/01_dev_core_december.json`
4. `prompts/00_register_sample_pack.txt`
