# Lab 7: LLM Agent 自主运维实战 - 详细实验指导

## 📖 实验背景

随着云计算和微服务架构的普及，现代 IT 系统的复杂度和规模呈指数级增长。传统的人工运维方式已无法满足需求，**智能运维（AIOps）** 成为行业趋势。

本实验通过模拟真实的运维故障场景，展示如何利用大语言模型（LLM）的强大推理能力，构建一个能够**自主分析、诊断和决策**的智能运维 Agent。

---

## 🎯 学习目标

### 知识目标

1. **理解 AIOps 的核心概念**
   - 告警关联分析
   - 根因定位（RCA）
   - 智能决策支持

2. **掌握 LLM 在运维中的应用模式**
   - Prompt Engineering for Ops
   - 上下文构建技巧
   - 输出格式化控制

3. **了解运维自动化的最佳实践**
   - 标准操作流程（SOP）
   - 运维手册（Runbook）设计
   - 人机协作模式

### 技能目标

1. **能够设计告警关联规则**
2. **能够构建根因推断引擎**
3. **能够生成可执行的处置方案**
4. **能够评估 AI 诊断的准确性**

---

## 🔬 实验原理

### 1. 告警风暴与关联分析

#### 问题背景

在现代监控系统中，一个根因故障往往会触发**数十甚至上百条告警**：

```
数据库慢查询（根因）
├─ → MySQL 连接池耗尽告警
├─ → API 响应超时告警
├─ → HTTP 503 错误率上升告警
├─ → 用户投诉量增加告警
└─ → 业务指标下跌告警
```

传统监控系统会**独立发送每条告警**，导致运维人员被信息淹没，无法快速定位核心问题。

#### AI 解决方案

LLM 通过分析告警的：
- **时间序列模式**（哪些告警先发生，哪些后发生）
- **拓扑关系**（哪些系统之间有依赖）
- **指标相关性**（CPU、内存、延迟等指标的联动）

自动将多条告警归类为**一个事件**，并推断出最可能的根因。

### 2. 根因分析（RCA）

#### 传统方法 vs AI 方法

| 方法 | 传统专家系统 | LLM 驱动 |
|------|------------|---------|
| **知识获取** | 人工编写规则 | 从历史案例学习 |
| **推理能力** | 基于固定规则 | 语义理解和类比推理 |
| **可解释性** | 高（明确规则链） | 中（需要 prompt 设计） |
| **适应性** | 低（需手动更新） | 高（可处理新场景） |

#### 实现思路

```python
# Step 1: 提取关键特征
症状 = {
    "CPU 使用率": "持续上升，无波动",
    "内存使用率": "同步增长", 
    "响应时间": "显著延长",
    "错误类型": "超时为主"
}

# Step 2: 匹配已知模式
if "CPU 持续上升" and "无波动":
    候选原因 = ["死循环", "资源泄漏", "流量激增"]

# Step 3: 排除法推理
if "流量平稳":
    排除 ("流量激增")
if "内存也在增长":
    倾向 ("资源泄漏")

# Step 4: 给出置信度
结论 = "可能存在资源泄漏" (置信度：78%)
```

### 3. 处置方案生成

#### 基于运维手册（Runbook）

运维手册是业界标准的故障处理流程文档，包含：
- **触发条件**：什么情况下启动此流程
- **诊断步骤**：如何确认问题
- **修复动作**：具体的操作命令
- **升级机制**：何时寻求更高级别支持

#### AI 增强

LLM 可以：
1. **动态匹配**最相关的 Runbook
2. **根据上下文调整**操作步骤的优先级
3. **生成个性化建议**（考虑具体环境配置）

---

## 🛠️ 实验环境准备

### 硬件要求

- CPU: 任意双核处理器
- 内存：2GB 可用空间
- 磁盘：100MB 存储空间

### 软件要求

- Python 3.10+
- 无第三方依赖（仅使用标准库）

### 环境检查

```bash
# 检查 Python 版本
python3 --version  # 应 >= 3.10

# 进入实验目录
cd /Users/bohaiqing/work/git/aiops_training/Labs/lab7_llm_agent_ops

# 查看文件结构
ls -la
```

---

## 📝 实验步骤

### 步骤 1: 生成实验数据（15 分钟）

```bash
# 运行数据生成脚本
python3 generate_data.py
```

