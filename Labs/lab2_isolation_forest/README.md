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

## 🔍 PCA 降维可视化详解

### 为什么需要 PCA？

本实验使用 5 个监控指标（CPU、内存、磁盘 IO、网络流量、响应时间），数据是 **5 维**的，无法直接在 2D 平面上可视化。

```python
feature_cols = [
    'cpu_usage_percent',      # 维度 1
    'memory_usage_percent',   # 维度 2
    'disk_io_percent',        # 维度 3
    'network_traffic_mbps',   # 维度 4
    'response_time_ms'        # 维度 5
]
```

**PCA 的作用**：将 5 维数据降维到 2 维，同时保留最重要的变异信息。

```python
pca = PCA(n_components=2)  # 5 维 → 2 维
X_pca = pca.fit_transform(X_scaled)
```

### PCA 的两个核心作用

#### 1. 降维可视化（主要目的）

| 问题 | 解决方案 |
|------|----------|
| 5 维数据无法在 2D 平面上画图 | PCA 映射到 2 维空间 |
| 无法直观观察异常点分布 | 散点图展示正常/异常点的空间分布 |

**可视化价值**：
- 一眼看出异常点是否与正常点明显分离
- 验证 Isolation Forest 的检测效果是否合理

#### 2. 发现核心异常维度（分析价值）

PCA 告诉你：**哪些原始维度对异常贡献最大**

```python
# 方差解释率
pca.explained_variance_ratio_
# 例如：[0.45, 0.30] 表示 PC1 解释 45%，PC2 解释 30%

# 主成分载荷（各特征的权重）
pca.components_
# 例如：[0.8, 0.6, 0.1, 0.1, 0.05] 表示 CPU 和内存权重最高
```

**如何解读**：
- 如果 PC1 方差解释率高（>40%），说明大部分异常集中在该方向
- 查看 `pca.components_[0]` 找出权重最大的原始特征
- 从而定位：**异常主要是由哪些指标引起的**

### 示例解读

假设检测到异常点，通过 PCA 分析发现：

```
PC1 载荷：[0.8, 0.6, 0.1, 0.1, 0.05]
         CPU   内存  磁盘  网络  响应时间
```

**结论**：这个异常主要是 **CPU 和内存** 的问题，而不是磁盘或网络。

### ⚠️ 重要提醒：PCA 发现的是相关性，不是因果性

PCA 载荷高只说明**指标间存在联动关系**，不代表因果关系：

```
PCA 载荷示例：
  CPU:  +0.82  ← 高载荷
  内存: +0.75  ← 高载荷
```

**PCA 能说的**：
- ✅ "CPU 和内存在这个主成分上经常一起变化"
- ✅ "这批异常主要和 CPU、内存的联动模式相关"

**PCA 不能说的**：
- ❌ "是 CPU 导致了内存高"
- ❌ "内存是异常的根因"
- ❌ "这两个指标导致了异常"

**可能的真相**：
```
业务流量高峰 → CPU 飙升 + 内存飙升
     ↑
   真正的根因（第三方因素）
```

CPU 和内存只是**同时表现出异常的相关指标**，不一定是**导致异常的原因**。

### 如何正确理解 PCA 在根因分析中的作用

| PCA 适合 | PCA 不适合 |
|---------|-----------|
| 快速定位异常涉及哪些指标范围 | 断定哪个指标是"罪魁祸首" |
| 发现指标间的联动模式 | 得出"A 导致了 B"的因果结论 |
| 可视化展示异常分布方向 | 定位具体是哪个时间点的哪个指标异常 |

**推荐的根因分析流程**：
1. **PCA 快速筛选** → "这批异常主要和 CPU、内存有关"
2. **查看异常详情** → "具体是第 234 个样本，CPU 95%，内存 88%"
3. **时序图验证** → 看该时间点的趋势图
4. **业务上下文判断** → 结合当时是否有业务高峰、发布变更等

### 总结

