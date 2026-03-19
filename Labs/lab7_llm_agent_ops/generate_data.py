#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: LLM Agent 自主运维实战
模拟真实的运维场景，让 AI Agent 自主分析告警、诊断问题并给出解决方案

核心功能:
1. 多源告警数据融合（监控日志、指标、事件）
2. 基于 LLM 的智能诊断
3. 根因分析和决策建议
4. 自动化处置方案生成
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_alert_data(output_dir='alert_data'):
    """生成多源运维告警数据"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 基础时间
    base_time = datetime.now() - timedelta(hours=2)
    
    # 场景 1: CPU 过载导致服务响应慢
    cpu_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-001",
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "source": "prometheus",
            "metric": "node_cpu_usage",
            "severity": "warning" if i < 3 else "critical",
            "value": 75 + i * 8,  # 从 75% 上升到 99%
            "threshold": 80,
            "host": "web-server-01",
            "message": f"CPU 使用率持续升高：{75 + i * 8}%",
            "labels": {
                "env": "production",
                "service": "nginx",
                "team": "platform"
            }
        }
        for i in range(6)
    ]
    
    # 关联告警：内存压力
    memory_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-002",
            "timestamp": (base_time + timedelta(minutes=i+2)).isoformat(),
            "source": "prometheus",
            "metric": "node_memory_usage",
            "severity": "warning",
            "value": 82 + i * 3,
            "threshold": 85,
            "host": "web-server-01",
            "message": f"内存使用率告警：{82 + i * 3}%",
            "labels": {
                "env": "production",
                "service": "nginx",
                "team": "platform"
            }
        }
        for i in range(4)
    ]
    
    # 关联告警：响应时间变长
    latency_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-003",
            "timestamp": (base_time + timedelta(minutes=i+3)).isoformat(),
            "source": "grafana",
            "metric": "http_response_time",
            "severity": "warning" if i < 2 else "critical",
            "value": 1.5 + i * 0.8,  # 从 1.5s 上升到 5.5s
            "threshold": 2.0,
            "host": "web-server-01",
            "message": f"HTTP 响应时间异常：{1.5 + i * 0.8:.2f}s",
            "labels": {
                "env": "production",
                "service": "api-gateway",
                "team": "backend"
            }
        }
        for i in range(5)
    ]
    
    # 关联告警：错误率上升
    error_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-004",
            "timestamp": (base_time + timedelta(minutes=i+4)).isoformat(),
            "source": "elk",
            "metric": "error_rate",
            "severity": "warning",
            "value": 2.5 + i * 1.5,  # 从 2.5% 上升到 8.5%
            "threshold": 5.0,
            "host": "web-server-01",
            "message": f"应用错误率升高：{2.5 + i * 1.5:.1f}%",
            "labels": {
                "env": "production",
                "service": "order-service",
                "team": "business"
            }
        }
        for i in range(4)
    ]
    
    # 场景 2: 数据库连接池耗尽
    db_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-005",
            "timestamp": (base_time + timedelta(minutes=i+5)).isoformat(),
            "source": "prometheus",
            "metric": "mysql_connection_pool_usage",
            "severity": "critical" if i > 2 else "warning",
            "value": 70 + i * 10,  # 从 70% 到 100%
            "threshold": 80,
            "host": "db-master-01",
            "message": f"MySQL 连接池使用率：{70 + i * 10}%",
            "labels": {
                "env": "production",
                "service": "mysql",
                "team": "dba"
            }
        }
        for i in range(4)
    ]
    
    # 场景 3: 磁盘空间不足
    disk_alerts = [
        {
            "alert_id": f"ALT-{base_time.strftime('%Y%m%d%H%M%S')}-006",
            "timestamp": (base_time + timedelta(hours=i)).isoformat(),
            "source": "zabbix",
            "metric": "disk_usage",
            "severity": "info" if i == 0 else ("warning" if i == 1 else "critical"),
            "value": 85 + i * 5,  # 从 85% 到 95%
            "threshold": 85,
            "host": "log-server-01",
            "mount_point": "/var/log",
            "message": f"磁盘空间不足：{85 + i * 5}% ({i * 20}GB 剩余)",
            "labels": {
                "env": "production",
                "service": "logging",
                "team": "infra"
            }
        }
        for i in range(3)
    ]
    
    # 合并所有告警
    all_alerts = cpu_alerts + memory_alerts + latency_alerts + error_alerts + db_alerts + disk_alerts
    
    # 按时间排序
    all_alerts.sort(key=lambda x: x['timestamp'])
    
    # 保存为文件
    alerts_file = os.path.join(output_dir, 'alerts.json')
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump(all_alerts, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已生成告警数据：{alerts_file}")
    print(f"✓ 告警总数：{len(all_alerts)}")
    print(f"✓ 告警来源：{len(set(a['source'] for a in all_alerts))} 个监控系统")
    print(f"✓ 严重级别分布:")
    
    severity_count = {}
    for alert in all_alerts:
        sev = alert['severity']
        severity_count[sev] = severity_count.get(sev, 0) + 1
    
    for sev, count in sorted(severity_count.items()):
        print(f"  - {sev}: {count}条")
    
    # 生成场景摘要
    scenarios = [
        {
            "scenario_id": "SCENARIO-001",
            "title": "CPU 过载连锁反应",
            "description": "CPU 使用率持续升高 → 内存压力 → 响应时间变长 → 错误率上升",
            "root_cause": "可能存在死循环或资源泄漏",
            "impact": "用户访问缓慢，部分请求失败",
            "alert_ids": [a['alert_id'] for a in cpu_alerts + memory_alerts + latency_alerts + error_alerts],
            "timeline_hours": 0.1  # 10 分钟内爆发
        },
        {
            "scenario_id": "SCENARIO-002", 
            "title": "数据库连接池耗尽",
            "description": "连接池使用率快速上升至 100%",
            "root_cause": "可能是慢查询或连接泄漏",
            "impact": "数据库操作超时，业务中断",
            "alert_ids": [a['alert_id'] for a in db_alerts],
            "timeline_hours": 0.08
        },
        {
            "scenario_id": "SCENARIO-003",
            "title": "磁盘空间渐进式告警",
            "description": "日志磁盘空间逐步被占用",
            "root_cause": "日志量过大或未清理旧日志",
            "impact": "可能导致日志写入失败，影响故障排查",
            "alert_ids": [a['alert_id'] for a in disk_alerts],
            "timeline_hours": 3  # 3 小时渐变
        }
    ]
    
    scenarios_file = os.path.join(output_dir, 'scenarios.json')
    with open(scenarios_file, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已生成故障场景：{scenarios_file}")
    print(f"✓ 场景数量：{len(scenarios)}")
    
    return all_alerts, scenarios


def generate_runbook_templates(output_dir='runbook_templates'):
    """生成运维手册模板库"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    runbooks = [
        {
            "runbook_id": "RB-CPU-HIGH",
            "title": "CPU 使用率过高处理流程",
            "trigger_condition": "CPU 使用率 > 80% 持续 5 分钟",
            "severity": "P1",
            "steps": [
                {
                    "step": 1,
                    "action": "确认告警真实性",
                    "command": "top -bn1 | head -20",
                    "check": "确认是否有进程占用异常 CPU"
                },
                {
                    "step": 2,
                    "action": "识别高负载进程",
                    "command": "ps aux --sort=-%cpu | head -10",
                    "check": "记录 PID 和进程名"
                },
                {
                    "step": 3,
                    "action": "分析进程行为",
                    "command": "strace -p <PID> -c",
                    "check": "查看系统调用分布"
                },
                {
                    "step": 4,
                    "action": "临时缓解",
                    "command": "renice +10 -p <PID>",
                    "check": "降低进程优先级"
                },
                {
                    "step": 5,
                    "action": "重启服务（如必要）",
                    "command": "systemctl restart <service>",
                    "check": "观察 CPU 是否恢复正常"
                }
            ],
            "escalation": "如果无法定位原因，升级到二线支持"
        },
        {
            "runbook_id": "RB-MEMORY-LEAK",
            "title": "内存泄漏排查流程",
            "trigger_condition": "内存使用率 > 85%",
            "severity": "P1",
            "steps": [
                {
                    "step": 1,
                    "action": "查看内存使用概况",
                    "command": "free -h && cat /proc/meminfo",
                    "check": "确认可用内存和缓存情况"
                },
                {
                    "step": 2,
                    "action": "识别内存占用进程",
                    "command": "ps aux --sort=-%mem | head -10",
                    "check": "找出内存占用最高的进程"
                },
                {
                    "step": 3,
                    "action": "检查 Java 堆内存（如果是 Java 应用）",
                    "command": "jmap -heap <pid>",
                    "check": "查看堆内存使用情况"
                },
                {
                    "step": 4,
                    "action": "分析内存增长趋势",
                    "command": "watch -n 5 'ps -p <PID> -o rss,vsz,%mem'",
                    "check": "观察内存是否持续增长"
                },
                {
                    "step": 5,
                    "action": "临时措施",
                    "command": "systemctl restart <service>",
                    "check": "释放内存，记录当前状态供后续分析"
                }
            ],
            "escalation": "收集 heap dump 并联系开发团队分析"
        },
        {
            "runbook_id": "RB-DISK-FULL",
            "title": "磁盘空间清理流程",
            "trigger_condition": "磁盘使用率 > 90%",
            "severity": "P2",
            "steps": [
                {
                    "step": 1,
                    "action": "查看磁盘使用情况",
                    "command": "df -h && du -sh /* | sort -hr | head -20",
                    "check": "找出占用空间最大的目录"
                },
                {
                    "step": 2,
                    "action": "检查日志文件",
                    "command": "find /var/log -type f -size +100M",
                    "check": "查找大日志文件"
                },
                {
                    "step": 3,
                    "action": "清理旧日志",
                    "command": "journalctl --vacuum-time=7d",
                    "check": "保留最近 7 天的日志"
                },
                {
                    "step": 4,
                    "action": "压缩归档",
                    "command": "tar -czf old_logs.tar.gz /var/log/*.gz",
                    "check": "将旧日志打包存档"
                },
                {
                    "step": 5,
                    "action": "设置日志轮转",
                    "command": "vi /etc/logrotate.d/<app>",
                    "check": "配置自动清理策略"
                }
            ],
            "escalation": "如需扩容磁盘，提交变更申请"
        },
        {
            "runbook_id": "RB-DB-CONNECTION",
            "title": "数据库连接池耗尽处理",
            "trigger_condition": "连接池使用率 > 90%",
            "severity": "P0",
            "steps": [
                {
                    "step": 1,
                    "action": "查看当前连接数",
                    "command": "mysql -e \"SHOW PROCESSLIST;\"",
                    "check": "统计活跃连接和睡眠连接"
                },
                {
                    "step": 2,
                    "action": "识别慢查询",
                    "command": "mysql -e \"SELECT * FROM information_schema.PROCESSLIST WHERE TIME > 60;\"",
                    "check": "找出执行时间过长的查询"
                },
                {
                    "step": 3,
                    "action": "终止异常连接",
                    "command": "mysql -e \"KILL <connection_id>;\"",
                    "check": "谨慎操作，避免影响正常业务"
                },
                {
                    "step": 4,
                    "action": "临时增加连接池大小",
                    "command": "修改配置文件 max_connections 参数",
                    "check": "评估数据库服务器承受能力"
                },
                {
                    "step": 5,
                    "action": "优化慢查询",
                    "command": "explain <slow_query>",
                    "check": "分析执行计划，添加索引"
                }
            ],
            "escalation": "联系 DBA 团队进行深度优化"
        }
    ]
    
    # 保存所有 runbook
    for runbook in runbooks:
        filename = os.path.join(output_dir, f"{runbook['runbook_id']}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(runbook, f, indent=2, ensure_ascii=False)
        print(f"✓ 已生成运维手册：{filename}")
    
    # 创建索引文件
    index = {
        "total_runbooks": len(runbooks),
        "runbooks": [
            {
                "runbook_id": rb["runbook_id"],
                "title": rb["title"],
                "severity": rb["severity"]
            }
            for rb in runbooks
        ]
    }
    
    index_file = os.path.join(output_dir, 'index.json')
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已生成索引：{index_file}")
    
    return runbooks


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 7: LLM Agent 自主运维实战 - 数据生成")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 生成告警数据
    print("=" * 60)
    print("步骤 1: 生成多源告警数据")
    print("=" * 60)
    alerts, scenarios = generate_alert_data('alert_data')
    print("")
    
    # 生成运维手册
    print("=" * 60)
    print("步骤 2: 生成运维手册模板库")
    print("=" * 60)
    runbooks = generate_runbook_templates('runbook_templates')
    print("")
    
    print("=" * 60)
    print("✅ 数据生成完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  运行：python3 main.py")
    print("  体验 LLM Agent 的自主运维诊断能力")
    print("")


if __name__ == '__main__':
    main()
