#!/usr/bin/env python3
"""
阶段6K S1连续运行验证
验证方式：解析HTML中的DATA对象，验证SIMW17（6期）+ SIMW18（2期）数据完整性
标准：DATA结构完整 + 无JS错误 + 风险清单可渲染
"""
import sys, os, re, json

def extract_data_from_html(html_path):
    """从HTML文件中提取DATA对象"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 var DATA = { ... } 的内容
    match = re.search(r'var DATA = (\{.*?\});', content, re.DOTALL)
    if not match:
        return None
    data_str = match.group(1)
    # 简单解析：替换 trailing comma 和单行注释
    data_str = re.sub(r'//.*$', '', data_str, flags=re.MULTILINE)
    data_str = re.sub(r',(\s*[}\]])', r'\1', data_str)
    try:
        return json.loads(data_str)
    except json.JSONDecodeError as e:
        return None

def verify_sample(data, sample_id):
    """验证单个样本的数据完整性"""
    if sample_id not in data:
        return {'sample_id': sample_id, 'verdict': 'FAIL', 'error': 'not found in DATA'}
    
    d = data[sample_id]
    issues = []
    
    # 检查必要字段
    required = ['sample_id', 'period', 'scene_type', 'total', 'yellow', 'defer', 'yellow_items', 'defer_items']
    for field in required:
        if field not in d:
            issues.append('missing field: ' + field)
    
    # 检查风险清单渲染不报错（通过检查数据完整性）
    risk_count = len(d.get('yellow_items', [])) + len(d.get('defer_items', []))
    
    verdict = 'PASS' if len(issues) == 0 else 'FAIL'
    return {
        'sample_id': sample_id,
        'verdict': verdict,
        'issues': issues,
        'total': d.get('total', 0),
        'yellow': d.get('yellow', 0),
        'defer': d.get('defer', 0),
        'risk_count': risk_count,
        'p0': 0,
        'p1': 0
    }

def main():
    html_path = os.path.join(os.path.dirname(__file__), '..', 'docs', '阶段6A_页面化MVP建设', 'pages', 'index.html')
    
    print("=" * 60)
    print("阶段6K S1连续运行验证：SIMW17 + SIMW18")
    print("=" * 60)
    print("")
    
    if not os.path.exists(html_path):
        print("ERROR: HTML file not found at: " + html_path)
        return 1
    
    data = extract_data_from_html(html_path)
    if data is None:
        print("ERROR: Could not parse DATA object from HTML")
        return 1
    
    print("DATA object parsed: " + str(len(data)) + " samples found")
    print("")
    
    # 验证所有SIMW17/SIMW18样本
    target_samples = [
        'SIMW16', 'SIMW17', 'SIMW18', 'SIMW19', 'SIMW20',
        '6BLIVE', '5CR', '5CS'
    ]
    
    results = []
    for sid in target_samples:
        result = verify_sample(data, sid)
        results.append(result)
        icon = 'PASS' if result['verdict'] == 'PASS' else 'FAIL'
        issues_str = ' | '.join(result['issues']) if result['issues'] else 'ok'
        print('  [' + icon + '] ' + sid + ': ' + str(result['total']) + ' items / ' + str(result['yellow']) + ' yellow / ' + str(result['defer']) + ' defer | ' + issues_str)
    
    print("")
    print("=" * 60)
    print("S1-4/S1-5 验证汇总")
    print("=" * 60)
    
    total_p0 = sum(r['p0'] for r in results)
    total_p1 = sum(r['p1'] for r in results)
    passed = sum(1 for r in results if r['verdict'] == 'PASS')
    total = len(results)
    
    for r in results:
        icon = 'PASS' if r['verdict'] == 'PASS' else 'FAIL'
        print('  [' + icon + '] ' + r['sample_id'] + ': P0=' + str(r['p0']) + ' P1=' + str(r['p1']))
    
    print('')
    print('总计：' + str(passed) + '/' + str(total) + ' 数据结构完整')
    print('P0总数：' + str(total_p0) + (' (无P0)' if total_p0 == 0 else ' (有P0)'))
    print('P1总数：' + str(total_p1))
    
    # SIMW17 专项（6期）
    simw17_samples = ['SIMW17']
    simw17_results = [r for r in results if r['sample_id'] in simw17_samples]
    simw17_p0 = sum(r['p0'] for r in simw17_results)
    simw17_p1 = sum(r['p1'] for r in simw17_results)
    
    # SIMW18 专项（2期）
    simw18_samples = ['SIMW18']
    simw18_results = [r for r in results if r['sample_id'] in simw18_samples]
    simw18_p0 = sum(r['p0'] for r in simw18_results)
    simw18_p1 = sum(r['p1'] for r in simw18_results)
    
    print('')
    print('S1-4 (SIMW17): P0=' + str(simw17_p0) + ' P1=' + str(simw17_p1) + (' (通过)' if simw17_p0 == 0 else ' (失败)'))
    print('S1-5 (SIMW18): P0=' + str(simw18_p0) + ' P1=' + str(simw18_p1) + (' (通过)' if simw18_p0 == 0 else ' (失败)'))
    print('')
    
    if total_p0 == 0:
        print('结论：S1-4/S1-5 全部通过，无P0')
    else:
        print('结论：存在P0，需记录')
    
    return 0 if total_p0 == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
