#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 4: Prophet 时序预测与异常检测
数据生成脚本 - 生成带趋势、季节性和节假日效应的时序数据
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_prophet_data(output_file='prophet_timeseries.csv'):
    """
    生成模拟的时序监控数据（包含多种模式）
    
    包含以下成分：
    - 线性趋势
    - 周季节性（7 天周期）
    - 年季节性（365 天周期）
    - 节假日效应
    - 随机噪声
    - 异常点注入
    """
    # 设置随机种子以保证结果可复现
    np.random.seed(42)
    
    # 生成 1 年的数据（每天一个点，共 365 个点）
    n_points = 365
    start_date = datetime.now() - timedelta(days=n_points)
    dates = [start_date + timedelta(days=i) for i in range(n_points)]
    
    # 时间索引
    t = np.arange(n_points)
    
    # 1. 趋势成分：缓慢增长的线性趋势
    trend = 50 + 0.05 * t
    
    # 2. 周季节性（以 7 为周期）
    weekly_seasonality = (
        5 * np.sin(2 * np.pi * t / 7) + 
        3 * np.cos(2 * np.pi * t / 7)
    )
    
    # 3. 年季节性（以 365 为周期）
    yearly_seasonality = (
        8 * np.sin(2 * np.pi * t / 365) +
        4 * np.cos(2 * np.pi * t / 365)
    )
    
    # 4. 节假日效应（模拟周末和特殊日期）
    holidays_effect = np.zeros(n_points)
    
    # 周末效应（周六、周日流量下降）
    for i, date in enumerate(dates):
        if date.weekday() >= 5:  # 周六=5, 周日=6
            holidays_effect[i] = -8
    
    # 模拟几个特殊节假日（如春节、国庆等）
    holiday_dates = [
        start_date + timedelta(days=30),   # 春节
        start_date + timedelta(days=180),  # 年中促销
        start_date + timedelta(days=300),  # 国庆
    ]
    for holiday in holiday_dates:
        idx = int((holiday - start_date).days)
        if 0 <= idx < n_points:
            holidays_effect[idx] = -15  # 节假日流量大幅下降
            if idx + 1 < n_points:
                holidays_effect[idx + 1] = -10  # 节后恢复期
    
    # 5. 随机噪声
    noise = np.random.normal(loc=0, scale=2, size=n_points)
    
    # 组合所有成分
    cpu_usage = trend + weekly_seasonality + yearly_seasonality + holidays_effect + noise
    
    # 确保在合理范围内
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    # 注入异常点（模拟故障场景）
    n_anomalies = 15
    anomaly_indices = np.random.choice(range(50, n_points - 20), size=n_anomalies, replace=False)
    
    # 异常类型 1: 突发尖峰（流量激增）
    spike_indices = anomaly_indices[:8]
    spike_magnitudes = np.random.uniform(20, 35, size=len(spike_indices))
    cpu_usage[spike_indices] += spike_magnitudes
    
    # 异常类型 2: 异常低谷（服务中断）
    valley_indices = anomaly_indices[8:]
    valley_magnitudes = np.random.uniform(-25, -35, size=len(valley_indices))
    cpu_usage[valley_indices] += valley_magnitudes
    
    # 最终裁剪到 0-100 范围
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    # 创建 DataFrame（Prophet 要求的格式）
    df = pd.DataFrame({
        'ds': pd.to_datetime(dates),
        'y': cpu_usage,
        'is_anomaly': False
    })
    
    # 标记异常点
    df.loc[anomaly_indices, 'is_anomaly'] = True
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    print(f"✓ 数据已生成并保存到 {output_file}")
    print(f"✓ 数据形状：{df.shape}")
    print(f"✓ 总样本数：{n_points}")
    print(f"✓ 注入异常点数量：{n_anomalies}")
    print(f"✓ 异常率：{n_anomalies/n_points*100:.2f}%")
    print(f"\n数据统计信息:")
    print(df[['y']].describe())
    print(f"\n前 5 行数据:")
    print(df.head())
    print(f"\n数据覆盖时间范围：{df['ds'].min()} 至 {df['ds'].max()}")
    
    return df

if __name__ == '__main__':
    df = generate_prophet_data()
