# Lab 6: 基于 RAG 的故障知识问答系统 - 详细指导

## 📖 实验背景

在企业运维场景中，积累了大量的故障处理经验和知识。如何快速检索和复用这些知识，是提升运维效率的关键。传统的关键词搜索无法理解语义，而大语言模型（LLM）虽然能理解语义，但缺乏企业特定的领域知识。

**RAG（Retrieval-Augmented Generation）** 结合了检索和生成的优势：
- **检索**：从知识库中查找相关文档
- **生成**：基于检索结果生成准确的答案

本实验将学习如何构建一个基于 RAG 的智能故障问答系统。

---

## 🎯 学习目标

### 知识目标
1. **理解 RAG 的工作原理**
   - 检索增强生成的概念
   - RAG vs 纯 LLM vs 纯检索
   
2. **掌握嵌入技术**
   - 文本向量化原理
   - 语义相似度计算
   - 多语言嵌入模型

3. **学会向量检索**
   - FAISS 索引类型
   - 余弦相似度 vs 内积
   - 精确搜索 vs 近似搜索

### 技能目标
1. ✅ 能够使用 sentence-transformers 生成文本嵌入
2. ✅ 能够使用 FAISS 构建向量索引
3. ✅ 能够实现基于相似度的文档检索
4. ✅ 能够构建简单的 RAG 问答系统
5. ✅ 能够评估检索质量

---

## 📚 前置知识

- Python 编程基础
- NumPy 数组操作
- 基本的机器学习概念（向量、相似度）
- 了解 Transformer 和 BERT 基本原理

---

## 🔬 技术原理

### 1. RAG 架构

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   用户提问   │  →   │  检索模块    │  →   │  生成模块    │
│   Query     │      │  Retrieval   │      │  Generation  │
└─────────────┘      └──────────────┘      └─────────────┘
                           ↓                     ↓
                    ┌──────────────┐      ┌─────────────┐
                    │  知识库       │      │  上下文      │
                    │  Knowledge   │      │  Context    │
                    └──────────────┘      └─────────────┘
```

### 2. 文本嵌入（Embedding）

将文本转换为固定长度的向量：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 编码文档
doc_embedding = model.encode("这是一篇关于 CPU 故障的文档")

# 编码问题
query_embedding = model.encode("CPU 使用率很高怎么办？")

# 向量维度：384
print(doc_embedding.shape)  # (384,)
```

### 3. 相似度计算

#### 余弦相似度（Cosine Similarity）
```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 归一化后，余弦相似度 = 内积
a_normalized = a / np.linalg.norm(a)
b_normalized = b / np.linalg.norm(b)
cosine_sim = np.dot(a_normalized, b_normalized)
```

#### 内积（Inner Product）
```python
# FAISS IndexFlatIP 使用内积
# 对于归一化向量，内积 = 余弦相似度
similarity = np.dot(query_emb, doc_emb)
```

### 4. FAISS 索引

FAISS 提供多种索引类型：

| 索引类型 | 特点 | 适用场景 |
|---------|------|---------|
| **IndexFlatIP** | 精确搜索、内积相似度 | 小规模数据（<10 万） |
| **IndexFlatL2** | 精确搜索、欧氏距离 | 需要距离度量 |
| **IndexHNSW** | 近似搜索、速度快 | 大规模数据 |
| **IndexIVF** | 倒排文件索引 | 超大规模数据 |

本实验使用 `IndexFlatIP`（精确内积搜索）。

---

## 💻 实验步骤

### Step 1: 环境准备

```bash
cd lab6_rag_knowledge_qa

# 创建虚拟环境
make venv

# 激活环境
source .venv/bin/activate

# 安装依赖
make deps
```

**核心依赖**:
- `sentence-transformers`: 文本嵌入模型
- `faiss-cpu`: 向量检索引擎
- `numpy`: 数值计算
- `pandas`: 数据处理

---

### Step 2: 生成故障知识库

```bash
make data
```

**生成内容**:
- 8 篇故障处理文档
- 涵盖 CPU、内存、磁盘、网络、数据库等场景
- 每篇包含：现象、原因、排查步骤、解决方案、预防措施

