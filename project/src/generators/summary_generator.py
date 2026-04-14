"""
领导摘要生成器 - 生成面向管理层的标准化摘要
output_format: 模板A（完整版）- 三层结构（事实/判断/建议）
Q01/Q03确认正式版本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine import ProjectTracker


def generate_summary_item(item: dict, engine_result: dict, metrics: list = None) -> dict:
    """
    为单个事项生成领导摘要条目
    输入：归一化事项 + 引擎判断结果 + 指标列表（可选）
    输出：领导摘要条目（优化版：结论更具体、建议更像管理动作）
    """
    risk_level = engine_result.get('risk_assessment', {}).get('level', '未知')
    escalation = engine_result.get('escalation_recommended', False)
    reasoning = engine_result.get('reasoning', {})

    # 整体判断
    overall = engine_result.get('status_summary', {}).get('overall', '未知')

    # 建议动作（优化：从技术语言转为管理动作）
    raw_actions = engine_result.get('suggested_actions', [])
    actions = _format_management_actions(raw_actions, item, risk_level)

    # 判断依据（优化：更短更清楚，用业务语言）
    raw_signal = reasoning.get('raw_signal', '')
    business_signal = _format_business_signal(raw_signal, item, risk_level)

    return {
        '事项名称': item['project_name'],
        '期间': item['period'],
        '状态': overall,
        '风险等级': risk_level,
        '升级建议': '是' if escalation else '否',
        '事实': {
            '承诺': item['promised_items'][:100] if item['promised_items'] else '无明确承诺',
            '进展': item['current_progress'][:200] if item['current_progress'] else '无进展描述',
            '风险自述': item['risk_points'][:200] if item['risk_points'] else '无',
        },
        '判断': {
            '触发规则': reasoning.get('rules_applied', []),
            '原始信号': reasoning.get('raw_signal', ''),
            '业务语言信号': business_signal,  # 新增：业务语言版判断依据
        },
        '建议': actions,  # 优化后：管理动作格式
    }


def _format_management_actions(raw_actions: list, item: dict, risk_level: str) -> list:
    """
    将技术语言建议动作转为管理动作
    原则：带时间节点、带对象、带具体动作
    """
    if not raw_actions:
        # 默认建议：根据风险等级给出管理建议
        if risk_level == '高':
            return ['本周内明确推进责任人与完成时间节点']
        elif risk_level == '中':
            return ['补充储备计划，明确前置条件完成时间']
        else:
            return ['按当前节奏继续跟踪']

    formatted_actions = []
    for action in raw_actions[:3]:
        # 去除技术术语，转为管理动作
        action = action.replace('持续跟踪', '按周跟踪')
        action = action.replace('关注', '跟踪')
        action = action.replace('建议', '')
        action = action.strip()

        # 如果没有时间节点，根据风险等级补充
        if '本周' not in action and '本周内' not in action and '04/' not in action and '05/' not in action:
            if risk_level == '高':
                action = '本周：' + action
            elif risk_level == '中':
                action = '尽快：' + action

        formatted_actions.append(action)

    return formatted_actions


def _format_business_signal(raw_signal: str, item: dict, risk_level: str) -> str:
    """
    将技术判断依据转为业务语言
    原则：先讲事实，再讲判断，少用专业术语
    """
    if not raw_signal:
        return ''

    signal = raw_signal

    # 去除触发规则名称（技术语言）
    signal = signal.replace('触发规则：指标偏离检测', '')
    signal = signal.replace('触发规则：延期检测', '')
    signal = signal.replace('触发规则：黄灯检测', '')
    signal = signal.replace('；原始信号：', '。')

    # 简化数字表达
    if '亿元' in signal:
        # 保留数字，去除百分比（太技术）
        pass

    return signal.strip()


def generate_leadership_summary(normalized_items: list, engine_results: list, metrics: list = None) -> dict:
    """
    生成领导摘要（面向管理层）
    模板A：三层结构（事实→判断→建议）
    优化版：增加verdict（具体整体判断）
    """
    total = len(normalized_items)
    escalated = []
    yellow_alerts = []
    delayed = []
    closed = []
    extended = []
    normal = []

    for i, (item, result) in enumerate(zip(normalized_items, engine_results)):
        overall = result.get('status_summary', {}).get('overall', '未知')
        risk_level = result.get('risk_assessment', {}).get('level', '未知')

        entry = generate_summary_item(item, result, metrics)

        if item.get('is_extension_request'):
            extended.append(entry)
        elif item.get('is_closure_request'):
            closed.append(entry)
        elif result.get('escalation_recommended'):
            escalated.append(entry)
        elif item.get('is_yellow_alert'):
            yellow_alerts.append(entry)
        elif risk_level == '中':
            delayed.append(entry)
        else:
            normal.append(entry)

    # 生成具体整体判断（优化版）
    verdict = _generate_specific_verdict(total, escalated, yellow_alerts, delayed, closed, extended, normal, metrics)

    return {
        '摘要类型': '领导摘要（模板A - 完整版）',
        '性质': '正式MVP试跑版本（Q01/Q03/Q04已确认，6D P1优化版）',
        '期间覆盖': list(set(i['period'] for i in normalized_items)),
        '总事项数': total,
        '统计': {
            '申请结项': len(closed),
            '申请延期': len(extended),
            '需领导介入': len(escalated),
            '黄灯关注': len(yellow_alerts),
            '延期/中风险': len(delayed),
            '正常': len(normal),
        },
        '已完成/已解决': closed,
        '申请延期事项': extended,
        '延期事项': delayed + yellow_alerts,
        '无明确进展': [],  # 样本中暂无
        '需领导介入': escalated,
        '整体判断': verdict,  # 优化新增：具体整体判断
    }


def _generate_specific_verdict(total: int, escalated: list, yellow_alerts: list,
                                delayed: list, closed: list, extended: list,
                                normal: list, metrics: list = None) -> dict:
    """
    生成具体的整体判断
    原则：带数量、带对象、带变化，不说空话
    """
    focus_items = escalated + yellow_alerts + delayed

    # 找出最大风险项
    max_risk_desc = ''
    if metrics:
        for m in metrics:
            if m.get('is_偏离', False) or m.get('偏离目标', False):
                name = m.get('指标名称', '未知指标')
                target = m.get('目标', 0)
                current = m.get('当前值', 0)
                diff = m.get('差额', 0)
                if abs(diff) > 0:
                    max_risk_desc = f'{name}缺口{abs(diff)}亿元（目标{target}亿，当前{current}亿）'
                    break

    # 构建具体判断
    if escalated:
        verdict_text = f'本周{total}项事项中，{len(escalated)}项需领导介入，{len(yellow_alerts)}项黄灯持续。整体承压，需重点跟踪。'
        if max_risk_desc:
            verdict_text += f'最大风险：{max_risk_desc}。'
    elif yellow_alerts or delayed:
        focus_count = len(yellow_alerts) + len(delayed)
        verdict_text = f'本周{total}项事项中，{focus_count}项需重点跟踪（黄灯{len(yellow_alerts)}项+延期{len(delayed)}项）。整体可控，但需关注。'
        if max_risk_desc:
            verdict_text += f'最大风险：{max_risk_desc}。'
    elif closed:
        verdict_text = f'本周{total}项事项中，{len(closed)}项已结项，整体进展正常。'
    else:
        verdict_text = f'本周{total}项事项整体进展正常，无异常信号。'

    return {
        '结论': verdict_text,
        '关注项数量': len(focus_items),
        '最大风险描述': max_risk_desc,
        '建议优先级': '高' if escalated else ('中' if (yellow_alerts or delayed) else '低'),
    }


def format_plain_summary(summary: dict) -> str:
    """将摘要格式化为可读文本（用于演示）- 优化版"""
    lines = []
    lines.append("=" * 60)
    lines.append("【领导摘要】6D P1优化版")
    lines.append("=" * 60)
    lines.append(f"期间：{', '.join(summary['期间覆盖'])}")
    lines.append(f"总事项数：{summary['总事项数']}")
    s = summary['统计']
    lines.append(f"其中：申请结项{s['申请结项']} | 申请延期{s.get('申请延期', 0)} | 需领导介入{s['需领导介入']} | 黄灯{s['黄灯关注']} | 延期/中风险{s['延期/中风险']} | 正常{s['正常']}")
    lines.append("")

    # 优化版整体判断（带数量、带对象）
    if '整体判断' in summary and summary['整体判断']:
        vc = summary['整体判断']
        lines.append("【整体判断】")
        lines.append(f"  {vc.get('结论', '')}")
        if vc.get('最大风险描述'):
            lines.append(f"  最大风险：{vc['最大风险描述']}")
        lines.append(f"  建议优先级：{vc.get('建议优先级', '低')}")
        lines.append("")

    if summary['已完成/已解决']:
        lines.append("【已完成/已解决】")
        for e in summary['已完成/已解决']:
            lines.append(f"  ✓ {e['事项名称']}")
        lines.append("")

    if summary.get('申请延期事项'):
        lines.append("【申请延期事项】")
        for e in summary['申请延期事项']:
            lines.append(f"  ⏳ {e['事项名称']} | 状态:延期 | 风险:中")
            # 优化：使用业务语言信号
            biz_signal = e['判断'].get('业务语言信号', e['判断'].get('原始信号', ''))
            if biz_signal:
                lines.append(f"     判断：{biz_signal[:80]}")
            # 优化：建议动作带时间
            if e['建议']:
                lines.append(f"     动作：{'；'.join(e['建议'][:2])}")
        lines.append("")

    if summary['延期事项']:
        lines.append("【延期/黄灯事项】")
        for e in summary['延期事项']:
            risk_icon = '🔴' if e['风险等级'] == '高' else '🟡'
            lines.append(f"  {risk_icon} {e['事项名称']} | 状态:{e['状态']} | 风险:{e['风险等级']}")
            # 优化：使用业务语言信号
            biz_signal = e['判断'].get('业务语言信号', e['判断'].get('原始信号', ''))
            if biz_signal:
                lines.append(f"     判断：{biz_signal[:80]}")
            # 优化：建议动作带时间
            if e['建议']:
                lines.append(f"     动作：{'；'.join(e['建议'][:2])}")
        lines.append("")

    if summary['需领导介入']:
        lines.append("【需领导介入】")
        for e in summary['需领导介入']:
            lines.append(f"  🚨 {e['事项名称']}")
            # 优化：建议动作为管理动作
            if e['建议']:
                lines.append(f"     动作：{'；'.join(e['建议'][:2])}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("【注意】本摘要为6D P1优化版，判断更具体、建议更像管理动作")
    return '\n'.join(lines)
