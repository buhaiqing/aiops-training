#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 规则引擎模块
实现可配置的规则匹配系统
"""

import json
import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

from logger import LoggerMixin


class Operator(Enum):
    """规则操作符"""

    EQ = auto()  # ==
    NE = auto()  # !=
    GT = auto()  # >
    GE = auto()  # >=
    LT = auto()  # <
    LE = auto()  # <=
    CONTAINS = auto()  # in
    MATCHES = auto()  # regex
    EXISTS = auto()  # key exists


class LogicalOp(Enum):
    """逻辑操作符"""

    AND = auto()
    OR = auto()
    NOT = auto()


@dataclass
class Condition:
    """规则条件"""

    field: str
    operator: Operator
    value: Any = None

    def evaluate(self, data: dict) -> bool:
        """评估条件"""
        actual_value = self._get_nested_value(data, self.field)

        if self.operator == Operator.EXISTS:
            return actual_value is not None

        if actual_value is None:
            return False

        evaluators = {
            Operator.EQ: lambda a, b: a == b,
            Operator.NE: lambda a, b: a != b,
            Operator.GT: lambda a, b: a > b,
            Operator.GE: lambda a, b: a >= b,
            Operator.LT: lambda a, b: a < b,
            Operator.LE: lambda a, b: a <= b,
            Operator.CONTAINS: lambda a, b: b in str(a),
            Operator.MATCHES: lambda a, b: bool(re.search(b, str(a))),
        }

        evaluator = evaluators.get(self.operator)
        if evaluator:
            return evaluator(actual_value, self.value)

        return False

    def _get_nested_value(self, data: dict, field: str) -> Any:
        """获取嵌套字段值"""
        keys = field.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value


@dataclass
class Rule:
    """规则定义"""

    rule_id: str
    name: str
    description: str
    priority: int = 100
    conditions: List[Condition] = field(default_factory=list)
    logical_op: LogicalOp = LogicalOp.AND
    actions: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def matches(self, data: dict) -> bool:
        """检查数据是否匹配规则"""
        if not self.conditions:
            return True

        results = [cond.evaluate(data) for cond in self.conditions]

        if self.logical_op == LogicalOp.AND:
            return all(results)
        elif self.logical_op == LogicalOp.OR:
            return any(results)
        elif self.logical_op == LogicalOp.NOT:
            return not any(results)

        return False


class RuleEngine(LoggerMixin):
    """规则引擎"""

    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.action_handlers: Dict[str, Callable] = {}

    def register_action_handler(self, action_type: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action_type] = handler
        self.logger.debug(f"注册动作处理器: {action_type}")

    def load_rules(self, rules_file: Path) -> int:
        """从文件加载规则"""
        if not rules_file.exists():
            self.logger.warning(f"规则文件不存在: {rules_file}")
            return 0

        with open(rules_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for rule_data in data.get("rules", []):
            rule = self._parse_rule(rule_data)
            if rule:
                self.rules[rule.rule_id] = rule
                count += 1

        self.log_operation("RULES_LOADED", file=str(rules_file), count=count)
        return count

    def _parse_rule(self, data: dict) -> Optional[Rule]:
        """解析规则"""
        try:
            conditions = [
                Condition(
                    field=cond.get("field", ""),
                    operator=Operator[cond.get("operator", "EQ").upper()],
                    value=cond.get("value"),
                )
                for cond in data.get("conditions", [])
            ]

            return Rule(
                rule_id=data["id"],
                name=data["name"],
                description=data.get("description", ""),
                priority=data.get("priority", 100),
                conditions=conditions,
                logical_op=LogicalOp[data.get("logical_op", "AND").upper()],
                actions=data.get("actions", []),
                metadata=data.get("metadata", {}),
            )
        except Exception as e:
            self.logger.error(f"解析规则失败: {e}")
            return None

    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
        self.logger.debug(f"添加规则: {rule.rule_id}")

    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.debug(f"移除规则: {rule_id}")
            return True
        return False

    def evaluate(self, data: dict) -> List[Rule]:
        """评估所有规则"""
        matched = [rule for rule in self.rules.values() if rule.matches(data)]

        # 按优先级排序
        matched.sort(key=lambda r: r.priority)

        return matched

    def execute_actions(self, rule: Rule, context: dict) -> List[Dict]:
        """执行规则动作"""
        results = []

        for action in rule.actions:
            action_type = action.get("type")
            handler = self.action_handlers.get(action_type)

            if handler:
                try:
                    result = handler(action, context)
                    results.append(
                        {"action": action, "result": result, "success": True}
                    )
                except Exception as e:
                    results.append(
                        {"action": action, "error": str(e), "success": False}
                    )
            else:
                results.append(
                    {
                        "action": action,
                        "error": f"未找到处理器: {action_type}",
                        "success": False,
                    }
                )

        return results


class DiagnosticRuleEngine(RuleEngine):
    """诊断专用规则引擎"""

    def __init__(self):
        super().__init__()
        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认动作处理器"""
        self.register_action_handler("generate_diagnosis", self._handle_diagnosis)
        self.register_action_handler("suggest_runbook", self._handle_runbook)
        self.register_action_handler("escalate", self._handle_escalation)

    def _handle_diagnosis(self, action: dict, context: dict) -> dict:
        """处理诊断动作"""
        return {
            "root_cause": action.get("root_cause", "未知"),
            "confidence": action.get("confidence", 70),
            "evidence": action.get("evidence", []),
        }

    def _handle_runbook(self, action: dict, context: dict) -> dict:
        """处理运维手册动作"""
        return {
            "runbook_id": action.get("runbook_id"),
            "title": action.get("title"),
            "steps": action.get("steps", []),
        }

    def _handle_escalation(self, action: dict, context: dict) -> dict:
        """处理升级动作"""
        return {
            "level": action.get("level", "L2"),
            "team": action.get("team", "ops"),
            "message": action.get("message", ""),
        }

    def diagnose(self, alerts: List[dict]) -> List[dict]:
        """基于规则进行诊断"""
        # 构建诊断上下文
        context = {
            "alerts": alerts,
            "alert_count": len(alerts),
            "metrics": list(set(a.get("metric", "") for a in alerts)),
            "hosts": list(set(a.get("host", "") for a in alerts)),
            "severities": list(set(a.get("severity", "") for a in alerts)),
        }

        # 评估规则
        matched_rules = self.evaluate(context)

        # 执行动作
        diagnoses = []
        for rule in matched_rules:
            results = self.execute_actions(rule, context)
            diagnoses.append(
                {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "priority": rule.priority,
                    "results": results,
                }
            )

        return diagnoses


