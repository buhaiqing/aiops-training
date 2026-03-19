#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 类型定义模块
使用 dataclass 和 TypeVar 定义核心数据类型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from constants import SeverityLevel, PriorityLevel, MetricType, RunbookID


@dataclass
class Alert:
    """告警数据模型"""

    alert_id: str
    timestamp: datetime
    source: str
    metric: str
    severity: SeverityLevel
    value: float
    threshold: float
    host: str
    message: str
    labels: Dict[str, str] = field(default_factory=dict)
    mount_point: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """从字典创建 Alert 实例"""
        # 处理时间戳
        ts = data.get("timestamp", "")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

        # 处理 severity 枚举
        severity = data.get("severity", "info")
        if isinstance(severity, str):
            severity = SeverityLevel(severity)

        return cls(
            alert_id=data["alert_id"],
            timestamp=ts,
            source=data["source"],
            metric=data["metric"],
            severity=severity,
            value=float(data["value"]),
            threshold=float(data["threshold"]),
            host=data["host"],
            message=data["message"],
            labels=data.get("labels", {}),
            mount_point=data.get("mount_point"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metric": self.metric,
            "severity": self.severity.value,
            "value": self.value,
            "threshold": self.threshold,
            "host": self.host,
            "message": self.message,
            "labels": self.labels,
            "mount_point": self.mount_point,
        }


@dataclass
class AlertChainItem:
    """告警链中的单个项目"""

    metric: str
    severity: SeverityLevel
    value: float
    message: str


@dataclass
class Correlation:
    """告警关联分析结果"""

    host: str
    alert_chain: List[AlertChainItem]
    time_span_minutes: float
    severity_escalation: bool
    potential_root_cause: str
    alerts: List[Alert] = field(default_factory=list)

    @property
    def metrics(self) -> List[str]:
        """获取所有指标类型"""
        return [item.metric for item in self.alert_chain]

    @property
    def has_critical(self) -> bool:
        """是否包含严重告警"""
        return any(item.severity == SeverityLevel.CRITICAL for item in self.alert_chain)


@dataclass
class RootCause:
    """根因分析结果"""

    primary: str
    evidence: List[str]
    confidence: int


@dataclass
class Impact:
    """影响评估"""

    business: str
    users: str
    data: str


@dataclass
class Action:
    """处置动作"""

    priority: PriorityLevel
    action: str
    command: str
    expected_outcome: str


@dataclass
class RunbookStep:
    """运维手册步骤"""

    step: int
    action: str
    command: str
    check: str


@dataclass
class Runbook:
    """运维手册"""

    runbook_id: RunbookID
    title: str
    trigger_condition: str
    severity: str
    steps: List[RunbookStep]
    escalation: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Runbook":
        """从字典创建 Runbook 实例"""
        steps = [
            RunbookStep(
                step=s["step"],
                action=s["action"],
                command=s["command"],
                check=s["check"],
            )
            for s in data.get("steps", [])
        ]

        return cls(
            runbook_id=RunbookID(data["runbook_id"]),
            title=data["title"],
            trigger_condition=data["trigger_condition"],
            severity=data["severity"],
            steps=steps,
            escalation=data.get("escalation", ""),
        )


@dataclass
class Diagnosis:
    """诊断结果"""

    root_cause: RootCause
    impact: Impact
    actions: List[Action]
    runbook: Optional[Runbook] = None


@dataclass
class Scenario:
    """故障场景"""

    scenario_id: str
    title: str
    description: str
    root_cause: str
    impact: str
    alert_ids: List[str]
    timeline_hours: float


@dataclass
class Config:
    """应用配置"""

    alerts_file: Path
    scenarios_file: Path
    runbooks_dir: Path
    output_dir: Path
    output_format: str = "llm_diagnosis_{timestamp}.md"
    log_level: str = "INFO"
    enable_cache: bool = True
    cache_ttl: int = 300  # 5 minutes

    @classmethod
    def default(cls) -> "Config":
        """返回默认配置"""
        return cls(
            alerts_file=Path("alert_data/alerts.json"),
            scenarios_file=Path("alert_data/scenarios.json"),
            runbooks_dir=Path("runbook_templates"),
            output_dir=Path("."),
        )


# 异常类型
class AlertLoadError(Exception):
    """告警加载错误"""

    pass


class CorrelationError(Exception):
    """关联分析错误"""

    pass


class RunbookLoadError(Exception):
    """运维手册加载错误"""

    pass


class DiagnosisError(Exception):
    """诊断错误"""

    pass
