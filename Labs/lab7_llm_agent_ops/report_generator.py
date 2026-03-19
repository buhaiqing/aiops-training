#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 报告生成器
分离报告渲染逻辑
"""

from typing import List
from datetime import datetime
from collections import defaultdict

from constants import (
    DISPLAY_WIDTH,
    DATETIME_FORMAT,
    SEVERITY_ICONS,
    SeverityLevel,
    PriorityLevel,
)
from types import Alert, Diagnosis, Correlation
from logger import LoggerMixin


class ReportRenderer(LoggerMixin):
    """Markdown 报告渲染器"""

    def render(self, alerts: List[Alert], diagnoses: List[Diagnosis]) -> str:
        """渲染完整报告"""
        sections = []

        # 报告头部
        sections.append(self._render_header())

        # 总体态势
        sections.append(self._render_overview(alerts))

        # 逐个事件诊断
        for i, diagnosis in enumerate(diagnoses, 1):
            sections.append(self._render_diagnosis(i, diagnosis))

        # 总结
        sections.append(self._render_summary(diagnoses))

        return "\n".join(sections)

    def _render_header(self) -> str:
        """渲染报告头部"""
        lines = [
            "=" * DISPLAY_WIDTH,
            "🤖 LLM Agent 智能诊断报告（优化版）",
            "=" * DISPLAY_WIDTH,
            f"生成时间：{datetime.now().strftime(DATETIME_FORMAT)}",
            "",
        ]
        return "\n".join(lines)

    def _render_overview(self, alerts: List[Alert]) -> str:
        """渲染总体态势"""
        # 统计
        severity_count = defaultdict(int)
        for alert in alerts:
            severity_count[alert.severity] += 1

        critical = severity_count[SeverityLevel.CRITICAL]
        warning = severity_count[SeverityLevel.WARNING]
        info = severity_count.get(SeverityLevel.INFO, 0)

        # 确定整体严重级别
        if critical > 0:
            overall = "🔴 严重"
        elif warning > 0:
            overall = "🟡 警告"
        else:
            overall = "🟢 正常"

        hosts = len(set(a.host for a in alerts))

        lines = [
            f"【整体态势】{overall}",
            f"  - 紧急告警：{critical} 条",
            f"  - 警告告警：{warning} 条",
            f"  - 提示信息：{info} 条",
            f"  - 影响系统：{hosts} 个",
            "",
        ]
        return "\n".join(lines)

    def _render_diagnosis(self, index: int, diagnosis: Diagnosis) -> str:
        """渲染单个诊断结果"""
        lines = [
            "=" * DISPLAY_WIDTH,
            f"【事件 {index}】诊断详情",
            "=" * DISPLAY_WIDTH,
            "",
            "🔍 根因分析:",
            f"  最可能原因：{diagnosis.root_cause.primary}",
            f"  置信度：{diagnosis.root_cause.confidence}%",
            f"  支持证据：",
        ]

        for evidence in diagnosis.root_cause.evidence:
            lines.append(f"    - {evidence}")

        lines.extend(
            [
                "",
                "💥 影响评估:",
                f"  业务影响：{diagnosis.impact.business}",
                f"  用户影响：{diagnosis.impact.users}",
                f"  数据风险：{diagnosis.impact.data}",
                "",
                "💡 处置建议:",
            ]
        )

        for i, action in enumerate(diagnosis.actions, 1):
            lines.extend(
                [
                    f"  {i}. {action.priority.value}: {action.action}",
                    f"     命令：{action.command}",
                    f"     预期：{action.expected_outcome}",
                ]
            )

        if diagnosis.runbook:
            lines.extend(
                [
                    "",
                    "📚 推荐运维手册:",
                    f"  - {diagnosis.runbook.title} ({diagnosis.runbook.runbook_id.value})",
                    f"    严重级别：{diagnosis.runbook.severity}",
                    f"    关键步骤：{len(diagnosis.runbook.steps)} 步",
                ]
            )

        lines.append("")
        return "\n".join(lines)

    def _render_summary(self, diagnoses: List[Diagnosis]) -> str:
        """渲染总结"""
        lines = [
            "=" * DISPLAY_WIDTH,
            "【总结与建议】",
            "=" * DISPLAY_WIDTH,
            "",
            "🎯 优先级排序:",
        ]

        # 按优先级排序
        p0_actions = []
        for diag in diagnoses:
            for action in diag.actions:
                if action.priority == PriorityLevel.P0:
                    p0_actions.append(action.action)

        for i, action in enumerate(p0_actions[:5], 1):
            lines.append(f"  {i}. P0 - {action} - 立即处理")

        lines.extend(
            [
                "",
                "📊 系统优化建议:",
                "  1. 考虑实施预测性告警，提前发现趋势",
                "  2. 完善自动化处置流程，缩短 MTTR",
                "  3. 定期进行容量规划评估",
                "  4. 建立知识库，积累诊断经验",
                "",
                "=" * DISPLAY_WIDTH,
                "报告生成完毕",
                "=" * DISPLAY_WIDTH,
            ]
        )

        return "\n".join(lines)


class JSONReportRenderer(ReportRenderer):
    """JSON 格式报告渲染器"""

    def render(self, alerts: List[Alert], diagnoses: List[Diagnosis]) -> str:
        """渲染 JSON 格式报告"""
        import json

        data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_alerts": len(alerts),
                "total_diagnoses": len(diagnoses),
                "hosts": list(set(a.host for a in alerts)),
            },
            "diagnoses": [
                {
                    "root_cause": {
                        "primary": d.root_cause.primary,
                        "confidence": d.root_cause.confidence,
                        "evidence": d.root_cause.evidence,
                    },
                    "impact": {
                        "business": d.impact.business,
                        "users": d.impact.users,
                        "data": d.impact.data,
                    },
                    "actions": [
                        {
                            "priority": a.priority.value,
                            "action": a.action,
                            "command": a.command,
                            "expected": a.expected_outcome,
                        }
                        for a in d.actions
                    ],
                    "runbook": d.runbook.runbook_id.value if d.runbook else None,
                }
                for d in diagnoses
            ],
        }

        return json.dumps(data, indent=2, ensure_ascii=False)
