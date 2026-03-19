#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3: LSTM 自动编码器时序异常检测
数据生成脚本 - 生成带有时序模式的监控数据
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_timeseries_data(output_file='timeseries_data.csv'):
    """
    生成时序监控数据（模拟真实场景）
    
    包含以下特征：
    - 趋势性（长期变化）
    - 周期性（日周期、周周期）
    - 随机波动
    - 异常点注入
    """
    # 设置随机种子以保证结果可复现
    np.random.seed(42)
    
    # 生成 14 天的数据（2016 个时间点，每 10 分钟一个点）
    n_points = 2016
    start_time = datetime.now() - timedelta(days=14)
    
    # 生成时间戳
    timestamps = [start_time + timedelta(minutes=10*i) for i in range(n_points)]
    
    # 时间索引（用于周期性计算）
    t = np.arange(n_points)
    
    # 基础值
    base_level = 50
    
    # 趋势成分：缓慢上升后下降
    trend = 0.005 * t - 0.000002 * t**2
    
    # 日周期成分（24 小时 = 144 个时间点）
    daily_cycle = 15 * np.sin(2 * np.pi * t / 144)
    
    # 周周期成分（7 天 = 1008 个时间点）
    weekly_cycle = 8 * np.sin(2 * np.pi * t / 1008)
    
    # 随机波动
    noise = np.random.normal(loc=0, scale=3, size=n_points)
    
    # 组合所有成分
    cpu_usage = base_level + trend + daily_cycle + weekly_cycle + noise
    
    # 确保在合理范围内
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    # 注入异常点（模拟故障场景）
    n_anomalies = 30
    valid_indices = np.arange(100, n_points - 100)
    anomaly_indices = np.random.choice(valid_indices, size=n_anomalies, replace=False)
    
    # 异常类型 1: 突发尖峰（CPU 使用率突然飙升）
    spike_indices = anomaly_indices[:15]
    spike_magnitudes = np.random.uniform(25, 40, size=len(spike_indices))
    cpu_usage[spike_indices] += spike_magnitudes
    
    # 异常类型 2: 持续高负载（连续多个点异常）
    plateau_start_indices = anomaly_indices[15:22]
    for start_idx in plateau_start_indices:
        plateau_length = np.random.randint(3, 8)
        cpu_usage[start_idx:start_idx+plateau_length] += np.random.uniform(20, 30)
    
    # 异常类型 3: 异常低谷（可能是服务中断）
    valley_indices = anomaly_indices[22:]
    valley_magnitudes = np.random.uniform(-20, -30, size=len(valley_indices))
    cpu_usage[valley_indices] += valley_magnitudes
    
    # 最终裁剪到 0-100 范围
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    # 创建 DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_usage_percent': cpu_usage
    })
    
    # 标记异常点（用于后续验证）
    df['is_anomaly'] = False
    df.loc[anomaly_indices, 'is_anomaly'] = True
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    print(f"✓ 数据已生成并保存到 {output_file}")
    print(f"✓ 数据形状：{df.shape}")
    print(f"✓ 总样本数：{n_points}")
    print(f"✓ 注入异常点数量：{n_anomalies}")
    print(f"✓ 异常率：{n_anomalies/n_points*100:.2f}%")
    print(f"\n数据统计信息:")
    print(df[['cpu_usage_percent']].describe())
    print(f"\n前 5 行数据:")
    print(df.head())
    
    return df

if __name__ == '__main__':
    df = generate_timeseries_data()
