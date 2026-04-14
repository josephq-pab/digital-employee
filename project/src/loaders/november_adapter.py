"""
适配层 - November 统一样本包数据格式 → 原型引擎期望格式

November/December 样本包结构（alert_lines/request_lines 字符串格式）
→ 原型 normalizer 期望格式（key_alerts/management_summary 对象格式）

这样可以在不修改 src/ 的情况下，直接用新样本包跑原型。
"""

import re
import os
import json
import datetime

# ============================================================
# 路径配置 - 统一样本包数据根目录
# ============================================================
UNIFIED_ROOT = '/home/admin/.openclaw/workspace-digital-employee/openclaw_unified_sample_pack/openclaw_unified_sample_pack'

NORMALIZED_DIR = os.path.join(UNIFIED_ROOT, 'normalized', 'weekly_reports', 'by_period')
LEDGER_DIR = os.path.join(UNIFIED_ROOT, 'normalized', 'ledgers', 'snapshots')
METRICS_DIR = os.path.join(UNIFIED_ROOT, 'normalized', 'metrics', 'snapshots')
SLICES_DIR = os.path.join(UNIFIED_ROOT, 'slices')


# ============================================================
# 适配转换
# ============================================================


def adapt_alert_line_to_key_alert(line: str):
    """
    将 alert_lines 字符串转为 (key_alert列表, closure_raw_parts列表) 元组

    W3-P1 核心修复：
    含"申请结项"/"申请延期"的行（如"2、搭建战略客户样板和北京分行战客专班建设...申请结项"）
    同时包含两类信息：
      - "搭建战略客户样板" → closure_requests
      - "北京分行战客专班建设"（+黄灯描述）→ key_alerts
    本函数将这类行拆分为 closure 片段（交给 adapt_report 统一处理）和 alert 片段。

    返回：(alert_items: list, closure_raw_parts: list)
    """
    line = line.lstrip('-').strip()
    # Aug/Sep 格式支持：去掉数字编号前缀如 "1、" 、"2、" 、"3、"
    line = re.sub(r'^\d+[.、]\s*', '', line)
    if not line:
        return [], []

    has_and = '和' in line
    has_closure_kw = ('申请结项' in line or '申请延期' in line or
                      '申请终止' in line or '申请推迟' in line)
    closure_raw_parts = []
    alert_results = []

    if has_closure_kw:
        # 含申请关键词的行：可能同时描述 closure + alert
        if has_and:
            parts = re.split(r'\s*和\s*', line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if ('申请结项' in part or '申请终止' in part or
                    '申请延期' in part or '申请推迟' in part):
                    closure_raw_parts.append(part)
                else:
                    m = re.match(r'^([^，,：:]+)', part)
                    pn = m.group(1).strip() if m else part
                    pn = re.sub(r'^\d+[.、、]\s*', '', pn).strip()
                    if not pn:
                        pn = part.split('，')[0]
                    alert_results.append({
                        'project_name': pn,
                        'alert_level': 'red' if '红灯' in part else 'yellow',
                        'raw': part,
                    })
        else:
            closure_raw_parts.append(line)
    else:
        if has_and:
            parts = re.split(r'\s*和\s*', line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                m = re.match(r'^([^，,：:]+)', part)
                pn = m.group(1).strip() if m else part
                pn = re.sub(r'^\d+[.、、]\s*', '', pn).strip()
                if not pn:
                    pn = part.split('，')[0]
                alert_results.append({
                    'project_name': pn,
                    'alert_level': 'red' if '红灯' in part else 'yellow',
                    'raw': part,
                })
        else:
            m = re.match(r'^([^，,：:]+)', line)
            pn = m.group(1).strip() if m else '未知'
            alert_results.append({
                'project_name': pn,
                'alert_level': 'red' if '红灯' in line else 'yellow',
                'raw': line,
            })

    return alert_results, closure_raw_parts

def adapt_request_lines_to_closure_requests(request_lines, raw_text=''):
    import re as _re
    closures = []
    raw_text = raw_text or ''
    i = 0
    while i < len(request_lines):
        line = request_lines[i].strip()
        i += 1
        if not line:
            continue
        # Detect header-only lines like 一、XXX请您审批：
        is_header = bool(_re.match(r"^一.+?(?:请您)?(审批|批示).{0,15}[：:]\s*$", line))
        skip_current = False  # 跳过当前行（内容已被后续行处理）
        if is_header and i < len(request_lines):
            next_line = request_lines[i].strip()
            if next_line and (next_line[0].isdigit() or next_line.startswith(("1、", "2、", "3、"))):
                skip_current = True  # 标题行后有具体内容行，跳过标题行本身
        if is_header and raw_text and not skip_current:
            header_in_text = _re.search(r"审批[：:]\s*\n([^\n]{2,60})", raw_text)
            if header_in_text:
                line = header_in_text.group(1).strip()
        if is_header and not any(kw in line for kw in ["结项", "终止", "延期", "推迟"]):
            continue
        if skip_current:
            continue
        if "延期" in line or "推迟" in line:
            m = _re.search(r'[\u201c\u201d\x22]([^\x22\u201c\u201d]{2,30})', line)
            if m:
                pn = m.group(1)
            else:
                pn = line.split("，")[0].split("：")[0].strip()
            pn = pn.replace('"', '').replace("'", '').strip()
            pn = pn.strip()
            if pn:
                closures.append({"project_name": pn, "raw": line, "type": "extension"})
        elif "申请结项" in line or "申请终止" in line:
            parts = _re.split(r"\s*和\s+", line)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                m = _re.match(r"^\d+[.、]\s*(.+?)[，,：:]", part)
                pn = m.group(1).strip() if m else part.split("，")[0].split("：")[0].strip()
                pn = pn.replace('"', '').replace("'", '').strip()
                pn = pn.strip()
                if not pn:
                    pn = part.split("，")[0]
                closures.append({"project_name": pn, "raw": part, "type": "closure"})
    return closures

def adapt_report_to_engine_format(report: dict) -> dict:
    """
    将统一样本包周报格式 → 原型引擎期望的 report_meta + key_alerts + key_requests 格式
    """
    period = report.get('report_period', '')
    report_date = report.get('report_date', '')

    # 构建 report_meta
    report_meta = {
        'report_period': period,
        'report_date': report_date,
    }

    # 转换 alert_lines → key_alerts（可能返回多条）
    # W3-P1修复：adapt_alert_line_to_key_alert 现返回(alert_items, closure_raw_parts)元组
    key_alerts = []
    all_closure_raw_parts = []  # 从alert_lines混入的closure片段
    for line in report.get('alert_lines', []):
        if line and line.strip():
            alert_items, closure_raw_parts = adapt_alert_line_to_key_alert(line)
            key_alerts.extend(alert_items)
            all_closure_raw_parts.extend(closure_raw_parts)

    # 转换 request_lines → closure_requests / extension_requests
    # W3-P2修复：传入raw_text用于标题-内容配对


    closure_list = adapt_request_lines_to_closure_requests(
        report.get('request_lines', []),
        report.get('raw_text', '')
    )

    # ========== Aug/Sep 格式兼容：request_lines 空时从 raw_text 提取 ==========
    _req_lines = report.get('request_lines', [])
    _raw_text = report.get('raw_text', '')
    if not _req_lines and _raw_text:
        m = re.search(r'([零一二两三四五六七八九十百\d]+)个项目申请[，,]?请您(审批|批示)意见[：:]', _raw_text)
        if m:
            section_start = m.end()
            section_text = _raw_text[section_start:section_start+600]
            for line in section_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # 遇到下一节标题则停止（申请段落结束）
                if any(x in line for x in ('项目亮灯', '请您重点', 'PMO周报', '本期')):
                    break
                if re.match(r'^\d+[.、]', line):
                    if '终止' in line:
                        ctype = 'closure'  # 终止算作closure_requests
                    elif '延期' in line or '推迟' in line:
                        ctype = 'extension'
                    else:
                        ctype = 'closure'
                    pn_match = re.match(r'^\d+[.、]\s*(.+?)[：:]', line)
                    pn = pn_match.group(1).strip() if pn_match else line.split('，')[0].strip()
                    pn = pn.replace('"', '').replace("'", '').strip()
                    if pn and len(pn) >= 2:
                        closure_list.append({'project_name': pn, 'raw': line, 'type': ctype})
    # ========== Aug/Sep 格式兼容结束 ==========

    # W3-P1修复：将alert_lines混入的closure片段也转为closure_requests条目
    for raw_part in all_closure_raw_parts:
        if '申请结项' in raw_part or '申请终止' in raw_part:
            ctype = 'closure'
        elif '申请延期' in raw_part or '申请推迟' in raw_part:
            ctype = 'extension'
        else:
            ctype = 'closure'
        # 提项目名
        import re as _re
        name_match = _re.match(r'^([^，,：:]+)', raw_part)
        project_name = name_match.group(1).strip() if name_match else raw_part.split('，')[0]
        project_name = _re.sub(r'^\d+[.、、]\s*', '', project_name).strip()
        closure_list.append({
            'project_name': project_name,
            'raw': raw_part,
            'type': ctype,
        })
    closure_requests = [c for c in closure_list if c['type'] == 'closure']
    extension_requests = [c for c in closure_list if c['type'] == 'extension']

    key_requests = {
        'closure_requests': [{'project_name': c['project_name'], 'raw': c['raw']} for c in closure_requests],
        'extension_requests': [{'project_name': c['project_name'], 'raw': c['raw']} for c in extension_requests],
    }

    # management_summary - 从 overview 构造
    overview = report.get('overview', {})
    management_summary = {
        'items_requiring_leadership_attention': [],
        'delayed_items': [alert['raw'] for alert in key_alerts],
    }

    # 新增项目（如果有 new_items_count）
    new_items = []
    if report.get('new_items_count', 0) > 0:
        # 从 raw_text 解析新增项目段落
        raw = report.get('raw_text', '')
        new_section = re.findall(r'新增项目[（(](\d+)项[）)][：:]\s*(.+?)(?=\n\n|\n二|\n公司|$)', raw, re.DOTALL)
        for _, content in new_section:
            items = re.findall(r'["""]([^"""]+)["""]', content)
            new_items.extend(items)




    return {
        'report_meta': report_meta,
        'key_alerts': key_alerts,
        'key_requests': key_requests,
        'management_summary': management_summary,
        'new_items': new_items,
    }


# ============================================================
# 加载器 - 适配统一样本包
# ============================================================

def load_slice(slice_name: str = '02_holdout_validation_november') -> dict:
    """
    加载指定切片的完整数据（周报+台账+指标）
    返回：{
        'slice_info': {...},
        'weekly_reports': [...],   # 适配后格式
        'ledger_snapshots': {...}, # period -> ledger
        'metrics_snapshots': {...}, # snapshot_date -> metrics
    }
    """
    slice_path = os.path.join(SLICES_DIR, f'{slice_name}.json')
    with open(slice_path, 'r', encoding='utf-8') as f:
        slice_info = json.load(f)

    weekly_reports = []
    ledger_snapshots = {}
    metrics_snapshots = {}

    for item in slice_info.get('items', []):
        period = item['report_period']
        # 加载并适配周报
        report_path = os.path.join(UNIFIED_ROOT, item['report_file'])
        with open(report_path, 'r', encoding='utf-8') as f:
            raw_report = json.load(f)
        adapted = adapt_report_to_engine_format(raw_report)
        adapted['_raw_report'] = raw_report  # 保留原始引用
        adapted['report_id'] = raw_report.get('report_id', f'PMO-{period}')
        adapted['report_period'] = period
        adapted['start_date'] = raw_report.get('start_date', '')
        adapted['end_date'] = raw_report.get('end_date', '')
        weekly_reports.append(adapted)

        # 加载台账快照
        ledger_path = os.path.join(UNIFIED_ROOT, item['ledger_snapshot_file'])
        if os.path.exists(ledger_path):
            with open(ledger_path, 'r', encoding='utf-8') as f:
                ledger_snapshots[period] = json.load(f)

        # 加载量化指标快照
        metrics_path = os.path.join(UNIFIED_ROOT, item['metrics_snapshot_file'])
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics_snapshots[item['metrics_snapshot_file'].split('/')[-1].replace('.json', '')] = json.load(f)

    return {
        'slice_info': slice_info,
        'weekly_reports': weekly_reports,
        'ledger_snapshots': ledger_snapshots,
        'metrics_snapshots': metrics_snapshots,
    }


def build_ledger_index(ledger_data: dict) -> dict:
    """构建台账索引：record_id → record（兼容原接口）"""
    records = ledger_data.get('projects', [])
    return {rec.get('record_id', rec.get('canonical_key', i)): rec for i, rec in enumerate(records)}


def load_november_for_prototype():
    """
    专门为 run_prototype.py 兼容接口加载 November 留出样本
    返回：(weekly_reports, ledger_data, mapping, ledger_index)
    """
    data = load_slice('02_holdout_validation_november')

    # 构建 ledger_data（兼容原 load_ledger 返回格式）
    all_projects = []
    for period, ledger in data['ledger_snapshots'].items():
        for proj in ledger.get('projects', []):
            proj['record_id'] = f"{period}_{proj.get('canonical_key', proj.get('project_name', ''))}"
            proj['_ledger_period'] = period
            all_projects.append(proj)

    ledger_data = {'records': all_projects}

    # 简单映射：按 canonical_key 匹配
    mapping = []
    for wr in data['weekly_reports']:
        period = wr['report_period']
        for alert in wr.get('key_alerts', []):
            project_name = alert.get('project_name', '')
            # 模糊匹配台账
            matched_rec_id = None
            for rec in ledger_data['records']:
                if project_name in rec.get('project_name', '') or rec.get('project_name', '') in project_name:
                    matched_rec_id = rec.get('record_id')
                    break
            mapping.append({
                'period': period,
                'source_type': 'key_alert',
                'source_project_name': project_name,
                'ledger_record_id': matched_rec_id,
                'match_type': 'ledger_matched' if matched_rec_id else 'unmatched',
            })
        for closure in wr.get('key_requests', {}).get('closure_requests', []):
            mapping.append({
                'period': period,
                'source_type': 'closure_requests',
                'source_project_name': closure.get('project_name', ''),
                'ledger_record_id': None,
                'match_type': 'unmatched',
            })

    ledger_index = build_ledger_index(ledger_data)

    return data['weekly_reports'], ledger_data, mapping, ledger_index


# ============================================================
# 输出生成器
# ============================================================

def run_week3_with_november():
    """
    执行 Week 3 原型运行（使用 November 留出样本）
    完整流程：加载 → 归一化 → 规则判断 → 生成输出
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    from src.adapters.normalizer import normalize_weekly_report
    from src.generators.summary_generator import generate_leadership_summary, format_plain_summary
    from src.generators.ledger_generator import generate_ledger_output, format_ledger_plain
    from src.generators.risk_list_generator import generate_risk_list, format_risk_list_plain
    from app.engine import ProjectTracker

    print("=" * 60)
    print("阶段4I-R - November 留出验证 Week 3 执行")
    print("=" * 60)
    print()

    # 加载数据
    print("[1/6] 加载 November 留出样本...")
    weekly_reports, ledger_data, mapping, ledger_index = load_november_for_prototype()
    print(f"  周报：{len(weekly_reports)}期")
    print(f"  台账：{len(ledger_data['records'])}条主记录")
    print(f"  映射：{len(mapping)}条")
    periods = [wr['report_period'] for wr in weekly_reports]
    print(f"  Periods：{', '.join(periods)}")
    print()

    # 归一化
    print("[2/6] 归一化处理...")
    all_normalized = []
    for wr in weekly_reports:
        period = wr['report_period']
        items = normalize_weekly_report(wr, ledger_index, mapping)
        all_normalized.extend(items)
        print(f"  {period}：{len(items)}事项")
    print(f"  归一化事项总数：{len(all_normalized)}")
    print()

    # 规则判断
    print("[3/6] 规则判断...")
    engine = ProjectTracker()
    engine_results = []
    for item in all_normalized:
        result = engine.evaluate(item)
        engine_results.append(result)
    print(f"  判断完成：{len(engine_results)}事项")
    print()

    # 生成输出
    print("[4/6] 生成输出...")

    summary = generate_leadership_summary(all_normalized, engine_results)
    summary_text = format_plain_summary(summary)
    print(f"  领导摘要：{summary.get('总事项数', 0)}事项")

    ledger_out = generate_ledger_output(all_normalized, engine_results, mapping)
    ledger_text = format_ledger_plain(ledger_out)
    print(f"  事项台账：{ledger_out.get('总事项数', 0)}事项")

    risk_out = generate_risk_list(all_normalized, engine_results)
    risk_text = format_risk_list_plain(risk_out)
    print(f"  风险清单：{risk_out.get('总风险数', 0)}风险项")
    print()

    # 保存输出
    print("[5/6] 保存输出...")
    OUTPUT_DIR = '/home/admin/.openclaw/workspace-digital-employee/project/data/output'
    TMP_DIR = '/home/admin/.openclaw/workspace-digital-employee/project/data/tmp'
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    summary_path = os.path.join(OUTPUT_DIR, f'领导摘要_{ts}.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"  领导摘要 → {summary_path}")

    ledger_path = os.path.join(OUTPUT_DIR, f'事项总台账_{ts}.txt')
    with open(ledger_path, 'w', encoding='utf-8') as f:
        f.write(ledger_text)
    print(f"  事项台账 → {ledger_path}")

    risk_path = os.path.join(OUTPUT_DIR, f'风险清单_{ts}.txt')
    with open(risk_path, 'w', encoding='utf-8') as f:
        f.write(risk_text)
    print(f"  风险清单 → {risk_path}")

    normalized_path = os.path.join(TMP_DIR, f'normalized_{ts}.json')
    with open(normalized_path, 'w', encoding='utf-8') as f:
        json.dump({
            'normalized_items': all_normalized,
            'engine_results': engine_results,
            'slice': '02_holdout_validation_november',
            'periods': periods,
        }, f, ensure_ascii=False, indent=2)
    print(f"  归一化中间结果 → {normalized_path}")
    print()

    # 冒烟测试
    print("[6/6] A1-A7 冒烟测试...")
    smoke_results = []

    try:
        assert len(weekly_reports) == 4
        smoke_results.append(('A1 样本可读', 'PASS', f'周报{len(weekly_reports)}期'))
    except Exception as e:
        smoke_results.append(('A1 样本可读', 'FAIL', str(e)))

    try:
        assert len(all_normalized) >= 10
        assert all('project_name' in n for n in all_normalized)
        smoke_results.append(('A2 输入可解析', 'PASS', f'归一化{len(all_normalized)}条'))
    except Exception as e:
        smoke_results.append(('A2 输入可解析', 'FAIL', str(e)))

    try:
        has_alerts = any(n.get('is_yellow_alert') for n in all_normalized)
        has_closures = any(n.get('is_closure_request') for n in all_normalized)
        has_ext = any('延期' in n.get('current_progress', '') for n in all_normalized)
        assert has_alerts or has_closures or has_ext
        smoke_results.append(('A3 事项可抽取', 'PASS', f'黄灯:{has_alerts},结项:{has_closures},延期:{has_ext}'))
    except Exception as e:
        smoke_results.append(('A3 事项可抽取', 'FAIL', str(e)))

    try:
        assert len(engine_results) == len(all_normalized)
        assert all('risk_assessment' in r for r in engine_results)
        smoke_results.append(('A4 规则可判断', 'PASS', f'{len(engine_results)}事项'))
    except Exception as e:
        smoke_results.append(('A4 规则可判断', 'FAIL', str(e)))

    try:
        assert summary.get('总事项数', 0) > 0
        smoke_results.append(('A5 领导摘要可生成', 'PASS', f'{summary["总事项数"]}事项'))
    except Exception as e:
        smoke_results.append(('A5 领导摘要可生成', 'FAIL', str(e)))

    try:
        assert ledger_out.get('总事项数', 0) > 0
        assert len(ledger_out.get('事项列表', [])) > 0
        smoke_results.append(('A6 事项总台账可生成', 'PASS', f'{ledger_out["总事项数"]}事项'))
    except Exception as e:
        smoke_results.append(('A6 事项总台账可生成', 'FAIL', str(e)))

    try:
        assert '风险列表' in risk_out
        smoke_results.append(('A7 风险清单可生成', 'PASS', f'{risk_out["总风险数"]}风险项'))
    except Exception as e:
        smoke_results.append(('A7 风险清单可生成', 'FAIL', str(e)))

    print()
    print("=" * 60)
    print("A1-A7 冒烟测试结果")
    print("=" * 60)
    passed = sum(1 for _, s, _ in smoke_results if s == 'PASS')
    for name, status, detail in smoke_results:
        icon = '✅' if status == 'PASS' else '❌'
        print(f"  {icon} {name}: {status} ({detail})")
    print()
    print(f"通过：{passed}/7")
    print("=" * 60)

    # 领导摘要预览
    print()
    print("【领导摘要预览（前2000字）】")
    print(summary_text[:2000])
    print()

    return {
        'smoke_results': smoke_results,
        'passed': passed,
        'summary': summary,
        'summary_text': summary_text,
        'ledger_out': ledger_out,
        'ledger_text': ledger_text,
        'risk_out': risk_out,
        'risk_text': risk_text,
        'all_normalized': all_normalized,
        'engine_results': engine_results,
        'weekly_reports': weekly_reports,
        'ledger_data': ledger_data,
        'mapping': mapping,
        'output_files': {
            '领导摘要': summary_path,
            '事项总台账': ledger_path,
            '风险清单': risk_path,
            '归一化中间结果': normalized_path,
        },
        'periods': periods,
        'ts': ts,
    }


if __name__ == '__main__':
    result = run_week3_with_november()
