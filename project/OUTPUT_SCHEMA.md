# OUTPUT_SCHEMA.md

> 本文件已与《输入输出数据契约.md》对齐。数据契约为权威版本，如有冲突以数据契约为准。

## 输出格式（领导摘要，必须实现）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `report_id` | string | UUID v4，唯一标识 |
| `generated_at` | string | ISO8601时间戳 |
| `project_name` | string | 项目名称（透传） |
| `owner` | string | 责任人（透传） |
| `status_summary` | object | 结构化状态摘要 |
| `risk_assessment` | object | 风险判断 |
| `suggested_actions` | string[] | 建议动作列表 |
| `escalation_recommended` | boolean | 是否建议升级 |
| `escalation_indicator` | string | system_suggested或user_requested |
| `reasoning` | object | 判断依据（供人工复核） |

### status_summary 结构

| 子字段 | 类型 | 说明 |
|--------|------|------|
| `overall` | string | 总体状态：正常/关注/危险 |
| `risk_level` | string | 风险等级：低/中/高 |
| `progress_text` | string | 进展摘要（≤200字） |
| `completion_estimate` | string | 完成度估算（≤100字） |
| `no_clear_progress` | boolean | 是否存在无明确进展 |

### risk_assessment 结构

| 子字段 | 类型 | 说明 |
|--------|------|------|
| `level` | string | 风险等级：低/中/高 |
| `triggered_by` | string[] | 触发的风险条件列表 |
| `summary` | string | 风险摘要描述 |
| `risk_points_present` | boolean | 是否存在风险自述 |

### reasoning 结构

| 子字段 | 类型 | 说明 |
|--------|------|------|
| `facts_extracted` | string[] | 从输入提取的事实清单 |
| `rules_applied` | string[] | 本次判断应用的规则名称 |
| `raw_signal` | string | 触发判断的原始关键词 |

## 示例输出

```json
{
  "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "generated_at": "2026-04-07T14:00:00+08:00",
  "project_name": "智慧园区一期",
  "owner": "张明",
  "status_summary": {
    "overall": "关注",
    "risk_level": "中",
    "progress_text": "基础平台部署80%，权限模块完成，数据看板滞后2周",
    "completion_estimate": "承诺事项存在无法按时完成的风险",
    "no_clear_progress": false
  },
  "risk_assessment": {
    "level": "中",
    "triggered_by": ["进度滞后", "责任人自述风险"],
    "summary": "数据看板开发滞后是主要风险",
    "risk_points_present": true
  },
  "suggested_actions": [
    "分析滞后根因，制定缓释措施",
    "对风险自述进行深入分析，制定缓释措施"
  ],
  "escalation_recommended": false,
  "escalation_indicator": "system_suggested",
  "reasoning": {
    "facts_extracted": [
      "承诺事项：6月30日前完成基础平台部署，交付物包括用户权限模块和数据看板",
      "当前进展：基础平台部署完成80%，用户权限模块开发完成，数据看板开发滞后约2周",
      "风险自述：数据源接口对接进度不及预期，可能影响看板按时上线"
    ],
    "rules_applied": ["rule_滞后", "rule_risk_self_reported"],
    "raw_signal": "进度描述包含'滞后'关键词，risk_points非空含风险词"
  }
}
```
