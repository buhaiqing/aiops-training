# Lab 6: 基于 RAG 的故障知识问答系统

## 📁 目录结构

```
lab6_rag_knowledge_qa/
├── README.md                    # 本文件（快速指南）
├── lab_guide.md                 # 详细实验指导文档
├── generate_data.py             # 故障知识库生成脚本
├── main.py                      # RAG 问答主程序
├── Makefile                     # 自动化构建脚本
├── pyproject.toml               # Python 项目配置
├── requirements.txt             # Python 依赖列表
├── install_uv.sh                # uv 安装脚本
├── .gitignore                   # Git 忽略配置
└── knowledge_base/              # 生成的知识库目录（运行后产生）
    ├── FAULT-001_CPU.json       # CPU 故障文档
    ├── FAULT-002_内存.json      # 内存故障文档
    ├── ...                      # 其他故障文档
    └── all_documents.json       # 合并的知识库文件
```

---

## 🚀 快速开始

### 前置要求

**Python 版本**: Python 3.10+（推荐 3.10）

**安装 uv** (如果尚未安装):

```bash
pip install uv
```

### 方式一：使用 uv + Makefile（推荐）

```bash
# 一键完成所有步骤
make all

# 分步执行
make venv     # 创建虚拟环境
make deps     # 安装依赖包（包括 sentence-transformers、faiss-cpu）
make data     # 生成故障知识库文档
make run      # 启动 RAG 问答系统
```

### 方式二：手动执行

#### 1. 安装依赖

```bash
pip install sentence-transformers faiss-cpu numpy pandas matplotlib scikit-learn nltk tqdm
```

#### 2. 生成故障知识库

```bash
python3 generate_data.py
```

#### 3. 运行 RAG 问答系统

```bash
python3 main.py
```

---

## 🎯 学习目标

完成本实验后，你将能够：

- ✅ 理解 RAG（检索增强生成）的基本原理
- ✅ 掌握文本嵌入（Embedding）技术
- ✅ 学会使用 FAISS 进行向量相似度搜索
- ✅ 构建基于向量检索的问答系统
- ✅ 对比传统关键词搜索与语义检索的差异
- ✅ 应用 RAG 解决实际运维场景问题

---

## ⏱️ 预计时间

- **基础部分**: 90-120 分钟
- **扩展练习**: 45-60 分钟

---

## 📊 核心概念

### 什么是 RAG？

**RAG (Retrieval-Augmented Generation)** = 检索 + 生成

```
用户提问 → 检索相关知识 → 生成答案
   ↓           ↓              ↓
 Query    Knowledge Base   Answer
```

### 为什么需要 RAG？

| 方法 | 优点 | 缺点 |
|------|------|------|
| **纯 LLM** | 通用知识强 | 领域知识弱、可能幻觉 |
| **纯检索** | 准确可靠 | 灵活性差、难以综合 |
| **RAG** | 准确 + 灵活、可追溯 | 实现复杂度较高 |

### RAG 的关键组件

1. **文档编码器**：将知识文档转换为向量
2. **查询编码器**：将用户问题转换为向量
3. **相似度计算**：余弦相似度、内积等
4. **答案生成器**：基于检索结果生成回答

---

## 💡 实验流程

### Step 1: 准备知识库

```bash
python3 generate_data.py
```

生成 8 篇故障处理文档：
- CPU 使用率异常
- 内存泄漏问题
- 磁盘空间不足
- 网络延迟高
- 数据库连接池耗尽
- 应用响应慢
- 服务不可用
- 日志异常

### Step 2: 创建文档嵌入

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(documents)
```

**模型选择**:
- `paraphrase-multilingual-MiniLM-L12-v2`: 多语言、384 维、速度快
- `bge-large-zh`: 中文优化、精度高、速度较慢
- `m3e-base`: 中文语义理解好

### Step 3: 构建 FAISS 索引

```python
import faiss

# 创建索引
index = faiss.IndexFlatIP(dimension)  # 内积相似度

# 归一化向量（用于余弦相似度）
faiss.normalize_L2(embeddings)

# 添加到索引
index.add(embeddings)
```

### Step 4: 检索与生成

```python
# 用户提问
query = "CPU 使用率很高怎么办？"

# 转换为向量
query_embedding = model.encode([query])
faiss.normalize_L2(query_embedding)

# 检索最相关的文档
similarities, indices = index.search(query_embedding, top_k=3)

# 生成答案
answer = generate_answer(query, retrieved_docs)
```

---

## 🔧 运行模式

### 模式 1: 演示模式

查看预设问题的检索效果：

```bash
python3 main.py
# 选择选项：1
```

**示例输出**:
```
问题 1: CPU 使用率很高怎么办？
============================================================

✓ 检索到 2 篇相关文档:

[1] CPU 使用率持续高于 90%
    相似度：0.8523
    类别：CPU
    关键标签：CPU, 性能，监控

[2] 应用响应时间过长
    相似度：0.7234
    类别：性能
    关键标签：性能，响应时间，优化
