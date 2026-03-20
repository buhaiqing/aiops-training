# Lab 7: 阿里云百炼 LLM 集成 - 使用说明

## 📋 概述

本实验实现了使用**阿里云百炼平台**的通义千问模型进行智能运维诊断，替代了原来的模拟实现。

## ✨ 主要特性

1. **真实的云厂商模型调用**: 使用阿里云百炼平台的 qwen-max 模型
2. **插件化架构**: 通过插件方式集成，易于扩展其他云厂商
3. **降级方案**: API 不可用时自动降级到规则引擎
4. **异步调用**: 支持异步 LLM 调用，提升性能

## 🔧 环境配置

### 1. 安装依赖

```bash
# 进入实验室目录
cd Labs/lab7_llm_agent_ops

# 使用 uv 安装（推荐）
uv pip install dashscope

# 或使用 pip
pip install dashscope
```

### 2. 配置 API Key

有三种方式配置阿里云百炼 API Key：

#### 方式 1: 环境变量（推荐）
```bash
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

#### 方式 2: 运行时输入
运行程序时会根据提示输入 API Key

#### 方式 3: 代码中传入
```python
from plugins.aliyun_bailian_plugin import AliyunBailianProvider

provider = AliyunBailianProvider(api_key="sk-your-api-key-here")
```

## 🚀 使用方法

### 方法 1: 使用新的主程序（推荐）

```bash
# 运行阿里云百炼版本
python main_bailian.py
```

程序会提示输入 API Key（如果未设置环境变量）：
```
请输入阿里云百炼 API Key (直接回车使用环境变量): 
```

### 方法 2: 在原有程序中集成

修改 `main_optimized.py`，注册阿里云百炼 Provider：

```python
from plugins.aliyun_bailian_plugin import AliyunBailianProvider

# 创建 Agent
agent = OptimizedLLMAgent(config)

# 注册阿里云百炼 Provider
bailian_provider = AliyunBailianProvider()
agent.plugin_manager.register_llm_provider(bailian_provider, default=True)
```

## 📊 运行示例

### 完整流程

```bash
# 1. 生成测试数据
python generate_data.py

# 2. 运行阿里云百炼诊断
python main_bailian.py

# 3. 查看生成的报告
cat bailian_diagnosis_20260320_143022.md
```

### 输出示例

```
============================================================
Lab 7: LLM Agent 自主运维实战 - 阿里云百炼版
============================================================
开始时间：2026-03-20 14:30:22

✓ LLM 配置:
  - 服务商：阿里云百炼
  - 模型：qwen-max
  - API Key: 已配置 ✓
  - 状态：可用 ✓

============================================================
加载告警数据
============================================================
✓ 成功加载 15 条告警
✓ 涉及主机：3 台

============================================================
执行智能诊断
============================================================
✓ 使用 LLM: aliyun-bailian
✓ LLM 诊断完成
✓ 响应长度：2847 字符

============================================================
诊断完成
============================================================
✅ 详细报告已保存：./bailian_diagnosis_20260320_143022.md
```

## 🔍 故障排查

### 问题 1: "未配置阿里云百炼 API Key"

**解决方案**:
```bash
export DASHSCOPE_API_KEY=sk-your-api-key
```

### 问题 2: "缺少 dashscope 依赖"

**解决方案**:
```bash
pip install dashscope
```

### 问题 3: API 调用失败

检查网络连通性和 API Key 有效性：
```bash
# 测试 API Key
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-turbo","messages":[{"role":"user","content":"你好"}]}'
```

## 📝 代码结构

```
lab7_llm_agent_ops/
├── plugins/
│   ├── aliyun_bailian_plugin.py    # 新增：阿里云百炼 Provider
│   └── plugins.py                   # 插件基类
├── main_bailian.py                  # 新增：阿里云百炼版主程序
├── main_optimized.py                # 优化版主程序（可使用模拟 LLM）
└── ...
```

## 🎯 核心组件

### AliyunBailianProvider

主要的 LLM Provider 实现：

```python
class AliyunBailianProvider(LLMProviderPlugin):
    """阿里云百炼 LLM 提供者"""
    
    def __init__(self, api_key=None, model="qwen-max"):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model
        
    async def diagnose(self, prompt: str, context: dict) -> str:
        """调用阿里云百炼 LLM 进行诊断"""
        # 异步调用阿里云百炼 API
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.call(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
        )
        return response.output.text
```

## 🔄 与模拟模式的对比

| 特性 | 模拟模式 (MockLLMProvider) | 阿里云百炼模式 |
|------|---------------------------|----------------|
| **准确性** | 预设规则，准确性一般 | 真实 AI 模型，准确性高 |
| **灵活性** | 低，只能返回固定文本 | 高，能理解复杂场景 |
| **成本** | 零成本 | 按 Token 计费 |
| **响应速度** | < 1 秒 | 3-8 秒 |
| **可解释性** | 高（规则明确） | 中（黑盒模型） |
| **适用场景** | 开发测试、演示 | 生产环境、真实诊断 |

## 🌟 扩展实验

### 任务 1: 添加腾讯云混元支持

参考 `aliyun_bailian_plugin.py`，创建 `tencent_hunyuan_plugin.py`

### 任务 2: 多模型对比

同时注册多个 LLM Provider，对比诊断结果：

```python
# 注册阿里云百炼
bailian = AliyunBailianProvider()
plugin_manager.register_llm_provider(bailian)

# 注册模拟 Provider 作为备选
mock = MockLLMProvider()
plugin_manager.register_llm_provider(mock)

# 切换使用不同的 Provider
llm_provider = plugin_manager.get_llm_provider("aliyun-bailian")
```

### 任务 3: 优化提示词

改进 `_build_diagnosis_prompt()` 方法，提升诊断质量。

## 📚 参考资料

- [阿里云百炼文档](https://help.aliyun.com/zh/dashscope/)
- [通义千问模型介绍](https://www.aliyun.com/product/bailian)
- [DashScope SDK GitHub](https://github.com/aliyun/alibabacloud-dashscope-python-sdk)

## 💡 最佳实践

1. **本地开发**: 使用模拟模式节省成本
2. **生产部署**: 使用真实的云厂商模型
3. **成本控制**: 设置 Token 使用上限
4. **性能优化**: 缓存常用诊断结果
5. **错误处理**: 始终准备降级方案

---

**实验完成！** 🎉
