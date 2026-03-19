.PHONY: all data run clean help

all: data run

data:
	@echo "============================================================"
	@echo "Lab 7: 生成告警数据和运维手册"
	@echo "============================================================"
	python3 generate_data.py

run:
	@echo "============================================================"
	@echo "Lab 7: 运行 LLM Agent 智能诊断"
	@echo "============================================================"
	python3 main.py

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
	@echo "  make all    - 执行所有步骤（生成数据 + 运行诊断）"
	@echo "  make data   - 生成告警数据和运维手册"
	@echo "  make run    - 运行 LLM Agent 诊断"
	@echo "  make clean  - 删除生成的文件"
	@echo "  make help   - 显示帮助信息"