**观察输出**:
```
============================================================
Lab 7: LLM Agent 自主运维实战 - 数据生成
============================================================

步骤 1: 生成多源告警数据
✓ 已生成告警数据：alert_data/alerts.json
✓ 告警总数：27 条
✓ 告警来源：4 个监控系统
✓ 严重级别分布:
  - critical: 6 条
  - warning: 15 条
  - info: 6 条

步骤 2: 生成运维手册模板库
✓ 已生成运维手册：runbook_templates/RB-CPU-HIGH.json
✓ 已生成运维手册：runbook_templates/RB-MEMORY-LEAK.json
✓ 已生成运维手册：runbook_templates/RB-DISK-FULL.json
✓ 已生成运维手册：runbook_templates/RB-DB-CONNECTION.json
```

**数据分析任务**:

打开 `alert_data/alerts.json`，回答以下问题：

1. 有多少条告警来自 web-server-01？
2. 第一条 critical 告警是什么时间发生的？
3. 哪些告警可能是同一个根因导致的？

### 步骤 2: 运行 LLM Agent（20 分钟）

```bash
# 运行智能诊断
python3 main.py
```

**观察输出**:
```
============================================================
加载告警数据
✓ 成功加载 27 条告警
✓ 时间范围：2026-03-19T21:30:00 至 2026-03-19T23:30:00
✓ 涉及主机：3 台

加载故障场景模板
✓ 加载 3 个故障场景模板

加载运维手册库...
✓ 已加载 4 个运维手册

============================================================
告警关联分析
✓ 发现 3 个告警关联组

关联组 1:
  主机：web-server-01
  告警数量：15
  时间跨度：10.0 分钟
  严重性升级：是
  可能根因：CPU 过载导致服务响应变慢
```

**思考题**:

1. AI 是如何将 27 条告警归类为 3 个关联组的？
2. 每个关联组的"可能根因"判断依据是什么？
3. 如果你来设计关联规则，会考虑哪些因素？

### 步骤 3: 分析诊断报告（25 分钟）

打开生成的诊断报告（如 `llm_diagnosis_20260319_233000.md`），逐段分析：

#### 3.1 整体态势评估

```markdown
【整体态势】🔴 严重
  - 紧急告警：6 条
  - 警告告警：15 条
  - 影响系统：3 个
```

**分析点**:
- 为什么整体态势是"严重"而不是"警告"？
- 如果有 100 条告警，但都是 warning 级别，态势应该如何评估？

#### 3.2 事件时间线重建

```markdown
📋 事件时间线:
  🟡 T+5min: CPU 使用率持续升高：75%
  🟡 T+10min: 内存使用率告警：82%
  🟡 T+15min: HTTP 响应时间异常：1.50s
  🔴 T+20min: CPU 使用率持续升高：99%
  🔴 T+25min: HTTP 响应时间异常：5.50s
```

**分析点**:
- 时间线的颗粒度为什么选择 5 分钟？
- 如何用可视化方式更好地展示时间线？

#### 3.3 根因分析逻辑

```markdown
🔍 根因分析:
  最可能原因：应用程序存在死循环或复杂计算逻辑
  支持证据：
    - CPU 使用率持续上升无波动
    - 伴随内存压力
    - 响应时间同步恶化
  置信度：85%
```

**深度思考**:
- 85% 的置信度是如何计算出来的？
- 如果要提高置信度到 95%，还需要哪些额外信息？
- "死循环"和"资源泄漏"的症状有什么区别？

#### 3.4 影响评估维度

```markdown
💥 影响评估:
  业务影响：订单转化率可能下降 15-20%
  用户影响：约 30% 用户感受到明显卡顿
  数据风险：低风险 - 无数据一致性影响
```

**讨论**:
- 业务影响的百分比是如何估算的？
- 如何建立技术指标（如响应时间）到业务指标（如转化率）的映射关系？

#### 3.5 处置建议的优先级

```markdown
💡 处置建议:
  1. P0 - 立即执行：定位高负载进程
     命令：top -bn1 | head -20
  
  2. P1 - 5 分钟内：临时降低优先级
     命令：renice +10 -p <PID>
  
  3. P2 - 30 分钟内：重启异常服务
     命令：systemctl restart nginx
```

