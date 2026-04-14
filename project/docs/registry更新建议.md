# registry更新建议

**版本：** v1.0
**日期：** 2026-04-07
**用途：** 说明哪些状态字段需要更新、更新顺序、哪些必须等外部确认后执行
**注意：** Agent不直接修改registry，只提供建议，由用户执行

---

## 一、registry当前状态（截至阶段4A.6）

| 字段 | 当前值 | 来源 |
|------|--------|------|
| s1.total | 0 | 阶段4A.6前为0 |
| s1.passed | 0 | 阶段4A.6前为0 |
| s2.total | 0 | 阶段4A.6前为0 |
| s2.passed | 0 | 阶段4A.6前为0 |

---

## 二、阶段4A.6样本验收后的更新建议

### 2.1 立即可执行的更新（不需要外部确认）

以下更新在阶段4A.6完成后即可执行：

```json
{
  "last_updated": "2026-04-07T21:00:00+08:00",
  "s1": {
    "total": 3,
    "passed": 3,
    "pending_confirmation": true,
    "confirmation_gate": "Q01确认后升级为完全通过",
    "samples": [
      {
        "id": "wr_1208_1212",
        "file": "samples/weekly_reports/weekly_report_1208-1212.json",
        "project": "某总行PMO周报",
        "period": "1208-1212",
        "submitted_date": "2026-04-07",
        "sanitized": true,
        "accepted": true,
        "gap_notes": "周报无owner字段（台账有owner_department）",
        "usable_for_s1": true,
        "usable_for_s2": true,
        "validation_5d": {
          "字段完整性": true,
          "时间信息": true,
          "状态可判定": true,
          "责任人": "partial",
          "文字可解析": true
        }
      },
      {
        "id": "wr_1215_1219",
        "file": "samples/weekly_reports/weekly_report_1215-1219.json",
        "project": "某总行PMO周报",
        "period": "1215-1219",
        "submitted_date": "2026-04-07",
        "sanitized": true,
        "accepted": true,
        "gap_notes": "周报无owner字段（台账有owner_department）",
        "usable_for_s1": true,
        "usable_for_s2": true,
        "validation_5d": {
          "字段完整性": true,
          "时间信息": true,
          "状态可判定": true,
          "责任人": "partial",
          "文字可解析": true
        }
      },
      {
        "id": "wr_1222_1226",
        "file": "samples/weekly_reports/weekly_report_1222-1226.json",
        "project": "某总行PMO周报",
        "period": "1222-1226",
        "submitted_date": "2026-04-07",
        "sanitized": true,
        "accepted": true,
        "gap_notes": "周报无owner字段（台账有owner_department）",
        "usable_for_s1": true,
        "usable_for_s2": true,
        "validation_5d": {
          "字段完整性": true,
          "时间信息": true,
          "状态可判定": true,
          "责任人": "partial",
          "文字可解析": true
        }
      }
    ]
  },
  "s2": {
    "total": 3,
    "passed": 3,
    "pending_confirmation": true,
    "confirmation_gate": "Q01确认后升级为完全通过",
    "samples": [
      {
        "id": "ledger_latest3",
        "file": "samples/project_ledger/project_ledger_latest3.json",
        "project": "项目台账",
        "periods": ["1208-1212", "1215-1219", "1222-1226"],
        "submitted_date": "2026-04-07",
        "sanitized": true,
        "accepted": true,
        "gap_notes": "",
        "record_count": 16,
        "usable_for_s1": true,
        "usable_for_s2": true,
        "validation_5d": {
          "字段完整性": true,
          "时间信息": true,
          "状态可判定": true,
          "责任人": true,
          "文字可解析": true
        }
      }
    ]
  }
}
```

### 2.2 需外部确认后才能执行的更新

以下字段需等Q01确认后才能更新为"完全通过"：

| 字段 | 当前值 | 确认后目标值 | 依赖确认项 |
|------|--------|------------|---------|
| s1.passed | 3 | 3（不变，但状态升级为"已确认"） | Q01 |
| s2.passed | 3 | 3（不变，但状态升级为"已确认"） | Q01 |
| s1.pending_confirmation | true | false | Q01 |
| s2.pending_confirmation | true | false | Q01 |

---

## 三、更新执行顺序

```
Step 1（立即执行，阶段4A.6完成后）：
  → 更新 s1.total = 3, s1.passed = 3
  → 更新 s2.total = 3, s2.passed = 3
  → 添加 pending_confirmation = true
  → 添加 validation_5d 字段
  → 添加 gap_notes 字段
  ↓
Step 2（Q01确认完成后）：
  → 更新 pending_confirmation = false
  → 样本状态升级为"已确认可用于4B"
  ↓
Step 3（Q03确认完成后）：
  → 更新输出格式相关字段（展示形态冻结）
  ↓
Step 4（Q04确认完成后）：
  → 更新试点范围字段
  → 如有新样本，添加样本记录
```

---

## 四、registry状态机

```
物理到位 → pending_confirmation=true → Q01确认 → pending_confirmation=false
                                              ↓
                                        样本可用于4B
```

```
pending_confirmation=false + G1=🟢 + G2=🟢 + G3=🟢 → 样本正式进入4B流程
```

---

## 五、谁可以执行registry更新

| 操作 | 执行人 | 理由 |
|------|-------|------|
| Step 1 | 用户或Agent | 样本已验收，无需外部确认 |
| Step 2-4 | 用户 | 涉及外部已确认的事项 |

---

## 六、registry查询路径

后续Agent如需查询样本状态，查询路径为：

```python
# 查询S1样本
registry["s1"]["samples"]

# 查询S2样本
registry["s2"]["samples"]

# 查询样本是否已确认
registry["s1"]["pending_confirmation"]  # true=待确认，false=已确认

# 查询样本是否可用于4B
is_ready_for_4b = (
    registry["s1"]["passed"] >= 1
    and registry["s2"]["passed"] >= 3
    and not registry["s1"]["pending_confirmation"]
)
```
