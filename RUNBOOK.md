# RUNBOOK - 数字员工原型 · 冻结建设版

> 本版本：2026-04-16 冻结建设版起点（统一版本 c1e85bc）
> 版本定位：冻结建设版起点（不是"最终版"）
> 当前主线：冻结建设版主线 → 准投产冻结版 → 最终移交
> 冒烟测试：7/7 PASS
> 压力测试：✅ 通过（38条/9期）
> 阶段6K状态：执行落地完成（2026-04-16）

---

**阶段6K落地状态：**
- ✅ 5个P1主流程缺口关闭（G1/G4/G5/G10/G12）
- ✅ 4个P1体验问题关闭（E-P1-1~E-P1-4）
- ✅ 数据口径C-1/C-2/C-3明文化完成
- ✅ S1连续运行：8期全部无P0，P1清零
- ⏳ **仅剩B1~B4业务确认（全需外部业务方输入）**
✅ **内部冻结：已达成（内部无可推进项）**
✅ **当前状态：纯外部确认等待态**

---

## 1. 这个原型能做什么

**一句话说明：**
输入项目周报和台账数据，自动生成领导摘要、事项总台账和风险清单。

**详细能力：**
- 读取 3 期周报 + 台账数据（JSON 格式）
- 将周报中的事项和台账对齐，生成统一的事项视图
- 基于预定义规则，判断每项事项的状态（正常/黄灯/延期/结项）
- 生成三种输出文件：领导摘要、事项总台账、风险清单

---

## 2. 输入文件在哪里

```
/home/admin/.openclaw/workspace-digital-employee/samples/samples/
├── weekly_reports/
│   └── weekly_report_series_latest3.json    ← 3期周报
├── project_ledger/
│   └── project_ledger_latest3.json           ← 项目台账
└── mapping/
    └── mapping_latest3.json                  ← 周报-台账映射关系
```

**注意：这三份文件是样本数据，不是用户真实数据。**

---

## 3. 如何运行主流程

### 方式一：一键运行（推荐）

```bash
cd /home/admin/.openclaw/workspace-digital-employee/project
python3 scripts/run_prototype.py
```

### 方式二：独立运行各模块

```bash
cd /home/admin/.openclaw/workspace-digital-employee/project

# Step 1：加载数据
python3 -c "
import sys, os
sys.path.insert(0, '.')
from src.loaders.sample_loader import load_weekly_reports, load_ledger, load_mapping
wr = load_weekly_reports()
ld = load_ledger()
mp = load_mapping()
print(f'周报:{len(wr)}期 台账:{len(ld[\"records\"])}条 映射:{len(mp)}条')
"

# Step 2：归一化 + 规则判断
python3 scripts/run_prototype.py  # 包含完整链路
```

---

## 4. 运行后会生成哪些文件

运行后，文件保存在以下目录：

```
/home/admin/.openclaw/workspace-digital-employee/project/data/output/
├── 领导摘要_YYYYMMDD_HHMMSS.txt      ← 领导摘要（纯文本）
├── 事项总台账_YYYYMMDD_HHMMSS.txt    ← 事项总台账（纯文本）
├── 风险清单_YYYYMMDD_HHMMSS.txt      ← 风险清单（纯文本）

/home/admin/.openclaw/workspace-digital-employee/project/data/tmp/
└── normalized_YYYYMMDD_HHMMSS.json   ← 归一化中间结果（JSON，可选查看）
```

每次运行会生成带时间戳的新文件，不会覆盖历史文件。

---

## 5. 如何执行 7/7 冒烟测试

冒烟测试已内置在 `run_prototype.py` 中，运行主流程即自动执行。

### 手动查看结果

运行主流程后，输出中包含：

```
============================================================
A1-A7 冒烟测试结果
============================================================
  ✅ A1 样本可读: PASS (周报3期+台账20条)
  ✅ A2 输入可解析: PASS (归一化11条)
  ✅ A3 事项可抽取: PASS (黄灯:True,结项:True)
  ✅ A4 规则可判断: PASS (11事项)
  ✅ A5 领导摘要可生成: PASS (11事项)
  ✅ A6 事项总台账可生成: PASS (11事项)
  ✅ A7 风险清单可生成: PASS (4风险项)

通过：7/7
```

