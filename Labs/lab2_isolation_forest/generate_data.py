#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 2: Isolation Forest 检测多维指标异常
数据生成脚本 - 生成多维监控数据
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_multidimensional_data(output_file='multidim_monitoring_data.csv'):
    """
    生成多维监控指标数据（模拟真实场景）
    
    包含以下维度：
    - CPU 使用率
    - 内存使用率
    - 磁盘 IO
    - 网络流量
    - 响应时间
    """
    # 设置随机种子以保证结果可复现
    np.random.seed(42)
    
    # 生成 7 天的数据（1008 个时间点，每 10 分钟一个点）
    n_points = 1008
    start_time = datetime.now() - timedelta(days=7)
    
    # 生成时间戳
    timestamps = [start_time + timedelta(minutes=10*i) for i in range(n_points)]
    
    # 正常模式：各指标之间存在一定的关联性
    # CPU 使用率：均值 45%，标准差 10%
    cpu_usage = np.random.normal(loc=45, scale=10, size=n_points)
    
    # 内存使用率：与 CPU 正相关（CPU 高时内存也倾向于高）
    memory_usage = 0.6 * cpu_usage + np.random.normal(loc=35, scale=8, size=n_points)
    
    # 磁盘 IO：与 CPU 中度相关
    disk_io = 0.4 * cpu_usage + np.random.normal(loc=50, scale=15, size=n_points)
    
    # 网络流量：周期性模式 + 随机波动
    time_index = np.arange(n_points)
    network_traffic = (
        30 * np.sin(2 * np.pi * time_index / 144) +  # 24 小时周期
        np.random.normal(loc=50, scale=12, size=n_points)
    )
    
    # 响应时间：与负载相关（CPU、内存、网络的综合影响）
    response_time = (
        0.3 * cpu_usage + 
        0.2 * memory_usage + 
        0.1 * network_traffic +
        np.random.normal(loc=50, scale=10, size=n_points)
    )
    
    # 确保所有值在合理范围内
    cpu_usage = np.clip(cpu_usage, 0, 100)
    memory_usage = np.clip(memory_usage, 0, 100)
    disk_io = np.clip(disk_io, 0, 100)
    network_traffic = np.clip(network_traffic, 0, 150)
    response_time = np.clip(response_time, 0, 200)
    
    # 注入异常点（模拟故障场景）
    n_anomalies = 25
    anomaly_indices = np.random.choice(n_points, size=n_anomalies, replace=False)
    
    # 异常类型 1: CPU 突发（DDoS 攻击或资源泄漏）
    cpu_spike_indices = anomaly_indices[:8]
    cpu_usage[cpu_spike_indices] = np.random.uniform(90, 99, size=len(cpu_spike_indices))
    
    # 异常类型 2: 内存泄漏
    mem_leak_indices = anomaly_indices[8:14]
    memory_usage[mem_leak_indices] = np.random.uniform(92, 99, size=len(mem_leak_indices))
    
    # 异常类型 3: 磁盘 IO 瓶颈
    io_bottleneck_indices = anomaly_indices[14:18]
    disk_io[io_bottleneck_indices] = np.random.uniform(95, 100, size=len(io_bottleneck_indices))
    
    # 异常类型 4: 网络流量激增
    network_spike_indices = anomaly_indices[18:22]
    network_traffic[network_spike_indices] = np.random.uniform(120, 150, size=len(network_spike_indices))
    
    # 异常类型 5: 响应时间超时（综合故障）
    timeout_indices = anomaly_indices[22:]
    response_time[timeout_indices] = np.random.uniform(150, 200, size=len(timeout_indices))
    cpu_usage[timeout_indices] = np.random.uniform(85, 95, size=len(timeout_indices))
    memory_usage[timeout_indices] = np.random.uniform(85, 95, size=len(timeout_indices))
    
    # 创建 DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_usage_percent': cpu_usage,
        'memory_usage_percent': memory_usage,
        'disk_io_percent': disk_io,
        'network_traffic_mbps': network_traffic,
        'response_time_ms': response_time
    })
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    print(f"✓ 数据已生成并保存到 {output_file}")
    print(f"✓ 数据形状：{df.shape}")
    print(f"✓ 注入异常点数量：{n_anomalies}")
    print(f"\n前 5 行数据:")
    print(df.head())
    print(f"\n数据统计信息:")
    print(df.describe())
    
    return df

if __name__ == '__main__':
    df = generate_multidimensional_data()
