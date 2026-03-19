# AIOps 培训 - 动手实验目录

本目录包含所有课程的动手实验代码和指导文档。

## 📚 实验列表

### Lab 1: 3-Sigma 原则检测 CPU/内存异常
**目录**: `lab1_3sigma_anomaly_detection/`

**文件结构**:
- `README.md` - 快速开始指南
- `lab_guide.md` - 详细实验指导
- `generate_data.py` - 数据生成脚本
- `main.py` - 主程序：异常检测与可视化

**内容**:
- ✅ 理解 3-Sigma 原则的基本原理
- ✅ 使用 Python 实现统计异常检测
- ✅ 可视化异常检测结果
- ✅ 对比不同 Sigma 阈值的效果
- ✅ 滑动窗口 3-Sigma 检测方法

**技术栈**: Python, NumPy, Pandas, Matplotlib

**预计时间**: 45-60 分钟

**快速开始**:
```bash
cd lab1_3sigma_anomaly_detection
python generate_data.py
python main.py
```

---

## 🔧 环境准备

### 基础依赖
```bash
pip install numpy pandas matplotlib seaborn scipy
```

### 可选依赖（后续实验）
```bash
# 机器学习方法
pip install scikit-learn xgboost

# 深度学习方法
pip install torch tensorflow

# 时序分析
pip install statsmodels prophet

# LLM 相关
pip install langchain chromadb openai
```

---

## 📝 使用说明

1. **按顺序完成实验**: 每个实验都建立在前置知识的基础上
2. **先运行代码**: 确保理解每段代码的作用
3. **完成扩展练习**: 加深对知识点的理解
4. **记录实验结果**: 保存关键图表和检测指标

---

## 🎯 学习目标

完成所有实验后，你将能够：

- ✅ 使用统计方法进行异常检测
- ✅ 应用机器学习算法识别异常模式
- ✅ 构建基于 LLM 的智能分析系统
- ✅ 设计和实施根因分析方案
- ✅ 开发自动化告警处理系统

---

## 📊 数据集

每个实验会提供：
- 模拟数据生成代码
- 真实场景数据样例
- 脱敏的生产环境数据

---

## 💡 提示

- 所有代码都经过测试，可以直接运行
- 实验结果图建议保存到本地用于复习
- 遇到问题可以先查看代码注释
- 欢迎提出改进建议和优化方案

---

## 📅 持续更新

更多实验正在添加中：
- Lab 2: Isolation Forest 多维异常检测 (Coming Soon)
- Lab 3: LSTM 自动编码器时序异常检测 (Coming Soon)
- Lab 4: 基于 RAG 的故障知识问答系统 (Coming Soon)
- Lab 5: LLM Agent 自主运维实战 (Coming Soon)
