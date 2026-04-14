# INPUT_SCHEMA.md

> 本文件已与《输入输出数据契约.md》对齐。数据契约为权威版本，如有冲突以数据契约为准。

## 格式A：周报/月报格式（标准JSON）

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `project_name` | string | 是 | 项目名称 |
| `owner` | string | 是 | 责任人姓名 |
| `report_type` | string | 否 | weekly/monthly，默认weekly |
| `report_date` | string | 否 | ISO日期，YYYY-MM-DD |
| `promised_items` | string | 是 | 本周期承诺完成的工作 |
| `current_progress` | string | 是 | 本周期实际进展 |
| `risk_points` | string | 否 | 风险自述，默认空字符串 |
| `escalation_requested` | boolean | 否 | 是否主动请求领导介入，默认false |

## 格式B：项目台账格式

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `project_name` | string | 是 | 项目名称 |
| `owner` | string | 是 | 责任人姓名 |
| `last_updated` | string | 否 | ISO日期 |
| `items` | array | 是 | 事项列表（结构见下方） |
| `overall_risk_points` | string | 否 | 总体风险自述 |
| `escalation_requested` | boolean | 否 | 默认false |

**items数组中每个事项的结构：**

| 子字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `item_id` | string | 是 | 事项唯一标识符 |
| `promised` | string | 是 | 承诺的里程碑 |
| `current_progress` | string | 是 | 当前进展 |
| `status` | string | 否 | in_progress/completed/blocked |

## 容错规则

| 场景 | 处理规则 |
|------|---------|
| risk_points为空 | 视为无风险自述 |
| escalation_requested缺失 | 默认为false |
| items数组缺失 | 降级为格式A处理 |
| 字段过长（>5000字） | 截断至5000字，标记truncated=true |

## 示例（格式A）

```json
{
  "project_name": "智慧园区一期",
  "owner": "张明",
  "report_type": "weekly",
  "report_date": "2026-04-07",
  "promised_items": "6月30日前完成基础平台部署，交付物包括用户权限模块和数据看板",
  "current_progress": "基础平台部署完成80%，用户权限模块开发完成，数据看板开发滞后约2周",
  "risk_points": "数据源接口对接进度不及预期，可能影响看板按时上线",
  "escalation_requested": false
}
```
