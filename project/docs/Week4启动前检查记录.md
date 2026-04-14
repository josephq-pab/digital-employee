# Week4 启动前检查记录

**版本：** v1.0
**日期：** 2026-04-08
**阶段：** 阶段4K《Week 4 运行与四周试跑收口》

---

## 一、代码状态检查

### 1.1 核心文件语法检查

| 文件 | 状态 |
|------|------|
| project/src/loaders/november_adapter.py | ✅ 语法正确 |
| project/src/adapters/normalizer.py | ✅ 语法正确 |
| project/src/generators/summary_generator.py | ✅ 语法正确 |
| project/src/generators/ledger_generator.py | ✅ 语法正确 |
| project/src/generators/risk_list_generator.py | ✅ 语法正确 |

### 1.2 最新运行状态

| 指标 | 值 |
|------|---|
| 最新归一化文件 | normalized_20260408_170558.json |
| 最新领导摘要 | 领导摘要_20260408_170558.txt |
| 样本集 | slices/02_holdout_validation_november.json（November 4期） |
| 归一化事项数 | 17条 |
| 压力回归状态 | ⚠️ 未完整执行（phase 4J 仅检查了格式，未执行完整 pipeline） |

---

## 二、W3-P1/P2 关闭确认

### 2.1 W3-P1（结项申请误合并）✅ 已关闭

- **修复文件：** november_adapter.py
- **修复内容：** adapt_alert_line_to_key_alert() 改返回 (alert_items, closure_raw_parts) 元组
- **验证结果：** 1103-1107黄灯从5降为4；1110-1114搭建战略客户样板正确识别为结项
- **关闭依据：** November 留出验证集回归 7/7 PASS

### 2.2 W3-P2（延期申请未识别）✅ 已关闭

- **修复文件：** november_adapter.py
- **修复内容：** adapt_request_lines_to_closure_requests() 增加 raw_text 配对逻辑
- **验证结果：** 1117-1121数字经营正确识别为延期申请
- **关闭依据：** November 留出验证集回归 7/7 PASS

---

## 三、Week 4 样本策略

### 3.1 样本决策

**结论：Week 4 = 压力回归样本（slices/03_stress_regression_aug_sep.json）**

依据：
1. phase 4J 未完整覆盖 slices/03（仅检查了格式，未执行完整 pipeline）
2. slices/03 是"高黄灯/高逾期/高复杂度"样本，是 MVP 验证的重要缺口
3. December（01）和 November（02）样本已分别覆盖 Week 1-3，Aug/Sep 压力样本是唯一未验证的高复杂度集

### 3.2 压力回归样本概况

| 属性 | 值 |
|------|---|
| 切片文件 | slices/03_stress_regression_aug_sep.json |
| 样本期数 | 9期（0728-0801 到 0922-0926） |
| 用途 | 高黄灯/高逾期/高复杂度压力回归 |
| 复杂度说明 | 映射和数据口径复杂度较高，更适合回归和稳态测试 |

### 3.3 数据格式差异（关键发现）

| 属性 | December (01) | November (02) | Aug/Sep (03) |
|------|--------------|--------------|--------------|
| alert_lines 前缀 | `-`（横杠） | `-`（横杠） | `1.`/`2.`/`3.`（数字编号） |
| request_lines | 有内容 | 有内容 | **空数组** |
| closure/termination requests 位置 | request_lines | request_lines | **raw_text 独立段落** |
| 台账/映射 | 完整 | 完整 | 复杂度较高 |

**关键差异：** Aug/Sep 的 closure/termination requests 不在 request_lines 中，而在 raw_text 的独立段落（如"两个项目申请，请您批示意见"）。

---

## 四、Week 4 执行计划

### 4.1 执行策略

**扩展 november_adapter.py**，增加 Aug/Sep 格式适配：

1. **alert_lines 编号适配：** 识别 `^\d+[..、]` 格式的数字编号行（不依赖 `-` 前缀）
2. **request_lines 空数组处理：** 当 request_lines 为空时，从 raw_text 解析"两个/三个项目申请"段落
3. **raw_text 解析逻辑：** 从 raw_text 提取申请段落中的项目名称和类型（结项/终止/延期）

### 4.2 风险评估

| 风险 | 级别 | 应对 |
|------|------|------|
| alert_lines 格式差异（1. vs -） | 中 | 扩展正则兼容两种格式 |
| request_lines 为空，closure 在 raw_text | 高 | 增加 raw_text 解析逻辑 |
| Aug/Sep 台账映射复杂度高 | 中 | 允许部分 unmatched，先跑通再优化 |
| 时间跨度9周，数据量大 | 低 | 分批处理或扩展超时 |

---

## 五、四周试跑样本总览

| Week | 切片 | 样本 | 用途 | 状态 |
|------|------|------|------|------|
| Week 1 | 01_dev_core_december | 1208-1226（3期） | 开发/演示主样本 | ✅ 已完成 |
| Week 2 | 01_dev_core_december | 同上 | 连续性模拟 | ✅ 已完成 |
| Week 3 | 02_holdout_november | 1103-1128（4期） | 留出验证 | ✅ 已完成 |
| Week 4 | 03_stress_aug_sep | 0728-0926（9期） | 高复杂度压力回归 | 🔄 待执行 |

---

## 六、检查结论

| 检查项 | 结论 |
|--------|------|
| 代码最新状态 | ✅ 阶段4J修复后，所有核心文件语法正确 |
| W3-P1 关闭 | ✅ 已通过 November 回归验证 |
| W3-P2 关闭 | ✅ 已通过 November 回归验证 |
| Week 4 样本策略 | ✅ 确认执行 slices/03（压力回归） |
| 压力回归覆盖 | ⚠️ 未完整执行，本阶段补齐 |
| 适配器扩展需求 | ✅ 需扩展以支持 Aug/Sep 格式差异 |

**Week 4 进入状态：✅ 可以执行（需先扩展适配器）**
