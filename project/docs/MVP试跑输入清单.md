# MVP试跑输入清单

**版本：** v1.0
**日期：** 2026-04-08
**试跑性质：** MVP模拟试跑（dry-run / conditional）

---

## 一、必需输入

### 1.1 周报数据

| 项目 | 内容 |
|------|------|
| 文件名 | weekly_report_series_latest3.json |
| 路径 | samples/samples/weekly_reports/ |
| 格式 | JSON |
| 必需字段 | report_meta.period, report_meta.week, items[].project, items[].owner, items[].progress, items[].risk |
| 样本数量 | ≥3期（本次试跑：3期） |
| 样本期间 | W50/W51/W52（2025-12） |

### 1.2 项目台账

| 项目 | 内容 |
|------|------|
| 文件名 | project_ledger_latest3.json |
| 路径 | samples/samples/project_ledger/ |
| 格式 | JSON |
| 必需字段 | records[].id, records[].project_name, records[].owner, records[].status, records[].due_date |
| 记录数量 | ≥16条（本次试跑：20条） |

### 1.3 映射文件

| 项目 | 内容 |
|------|------|
| 文件名 | weekly_to_ledger_mapping_latest3.json |
| 路径 | samples/samples/linked/ |
| 格式 | JSON |
| 必需字段 | mapping[].weekly_item, mapping[].ledger_id, mapping[].match_type |
| 映射数量 | ≥1条（本次试跑：12条） |

---

## 二、可选输入

| # | 文件 | 路径 | 说明 |
|---|------|------|------|
| 1 | 行业术语映射 | samples/samples/行业映射_*.json | MAP-01~04覆盖率优化用，本次试跑未接入 |

---

## 三、输入命名规范

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 周报 | weekly_report_series_v*_YYYYMMDD.json | weekly_report_series_latest3.json |
| 台账 | project_ledger_v*_YYYYMMDD.json | project_ledger_latest3.json |
| 映射 | weekly_to_ledger_mapping_v*_YYYYMMDD.json | weekly_to_ledger_mapping_latest3.json |

---

## 四、输入验收标准

| # | 检查项 | 通过条件 |
|---|--------|---------|
| IN-1 | 周报JSON语法正确 | Python json.load()不报错 |
| IN-2 | 周报期数≥3 | len(weekly_reports) ≥ 3 |
| IN-3 | 周报每期有items | len(items) > 0 |
| IN-4 | 台账JSON语法正确 | Python json.load()不报错 |
| IN-5 | 台账记录≥16条 | len(records) ≥ 16 |
| IN-6 | 映射文件JSON语法正确 | Python json.load()不报错 |
| IN-7 | 映射数量≥1 | len(mapping) ≥ 1 |

---

## 五、输入版本记录

| 字段 | 内容 |
|------|------|
| 周报版本 | latest3（3期 W50/W51/W52 2025-12） |
| 台账版本 | latest3（20条主记录） |
| 映射版本 | latest3（12条映射） |
| 样本S级判定 | S2可用（详见样本验收报告） |
| 本轮试跑接入时间 | 2026-04-08 |

---

## 六、输入目录结构

```
samples/samples/
├── weekly_reports/
│   └── weekly_report_series_latest3.json   ← 必需
├── project_ledger/
│   └── project_ledger_latest3.json          ← 必需
└── linked/
    └── weekly_to_ledger_mapping_latest3.json ← 必需
```
