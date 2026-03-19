#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 1: 3-Sigma 原则检测 CPU/内存异常
主程序：异常检测与可视化
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def detect_anomalies_3sigma(data, column_name):
    """
    使用 3-Sigma 原则检测异常
    
    参数:
        data: 输入 DataFrame
        column_name: 要检测的列名
    
    返回:
        anomalies: 异常点 DataFrame
        lower_bound: 下界
        upper_bound: 上界
        mean: 均值
        std: 标准差
    """
    # 计算均值和标准差
    mean = data[column_name].mean()
    std = data[column_name].std()
    
    # 计算 3-Sigma 边界
    lower_bound = mean - 3 * std
    upper_bound = mean + 3 * std
    
    # 检测异常点
    anomalies = data[(data[column_name] < lower_bound) | 
                     (data[column_name] > upper_bound)].copy()
    anomalies['anomaly_type'] = np.where(
        anomalies[column_name] < lower_bound, 
        '低于下界', 
        '高于上界'
    )
    
    return anomalies, lower_bound, upper_bound, mean, std


def generate_anomaly_report(anomalies, metric_name):
    """生成异常详情报告"""
    print(f"\n{'='*60}")
    print(f"{metric_name}异常详情报告")
    print(f"{'='*60}")
    
    if len(anomalies) == 0:
        print("未检测到异常")
        return
    
    print(f"\n共发现 {len(anomalies)} 个异常点:\n")
    
    for idx, row in anomalies.iterrows():
        anomaly_type = row.get('anomaly_type', '未知')
        if 'cpu' in metric_name.lower():
            value = row['cpu_usage_percent']
        else:
            value = row['memory_usage_percent']
        
        print(f"时间：{row['timestamp']}, "
              f"值：{value:.2f}%, "
              f"类型：{anomaly_type}")


def visualize_results(df, cpu_anomalies, mem_anomalies, 
                      cpu_mean, cpu_std, cpu_lower, cpu_upper,
                      mem_mean, mem_std, mem_lower, mem_upper):
    """创建可视化图表"""
    # 创建可视化图表
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # CPU 使用率图
    axes[0].plot(df['timestamp'], df['cpu_usage_percent'], 
                 alpha=0.6, label='CPU 使用率', linewidth=1)
    axes[0].axhline(y=cpu_mean, color='green', linestyle='--', 
                    label=f'均值 ({cpu_mean:.2f}%)', linewidth=2)
    axes[0].axhline(y=cpu_upper, color='red', linestyle='--', 
                    label=f'上界 ({cpu_upper:.2f}%)', linewidth=2)
    axes[0].axhline(y=cpu_lower, color='orange', linestyle='--', 
                    label=f'下界 ({cpu_lower:.2f}%)', linewidth=2)
    
    # 标记异常点
    axes[0].scatter(cpu_anomalies['timestamp'], 
                    cpu_anomalies['cpu_usage_percent'],
                    c='red', s=100, marker='o', 
                    label=f'异常点 ({len(cpu_anomalies)}个)', 
                    zorder=5, edgecolors='black')
    
    # 填充正常区域
    axes[0].fill_between(df['timestamp'], 
                          cpu_lower, cpu_upper, 
                          alpha=0.2, color='green',
                          label='正常范围')
    
    axes[0].set_title('CPU 使用率 3-Sigma 异常检测', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('时间')
    axes[0].set_ylabel('CPU 使用率 (%)')
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 内存使用率图
    axes[1].plot(df['timestamp'], df['memory_usage_percent'], 
                 alpha=0.6, label='内存使用率', linewidth=1, color='orange')
    axes[1].axhline(y=mem_mean, color='green', linestyle='--', 
                    label=f'均值 ({mem_mean:.2f}%)', linewidth=2)
    axes[1].axhline(y=mem_upper, color='red', linestyle='--', 
                    label=f'上界 ({mem_upper:.2f}%)', linewidth=2)
    axes[1].axhline(y=mem_lower, color='darkorange', linestyle='--', 
                    label=f'下界 ({mem_lower:.2f}%)', linewidth=2)
    
    # 标记异常点
    axes[1].scatter(mem_anomalies['timestamp'], 
                    mem_anomalies['memory_usage_percent'],
                    c='red', s=100, marker='^', 
                    label=f'异常点 ({len(mem_anomalies)}个)', 
                    zorder=5, edgecolors='black')
    
    # 填充正常区域
    axes[1].fill_between(df['timestamp'], 
                          mem_lower, mem_upper, 
                          alpha=0.2, color='green',
                          label='正常范围')
    
    axes[1].set_title('内存使用率 3-Sigma 异常检测', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('时间')
    axes[1].set_ylabel('内存使用率 (%)')
    axes[1].legend(loc='upper right', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('3sigma_detection_result.png', dpi=300, bbox_inches='tight')
    print("\n✓ 可视化结果已保存到：3sigma_detection_result.png")
    plt.show()


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 1: 3-Sigma 原则检测 CPU/内存异常")
    print("=" * 60)
    
    # 读取数据
    df = pd.read_csv('cpu_memory_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 检测 CPU 异常
    cpu_anomalies, cpu_lower, cpu_upper, cpu_mean, cpu_std = detect_anomalies_3sigma(
        df, 'cpu_usage_percent'
    )
    
    # 检测内存异常
    mem_anomalies, mem_lower, mem_upper, mem_mean, mem_std = detect_anomalies_3sigma(
        df, 'memory_usage_percent'
    )
    
    print("=" * 60)
    print("CPU 使用率 3-Sigma 检测结果")
    print("=" * 60)
    print(f"均值：{cpu_mean:.2f}%")
    print(f"标准差：{cpu_std:.2f}%")
    print(f"正常范围：[{cpu_lower:.2f}%, {cpu_upper:.2f}%]")
    print(f"检测到的异常点数量：{len(cpu_anomalies)}")
    print(f"异常率：{len(cpu_anomalies)/len(df)*100:.2f}%")
    
    print("\n" + "=" * 60)
    print("内存使用率 3-Sigma 检测结果")
    print("=" * 60)
    print(f"均值：{mem_mean:.2f}%")
    print(f"标准差：{mem_std:.2f}%")
    print(f"正常范围：[{mem_lower:.2f}%, {mem_upper:.2f}%]")
    print(f"检测到的异常点数量：{len(mem_anomalies)}")
    print(f"异常率：{len(mem_anomalies)/len(df)*100:.2f}%")
    
    # 生成异常报告
    generate_anomaly_report(cpu_anomalies, 'CPU')
    generate_anomaly_report(mem_anomalies, '内存')
    
    # 可视化
    visualize_results(df, cpu_anomalies, mem_anomalies,
                      cpu_mean, cpu_std, cpu_lower, cpu_upper,
                      mem_mean, mem_std, mem_lower, mem_upper)


if __name__ == '__main__':
    main()