**输出示例**:
```
✓ 已生成文档：knowledge_base/FAULT-001_CPU.json
✓ 已生成文档：knowledge_base/FAULT-002_内存.json
...
✓ 知识库生成完成
✓ 文档总数：8
✓ 文档类别：7
✓ 标签总数：28
```

---

### Step 3: 加载文档并创建嵌入

运行主程序会自动执行：

```python
# 1. 加载文档
kb.load_documents('knowledge_base')

# 2. 加载嵌入模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 3. 生成文档嵌入
texts = [f"{doc['title']} {doc['content']}" for doc in documents]
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

# 输出：(8, 384)
print(embeddings.shape)
```

**嵌入过程**:
1. 文本预处理（拼接标题和内容）
2. 分词（Tokenizer）
3. 通过 Transformer 模型
4. 池化（Pooling）得到固定长度向量
5. 归一化（用于余弦相似度）

---

### Step 4: 构建 FAISS 索引

```python
import faiss

# 获取向量维度
dimension = embeddings.shape[1]  # 384

# 创建内积索引
index = faiss.IndexFlatIP(dimension)

# 归一化向量
faiss.normalize_L2(embeddings)

# 添加到索引
index.add(embeddings)

# 索引大小：8
print(index.ntotal)
```

**索引构建完成**后，可以进行快速检索。

---

### Step 5: 检索相关文档

```python
# 用户提问
query = "CPU 使用率很高怎么办？"

# 编码查询
query_embedding = model.encode([query])
faiss.normalize_L2(query_embedding)

# 检索 top-3 最相似的文档
top_k = 3
similarities, indices = index.search(query_embedding, top_k)

# 返回结果
for sim, idx in zip(similarities[0], indices[0]):
    doc = documents[idx]
    print(f"标题：{doc['title']}")
    print(f"相似度：{sim:.4f}")
```

**输出示例**:
```
标题：CPU 使用率持续高于 90%
相似度：0.8523

标题：应用响应时间过长
相似度：0.7234

标题：日志中出现大量 ERROR 和 EXCEPTION
相似度：0.6891
```

---

### Step 6: 生成答案

基于检索到的文档，构建结构化的答案：

```python
def generate_answer(query, retrieved_docs):
    # 构建上下文
    context = "\n".join([doc['content'] for doc in retrieved_docs])
    
    # 生成答案模板
    answer = f"""
针对您的问题：**{query}**

## 📋 相关知识

{context}

## 💡 建议处理步骤

1. **确认故障现象**
2. **排查可能原因**
3. **执行解决方案**
4. **落实预防措施**
"""
    return answer
```

---

## 📊 结果分析

### 检索质量指标

#### 1. 相似度分数分布

```python
similarities = [doc['similarity'] for doc in retrieved_docs]

print(f"最高相似度：{max(similarities):.4f}")
print(f"最低相似度：{min(similarities):.4f}")
print(f"平均相似度：{np.mean(similarities):.4f}")
```

**解读**:
- > 0.8: 非常相关
- 0.6-0.8: 比较相关
- 0.4-0.6: 一般相关
- < 0.4: 不太相关

#### 2. 召回率分析

```python
# 如果有标准答案
def recall_at_k(retrieved, relevant, k):
    """计算 Recall@K"""
    retrieved_set = set(retrieved[:k])
    relevant_set = set(relevant)
    return len(retrieved_set & relevant_set) / len(relevant_set)

# Recall@3 = 1.0 表示前 3 个结果包含了所有相关文档
```

---

## 🔧 参数调优

### 1. Top-K 选择

```python
# 测试不同的 k 值
for k in [1, 3, 5, 10]:
    results = kb.search(query, top_k=k)
    print(f"k={k}: 找到 {len(results)} 篇文档")
```

**权衡**:
- k 太小：可能漏掉相关文档
- k 太大：引入噪声，影响答案质量

**建议**: 从 k=3 开始，根据效果调整

### 2. 相似度阈值

