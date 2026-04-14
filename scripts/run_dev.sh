#!/usr/bin/env bash
# ============================================================
# run_dev.sh - 本地演示 / 开发入口
# 用途：加载 DEMO_CASE_01.json，运行推理引擎，输出完整结果
# 下一步：接入真实项目数据 or 增加输入参数支持
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$PROJECT_DIR/project/app"
DATA_DIR="$PROJECT_DIR/project/data"

echo "============================================"
echo " 数字员工实验室 - 重点项目执行跟踪演示"
echo "============================================"
echo ""

# 构造 Python 执行路径
PYTHON_CMD="python3"
if ! command -v python3 &>/dev/null; then
    PYTHON_CMD="python"
fi

echo "[1] 加载演示案例: data/DEMO_CASE_01.json"
cat "$DATA_DIR/DEMO_CASE_01.json"
echo ""

echo "[2] 运行推理引擎..."
RESULT=$($PYTHON_CMD -c "
import json, sys
sys.path.insert(0, '$APP_DIR')
from engine import ProjectTracker
tracker = ProjectTracker()
with open('$DATA_DIR/DEMO_CASE_01.json') as f:
    result = tracker.evaluate(json.load(f))
print(json.dumps(result, ensure_ascii=False, indent=2))
" 2>&1)

if [ $? -ne 0 ]; then
    echo "[ERROR] 引擎运行失败:"
    echo "$RESULT"
    exit 1
fi

echo "[3] 推理结果:"
echo "$RESULT"
echo ""
echo "[OK] 演示完成"
