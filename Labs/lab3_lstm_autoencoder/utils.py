#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3: LSTM 自动编码器时序异常检测
工具函数
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix


def calculate_statistics(y_true, y_pred):
    """
    计算分类统计指标
    
    参数:
        y_true: 真实标签
        y_pred: 预测标签
    
    返回:
        stats_dict: 包含各种统计指标的字典
    """
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    stats_dict = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': int(tp),
        'false_positives': int(fp),
        'true_negatives': int(tn),
        'false_negatives': int(fn),
        'accuracy': (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    }
    
    return stats_dict


def print_statistics(stats_dict):
    """打印统计指标"""
    print("=" * 60)
    print("异常检测性能统计")
    print("=" * 60)
    print(f"精确率 (Precision):  {stats_dict['precision']:.4f}")
    print(f"召回率 (Recall):     {stats_dict['recall']:.4f}")
    print(f"F1 分数 (F1-Score):   {stats_dict['f1_score']:.4f}")
    print(f"准确率 (Accuracy):   {stats_dict['accuracy']:.4f}")
    print("-" * 60)
    print(f"真正例 (TP): {stats_dict['true_positives']}")
    print(f"假正例 (FP): {stats_dict['false_positives']}")
    print(f"真负例 (TN): {stats_dict['true_negatives']}")
    print(f"假负例 (FN): {stats_dict['false_negatives']}")
    print("=" * 60)


def find_optimal_threshold(anomaly_scores, true_labels, percentile_range=(90, 99)):
    """
    寻找最优异常阈值
    
    参数:
        anomaly_scores: 异常分数数组
        true_labels: 真实标签数组
        percentile_range: 搜索的百分位范围
    
    返回:
        optimal_threshold: 最优阈值
        best_f1: 最佳 F1 分数
        best_stats: 最佳统计指标
    """
    print(f"\n搜索最优阈值（百分位范围：{percentile_range[0]}-{percentile_range[1]}）...")
    
    percentiles = np.arange(percentile_range[0], percentile_range[1] + 1, 0.5)
    best_f1 = 0
    optimal_threshold = 0
    best_stats = None
    
    for percentile in percentiles:
        threshold = np.percentile(anomaly_scores, percentile)
        predictions = anomaly_scores > threshold
        
        stats = calculate_statistics(true_labels, predictions)
        
        if stats['f1_score'] > best_f1:
            best_f1 = stats['f1_score']
            optimal_threshold = threshold
            best_stats = stats
    
    print(f"✓ 最优阈值：{optimal_threshold:.6f} (第{np.searchsorted(np.sort(anomaly_scores), optimal_threshold)/len(anomaly_scores)*100:.2f}百分位)")
    print(f"✓ 最佳 F1 分数：{best_f1:.4f}")
    
    return optimal_threshold, best_f1, best_stats


def plot_anomaly_examples(df, anomaly_scores, is_anomaly, example_indices, 
                          window_size=100, save_path='anomaly_examples.png'):
    """
    绘制异常示例的详细视图
    
    参数:
        df: 原始 DataFrame
        anomaly_scores: 异常分数
        is_anomaly: 异常标记
        example_indices: 要展示的异常点索引列表
        window_size: 展示的时间窗口大小
        save_path: 保存路径
    """
    fig, axes = plt.subplots(len(example_indices), 1, figsize=(16, 4*len(example_indices)))
    
    if len(example_indices) == 1:
        axes = [axes]
    
    for idx, ax in zip(example_indices, axes):
        # 确定时间窗口
        start_idx = max(0, idx - window_size//2)
        end_idx = min(len(df), idx + window_size//2)
        
        # 绘制 CPU 使用率
        timestamps = df.iloc[start_idx:end_idx]['timestamp'].values
        cpu_values = df.iloc[start_idx:end_idx]['cpu_usage_percent'].values
        
        ax.plot(timestamps, cpu_values, linewidth=2, label='CPU Usage', color='steelblue')
        
        # 标记异常点
        if is_anomaly[idx]:
            ax.scatter(df.iloc[idx]['timestamp'], df.iloc[idx]['cpu_usage_percent'],
                      c='red', s=200, marker='x', label='Anomaly', zorder=5, linewidth=3)
        
        # 标记当前点
        ax.scatter(df.iloc[idx]['timestamp'], df.iloc[idx]['cpu_usage_percent'],
                  c='orange', s=100, marker='o', zorder=4, edgecolors='black')
        
        ax.set_title(f'Example at Index {idx} (Score: {anomaly_scores[idx]:.6f})', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('CPU Usage (%)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 异常示例已保存到：{save_path}")
    plt.show()


def compare_methods(method1_results, method2_results, true_labels, method1_name='Method 1', 
                    method2_name='Method 2'):
    """
    比较两种方法的性能
    
    参数:
        method1_results: 方法 1 的预测结果
        method2_results: 方法 2 的预测结果
        true_labels: 真实标签
        method1_name: 方法 1 名称
        method2_name: 方法 2 名称
    """
    print("\n" + "=" * 60)
    print("方法对比分析")
    print("=" * 60)
    
    stats1 = calculate_statistics(true_labels, method1_results)
    stats2 = calculate_statistics(true_labels, method2_results)
    
    print(f"\n{method1_name}:")
    print_statistics(stats1)
    
    print(f"\n{method2_name}:")
    print_statistics(stats2)
    
    # 比较
    print("\n" + "=" * 60)
    print("性能对比")
    print("=" * 60)
    print(f"{'指标':<15} | {method1_name:<15} | {method2_name:<15} | {'提升':<10}")
    print("-" * 60)
    
    metrics = ['precision', 'recall', 'f1_score', 'accuracy']
    for metric in metrics:
        val1 = stats1[metric]
        val2 = stats2[metric]
        improvement = ((val2 - val1) / val1 * 100) if val1 > 0 else 0
        print(f"{metric:<15} | {val1:<15.4f} | {val2:<15.4f} | {improvement:+.2f}%")
    
    print("=" * 60)


if __name__ == '__main__':
    # 示例用法
    print("工具函数模块 - 直接运行无操作")
    print("请在其他脚本中导入使用这些函数")
