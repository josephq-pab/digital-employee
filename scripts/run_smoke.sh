#!/usr/bin/env bash
# ============================================================
# run_smoke.sh - 冒烟测试
# 用途：运行内置测试用例，验证最小原型是否满足 EVAL_RULES.md
# 下一步：接入 CI/CD 自动跑
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$PROJECT_DIR/project/app"
DATA_DIR="$PROJECT_DIR/project/data"

PYTHON_CMD="python3"
if ! command -v python3 &>/dev/null; then
    PYTHON_CMD="python"
fi

echo "============================================"
echo " 冒烟测试 - 重点项目执行跟踪数字员工"
echo "============================================"
echo ""

PASS=0
FAIL=0

run_test() {
    local name="$1"
    local input_json="$2"
    local expect_level="$3"
    local expect_escalation="$4"
    local expect_overall="$5"

    echo -n "[TEST] $name ... "
    RESULT=$($PYTHON_CMD -c "
import json, sys
sys.path.insert(0, '$APP_DIR')
from engine import ProjectTracker
tracker = ProjectTracker()
result = tracker.evaluate(json.loads('''$input_json'''))
print(json.dumps(result))
" 2>&1) || {
        echo "FAIL (script error)"
        FAIL=$((FAIL+1))
        return
    }

    # 解析输出（Python json.dumps 输出 Python bool 为 true/false，JSON 标准）
    LEVEL=$(echo "$RESULT" | $PYTHON_CMD -c "import json,sys; d=json.load(sys.stdin); print(d['risk_assessment']['level'])")
    # JSON bool 序列化为 "true"/"false"，转为小写比较
    ESC=$(echo "$RESULT" | $PYTHON_CMD -c "import json,sys; d=json.load(sys.stdin); print(str(d['escalation_recommended']).lower())")
    OVERALL=$(echo "$RESULT" | $PYTHON_CMD -c "import json,sys; d=json.load(sys.stdin); print(d['status_summary']['overall'])")
    FACTS=$(echo "$RESULT" | $PYTHON_CMD -c "import json,sys; d=json.load(sys.stdin); print(len(d['reasoning']['facts_extracted']))")

    OK=true
    [ "$expect_level" != "_" ] && [ "$LEVEL" != "$expect_level" ] && OK=false
    [ "$expect_escalation" != "_" ] && [ "$ESC" != "$expect_escalation" ] && OK=false
    [ "$expect_overall" != "_" ] && [ "$OVERALL" != "$expect_overall" ] && OK=false
    [ "$FACTS" -eq 0 ] && OK=false

    if $OK; then
        echo "PASS"
        PASS=$((PASS+1))
    else
        echo "FAIL (level=$LEVEL esc=$ESC overall=$OVERALL facts=$FACTS)"
        FAIL=$((FAIL+1))
    fi
}

# TC01: 正常进度，无风险点 → 低风险，不升级，正常
run_test "TC01-正常无风险" \
    '{"project_name":"测试项目A","owner":"李四","promised_items":"6月交付","current_progress":"已按计划完成","risk_points":"","escalation_requested":false}' \
    "低" "false" "正常"

# TC02: 进度滞后 + 风险自述 → 中风险，不升级，关注
run_test "TC02-滞后有风险" \
    '{"project_name":"测试项目B","owner":"王五","promised_items":"6月交付","current_progress":"进度滞后约2周","risk_points":"人员不足","escalation_requested":false}' \
    "中" "false" "关注"

# TC03: escalation_requested=true → 高风险，建议升级，危险
run_test "TC03-请求介入" \
    '{"project_name":"测试项目C","owner":"赵六","promised_items":"6月交付","current_progress":"正常","risk_points":"","escalation_requested":true}' \
    "高" "true" "危险"

# TC04: 严重滞后 → 高风险，建议升级，危险
run_test "TC04-严重滞后" \
    '{"project_name":"测试项目D","owner":"钱七","promised_items":"6月交付","current_progress":"进度严重滞后","risk_points":"","escalation_requested":false}' \
    "高" "true" "危险"

# TC05: 无风险点+正常进度 → 低风险，不升级，正常
run_test "TC05-无风险正常进度" \
    '{"project_name":"测试项目E","owner":"孙八","promised_items":"7月交付","current_progress":"开发顺利，按计划推进中","risk_points":"","escalation_requested":false}' \
    "低" "false" "正常"

echo ""
echo "============================================"
echo " 结果: PASS=$PASS FAIL=$FAIL"
if [ $FAIL -eq 0 ]; then
    echo " 状态: ALL TESTS PASSED"
else
    echo " 状态: SOME TESTS FAILED"
    exit 1
fi
