"""
风险清单生成器 - 聚焦延期/无明确进展/需领导介入事项
面向内部校验用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_risk_list(normalized_items: list, engine_results: list) -> dict:
    """
    生成风险清单（内部校验用）
    仅包含：延期 / 无明确进展 / 需领导介入 / 黄灯 事项
    """
    risk_items = []

    for item, result in zip(normalized_items, engine_results):
        # QUAL-02修复：结项申请 = 风险已释放，不进入风险清单
        if item.get('is_closure_request'):
            continue

        risk_level = result.get('risk_assessment', {}).get('level', '未知')
        escalation = result.get('escalation_recommended', False)
        reasoning = result.get('reasoning', {})
        overall = result.get('status_summary', {}).get('overall', '未知')

        # 判断是否属于风险事项
        is_risk = (
            item.get('is_yellow_alert')
            or risk_level in ('中', '高')
            or escalation
            or '延期' in item['project_name']
        )

        if not is_risk:
            continue

        # 分类
        if escalation or risk_level == '高':
            category = '需领导介入'
        elif item.get('is_yellow_alert'):
            category = '黄灯关注'
        elif risk_level == '中':
            category = '延期/中风险'
        else:
            category = '其他风险'

        risk_items.append({
            '事项名称': item['project_name'][:80],  # P3 fix: 60→80，减少截断
            '期间': item['period'],
            '来源': item['source'],
            '分类': category,
            '整体状态': overall,
            '风险等级': risk_level,
            '升级建议': '是' if escalation else '否',
            '规则依据': ', '.join(sorted(set(reasoning.get('rules_applied', [])))),  # P4 fix: 去重+排序
            '原始信号': reasoning.get('raw_signal', ''),
            '承诺事项': item['promised_items'][:100] if item['promised_items'] else '无',
            '风险描述': item['risk_points'][:200] if item['risk_points'] else '无',
        })

    # 按风险等级排序：高 > 黄灯 > 中 > 低
    order = {'需领导介入': 0, '延期/中风险': 1, '黄灯关注': 2}
    risk_items.sort(key=lambda x: order.get(x['分类'], 9))

    return {
        '清单类型': '风险清单',
        '用途': '内部校验',
        '性质': '正式MVP试跑版本（Q01/Q03/Q04已确认）',
        '期间覆盖': list(set(i['period'] for i in normalized_items)),
        '总风险数': len(risk_items),
        '统计': {
            '需领导介入': sum(1 for r in risk_items if r['分类'] == '需领导介入'),
            '延期/中风险': sum(1 for r in risk_items if r['分类'] == '延期/中风险'),
            '黄灯关注': sum(1 for r in risk_items if r['分类'] == '黄灯关注'),
        },
        '风险列表': risk_items,
    }


def format_risk_list_plain(risk_out: dict) -> str:
    """格式化为可读文本"""
    lines = []
    lines.append("=" * 80)
    lines.append("【风险清单】")
    lines.append("=" * 80)
    lines.append(f"期间：{', '.join(risk_out['期间覆盖'])}")
    lines.append(f"风险总数：{risk_out['总风险数']}")
    s = risk_out['统计']
    lines.append(f"其中：需领导介入{s['需领导介入']} | 延期/中风险{s['延期/中风险']} | 黄灯{s['黄灯关注']}")
    lines.append("")

    for item in risk_out['风险列表']:
        icon = '🚨' if item['分类'] == '需领导介入' else ('🟡' if item['分类'] == '黄灯关注' else '⚠️')
        lines.append(f"{icon} [{item['分类']}] {item['事项名称']}")
        lines.append(f"   来源：{item['来源']} | 期间：{item['期间']} | 风险等级：{item['风险等级']}")
        lines.append(f"   规则：{item['规则依据']}")
        lines.append(f"   信号：{item['原始信号']}")
        if item['风险描述']:
            lines.append(f"   风险：{item['风险描述']}")
        lines.append("")

    return '\n'.join(lines)
