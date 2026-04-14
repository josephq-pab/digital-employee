"""
数据加载器 - 从样本文件加载周报、台账、映射数据
"""

import json
import os

SAMPLES_DIR = '/home/admin/.openclaw/workspace-digital-employee/samples/samples'


def load_weekly_reports():
    """加载3期周报"""
    path = os.path.join(SAMPLES_DIR, 'weekly_reports', 'weekly_report_series_latest3.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ledger():
    """加载项目台账"""
    path = os.path.join(SAMPLES_DIR, 'project_ledger', 'project_ledger_latest3.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_mapping():
    """加载周报台账映射"""
    path = os.path.join(SAMPLES_DIR, 'linked', 'weekly_to_ledger_mapping_latest3.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_ledger_index(ledger_data):
    """构建台账索引：record_id → record"""
    return {rec['record_id']: rec for rec in ledger_data['records']}


def find_ledger_record(ledger_index, project_name):
    """fuzzy匹配：在台账中查找对应项目"""
    if not project_name:
        return None
    name_lower = project_name.lower()
    for rid, rec in ledger_index.items():
        if name_lower in rec['project_name'].lower() or rec['project_name'].lower() in name_lower:
            return rec
    return None


if __name__ == '__main__':
    wr = load_weekly_reports()
    ld = load_ledger()
    mp = load_mapping()
    print(f"周报：{len(wr)}期")
    print(f"台账：{len(ld['records'])}条主记录")
    print(f"映射：{len(mp)}条")
    for period in ['1222-1226', '1215-1219', '1208-1212']:
        period_reports = [r for r in wr if r['report_meta']['report_period'] == period]
        if period_reports:
            r = period_reports[0]
            print(f"\n{period}：{r['project_overview']['total_items']}事项，状态灯：{r['project_overview']['status_light']}")
