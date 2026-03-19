#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 插件架构模块
实现可扩展的插件系统
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from importlib import import_module
from pathlib import Path
import inspect
import json

from logger import LoggerMixin


class DiagnosticPlugin(ABC, LoggerMixin):
    """诊断插件基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass

    @property
    @abstractmethod
    def supported_metrics(self) -> List[str]:
        """支持的指标类型"""
        pass

    @abstractmethod
    def analyze(self, alerts: List[dict]) -> Optional[dict]:
        """
        分析告警并返回诊断结果

        Returns:
            诊断结果字典，如果不匹配则返回 None
        """
        pass

    @abstractmethod
    def get_actions(self, diagnosis: dict) -> List[dict]:
        """获取处置动作"""
        pass

    def validate(self) -> bool:
        """验证插件配置"""
        return True


class LLMProviderPlugin(ABC, LoggerMixin):
    """LLM 提供者插件基类"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供者名称"""
        pass

    @abstractmethod
    async def diagnose(self, prompt: str, context: dict) -> str:
        """
        调用 LLM 进行诊断

        Args:
            prompt: 诊断提示词
            context: 上下文信息

        Returns:
            LLM 生成的诊断结果
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass


class RuleBasedPlugin(DiagnosticPlugin):
    """基于规则的诊断插件"""

    def __init__(self, rules_file: Optional[Path] = None):
        self.rules_file = rules_file
        self.rules: List[dict] = []

        if rules_file and rules_file.exists():
            self._load_rules()

    def _load_rules(self):
        """加载规则文件"""
        with open(self.rules_file, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    @property
    def name(self) -> str:
        return "rule_based_diagnostic"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_metrics(self) -> List[str]:
        return list(set(rule.get("metric") for rule in self.rules if "metric" in rule))

    def analyze(self, alerts: List[dict]) -> Optional[dict]:
        """基于规则分析"""
        for rule in self.rules:
            if self._match_rule(rule, alerts):
                return {
                    "root_cause": rule.get("root_cause", "未知"),
                    "confidence": rule.get("confidence", 70),
                    "evidence": rule.get("evidence", []),
                    "matched_rule": rule.get("id", "unknown"),
                }
        return None

    def _match_rule(self, rule: dict, alerts: List[dict]) -> bool:
        """匹配规则"""
        conditions = rule.get("conditions", [])
        match_all = rule.get("match_all", True)

        results = []
        for condition in conditions:
            metric = condition.get("metric")
            threshold = condition.get("threshold")
            operator = condition.get("operator", ">=")

            for alert in alerts:
                if alert.get("metric") == metric:
                    value = alert.get("value", 0)
                    result = self._evaluate_condition(value, operator, threshold)
                    results.append(result)

        if match_all:
            return all(results) if results else False
        return any(results)

    def _evaluate_condition(
        self, value: float, operator: str, threshold: float
    ) -> bool:
        """评估条件"""
        operators = {
            ">": value > threshold,
            ">=": value >= threshold,
            "<": value < threshold,
            "<=": value <= threshold,
            "==": value == threshold,
            "!=": value != threshold,
        }
        return operators.get(operator, False)

    def get_actions(self, diagnosis: dict) -> List[dict]:
        """获取规则对应的动作"""
        rule_id = diagnosis.get("matched_rule")
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return rule.get("actions", [])
        return []


class MockLLMProvider(LLMProviderPlugin):
    """模拟 LLM 提供者（默认）"""

    @property
    def provider_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    async def diagnose(self, prompt: str, context: dict) -> str:
        """模拟诊断"""
        self.log_operation("MOCK_DIAGNOSE", prompt_length=len(prompt))

        # 基于上下文生成模拟结果
        metrics = context.get("metrics", [])

        if "node_cpu_usage" in metrics:
            return "应用程序存在死循环或复杂计算逻辑"
        elif "mysql_connection_pool" in metrics:
            return "慢查询导致连接占用时间过长"
        else:
            return "需要进一步分析"


class PluginManager(LoggerMixin):
    """插件管理器"""

    def __init__(self):
        self.diagnostic_plugins: Dict[str, DiagnosticPlugin] = {}
        self.llm_providers: Dict[str, LLMProviderPlugin] = {}
        self._default_llm: Optional[str] = None

    def register_diagnostic_plugin(self, plugin: DiagnosticPlugin) -> bool:
        """注册诊断插件"""
        if not plugin.validate():
            self.logger.warning(f"插件验证失败: {plugin.name}")
            return False

        self.diagnostic_plugins[plugin.name] = plugin
        self.log_operation("PLUGIN_REGISTER", name=plugin.name, version=plugin.version)
        return True

    def register_llm_provider(self, provider: LLMProviderPlugin, default: bool = False):
        """注册 LLM 提供者"""
        self.llm_providers[provider.provider_name] = provider

        if default or self._default_llm is None:
            self._default_llm = provider.provider_name

        self.log_operation(
            "LLM_REGISTER", provider=provider.provider_name, default=default
        )

    def load_plugins_from_directory(self, directory: Path) -> int:
        """从目录加载插件"""
        if not directory.exists():
            self.logger.warning(f"插件目录不存在: {directory}")
            return 0

        count = 0
        for file_path in directory.glob("*_plugin.py"):
            try:
                module = import_module(f"plugins.{file_path.stem}")
                self._register_from_module(module)
                count += 1
            except Exception as e:
                self.logger.error(f"加载插件失败: {file_path} - {e}")

        self.log_operation("PLUGINS_LOADED", dir=str(directory), count=count)
        return count

    def _register_from_module(self, module):
        """从模块注册插件"""
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, DiagnosticPlugin):
                if obj is not DiagnosticPlugin:
                    instance = obj()
                    self.register_diagnostic_plugin(instance)

            elif inspect.isclass(obj) and issubclass(obj, LLMProviderPlugin):
                if obj is not LLMProviderPlugin:
                    instance = obj()
                    self.register_llm_provider(instance)

    def get_diagnostic_plugin(self, name: str) -> Optional[DiagnosticPlugin]:
        """获取诊断插件"""
        return self.diagnostic_plugins.get(name)

    def get_llm_provider(
        self, name: Optional[str] = None
    ) -> Optional[LLMProviderPlugin]:
        """获取 LLM 提供者"""
        if name is None:
            name = self._default_llm
        return self.llm_providers.get(name)

    def list_plugins(self) -> Dict[str, List[str]]:
        """列出所有插件"""
        return {
            "diagnostic": list(self.diagnostic_plugins.keys()),
            "llm_providers": list(self.llm_providers.keys()),
            "default_llm": self._default_llm,
        }

    def find_plugin_for_metrics(self, metrics: List[str]) -> Optional[DiagnosticPlugin]:
        """根据指标查找合适的插件"""
        for plugin in self.diagnostic_plugins.values():
            supported = set(plugin.supported_metrics)
            if supported & set(metrics):
                return plugin
        return None
