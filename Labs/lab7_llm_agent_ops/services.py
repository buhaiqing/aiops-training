#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 服务层
实现业务逻辑和核心算法
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import defaultdict

from logger import LoggerMixin
from types import (
    Alert,
    Correlation,
    AlertChainItem,
    RootCause,
    Impact,
    Action,
    Runbook,
    Scenario,
    Diagnosis,
    SeverityLevel,
    PriorityLevel,
    MetricType,
    RunbookID,
)
from constants import (
    SEVERITY_ICONS,
    SEVERITY_PRIORITY,
    DISPLAY_WIDTH,
    DEFAULT_CONFIDENCE_HIGH,
    DEFAULT_CONFIDENCE_MEDIUM,
    DEFAULT_CONFIDENCE_LOW,
)


class AlertCorrelationService(LoggerMixin):
    """告警关联分析服务"""

    def __init__(self):
        self.correlations: List[Correlation] = []

    def analyze(self, alerts: List[Alert]) -> List[Correlation]:
        """分析告警关联性"""
        self.log_operation("CORRELATION_START", alert_count=len(alerts))

        # 按主机分组（使用 defaultdict 优化）
        alerts_by_host: Dict[str, List[Alert]] = defaultdict(list)
        for alert in alerts:
            alerts_by_host[alert.host].append(alert)

        correlations = []

        for host, host_alerts in alerts_by_host.items():
            if len(host_alerts) < 2:
                continue

            # 按时间排序（使用稳定排序）
            host_alerts.sort(key=lambda x: x.timestamp)

            # 构建关联
            correlation = self._build_correlation(host, host_alerts)
            correlations.append(correlation)

        self.log_operation("CORRELATION_COMPLETE", correlation_count=len(correlations))
        return correlations

    def _build_correlation(self, host: str, alerts: List[Alert]) -> Correlation:
        """构建单个主机的告警关联"""
        first_time = alerts[0].timestamp
        last_time = alerts[-1].timestamp
        time_span = (last_time - first_time).total_seconds() / 60

        # 构建告警链
        alert_chain = [
            AlertChainItem(
                metric=alert.metric,
                severity=alert.severity,
                value=alert.value,
                message=alert.message,
            )
            for alert in alerts
        ]

        # 检查严重性升级
        has_escalation = any(a.severity == SeverityLevel.CRITICAL for a in alerts)

        # 推断根因（优化算法）
        metrics = {a.metric for a in alerts}
        root_cause = self._infer_root_cause(metrics)

        return Correlation(
            host=host,
            alert_chain=alert_chain,
            time_span_minutes=time_span,
            severity_escalation=has_escalation,
            potential_root_cause=root_cause,
            alerts=alerts,
        )

    def _infer_root_cause(self, metrics: set) -> str:
        """基于指标集推断根因"""
        metric_rules = {
            frozenset(
                {MetricType.CPU_USAGE.value, MetricType.HTTP_RESPONSE_TIME.value}
            ): "CPU 过载导致服务响应变慢",
            frozenset({MetricType.MYSQL_CONNECTION_POOL.value}): "数据库连接池问题",
            frozenset({MetricType.DISK_USAGE.value}): "磁盘空间不足",
            frozenset({MetricType.MEMORY_USAGE.value}): "内存压力问题",
        }

        for rule_metrics, cause in metric_rules.items():
            if rule_metrics & metrics:
                return cause

        return "资源竞争或配置问题"


class RootCauseAnalysisService(LoggerMixin):
    """根因分析服务"""

    def analyze(self, correlation: Correlation) -> RootCause:
        """分析根因"""
        metrics = correlation.metrics

        # 使用策略模式替代硬编码判断
        if MetricType.CPU_USAGE.value in metrics:
            return RootCause(
                primary="应用程序存在死循环或复杂计算逻辑",
                evidence=[
                    "CPU 使用率持续上升无波动",
                    "伴随内存压力",
                    "响应时间同步恶化",
                ],
                confidence=DEFAULT_CONFIDENCE_HIGH,
            )

        elif MetricType.MYSQL_CONNECTION_POOL.value in metrics:
            return RootCause(
                primary="慢查询导致连接占用时间过长",
                evidence=["连接池使用率快速攀升", "无明显流量高峰", "可能存在全表扫描"],
                confidence=DEFAULT_CONFIDENCE_MEDIUM,
            )

        elif MetricType.DISK_USAGE.value in metrics:
            return RootCause(
                primary="日志文件过大或磁盘空间规划不足",
                evidence=["磁盘使用率渐进式增长", "无突发性变化", "长期累积效应"],
                confidence=DEFAULT_CONFIDENCE_MEDIUM,
            )

        else:
            return RootCause(
                primary="资源规划不足或使用模式改变",
                evidence=["渐进式增长模式", "无突发性变化", "长期累积效应"],
                confidence=DEFAULT_CONFIDENCE_LOW,
            )


class ImpactAssessmentService(LoggerMixin):
    """影响评估服务"""

    def assess(self, correlation: Correlation) -> Impact:
        """评估影响"""
        metrics = correlation.metrics

        # 使用映射表替代条件判断
        impact_map = {
            MetricType.HTTP_RESPONSE_TIME.value: Impact(
                business="订单转化率可能下降 15-20%",
                users="约 30% 用户感受到明显卡顿",
                data="低风险 - 无数据一致性影响",
            ),
            MetricType.MYSQL_CONNECTION_POOL.value: Impact(
                business="高风险 - 可能导致交易失败",
                users="所有依赖数据库的功能不可用",
                data="中风险 - 需检查是否有部分提交",
            ),
            MetricType.DISK_USAGE.value: Impact(
                business="中等影响 - 非核心功能降级",
                users="内部运维效率降低",
                data="低风险 - 不影响核心数据",
            ),
        }

        for metric, impact in impact_map.items():
            if metric in metrics:
                return impact

        # 默认影响
        return Impact(business="待评估", users="待评估", data="低风险")