| 作用 | 目的 |
|------|------|
| **可视化** | 5 维 → 2 维，能在图上看到异常点分布 |
| **发现核心维度** | 通过主成分的方差解释率和载荷，判断哪些指标是异常的主要来源 |
| **验证效果** | 看异常点是否在 PCA 空间中与正常点分离 |

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

## 🧪 MLflow 模型评估与实验追踪

本实验已集成 **MLflow**（Machine Learning Flow）进行实验追踪、模型管理和结果可视化。MLflow 是一个开源的机器学习生命周期管理平台，可以帮助你：

- ✅ **追踪实验参数和指标**：自动记录每次实验的超参数和结果
- ✅ **对比不同实验**：在 UI 界面直观对比多次实验的效果
- ✅ **保存和版本化模型**：管理训练好的 IsolationForest 模型
- ✅ **可复现性**：记录代码版本、依赖环境、随机种子等元数据
- ✅ **分享成果**：导出实验结果或与团队成员共享

### 📦 MLflow 核心概念

| 概念 | 说明 | 本实验示例 |
|------|------|-----------|
| **Experiment（实验）** | 一组相关的运行 | `lab2_isolation_forest_anomaly_detection` |
| **Run（运行）** | 单次实验执行 | 使用特定 contamination 值的检测 |
| **Parameters（参数）** | 输入超参数 | `n_estimators=100`, `contamination=0.025` |
| **Metrics（指标）** | 输出性能指标 | `anomaly_rate`, `avg_anomaly_score` |
| **Artifacts（产物）** | 输出的文件 | 模型、可视化图表、统计数据 |

### 🔧 环境准备

#### 方式一：使用 Docker Compose（推荐，生产级配置）

**前置要求**：
- Docker Desktop（macOS/Windows）或 Docker + Docker Compose（Linux）
- 至少 2GB 可用内存

**步骤**：

```bash
# 1. 启动 MLflow 服务（PostgreSQL + MinIO）
make mlflow-server

# 等待约 15 秒，直到所有服务启动完成
# 看到 "✓ MLflow 服务已启动！" 提示即可
```

**服务组成**：
- **MLflow Tracking Server**：实验追踪服务（端口 5000）
- **PostgreSQL**：后端存储数据库（端口 5432）
- **MinIO**：Artifact 对象存储（端口 9000/9001）

**访问地址**：
- 🌐 MLflow UI: http://localhost:5000
- 🗄️ MinIO 控制台：http://localhost:9001 
  - 用户名：`minioadmin`
  - 密码：`minioadmin`
- 🐘 PostgreSQL: `localhost:5432`
  - 数据库：`mlflow_db`
  - 用户：`mlflow`
  - 密码：`mlflow_password`

**查看日志**：
```bash
# 查看 MLflow 服务日志
docker compose logs -f mlflow

# 查看所有服务状态
docker compose ps
```

**停止服务**：
```bash
# 停止但不删除容器和数据
make mlflow-stop

# 完全清理（删除所有容器和数据）
make mlflow-clean
```

#### 方式二：本地 SQLite（快速测试，无需 Docker）

```bash
# 使用本地 SQLite 启动 MLflow 服务器
make mlflow-local

# 访问 http://localhost:5000

# 停止服务
pkill -f 'mlflow server'
```

**注意**：SQLite 模式适合快速测试，但不支持并发和多用户访问。

### 🚀 运行带 MLflow 追踪的实验

#### 1. 安装依赖

```bash
# 使用 uv（推荐）
make venv
make deps

# 或手动安装
pip install -r requirements.txt
```

#### 2. 生成数据

```bash
make data
```

#### 3. 运行实验

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 运行主程序（会自动连接 MLflow）
make run
```

**运行时你会看到**：
```
正在初始化 MLflow 实验追踪...
✓ MLflow 实验已设置：lab2_isolation_forest_anomaly_detection
  跟踪 URI: sqlite:///mlflow.db

