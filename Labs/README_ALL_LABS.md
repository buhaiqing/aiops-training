# AIOps 动手实验课程体系

欢迎来到 AI 运维（AIOps）动手实验课程体系！本系列实验涵盖从传统统计方法到最新 LLM 应用的完整 AIOps 技术栈。

---

## 📚 实验列表

### 🔹 模块 1：基础异常检测

#### **Lab 1: 3-Sigma 原则检测 CPU/内存异常**
- **难度**: ⭐⭐☆☆☆
- **预计时间**: 45-60 分钟
- **核心内容**: 
  - 3-Sigma 统计原理
  - 单变量异常检测
  - 滑动窗口技术
  - 数据可视化
- **技术栈**: NumPy, Pandas, Matplotlib
- **目录**: [`lab1_3sigma_anomaly_detection/`](./lab1_3sigma_anomaly_detection/)
- **快速开始**:
  ```bash
  cd lab1_3sigma_anomaly_detection
  make all
  ```
- **实验目标** 🎯:
  - ✅ 理解 3-Sigma 原则的统计学原理和应用场景
  - ✅ 掌握基于均值和标准差的异常检测方法
  - ✅ 学会计算动态上下界并识别异常点
  - ✅ 能够使用滑动窗口处理非平稳序列
  - ✅ 掌握异常检测结果的可视化与报告生成

---

#### **Lab 2: Isolation Forest 检测多维指标异常**
- **难度**: ⭐⭐⭐☆☆
- **预计时间**: 60-75 分钟
- **核心内容**:
  - Isolation Forest 算法原理
  - 多维特征联合检测
  - 无监督学习
  - PCA 降维可视化
- **技术栈**: scikit-learn, NumPy, Pandas, Matplotlib
- **目录**: [`lab2_isolation_forest/`](./lab2_isolation_forest/)
- **快速开始**:
  ```bash
  cd lab2_isolation_forest
  make all
  ```
- **实验目标** 🎯:
  - ✅ 理解 Isolation Forest 的"孤立"思想和算法原理
  - ✅ 掌握使用 scikit-learn 实现 Isolation Forest 模型
  - ✅ 学会对 CPU、内存、磁盘等多维指标进行联合异常检测
  - ✅ 掌握 contamination 参数调优方法
  - ✅ 能够使用 PCA 降维可视化高维异常分布
  - ✅ 理解多维检测相比单变量检测的优势

---

### 🔹 模块 2：深度学习与高级方法

#### **Lab 3: LSTM 自动编码器时序异常检测**
- **难度**: ⭐⭐⭐⭐☆
- **预计时间**: 90-120 分钟
- **核心内容**:
  - LSTM 网络架构
  - 自动编码器原理
  - 时序数据建模
  - 重构误差分析
- **技术栈**: PyTorch, scikit-learn
- **目录**: [`lab3_lstm_autoencoder/`](./lab3_lstm_autoencoder/)
- **快速开始**:
  ```bash
  cd lab3_lstm_autoencoder
  make all
  ```
- **实验目标** 🎯:
  - ✅ 理解 LSTM 网络的门控机制和长期依赖捕捉能力
  - ✅ 掌握自动编码器的编码器 - 解码器架构设计
  - ✅ 学会基于重构误差的无监督异常检测方法
  - ✅ 掌握时序数据的滑动窗口预处理技术
  - ✅ 能够调优深度学习模型的超参数（sequence_length、hidden_size 等）
  - ✅ 理解深度学习模型在复杂时序模式识别中的优势

---

#### **Lab 4: Prophet 时序预测与异常检测**
- **难度**: ⭐⭐⭐☆☆
- **预计时间**: 60-90 分钟
- **核心内容**:
  - Prophet 模型原理
  - 趋势与季节性分解
  - 节假日效应处理
  - 基于预测残差的异常检测
- **技术栈**: Prophet, Pandas, Matplotlib
- **目录**: [`lab4_prophet_forecast/`](./lab4_prophet_forecast/)
- **快速开始**:
  ```bash
  cd lab4_prophet_forecast
  make all
  ```
- **实验目标** 🎯:
  - ✅ 掌握 Prophet 时序分解方法（趋势 + 季节 + 节假日）
  - ✅ 学会使用置信区间进行异常判定
  - ✅ 理解预测残差分析与 Z-Score 应用
  - ✅ 能够对比 Prophet vs LSTM 的适用场景

---

#### **Lab 5: One-Class SVM 未知故障模式识别**
- **难度**: ⭐⭐⭐⭐☆
- **预计时间**: 75-90 分钟
- **核心内容**:
  - 支持向量机理论
  - 核函数技巧
  - 边界检测方法
  - 小样本异常检测
- **技术栈**: scikit-learn, CVXOPT
- **目录**: [`lab5_ocsvm_anomaly_detection/`](./lab5_ocsvm_anomaly_detection/)
- **状态**: 🚧 开发中...
- **实验目标** 🎯:
  - ✅ 理解 One-Class SVM 的边界检测思想
  - ✅ 掌握核函数（RBF、Linear）的选择策略
  - ✅ 学会处理小样本/不平衡数据场景
  - ✅ 能够应用于未知故障类型的识别

