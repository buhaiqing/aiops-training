#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 6: 基于 RAG 的故障知识问答系统
主程序：实现检索增强生成的问答流程
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime

# 尝试导入必要的库
try:
    # 禁用可能的冲突和警告
    import os
    import warnings
    
    os.environ['WANDB_DISABLED'] = 'true'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    # 忽略特定警告
    warnings.filterwarnings('ignore', category=FutureWarning, module='.*wandb.*')
    warnings.filterwarnings('ignore', message='.*MessageFactory.*')
    
    # 先尝试导入关键模块，失败则使用简化版
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    # 尝试加载 sentence-transformers（可选）
    try:
        # 临时重定向 stderr 以隐藏 protobuf 警告
        import sys
        from io import StringIO
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        from sentence_transformers import SentenceTransformer
        import faiss
        
        sys.stderr = old_stderr
        HAS_ADVANCED_EMBEDDING = True
        print("✓ 高级嵌入模型可用（sentence-transformers + FAISS）")
    except (ImportError, AttributeError) as e:
        sys.stderr = old_stderr
        HAS_ADVANCED_EMBEDDING = False
    
    HAS_RAG_LIBS = True
    
except ImportError as e:
    print(f"⚠️  缺少必要依赖：{e}")
    print("请运行：pip install scikit-learn sentence-transformers faiss-cpu")
    HAS_RAG_LIBS = False


