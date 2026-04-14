# 阶段4I-R 修订记录

**日期**：2026-04-08
**阶段**：阶段4I-R（基于统一样本包的 Week 3 留出验证）
**版本**：v1.0（首次创建）

---

## 一、阶段概述

本次阶段4I-R 是对原阶段4I（Week 3 未完成）的重启，因：
1. 原样本包（samples/samples/）中 W50/W51/W52 被 Week 1 和 Week 2 共用，无法再作为 Week 3 新样本
2. 统一样本包（openclaw_unified_sample_pack_v2.zip）提供了 November 留出验证集（1103~1128），可用于真正的 Week 3 新样本验证

---

## 二、本阶段新增文件

| 文件名 | 说明 |
|--------|------|
| `src/loaders/november_adapter.py` | November 样本格式适配器（新增） |
| `docs/统一样本包切换记录.md` | 数据源切换记录 |
| `docs/Week3输入检查记录_统一样本包版.md` | November 输入检查 |
| `docs/Week3新样本适配验证记录_统一样本包版.md` | 适配验证记录 |
| `docs/正式MVP试跑Week3运行记录.md` | Week 3 执行记录 |
| `docs/正式MVP试跑Week3周报.md` | Week 3 周报 |
| `docs/正式MVP试跑Week3阶段判断.md` | Week 3 判定 |
| `docs/正式MVP试跑Week3问题清单.md` | 问题清单 |
| `docs/正式MVP试跑Week3观察项清单.md` | 观察项清单 |
| `docs/Week1-Week3试跑趋势总结_统一样本包版.md` | 三周趋势总结 |
| `docs/正式MVP试跑Week4进入条件_统一样本包版.md` | Week 4 条件 |
| `docs/扩大试跑评估更新说明_统一样本包版.md` | 扩大评估更新 |
| `docs/阶段4I-R修订记录.md` | 本修订记录 |
| `docs/阶段4I-R进展报告.md` | 阶段收尾报告 |

---

## 三、本阶段核心发现

### 3.1 数据格式差异

November/December 样本包使用 `alert_lines` 和 `request_lines`（字符串数组），与原型引擎期望的 `key_alerts`/`management_summary`（对象数组）格式不同。December 开发集（W50/W51/W52）也使用相同格式，但原样本包和原型均未做格式对齐。

**解决**：创建 `november_adapter.py` 作为格式适配层。

### 3.2 适配层实现问题

| 编号 | 问题 | 严重度 | 状态 |
|------|------|--------|------|
| W3-P1 | 结项申请内容误合并（request_lines 并列结构） | P2 | 开放 |
| W3-P2 | 延期申请未单独识别（中文引号项目名） | P2 | 开放 |

### 3.3 新增观察项

| 编号 | 观察项 |
|------|-------|
| OBS-W3-01 | 行业维度黄灯跨期重复出现 |
| OBS-W3-02 | 台账匹配率低（行业名 vs 项目名） |
| OBS-W3-03 | 延期申请作为独立事项类型（待 Q01 确认） |

---

## 四、口径更新

| 口径项 | 更新内容 | 版本 |
|--------|---------|------|
| 样本数据根目录 | samples/samples/ → openclaw_unified_sample_pack/openclaw_unified_sample_pack/ | v2.0 |
| 开发/冒烟默认切片 | slices/01_dev_core_december.json | v2.0 |
| Week 3 验证切片 | slices/02_holdout_validation_november.json | v2.0 |
| 压力回归切片 | slices/03_stress_regression_aug_sep.json | v2.0 |
| 正式试跑占位 | slices/05_formal_trial_live_placeholder.json | v2.0 |
| 样本包版本 | openclaw_unified_sample_pack_v2.zip | v2.0 |

---

## 五、受影响文档更新

| 文档 | 更新版本 | 主要变更 |
|------|---------|---------|
| MVP推进路线图.md | v1.4 | 新增 Week 4 进入条件（统一样本包版） |
| 决策记录与待确认事项.md | v1.4 | 新增 OBS-W3-03 待确认事项 |
| 正式MVP试跑版本说明.md | v1.2 | 新增 November 留出验证集说明 |

---

## 六、下阶段工作项

| 序号 | 工作项 | 优先级 | 建议时间 |
|------|-------|--------|---------|
| 1 | W3-P1 适配层修复 | P2 | Week 4 启动前 |
| 2 | W3-P2 适配层修复 | P2 | Week 4 启动前 |
| 3 | footer"Week 1"硬编码修复 | P3 | Week 4 期间 |
| 4 | OBS-W3-03 Q01 延期申请类型确认 | P1 | Week 4 启动前 |
| 5 | November 重跑验证修复效果 | 必须 | Week 4 启动时 |
| 6 | 推进生产数据切换评审准备 | P2 | Week 5+ |