def create_default_rules() -> List[dict]:
    """创建默认规则集"""
    return [
        {
            "id": "RULE-CPU-HIGH",
            "name": "CPU过载诊断",
            "description": "检测CPU使用率过高导致的性能问题",
            "priority": 10,
            "conditions": [
                {"field": "metrics", "operator": "contains", "value": "node_cpu_usage"},
                {"field": "alert_count", "operator": "ge", "value": 3},
            ],
            "logical_op": "AND",
            "actions": [
                {
                    "type": "generate_diagnosis",
                    "root_cause": "应用程序存在死循环或复杂计算逻辑",
                    "confidence": 85,
                    "evidence": ["CPU使用率持续上升", "响应时间同步恶化"],
                },
                {
                    "type": "suggest_runbook",
                    "runbook_id": "RB-CPU-HIGH",
                    "title": "CPU使用率过高处理流程",
                },
            ],
        },
        {
            "id": "RULE-DB-CONNECTION",
            "name": "数据库连接池问题",
            "description": "检测数据库连接池耗尽问题",
            "priority": 5,
            "conditions": [
                {
                    "field": "metrics",
                    "operator": "contains",
                    "value": "mysql_connection_pool",
                }
            ],
            "actions": [
                {
                    "type": "generate_diagnosis",
                    "root_cause": "慢查询导致连接占用时间过长",
                    "confidence": 78,
                    "evidence": ["连接池使用率快速攀升"],
                },
                {
                    "type": "suggest_runbook",
                    "runbook_id": "RB-DB-CONNECTION",
                    "title": "数据库连接池耗尽处理",
                },
                {
                    "type": "escalate",
                    "level": "L2",
                    "team": "dba",
                    "message": "数据库连接池问题需要DBA介入",
                },
            ],
        },
    ]