### 各测试项含义

| 测试项 | 检查内容 |
|--------|---------|
| A1 样本可读 | 周报3期 + 台账≥16条记录能正常读取 |
| A2 输入可解析 | 归一化后≥10条事项，每条含 project_name |
| A3 事项可抽取 | 至少存在1条黄灯或结项申请 |
| A4 规则可判断 | 每条事项都有 risk_assessment 输出 |
| A5 领导摘要可生成 | 摘要含总事项数、已完成/延期等结构 |
| A6 事项总台账可生成 | 台账含事项列表和总事项数字段 |
| A7 风险清单可生成 | 风险清单含风险列表和总数 |

---

## 6. 如何执行压力测试

### 运行压力测试脚本

```bash
cd /home/admin/.openclaw/workspace-digital-employee/project
python3 scripts/run_week4_stress.py
```

### 压力测试验证什么

压力测试使用 3 期周报 + 台账数据，执行完整链路并检查：
- 所有模块正常加载，无 import 错误
- 数据规模较大时仍能完整输出
- 领导摘要、事项台账、风险清单三项均完整生成

### 压力测试预期结果（基线版本）

```
成功：领导摘要 + 事项总台账 + 风险清单三项输出均完整
通过门槛：7/7 冒烟全部 PASS
```

---

## 7. 失败时优先看哪些文件

### 步骤一：看报错位置

- 如果是 `ImportError`：检查 `src/` 下各模块是否完整
- 如果是 `FileNotFoundError`：检查样本文件路径是否正确
- 如果是 `JSONDecodeError`：检查 JSON 文件是否损坏

### 步骤二：看输入文件

```bash
# 确认样本文件存在
ls -la /home/admin/.openclaw/workspace-digital-employee/samples/samples/weekly_reports/
ls -la /home/admin/.openclaw/workspace-digital-employee/samples/samples/project_ledger/
ls -la /home/admin/.openclaw/workspace-digital-employee/samples/samples/mapping/
```

### 步骤三：看归一化中间结果

```bash
# 最近一次归一化中间结果
ls -t /home/admin/.openclaw/workspace-digital-employee/project/data/tmp/normalized_*.json | head -1
```

### 步骤四：看输出文件

```bash
# 最近一次输出
ls -t /home/admin/.openclaw/workspace-digital-employee/project/data/output/*.txt | head -3
```

---

## 8. 当前已知限制

| 限制项 | 说明 |
|--------|------|
| 数据为样本，非真实业务数据 | 当前使用固定样本文件，不接真实输入 |
| 无前端界面 | 纯命令行运行，无 Web 或 API |
| 无持久化 | 不保存历史运行结果（输出文件需手动保存） |
| 无通知推送 | 风险清单生成后不自动发消息 |
| GitHub 远程未同步 | 代码在本地，网络恢复后需手动 push |
| 压力测试结果 | ✅ 已验证通过 | run_week4_stress.py，38条/9期无报错 |

---

## 9. 快速参考命令汇总

```bash
# 1. 运行主流程（含7/7冒烟测试）
cd /home/admin/.openclaw/workspace-digital-employee/project
python3 scripts/run_prototype.py

# 2. 运行压力测试
python3 scripts/run_week4_stress.py

# 3. 查看最新输出
ls -t /home/admin/.openclaw/workspace-digital-employee/project/data/output/*.txt | head -3

# 4. 查看冒烟测试结果（从运行输出）
# 直接看 run_prototype.py 的输出末尾

# 5. 查看归一化中间结果
ls -t /home/admin/.openclaw/workspace-digital-employee/project/data/tmp/normalized_*.json | head -1
```

---

## 10. 紧急联系说明

本原型目前无 on-call 机制。发现异常时：
1. 先看本 RUNBOOK 第 7 节「失败时优先看哪些文件」
2. 检查样本文件是否被意外修改
3. 确认 Python 环境正常（Python 3.6+）

---

*本 RUNBOOK 为 2026-04-16 固化基线版本，每次代码变更后请更新「本版本」日期。*
