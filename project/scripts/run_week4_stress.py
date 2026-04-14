"""
阶段4K - Week 4 压力回归运行脚本
执行 slices/03_stress_regression_aug_sep.json (9期 Aug/Sep 周报)
"""
import sys
import os
import json
import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)            # for 'app' module
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))  # for 'src' modules

SLICES_DIR = '/home/admin/.openclaw/workspace-digital-employee/openclaw_unified_sample_pack/openclaw_unified_sample_pack/slices'
DATA_ROOT = '/home/admin/.openclaw/workspace-digital-employee/openclaw_unified_sample_pack/openclaw_unified_sample_pack'
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output')
TMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'tmp')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

def run_week4_stress():
    """执行 Week 4 压力回归"""
    print("=" * 60)
    print("阶段4K - Week 4 压力回归")
    print("=" * 60)
    print()

    # 加载切片
    with open(os.path.join(SLICES_DIR, '03_stress_regression_aug_sep.json'), 'r', encoding='utf-8') as f:
        slice_info = json.load(f)

    reports_raw = []
    for item in slice_info['items']:
        path = os.path.join(DATA_ROOT, item['report_file'])
        with open(path, 'r', encoding='utf-8') as f:
            reports_raw.append(json.load(f))

    print(f"[1/4] 加载数据...")
    print(f"  压力回归样本: {len(reports_raw)}期")
    for r in reports_raw:
        print(f"  {r['report_period']}: alert_lines={len(r.get('alert_lines',[]))} request_lines={len(r.get('request_lines',[]))}")
    print()

    # 适配
    print("[2/4] 适配处理...")
    from src.loaders.november_adapter import adapt_report_to_engine_format

    adapted_reports = []
    all_items = []
    all_alerts = []
    all_closures = []
    all_extensions = []

    for r in reports_raw:
        adapted = adapt_report_to_engine_format(r)
        adapted['_raw_report'] = r
        adapted['report_id'] = r.get('report_id', f"PMO-{r['report_period']}")
        adapted['report_period'] = r['report_period']
        adapted['start_date'] = r.get('start_date', '')
        adapted['end_date'] = r.get('end_date', '')
        adapted_reports.append(adapted)

        # 统计
        ka = adapted.get('key_alerts', [])
        cr = adapted.get('key_requests', {}).get('closure_requests', [])
        er = adapted.get('key_requests', {}).get('extension_requests', [])
        all_items.append(len(ka) + len(cr) + len(er))
        all_alerts.extend(ka)
        all_closures.extend(cr)
        all_extensions.extend(er)
        print(f"  {r['report_period']}: alerts={len(ka)} closures={len(cr)} extensions={len(er)}")

    total_items = sum(all_items)
    print(f"  归一化事项总数: {total_items}")
    print()

    # 加载台账
    print("[3/4] 台账加载...")
    from src.loaders.sample_loader import load_ledger, load_mapping, build_ledger_index
    try:
        ledger_data = load_ledger()
        mapping = load_mapping()
        ledger_index = build_ledger_index(ledger_data)
        print(f"  台账: {len(ledger_data['records'])}条")
        print(f"  映射: {len(mapping)}条")
    except Exception as e:
        ledger_data = {'records': []}
        mapping = []
        ledger_index = {}
        print(f"  ⚠️ 台账加载失败（使用空台账）: {e}")

    # 归一化
    print()
    print("[4/4] 归一化处理...")
    from src.adapters.normalizer import normalize_weekly_report

    all_normalized = []
    period_stats = {}
    for adapted in adapted_reports:
        period = adapted['report_period']
        items = normalize_weekly_report(adapted, ledger_index, mapping)
        all_normalized.extend(items)
        period_stats[period] = len(items)
        print(f"  {period}: {len(items)}事项")

    # 统计
    yellow = sum(1 for it in all_normalized if it.get('is_yellow_alert'))
    closure = sum(1 for it in all_normalized if it.get('is_closure_request'))
    extension = sum(1 for it in all_normalized if it.get('is_extension_request'))
    normal = len(all_normalized) - yellow - closure - extension

    print()
    print(f"【压力回归统计】")
    print(f"  总事项: {len(all_normalized)}")
    print(f"  黄灯: {yellow}")
    print(f"  结项申请: {closure}")
    print(f"  延期申请: {extension}")
    print(f"  正常: {normal}")
    print()

    # 生成输出
    from src.generators.summary_generator import generate_leadership_summary as generate_summary, format_plain_summary
    from src.generators.ledger_generator import generate_ledger_output as generate_ledger, format_ledger_plain
    from src.generators.risk_list_generator import generate_risk_list, format_risk_list_plain

    print("[输出生成]...")
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # 模拟引擎结果
    engine_results = []
    for it in all_normalized:
        r = {'status_summary': {'overall': '黄灯' if it.get('is_yellow_alert') else '正常'},
             'risk_assessment': {'level': '高' if it.get('is_yellow_alert') else '低'},
             'escalation_recommended': False}
        engine_results.append(r)

    summary = generate_summary(all_normalized, engine_results)  # generate_leadership_summary
    summary_text = format_plain_summary(summary)

    ledger_out = generate_ledger(all_normalized, engine_results, mapping)  # generate_ledger_output
    ledger_text = format_ledger_plain(ledger_out)

    risk_out = generate_risk_list(all_normalized, engine_results)
    risk_text = format_risk_list_plain(risk_out)

    # 保存
    with open(os.path.join(OUTPUT_DIR, f'领导摘要_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write(summary_text)
    with open(os.path.join(OUTPUT_DIR, f'事项总台账_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write(ledger_text)
    with open(os.path.join(OUTPUT_DIR, f'风险清单_{timestamp}.txt'), 'w', encoding='utf-8') as f:
        f.write(risk_text)
    with open(os.path.join(TMP_DIR, f'normalized_{timestamp}.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'normalized_items': all_normalized,
            'slice': '03_stress_regression_aug_sep',
            'timestamp': timestamp,
            'stats': {
                'total': len(all_normalized),
                'yellow': yellow,
                'closure': closure,
                'extension': extension,
                'normal': normal,
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"  领导摘要: 领导摘要_{timestamp}.txt")
    print(f"  事项总台账: 事项总台账_{timestamp}.txt")
    print(f"  风险清单: 风险清单_{timestamp}.txt")
    print(f"  归一化: normalized_{timestamp}.json")
    print()
    print("✅ Week 4 压力回归完成")

    return {
        'total': len(all_normalized),
        'yellow': yellow,
        'closure': closure,
        'extension': extension,
        'normal': normal,
        'period_stats': period_stats,
        'timestamp': timestamp,
    }

if __name__ == '__main__':
    result = run_week4_stress()
    print()
    print("=== 最终结果 ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
