#!/usr/bin/env python3
"""
阶段4B主运行脚本 - 端到端最小原型执行
输入：样本（周报+台账+映射）
处理：归一化 → 规则判断 → 输出生成
输出：领导摘要 + 事项台账 + 风险清单
"""

import sys
import os
import json
import datetime

# 添加src路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.loaders.sample_loader import load_weekly_reports, load_ledger, load_mapping, build_ledger_index
from src.adapters.normalizer import normalize_weekly_report, normalize_ledger_record
from src.generators.summary_generator import generate_leadership_summary, format_plain_summary
from src.generators.ledger_generator import generate_ledger_output, format_ledger_plain
from src.generators.risk_list_generator import generate_risk_list, format_risk_list_plain
from app.engine import ProjectTracker

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'output')
TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'tmp')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


def run_minimal_prototype():
    """执行最小原型端到端流程"""
    print("=" * 60)
    print("阶段4B - 条件性原型执行")
    print("=" * 60)
    print()

    # Step 1: 加载数据
    print("[1/6] 加载样本数据...")
    weekly_reports = load_weekly_reports()
    ledger_data = load_ledger()
    mapping = load_mapping()
    ledger_index = build_ledger_index(ledger_data)
    print(f"  周报：{len(weekly_reports)}期")
    print(f"  台账：{len(ledger_data['records'])}条主记录")
    print(f"  映射：{len(mapping)}条")
    print()

    # Step 2: 归一化
    print("[2/6] 归一化处理...")
    all_normalized = []
    for wr in weekly_reports:
        period = wr['report_meta']['report_period']
        items = normalize_weekly_report(wr, ledger_index, mapping)
        all_normalized.extend(items)
        print(f"  {period}：{len(items)}事项")
    print(f"  归一化事项总数：{len(all_normalized)}")
    print()

    # Step 3: 规则判断
    print("[3/6] 规则判断...")
    engine = ProjectTracker()
    engine_results = []
    for item in all_normalized:
        result = engine.evaluate(item)
        engine_results.append(result)
    print(f"  判断完成：{len(engine_results)}事项")
    print()

    # Step 4: 生成输出
    print("[4/6] 生成输出...")

    # 领导摘要
    summary = generate_leadership_summary(all_normalized, engine_results)
    summary_text = format_plain_summary(summary)
    print(f"  领导摘要：{summary['总事项数']}事项")

    # 事项总台账
    ledger_out = generate_ledger_output(all_normalized, engine_results, mapping)
    ledger_text = format_ledger_plain(ledger_out)
    print(f"  事项台账：{ledger_out['总事项数']}事项")

    # 风险清单
    risk_out = generate_risk_list(all_normalized, engine_results)
    risk_text = format_risk_list_plain(risk_out)
    print(f"  风险清单：{risk_out['总风险数']}风险项")
    print()

    # Step 5: 保存输出
    print("[5/6] 保存输出...")
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

    # 保存归一化中间结果（JSON）
    normalized_path = os.path.join(TMP_DIR, f'normalized_{ts}.json')
    with open(normalized_path, 'w', encoding='utf-8') as f:
        json.dump({
            'normalized_items': all_normalized,
            'engine_results': engine_results,
        }, f, ensure_ascii=False, indent=2)
    print(f"  归一化中间结果 → {normalized_path}")
    print()

    # Step 6: 冒烟测试检查
    print("[6/6] A1-A7冒烟测试检查...")
    smoke_results = []

    # A1: 样本可读
    try:
        assert len(weekly_reports) == 3
        assert len(ledger_data['records']) >= 16
        smoke_results.append(('A1 样本可读', 'PASS', f'周报{len(weekly_reports)}期+台账{len(ledger_data["records"])}条'))
    except Exception as e:
        smoke_results.append(('A1 样本可读', 'FAIL', str(e)))

    # A2: 输入可解析
    try:
        assert len(all_normalized) >= 10
        assert all('project_name' in n for n in all_normalized)
        smoke_results.append(('A2 输入可解析', 'PASS', f'归一化{len(all_normalized)}条'))
    except Exception as e:
        smoke_results.append(('A2 输入可解析', 'FAIL', str(e)))

    # A3: 事项可抽取
    try:
        has_alerts = any(n.get('is_yellow_alert') for n in all_normalized)
        has_closures = any(n.get('is_closure_request') for n in all_normalized)
        assert has_alerts or has_closures
        smoke_results.append(('A3 事项可抽取', 'PASS', f'黄灯:{has_alerts},结项:{has_closures}'))
    except Exception as e:
        smoke_results.append(('A3 事项可抽取', 'FAIL', str(e)))

    # A4: 规则可判断
    try:
        assert len(engine_results) == len(all_normalized)
        assert all('risk_assessment' in r for r in engine_results)
        smoke_results.append(('A4 规则可判断', 'PASS', f'{len(engine_results)}事项'))
    except Exception as e:
        smoke_results.append(('A4 规则可判断', 'FAIL', str(e)))

    # A5: 领导摘要可生成
    try:
        assert summary['总事项数'] > 0
        assert '已完成/已解决' in summary
        assert '延期事项' in summary
        smoke_results.append(('A5 领导摘要可生成', 'PASS', f'{summary["总事项数"]}事项'))
    except Exception as e:
        smoke_results.append(('A5 领导摘要可生成', 'FAIL', str(e)))

    # A6: 事项总台账可生成
    try:
        assert ledger_out['总事项数'] > 0
        assert len(ledger_out['事项列表']) > 0
        smoke_results.append(('A6 事项总台账可生成', 'PASS', f'{ledger_out["总事项数"]}事项'))
    except Exception as e:
        smoke_results.append(('A6 事项总台账可生成', 'FAIL', str(e)))

    # A7: 风险清单可生成
    try:
        assert '风险列表' in risk_out
        smoke_results.append(('A7 风险清单可生成', 'PASS', f'{risk_out["总风险数"]}风险项'))
    except Exception as e:
        smoke_results.append(('A7 风险清单可生成', 'FAIL', str(e)))

    # 打印结果
    print()
    print("=" * 60)
    print("A1-A7 冒烟测试结果")
    print("=" * 60)
    passed = 0
    for name, status, detail in smoke_results:
        icon = '✅' if status == 'PASS' else '❌'
        print(f"  {icon} {name}: {status} ({detail})")
        if status == 'PASS':
            passed += 1
    print()
    print(f"通过：{passed}/7")
    print("=" * 60)

    # 打印领导摘要预览
    print()
    print("【领导摘要预览】")
    print(summary_text[:1500])
    print()

    return {
        'smoke_results': smoke_results,
        'passed': passed,
        'summary': summary,
        'ledger_out': ledger_out,
        'risk_out': risk_out,
        'output_files': {
            '领导摘要': summary_path,
            '事项总台账': ledger_path,
            '风险清单': risk_path,
            '归一化中间结果': normalized_path,
        }
    }


if __name__ == '__main__':
    result = run_minimal_prototype()
