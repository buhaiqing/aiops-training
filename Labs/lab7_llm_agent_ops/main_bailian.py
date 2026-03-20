#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 使用阿里云百炼 LLM 进行智能诊断
基于真实的云厂商模型服务
"""

import sys
import asyncio
from datetime import datetime
from pathlib import Path

from constants import DISPLAY_WIDTH, DATETIME_FORMAT, FILE_TIMESTAMP_FORMAT
from types import Alert, Config, Runbook
from logger import setup_logger
from repositories import AlertLoader, RunbookLoader
from services import DiagnosisOrchestrator, RunbookMatchingService
from plugins import PluginManager
from plugins.aliyun_bailian_plugin import AliyunBailianProvider


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


class BailianLLMAgent:
    """使用阿里云百炼的 LLM 运维智能体"""

    def __init__(self, config: Config = None, api_key: str = None):
        self.config = config or Config.default()
        self.logger = setup_logger("bailian_llm_ops", level=self.config.log_level)
        
        # 数据加载器
        self.alert_loader = AlertLoader(cache_enabled=self.config.enable_cache)
        self.runbook_loader = RunbookLoader(cache_enabled=self.config.enable_cache)
        
        # 初始化阿里云百炼 Provider
        self.bailian_provider = AliyunBailianProvider(api_key=api_key)
        
        # 插件管理器
        self.plugin_manager = PluginManager()
        
        # 如果百炼可用，注册为默认 LLM Provider
        if self.bailian_provider.is_available():
            self.plugin_manager.register_llm_provider(self.bailian_provider, default=True)
            self.logger.info("已注册阿里云百炼为默认 LLM Provider")
        else:
            self.logger.warning("阿里云百炼不可用，将使用模拟模式")
        
        self.runbooks = {}
        self.alerts = []

    def initialize(self):
        """初始化系统"""
        print_header("Lab 7: LLM Agent 自主运维实战 - 阿里云百炼版")
        print(f"开始时间：{datetime.now().strftime(DATETIME_FORMAT)}")
        print()
        
        self.logger.info("系统初始化", config=self.config.__dict__)
        
        # 显示模型信息
        if self.bailian_provider.is_available():
            model_info = self.bailian_provider.get_model_info()
            print("✓ LLM 配置:")
            print(f"  - 服务商：阿里云百炼")
            print(f"  - 模型：{model_info['model']}")
            print(f"  - API Key: {'已配置 ✓' : '未配置 ✗'}")
            print(f"  - 状态：{'可用 ✓' : '不可用 ✗'}")
        else:
            print("⚠️  阿里云百炼未配置，将使用模拟模式")
            print("   请设置环境变量 DASHSCOPE_API_KEY 或传入 api_key 参数")
        print()
        
        # 加载运维手册
        self._load_runbooks()
        
        self.logger.info("系统初始化完成")

    def _load_runbooks(self):
        """加载运维手册"""
        print_section("加载运维手册库")
        
        if not self.config.runbooks_dir.exists():
            self.logger.warning(f"运维手册目录不存在：{self.config.runbooks_dir}")
            return
        
        try:
            raw_runbooks = self.runbook_loader.load_directory(self.config.runbooks_dir)
            
            # 转换为 Runbook 对象
            self.runbooks = {
                runbook_id: Runbook.from_dict(data)
                for runbook_id, data in raw_runbooks.items()
            }
            
            self.logger.info(f"已加载 {len(self.runbooks)} 个运维手册")
            print(f"✓ 已加载 {len(self.runbooks)} 个运维手册")
            
        except Exception as e:
            self.logger.error(f"加载运维手册失败：{e}")

    def load_alerts(self) -> bool:
        """加载告警数据"""
        print_section("加载告警数据")
        
        if not self.config.alerts_file.exists():
            print(f"❌ 告警文件不存在：{self.config.alerts_file}")
            print("\n请先运行：python3 generate_data.py")
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
            
        except Exception as e:
            print(f"❌ 告警加载失败：{e}")
            return False

    async def analyze_with_llm(self) -> str:
        """使用 LLM 执行智能诊断"""
        if not self.alerts:
            print("❌ 没有告警数据可供分析")
            return ""
        
        print_section("执行智能诊断")
        
        # 获取 LLM Provider
        llm_provider = self.plugin_manager.get_llm_provider()
        
        if not llm_provider:
            print("⚠️  无可用 LLM Provider，使用规则引擎分析")
            return self._analyze_with_rules()
        
        print(f"✓ 使用 LLM: {llm_provider.provider_name}")
        
        # 构建诊断提示词
        prompt = self._build_diagnosis_prompt()
        
        # 准备上下文
        context = {
            "alert_count": len(self.alerts),
            "metrics": list(set(a.metric for a in self.alerts)),
            "hosts": list(set(a.host for a in self.alerts)),
            "severities": list(set(a.severity for a in self.alerts))
        }
        
        try:
            # 异步调用 LLM
            diagnosis_result = await llm_provider.diagnose(prompt, context)
            
            print(f"✓ LLM 诊断完成")
            print(f"✓ 响应长度：{len(diagnosis_result)} 字符")
            
            return diagnosis_result
            
        except Exception as e:
            print(f"❌ LLM 调用失败：{e}")
            print("⚠️  降级到规则引擎分析")
            return self._analyze_with_rules()

    def _build_diagnosis_prompt(self) -> str:
        """构建诊断提示词"""
        # 按主机分组告警
        alerts_by_host = {}
        for alert in self.alerts:
            host = alert.host
            if host not in alerts_by_host:
                alerts_by_host[host] = []
            alerts_by_host[host].append(alert)
        
        # 构建详细的告警描述
        alert_descriptions = []
        for host, host_alerts in sorted(alerts_by_host.items()):
            host_alerts.sort(key=lambda x: x.timestamp)
            alert_descriptions.append(f"\n【主机：{host}】")
            alert_descriptions.append(f"告警数量：{len(host_alerts)}")
            
            for i, alert in enumerate(host_alerts, 1):
                alert_descriptions.append(
                    f"  {i}. [{alert.severity}] {alert.metric} = {alert.value}\n"
                    f"     时间：{alert.timestamp}\n"
                    f"     描述：{alert.message}"
                )
        
        alert_text = "\n".join(alert_descriptions)
        
        # 构建完整的提示词
        prompt = f"""你是一位经验丰富的运维专家。请根据以下监控告警数据进行分析诊断。

