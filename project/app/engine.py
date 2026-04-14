"""
ProjectTracker - 重点项目执行跟踪推理引擎（最小原型）

本模块：纯规则推理，无需 LLM
输入：结构化项目状态字典
输出：结构化评估结果（含事实/判断/建议分离）
"""

import re
from typing import Any


# ============================================================
# 规则定义
# ============================================================

# 顺序重要：更具体的模式放前面，避免被通用模式短路
LAG_PATTERNS = [
    (re.compile(r'严重滞后|大幅落后|critical delay', re.I), '严重滞后'),
    (re.compile(r'停滞|卡住|blocked|stuck', re.I), '进度停滞'),
    (re.compile(r'滞后|延后|behind', re.I), '进度滞后'),
    (re.compile(r'未完成|未到位|incomplete|not done', re.I), '未完成承诺'),
]

RISK_TRIGGERS = [
    ('escalation_requested', '请求领导介入'),
]

RISK_SELF_REPORTED_PATTERNS = [
    (re.compile(r'风险|risk|uncertain|不确定|可能影响', re.I), '责任人自述风险'),
]

NORMAL_PATTERNS = [
    (re.compile(r'完成|完成100%|全部完成|已交付|delivered|done|complete', re.I), '已完成'),
    (re.compile(r'正常|顺利|按计划|on track|on schedule', re.I), '进度正常'),
]


# ============================================================
# 推理引擎
# ============================================================

class ProjectTracker:
    """重点项目执行状态评估引擎"""

    def evaluate(self, project_input: dict) -> dict:
        facts = self._extract_facts(project_input)
        rules_fired = []
        risk_signals = []
        status_signals = []

        # 1. 风险信号检测
        for field, label in RISK_TRIGGERS:
            if project_input.get(field, False):
                risk_signals.append(label)
                rules_fired.append(f'rule_{field}')

        risk_text = project_input.get('risk_points', '') or ''
        for pattern, label in RISK_SELF_REPORTED_PATTERNS:
            if pattern.search(risk_text):
                risk_signals.append(label)
                rules_fired.append('rule_risk_self_reported')
                break

        # 2. 进度信号检测
        progress_text = project_input.get('current_progress', '') or ''
        for pattern, label in LAG_PATTERNS:
            if pattern.search(progress_text):
                status_signals.append(label)
                rules_fired.append(f'rule_{label}')
                break
        else:
            for pattern, label in NORMAL_PATTERNS:
                if pattern.search(progress_text):
                    status_signals.append(label)
                    rules_fired.append(f'rule_normal_progress')
                    break

        # 3. 风险等级判定
        risk_level, escalation, overall_override = self._judge_risk(risk_signals, status_signals)

        # 4. 状态摘要
        status_summary = self._build_status(project_input, status_signals)

        # 5. 风险摘要
        risk_summary = self._build_risk_summary(risk_signals, status_signals)

        # 6. 建议动作
        actions = self._suggest_actions(risk_signals, status_signals, risk_level)

        # 7. 原始信号
        raw_signals = [s for s in risk_signals + status_signals if s]

        # 8. 组装输出，注入 overall_override（如果有）
        result = {
            'project_name': project_input.get('project_name', ''),
            'status_summary': status_summary,
            'risk_assessment': {
                'level': risk_level,
                'triggered_by': list(set(risk_signals)),
                'summary': risk_summary,
            },
            'suggested_actions': actions,
            'escalation_recommended': escalation,
            'reasoning': {
                'facts_extracted': facts,
                'rules_applied': list(set(rules_fired)),
                'raw_signal': '；'.join(raw_signals) if raw_signals else '无明显风险信号',
            },
        }
        if overall_override:
            result['status_summary'] = {
                'overall': overall_override,
                'progress_text': status_summary['progress_text'],
                'completion_estimate': '因触发升级条件，整体状态为危险',
            }
        return result

    # ----------------------------------------------------------
    # 内部方法
    # ----------------------------------------------------------

    def _extract_facts(self, inp: dict) -> list:
        """从输入中提炼不可争辩的事实"""
        facts = []
        promised = inp.get('promised_items', '')
        if promised:
            facts.append(f'承诺事项：{promised}')
        progress = inp.get('current_progress', '')
        if progress:
            facts.append(f'当前进展：{progress}')
        risk = inp.get('risk_points', '')
        if risk:
            facts.append(f'风险自述：{risk}')
        if inp.get('escalation_requested'):
            facts.append('责任人主动请求领导介入')
        return facts

    def _judge_risk(self, risk_signals: list, status_signals: list) -> tuple:
        """判定风险等级和是否建议升级"""
        escalation = False
        overall_override = None

        # 请求升级 → 直接建议升级
        if '请求领导介入' in risk_signals:
            return '高', True, '危险'

        # 严重滞后 → 高风险
        if '严重滞后' in status_signals:
            return '高', True, '危险'

        # 进度滞后 + 有风险自述 → 中风险
        has_lag = any(s in status_signals for s in ['进度滞后', '未完成承诺', '进度停滞'])
        has_risk_self = '责任人自述风险' in risk_signals
        if has_lag and has_risk_self:
            return '中', False, None

        # 只有进度滞后 → 中风险
        if has_lag:
            return '中', False, None

        # 只有风险自述 → 低风险
        if has_risk_self:
            return '低', False, None

        return '低', False, None

    def _build_status(self, inp: dict, status_signals: list) -> dict:
        """构建状态摘要"""
        progress = inp.get('current_progress', '') or ''
        promised = inp.get('promised_items', '') or ''

        if any(s in status_signals for s in ['严重滞后', '进度停滞']):
            overall = '危险'
            estimate = '承诺事项按时完成风险极高'
        elif any(s in status_signals for s in ['进度滞后', '未完成承诺']):
            overall = '关注'
            estimate = '承诺事项存在无法按时完成的风险'
        elif status_signals or progress:
            overall = '正常'
            estimate = '当前未发现明显进度风险'
        else:
            overall = '正常'
            estimate = '信息不足，无法评估'

        return {
            'overall': overall,
            'progress_text': progress[:100],
            'completion_estimate': estimate,
        }

    def _build_risk_summary(self, risk_signals: list, status_signals: list) -> str:
        parts = []
        if '进度滞后' in status_signals:
            parts.append('进度滞后是主要风险点')
        if '严重滞后' in status_signals:
            parts.append('进度严重落后于计划')
        if '责任人自述风险' in risk_signals:
            parts.append('责任人已主动识别风险')
        if '请求领导介入' in risk_signals:
            parts.append('责任人请求领导介入')
        return ' '.join(parts) if parts else '未发现显著风险'

    def _suggest_actions(self, risk_signals: list, status_signals: list, level: str) -> list:
        """生成建议动作"""
        actions = []
        if level == '高':
            actions.append('建议尽快向领导汇报，获取资源支持')
            actions.append('制定应急计划，评估能否分阶段交付')
        if '进度滞后' in status_signals or '严重滞后' in status_signals:
            actions.append('分析滞后根因，明确下一步行动和责任人')
        if '责任人自述风险' in risk_signals:
            actions.append('对自述风险进行深入分析，制定缓释措施')
        if not actions:
            actions.append('继续保持当前节奏，定期更新进展')
        return actions