============================================================
Lab 2: Isolation Forest 检测多维指标异常
============================================================
...
============================================================
MLflow 实验追踪完成！
============================================================
Run ID: a1b2c3d4e5f6g7h8i9j0
Run Name: isolation_forest_contamination_0.025
Experiment ID: 1
Artifact 路径：./mlruns/1/a1b2c3d4e5f6g7h8i9j0/artifacts
```

### 📊 访问 MLflow UI 查看实验结果

#### 步骤 1：打开浏览器访问 MLflow UI

根据你选择的环境：
- **Docker 模式**：http://localhost:5000
- **本地模式**：http://localhost:5000

#### 步骤 2：查看实验列表

在左侧边栏选择实验：
```
lab2_isolation_forest_anomaly_detection
```

#### 步骤 3：查看 Run 详情

点击最新的运行记录（`isolation_forest_contamination_0.025`），你将看到：

**📋 Parameters（参数）标签页**：
```
n_estimators       100
max_samples        auto
contamination      0.025
random_state       42
n_jobs             -1
```

**📈 Metrics（指标）标签页**：
```
total_samples           1008
detected_anomalies      25
anomaly_rate            2.48%
avg_anomaly_score       0.1234
min_anomaly_score      -0.2345
max_anomaly_score       0.4567
```

**📁 Artifacts（产物）标签页**：
- `isolation_forest_model/` - 训练好的模型（Pipeline 格式）
- `visualizations/isolation_forest_results.png` - 检测结果可视化图表
- `data/feature_statistics.csv` - 特征统计信息

**🏷️ Tags（标签）标签页**：
```
mlflow.runName              isolation_forest_contamination_0.025
experiment.type             anomaly_detection
algorithm                   IsolationForest
```

### 🔄 对比不同参数组合的实验效果

MLflow 的强大之处在于可以轻松对比多次实验。

#### 方法 1：修改 contamination 参数运行多次实验

```bash
# 第一次运行（contamination=0.025）
python main.py

# 修改 main.py 中的 contamination=0.03，然后再次运行
python main.py

# 修改 contamination=0.02，第三次运行
python main.py
```

#### 方法 2：创建对比实验脚本

创建 `experiment_comparison.py`：

```python
#!/usr/bin/env python3
"""对比不同 contamination 参数的实验效果"""

import mlflow
from mlflow_config import MLflowConfig
from main import load_and_prepare_data, train_isolation_forest, detect_anomalies

# 设置 MLflow
MLflowConfig.setup()

# 不同的 contamination 值
contamination_values = [0.01, 0.02, 0.025, 0.03, 0.05]

# 加载数据
df, X, timestamps, feature_cols = load_and_prepare_data()

for cont in contamination_values:
    with mlflow.start_run(run_name=f"isolation_forest_contamination_{cont}"):
        # 记录参数
        params = MLflowConfig.DEFAULT_PARAMS.copy()
        params['contamination'] = cont
        mlflow.log_params(params)
        
        # 训练和检测
        model, scaler, X_scaled = train_isolation_forest(X, contamination=cont)
        predictions, scores = detect_anomalies(model, X_scaled, timestamps)
        
        # 记录指标
        n_total = len(predictions)
        n_anomalies = np.sum(predictions == -1)
        anomaly_rate = n_anomalies / n_total * 100
        
        mlflow.log_metric("contamination", cont)
        mlflow.log_metric("detected_anomalies", n_anomalies)
        mlflow.log_metric("anomaly_rate", anomaly_rate)
        mlflow.log_metric("avg_anomaly_score", float(scores.mean()))
        
        print(f"✓ 完成 contamination={cont}: 检测到 {n_anomalies} 个异常 ({anomaly_rate:.2f}%)")

print("\n所有实验完成！请在 MLflow UI 中对比结果。")
```

运行对比实验：
```bash
python experiment_comparison.py
```

#### 在 MLflow UI 中对比

1. 访问 http://localhost:5000
2. 点击实验名称
3. 勾选多个 Run 记录
4. 自动显示对比表格和图表

**对比视图会显示**：
- 并排的参数对比
- 指标趋势图（折线图、柱状图）
- 散点图矩阵

### 💾 加载和复现已记录的模型

#### 从 Python 代码加载

```python
import mlflow
from mlflow_config import MLflowConfig

