#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3: LSTM 自动编码器时序异常检测
异常检测与可视化脚本
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

from model import create_model


def load_data_and_model(data_file='timeseries_data.csv', model_path='lstm_ae_model.pth', 
                        sequence_length=60, device='cpu'):
    """加载数据、模型和标准化器"""
    
    # 读取数据
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 提取 CPU 使用率
    cpu_data = df['cpu_usage_percent'].values.reshape(-1, 1)
    
    # 数据标准化
    scaler = MinMaxScaler(feature_range=(0, 1))
    cpu_scaled = scaler.fit_transform(cpu_data)
    
    # 加载模型
    checkpoint = torch.load(model_path, map_location=device)
    model_config = checkpoint['model_config']
    
    model = create_model(
        input_size=model_config['input_size'],
        hidden_size=model_config['hidden_size'],
        num_layers=model_config['num_layers'],
        device=device
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"✓ 模型加载完成：{model_path}")
    print(f"  - 输入维度：{model_config['input_size']}")
    print(f"  - 隐藏层大小：{model_config['hidden_size']}")
    print("")
    
    return df, cpu_scaled, scaler, model


def create_sequences(data, seq_length):
    """创建滑动窗口序列"""
    sequences = []
    indices = []
    for i in range(len(data) - seq_length):
        seq = data[i:i+seq_length]
        sequences.append(seq)
        indices.append(i + seq_length - 1)  # 记录序列最后一个点的索引
    
    return np.array(sequences), np.array(indices)


def detect_anomalies(model, data, scaler, sequence_length=60, threshold_percentile=95, device='cpu'):
    """
    使用训练好的模型检测异常
    
    参数:
        model: LSTM 自动编码器模型
        data: 标准化后的数据
        scaler: 标准化器
        sequence_length: 序列长度
        threshold_percentile: 异常阈值百分位数
        device: 计算设备
    
    返回:
        reconstruction_errors: 重构误差数组
        anomaly_scores: 异常分数数组
        is_anomaly: 布尔数组，标记是否为异常
        threshold: 异常阈值
    """
    print("=" * 60)
    print("执行异常检测")
    print("=" * 60)
    
    # 创建序列
    X_sequences, indices = create_sequences(data, sequence_length)
    X_tensor = torch.FloatTensor(X_sequences).to(device)
    
    # 使用模型进行重构
    with torch.no_grad():
        reconstructions = model(X_tensor)
    
    # 计算重构误差（MSE）
    mse_loss = nn.MSELoss(reduction='none')
    reconstruction_errors = mse_loss(reconstructions.cpu(), X_tensor.cpu()).numpy()
    
    # 对每个序列取平均误差作为该时间点的异常分数
    anomaly_scores = reconstruction_errors.mean(axis=(1, 2))
    
    # 确定异常阈值
    threshold = np.percentile(anomaly_scores, threshold_percentile)
    
    # 标记异常点
    is_anomaly = anomaly_scores > threshold
    
    # 扩展为完整时间长度的数组（前面的点没有预测）
    full_anomaly_scores = np.zeros(len(data))
    full_is_anomaly = np.zeros(len(data), dtype=bool)
    
    for idx, score, anomaly in zip(indices, anomaly_scores, is_anomaly):
        full_anomaly_scores[idx] = score
        full_is_anomaly[idx] = anomaly
    
    print(f"✓ 异常检测完成")
    print(f"  - 总样本数：{len(data)}")
    print(f"  - 异常点数量：{np.sum(full_is_anomaly)}")
    print(f"  - 异常率：{np.sum(full_is_anomaly)/len(data)*100:.2f}%")
    print(f"  - 异常阈值：{threshold:.6f}")
    print("")
    
    return full_anomaly_scores, full_is_anomaly, threshold


