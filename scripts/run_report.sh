#!/usr/bin/env bash
# ============================================================
# run_report.sh - 当前阶段简报
# 用途：输出原型当前状态、已验证项、缺口清单
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo " 重点项目执行跟踪数字员工 - 阶段简报"
echo "============================================"
echo " 时间: $(date '+%Y-%m-%d %H:%M')"
echo ""

echo "【原型目标】"
echo " 单项目结构化输入 → 标准化输出（含事实/判断/建议分离）"
echo " 最小可验证闭环，规则推理，无需 LLM"
echo ""

echo "【已完成文件】"
find "$PROJECT_DIR/project" -type f | sort | while read f; do
    echo "  $f"
done
echo ""

echo "【演示入口】"
echo "  bash scripts/run_dev.sh      # 运行演示案例"
echo "  bash scripts/run_smoke.sh     # 冒烟测试"
echo "  bash scripts/run_report.sh    # 本简报"
echo ""

echo "【当前最小闭环状态】"
echo "  ✅ 输入: project/data/DEMO_CASE_01.json"
echo "  ✅ 引擎: project/app/engine.py (规则推理)"
echo "  ✅ 输出: JSON 结构化结果（事实/判断/建议分离）"
echo "  ✅ 演示: scripts/run_dev.sh"
echo "  ✅ 测试: scripts/run_smoke.sh (5个测试用例)"
echo ""

echo "【当前缺口】"
echo "  ⚠ 无前端界面（下一轮可做）"
echo "  ⚠ 无多项目汇总能力"
echo "  ⚠ 无历史数据持久化"
echo "  ⚠ 规则数量有限（5条），覆盖度待扩"
echo "  ⚠ 无 API / Web 服务封装"
echo ""

echo "【下一轮最值得做的3件事】"
echo "  1. 扩规则：增加里程碑对比、承诺时间与当前时间差等判断"
echo "  2. 接数据：对接飞书/企微，获取真实项目数据"
echo "  3. 做成 Web 服务：提供 HTTP 接口，前端输入输出"
echo ""
echo "============================================"