# 设置 MLflow
MLflowConfig.setup()

# 获取最近的运行
client = mlflow.MlflowClient()
experiment = client.get_experiment_by_name(MLflowConfig.EXPERIMENT_NAME)
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["start_time DESC"],
    max_results=1
)

if runs:
    run_id = runs[0].info.run_id
    
    # 加载模型
    model_uri = f"runs:/{run_id}/{MLflowConfig.MODEL_PATH}"
    loaded_pipeline = mlflow.sklearn.load_model(model_uri)
    
    print(f"✓ 模型加载成功：{model_uri}")
    
    # 使用加载的模型进行预测
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    
    # 加载新数据
    new_data = pd.read_csv('new_monitoring_data.csv')
    predictions = loaded_pipeline.predict(new_data)
    
    # 分析结果
    anomalies = predictions[predictions == -1]
    print(f"检测到 {len(anomalies)} 个异常点")
else:
    print("未找到任何运行的实验")
```

#### 从 MLflow UI 下载模型

1. 访问 MLflow UI
2. 选择目标 Run
3. 在 Artifacts 标签页找到 `isolation_forest_model/` 文件夹
4. 点击 "Download" 下载模型
5. 使用以下代码加载：

```python
import mlflow.sklearn

# 加载本地下载的模型
model = mlflow.sklearn.load_model("path/to/downloaded/isolation_forest_model")
```

### 🎯 最佳实践

#### 1. 命名规范

```python
# 清晰的 Run 命名
mlflow.start_run(run_name=f"isolation_forest_contamination_{cont}_20241204")

# 避免使用默认名称
# ❌ 不推荐：run_name="run_001"
# ✅ 推荐：run_name="isolation_forest_contamination_0.025_baseline"
```

#### 2. 参数分组

```python
# 记录详细的参数信息
mlflow.log_param("model.n_estimators", 100)
mlflow.log_param("model.contamination", 0.025)
mlflow.log_param("data.feature_count", 5)
mlflow.log_param("preprocessing.scaler", "StandardScaler")
```

#### 3. 指标分类

```python
# 按类别记录指标
mlflow.log_metric("data.total_samples", n_total)
mlflow.log_metric("data.anomaly_count", n_anomalies)
mlflow.log_metric("performance.anomaly_rate", anomaly_rate)
mlflow.log_metric("score.average", float(scores.mean()))
```

#### 4. 添加丰富的 Tags

```python
mlflow.set_tag("author", "your_name")
mlflow.set_tag("purpose", "baseline_experiment")
mlflow.set_tag("dataset.version", "v1.0")
mlflow.set_tag("environment", "docker_compose")
```

#### 5. 定期清理

```bash
# 清理旧的实验数据（保留最近 30 天）
# 使用 MLflow API 或手动清理
make mlflow-clean  # 完全清理
rm -rf mlruns/*     # 删除本地运行数据
```

### 🔍 故障排查

#### 问题 1：无法连接到 MLflow 服务器

```bash
# 检查 Docker 容器状态
docker compose ps

# 查看日志
docker compose logs mlflow

# 重启服务
make mlflow-stop
make mlflow-server
```

#### 问题 2：模型保存失败

```python
# 确保使用了 Pipeline 包装
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', scaler),
    ('model', model)
])

mlflow.sklearn.log_model(pipeline, "model")
```

#### 问题 3：中文乱码

```python
# 在 matplotlib 配置中添加
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
plt.rcParams['axes.unicode_minus'] = False
```

### 📚 扩展阅读

- [MLflow 官方文档](https://www.mlflow.org/docs/latest/index.html)
- [MLflow 追踪（Tracking）](https://www.mlflow.org/docs/latest/tracking.html)
- [MLflow 模型（Models）](https://www.mlflow.org/docs/latest/models.html)
- [Isolation Forest 论文](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)

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