```python
# 过滤低相似度结果
threshold = 0.6
filtered_results = [doc for doc in results if doc['similarity'] > threshold]
```

**作用**:
- 避免不相关的文档干扰答案
- 提高答案准确性

### 3. 嵌入模型选择

| 模型 | 维度 | 速度 | 中文效果 | 推荐场景 |
|------|------|------|---------|---------|
| MiniLM | 384 | 快 | 好 | 快速原型 |
| BGE | 1024 | 中 | 很好 | 生产环境 |
| M3E | 768 | 中 | 优秀 | 中文场景 |

---

## 🎯 扩展实验

### 实验 1: 对比不同模型

```python
models = [
    'paraphrase-multilingual-MiniLM-L12-v2',
    'BAAI/bge-base-zh-v1.5',
    'moka-ai/m3e-base'
]

for model_name in models:
    model = SentenceTransformer(model_name)
    # ... 测试检索效果
```

记录并对比：
- 平均相似度
- 检索准确率
- 响应时间

### 实验 2: 添加混合检索

结合语义检索和关键词检索：

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# TF-IDF 关键词检索
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)

# 语义检索
semantic_results = kb.search(query, top_k=5)

# 关键词检索
keyword_results = tfidf_search(query, tfidf_matrix, top_k=5)

# 融合结果（加权）
final_results = fuse_results(semantic_results, keyword_results, alpha=0.7)
```

### 实验 3: 实现重排序

```python
# 第一步：粗排（快速召回）
coarse_results = kb.search(query, top_k=20)

# 第二步：精排（Cross-Encoder 重排序）
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
pairs = [[query, doc['content']] for doc in coarse_results]
scores = reranker.predict(pairs)

# 按新分数排序
reranked_results = sorted(coarse_results, key=lambda x: scores[x['id']], reverse=True)

# 取 top-3
final_results = reranked_results[:3]
```

---

## ⚠️ 注意事项

### 1. 内存管理

```python
# 大批量编码时分批处理
embeddings = model.encode(
    texts,
    batch_size=32,  # 避免 OOM
    show_progress_bar=True
)
```

### 2. 模型下载

第一次运行时会下载模型（约 500MB），建议：

```bash
# 设置国内镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### 3. 索引持久化

```python
# 保存索引
faiss.write_index(index, 'knowledge.index')

# 加载索引
index = faiss.read_index('knowledge.index')
```

---

## 📈 性能优化

### 1. 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query_hash, top_k):
    return kb.search(query, top_k)
```

### 2. 增量更新

```python
# 添加新文档时，不需要重新构建整个索引
new_embedding = model.encode([new_doc])
faiss.normalize_L2(new_embedding)
index.add(new_embedding)
```

### 3. 并行处理

```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(search_single_query, queries)
```

---

## 🤔 思考题

1. **RAG 相比纯 LLM 有哪些优势？**
   - 知识可追溯
   - 减少幻觉
   - 更新成本低

2. **如何处理多轮对话？**
   - 考虑对话历史
   - 使用上下文增强查询

3. **如何评估 RAG 系统的整体质量？**
   - 检索质量（Recall、Precision）
   - 生成质量（相关性、准确性）
   - 用户体验（响应时间、满意度）

4. **在生产环境中部署 RAG 需要考虑什么？**
   - 高可用性
   - 水平扩展
   - 监控告警
   - 安全防护

---

## 📚 参考资料

- [RAG 原论文](https://arxiv.org/abs/2005.11401)
- [FAISS 官方文档](https://github.com/facebookresearch/faiss)
- [Sentence-Transformers 教程](https://www.sbert.net/)
- [RAG 最佳实践](https://weaviate.io/blog/rag-best-practices)

---

## ✅ 总结

通过本实验，你掌握了：
- ✅ RAG 的基本原理和架构
- ✅ 文本嵌入技术和相似度计算
- ✅ FAISS 向量检索引擎的使用
- ✅ 构建简单的问答系统
- ✅ 评估和优化检索质量

这为你后续学习更复杂的 LLM Agent 和 ChatOps 打下了坚实基础！

---

**Happy Coding! 🚀**
