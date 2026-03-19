# Lab 3: LSTM 自动编码器时序异常检测

## 📁 目录结构

```
lab3_lstm_autoencoder/
├── README.md                    # 本文件（快速指南）
├── lab_guide.md                 # 详细实验指导文档
├── generate_data.py             # 数据生成脚本
├── model.py                     # LSTM 自动编码器模型定义
├── train.py                     # 模型训练脚本
├── predict.py                   # 异常检测与可视化
├── utils.py                     # 工具函数
├── Makefile                     # 自动化构建脚本
├── pyproject.toml               # Python 项目配置
├── requirements.txt             # Python 依赖列表
├── install_uv.sh                # uv 安装脚本
├── .gitignore                   # Git 忽略配置
└── timeseries_data.csv          # 生成的数据文件（运行后产生）
```

---

## 🚀 快速开始

### 前置要求

**Python 版本**: Python 3.10（推荐）

**安装 uv** (如果尚未安装):

```bash
pip install uv
```

### 方式一：使用 uv + Makefile（推荐）

```bash
# 一键完成所有步骤
make all

# 分步执行
make venv     # 创建虚拟环境
make deps     # 安装依赖包
make data     # 生成时序数据
make run      # 训练模型并检测异常
```

### 方式二：手动执行

#### 1. 安装依赖

```bash
pip install numpy pandas matplotlib scikit-learn torch
```

#### 2. 生成数据

```bash
python generate_data.py
```

#### 3. 训练模型

```bash
python train.py
```

#### 4. 异常检测与可视化

```bash
python predict.py
```

---

## 🎯 学习目标

完成本实验后，你将能够：

- ✅ 理解 LSTM 网络的基本原理
- ✅ 掌握自动编码器的架构设计
- ✅ 实现基于重构误差的异常检测
- ✅ 处理时序数据的滑动窗口技术
- ✅ 调优深度学习模型超参数

---

## ⏱️ 预计时间

- **基础部分**: 60-90 分钟
- **扩展练习**: 30-60 分钟

---

## 📊 输出文件

| 文件名 | 说明 |
|--------|------|
| `timeseries_data.csv` | 时序模拟数据 |
| `lstm_ae_model.pth` | 训练好的模型权重 |
| `reconstruction_error.png` | 重构误差分析图 |
| `anomaly_detection_results.png` | 异常检测结果可视化 |

---

## 💡 核心思想

LSTM 自动编码器通过以下方式检测异常：

1. **训练阶段**: 学习正常数据的时序模式
2. **预测阶段**: 用训练好的模型重构输入数据
3. **异常判定**: 重构误差大的点为异常点

**优势**:
- 捕捉长期依赖关系
- 适应复杂的时序模式
- 无需标注数据（无监督）

---

## 🔧 故障排查

### 问题 1: GPU 不可用
```python
# 使用 CPU 训练（速度较慢但可用）
device = torch.device('cpu')
```

### 问题 2: 内存不足
```bash
# 减小 batch_size 或 sequence_length
# 在 train.py 中修改：
batch_size = 32  # 改为 16 或 8
```

### 问题 3: 训练不收敛
- 检查学习率是否过大
- 增加训练轮数
- 调整网络层数和隐藏单元数

---

## 📝 下一步

完成 Lab 3 后，继续学习：
- Lab 4: One-Class SVM 未知故障模式识别
- Lab 5: 基于 RAG 的故障知识问答系统
- Lab 6: LLM Agent 自主运维实战

---

## ❓ 常见问题

**Q: LSTM 相比传统方法有什么优势？**  
A: LSTM 可以捕捉时间序列中的长期依赖关系，适合处理具有复杂时序模式的异常检测。

**Q: 如何确定合适的 sequence_length？**  
A: 根据数据的周期性特征选择。可以尝试多个值，选择重构误差最小的。

**Q: 为什么使用自动编码器而不是直接预测？**  
A: 自动编码器学习数据的压缩表示，通过重构误差检测异常，更适合无监督场景。

---

## 📧 反馈与建议

欢迎提出改进建议和优化方案！
