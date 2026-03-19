# Lab 1: 3-Sigma 原则检测 CPU/内存异常
# Makefile - 自动化实验流程

.PHONY: help setup venv deps data run clean test all

# 默认目标
all: venv deps data run

# 显示帮助信息
help:
	@echo "========================================"
	@echo "Lab 1: 3-Sigma 原则检测 CPU/内存异常"
	@echo "========================================"
	@echo ""
	@echo "可用命令:"
	@echo "  make venv    - 使用 uv 创建虚拟环境"
	@echo "  make deps    - 安装依赖包到虚拟环境"
	@echo "  make data    - 生成模拟数据"
	@echo "  make run     - 运行异常检测主程序"
	@echo "  make clean   - 清理生成的文件"
	@echo "  make test    - 测试环境配置"
	@echo "  make all     - 完整流程 (venv + deps + data + run)"
	@echo "  make help    - 显示此帮助信息"
	@echo ""
	@echo "快速开始:"
	@echo "  make all     # 一键完成所有步骤"
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
	@echo "开始运行 3-Sigma 异常检测..."
	@echo "========================================"
	@echo ""
	python3 main.py
	@echo ""
	@echo "========================================"
	@echo "实验完成！"
	@echo "========================================"
	@echo ""
	@echo "查看结果:"
	@echo "  - 控制台输出：异常检测结果和报告"
	@echo "  - 图片文件：3sigma_detection_result.png"
	@echo ""

# 清理生成的文件
clean:
	@echo "正在清理生成的文件..."
	rm -f cpu_memory_data.csv
	rm -f 3sigma_detection_result.png
	rm -rf __pycache__
	rm -f *.pyc
	@echo "✓ 清理完成"
	@echo ""
	@echo "提示：如需删除虚拟环境，运行: rm -rf .venv"

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
	@echo ""
	@echo "环境测试完成！"