def visualize_results(df, original_data, anomaly_scores, is_anomaly, threshold, 
                      save_path='anomaly_detection_results.png'):
    """可视化异常检测结果"""
    
    # 创建图形
    fig = plt.figure(figsize=(20, 12))
    
    # 子图 1: 原始数据 + 异常点标记
    ax1 = plt.subplot(3, 1, 1)
    timestamps = df['timestamp'].values
    
    plt.plot(timestamps, original_data.flatten(), linewidth=1.5, 
             label='CPU Usage', color='steelblue', alpha=0.7)
    
    # 标记异常点
    anomaly_mask = is_anomaly
    plt.scatter(timestamps[anomaly_mask], original_data[anomaly_mask].flatten(),
                c='red', s=80, marker='o', label='Anomaly', zorder=5, edgecolors='black')
    
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('CPU Usage (%)', fontsize=12)
    plt.title('CPU Usage Time Series with Anomalies', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # 子图 2: 异常分数随时间变化
    ax2 = plt.subplot(3, 1, 2)
    plt.plot(timestamps, anomaly_scores, linewidth=1.5, 
             label='Anomaly Score', color='coral')
    plt.axhline(y=threshold, color='red', linestyle='--', linewidth=2, 
                label=f'Threshold ({threshold:.6f})')
    
    plt.fill_between(timestamps, 0, anomaly_scores, 
                     where=(anomaly_scores > threshold),
                     interpolate=True, color='red', alpha=0.3,
                     label='Anomaly Region')
    
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Anomaly Score (Reconstruction Error)', fontsize=12)
    plt.title('Anomaly Scores Over Time', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # 子图 3: 异常分数分布直方图
    ax3 = plt.subplot(3, 1, 3)
    plt.hist(anomaly_scores[anomaly_scores > 0], bins=100, 
             alpha=0.7, color='steelblue', edgecolor='black', density=True)
    
    # 绘制阈值线
    plt.axvline(x=threshold, color='red', linestyle='--', linewidth=2, 
                label=f'Threshold ({threshold:.6f})')
    
    # 标记异常区域
    plt.fill_between(np.linspace(min(anomaly_scores[anomaly_scores > 0]), 
                                  max(anomaly_scores[anomaly_scores > 0]), 100),
                     0, 1, 
                     where=(np.linspace(min(anomaly_scores[anomaly_scores > 0]), 
                                        max(anomaly_scores[anomaly_scores > 0]), 100) > threshold),
                     interpolate=True, color='red', alpha=0.3,
                     transform=ax3.get_xaxis_transform())
    
    plt.xlabel('Anomaly Score', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.title('Distribution of Anomaly Scores', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ 可视化结果已保存到：{save_path}")
    plt.show()


def generate_anomaly_report(df, anomaly_scores, is_anomaly, top_n=10):
    """生成异常详情报告"""
    
    print("=" * 60)
    print("异常详情报告")
    print("=" * 60)
    
    # 获取所有异常点
    anomaly_indices = np.where(is_anomaly)[0]
    
    if len(anomaly_indices) == 0:
        print("未检测到异常")
        return
    
    print(f"\n共发现 {len(anomaly_indices)} 个异常点\n")
    
    # 按异常分数排序，显示前 N 个最严重的异常
    sorted_indices = np.argsort(anomaly_scores[is_anomaly])[::-1][:top_n]
    
    print(f"Top {top_n} 严重异常点:")
    print("-" * 60)
    
    for rank, idx in enumerate(sorted_indices, 1):
        actual_idx = anomaly_indices[idx]
        timestamp = df.iloc[actual_idx]['timestamp']
        cpu_value = df.iloc[actual_idx]['cpu_usage_percent']
        score = anomaly_scores[actual_idx]
        
        print(f"\n#{rank}: 时间={timestamp}, "
              f"CPU={cpu_value:.2f}%, "
              f"异常分数={score:.6f}")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 3: LSTM 自动编码器时序异常检测 - 异常检测与可视化")
    print("=" * 60)
    print("")
    
    # 检测设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"✓ 使用设备：{device}")
    print("")
    
    # 加载数据和模型
    df, cpu_scaled, scaler, model = load_data_and_model(
        data_file='timeseries_data.csv',
        model_path='lstm_ae_model.pth',
        sequence_length=60,
        device=device
    )
    
    # 检测异常
    anomaly_scores, is_anomaly, threshold = detect_anomalies(
        model=model,
        data=cpu_scaled,
        scaler=scaler,
        sequence_length=60,
        threshold_percentile=95,
        device=device
    )
    
    # 可视化结果
    visualize_results(
        df=df,
        original_data=df['cpu_usage_percent'].values.reshape(-1, 1),
        anomaly_scores=anomaly_scores,
        is_anomaly=is_anomaly,
        threshold=threshold,
        save_path='anomaly_detection_results.png'
    )
    
    # 生成异常报告
    generate_anomaly_report(df, anomaly_scores, is_anomaly, top_n=10)
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)
    print("")
    print("输出文件:")
    print("  - lstm_ae_model.pth: 训练好的模型")
    print("  - training_history.png: 训练历史曲线")
    print("  - anomaly_detection_results.png: 异常检测结果")
    print("")
    print("下一步:")
    print("  1. 分析异常检测结果")
    print("  2. 调整阈值观察效果")
    print("  3. 对比其他方法（如 Isolation Forest）")
    print("")


if __name__ == '__main__':
    main()
