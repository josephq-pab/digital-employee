"""
适配层 - 将周报/台账数据适配到统一输入格式
处理缺失字段、风险抽取、escalation推断、行业→项目映射
"""

import re
from typing import Optional


def extract_risk_points_from_alert(alert_item: dict) -> str:
    """从key_alert项抽取风险描述"""
    raw = alert_item.get('raw', '')
    level = alert_item.get('alert_level', '')
    name = alert_item.get('project_name', '')
    if level == 'yellow' and raw:
        # W1-P1修复：若raw已以name开头（样本数据特征），不重复拼接project_name
        if raw.startswith(name):
            return f"[黄灯]{raw}"
        return f"[黄灯]{name}：{raw}"
    return ''


def extract_risk_points_from_summary(summary: dict) -> str:
    """从management_summary抽取需关注事项"""
    parts = []
    for item in summary.get('items_requiring_leadership_attention', []):
        if item:
            parts.append(f"[需领导关注]{item}")
    for item in summary.get('delayed_items', []):
        if item:
            parts.append(f"[延期]{item}")
    return '；'.join(parts)


def infer_escalation(summary: dict) -> bool:
    """
    推断escalation_requested
    Q01确认实现（ADPT-ASSUME-03）
    条件：management_summary.items_requiring_leadership_attention非空 → escalation=True
    """
    leadership_items = summary.get('items_requiring_leadership_attention', [])
    return bool(leadership_items and len(leadership_items) > 0)


def extract_closure_requests(key_requests: dict) -> list:
    """提取结项申请事项"""
    closures = key_requests.get('closure_requests', [])
    return [c['project_name'] for c in closures if c.get('project_name')]


def build_normalized_item(
    project_name: str,
    period: str,
    source: str,  # 'weekly_report' / 'ledger'
    alert_item: Optional[dict] = None,
    summary: Optional[dict] = None,
    closure_item: Optional[dict] = None,
    extension_item: Optional[dict] = None,
    ledger_record: Optional[dict] = None,
    is_yellow_alert: bool = False,
) -> dict:
    """
    构建标准化的单条事项输入格式
    适配层统一输出格式，用于规则引擎判断
    """
    # 风险点
    risk_points = ''
    if alert_item:
        risk_points = extract_risk_points_from_alert(alert_item)
    if summary:
        risk_points_summary = extract_risk_points_from_summary(summary)
        if risk_points_summary:
            risk_points = (risk_points + '；' + risk_points_summary).strip('；')

    # 进展描述
    current_progress = ''
    promised_items = ''
    if alert_item:
        current_progress = alert_item.get('raw', '')
        promised_items = alert_item.get('project_name', '')
    if closure_item:
        promised_items = closure_item.get('project_name', '')
        current_progress = closure_item.get('raw', '')
    if extension_item:
        promised_items = extension_item.get('project_name', '')
        current_progress = extension_item.get('raw', '')

    # escalation推断
    escalation_requested = False
    if summary:
        escalation_requested = infer_escalation(summary)

    # 黄灯 → 中风险注入（Q01确认，ADPT-ASSUME-03）
    # 注意：extract_risk_points_from_alert已包含"[黄灯]"前缀，
    # 此处只注入current_progress信号，不重复拼接"[黄灯]"标记
    if is_yellow_alert:
        # QUAL-01核心修复：注入"进度滞后"到current_progress（供LAG_PATTERNS匹配）
        if '进度滞后' not in current_progress and '滞后' not in current_progress:
            current_progress = current_progress + '存在逾期风险，进度滞后。'

    # 责任人（Q01确认：周报无owner时使用台账owner_department，ADPT-ASSUME-02）
    # QUAL-05修复：优先从ledger_record提取owner_department
    owner = '[待关联]'
    if ledger_record:
        owner = ledger_record.get('owner_department', '') or '[待关联]'

    return {
        'project_name': project_name,
        'period': period,
        'source': source,
        'owner': owner,
        'promised_items': promised_items,
        'current_progress': current_progress,
        'risk_points': risk_points,
        'escalation_requested': escalation_requested,
        'is_closure_request': closure_item is not None,
        'is_extension_request': extension_item is not None,
        'is_yellow_alert': is_yellow_alert,
        'ledger_record_id': ledger_record.get('record_id') if ledger_record else None,
    }