class ActionGenerationService(LoggerMixin):
    """处置动作生成服务"""

    def generate(self, correlation: Correlation) -> List[Action]:
        """生成处置动作"""
        metrics = correlation.metrics

        # CPU 相关动作
        if MetricType.CPU_USAGE.value in metrics:
            return self._cpu_actions()

        # 数据库相关动作
        elif MetricType.MYSQL_CONNECTION_POOL.value in metrics:
            return self._db_actions()

        # 磁盘相关动作
        elif MetricType.DISK_USAGE.value in metrics:
            return self._disk_actions()

        # 默认动作
        return self._default_actions()

    def _cpu_actions(self) -> List[Action]:
        return [
            Action(
                priority=PriorityLevel.P0,
                action="定位高负载进程",
                command="top -bn1 | head -20",
                expected_outcome="识别占用 CPU 最高的进程",
            ),
            Action(
                priority=PriorityLevel.P1,
                action="临时降低优先级",
                command="renice +10 -p <PID>",
                expected_outcome="缓解系统压力",
            ),
            Action(
                priority=PriorityLevel.P2,
                action="重启异常服务",
                command="systemctl restart <service>",
                expected_outcome="恢复正常状态",
            ),
        ]

    def _db_actions(self) -> List[Action]:
        return [
            Action(
                priority=PriorityLevel.P0,
                action="查看活跃连接",
                command='mysql -e "SHOW PROCESSLIST;"',
                expected_outcome="识别占用连接的会话",
            ),
            Action(
                priority=PriorityLevel.P1,
                action="终止慢查询",
                command='mysql -e "KILL <connection_id>"',
                expected_outcome="释放连接资源",
            ),
            Action(
                priority=PriorityLevel.P2,
                action="优化查询语句",
                command="EXPLAIN SELECT ...",
                expected_outcome="防止问题复发",
            ),
        ]

    def _disk_actions(self) -> List[Action]:
        return [
            Action(
                priority=PriorityLevel.P2,
                action="清理磁盘空间",
                command="journalctl --vacuum-time=7d",
                expected_outcome="释放至少 20GB 空间",
            )
        ]

    def _default_actions(self) -> List[Action]:
        return [
            Action(
                priority=PriorityLevel.P3,
                action="人工排查",
                command="echo '需要人工介入分析'",
                expected_outcome="定位问题根因",
            )
        ]


class RunbookMatchingService(LoggerMixin):
    """运维手册匹配服务"""

    def __init__(self, runbooks: Dict[str, Runbook]):
        self.runbooks = runbooks

    def match(self, correlation: Correlation) -> Optional[Runbook]:
        """匹配运维手册"""
        root_cause = correlation.potential_root_cause

        # 使用关键词匹配
        keywords = {
            "CPU": RunbookID.CPU_HIGH.value,
            "数据库": RunbookID.DB_CONNECTION.value,
            "连接池": RunbookID.DB_CONNECTION.value,
            "磁盘": RunbookID.DISK_FULL.value,
            "内存": RunbookID.MEMORY_LEAK.value,
        }

        for keyword, runbook_id in keywords.items():
            if keyword in root_cause and runbook_id in self.runbooks:
                return self.runbooks[runbook_id]

        return None


class DiagnosisOrchestrator(LoggerMixin):
    """诊断编排器 - 协调各个服务"""

    def __init__(
        self,
        correlation_service: Optional[AlertCorrelationService] = None,
        root_cause_service: Optional[RootCauseAnalysisService] = None,
        impact_service: Optional[ImpactAssessmentService] = None,
        action_service: Optional[ActionGenerationService] = None,
        runbook_service: Optional[RunbookMatchingService] = None,
    ):
        self.correlation_service = correlation_service or AlertCorrelationService()
        self.root_cause_service = root_cause_service or RootCauseAnalysisService()
        self.impact_service = impact_service or ImpactAssessmentService()
        self.action_service = action_service or ActionGenerationService()
        self.runbook_service = runbook_service

    def diagnose(self, alerts: List[Alert]) -> List[Diagnosis]:
        """执行完整诊断流程"""
        self.log_operation("DIAGNOSIS_START", alert_count=len(alerts))

        # 1. 关联分析
        correlations = self.correlation_service.analyze(alerts)

        # 2. 对每个关联组进行诊断
        diagnoses = []
        for correlation in correlations:
            diagnosis = self._diagnose_correlation(correlation)
            diagnoses.append(diagnosis)

        self.log_operation("DIAGNOSIS_COMPLETE", diagnosis_count=len(diagnoses))
        return diagnoses

    def _diagnose_correlation(self, correlation: Correlation) -> Diagnosis:
        """诊断单个关联组"""
        # 并行执行独立分析
        root_cause = self.root_cause_service.analyze(correlation)
        impact = self.impact_service.assess(correlation)
        actions = self.action_service.generate(correlation)

        # 匹配运维手册
        runbook = None
        if self.runbook_service:
            runbook = self.runbook_service.match(correlation)

        return Diagnosis(
            root_cause=root_cause, impact=impact, actions=actions, runbook=runbook
        )