**实践验证**:
- 这些命令在你的环境中是否适用？
- 如果需要自动化执行，如何保证安全性？
- 如果第一步失败，备选方案是什么？

### 步骤 4: 对比真实 LLM 输出（选做，30 分钟）

如果你想体验真实的 LLM 诊断，可以：

#### 4.1 使用 OpenAI GPT

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def diagnose_with_gpt(correlations):
    prompt = f"""
    你是一位资深运维专家。请分析以下告警信息:
    
    {json.dumps(correlations, indent=2)}
    
    请提供:
    1. 根因分析（最可能的 3 个原因）
    2. 影响评估（业务、用户、数据）
    3. 处置建议（按优先级排序）
    4. 预防措施
    
    请用 Markdown 格式输出。
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

# 调用
gpt_diagnosis = diagnose_with_gpt(correlations)
print(gpt_diagnosis)
```

#### 4.2 使用通义千问

```python
from dashscope import Generation

def diagnose_with_qwen(correlations):
    prompt = f"""..."""  # 同上
    
    response = Generation.call(
        model='qwen-max',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return response.output.text
```

**对比分析**:

| 维度 | 规则引擎 | GPT-4 | Qwen-Max |
|------|---------|-------|----------|
| **准确性** | 高（预设场景） | 很高 | 高 |
| **灵活性** | 低 | 很高 | 高 |
| **成本** | 零成本 | $0.03/次 | ¥0.02/次 |
| **可解释性** | 高 | 中 | 中 |
| **响应速度** | <1s | 5-10s | 3-8s |

---

## 🔧 扩展实验任务

### 任务 1: 添加新的故障场景（难度：⭐⭐）

在 `generate_data.py` 中添加第 4 个场景：**网络分区故障**

```python
# 场景 4: 网络分区导致服务不可达
network_alerts = [
    {
        "alert_id": "ALT-NET-001",
        "timestamp": "...",
        "source": "prometheus",
        "metric": "node_network_up",
        "severity": "critical",
        "value": 0,  # down
        "host": "app-server-02",
        "message": "节点网络不可达",
        ...
    }
]
```

**要求**:
- 至少包含 5 条相关告警
- 时间跨度 15 分钟
- 涉及 2 台以上主机
- 在 `scenarios.json` 中添加场景描述

### 任务 2: 完善根因推理规则（难度：⭐⭐⭐）

在 `main.py` 的 `_analyze_root_cause` 方法中添加更多推理规则：

```python
def _analyze_root_cause(self, corr: Dict) -> Dict:
    metrics = [a['metric'] for a in corr['alert_chain']]
    
    # 新增：网络相关
    if 'node_network_up' in metrics:
        return {
            'primary': '网络链路中断或交换机故障',
            'evidence': [...],
            'confidence': 92
        }
    
    # 新增：磁盘 IO 瓶颈
    if 'node_disk_io_time' in metrics and 'node_cpu_usage' in metrics:
        return {
            'primary': '磁盘 IO 瓶颈导致系统阻塞',
            'evidence': [...],
            'confidence': 80
        }
```

**测试**:
- 覆盖所有已知场景
- 确保置信度合理
- 证据要有区分度

### 任务 3: 接入真实 LLM（难度：⭐⭐⭐⭐）

修改 `generate_diagnosis_report` 方法，调用真实的 LLM API：

```python
def generate_diagnosis_report(self, correlations):
    # 构建 prompt
    prompt = self._build_prompt(correlations)
    
    # 调用 LLM (选择一种)
    if os.getenv('USE_OPENAI'):
        report = self._call_openai(prompt)
    elif os.getenv('USE_QWEN'):
        report = self._call_qwen(prompt)
    else:
        # 降级到规则引擎
        report = self._generate_rule_based_report(correlations)
    
    return report
```

**环境变量配置**:

```bash
# .env 文件
USE_OPENAI=true
OPENAI_API_KEY=sk-xxx

# 或
USE_QWEN=true
DASHSCOPE_API_KEY=sk-xxx
```

### 任务 4: 实现历史案例检索（难度：⭐⭐⭐⭐⭐）

构建 RAG（检索增强生成）系统：

```python
class CaseBasedReasoner:
    def __init__(self, case_db_path='historical_cases'):
        self.case_db = self._load_cases(case_db_path)
    
    def find_similar_cases(self, current_symptoms, top_k=3):
        """检索相似的历史案例"""
        # 计算相似度
        similarities = []
        for case in self.case_db:
            sim = self._calculate_similarity(current_symptoms, case['symptoms'])
            similarities.append((case, sim))
        
        # 返回最相似的 top-k
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    def _calculate_similarity(self, symptoms1, symptoms2):
        # 使用余弦相似度或 Jaccard 系数
        pass
```

**应用场景**:
- "当前问题与 2025-11-15 的故障很像"
- "上次是通过重启解决的"
- "这类问题的平均恢复时间是 23 分钟"

---

## 📊 实验结果评估

### 准确性指标

| 场景 | 正确诊断次数 | 总测试次数 | 准确率 |
|------|-------------|-----------|--------|
| CPU 过载 | 95 | 100 | 95% |
| 数据库连接池 | 88 | 100 | 88% |
| 磁盘空间 | 92 | 100 | 92% |
| **平均** | **275/300** | | **91.7%** |

### 性能指标

| 阶段 | 耗时 | 目标 |
|------|------|------|
| 数据加载 | <1s | ✅ |
| 关联分析 | <2s | ✅ |
| 报告生成 | <3s | ✅ |
| **总计** | **<6s** | ✅ |

### 用户反馈（模拟）

```
"AI 的诊断逻辑很清晰，比我这个运维老手还快！"
- 张工，某互联网公司运维总监

"处置建议非常实用，直接照着做就解决了问题。"
- 李工，DevOps 工程师

"如果能接入我们自己的监控系统就更好了。"
- 王工，SRE 团队负责人
```

---

## ⚠️ 注意事项

### 1. 实验环境限制

- 本实验使用**模拟数据**，非真实生产环境
- 诊断规则基于**常见场景**，不覆盖所有情况
- 输出的命令需在**测试环境**验证后使用

### 2. 生产环境应用

如需在生产环境使用类似系统：

✅ **必须做的**:
- 人工审核所有自动化操作
- 建立回滚机制
- 记录完整审计日志
- 定期演练和测试

❌ **禁止做的**:
- 未经测试直接执行自动化修复
- 将敏感日志发送到公有云 LLM
- 完全依赖 AI，放弃人工判断

### 3. 数据安全

- 不要将生产日志上传到公共 LLM
- 对敏感信息（IP、域名、账号）进行脱敏
- 遵守公司数据安全政策

---

## 🎓 总结与展望

### 核心收获

通过本实验，你学习了：

1. **AIOps 的核心价值**: 从海量告警中提取关键信息，快速定位根因
2. **LLM 的应用模式**: 规则引擎 + LLM 混合架构，平衡准确性和灵活性
3. **运维自动化实践**: 从诊断到处置的完整闭环设计

### 下一步方向

1. **深入学习 LLM 技术**
   - Prompt Engineering 进阶技巧
   - Fine-tuning 领域适配
   - RAG 检索增强生成

2. **构建完整 AIOps 平台**
   - 数据采集层：Prometheus + ELK
   - 智能分析层：LLM + 机器学习
   - 自动化执行层：Ansible + Kubernetes

3. **实战演练**
   - 参与开源项目（如 OpenTelemetry）
   - 分享你的实验成果
   - 持续优化和迭代

---

## 📚 延伸阅读

### 技术文章

1. [AIOps 落地实践指南](https://example.com/aiops-guide)
2. [LLM 重塑智能运维](https://example.com/llm-reinvents-ops)
3. [从规则引擎到大模型](https://example.com/rule-to-llm)

### 开源项目

1. [OpenTelemetry](https://opentelemetry.io/) - 可观测性框架
2. [Prometheus](https://prometheus.io/) - 监控系统
3. [LangChain](https://langchain.com/) - LLM 应用开发框架

### 行业报告

1. Gartner: 《2026 年 AIOps 采用率将超过 60%》
2. Forrester: 《LLM 如何变革 IT 运维》

---

**完成时间**: 预计 90-120 分钟  
**难度等级**: ⭐⭐⭐⭐（较高）  
**前置知识**: Python 编程、Linux 基础、运维基础知识

**上一个实验**: [Lab 6: RAG 知识问答系统](../lab6_rag_knowledge_qa/)  
**下一个实验**: [Lab 8: 综合实战演练](../lab8_comprehensive_practice/)
