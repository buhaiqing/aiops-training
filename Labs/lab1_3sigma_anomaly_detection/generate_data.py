#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 1: 3-Sigma 原则检测 CPU/内存异常
数据生成脚本
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_cpu_memory_data(output_file='cpu_memory_data.csv'):
    """
    生成模拟的 CPU 和内存使用率数据
    
    参数:
        output_file: 输出 CSV 文件名
    """
    # 设置随机种子以保证结果可复现
    np.random.seed(42)
    
    # 生成 7 天（1008 个时间点，每 10 分钟一个点）的数据
    n_points = 1008
    start_time = datetime.now() - timedelta(days=7)
    
    # 正常 CPU 使用率：均值 45%，标准差 10%
    cpu_normal = np.random.normal(loc=45, scale=10, size=n_points)
    
    # 添加一些异常点（模拟故障）
    anomaly_indices = np.random.choice(n_points, size=20, replace=False)
    cpu_anomalies = np.random.uniform(low=85, high=98, size=20)
    cpu_usage = cpu_normal.copy()
    cpu_usage[anomaly_indices] = cpu_anomalies
    
    # 确保 CPU 使用率在 0-100 之间
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    # 生成时间戳
    timestamps = [start_time + timedelta(minutes=10*i) for i in range(n_points)]
    
    # 创建 DataFrame
    df_cpu = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_usage_percent': cpu_usage
    })
    
    # 同样方法生成内存使用率数据
    mem_normal = np.random.normal(loc=60, scale=8, size=n_points)
    mem_anomaly_indices = np.random.choice(n_points, size=15, replace=False)
    mem_anomalies = np.random.uniform(low=90, high=99, size=15)
    mem_usage = mem_normal.copy()
    mem_usage[mem_anomaly_indices] = mem_anomalies
    mem_usage = np.clip(mem_usage, 0, 100)
    
    df_mem = pd.DataFrame({
        'timestamp': timestamps,
        'memory_usage_percent': mem_usage
    })
    
    # 合并数据
    df = pd.merge(df_cpu, df_mem, on='timestamp')
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    print(f"✓ 数据已生成并保存到 {output_file}")
    print(f"✓ 数据形状：{df.shape}")
    print(f"\n前 5 行数据:")
    print(df.head())
    
    return df

if __name__ == '__main__':
    df = generate_cpu_memory_data()