class RAGKnowledgeBase:
    """基于向量检索的知识库（支持高级嵌入和 TF-IDF 双模式）"""
    
    def __init__(self, use_advanced_embedding=True):
        """
        初始化 RAG 知识库
        
        参数:
            use_advanced_embedding: 是否使用高级嵌入模型（sentence-transformers）
        """
        self.use_advanced_embedding = use_advanced_embedding and HAS_ADVANCED_EMBEDDING
        self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.model = None
        self.documents = []
        self.embeddings = None
        self.index = None
        
        # TF-IDF 相关
        self.vectorizer = None
        self.tfidf_matrix = None
        
    def load_documents(self, knowledge_base_dir='knowledge_base'):
        """加载知识库文档"""
        print("=" * 60)
        print("加载知识库文档")
        print("=" * 60)
        
        all_docs_file = os.path.join(knowledge_base_dir, 'all_documents.json')
        
        if not os.path.exists(all_docs_file):
            raise FileNotFoundError(f"知识库文件不存在：{all_docs_file}")
        
        with open(all_docs_file, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        print(f"✓ 成功加载 {len(self.documents)} 个文档")
        print(f"✓ 文档类别：{len(set(doc['category'] for doc in self.documents))}")
        print(f"✓ 标签总数：{len(set(tag for doc in self.documents for tag in doc['tags']))}")
        print("")
        
        return self.documents
    
    def create_embeddings(self):
        """创建文档嵌入向量（自动选择高级或 TF-IDF 模式）"""
        print("=" * 60)
        print("创建文档嵌入向量")
        print("=" * 60)
        
        if self.use_advanced_embedding:
            return self._create_advanced_embeddings()
        else:
            return self._create_tfidf_embeddings()
    
    def _create_advanced_embeddings(self):
        """使用 sentence-transformers 创建高级嵌入"""
        # 加载模型
        print(f"加载嵌入模型：{self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"⚠️  模型加载失败：{e}")
            print("ℹ️  切换到 TF-IDF 模式")
            self.use_advanced_embedding = False
            return self._create_tfidf_embeddings()
        
        # 准备文档文本
        texts = []
        for doc in self.documents:
            text = f"{doc['title']} {doc['content']}"
            texts.append(text)
        
        print(f"处理文档数量：{len(texts)}")
        
        # 生成嵌入向量
        print("正在生成嵌入向量...")
        self.embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=32
        )
        
        print(f"✓ 嵌入向量形状：{self.embeddings.shape}")
        print(f"✓ 向量维度：{self.embeddings.shape[1]}")
        print("")
        
        return True
    
    def _create_tfidf_embeddings(self):
        """使用 TF-IDF 创建简单嵌入"""
        print("使用 TF-IDF 方法创建索引...")
        
        # 准备文档文本
        texts = []
        for doc in self.documents:
            text = f"{doc['title']} {doc['content']} {' '.join(doc['tags'])}"
            texts.append(text)
        
        print(f"处理文档数量：{len(texts)}")
        
        # 创建 TF-IDF 向量化器
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # 拟合并转换
        print("正在生成 TF-IDF 向量...")
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        print(f"✓ TF-IDF 矩阵形状：{self.tfidf_matrix.shape}")
        print(f"✓ 词汇表大小：{len(self.vectorizer.vocabulary_)}")
        print("")
        
        return True
    
    def build_index(self):
        """构建 FAISS 索引或 TF-IDF 索引"""
        print("=" * 60)
        print("构建检索索引")
        print("=" * 60)
        
        if self.use_advanced_embedding:
            return self._build_faiss_index()
        else:
            # TF-IDF 不需要额外构建索引
            print("✓ TF-IDF 模式，无需额外索引构建")
            print("")
            return True
    
    def _build_faiss_index(self):
        """构建 FAISS 索引"""
        if self.embeddings is None:
            print("❌ 请先创建嵌入向量")
            return False
        
        # 创建 FAISS 索引（使用内积相似度）
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        # 归一化向量（用于余弦相似度）
        faiss.normalize_L2(self.embeddings)
        
        # 添加到索引
        self.index.add(self.embeddings)
        
        print(f"✓ 索引类型：FAISS IndexFlatIP")
        print(f"✓ 索引大小：{self.index.ntotal}")
        print(f"✓ 向量维度：{dimension}")
        print("")
        
        return True
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """检索最相关的文档（自动选择 FAISS 或 TF-IDF）"""
        if self.use_advanced_embedding:
            return self._search_faiss(query, top_k)
        else:
            return self._search_tfidf(query, top_k)
    
    def _search_faiss(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """使用 FAISS 进行语义检索"""
        if self.index is None or self.model is None:
            print("❌ 请先初始化索引")
            return []
        
        # 将查询转换为向量
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # 搜索最相似的文档
        similarities, indices = self.index.search(query_embedding, top_k)
        
        # 返回结果
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarity)
                results.append(doc)
        
        return results
    
    def _search_tfidf(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """使用 TF-IDF 进行关键词检索"""
        if self.vectorizer is None or self.tfidf_matrix is None:
            print("❌ 请先初始化索引")
            return []
        
        # 将查询转换为 TF-IDF 向量
        query_vector = self.vectorizer.transform([query])
        
        # 计算余弦相似度
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 获取 top-k 结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # 返回结果
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # 过滤太低的相关性
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarities[idx])
                results.append(doc)
        
        return results
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        """
        基于检索到的文档生成答案
        
        参数:
            query: 用户问题
            retrieved_docs: 检索到的文档列表
        
        返回:
            生成的答案
        """
        if not retrieved_docs:
            return "抱歉，没有找到相关的故障处理知识。"
        
        # 构建上下文
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"""
【相关知识 {i}】
标题：{doc['title']}
类别：{doc['category']}
严重程度：{doc.get('severity', '未知')}
内容：
{doc['content']}
""")
        
        context = "\n".join(context_parts)
        
        # 生成答案模板
        answer = f"""
根据故障知识库的检索结果，针对您的问题：**{query}**

## 📋 相关知识

{context}

## 💡 建议处理步骤

基于检索到的知识，建议您按照以下步骤处理：

1. **确认故障现象**：对照上述文档描述，确认是否符合您的情况
2. **排查可能原因**：逐一检查列出的可能原因
3. **执行排查步骤**：按照文档中的排查步骤进行操作
4. **实施解决方案**：根据排查结果选择对应的解决方案
5. **落实预防措施**：故障解决后，建立预防机制

## ⚠️ 注意事项

- 如果问题紧急，请优先联系值班人员或专家团队
- 操作前请做好数据备份和风险评估
- 记录详细的处理过程，便于后续复盘

## 📞 如需进一步帮助

如上述知识无法解决您的问题，请提供：
- 详细的故障现象描述
- 相关日志和监控截图
- 已尝试的处理步骤
- 系统环境信息
"""
        
        return answer


def interactive_qa(kb: RAGKnowledgeBase):
    """交互式问答"""
    
    print("\n" + "=" * 60)
    print("🤖 故障知识问答系统 - 交互式模式")
    print("=" * 60)
    print("\n欢迎使用基于 RAG 的故障知识问答系统！")
    print("\n💡 使用提示：")
    print("  - 输入问题获取故障处理建议")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'history' 查看历史提问")
    print("")
    
    history = []
    
    while True:
        try:
            # 获取用户输入
            query = input("📝 请输入您的问题：").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n✓ 感谢使用，再见！")
                break
            
            if query.lower() == 'history':
                if history:
                    print("\n历史提问:")
                    for i, q in enumerate(history[-5:], 1):
                        print(f"  {i}. {q}")
                else:
                    print("\n暂无历史提问")
                continue
            
            # 记录历史
            history.append(query)
            
            # 检索相关知识
            print("\n🔍 正在检索知识库...")
            retrieved_docs = kb.search(query, top_k=3)
            
            if not retrieved_docs:
                print("❌ 未找到相关知识")
                continue
            
            # 显示检索结果
            print(f"\n✓ 找到 {len(retrieved_docs)} 篇相关文档:\n")
            for i, doc in enumerate(retrieved_docs, 1):
                print(f"[{i}] {doc['title']}")
                print(f"    类别：{doc['category']} | 相似度：{doc['similarity']:.4f}")
                print(f"    标签：{', '.join(doc['tags'])}")
                print("")
            
            # 生成答案
            show_answer = input("是否查看详细答案？(y/n): ").strip().lower()
            
            if show_answer == 'y':
                answer = kb.generate_answer(query, retrieved_docs)
                print("\n" + "=" * 60)
                print(answer)
                print("=" * 60)
            
            print("")
            
        except KeyboardInterrupt:
            print("\n\n✓ 已退出交互模式")
            break
        except Exception as e:
            print(f"\n❌ 发生错误：{e}")
            continue


