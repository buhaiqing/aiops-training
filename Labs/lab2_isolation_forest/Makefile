# Lab 2: Isolation Forest 检测多维指标异常
# Makefile - 自动化实验流程（含 MLflow 集成）

.PHONY: help setup venv deps data run mlflow-server mlflow-stop mlflow-clean mlflow-local mlflow-local-stop clean test all

# 默认目标
all: venv deps data run

# 显示帮助信息
help:
	@echo "========================================"
	@echo "Lab 2: Isolation Forest 检测多维指标异常"
	@echo "========================================"
	@echo ""
	@echo "可用命令:"
	@echo "  make venv          - 使用 uv 创建虚拟环境"
	@echo "  make deps          - 安装依赖包到虚拟环境"
	@echo "  make data          - 生成模拟数据"
	@echo "  make run           - 运行异常检测主程序"
	@echo "  make clean         - 清理生成的文件"
	@echo "  make test          - 测试环境配置"
	@echo "  make all           - 完整流程 (venv + deps + data + run)"
	@echo "  make help          - 显示此帮助信息"
	@echo ""
	@echo "MLflow 相关命令:"
	@echo "  make mlflow-server     - 启动 MLflow Docker 服务（PostgreSQL + MinIO）"
	@echo "  make mlflow-stop       - 停止 MLflow Docker 服务"
	@echo "  make mlflow-clean      - 清理 MLflow Docker 服务和数据"
	@echo "  make mlflow-local      - 使用本地 SQLite 启动 MLflow 服务器（无需 Docker）"
	@echo "  make mlflow-local-stop - 停止本地 MLflow 服务器"
	@echo ""
	@echo "快速开始:"
	@echo "  make all            # 一键完成所有步骤（不含 MLflow 服务器）"
	@echo "  make mlflow-server  # 启动 MLflow 跟踪服务器"
	@echo "  source .venv/bin/activate && make run  # 运行实验"
	@echo ""
	@echo "MLflow UI 访问:"
	@echo "  本地模式：http://localhost:5000"
	@echo "  Docker 模式：http://localhost:5000"
	@echo "  MinIO 控制台：http://localhost:9001"
	@echo ""

# 使用 uv 创建虚拟环境
venv:
	@echo "正在使用 uv 创建虚拟环境..."
	@command -v uv >/dev/null 2>&1 || { echo "错误：uv 未安装，请先安装 uv: pip install uv"; exit 1; }
	uv venv
	@echo "✓ 虚拟环境创建完成 (.venv)"
	@echo ""
	@echo "提示：激活虚拟环境后运行实验"
	@echo "  macOS/Linux: source .venv/bin/activate"
	@echo "  Windows: .venv\\Scripts\\activate"
	@echo ""

# 安装依赖
deps:
	@echo "正在安装依赖包..."
	@command -v uv >/dev/null 2>&1 || { echo "错误：uv 未安装，请先安装 uv: pip install uv"; exit 1; }
	uv pip install -r requirements.txt
	@echo "✓ 依赖包安装完成"
	@echo ""
	@echo "提示：也可以使用 pyproject.toml 安装"
	@echo "  uv pip install -e .[dev]"
	@echo ""

# 生成数据
data:
	@echo "正在生成模拟数据..."
	python3 generate_data.py
	@echo ""

# 运行主程序
run:
	@echo "========================================"
	@echo "开始运行 Isolation Forest 异常检测..."
	@echo "========================================"
	@echo ""
	@python3 main.py
	@echo ""
	@echo "========================================"
	@echo "实验完成！"
	@echo "========================================"
	@echo ""
	@echo "查看结果:"
	@echo "  - 控制台输出：异常检测结果和报告"
	@echo "  - 图片文件：isolation_forest_results.png"
	@echo "  - MLflow 追踪：运行 'make mlflow-server' 后访问 http://localhost:5000"
	@echo ""

# 清理生成的文件
clean:
	@echo "正在清理生成的文件..."
	rm -f multidim_monitoring_data.csv
	rm -f isolation_forest_results.png
	rm -f feature_statistics.csv
	rm -f mlflow.db
	rm -rf __pycache__
	rm -rf mlruns
	rm -f *.pyc
	@echo "✓ 清理完成"
	@echo ""
	@echo "提示：如需删除虚拟环境，运行：rm -rf .venv"
	@echo "      如需删除 MLflow Docker 数据，运行：make mlflow-clean"
	@echo ""

