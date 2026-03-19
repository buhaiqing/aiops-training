#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 测试套件
单元测试和集成测试
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from constants import SeverityLevel, PriorityLevel, MetricType
from types import Alert, Correlation, AlertChainItem, RootCause, Impact, Action, Config
from services import AlertCorrelationService, RootCauseAnalysisService
from repositories import AlertLoader, RunbookLoader
from performance import AsyncCache, OptimizedAlgorithms
from rule_engine import Condition, Operator, Rule, RuleEngine


class TestAlertTypes:
    """测试告警类型"""

    def test_alert_creation(self):
        """测试告警创建"""
        alert = Alert(
            alert_id="TEST-001",
            timestamp=datetime.now(),
            source="prometheus",
            metric="cpu_usage",
            severity=SeverityLevel.CRITICAL,
            value=95.5,
            threshold=80.0,
            host="test-server",
            message="CPU high",
        )

        assert alert.alert_id == "TEST-001"
        assert alert.value == 95.5
        assert alert.severity == SeverityLevel.CRITICAL

    def test_alert_from_dict(self):
        """测试从字典创建告警"""
        data = {
            "alert_id": "TEST-002",
            "timestamp": "2026-03-20T10:00:00",
            "source": "grafana",
            "metric": "memory_usage",
            "severity": "warning",
            "value": 85.0,
            "threshold": 80.0,
            "host": "test-host",
            "message": "Memory high",
            "labels": {"env": "test"},
        }

        alert = Alert.from_dict(data)
        assert alert.alert_id == "TEST-002"
        assert alert.severity == SeverityLevel.WARNING
        assert alert.labels["env"] == "test"


class TestAlertCorrelationService:
    """测试告警关联服务"""

    @pytest.fixture
    def service(self):
        return AlertCorrelationService()

    @pytest.fixture
    def sample_alerts(self):
        base_time = datetime.now()
        return [
            Alert(
                alert_id="ALT-001",
                timestamp=base_time,
                source="prometheus",
                metric="node_cpu_usage",
                severity=SeverityLevel.WARNING,
                value=85.0,
                threshold=80.0,
                host="server-01",
                message="CPU high",
            ),
            Alert(
                alert_id="ALT-002",
                timestamp=base_time + timedelta(minutes=5),
                source="grafana",
                metric="http_response_time",
                severity=SeverityLevel.CRITICAL,
                value=5.0,
                threshold=2.0,
                host="server-01",
                message="Response slow",
            ),
            Alert(
                alert_id="ALT-003",
                timestamp=base_time,
                source="prometheus",
                metric="node_cpu_usage",
                severity=SeverityLevel.WARNING,
                value=90.0,
                threshold=80.0,
                host="server-02",
                message="CPU high",
            ),
        ]

    def test_analyze_creates_correlations(self, service, sample_alerts):
        """测试关联分析创建关联组"""
        correlations = service.analyze(sample_alerts)

        assert len(correlations) == 1  # server-01 有多个告警
        assert correlations[0].host == "server-01"
        assert len(correlations[0].alert_chain) == 2

    def test_root_cause_inference(self, service):
        """测试根因推断"""
        metrics = {"node_cpu_usage", "http_response_time"}
        root_cause = service._infer_root_cause(metrics)

        assert "CPU" in root_cause
        assert "服务响应" in root_cause


class TestRootCauseAnalysisService:
    """测试根因分析服务"""

    @pytest.fixture
    def service(self):
        return RootCauseAnalysisService()

    @pytest.fixture
    def cpu_correlation(self):
        return Correlation(
            host="server-01",
            alert_chain=[
                AlertChainItem(
                    metric="node_cpu_usage",
                    severity=SeverityLevel.CRITICAL,
                    value=95.0,
                    message="CPU high",
                )
            ],
            time_span_minutes=10.0,
            severity_escalation=True,
            potential_root_cause="CPU issue",
            alerts=[],
        )

    def test_analyze_cpu_issue(self, service, cpu_correlation):
        """测试 CPU 问题分析"""
        root_cause = service.analyze(cpu_correlation)

        assert "死循环" in root_cause.primary or "复杂计算" in root_cause.primary
        assert root_cause.confidence >= 80
        assert len(root_cause.evidence) > 0