```

### 模式 2: 交互模式

自由提问获取答案：

```bash
python3 main.py
# 选择选项：2

📝 请输入您的问题：内存泄漏如何处理？

🔍 正在检索知识库...

✓ 找到 1 篇相关文档:

[1] 内存泄漏导致 OOM 错误
    类别：内存 | 相似度：0.8934
    标签：内存，OOM, JVM, GC

是否查看详细答案？(y/n): y

============================================================
根据故障知识库的检索结果，针对您的问题：**内存泄漏如何处理？**

## 📋 相关知识

【相关知识 1】
标题：内存泄漏导致 OOM 错误
类别：内存
严重程度：紧急
内容：
故障现象：
- 内存使用率持续增长，不下降
- 频繁触发 Full GC
- 最终抛出 OutOfMemoryError
...

## 💡 建议处理步骤
...
```

### 模式 3: 批量测试

自动测试所有预设问题：

```bash
python3 main.py
# 选择选项：3
```

---

## 📈 性能指标

### 检索质量评估

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **召回率@K** | 前 K 个结果中包含正确答案的比例 | >90% |
| **MRR** | 第一个正确答案的平均排名 | >0.8 |
| **NDCG** | 排序质量（考虑相关性分级） | >0.85 |
| **响应时间** | 从提问到返回答案的时间 | <2 秒 |

### 影响性能的因素

1. **嵌入模型质量**
   - 语义理解能力
   - 领域适应性
   
2. **索引类型**
   - 精确搜索：IndexFlatIP（慢但准）
   - 近似搜索：IndexHNSW（快但有损）

3. **文档粒度**
   - 太粗：检索不精确
   - 太细：丢失上下文

---

## 🎯 实验任务

### 基础任务

#### 任务 1: 体验 RAG 问答
- 运行交互模式
- 提出至少 5 个不同的故障问题
- 记录检索结果的质量

#### 任务 2: 分析检索效果
- 对比不同问题的相似度分数
- 分析高相似度和低相似度的原因
- 思考如何改进

#### 任务 3: 调整参数
- 修改 `top_k` 值（3、5、10）
- 观察检索结果的变化
- 找到最优的 top_k

### 进阶任务

#### 任务 4: 添加新文档
在知识库中添加新的故障文档：

```python
new_doc = {
    "id": "FAULT-009",
    "title": "Kubernetes Pod 频繁重启",
    "category": "容器",
    "severity": "高",
    "content": "...",
    "tags": ["K8s", "Pod", "重启"]
}
```

#### 任务 5: 实现答案评分
让用户对答案评分，收集反馈：

```python
def rate_answer(question, answer, rating):
    """评分 1-5 星"""
    save_to_feedback_db({
        'question': question,
        'answer': answer,
        'rating': rating,
        'timestamp': datetime.now()
    })
```

#### 任务 6: 对比实验
对比不同嵌入模型的效果：

| 模型 | 平均相似度 | 用户满意度 | 响应时间 |
|------|-----------|-----------|---------|
| MiniLM | ? | ? | ? |
| BGE | ? | ? | ? |
| M3E | ? | ? | ? |

---

## 🔍 扩展阅读

### RAG 最佳实践

1. **文档预处理**
   - 分段处理（chunking）
   - 去除噪声
   - 添加元数据

2. **混合检索**
   - 语义检索 + 关键词检索
   - 加权融合结果

3. **重排序（Re-ranking）**
   - 初次检索：快速召回
   - 精细排序：提高质量

4. **缓存策略**
   - 缓存热门问题答案
   - 降低响应时间

### 生产环境考虑

1. **可扩展性**
   - 分布式索引
   - 负载均衡

2. **更新机制**
   - 增量更新索引
   - 版本管理

3. **监控告警**
   - 检索成功率
   - 响应时间
   - 用户满意度

---

## ❓ 常见问题

**Q: 为什么选择 FAISS 而不是其他向量数据库？**  
A: FAISS 是 Facebook 开源的高性能向量检索库，支持多种索引类型和相似度度量，适合学习和原型开发。生产环境可考虑 Milvus、Weaviate 等。

**Q: 如何处理中文语义理解？**  
A: 使用专门训练的中文嵌入模型，如 `bge-large-zh`、`m3e-base` 等。本实验使用的 multilingual-MiniLM 也支持中文。

**Q: 检索结果不准确怎么办？**  
A: 
1. 更换更好的嵌入模型
2. 调整文档分段策略
3. 使用混合检索（语义 + 关键词）
4. 添加重排序步骤

**Q: 如何评估 RAG 系统的质量？**  
A: 
1. 构建测试集（问题 + 标准答案）
2. 计算召回率和准确率
3. 收集用户反馈评分
4. A/B 测试不同配置

---

## 📝 下一步

完成 Lab 6 后，继续学习：
- Lab 7: LLM Agent 自主运维实战
- Lab 8: ChatOps 集成 - 钉钉/企微机器人

---

## 📧 反馈与建议

欢迎提出改进建议和优化方案！