# 测试环境配置
test:
	@echo "正在测试环境配置..."
	@echo ""
	@python3 -c "import sys; print(f'Python 版本：{sys.version}')"
	@echo ""
	@python3 -c "import numpy; print(f'NumPy 版本：{numpy.__version__}')" 2>/dev/null || echo "NumPy: 未安装"
	@python3 -c "import pandas; print(f'Pandas 版本：{pandas.__version__}')" 2>/dev/null || echo "Pandas: 未安装"
	@python3 -c "import matplotlib; print(f'Matplotlib 版本：{matplotlib.__version__}')" 2>/dev/null || echo "Matplotlib: 未安装"
	@python3 -c "import seaborn; print(f'Seaborn 版本：{seaborn.__version__}')" 2>/dev/null || echo "Seaborn: 未安装"
	@python3 -c "import sklearn; print(f'Scikit-learn 版本：{sklearn.__version__}')" 2>/dev/null || echo "Scikit-learn: 未安装"
	@python3 -c "import mlflow; print(f'MLflow 版本：{mlflow.__version__}')" 2>/dev/null || echo "MLflow: 未安装"
	@echo ""
	@echo "环境测试完成！"
	@echo ""

# ========================================
# MLflow 相关命令
# ========================================

# 启动 MLflow Docker 服务
mlflow-server:
	@echo "========================================"
	@echo "启动 MLflow 跟踪服务器..."
	@echo "========================================"
	@echo ""
	@command -v docker >/dev/null 2>&1 || { echo "错误：Docker 未安装，请先安装 Docker Desktop"; exit 1; }
	@docker compose ps 2>/dev/null | grep -q "mlflow-tracking-server" && { echo "⚠️  MLflow 服务已在运行"; exit 0; }
	@echo "正在启动 Docker Compose 服务..."
	@docker compose up -d
	@echo ""
	@echo "等待服务启动..."
	@sleep 15
	@echo ""
	@echo "✓ MLflow 服务已启动！"
	@echo ""
	@echo "访问地址:"
	@echo "  - MLflow UI: http://localhost:5000"
	@echo "  - MinIO 控制台：http://localhost:9001 (用户名/密码：minioadmin/minioadmin)"
	@echo "  - PostgreSQL: localhost:5432 (数据库：mlflow_db, 用户：mlflow, 密码：mlflow_password)"
	@echo ""
	@echo "查看日志:"
	@echo "  docker compose logs -f mlflow"
	@echo ""
	@echo "停止服务:"
	@echo "  make mlflow-stop"
	@echo ""

# 停止 MLflow Docker 服务
mlflow-stop:
	@echo "========================================"
	@echo "停止 MLflow 跟踪服务器..."
	@echo "========================================"
	@echo ""
	@docker compose stop
	@echo ""
	@echo "✓ MLflow 服务已停止"
	@echo ""
	@echo "提示：如需删除容器，运行：make mlflow-clean"
	@echo ""

# 清理 MLflow Docker 服务和数据
mlflow-clean:
	@echo "========================================"
	@echo "清理 MLflow Docker 服务和数据..."
	@echo "========================================"
	@echo ""
	@docker compose down -v
	@echo ""
	@echo "✓ MLflow 服务和数据已清理"
	@echo ""
	@echo "警告：此操作会删除所有 MLflow 实验数据和模型！"
	@echo ""

# 使用本地 SQLite 运行 MLflow 服务器（无需 Docker）
mlflow-local:
	@echo "========================================"
	@echo "使用本地 SQLite 启动 MLflow 服务器..."
	@echo "========================================"
	@echo ""
	@command -v mlflow >/dev/null 2>&1 || { echo "错误：MLflow 未安装，请先运行：pip install mlflow"; exit 1; }
	@mkdir -p ./mlruns
	@mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns &
	@echo ""
	@echo "✓ MLflow 本地服务器已启动（PID: $$!）"
	@echo ""
	@echo "访问地址：http://localhost:5000"
	@echo ""
	@echo "停止服务：make mlflow-local-stop"
	@echo "或：pkill -f 'mlflow server'"
	@echo ""
	@echo "查看进程：ps aux | grep 'mlflow server'"
	@echo ""

# 停止本地 MLflow 服务器
mlflow-local-stop:
	@echo "========================================"
	@echo "停止本地 MLflow 服务器..."
	@echo "========================================"
	@echo ""
	@pkill -f 'mlflow server' || { echo "ℹ️  MLflow 服务器未运行"; exit 0; }
	@echo ""
	@echo "✓ MLflow 本地服务器已停止"
	@echo ""
	@echo "提示：如需删除数据库文件，运行：rm mlflow.db"
	@echo "      如需删除 artifact 数据，运行：rm -rf mlruns/"
	@echo ""
