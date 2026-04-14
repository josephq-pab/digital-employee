# RUN_DEMO.md

## 快速演示

### 前置条件

- Python 3.8+
- 无需额外依赖（本原型零外部依赖）

### 方式一：本地演示（run_dev）

```bash
cd /home/admin/.openclaw/workspace-digital-employee
bash scripts/run_dev.sh
```

输出示例：演示 JSON 数据经过推理引擎后的完整输出。

### 方式二：冒烟测试（run_smoke）

```bash
bash scripts/run_smoke.sh
```

执行所有测试用例，检查输出是否符合验收标准。

### 方式三：阶段简报（run_report）

```bash
bash scripts/run_report.sh
```

输出当前阶段状态报告（原型完成度、已验证项、缺口清单）。

## 手动运行核心逻辑

```bash
cd /home/admin/.openclaw/workspace-digital-employee/project
python3 -c "
import json, sys
sys.path.insert(0, 'app')
from engine import ProjectTracker
tracker = ProjectTracker()
with open('data/DEMO_CASE_01.json') as f:
    result = tracker.evaluate(json.load(f))
print(json.dumps(result, ensure_ascii=False, indent=2))
"
```

## 下一步

1. 替换 `data/DEMO_CASE_01.json` 为真实项目数据即可验证
2. 核心逻辑在 `app/engine.py`，按 EVAL_RULES.md 增补规则
