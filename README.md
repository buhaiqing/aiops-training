# AI 运维（AIOps）培训体系

<div align="center">


**专注于培养具备实际 AI 运维能力的专业人才**

[📚 课程模块](#-课程模块) • [🚀 快速开始](#-快速开始) • [📋 学习路径](#-学习路径) • [💡 最佳实践](#-最佳实践)

</div>

---

## 🎯 项目简介

本项目是一套完整的 **AI 运维（AIOps）动手实验课程体系**，专注于培养具备实际 AI 运维能力的专业人才。课程内容涵盖从传统统计方法到最新 LLM 应用的完整技术栈。

### ✨ 核心特色

#### 🚀 完全实战导向
- **不讲理论推导**：聚焦代码实现和实际应用
- **70% 时间实操**：每个知识点都有对应的动手实验
- **真实场景还原**：使用脱敏生产数据，非玩具数据集

#### 🤖 LLM 深度整合
- **RAG 知识库**：构建智能问答系统
- **Agent 自主运维**：实现自动化故障诊断与修复
- **ChatOps 集成**：通过对话机器人执行应急操作

#### 📦 开箱即用
- **uv 包管理**：超快的 Python 环境管理
- **Makefile 自动化**：一键完成所有步骤
- **Docker 预配置**：统一实验环境
- **MLflow 集成**：专业的实验追踪和模型管理

---

## 📚 课程模块

### ✅ 已完成 Lab

#### Lab 1: 3-Sigma 原则检测 CPU/内存异常
- **技术**: 统计方法、单变量分析
- **难度**: ⭐⭐☆☆☆
- **时间**: 45-60 分钟
- **目录**: [`Labs/lab1_3sigma_anomaly_detection/`](./Labs/lab1_3sigma_anomaly_detection/)
- **特点**: 零基础入门，理解异常检测的基本思想

#### ✅ Lab 2: Isolation Forest 检测多维指标异常
- **技术**: 机器学习、多维特征联合检测 + **MLflow 实验追踪**
- **难度**: ⭐⭐⭐☆☆
- **时间**: 60-75 分钟
- **目录**: [`Labs/lab2_isolation_forest/`](./Labs/lab2_isolation_forest/)
- **特点**: 
  - 理解 Isolation Forest 算法原理
  - 掌握多维异常检测方法
  - **学习使用 MLflow 进行实验管理和模型追踪**

#### ✅ Lab 3: LSTM 自动编码器时序异常检测
- **技术**: 深度学习、LSTM、自动编码器
- **难度**: ⭐⭐⭐⭐☆
- **时间**: 90-120 分钟
- **目录**: [`Labs/lab3_lstm_autoencoder/`](./Labs/lab3_lstm_autoencoder/)
- **特点**: 处理时序数据的深度学习方法

#### ✅ Lab 4: Prophet 时序预测与异常检测
- **技术**: Facebook Prophet、时序分解
- **难度**: ⭐⭐⭐☆☆
- **时间**: 75-90 分钟
- **目录**: [`Labs/lab4_prophet_forecast/`](./Labs/lab4_prophet_forecast/)
- **特点**: 工业级时序预测工具

#### ✅ Lab 6: 基于 RAG 的故障知识问答系统
- **技术**: LangChain, Chroma/Milvus, LLM
- **难度**: ⭐⭐⭐⭐⭐
- **时间**: 120-150 分钟
- **目录**: [`Labs/lab6_rag_knowledge_qa/`](./Labs/lab6_rag_knowledge_qa/)
- **特点**: 构建企业级智能问答系统

#### ✅ Lab 7: LLM Agent 自主运维实战
- **技术**: AutoGen/CrewAI, Function Calling, 阿里云百炼
- **难度**: ⭐⭐⭐⭐⭐
- **时间**: 150-180 分钟
- **目录**: [`Labs/lab7_llm_agent_ops/`](./Labs/lab7_llm_agent_ops/)
- **特点**: 
  - 实现自主故障诊断 Agent
  - 集成阿里云百炼大模型
  - 支持多种运维插件

### 🚧 开发中 Lab

#### Lab 5: One-Class SVM 未知故障模式识别
- **技术**: 支持向量机、边界检测
- **难度**: ⭐⭐⭐⭐☆
- **时间**: 75-90 分钟
- **状态**: 规划中

#### Lab 8: ChatOps 集成 - 钉钉/企微机器人
- **技术**: Flask/FastAPI, Webhook, LLM API
- **难度**: ⭐⭐⭐⭐☆
- **时间**: 90-120 分钟
- **状态**: 规划中

---

## 🛠️ 快速开始

### 前置要求

1. **Python**: 3.10+ （推荐 3.10）
2. **操作系统**: macOS / Linux / Windows (WSL)
3. **包管理工具**: uv

### 安装 uv

```bash
# 方法 1: 使用 pip（推荐）
pip install uv

# 方法 2: 使用官方脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 运行第一个实验

```bash
# 进入 Lab 1 目录
cd Labs/lab1_3sigma_anomaly_detection

# 一键完成所有步骤
make all

# 或者分步执行
make venv     # 创建虚拟环境
make deps     # 安装依赖包
make data     # 生成模拟数据
make run      # 运行异常检测
```

### 体验 MLflow 实验追踪（Lab 2）

```bash
# 进入 Lab 2 目录
cd Labs/lab2_isolation_forest

# 方式 A: Docker Compose（推荐）
make mlflow-server    # 启动 MLflow 服务
sleep 15              # 等待服务就绪
python main.py        # 运行实验

# 方式 B: 本地 SQLite（无需 Docker）
make mlflow-local     # 启动本地 MLflow 服务器
python main.py        # 运行实验

# 访问 MLflow UI
# 浏览器打开 http://localhost:5000
```

---

## 📋 学习路径

### 入门级（运维新手）
```
Lab 1 → Lab 2 → Lab 3
```
掌握基础的统计和机器学习方法，理解异常检测的核心思想。

### 进阶级（有一定经验）
```
Lab 2 → Lab 3 → Lab 4 → Lab 6
```
深入学习深度学习和 LLM 应用，构建完整的智能检测能力。

### 专家级（追求前沿）
```
Lab 6 → Lab 7
```
掌握最新的 LLM Agent 技术，实现自主运维和 ChatOps。

---

## 📊 技术栈总览

| 类别 | 技术选型 |
|------|---------|
| **编程语言** | Python 3.10+ |
| **数据处理** | NumPy, Pandas |
| **可视化** | Matplotlib, Seaborn |
| **机器学习** | scikit-learn, XGBoost |
| **深度学习** | PyTorch / TensorFlow |
| **时序分析** | Prophet, LSTM |
| **包管理** | uv, pip |
| **环境管理** | venv, Docker |
| **LLM 框架** | LangChain, LlamaIndex |
| **向量数据库** | Chroma, Milvus |
| **LLM 模型** | Qwen, Llama3, ChatGLM |
| **云服务** | 阿里云百炼 |
| **Agent 框架** | Agno |
| **实验追踪** | MLflow |
| **部署** | FastAPI, Docker |

---

## 💡 最佳实践

### 1. 循序渐进
从简单的统计方法开始，逐步过渡到复杂的深度学习模型。

### 2. 理解原理
不要只运行代码，要理解每个算法背后的思想。

### 3. 动手实践
修改参数、添加特征、尝试不同的数据集。

### 4. 对比分析
比较不同方法的优缺点，理解适用场景。

### 5. 使用工具
善用 MLflow 等工具管理实验和模型。

### 6. 应用到实际
思考如何将所学应用到真实生产环境。

---

## 📁 项目结构

```
aiops-training/
├── README.md                      # 本文件
├── README_PROJECT.md              # 项目详细说明
├── traning_plan.md                # 培训方案
├── customer_interview_outline.md  # 需求文档
├── training_proposal_template.md  # 培训方案模板
├── Labs/                          # 动手实验目录
│   ├── README_ALL_LABS.md         # 所有 Lab 总览
│   ├── COURSE_OVERVIEW.md         # 课程概览
│   ├── LEARNING_GUIDE.md          # 学习指南
│   ├── lab1_3sigma_anomaly_detection/
│   ├── lab2_isolation_forest/     # ✨ 含 MLflow 集成
│   ├── lab3_lstm_autoencoder/
│   ├── lab4_prophet_forecast/
│   ├── lab6_rag_knowledge_qa/
│   └── lab7_llm_agent_ops/
└── ...
```

---

## 🎓 培训方案

### 方案 A：集中培训（2 天）

```
Day 1 (全天):
  上午 (3h): Lab 1 - 3-Sigma 原则
  下午 (4h): Lab 2 - Isolation Forest + MLflow

Day 2 (全天):
  上午 (3h): Lab 3 - LSTM 自动编码器
  下午 (4h): LLM 应用演示 (Lab 6/7)
```

### 方案 B：周末班（4 周）

```
每周六日上课，每天 6 小时
周末 1: Lab 1 + Lab 2 (基础方法)
周末 2: Lab 3 + Lab 4 (深度学习方法)
周末 3: Lab 6 + Lab 7 (LLM 应用)
周末 4: 综合演练 + 考核
```

详细培训方案请查看：[`traning_plan.md`](./traning_plan.md)

---

## 🤝 贡献指南

欢迎提出改进建议、报告问题或贡献新的实验！

### 提交 Issue
遇到问题请提交 Issue，描述清楚：
- 复现步骤
- 预期行为
- 实际行为
- 环境信息

### 提交 PR
改进了代码或文档？欢迎提交 Pull Request！

---

## 📧 联系方式

- **项目主页**: [GitHub Repository](https://github.com/aiops-training)
- **问题反馈**: [Issue Tracker](https://github.com/aiops-training/issues)
- **讨论区**: [Discussions](https://github.com/aiops-training/discussions)

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢所有为 AIOps 社区做出贡献的开发者！

特别感谢：
- 提供真实场景数据的合作伙伴
- 参与课程设计和评审的专家团队
- 所有贡献代码和文档的志愿者

---

<div align="center">

**Happy Coding! 🚀**

[返回顶部 ↑](#aiops 培训体系)

</div>
