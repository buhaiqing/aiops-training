#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: LLM Agent 自主运维实战 - 核心诊断引擎
使用大语言模型（LLM）进行智能故障诊断和根因分析

核心能力:
1. 多告警关联分析
2. 根因推断
3. 处置方案生成
4. 决策建议输出
"""

import os
import json
from datetime import datetime
from typing import List, Dict


class LLMOpsAgent:
    """基于 LLM 的运维智能体"""
    
    def __init__(self):
        self.alerts = []
        self.scenarios = []
        self.runbooks = {}
        
    def load_alerts(self, alerts_file='alert_data/alerts.json'):
        """加载告警数据"""
        print("=" * 60)
        print("加载告警数据")
        print("=" * 60)
        
        if not os.path.exists(alerts_file):
            raise FileNotFoundError(f"告警文件不存在：{alerts_file}")
        
        with open(alerts_file, 'r', encoding='utf-8') as f:
            self.alerts = json.load(f)
        
        print(f"✓ 成功加载 {len(self.alerts)} 条告警")
        print(f"✓ 时间范围：{self.alerts[0]['timestamp'][:19]} 至 {self.alerts[-1]['timestamp'][:19]}")
        print(f"✓ 涉及主机：{len(set(a['host'] for a in self.alerts))} 台")
        print("")
        
        return self.alerts
    
    def load_scenarios(self, scenarios_file='alert_data/scenarios.json'):
        """加载故障场景"""
        if os.path.exists(scenarios_file):
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                self.scenarios = json.load(f)
            print(f"✓ 加载 {len(self.scenarios)} 个故障场景模板")
        else:
            print("⚠️  未找到故障场景文件，将使用通用分析模式")
            self.scenarios = []
        print("")
    
    def load_runbooks(self, runbooks_dir='runbook_templates'):
        """加载运维手册"""
        print("加载运维手册库...")
        
        if not os.path.exists(runbooks_dir):
            print(f"⚠️  运维手册目录不存在：{runbooks_dir}")
            return
        
        for filename in os.listdir(runbooks_dir):
            # 跳过索引文件
            if filename == 'index.json':
                continue
            
            if filename.endswith('.json'):
                filepath = os.path.join(runbooks_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    runbook = json.load(f)
                    self.runbooks[runbook['runbook_id']] = runbook
        
        print(f"✓ 已加载 {len(self.runbooks)} 个运维手册")
        print("")
    
    def analyze_alert_correlation(self) -> List[Dict]:
        """分析告警之间的关联性"""
        print("=" * 60)
        print("告警关联分析")
        print("=" * 60)
        
        # 按主机分组告警
        alerts_by_host = {}
        for alert in self.alerts:
            host = alert['host']
            if host not in alerts_by_host:
                alerts_by_host[host] = []
            alerts_by_host[host].append(alert)
        
        correlations = []
        
        for host, host_alerts in alerts_by_host.items():
            if len(host_alerts) < 2:
                continue
            
            # 按时间排序
            host_alerts.sort(key=lambda x: x['timestamp'])
            
            # 识别因果链
            correlation = {
                'host': host,
                'alert_chain': [],
                'time_span_minutes': 0,
                'severity_escalation': False,
                'potential_root_cause': ''
            }
            
            # 构建告警链
            first_time = datetime.fromisoformat(host_alerts[0]['timestamp'])
            last_time = datetime.fromisoformat(host_alerts[-1]['timestamp'])
            correlation['time_span_minutes'] = (last_time - first_time).total_seconds() / 60
            
            for alert in host_alerts:
                correlation['alert_chain'].append({
                    'metric': alert['metric'],
                    'severity': alert['severity'],
                    'value': alert['value'],
                    'message': alert['message']
                })
                
                # 检查严重性升级
                if alert['severity'] == 'critical':
                    correlation['severity_escalation'] = True
            
            # 推断根因
            metrics = [a['metric'] for a in host_alerts]
            
            if 'node_cpu_usage' in metrics and 'http_response_time' in metrics:
                correlation['potential_root_cause'] = 'CPU 过载导致服务响应变慢'
            elif 'mysql_connection_pool_usage' in metrics:
                correlation['potential_root_cause'] = '数据库连接池问题'
            elif 'disk_usage' in metrics:
                correlation['potential_root_cause'] = '磁盘空间不足'
            else:
                correlation['potential_root_cause'] = '资源竞争或配置问题'
            
            correlations.append(correlation)
        
        print(f"✓ 发现 {len(correlations)} 个告警关联组")
        for i, corr in enumerate(correlations, 1):
            print(f"\n关联组 {i}:")
            print(f"  主机：{corr['host']}")
            print(f"  告警数量：{len(corr['alert_chain'])}")
            print(f"  时间跨度：{corr['time_span_minutes']:.1f} 分钟")
            print(f"  严重性升级：{'是' if corr['severity_escalation'] else '否'}")
            print(f"  可能根因：{corr['potential_root_cause']}")
        
        print("")
        return correlations
    
    def generate_diagnosis_report(self, correlations: List[Dict]) -> str:
        """生成诊断报告（模拟 LLM 输出）"""
        
        report = []
        report.append("=" * 60)
        report.append("🤖 LLM Agent 智能诊断报告")
        report.append("=" * 60)
        report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 总体态势评估
        critical_count = sum(1 for a in self.alerts if a['severity'] == 'critical')
        warning_count = sum(1 for a in self.alerts if a['severity'] == 'warning')
        
        overall_severity = "🔴 严重" if critical_count > 0 else ("🟡 警告" if warning_count > 0 else "🟢 正常")
        
        report.append(f"【整体态势】{overall_severity}")
        report.append(f"  - 紧急告警：{critical_count} 条")
        report.append(f"  - 警告告警：{warning_count} 条")
        report.append(f"  - 影响系统：{len(set(a['host'] for a in self.alerts))} 个")
        report.append("")
        
        # 逐个分析关联组
        for i, corr in enumerate(correlations, 1):
            report.append(f"{'='*60}")
            report.append(f"【事件 {i}】{corr['host']} - {corr['potential_root_cause']}")
            report.append("=" * 60)
            report.append("")
            
            # 时间线分析
            report.append("📋 事件时间线:")
            for j, alert in enumerate(corr['alert_chain'], 1):
                severity_icon = "🔴" if alert['severity'] == 'critical' else ("🟡" if alert['severity'] == 'warning' else "🟢")
                report.append(f"  {severity_icon} T+{j*5}min: {alert['message']}")
            report.append("")
            
            # 根因分析
            report.append("🔍 根因分析:")
            root_cause = self._analyze_root_cause(corr)
            report.append(f"  最可能原因：{root_cause['primary']}")
            report.append(f"  支持证据：{', '.join(root_cause['evidence'])}")
            report.append(f"  置信度：{root_cause['confidence']}%")
            report.append("")
            
            # 影响评估
            report.append("💥 影响评估:")
            impact = self._assess_impact(corr)
            report.append(f"  业务影响：{impact['business']}")
            report.append(f"  用户影响：{impact['users']}")
            report.append(f"  数据风险：{impact['data']}")
            report.append("")
            
            # 处置建议
            report.append("💡 处置建议:")
            actions = self._generate_actions(corr)
            for k, action in enumerate(actions, 1):
                report.append(f"  {k}. {action['priority']}: {action['action']}")
                report.append(f"     命令：{action['command']}")
                report.append(f"     预期：{action['expected_outcome']}")
            report.append("")
            
            # 推荐运维手册
            if corr['potential_root_cause'] in self.runbooks or any(k in corr['potential_root_cause'] for k in self.runbooks.keys()):
                report.append("📚 推荐运维手册:")
                matched_runbook = self._match_runbook(corr)
                if matched_runbook:
                    report.append(f"  - {matched_runbook['title']} ({matched_runbook['runbook_id']})")
                    report.append(f"    严重级别：{matched_runbook['severity']}")
                    report.append(f"    关键步骤：{len(matched_runbook['steps'])} 步")
                report.append("")
        
        # 总结和建议
        report.append("=" * 60)
        report.append("【总结与建议】")
        report.append("=" * 60)
        report.append("")
        report.append("🎯 优先级排序:")
        report.append("  1. P0 - CPU 过载事件（web-server-01）- 立即处理")
        report.append("  2. P0 - 数据库连接池（db-master-01）- 立即处理")
        report.append("  3. P2 - 磁盘空间（log-server-01）- 可延后处理")
        report.append("")
        report.append("📊 趋势预测:")
        report.append("  - 如不干预，CPU 告警可能在 30 分钟内扩散到其他节点")
        report.append("  - 数据库连接池将在 10 分钟内耗尽，导致业务中断")
        report.append("  - 磁盘空间预计还可维持 6 小时")
        report.append("")
        report.append("👥 人员调度建议:")
        report.append("  - 平台团队：处理 CPU 和内存问题")
        report.append("  - DBA 团队：优化数据库连接")
        report.append("  - 基础架构团队：清理磁盘空间")
        report.append("")
        
        return "\n".join(report)
    
    def _analyze_root_cause(self, corr: Dict) -> Dict:
        """分析根因（模拟 LLM 推理）"""
        
        metrics = [a['metric'] for a in corr['alert_chain']]
        
        if 'node_cpu_usage' in metrics:
            return {
                'primary': '应用程序存在死循环或复杂计算逻辑',
                'evidence': [
                    'CPU 使用率持续上升无波动',
                    '伴随内存压力',
                    '响应时间同步恶化'
                ],
                'confidence': 85
            }
        elif 'mysql_connection_pool_usage' in metrics:
            return {
                'primary': '慢查询导致连接占用时间过长',
                'evidence': [
                    '连接池使用率快速攀升',
                    '无明显流量高峰',
                    '可能存在全表扫描'
                ],
                'confidence': 78
            }
        else:
            return {
                'primary': '资源规划不足或使用模式改变',
                'evidence': [
                    '渐进式增长模式',
                    '无突发性变化',
                    '长期累积效应'
                ],
                'confidence': 70
            }
    
    def _assess_impact(self, corr: Dict) -> Dict:
        """评估影响（模拟 LLM 判断）"""
        
        has_critical = any(a['severity'] == 'critical' for a in corr['alert_chain'])
        
        if 'http_response_time' in [a['metric'] for a in corr['alert_chain']]:
            return {
                'business': '订单转化率可能下降 15-20%',
                'users': '约 30% 用户感受到明显卡顿',
                'data': '低风险 - 无数据一致性影响'
            }
        elif 'mysql_connection_pool_usage' in [a['metric'] for a in corr['alert_chain']]:
            return {
                'business': '高风险 - 可能导致交易失败',
                'users': '所有依赖数据库的功能不可用',
                'data': '中风险 - 需检查是否有部分提交'
            }
        else:
            return {
                'business': '中等影响 - 非核心功能降级',
                'users': '内部运维效率降低',
                'data': '低风险 - 不影响核心数据'
            }
    
    def _generate_actions(self, corr: Dict) -> List[Dict]:
        """生成处置动作（模拟 LLM 决策）"""
        
        actions = []
        
        if 'node_cpu_usage' in [a['metric'] for a in corr['alert_chain']]:
            actions = [
                {
                    'priority': 'P0 - 立即执行',
                    'action': '定位高负载进程',
                    'command': 'top -bn1 | head -20',
                    'expected_outcome': '识别占用 CPU 最高的进程'
                },
                {
                    'priority': 'P1 - 5 分钟内',
                    'action': '临时降低优先级',
                    'command': 'renice +10 -p <PID>',
                    'expected_outcome': '缓解系统压力'
                },
                {
                    'priority': 'P2 - 30 分钟内',
                    'action': '重启异常服务',
                    'command': 'systemctl restart <service>',
                    'expected_outcome': '恢复正常状态'
                }
            ]
        elif 'mysql_connection_pool_usage' in [a['metric'] for a in corr['alert_chain']]:
            actions = [
                {
                    'priority': 'P0 - 立即执行',
                    'action': '查看活跃连接',
                    'command': 'mysql -e "SHOW PROCESSLIST;"',
                    'expected_outcome': '识别占用连接的会话'
                },
                {
                    'priority': 'P1 - 5 分钟内',
                    'action': '终止慢查询',
                    'command': 'mysql -e "KILL <connection_id>"',
                    'expected_outcome': '释放连接资源'
                },
                {
                    'priority': 'P2 - 1 小时内',
                    'action': '优化查询语句',
                    'command': 'EXPLAIN SELECT ...',
                    'expected_outcome': '防止问题复发'
                }
            ]
        else:
            actions = [
                {
                    'priority': 'P2 - 今日完成',
                    'action': '清理磁盘空间',
                    'command': 'journalctl --vacuum-time=7d',
                    'expected_outcome': '释放至少 20GB 空间'
                }
            ]
        
        return actions
    
    def _match_runbook(self, corr: Dict):
        """匹配最相关的运维手册"""
        
        if 'CPU' in corr['potential_root_cause']:
            return self.runbooks.get('RB-CPU-HIGH')
        elif '数据库' in corr['potential_root_cause'] or '连接池' in corr['potential_root_cause']:
            return self.runbooks.get('RB-DB-CONNECTION')
        elif '磁盘' in corr['potential_root_cause']:
            return self.runbooks.get('RB-DISK-FULL')
        else:
            return None


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 7: LLM Agent 自主运维实战 - 智能诊断")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 创建 Agent
    agent = LLMOpsAgent()
    
    try:
        # 1. 加载数据
        agent.load_alerts('alert_data/alerts.json')
        agent.load_scenarios('alert_data/scenarios.json')
        agent.load_runbooks('runbook_templates')
        
        # 2. 关联分析
        correlations = agent.analyze_alert_correlation()
        
        # 3. 生成诊断报告
        report = agent.generate_diagnosis_report(correlations)
        
        # 4. 保存报告
        report_file = f'llm_diagnosis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("=" * 60)
        print("✅ 诊断完成！")
        print("=" * 60)
        print(f"\n详细报告已保存至：{report_file}")
        print("\n下一步:")
        print("  1. 查看生成的诊断报告")
        print("  2. 验证 AI 的判断是否准确")
        print("  3. 思考如何改进诊断逻辑")
        print("")
        
        # 显示报告摘要
        print("\n" + "=" * 60)
        print("📄 报告预览（前 50 行）")
        print("=" * 60)
        preview_lines = report.split('\n')[:50]
        print('\n'.join(preview_lines))
        print("...")
        print(f"\n完整报告共 {len(report.split(chr(10)))} 行，请查看 {report_file}")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误：{e}")
        print("\n请先运行以下命令生成数据:")
        print("  python3 generate_data.py")
        print("或运行:")
        print("  make data")
    
    except Exception as e:
        print(f"\n❌ 系统错误：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)
    print("")


if __name__ == '__main__':
    main()
