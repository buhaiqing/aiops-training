#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3: LSTM 自动编码器时序异常检测
模型训练脚本
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

from model import create_model, count_parameters


def prepare_data(data_file='timeseries_data.csv', sequence_length=60, train_ratio=0.8):
    """
    准备训练数据
    
    参数:
        data_file: 数据文件路径
        sequence_length: 序列长度（滑动窗口大小）
        train_ratio: 训练集比例
    
    返回:
        train_loader: 训练数据加载器
        test_loader: 测试数据加载器
        scaler: 数据标准化器
        train_data: 原始训练数据
        test_data: 原始测试数据
    """
    print("=" * 60)
    print("准备训练数据")
    print("=" * 60)
    
    # 读取数据
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 提取 CPU 使用率
    cpu_data = df['cpu_usage_percent'].values.reshape(-1, 1)
    
    # 数据标准化
    scaler = MinMaxScaler(feature_range=(0, 1))
    cpu_scaled = scaler.fit_transform(cpu_data)
    
    # 划分训练集和测试集
    train_size = int(len(cpu_scaled) * train_ratio)
    train_data = cpu_scaled[:train_size]
    test_data = cpu_scaled[train_size:]
    
    print(f"✓ 数据标准化完成 (Min-Max 缩放)")
    print(f"✓ 训练集大小：{len(train_data)}")
    print(f"✓ 测试集大小：{len(test_data)}")
    
    # 创建滑动窗口数据集
    def create_sequences(data, seq_length):
        sequences = []
        for i in range(len(data) - seq_length):
            seq = data[i:i+seq_length]
            sequences.append(seq)
        return np.array(sequences)
    
    # 生成序列
    X_train = create_sequences(train_data, sequence_length)
    X_test = create_sequences(test_data, sequence_length)
    
    print(f"✓ 训练序列形状：{X_train.shape}")
    print(f"✓ 测试序列形状：{X_test.shape}")
    
    # 转换为 PyTorch 张量
    X_train_tensor = torch.FloatTensor(X_train)
    X_test_tensor = torch.FloatTensor(X_test)
    
    # 创建 DataLoader
    batch_size = 64
    train_dataset = TensorDataset(X_train_tensor, X_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    test_dataset = TensorDataset(X_test_tensor, X_test_tensor)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"✓ 训练 DataLoader 创建完成 (batch_size={batch_size})")
    print("")
    
    return train_loader, test_loader, scaler, train_data, test_data


def train_model(train_loader, test_loader, input_size=1, hidden_size=64, 
                num_layers=2, learning_rate=0.001, num_epochs=50, device='cpu'):
    """
    训练 LSTM 自动编码器模型
    
    参数:
        train_loader: 训练数据加载器
        test_loader: 测试数据加载器
        input_size: 输入特征维度
        hidden_size: 隐藏层大小
        num_layers: LSTM 层数
        learning_rate: 学习率
        num_epochs: 训练轮数
        device: 计算设备
    
    返回:
        model: 训练好的模型
        train_losses: 训练损失历史
        test_losses: 测试损失历史
    """
    print("=" * 60)
    print("训练 LSTM 自动编码器模型")
    print("=" * 60)
    
    # 创建模型
    model = create_model(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=0.2,
        device=device
    )
    
    print(f"✓ 模型架构：LSTM Autoencoder")
    print(f"  - 输入维度：{input_size}")
    print(f"  - 隐藏层大小：{hidden_size}")
    print(f"  - LSTM 层数：{num_layers}")
    print(f"  - 参数量：{count_parameters(model):,}")
    print(f"  - 设备：{device}")
    print("")
    
    # 定义损失函数和优化器
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )
    
    # 训练循环
    train_losses = []
    test_losses = []
    
    print(f"开始训练，共 {num_epochs} 轮...")
    print("-" * 60)
    
    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            
            # 前向传播
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        
        # 测试阶段
        model.eval()
        test_loss = 0.0
        
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                test_loss += loss.item()
        
        avg_test_loss = test_loss / len(test_loader)
        test_losses.append(avg_test_loss)
        
        # 学习率调度
        scheduler.step(avg_test_loss)
        
        # 打印进度
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1:3d}/{num_epochs}] | "
                  f"Train Loss: {avg_train_loss:.6f} | "
                  f"Test Loss: {avg_test_loss:.6f}")
    
    print("-" * 60)
    print(f"✓ 训练完成!")
    print(f"  - 最终训练损失：{train_losses[-1]:.6f}")
    print(f"  - 最终测试损失：{test_losses[-1]:.6f}")
    print("")
    
    return model, train_losses, test_losses


def plot_training_history(train_losses, test_losses, save_path='training_history.png'):
    """绘制训练历史曲线"""
    plt.figure(figsize=(12, 6))
    
    plt.plot(train_losses, label='Training Loss', linewidth=2, color='steelblue')
    plt.plot(test_losses, label='Testing Loss', linewidth=2, color='coral')
    
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss (MSE)', fontsize=12)
    plt.title('Training History - LSTM Autoencoder', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ 训练历史已保存到：{save_path}")
    plt.show()


def save_model(model, save_path='lstm_ae_model.pth'):
    """保存模型"""
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_config': {
            'input_size': 1,
            'hidden_size': 64,
            'num_layers': 2
        }
    }, save_path)
    print(f"✓ 模型已保存到：{save_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 3: LSTM 自动编码器时序异常检测 - 模型训练")
    print("=" * 60)
    print("")
    
    # 设置随机种子以保证结果可复现
    torch.manual_seed(42)
    np.random.seed(42)
    
    # 检测设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"✓ 使用设备：{device}")
    if device.type == 'cuda':
        print(f"  - GPU: {torch.cuda.get_device_name(0)}")
    print("")
    
    # 准备数据
    train_loader, test_loader, scaler, train_data, test_data = prepare_data(
        data_file='timeseries_data.csv',
        sequence_length=60,
        train_ratio=0.8
    )
    
    # 训练模型
    model, train_losses, test_losses = train_model(
        train_loader=train_loader,
        test_loader=test_loader,
        input_size=1,
        hidden_size=64,
        num_layers=2,
        learning_rate=0.001,
        num_epochs=50,
        device=device
    )
    
    # 绘制训练历史
    plot_training_history(train_losses, test_losses, save_path='training_history.png')
    
    # 保存模型
    save_model(model, save_path='lstm_ae_model.pth')
    
    print("=" * 60)
    print("训练完成！")
    print("=" * 60)
    print("")
    print("下一步:")
    print("  1. 运行 predict.py 进行异常检测")
    print("  2. 查看训练历史图表 training_history.png")
    print("  3. 调整超参数优化模型性能")
    print("")


if __name__ == '__main__':
    main()