## 告警数据概览
- 总告警数：{len(self.alerts)}
- 涉及主机：{len(alerts_by_host)} 台
- 告警指标：{', '.join(set(a.metric for a in self.alerts))}

## 详细告警列表
{alert_text}

## 任务要求
请完成以下分析：
1. **关联分析**：识别同一主机上的告警之间的因果关系
2. **根因推断**：分析最可能的根本原因
3. **影响评估**：评估对业务和用户的影响
4. **处置建议**：提供具体的处理步骤和命令
5. **优先级排序**：按照紧急程度排序

## 输出格式
请按照以下结构输出诊断报告：
```
# 智能诊断报告

## 一、整体态势评估
[描述整体严重程度和影响范围]

## 二、事件分析
### 事件 1: [主机名] - [问题描述]
- **时间线**: [按时间顺序描述告警]
- **根因分析**: [分析根本原因]
- **影响评估**: [业务和用户影响]
- **处置建议**: 
  1. [P0] [具体操作和命令]
  2. [P1] [具体操作和命令]
  3. [P2] [具体操作和命令]

## 三、总结与建议
[总体建议和人员调度方案]
```

请开始你的专业分析："""
        
        return prompt

    def _analyze_with_rules(self) -> str:
        """使用规则引擎分析（降级方案）"""
        from main_optimized import OptimizedLLMAgent
        
        agent = OptimizedLLMAgent(self.config)
        agent.alerts = self.alerts
        diagnoses = agent.analyze()
        
        if diagnoses:
            from report_generator import ReportRenderer
            renderer = ReportRenderer()
            return renderer.render(self.alerts, diagnoses)
        
        return "无法生成诊断报告"

    def save_report(self, report: str) -> str:
        """保存诊断报告"""
        timestamp = datetime.now().strftime(FILE_TIMESTAMP_FORMAT)
        report_file = self.config.output_dir / f"bailian_diagnosis_{timestamp}.md"
        
        report_file.write_text(report, encoding="utf-8")
        
        self.logger.info(f"报告已保存：{report_file}")
        return str(report_file)

    async def run(self):
        """运行完整流程"""
        self.initialize()
        
        # 加载数据
        if not self.load_alerts():
            return 1
        
        # 执行 LLM 诊断
        diagnosis_report = await self.analyze_with_llm()
        
        if not diagnosis_report:
            return 1
        
        # 保存报告
        report_file = self.save_report(diagnosis_report)
        
        # 显示结果
        print_section("诊断完成")
        print(f"✅ 详细报告已保存：{report_file}")
        
        print_section("报告预览（前 30 行）")
        preview_lines = diagnosis_report.split("\n")[:30]
        print("\n".join(preview_lines))
        print("...")
        
        print(f"\n完整报告共 {len(diagnosis_report.split(chr(10)))} 行")
        
        return 0


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 7: LLM Agent 自主运维实战 - 阿里云百炼集成")
    print("=" * 60)
    print()
    
    # 检查 API Key
    api_key = input("请输入阿里云百炼 API Key (直接回车使用环境变量): ").strip()
    
    if not api_key:
        api_key = None
    
    try:
        # 创建配置
        config = Config.default()
        
        # 创建并运行智能体
        agent = BailianLLMAgent(config, api_key=api_key)
        
        # 运行异步主函数
        return asyncio.run(agent.run())
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 系统错误：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
