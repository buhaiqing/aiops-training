#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 6: 基于 RAG 的故障知识问答系统 (简化版 - TF-IDF)
不依赖深度学习框架，使用传统的 TF-IDF + 余弦相似度
"""

import os
import json
import numpy as np
from typing import List, Dict
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAGKnowledgeBase:
    """基于 TF-IDF 的简单 RAG 知识库"""
    
    def __init__(self):
        self.documents = []
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
        print("")
        
        return self.documents
    
    def create_tfidf_index(self):
        """创建 TF-IDF 索引"""
        print("=" * 60)
        print("创建 TF-IDF 索引")
        print("=" * 60)
        
        # 准备文档文本
        texts = []
        for doc in self.documents:
            text = f"{doc['title']} {doc['content']} {' '.join(doc['tags'])}"
            texts.append(text)
        
        print(f"处理文档数量：{len(texts)}")
        
        # 创建 TF-IDF 向量化器
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # 中文不需要英文停用词
            ngram_range=(1, 2),  # 使用 unigram 和 bigram
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
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索最相关的文档"""
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
            if similarities[idx] > 0.1:  # 过滤太低的相关性
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarities[idx])
                results.append(doc)
        
        return results
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        """基于检索到的文档生成答案"""
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
内容摘要：{doc['content'][:300]}...
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
"""
        
        return answer


def demo_queries(kb: SimpleRAGKnowledgeBase):
    """演示查询示例"""
    
    print("\n" + "=" * 60)
    print("🤖 故障知识问答系统 - 演示模式 (TF-IDF 简化版)")
    print("=" * 60)
    
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
            
            # 提取故障现象
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
                for line in symptom_lines[1:]:
                    if line.strip():
                        print(f"     {line.strip()}")
            
            print("")
        else:
            print("❌ 未找到相关文档")
        
        input("按回车继续下一个问题...")


def main():
    """主函数"""
    print("=" * 60)
    print("Lab 6: 基于 RAG 的故障知识问答系统 (简化版)")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 创建知识库实例
    kb = SimpleRAGKnowledgeBase()
    
    try:
        # 1. 加载文档
        kb.load_documents('knowledge_base')
        
        # 2. 创建 TF-IDF 索引
        if not kb.create_tfidf_index():
            return
        
        # 3. 演示查询
        demo_queries(kb)
        
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
    print("\n💡 说明:")
    print("  - 本版本使用 TF-IDF + 余弦相似度进行检索")
    print("  - 完整版使用 sentence-transformers 进行语义检索")
    print("  - TF-IDF 优点：快速、无需深度学习依赖")
    print("  - TF-IDF 缺点：无法理解深层语义")
    print("")


if __name__ == '__main__':
    main()
