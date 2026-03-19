#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 日志配置模块
提供结构化日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "llm_agent_ops",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    配置结构化日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        console_output: 是否输出到控制台

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除现有处理器
    logger.handlers.clear()

    # 创建格式化器
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # 文件记录 DEBUG 及以上级别
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LoggerMixin:
    """为类提供日志功能的 Mixin"""

    _logger: Optional[logging.Logger] = None

    @property
    def logger(self) -> logging.Logger:
        """获取日志记录器"""
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    def log_operation(self, operation: str, **kwargs):
        """记录操作日志"""
        extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.info(f"[{operation}] {extra_info}")

    def log_error(self, error: Exception, context: str = ""):
        """记录错误日志"""
        self.logger.error(f"[{context}] Error: {error}", exc_info=True)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)


# 预定义的日志记录器
agent_logger = get_logger("llm_agent")
data_logger = get_logger("data_loader")
analysis_logger = get_logger("analysis")
report_logger = get_logger("report")
