.PHONY: all data run bailian deps clean help

all: data run

data:
	@echo "============================================================"
	@echo "Lab 7: 生成告警数据和运维手册"
	@echo "============================================================"
	python3 generate_data.py

run:
	@echo "============================================================"
	@echo "Lab 7: 运行 LLM Agent 智能诊断（模拟模式）"
	@echo "============================================================"
	python3 main.py

bailian: 
	@echo "============================================================"
	@echo "Lab 7: 运行阿里云百炼 LLM 智能诊断"
	@echo "============================================================"
	@echo "提示：请确保已设置 DASHSCOPE_API_KEY 环境变量"
	@echo "运行命令：export DASHSCOPE_API_KEY=sk-your-api-key"
	@echo "============================================================"
	python3 main_bailian.py

deps:
	@echo "============================================================"
	@echo "安装阿里云百炼依赖"
	@echo "============================================================"
	uv pip install dashscope
	@echo "✓ 依赖安装完成"

clean:
	@echo "清理生成的文件..."
	rm -rf alert_data/
	rm -rf runbook_templates/
	rm -f llm_diagnosis_*.md
	@echo "✓ 清理完成"

help:
	@echo "Lab 7: LLM Agent 自主运维实战"
	@echo ""
	@echo "可用目标:"
	@echo "  make all       - 执行所有步骤（生成数据 + 运行诊断）"
	@echo "  make data      - 生成告警数据和运维手册"
	@echo "  make run       - 运行 LLM Agent 诊断（模拟模式）"
	@echo "  make bailian   - 运行阿里云百炼 LLM 诊断（需配置 API Key）"
	@echo "  make deps      - 安装阿里云百炼依赖 (dashscope)"
	@echo "  make clean     - 删除生成的文件"
	@echo "  make help      - 显示帮助信息"
	@echo ""
	@echo "快速开始:"
	@echo "  1. make data                    # 生成测试数据"
	@echo "  2. export DASHSCOPE_API_KEY=xxx # 配置阿里云百炼 API Key"
	@echo "  3. make bailian                 # 运行真实的 LLM 诊断"
	@echo ""
	@echo "使用说明:"
	@echo "  - 模拟模式：make run (使用 MockLLMProvider，无需 API Key)"
	@echo "  - 真实模式：make bailian (使用阿里云百炼，需要 API Key)"
