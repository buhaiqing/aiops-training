#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 优化后的主入口
整合所有优化模块的新版本
"""

import sys
from datetime import datetime
from pathlib import Path

from constants import DISPLAY_WIDTH, DATETIME_FORMAT, FILE_TIMESTAMP_FORMAT
from types import Alert, Config, AlertLoadError, RunbookLoadError
from logger import setup_logger
from repositories import AlertLoader, RunbookLoader
from services import DiagnosisOrchestrator, RunbookMatchingService
from plugins import PluginManager, MockLLMProvider
from rule_engine import DiagnosticRuleEngine, create_default_rules
import json


def print_header(text: str, width: int = DISPLAY_WIDTH):
    """打印格式化标题"""
    print("=" * width)
    print(text)
    print("=" * width)


def print_section(text: str, width: int = DISPLAY_WIDTH):
    """打印分隔线"""
    print(f"\n{'=' * width}")
    print(text)
    print("=" * width)


class OptimizedLLMAgent:
    """优化后的 LLM 运维智能体"""

    def __init__(self, config: Config = None):
        self.config = config or Config.default()
        self.logger = setup_logger("llm_agent_ops", level=self.config.log_level)

        # 数据加载器
        self.alert_loader = AlertLoader(cache_enabled=self.config.enable_cache)
        self.runbook_loader = RunbookLoader(cache_enabled=self.config.enable_cache)

        # 插件管理器
        self.plugin_manager = PluginManager()
        self.plugin_manager.register_llm_provider(MockLLMProvider(), default=True)

        # 规则引擎
        self.rule_engine = DiagnosticRuleEngine()

        # 服务层
        self.orchestrator: DiagnosisOrchestrator = None

        self.alerts = []
        self.runbooks = {}

    def initialize(self):
        """初始化系统"""
        print_header("Lab 7: LLM Agent 自主运维实战 - 优化版")
        print(f"开始时间：{datetime.now().strftime(DATETIME_FORMAT)}")
        print()

        self.logger.info("系统初始化", config=self.config.__dict__)

        # 加载运维手册
        self._load_runbooks()

        # 初始化诊断编排器
        if self.runbooks:
            runbook_service = RunbookMatchingService(self.runbooks)
            self.orchestrator = DiagnosisOrchestrator(runbook_service=runbook_service)
        else:
            self.orchestrator = DiagnosisOrchestrator()

        # 加载默认规则
        default_rules = create_default_rules()
        for rule_data in default_rules:
            # 这里简化处理，实际应该通过 rule_engine 加载
            pass

        self.logger.info("系统初始化完成")

    def _load_runbooks(self):
        """加载运维手册"""
        print_section("加载运维手册库")

        if not self.config.runbooks_dir.exists():
            self.logger.warning(f"运维手册目录不存在: {self.config.runbooks_dir}")
            return

        try:
            raw_runbooks = self.runbook_loader.load_directory(self.config.runbooks_dir)

            # 转换为 Runbook 对象
            from types import Runbook

            self.runbooks = {
                runbook_id: Runbook.from_dict(data)
                for runbook_id, data in raw_runbooks.items()
            }

            self.logger.info(f"已加载 {len(self.runbooks)} 个运维手册")

        except Exception as e:
            self.logger.error(f"加载运维手册失败: {e}")

    def load_alerts(self) -> bool:
        """加载告警数据"""
        print_section("加载告警数据")

        if not self.config.alerts_file.exists():
            print(f"❌ 告警文件不存在: {self.config.alerts_file}")
            print("\n请先运行: python3 generate_data.py")
            return False

        try:
            raw_alerts = self.alert_loader.load(self.config.alerts_file)

            # 转换为 Alert 对象
            self.alerts = [Alert.from_dict(data) for data in raw_alerts]

            hosts = len(set(a.host for a in self.alerts))
            self.logger.info(
                "告警加载完成",
                count=len(self.alerts),
                hosts=hosts,
                time_range=f"{self.alerts[0].timestamp} 至 {self.alerts[-1].timestamp}",
            )

            print(f"✓ 成功加载 {len(self.alerts)} 条告警")
            print(f"✓ 涉及主机：{hosts} 台")

            return True

        except AlertLoadError as e:
            print(f"❌ 告警加载失败: {e}")
            return False

    def analyze(self):
        """执行分析"""
        if not self.alerts:
            print("❌ 没有告警数据可供分析")
            return None

        print_section("执行智能诊断")

        # 执行诊断编排
        diagnoses = self.orchestrator.diagnose(self.alerts)

        print(f"✓ 完成 {len(diagnoses)} 个事件组的诊断")

        return diagnoses

    def generate_report(self, diagnoses: list) -> str:
        """生成诊断报告"""
        from report_generator import ReportRenderer

        renderer = ReportRenderer()
        report = renderer.render(self.alerts, diagnoses)

        # 保存报告
        timestamp = datetime.now().strftime(FILE_TIMESTAMP_FORMAT)
        report_file = self.config.output_dir / f"llm_diagnosis_optimized_{timestamp}.md"

        report_file.write_text(report, encoding="utf-8")

        self.logger.info(f"报告已保存: {report_file}")

        return report, report_file

    def run(self):
        """运行完整流程"""
        self.initialize()

        # 加载数据
        if not self.load_alerts():
            return 1

        # 执行分析
        diagnoses = self.analyze()
        if diagnoses is None:
            return 1

        # 生成报告
        report, report_file = self.generate_report(diagnoses)

        # 显示结果
        print_section("诊断完成")
        print(f"✅ 详细报告已保存: {report_file}")

        print_section("报告预览（前 30 行）")
        preview_lines = report.split("\n")[:30]
        print("\n".join(preview_lines))
        print("...")

        print(f"\n完整报告共 {len(report.split(chr(10)))} 行")

        return 0


def main():
    """主函数"""
    try:
        # 创建配置
        config = Config.default()

        # 创建并运行智能体
        agent = OptimizedLLMAgent(config)
        return agent.run()

    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