---

### 🔹 模块 3：LLM 与智能运维

#### **Lab 6: 基于 RAG 的故障知识问答系统**
- **难度**: ⭐⭐⭐⭐⭐
- **预计时间**: 120-150 分钟
- **核心内容**:
  - RAG 检索增强生成
  - 向量数据库使用
  - Agno 框架
  - 知识库构建
- **技术栈**: LanceDB, OpenAI API/Qwen, sentence-transformers, FAISS
- **目录**: [`lab6_rag_knowledge_qa/`](./lab6_rag_knowledge_qa/)
- **快速开始**:
  ```bash
  cd lab6_rag_knowledge_qa
  make all
  ```
- **实验目标** 🎯:
  - ✅ 理解 RAG 架构和检索增强生成原理
  - ✅ 掌握文本嵌入（Embedding）技术
  - ✅ 学会使用 FAISS 进行向量相似度搜索
  - ✅ 能够构建基于向量检索的智能问答系统

---

#### **Lab 7: LLM Agent 自主运维实战** ✅
- **难度**: ⭐⭐⭐⭐⭐
- **预计时间**: 90-120 分钟
- **核心内容**:
  - 多源告警数据融合
  - 智能关联分析
  - 根因推断（RCA）
  - 处置方案生成
- **技术栈**: Python 标准库、规则引擎、LLM 模拟
- **目录**: [`lab7_llm_agent_ops/`](./lab7_llm_agent_ops/)
- **实验目标** 🎯:
  - ✅ 理解 AIOps 的核心价值和应用场景
  - ✅ 掌握告警关联分析的基本方法
  - ✅ 学会设计智能运维系统的架构
  - ✅ 了解 LLM 在运维领域的落地方式
- **状态**: ✅ 已完成

---

#### **Lab 8: ChatOps 集成 - 钉钉/企微机器人**
- **难度**: ⭐⭐⭐⭐☆
- **预计时间**: 90-120 分钟
- **核心内容**:
  - Webhook 集成
  - 自然语言告警摘要
  - 交互式诊断
  - 自动化预案执行
- **技术栈**: FastAPI, LLM API, 钉钉/企微 SDK
- **目录**: [`lab8_chatops_integration/`](./lab8_chatops_integration/)
- **状态**: 🚧 规划中...
- **实验目标** 🎯:
  - ✅ 掌握企业 IM 机器人的 Webhook 接入方法
  - ✅ 学会使用 LLM 生成自然语言告警摘要
  - ✅ 能够设计交互式故障诊断对话流程
  - ✅ 了解 ChatOps 在运维协作中的应用价值

---

## 🎯 学习路径建议

### 入门级（运维新手）
```
Lab 1 → Lab 2 → Lab 3 → Lab 4
```
掌握基础的统计和机器学习方法，理解异常检测的核心思想。

### 进阶级（有一定经验）
```
Lab 2 → Lab 3 → Lab 4 → Lab 5 → Lab 6
```
深入学习深度学习和 LLM 应用，构建完整的智能检测能力。

### 专家级（追求前沿）
```
Lab 5 → Lab 6 → Lab 7
```
掌握最新的 LLM Agent 技术，实现自主运维和 ChatOps。

---

## 🛠️ 环境准备

### 统一要求
- **Python**: 3.10+ （推荐 3.10）
- **包管理**: uv（超快的 Python 包管理工具）
- **操作系统**: macOS / Linux / Windows (WSL)

### 安装 uv
```bash
# 方法 1: 使用 pip
pip install uv

# 方法 2: 使用官方脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 通用命令
每个 Lab 都支持以下命令：
```bash
make venv     # 创建虚拟环境
make deps     # 安装依赖
make data     # 生成数据
make run      # 运行实验
make test     # 测试环境
make clean    # 清理文件
make help     # 查看帮助
```

---

## 📊 实验对比

| Lab | 方法类型 | 数据维度 | 是否需要标注 | 适用场景 |
|-----|---------|---------|-------------|---------|
| Lab 1 | 统计方法 | 单变量 | ❌ | 稳定指标的简单异常 |
| Lab 2 | 机器学习 | 多变量 | ❌ | 多维联合异常检测 |
| Lab 3 | 深度学习 | 时序数据 | ❌ | 复杂时序模式识别 |
| Lab 4 | 时序预测 | 单变量 + 时间 | ❌ | 趋势预测与残差异常 |
| Lab 5 | 机器学习 | 多变量 | ❌ | 小样本未知故障 |
| Lab 6 | LLM+RAG | 文本 + 数据 | ✅ | 知识问答与诊断 |
| Lab 7 | LLM Agent | 多模态 | ✅ | 自主运维决策 |
| Lab 8 | ChatOps | 对话交互 | ✅ | 人机协作应急 |

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

### 5. 应用到实际
思考如何将所学应用到真实生产环境。

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

