# Lab 2: Isolation Forest 检测多维指标异常

## 📁 目录结构

```
lab2_isolation_forest/
├── README.md                    # 本文件（快速指南）
├── lab_guide.md                 # 详细实验指导文档
├── generate_data.py             # 数据生成脚本
├── main.py                      # 主程序：Isolation Forest 异常检测
├── Makefile                     # 自动化构建脚本
├── pyproject.toml               # Python 项目配置
├── requirements.txt             # Python 依赖列表
├── install_uv.sh                # uv 安装脚本
├── .gitignore                   # Git 忽略配置
└── multidim_monitoring_data.csv # 生成的数据文件（运行后产生）
```

## 🚀 快速开始

### 前置要求

**Python 版本**: Python 3.10（推荐）

**安装 uv** (如果尚未安装):

```bash
# 方法 1: 使用 pip 安装（推荐）
pip install uv

# 方法 2: 使用官方脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者运行提供的安装脚本
./install_uv.sh
```

### 方式一：使用 uv + Makefile（推荐）

```bash
# 一键完成所有步骤（创建虚拟环境 + 安装依赖 + 生成数据 + 运行检测）
make all

# 或者分步执行
make venv     # 使用 uv 创建虚拟环境
make deps     # 安装依赖包到虚拟环境
make data     # 生成模拟数据
make run      # 运行 Isolation Forest 检测

# 其他有用命令
make test     # 测试环境配置
make clean    # 清理生成的文件
make help     # 显示帮助信息
```

**激活虚拟环境**:
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 方式二：手动执行

#### 1. 安装依赖

```bash
pip install numpy pandas matplotlib seaborn scikit-learn
```

#### 2. 生成数据

```bash
python generate_data.py
```

输出示例：
```
✓ 数据已生成并保存到 multidim_monitoring_data.csv
✓ 数据形状：(1008, 6)
✓ 注入异常点数量：25

前 5 行数据:
                  timestamp  cpu_usage_percent  memory_usage_percent  ...
0 2024-03-12 10:30:00            54.881350             68.928810       ...
1 2024-03-12 10:40:00            41.121978             60.513187       ...
2 2024-03-12 10:50:00            56.312332             69.727400       ...
3 2024-03-12 11:00:00            39.054605             59.372563       ...
4 2024-03-12 11:10:00            45.477588             63.226553       ...
```

#### 3. 运行 Isolation Forest 检测

```bash
python main.py
```

输出示例：
```
============================================================
Lab 2: Isolation Forest 检测多维指标异常
============================================================

✓ 数据加载完成
  - 样本数量：1008
  - 特征维度：5
  - 特征列表：cpu_usage_percent, memory_usage_percent, disk_io_percent, network_traffic_mbps, response_time_ms

============================================================
训练 Isolation Forest 模型
============================================================
✓ 模型训练完成
  - 树的数量：100
  - 异常点比例估计：2.5%

============================================================
Isolation Forest 异常检测结果
============================================================
总样本数：1008
检测到的异常点数：25
异常率：2.48%
平均异常分数：0.1234
最小异常分数：-0.2345
最大异常分数：0.4567
```

### 4. 查看结果

程序会生成可视化图表 `isolation_forest_results.png`，包含：
- 异常分数分布直方图
- 异常点时间分布散点图
- PCA 降维后的异常分布
- 各指标的异常点分布详情

---

## 🎯 学习目标

完成本实验后，你将能够：

- ✅ 理解 Isolation Forest 算法的基本原理
- ✅ 使用 scikit-learn 实现 Isolation Forest
- ✅ 对多维监控指标进行联合异常检测
- ✅ 分析和解释异常检测结果
- ✅ 调整 contamination 参数优化检测效果
- ✅ 使用 PCA 降维可视化高维异常

---

## ⏱️ 预计时间

- **基础部分**：40-50 分钟（数据生成 + 模型训练 + 异常检测 + 可视化）
- **扩展练习**：20-30 分钟（参数调优 + 特征分析 + 对比实验）

---

## 📊 输出文件

运行后会生成以下文件：

| 文件名 | 说明 |
|--------|------|
| `multidim_monitoring_data.csv` | 多维监控指标模拟数据 |
| `isolation_forest_results.png` | Isolation Forest 检测结果可视化 |

---

## 💡 使用提示

1. **理解原理**：Isolation Forest 基于"孤立"思想，异常点更容易被隔离
2. **参数调优**：contamination 参数影响异常点的判定阈值
3. **特征工程**：可以尝试不同的特征组合或添加新特征
4. **结果解读**：关注异常分数而不仅仅是二元分类结果
5. **对比分析**：与 3-Sigma 等单变量方法对比，体会多维检测的优势

---

## 🔧 故障排查

### 问题 1：内存不足
```bash
# 减少 n_estimators 或 max_samples 参数
# 在 main.py 中修改：
model = IsolationForest(n_estimators=50, max_samples=256, ...)
```

### 问题 2：检测效果不佳
- 调整 contamination 参数（建议范围：0.01-0.05）
- 检查数据是否需要标准化
- 尝试增加或减少特征维度

### 问题 3：可视化中文显示问题
```python
# 修改字体配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
```

---

## 📝 下一步

完成 Lab 2 后，继续学习：
- Lab 3: LSTM 自动编码器时序异常检测
- Lab 4: 基于 RAG 的故障知识问答系统
- Lab 5: LLM Agent 自主运维实战

---

## ❓ 常见问题

**Q: Isolation Forest 相比 3-Sigma 有什么优势？**  
A: Isolation Forest 可以检测多维空间中的异常，考虑了特征间的相关性，而 3-Sigma 只能检测单变量的异常。

**Q: 如何选择合适的 contamination 值？**  
A: 根据业务场景估计异常比例。如果没有先验知识，可以从 0.01-0.05 开始尝试，观察检测效果。

**Q: 为什么需要数据标准化？**  
A: Isolation Forest 基于距离计算，不同量纲的特征会影响结果。标准化确保所有特征在同一尺度上。

**Q: 如何处理类别不平衡（正常点远多于异常点）？**  
A: Isolation Forest 对不平衡数据有较好的鲁棒性。可以通过调整 contamination 参数或使用加权采样进一步优化。

---

## 📧 反馈与建议

欢迎提出改进建议和优化方案！