def demo_queries(kb: RAGKnowledgeBase):
    """演示查询示例"""
    
    print("\n" + "=" * 60)
    print("🤖 故障知识问答系统 - 演示模式")
    print("=" * 60)
    
    # 预设问题列表
    demo_questions = [
        "CPU 使用率很高怎么办？",
        "内存泄漏如何处理？",
        "数据库连接池耗尽了怎么解决？",
        "服务返回 503 错误，如何排查？",
        "磁盘空间不足，如何清理？"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'='*60}")
        print(f"问题 {i}: {question}")
        print('='*60)
        
        # 检索
        retrieved_docs = kb.search(question, top_k=2)
        
        if retrieved_docs:
            print(f"\n✓ 检索到 {len(retrieved_docs)} 篇相关文档:\n")
            for j, doc in enumerate(retrieved_docs, 1):
                print(f"[{j}] {doc['title']}")
                print(f"    相似度：{doc['similarity']:.4f}")
                print(f"    类别：{doc['category']}")
                print(f"    关键标签：{', '.join(doc['tags'][:3])}")
                print("")
            
            # 显示第一篇文档的摘要
            top_doc = retrieved_docs[0]
            print(f"📄 最相关文档摘要:")
            print(f"   标题：{top_doc['title']}")
            print(f"   严重程度：{top_doc.get('severity', '未知')}")
            
            # 提取故障现象（前 3 行）
            content_lines = top_doc['content'].strip().split('\n')
            symptom_lines = []
            capture = False
            for line in content_lines[:10]:
                if '故障现象' in line:
                    capture = True
                if capture:
                    symptom_lines.append(line)
                    if len(symptom_lines) >= 3:
                        break
            
            if symptom_lines:
                print(f"   故障现象:")
                for line in symptom_lines[1:]:  # 跳过"故障现象："标题
                    if line.strip():
                        print(f"     {line.strip()}")
            
            print("")
        else:
            print("❌ 未找到相关文档")
        
        input("按回车继续下一个问题...")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 6: 基于 RAG 的故障知识问答系统")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 检查依赖
    if not HAS_RAG_LIBS:
        print("❌ 缺少必要的依赖包")
        print("\n请运行以下命令安装:")
        print("  pip install scikit-learn sentence-transformers faiss-cpu")
        print("\n或使用 make deps 安装所有依赖")
        return
    
    # 创建知识库实例
    kb = RAGKnowledgeBase()
    
    try:
        # 1. 加载文档
        kb.load_documents('knowledge_base')
        
        # 2. 创建嵌入向量
        if not kb.create_embeddings():
            return
        
        # 3. 构建索引
        if not kb.build_index():
            return
        
        # 4. 选择模式
        print("\n请选择运行模式:")
        print("  1. 演示模式（查看预设问题示例）")
        print("  2. 交互模式（自由提问）")
        print("  3. 批量测试（自动测试所有预设问题）")
        print("")
        
        choice = input("请输入选项 (1/2/3): ").strip()
        
        if choice == '1':
            demo_queries(kb)
        elif choice == '2':
            interactive_qa(kb)
        elif choice == '3':
            demo_questions = [
                "CPU 使用率很高怎么办？",
                "内存泄漏如何处理？",
                "数据库连接池耗尽了怎么解决？",
                "服务返回 503 错误，如何排查？",
                "磁盘空间不足，如何清理？"
            ]
            for question in demo_questions:
                print(f"\n问题：{question}")
                retrieved_docs = kb.search(question, top_k=2)
                if retrieved_docs:
                    print(f"✓ 找到 {len(retrieved_docs)} 篇相关文档")
                    print(f"  最相关：{retrieved_docs[0]['title']}")
                    print(f"  相似度：{retrieved_docs[0]['similarity']:.4f}")
                print("")
        else:
            print("无效的选项")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误：{e}")
        print("\n请先运行以下命令生成知识库:")
        print("  python3 generate_data.py")
        print("或运行:")
        print("  make data")
    
    except Exception as e:
        print(f"\n❌ 系统错误：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
