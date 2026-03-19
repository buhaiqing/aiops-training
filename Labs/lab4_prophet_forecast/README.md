# Lab 4: Prophet 时序预测与异常检测

## 📁 目录结构

```
lab4_prophet_forecast/
├── README.md                    # 本文件（快速指南）
├── lab_guide.md                 # 详细实验指导文档
├── generate_data.py             # 数据生成脚本
├── main.py                      # 主程序：Prophet 预测与异常检测
├── Makefile                     # 自动化构建脚本
├── pyproject.toml               # Python 项目配置
├── requirements.txt             # Python 依赖列表
├── install_uv.sh                # uv 安装脚本
├── .gitignore                   # Git 忽略配置
└── prophet_timeseries.csv       # 生成的数据文件（运行后产生）
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
make deps     # 安装依赖包（包括 Prophet）
make data     # 生成时序数据
make run      # 执行预测与异常检测
```

### 方式二：手动执行

#### 1. 安装依赖

```bash
pip install pandas matplotlib scikit-learn prophet
```

#### 2. 生成数据

```bash
python generate_data.py
```

#### 3. 运行 Prophet 分析

```bash
python main.py
```

---

## 🎯 学习目标

完成本实验后，你将能够：

- ✅ 理解 Prophet 模型的基本原理
- ✅ 掌握时序数据的趋势、季节性分解
- ✅ 处理节假日效应等特殊时间模式
- ✅ 基于预测残差进行异常检测
- ✅ 评估时序预测模型的性能
- ✅ 对比不同异常检测方法的效果

---

## ⏱️ 预计时间

- **基础部分**: 60-75 分钟
- **扩展练习**: 30-45 分钟

---

## 📊 输出文件

| 文件名 | 说明 |
|--------|------|
| `prophet_timeseries.csv` | 带趋势和季节性的时序数据 |
| `prophet_anomaly_detection_results.png` | 检测结果可视化（6 个子图） |
| `prophet_forecast_full.csv` | 完整预测结果（包含置信区间） |

---

## 💡 核心思想

Prophet 通过以下方式实现异常检测：

1. **时序分解**: 将数据分解为趋势、季节性、节假日成分
2. **区间预测**: 生成预测的上下界（置信区间）
3. **残差分析**: 计算实际值与预测值的偏差
4. **异常判定**: 超出置信区间或 Z-Score 过大的点为异常

**优势**:
- 自动处理趋势变化
- 捕捉多种季节性模式
- 内置节假日效应处理
- 可解释性强，易于业务理解

---

## 🔧 故障排查

### 问题 1: Prophet 安装失败
```bash
# 方法 1: 使用 conda
conda install -c conda-forge prophet

# 方法 2: 先安装 cmdstanpy
pip install cmdstanpy
pip install prophet
```

### 问题 2: 训练速度慢
```python
# 减少季节性组件或使用简化的模型
model = Prophet(
    weekly_seasonality=True,
    yearly_seasonality=False,  # 关闭年季节性
    changepoint_prior_scale=0.05
)
```

### 问题 3: 中文显示问题
```python
# 修改字体配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
```

---

## 📝 下一步

完成 Lab 4 后，继续学习：
- Lab 5: One-Class SVM 未知故障模式识别
- Lab 6: 基于 RAG 的故障知识问答系统
- Lab 7: LLM Agent 自主运维实战
- Lab 8: ChatOps 集成 - 钉钉/企微机器人

---

## ❓ 常见问题

**Q: Prophet 相比 LSTM 有什么优势？**  
A: Prophet 更易用，可解释性更好，适合有明显趋势和季节性的数据。LSTM 更适合复杂的非线性时序关系。

**Q: 如何选择合适的 threshold_multiplier？**  
A: 通常使用 2.5-3.0。可以根据业务容忍度调整，敏感场景用 2.0，宽松场景用 3.5。

**Q: 如何处理多个季节性周期？**  
A: Prophet 支持添加自定义季节性，如小时级别、月级别等。

**Q: 预测效果不好怎么办？**  
A: 
1. 检查数据是否有足够的历史长度
2. 调整 changepoint_prior_scale 参数
3. 添加重要的节假日信息
4. 考虑是否需要分段建模

---

## 📧 反馈与建议

欢迎提出改进建议和优化方案！
