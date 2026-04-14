"""
事项总台账生成器 - 汇总所有识别事项的完整台账
面向内部校验用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_ledger_output(normalized_items: list, engine_results: list, mapping: list) -> dict:
    """
    生成事项总台账（内部校验用）
    包含：事项名称、来源、状态、映射情况、判断依据
    """
    items = []

    for item, result in zip(normalized_items, engine_results):
        risk_level = result.get('risk_assessment', {}).get('level', '未知')
        reasoning = result.get('reasoning', {})
        overall = result.get('status_summary', {}).get('overall', '未知')

        # 查找映射情况
        period = item['period']
        map_status = ''
        ledger_id = item.get('ledger_record_id')
        if ledger_id:
            map_status = f'已映射→{ledger_id}'
        elif item['source'] == 'weekly_report':
            # 在映射文件中查找
            for m in mapping:
                if m['period'] == period and m['source_project_name'].startswith(item['project_name'][:8]):
                    if m['match_type'] == 'unmatched':
                        map_status = f'未映射({m.get("match_type","unknown")})'
                    else:
                        map_status = f'已映射({m.get("match_type","")})→{m.get("ledger_record_id","")}'
                    break
        else:
            map_status = '台账原生态'

        items.append({
            '序号': len(items) + 1,
            '事项名称': item['project_name'][:80],  # P3 fix: 50→80，减少截断
            '来源': item['source'],
            '期间': item['period'],
            '责任人': item['owner'],
            '整体状态': overall,
            '风险等级': risk_level,
            '升级建议': '是' if result.get('escalation_recommended') else '否',
            '映射状态': map_status,
            '判断规则': ', '.join(reasoning.get('rules_applied', [])),
            '原始信号': reasoning.get('raw_signal', ''),
            '进展描述': item['current_progress'][:100] if item['current_progress'] else '无',
        })

    return {
        '台账类型': '事项总台账',
        '用途': '内部校验',
        '性质': '正式MVP试跑版本（Q01/Q03/Q04已确认）',
        '总事项数': len(items),
        '事项列表': items,
    }


def format_ledger_plain(ledger_out: dict) -> str:
    """格式化为可读文本"""
    lines = []
    lines.append("=" * 80)
    lines.append("【事项总台账】")
    lines.append("=" * 80)
    lines.append(f"总事项数：{ledger_out['总事项数']}")
    lines.append("")

    for item in ledger_out['事项列表']:
        lines.append(f"--- [{item['序号']}] {item['事项名称']} ---")
        lines.append(f"  来源：{item['来源']} | 期间：{item['期间']} | 责任人：{item['责任人']}")
        lines.append(f"  状态：{item['整体状态']} | 风险：{item['风险等级']} | 升级：{item['升级建议']}")
        lines.append(f"  映射：{item['映射状态']}")
        lines.append(f"  规则：{item['判断规则']}")
        if item['进展描述']:
            lines.append(f"  进展：{item['进展描述']}")
        lines.append("")

    return '\n'.join(lines)
