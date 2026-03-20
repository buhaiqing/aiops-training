# 🚀 Lab 7 升级公告：从模拟到真实云厂商模型

## 📢 重要更新

Lab 7 现已支持使用**阿里云百炼平台**的真实 LLM 模型进行智能运维诊断！

---

## ✨ 新增功能

### 1. 真实的 AI 诊断能力
- ✅ 集成阿里云百炼平台
- ✅ 使用通义千问 (qwen-max) 模型
- ✅ 生成专业级运维诊断报告

### 2. 插件化架构
- ✅ 可扩展的 LLM Provider 框架
- ✅ 支持多云厂商（阿里、腾讯等）
- ✅ 热插拔机制

### 3. 优雅降级
- ✅ API 不可用时自动切换到规则引擎
- ✅ 保证系统可用性
- ✅ 零配置运行（模拟模式）

---

## 🎯 快速开始（3 分钟上手）

### 方式 1: 模拟模式（无需配置）

```bash
cd Labs/lab7_llm_agent_ops
make all
```

适合：开发测试、演示

### 方式 2: 真实模式（推荐）⭐

```bash
# 1. 安装依赖
make deps

# 2. 配置 API Key
export DASHSCOPE_API_KEY=sk-your-api-key

# 3. 生成数据
make data

# 4. 运行真实诊断
make bailian
```

适合：生产环境、真实场景

---

## 📊 效果对比

### 模拟模式输出

```
根因分析:
  最可能原因：应用程序存在死循环或复杂计算逻辑
  置信度：85%
```

### 阿里云百炼模式输出

```markdown
# 智能诊断报告

## 一、整体态势评估 🔴
当前系统处于严重告警状态，涉及 3 台主机，共检测到 15 条告警。
主要问题集中在 CPU 过载和数据库连接池耗尽...

## 二、事件分析

### 事件 1: web-server-01 - CPU 过载导致服务响应变慢

**时间线**:
- T+0min: CPU 使用率达到 80%（警告）
- T+3min: CPU 使用率飙升至 95%（紧急）
- T+5min: HTTP 响应时间恶化至 2.5s

**根因分析**:
根据监控数据显示，CPU 使用率呈现持续上升趋势且无明显波动，
同时伴随内存压力增加。这通常表明应用程序中存在以下可能：
1. 某个进程陷入死循环
2. 执行了复杂的计算任务
3. 资源泄漏导致 GC 频繁

**处置建议**:
1. [P0] 立即定位高负载进程
   ```bash
   top -bn1 | head -20
   ```
2. [P1] 临时降低异常进程优先级
   ```bash
   renice +10 -p <PID>
   ```
...
```

---

## 🛠️ 核心组件

### 1. AliyunBailianProvider

```python
from plugins.aliyun_bailian_plugin import AliyunBailianProvider

# 创建 Provider
provider = AliyunBailianProvider(
    api_key="sk-xxx",  # 或使用环境变量
    model="qwen-max"   # 可选：qwen-max, qwen-plus, qwen-turbo
)

# 异步调用
result = await provider.diagnose(prompt, context)
```

### 2. main_bailian.py

完整的主程序，包含：
- 交互式 API Key 配置
- 智能提示词构建
- 完整的错误处理
- 降级机制

### 3. 测试工具

```bash
# 快速验证集成
python test_bailian.py
```

---

## 💰 成本说明

### 模拟模式
- **费用**: ¥0
- **适用**: 开发、测试、演示

### 阿里云百炼模式
- **qwen-max**: ¥0.02/次（约 2000 tokens）
- **日均 100 次**: ¥2/天 ≈ ¥60/月
- **适用**: 生产环境、真实诊断

💡 **省钱技巧**:
- 开发阶段使用模拟模式
- 生产环境使用真实模式
- 缓存常用诊断结果

---

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| [ALIYUN_BAILIAN_USAGE.md](./ALIYUN_BAILIAN_USAGE.md) | 详细使用手册 |
| [BAILIAN_INTEGRATION_SUMMARY.md](./BAILIAN_INTEGRATION_SUMMARY.md) | 实现技术细节 |
| [lab_guide.md](./lab_guide.md) | 原始实验指南 |

---

## 🔍 故障排查

### 问题 1: "未配置 API Key"

```bash
# 解决方案
export DASHSCOPE_API_KEY=sk-your-api-key
```

### 问题 2: "缺少 dashscope 依赖"

```bash
# 解决方案
make deps
# 或
pip install dashscope
```

### 问题 3: API 调用失败

检查网络和 API Key 有效性：
```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"你好"}]}'
```

---

## 🎓 学习价值

通过本实验，你将掌握：

1. ✅ 云厂商模型集成方法
2. ✅ 插件化架构设计
3. ✅ 异步编程实践
4. ✅ 降级策略实现
5. ✅ Prompt Engineering

---

## 🌟 扩展任务

### 任务 1: 添加腾讯云混元支持 ⭐⭐

参考 `aliyun_bailian_plugin.py`，创建 `tencent_hunyuan_plugin.py`

### 任务 2: 多模型对比 ⭐⭐⭐

同时使用多个 LLM Provider，对比诊断结果

### 任务 3: 优化提示词 ⭐⭐⭐

改进 `_build_diagnosis_prompt()`，提升诊断质量

---

## 📞 技术支持

遇到问题？

1. 查看 [ALIYUN_BAILIAN_USAGE.md](./ALIYUN_BAILIAN_USAGE.md) 故障排查章节
2. 运行 `python test_bailian.py` 诊断问题
3. 参考 [BAILIAN_INTEGRATION_SUMMARY.md](./BAILIAN_INTEGRATION_SUMMARY.md) 技术细节

---

## 🎉 总结

Lab 7 现在已经完全支持使用真实的云厂商模型进行智能运维诊断！

**立即体验**:
```bash
make bailian
```

**从入门到精通**:
```bash
# 1. 模拟模式入门
make run

# 2. 真实模式实战
make bailian

# 3. 深入理解原理
cat BAILIAN_INTEGRATION_SUMMARY.md
```

---

**Happy Coding! 🚀**
