#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试阿里云百炼集成
验证插件是否正确配置和可用
"""

import asyncio
import sys
from plugins.aliyun_bailian_plugin import AliyunBailianProvider


async def test_bailian_provider():
    """测试阿里云百炼 Provider"""
    print("=" * 60)
    print("测试阿里云百炼 LLM Provider")
    print("=" * 60)
    
    # 创建 Provider 实例
    provider = AliyunBailianProvider()
    
    # 显示模型信息
    model_info = provider.get_model_info()
    print("\n模型信息:")
    print(f"  - 服务商：{model_info['provider']}")
    print(f"  - 模型：{model_info['model']}")
    print(f"  - API Key 已配置：{model_info['api_key_configured']}")
    print(f"  - 状态：{'可用 ✓' if model_info['available'] else '不可用 ✗'}")
    print()
    
    if not model_info['available']:
        print("⚠️  阿里云百炼不可用")
        print("\n请配置 API Key:")
        print("  export DASHSCOPE_API_KEY=sk-your-api-key")
        return False
    
    # 测试简单调用
    print("执行测试诊断...")
    test_prompt = "CPU 使用率 95%，内存使用率 85%，请分析可能的原因。"
    test_context = {
        "metrics": ["node_cpu_usage", "node_memory_usage"],
        "alert_count": 2
    }
    
    try:
        result = await provider.diagnose(test_prompt, test_context)
        
        print("✓ 诊断成功!")
        print(f"\n诊断结果 (前 100 字符):")
        print("-" * 60)
        print(result[:100] + "..." if len(result) > 100 else result)
        print("-" * 60)
        print(f"\n总长度：{len(result)} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断失败：{e}")
        return False


def main():
    """主函数"""
    print("\nLab 7: 阿里云百炼集成测试\n")
    
    # 运行测试
    success = asyncio.run(test_bailian_provider())
    
    if success:
        print("\n✅ 测试通过！阿里云百炼已正确配置。")
        print("\n下一步:")
        print("  1. 运行：make data      # 生成测试数据")
        print("  2. 运行：make bailian   # 执行完整的 LLM 诊断")
        return 0
    else:
        print("\n❌ 测试失败或未配置 API Key")
        print("\n使用说明:")
        print("  1. 配置 API Key: export DASHSCOPE_API_KEY=sk-xxx")
        print("  2. 安装依赖：make deps")
        print("  3. 重新运行此测试：python test_bailian.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
