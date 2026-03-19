#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 3: LSTM 自动编码器时序异常检测
模型定义 - LSTM Autoencoder 架构
"""

import torch
import torch.nn as nn


class LSTMEncoder(nn.Module):
    """LSTM 编码器：将输入序列压缩为低维表示"""
    
    def __init__(self, input_size, hidden_size, num_layers=1, dropout=0.2):
        super(LSTMEncoder, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
    
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        outputs, (hidden, cell) = self.lstm(x)
        # 返回最后一个时间步的隐藏状态
        return hidden, cell


class LSTMDecoder(nn.Module):
    """LSTM 解码器：从低维表示重构原始序列"""
    
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, dropout=0.2):
        super(LSTMDecoder, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x, hidden, cell):
        # x shape: (batch_size, seq_len, input_size)
        output, (hidden, cell) = self.lstm(x, (hidden, cell))
        # 通过全连接层输出
        prediction = self.fc(output)
        return prediction, hidden, cell


class LSTMAutoencoder(nn.Module):
    """LSTM 自动编码器：编码器 + 解码器"""
    
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, dropout=0.2):
        super(LSTMAutoencoder, self).__init__()
        
        self.encoder = LSTMEncoder(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout
        )
        
        self.decoder = LSTMDecoder(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=input_size,
            num_layers=num_layers,
            dropout=dropout
        )
    
    def forward(self, x):
        # 编码
        hidden, cell = self.encoder(x)
        
        # 解码（使用零向量作为解码器输入）
        batch_size = x.size(0)
        seq_len = x.size(1)
        decoder_input = torch.zeros(batch_size, seq_len, x.size(2)).to(x.device)
        
        reconstruction, _, _ = self.decoder(decoder_input, hidden, cell)
        
        return reconstruction
    
    def encode(self, x):
        """获取编码后的表示"""
        hidden, cell = self.encoder(x)
        return hidden, cell


def create_model(input_size=1, hidden_size=64, num_layers=2, dropout=0.2, device='cpu'):
    """
    创建 LSTM 自动编码器模型
    
    参数:
        input_size: 输入特征维度（通常为 1）
        hidden_size: 隐藏层大小
        num_layers: LSTM 层数
        dropout: Dropout 比例
        device: 计算设备
    
    返回:
        model: PyTorch 模型
    """
    model = LSTMAutoencoder(
        input_size=input_size,
        hidden_size=hidden_size,
        num_layers=num_layers,
        dropout=dropout
    ).to(device)
    
    return model


def count_parameters(model):
    """统计模型参数数量"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == '__main__':
    # 测试模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 创建示例输入
    batch_size = 32
    seq_len = 60
    input_size = 1
    
    x = torch.randn(batch_size, seq_len, input_size).to(device)
    
    # 创建模型
    model = create_model(input_size=input_size, hidden_size=64, num_layers=2, device=device)
    
    print(f"模型参数量：{count_parameters(model):,}")
    print(f"输入形状：{x.shape}")
    
    # 前向传播
    reconstruction = model(x)
    print(f"输出形状：{reconstruction.shape}")
    
    # 计算重构误差
    mse_loss = nn.MSELoss(reduction='none')
    loss = mse_loss(reconstruction, x)
    print(f"重构误差形状：{loss.shape}")
    print(f"平均重构误差：{loss.mean().item():.6f}")
