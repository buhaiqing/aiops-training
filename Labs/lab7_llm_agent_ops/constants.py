#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 常量定义模块
集中管理所有配置常量和枚举值
"""

from enum import Enum
from pathlib import Path


class SeverityLevel(str, Enum):
    """告警严重级别枚举"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class MetricType(str, Enum):
    """指标类型枚举"""

    CPU_USAGE = "node_cpu_usage"
    MEMORY_USAGE = "node_memory_usage"
    HTTP_RESPONSE_TIME = "http_response_time"
    ERROR_RATE = "error_rate"
    DB_CONNECTION_POOL = "mysql_connection_pool_usage"
    DISK_USAGE = "disk_usage"


class PriorityLevel(str, Enum):
    """处置优先级枚举"""

    P0 = "P0 - 立即执行"
    P1 = "P1 - 5分钟内"
    P2 = "P2 - 30分钟内"
    P3 = "P3 - 今日完成"


class RunbookID(str, Enum):
    """运维手册ID枚举"""

    CPU_HIGH = "RB-CPU-HIGH"
    MEMORY_LEAK = "RB-MEMORY-LEAK"
    DISK_FULL = "RB-DISK-FULL"
    DB_CONNECTION = "RB-DB-CONNECTION"


# 路径常量
DEFAULT_ALERTS_FILE = Path("alert_data/alerts.json")
DEFAULT_SCENARIOS_FILE = Path("alert_data/scenarios.json")
DEFAULT_RUNBOOKS_DIR = Path("runbook_templates")
DEFAULT_OUTPUT_DIR = Path(".")

# 时间格式
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# 编码
DEFAULT_ENCODING = "utf-8"

# 告警阈值
CPU_WARNING_THRESHOLD = 80.0
CPU_CRITICAL_THRESHOLD = 95.0
MEMORY_WARNING_THRESHOLD = 85.0
DB_POOL_WARNING_THRESHOLD = 80.0
DB_POOL_CRITICAL_THRESHOLD = 90.0
DISK_WARNING_THRESHOLD = 90.0
DISK_CRITICAL_THRESHOLD = 95.0

# 图标映射
SEVERITY_ICONS = {
    SeverityLevel.CRITICAL: "🔴",
    SeverityLevel.WARNING: "🟡",
    SeverityLevel.INFO: "🟢",
}

SEVERITY_PRIORITY = {
    SeverityLevel.CRITICAL: 0,
    SeverityLevel.WARNING: 1,
    SeverityLevel.INFO: 2,
}

# 显示宽度
DISPLAY_WIDTH = 60
REPORT_PREVIEW_LINES = 50

# 告警源系统
ALERT_SOURCES = ["prometheus", "grafana", "elk", "zabbix"]

# 根因分析置信度
DEFAULT_CONFIDENCE_HIGH = 85
DEFAULT_CONFIDENCE_MEDIUM = 75
DEFAULT_CONFIDENCE_LOW = 60
