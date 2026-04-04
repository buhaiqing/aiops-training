# MLflow 集成快速开始指南

## 📋 概述

本实验已完整集成 MLflow，用于实验追踪、模型管理和结果可视化。

## 🚀 5 分钟快速开始

### 步骤 1: 安装依赖

```bash
# 使用 uv（推荐）
pip install uv
uv venv
source .venv/bin/activate  # macOS/Linux
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 步骤 2: 启动 MLflow 服务

**方式 A: Docker Compose（推荐）**
```bash
make mlflow-server
```

**方式 B: 本地 SQLite（无需 Docker）**
```bash
make mlflow-local
```

### 步骤 3: 运行实验

```bash
# 生成数据
python generate_data.py

# 运行主实验（自动记录到 MLflow）
python main.py

# 或运行参数对比实验
python experiment_comparison.py
```

### 步骤 4: 查看结果

访问 MLflow UI：**http://localhost:5000**

## 📂 文件说明

### 核心文件
- `main.py` - 主程序（含 MLflow 集成）
- `mlflow_config.py` - MLflow 配置模块
- `experiment_comparison.py` - 参数对比实验脚本
- `load_model_from_mlflow.py` - 模型加载工具

### Docker 相关文件
- `docker-compose.yml` - MLflow 服务编排
- `init-db.sql` - PostgreSQL 初始化脚本

### Makefile 命令
```bash
make mlflow-server    # 启动 Docker 服务
make mlflow-stop      # 停止服务
make mlflow-clean     # 清理所有数据
make mlflow-local     # 本地 SQLite 模式
make run              # 运行主实验
make all              # 完整流程
```

## 🎯 MLflow 追踪内容

### 超参数（Parameters）
- `n_estimators`: 树的数量 (100)
- `contamination`: 异常点比例估计 (0.025)
- `max_samples`: 每棵树样本数 (auto)
- `random_state`: 随机种子 (42)

### 指标（Metrics）
- `total_samples`: 总样本数
- `detected_anomalies`: 检测到的异常数
- `anomaly_rate`: 异常率 (%)
- `avg_anomaly_score`: 平均异常分数
- `min_anomaly_score`: 最小异常分数
- `max_anomaly_score`: 最大异常分数

### 产物（Artifacts）
- `isolation_forest_model/` - 训练好的模型
- `visualizations/isolation_forest_results.png` - 结果可视化
- `data/feature_statistics.csv` - 特征统计

## 💡 常用场景

### 场景 1: 对比不同参数效果

```bash
# 运行参数对比实验
python experiment_comparison.py

# 在 MLflow UI 中勾选多个 Run 进行对比
```

### 场景 2: 加载已训练的模型

```bash
# 列出所有实验运行
python load_model_from_mlflow.py list

# 加载最新模型并预测
python load_model_from_mlflow.py load

# 对指定数据文件预测
python load_model_from_mlflow.py load new_data.csv
```

### 场景 3: 清理实验数据

```bash
# 清理 Docker 容器和数据
make mlflow-clean

# 仅清理本地运行数据
rm -rf mlruns/*
```

## 🔍 故障排查

### 问题：无法访问 MLflow UI

```bash
# 检查服务状态
docker compose ps

# 查看日志
docker compose logs mlflow

# 重启服务
make mlflow-stop
make mlflow-server
```

### 问题：模型保存失败

确保使用了 Pipeline 包装：
```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', scaler),
    ('model', model)
])
```

## 📚 更多信息

详细文档请查看 README.md 中的"MLflow 模型评估与实验追踪"章节。

## ⚠️ 注意事项

1. **Docker 资源**: Docker 模式需要至少 2GB 内存
2. **端口占用**: 确保端口 5000, 5432, 9000, 9001 未被占用
3. **数据持久化**: Docker 卷会持久化数据，使用 `make mlflow-clean` 完全清理
4. **生产环境**: 生产部署时请修改默认密码和安全配置

---

**快速参考卡片**

```bash
# 一键启动（推荐）
make mlflow-server && sleep 15 && python main.py

# 访问 MLflow UI
open http://localhost:5000  # macOS
xdg-open http://localhost:5000  # Linux

# 停止和清理
make mlflow-stop
make mlflow-clean
```
