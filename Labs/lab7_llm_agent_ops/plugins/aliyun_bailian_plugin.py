#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼 LLM Provider 插件
使用阿里云百炼平台提供的通义千问模型进行智能诊断
"""

import asyncio
from typing import Optional
import os

from logger import LoggerMixin
from plugins import LLMProviderPlugin


class AliyunBailianProvider(LLMProviderPlugin):
    """阿里云百炼 LLM 提供者"""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen-max"):
        """
        初始化阿里云百炼 LLM 提供者

        Args:
            api_key: 阿里云百炼 API Key，如不提供则从环境变量 DASHSCOPE_API_KEY 读取
            model: 模型名称，默认使用 qwen-max
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model
        self.client = None
        
        if not self.api_key:
            self.logger.warning(
                "未配置阿里云百炼 API Key",
                hint="请设置环境变量 DASHSCOPE_API_KEY 或在构造函数中传入"
            )
        
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        try:
            from dashscope import Generation
            self.client = Generation
            self.logger.info(f"阿里云百炼客户端初始化成功，模型：{self.model}")
        except ImportError as e:
            self.logger.error(
                "缺少 dashscope 依赖",
                error=str(e),
                hint="请运行：pip install dashscope"
            )
            self.client = None

    @property
    def provider_name(self) -> str:
        return "aliyun-bailian"

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.client is not None and self.api_key is not None

    async def diagnose(self, prompt: str, context: dict) -> str:
        """
        调用阿里云百炼 LLM 进行诊断

        Args:
            prompt: 诊断提示词
            context: 上下文信息

        Returns:
            LLM 生成的诊断结果
        """
        if not self.is_available():
            raise RuntimeError("阿里云百炼服务不可用，请检查 API Key 配置")

        self.log_operation(
            "BAILIAN_DIAGNOSE",
            model=self.model,
            prompt_length=len(prompt),
            context_keys=list(context.keys())
        )

        try:
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的运维专家，擅长分析系统告警并提供专业的故障诊断建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # 异步调用阿里云百炼 API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.call(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048
                )
            )

            # 解析响应
            if response and hasattr(response, 'output') and hasattr(response.output, 'text'):
                result = response.output.text
                self.logger.info(
                    "诊断完成",
                    model=self.model,
                    response_length=len(result)
                )
                return result
            else:
                self.logger.warning("响应格式异常", response_type=type(response))
                return "抱歉，诊断服务暂时不可用。"

        except Exception as e:
            self.logger.error(
                "诊断调用失败",
                error=str(e),
                model=self.model
            )
            raise RuntimeError(f"阿里云百炼调用失败：{str(e)}")

    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "api_key_configured": self.api_key is not None,
            "available": self.is_available()
        }