class TestRepositories:
    """测试数据存储层"""

    def test_alert_loader(self):
        """测试告警加载器"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                [
                    {"alert_id": "1", "message": "test"},
                    {"alert_id": "2", "message": "test2"},
                ],
                f,
            )
            temp_path = Path(f.name)

        try:
            loader = AlertLoader()
            result = loader.load(temp_path)

            assert len(result) == 2
            assert result[0]["alert_id"] == "1"
        finally:
            temp_path.unlink()

    def test_alert_loader_cache(self):
        """测试加载器缓存"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"id": "1"}], f)
            temp_path = Path(f.name)

        try:
            loader = AlertLoader(cache_enabled=True)

            # 第一次加载
            result1 = loader.load(temp_path)

            # 第二次加载（应该命中缓存）
            result2 = loader.load(temp_path)

            assert result1 == result2
        finally:
            temp_path.unlink()


class TestPerformance:
    """测试性能优化"""

    @pytest.mark.asyncio
    async def test_async_cache(self):
        """测试异步缓存"""
        cache = AsyncCache(ttl=60)

        # 设置缓存
        await cache.set("key1", "value1")

        # 获取缓存
        result = await cache.get("key1")
        assert result == "value1"

        # 获取不存在的键
        result = await cache.get("key2")
        assert result is None

    def test_group_by_algorithm(self):
        """测试分组算法"""
        alerts = [
            {"host": "h1", "metric": "cpu"},
            {"host": "h2", "metric": "mem"},
            {"host": "h1", "metric": "disk"},
        ]

        groups = OptimizedAlgorithms.group_by(alerts, lambda x: x["host"])

        assert len(groups) == 2
        assert len(groups["h1"]) == 2
        assert len(groups["h2"]) == 1

    def test_find_chains(self):
        """测试链式检测算法"""

        class MockAlert:
            def __init__(self, ts):
                self.timestamp = ts

        now = datetime.now()
        alerts = [
            MockAlert(now),
            MockAlert(now + timedelta(seconds=30)),
            MockAlert(now + timedelta(seconds=60)),
            MockAlert(now + timedelta(minutes=10)),  # 断开
        ]

        chains = OptimizedAlgorithms.find_chains(alerts, time_threshold=300)

        assert len(chains) == 1  # 第一个链有3个告警
        assert len(chains[0]) == 3


class TestRuleEngine:
    """测试规则引擎"""

    @pytest.fixture
    def engine(self):
        return RuleEngine()

    def test_condition_evaluation(self):
        """测试条件评估"""
        condition = Condition(field="value", operator=Operator.GT, value=80)

        assert condition.evaluate({"value": 90}) is True
        assert condition.evaluate({"value": 70}) is False

    def test_rule_matching(self):
        """测试规则匹配"""
        rule = Rule(
            rule_id="TEST-001",
            name="Test Rule",
            description="A test rule",
            priority=10,
            conditions=[
                Condition("severity", Operator.EQ, "critical"),
                Condition("value", Operator.GE, 90),
            ],
            logical_op="AND",
            actions=[{"type": "alert"}],
        )

        # 匹配的数据
        data_match = {"severity": "critical", "value": 95}
        assert rule.matches(data_match) is True

        # 不匹配的数据
        data_no_match = {"severity": "warning", "value": 95}
        assert rule.matches(data_no_match) is False

    def test_engine_evaluate(self, engine):
        """测试引擎评估"""
        rule = Rule(
            rule_id="TEST-002",
            name="Test Rule 2",
            description="Another test rule",
            priority=5,
            conditions=[Condition("type", Operator.EQ, "cpu")],
            actions=[],
        )

        engine.add_rule(rule)

        matched = engine.evaluate({"type": "cpu"})
        assert len(matched) == 1
        assert matched[0].rule_id == "TEST-002"

        matched = engine.evaluate({"type": "memory"})
        assert len(matched) == 0


class TestIntegration:
    """集成测试"""

    def test_full_diagnosis_flow(self):
        """测试完整诊断流程"""
        from services import DiagnosisOrchestrator

        # 创建测试数据
        alerts = [
            Alert(
                alert_id="ALT-001",
                timestamp=datetime.now(),
                source="prometheus",
                metric="node_cpu_usage",
                severity=SeverityLevel.CRITICAL,
                value=95.0,
                threshold=80.0,
                host="server-01",
                message="CPU critical",
            ),
            Alert(
                alert_id="ALT-002",
                timestamp=datetime.now() + timedelta(minutes=5),
                source="grafana",
                metric="http_response_time",
                severity=SeverityLevel.WARNING,
                value=3.0,
                threshold=2.0,
                host="server-01",
                message="Response slow",
            ),
        ]

        # 执行诊断
        orchestrator = DiagnosisOrchestrator()
        diagnoses = orchestrator.diagnose(alerts)

        assert len(diagnoses) == 1
        assert diagnoses[0].root_cause.confidence > 0
        assert len(diagnoses[0].actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