def normalize_weekly_report(wr_item: dict, ledger_index: dict, mapping: list) -> list:
    """
    将单期周报归一化为标准事项列表
    返回：该周报中所有可处理的事项
    """
    period = wr_item['report_meta']['report_period']
    normalized_items = []

    # 1. key_alerts（黄灯事项）
    for alert in wr_item.get('key_alerts', []):
        # 尝试在映射中找对应台账
        ledger_rec = None
        for m in mapping:
            if m['period'] == period and m['source_type'] == 'key_alert':
                if alert.get('project_name', '').startswith(m['source_project_name'][:10]):
                    if m['ledger_record_id']:
                        ledger_rec = ledger_index.get(m['ledger_record_id'])
                        break

        item = build_normalized_item(
            project_name=alert.get('project_name', '未知'),
            period=period,
            source='weekly_report',
            alert_item=alert,
            summary=None,
            ledger_record=ledger_rec,
            is_yellow_alert=(alert.get('alert_level') == 'yellow'),
        )
        normalized_items.append(item)

    # 2. closure_requests（结项申请）
    for closure in wr_item.get('key_requests', {}).get('closure_requests', []):
        # QUAL-05修复：为closure项也查找台账以提取owner
        closure_ledger_rec = None
        for m in mapping:
            if m['period'] == period and m['source_type'] == 'closure_requests':
                if closure.get('project_name', '') and closure.get('project_name', '').startswith(m['source_project_name'][:8]):
                    if m['ledger_record_id']:
                        closure_ledger_rec = ledger_index.get(m['ledger_record_id'])
                        break
        item = build_normalized_item(
            project_name=closure.get('project_name', '未知'),
            period=period,
            source='weekly_report',
            alert_item=None,
            summary=None,
            closure_item=closure,
            ledger_record=closure_ledger_rec,
            is_yellow_alert=False,
        )
        normalized_items.append(item)

    # 2b. extension_requests（延期申请）
    for extension in wr_item.get('key_requests', {}).get('extension_requests', []):
        extension_ledger_rec = None
        for m in mapping:
            if m['period'] == period and m['source_type'] == 'extension_requests':
                if extension.get('project_name', '') and extension.get('project_name', '').startswith(m['source_project_name'][:8]):
                    if m['ledger_record_id']:
                        extension_ledger_rec = ledger_index.get(m['ledger_record_id'])
                        break
        item = build_normalized_item(
            project_name=extension.get('project_name', '未知'),
            period=period,
            source='weekly_report',
            alert_item=None,
            summary=None,
            extension_item=extension,
            ledger_record=extension_ledger_rec,
            is_yellow_alert=False,
        )
        normalized_items.append(item)

    # 3. management_summary中的需关注项（未在alerts中出现的）
    summary = wr_item.get('management_summary', {})
    alert_names = {a.get('project_name', '') for a in wr_item.get('key_alerts', [])}
    for leadership_item in summary.get('items_requiring_leadership_attention', []):
        if leadership_item and leadership_item not in alert_names:
            item = build_normalized_item(
                project_name=leadership_item,
                period=period,
                source='weekly_report',
                summary=summary,
                is_yellow_alert=False,
            )
            normalized_items.append(item)

    return normalized_items


def normalize_ledger_record(ledger_rec: dict, period: str) -> list:
    """
    将台账主记录归一化（按周期）
    """
    progress_by_period = ledger_rec.get('progress_by_period', {})
    progress_text = progress_by_period.get(period, '') or ''

    return {
        'project_name': ledger_rec.get('project_name', '未知'),
        'record_id': ledger_rec.get('record_id', ''),
        'period': period,
        'source': 'ledger',
        'owner': ledger_rec.get('owner_department', ''),
        'promised_items': ledger_rec.get('objective_or_requirement', '')[:200],
        'current_progress': progress_text[:500],
        'risk_points': '',  # 台账本身无独立风险字段
        'escalation_requested': False,
        'record_type': ledger_rec.get('record_type', ''),
        'project_type': ledger_rec.get('project_type', ''),
    }
